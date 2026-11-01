import re
from pathlib import Path, PurePosixPath
from typing import NamedTuple, Optional

import yaml

from .action import ACTION_STATUSES, LIST_ITEM, ActionSchemaError, actions_block, extract_actions
from .documents import FRONTMATTER, YAML_BLOCK
from .paths import RUN_PATTERN, require_project_directory
from .scan import (
    ADR_FILE_PATTERN,
    DECISIONS_DIRNAME,
    FINDING_FILE_PATTERN,
    PLAN_LOCATIONS,
    RFCS_DIRNAME,
    TASKS_DIRNAME,
    WORKFLOWS_DIRNAME,
    ScanError,
    documents,
    load_mapping,
    read,
    record_files,
    relative,
)
from .summary import SUMMARY_FILENAME, SUMMARY_SUFFIX
from .task import TASK_ID_PATTERN
from .validate import BLOCKING_SEVERITIES, BLOCKING_STATE, origin_task

MANIFEST_FILE = "manifest.yaml"
TRIVIAL_DIRNAME = "trivial"
EXECUTION_DIRNAME = "hactors"
EXECUTION_PREFIX = f"{EXECUTION_DIRNAME}/"
TASK_FILE_PATTERN = re.compile(rf"{TASK_ID_PATTERN.pattern}\.md")
TRV_FILE_PATTERN = re.compile(r"TRV-[0-9]{5,}")
WORKFLOW_FILE_PATTERN = re.compile(r"WORKFLOW-[0-9]{5,}")
FIELD_LINE = re.compile(
    r"^(?P<indent>[ ]*)(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?P<sep>[ \t]*)"
    r"(?P<value>[^#]*?)(?P<tail>[ \t]*#.*)?$"
)
ITEM_FIELD_LINE = re.compile(
    r"^(?P<prefix>[ ]*-[ \t]+)(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?P<sep>[ \t]*)"
    r"(?P<value>[^#]*?)(?P<tail>[ \t]*#.*)?$"
)
QUOTE_CHARS = "\"'"
DONE = "done"
COMPLETED = "completed"
CONSOLIDATED = "consolidated"
SUPERSEDED = "superseded"

RFC_STATUSES = frozenset(
    {
        "proposed", "draft", "approved", "in-progress", "implemented", "tested",
        "under_review", "validated", "merged", "done", "rejected", "cancelled",
        "superseded", "deprecated",
    }
)
TASK_STATUSES = frozenset(
    {
        "proposed", "draft", "approved", "in-progress", "implemented", "tested",
        "done", "rejected", "cancelled",
    }
)
SUMMARY_STATUSES = frozenset({"in-progress", "consolidated"})
WORKFLOW_STATUSES = frozenset({"proposed", "active", "closing", "closed", "cancelled", "aborted"})
PLAN_STATUSES = frozenset({"draft", "proposed", "approved", "rejected", "superseded", "completed"})
ADR_STATUSES = frozenset({"proposed", "accepted", "rejected", "superseded"})
TRV_STATUSES = frozenset({"proposed", "approved", "done", "rejected", "escalated"})
FINDING_STATES = frozenset({"open", "tracked", "resolved", "wont-fix", "superseded"})


def _chain(*statuses: str) -> frozenset:
    return frozenset(zip(statuses, statuses[1:]))


RFC_EDGES = _chain(
    "proposed", "draft", "approved", "in-progress", "implemented", "tested",
    "under_review", "validated", "merged", "done",
) | frozenset(
    {
        ("validated", "done"),
        ("implemented", "in-progress"),
        ("tested", "in-progress"),
        ("under_review", "in-progress"),
        ("proposed", "rejected"),
        ("draft", "rejected"),
        ("approved", "rejected"),
        ("in-progress", "cancelled"),
        ("implemented", "cancelled"),
        ("tested", "cancelled"),
        ("under_review", "cancelled"),
        ("validated", "cancelled"),
        ("merged", "cancelled"),
        ("approved", "superseded"),
        ("under_review", "superseded"),
        ("done", "superseded"),
        ("done", "deprecated"),
    }
)
TASK_EDGES = _chain(
    "proposed", "draft", "approved", "in-progress", "implemented", "tested", "done"
) | frozenset(
    {
        ("proposed", "rejected"),
        ("draft", "rejected"),
        ("approved", "rejected"),
        ("in-progress", "cancelled"),
        ("implemented", "cancelled"),
        ("tested", "cancelled"),
    }
)
SUMMARY_EDGES = frozenset({("in-progress", "consolidated"), ("consolidated", "in-progress")})
WORKFLOW_EDGES = _chain("proposed", "active", "closing", "closed") | frozenset(
    {
        ("active", "cancelled"),
        ("closing", "cancelled"),
        ("active", "aborted"),
        ("closing", "aborted"),
    }
)
PLAN_EDGES = _chain("draft", "proposed", "approved", "completed") | frozenset(
    {("proposed", "rejected"), ("approved", "superseded")}
)
ADR_EDGES = frozenset(
    {("proposed", "accepted"), ("proposed", "rejected"), ("accepted", "superseded")}
)
TRV_EDGES = _chain("proposed", "approved", "done") | frozenset(
    {("proposed", "rejected"), ("proposed", "escalated")}
)
ACTION_EDGES = _chain("pending", "in-progress", "completed") | frozenset(
    {
        ("pending", "blocked"),
        ("blocked", "pending"),
        ("in-progress", "cancelled"),
        ("completed", "superseded"),
    }
)
FINDING_EDGES = _chain("open", "tracked", "resolved") | frozenset(
    {("open", "wont-fix"), ("open", "superseded"), ("tracked", "open")}
)


class _Family(NamedTuple):
    label: str
    statuses: frozenset
    edges: frozenset
    field_path: tuple

    @property
    def field(self) -> str:
        return ".".join(self.field_path)


TASK_FAMILY = _Family("TASK", TASK_STATUSES, TASK_EDGES, ("execution", "status"))
RFC_FAMILY = _Family("RFC", RFC_STATUSES, RFC_EDGES, ("status",))
SUMMARY_FAMILY = _Family("Resumen", SUMMARY_STATUSES, SUMMARY_EDGES, ("status",))
WORKFLOW_FAMILY = _Family("WORKFLOW", WORKFLOW_STATUSES, WORKFLOW_EDGES, ("status",))
PLAN_FAMILY = _Family("PLAN", PLAN_STATUSES, PLAN_EDGES, ("status",))
ADR_FAMILY = _Family("ADR", ADR_STATUSES, ADR_EDGES, ("status",))
TRV_FAMILY = _Family("TRV", TRV_STATUSES, TRV_EDGES, ("status",))
ACTION_FAMILY = _Family("Acción derivada", ACTION_STATUSES, ACTION_EDGES, ("status",))
FINDING_FAMILY = _Family("Hallazgo", FINDING_STATES, FINDING_EDGES, ("state",))
FAMILIES = (
    TASK_FAMILY, RFC_FAMILY, SUMMARY_FAMILY, WORKFLOW_FAMILY, PLAN_FAMILY,
    ADR_FAMILY, TRV_FAMILY, ACTION_FAMILY, FINDING_FAMILY,
)


class _Target(NamedTuple):
    family: _Family
    subject: str
    where: str
    text: str
    data: dict
    region: tuple
    line: int


class TransitionError(Exception):
    pass


def transition(
    root: Path, project_name: str, artifact: str, to: str, identity: Optional[str] = None
) -> tuple[str, str, str]:
    try:
        project = require_project_directory(root, project_name)
        base, path = _target_file(root, project, artifact)
        where = relative(base, path)
        target = _resolve(base, path, where, identity)
        previous = _check_edge(target, to)
        problems = _closure_problems(project, target, to)
        if problems:
            raise ValueError("\n".join(problems))
        path.write_text(_rewritten(target, to))
    except (ActionSchemaError, ScanError, ValueError, OSError, yaml.YAMLError) as exc:
        raise TransitionError(str(exc)) from exc
    return target.subject, where, previous


def _target_file(root: Path, project: Path, artifact: str) -> tuple[Path, Path]:
    if not isinstance(artifact, str) or not artifact.strip():
        raise ValueError("Artefacto inválido: use una ruta relativa al proyecto.")
    parts = artifact.split("/")
    if Path(artifact).is_absolute() or "\\" in artifact or any(part in ("", ".", "..") for part in parts):
        raise ValueError("Artefacto inválido: use una ruta relativa al proyecto sin '.' ni '..'.")
    # TRIVIAL.md prescribe una segunda ubicación en la raíz de la copia, fuera de todo proyecto.
    at_root = _root_trivial(parts) and not (project / artifact).exists()
    base = root if at_root else project
    path = base / artifact
    if path.is_symlink():
        raise ValueError("El artefacto no admite enlaces simbólicos.")
    if not path.exists():
        raise ValueError(f"Artefacto no encontrado: '{artifact}'.")
    if not path.is_file():
        raise ValueError(f"'{artifact}' es un directorio; la sección 17 exige un archivo.")
    if not path.resolve().is_relative_to(base.resolve()):
        raise ValueError(
            "El artefacto está fuera de la raíz de HACTORS."
            if at_root
            else "El artefacto está fuera del directorio del proyecto."
        )
    return base, path


def _root_trivial(parts: list) -> bool:
    return (
        len(parts) == 2 and parts[0] == TRIVIAL_DIRNAME and TRV_FILE_PATTERN.match(parts[1]) is not None
    )


def _resolve(project: Path, path: Path, where: str, identity: Optional[str]) -> _Target:
    parts = PurePosixPath(where).parts
    name = parts[-1]
    if FINDING_FILE_PATTERN.fullmatch(name):
        return _whole(_record(project, path, where), identity)
    if len(parts) == 2 and parts[0] == TASKS_DIRNAME and TASK_FILE_PATTERN.fullmatch(name):
        return _whole(_task(project, path, where), identity)
    if len(parts) == 2 and parts[0] == RFCS_DIRNAME:
        return _rfcs(project, path, where, identity)
    if (
        len(parts) == 3
        and parts[0] == EXECUTION_DIRNAME
        and RUN_PATTERN.fullmatch(parts[1])
        and name == SUMMARY_FILENAME
    ):
        return _whole(_summary(project, path, where), identity)
    if (
        len(parts) == 3
        and parts[0] == WORKFLOWS_DIRNAME
        and WORKFLOW_FILE_PATTERN.fullmatch(parts[1])
        and name == MANIFEST_FILE
    ):
        return _whole(_workflow(project, path, where), identity)
    if "/".join(parts[:-1]) in PLAN_LOCATIONS and name.endswith(".md"):
        return _whole(_plan(project, path, where), identity)
    if len(parts) == 2 and parts[0] == DECISIONS_DIRNAME and ADR_FILE_PATTERN.match(name):
        return _whole(_declared(ADR_FAMILY, "adr", project, path, where), identity)
    if len(parts) == 2 and parts[0] == TRIVIAL_DIRNAME and TRV_FILE_PATTERN.match(name):
        return _whole(_declared(TRV_FAMILY, "id", project, path, where), identity)
    raise ValueError(
        f"'{where}' no pertenece a ninguna familia de estados documentales: "
        "véase la tabla de la sección 17 de HACTORS_SYSTEM.md."
    )


def _whole(target: _Target, identity: Optional[str]) -> _Target:
    if identity is not None:
        raise ValueError(
            f"'{target.where}' es {target.family.label} y no tiene elementos: "
            "su estado pertenece al archivo entero, así que '--id' no aplica."
        )
    return target


def _rfcs(project: Path, path: Path, where: str, identity: Optional[str]) -> _Target:
    text = read(project, path)
    region, block = _block_region(text, "rfc", where)
    if region is None:
        front, data = _frontmatter_region(text, where)
        if front is None or not _text(data, "artifact"):
            raise ValueError(
                f"'{where}' no declara 'rfc:' en un bloque `yaml` ni 'artifact:' en su frontmatter."
            )
        return _whole(_located(SUMMARY_FAMILY, _text(data, "artifact"), where, text, data, front), identity)
    if identity is None:
        return _located(RFC_FAMILY, _text(block, "rfc"), where, text, block, region)
    return _action(path, where, text, identity)


def _task(project: Path, path: Path, where: str) -> _Target:
    text = read(project, path)
    region, data = _frontmatter_region(text, where)
    if region is None:
        raise ValueError(f"'{where}' no empieza con una cabecera frontmatter.")
    return _located(TASK_FAMILY, path.stem, where, text, data, region)


def _summary(project: Path, path: Path, where: str) -> _Target:
    text = read(project, path)
    region, data = _frontmatter_region(text, where)
    if region is None:
        raise ValueError(f"'{where}' no empieza con una cabecera frontmatter.")
    artifact = _text(data, "artifact")
    if not artifact:
        raise ValueError(f"'{where}' no declara 'artifact:'.")
    return _located(SUMMARY_FAMILY, artifact, where, text, data, region)


def _declared(family: _Family, field: str, project: Path, path: Path, where: str) -> _Target:
    text = read(project, path)
    region, data = _frontmatter_region(text, where)
    if region is None or not _text(data, field):
        region, data = _block_region(text, field, where)
    if region is None:
        raise ValueError(
            f"'{where}' no declara '{field}:' en su frontmatter ni en un bloque `yaml`."
        )
    return _located(family, _text(data, field), where, text, data, region)


def _plan(project: Path, path: Path, where: str) -> _Target:
    text = read(project, path)
    region, data = _block_region(text, "id", where)
    if region is None:
        raise ValueError(f"'{where}' no declara 'id:' en un bloque `yaml`.")
    return _located(PLAN_FAMILY, _text(data, "id"), where, text, data, region)


def _workflow(project: Path, path: Path, where: str) -> _Target:
    text = read(project, path)
    lines = text.split("\n")
    region = (0, len(lines))
    data = _parsed(lines, region, where)
    identity = _text(data, "id")
    if not identity:
        raise ValueError(f"'{where}' no declara 'id:'.")
    return _located(WORKFLOW_FAMILY, identity, where, text, data, region)


def _record(project: Path, path: Path, where: str) -> _Target:
    text = read(project, path)
    lines = text.split("\n")
    region = (0, len(lines))
    return _located(FINDING_FAMILY, path.stem, where, text, _parsed(lines, region, where), region)


def _action(path: Path, where: str, text: str, identity: str) -> _Target:
    try:
        start, end = actions_block(text)
        declared = extract_actions(text)
    except (ActionSchemaError, yaml.YAMLError) as exc:
        raise ValueError(f"'{where}': {exc}") from exc
    if not isinstance(declared, list):
        raise ValueError(f"'{where}': `actions:` debe ser una lista, no {type(declared).__name__}.")
    lines = text.split("\n")
    for begin, limit in _items(lines, _span(text, start, end)):
        region = (begin, limit)
        element = _parsed(lines, region, where, element=True)
        if _text(element, "id") != identity:
            continue
        line = _element_field_line(lines, begin, limit, ACTION_FAMILY.field)
        if line is None:
            raise ValueError(f"La acción '{identity}' de '{where}' no declara el campo `status`.")
        return _Target(ACTION_FAMILY, identity, where, text, element, region, line)
    raise ValueError(f"'{where}' no declara la acción '{identity}' en su campo `actions:`.")


def _items(lines: list, region: tuple) -> list:
    field = _key_line(lines, region[0], region[1], 0, ("actions",))
    if field is None:
        return []
    start, limit = _block_extent(lines, field, region[1])
    indent = None
    begins = []
    for index in range(start, limit):
        match = LIST_ITEM.match(lines[index])
        if not match:
            continue
        if indent is None:
            indent = len(match["indent"])
        if len(match["indent"]) == indent:
            begins.append(index)
    return list(zip(begins, begins[1:] + [limit]))


def _frontmatter_region(text: str, where: str) -> tuple:
    if not text.startswith(FRONTMATTER):
        return None, {}
    lines = text.split("\n")
    for index in range(1, len(lines)):
        if lines[index] == "---":
            region = (1, index)
            return region, _parsed(lines, region, where)
    return None, {}


def _block_region(text: str, field: str, where: str) -> tuple:
    lines = text.split("\n")
    for match in YAML_BLOCK.finditer(text):
        region = _span(text, match.start(1), match.end(1))
        try:
            data = yaml.safe_load("\n".join(lines[region[0] : region[1]]))
        except yaml.YAMLError as exc:
            raise ValueError(f"'{where}': bloque `yaml` ilegible: {exc}") from exc
        if isinstance(data, dict) and _text(data, field):
            return region, data
    return None, {}


def _span(text: str, start: int, end: int) -> tuple:
    return text[:start].count("\n"), text[:end].count("\n")


def _parsed(lines: list, region: tuple, where: str, element: bool = False) -> dict:
    try:
        data = yaml.safe_load("\n".join(lines[region[0] : region[1]]))
    except yaml.YAMLError as exc:
        raise ValueError(f"'{where}': YAML ilegible: {exc}") from exc
    if element and isinstance(data, list):
        data = data[0] if len(data) == 1 else None
    if not isinstance(data, dict):
        raise ValueError(f"'{where}': el YAML no es un mapeo, sino {type(data).__name__}.")
    return data


def _located(family: _Family, subject: str, where: str, text: str, data: dict, region: tuple) -> _Target:
    lines = text.split("\n")
    line = _key_line(lines, region[0], region[1], 0, family.field_path)
    if line is None:
        raise ValueError(f"'{where}' no declara el campo `{family.field}`.")
    return _Target(family, subject, where, text, data, region, line)


def _key_line(lines: list, start: int, limit: int, indent: int, path: tuple) -> Optional[int]:
    for depth, key in enumerate(path):
        index = _find_key(lines, start, limit, indent, key)
        if index is None:
            return None
        if depth + 1 == len(path):
            return index
        start, limit = _block_extent(lines, index, limit)
        indent = _child_indent(lines, start, limit)
        if indent is None:
            return None
    return None


def _find_key(lines: list, start: int, limit: int, indent: int, key: str) -> Optional[int]:
    for index in range(start, limit):
        line = lines[index]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if _indent(line) < indent:
            return None
        match = FIELD_LINE.match(line)
        if match and _indent(line) == indent and match["key"] == key:
            return index
    return None


def _block_extent(lines: list, index: int, limit: int) -> tuple:
    indent = _indent(lines[index])
    end = index + 1
    while end < limit:
        line = lines[end]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            end += 1
            continue
        # Una lista puede escribirirse con el guion a la misma sangría que su clave.
        item = LIST_ITEM.match(line)
        if _indent(line) <= indent and not (item and len(item["indent"]) == indent):
            break
        end += 1
    return index + 1, end


def _child_indent(lines: list, start: int, limit: int) -> Optional[int]:
    for index in range(start, limit):
        stripped = lines[index].strip()
        if stripped and not stripped.startswith("#"):
            return _indent(lines[index])
    return None


def _element_field_line(lines: list, start: int, limit: int, key: str) -> Optional[int]:
    for index in range(start, limit):
        match = FIELD_LINE.match(lines[index]) or ITEM_FIELD_LINE.match(lines[index])
        if match and match["key"] == key:
            return index
    return None


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _check_edge(target: _Target, to: str) -> str:
    family = target.family
    current = _walk(target.data, family.field_path)
    if not isinstance(current, str) or not current:
        raise ValueError(f"'{target.where}': el campo `{family.field}` no declara un estado legible.")
    if current not in family.statuses:
        raise ValueError(
            f"'{target.where}': el campo `{family.field}` vale '{current}', "
            f"fuera de los estados de {family.label}."
        )
    if to not in family.statuses:
        raise ValueError(f"'{to}' no es un estado de {family.label}.")
    if to == current:
        raise ValueError(
            f"{family.label} '{target.subject}' ya está en '{to}': "
            "repetir el estado propio no es una transición."
        )
    if (current, to) not in family.edges:
        raise ValueError(f"{family.label} no admite la transición '{current}' → '{to}'.")
    return current


def _walk(data, path: tuple):
    for key in path:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def _rewritten(target: _Target, to: str) -> str:
    lines = target.text.split("\n")
    lines[target.line] = _rewrite_line(lines[target.line], to, target.family.field)
    updated = "\n".join(lines)
    written = _walk(
        _parsed(updated.split("\n"), target.region, target.where, target.family is ACTION_FAMILY),
        target.family.field_path,
    )
    if written != to:
        raise ValueError(f"No se pudo reescribir `{target.family.field}` en '{target.where}'.")
    return updated


def _rewrite_line(line: str, value: str, field: str) -> str:
    match = FIELD_LINE.match(line) or ITEM_FIELD_LINE.match(line)
    if match is None:
        raise ValueError(f"La línea del campo `{field}` no tiene la forma de un campo YAML.")
    groups = match.groupdict()
    head = groups.get("indent") or groups.get("prefix") or ""
    token = groups["value"].strip()
    quoted = len(token) > 1 and token[0] == token[-1] and token[0] in QUOTE_CHARS
    rendered = f"{token[0]}{value}{token[0]}" if quoted else value
    return f"{head}{groups['key']}:{groups['sep']}{rendered}{groups['tail'] or ''}"


def _closure_problems(project: Path, target: _Target, to: str) -> list:
    family = target.family
    if family is TASK_FAMILY and to == DONE:
        return _task_closure(project, target)
    if family is RFC_FAMILY and to == DONE:
        return _scope_closure(target)
    if family is ACTION_FAMILY and to == COMPLETED:
        return _evidence_closure(target)
    if family is SUMMARY_FAMILY and to == CONSOLIDATED:
        return _summary_closure(project, target)
    return []


def _task_closure(project: Path, target: _Target) -> list:
    declared = target.data.get("rfcs")
    scope = [item for item in declared if isinstance(item, str) and item] if isinstance(declared, list) else []
    states = _rfc_states(project)
    problems = []
    for identity in scope:
        problem = _scope_problem(identity, scope, states)
        if problem:
            problems.append(f"{target.where}: {problem}")
    problems.extend(_blocking(project, target, lambda data: origin_task(project, data) == target.subject))
    return problems


def _rfc_states(project: Path) -> dict:
    identities, _ = documents(
        project, (f"{RFCS_DIRNAME}/*.md",), "rfc", skip_suffixes=(SUMMARY_SUFFIX,)
    )
    states = {}
    for identity, path in identities.items():
        where = relative(project, path)
        _, block = _block_region(read(project, path), "rfc", where)
        states[identity] = (_text(block, "status"), block)
    return states


def _scope_problem(identity: str, scope: list, states: dict) -> str:
    if identity not in states:
        return f"la RFC '{identity}' de su campo `rfcs:` no existe en {RFCS_DIRNAME}/."
    status, block = states[identity]
    if status == DONE:
        return ""
    if status != SUPERSEDED:
        return f"la RFC '{identity}' de su campo `rfcs:` está en '{status}', no en `done`."
    successors = _successors(block)
    if not successors:
        return f"la RFC '{identity}' está en `superseded` sin `superseded_by`."
    outside = [item for item in successors if item not in scope]
    if outside:
        return f"la sustituta {_listed(outside)} de la RFC '{identity}' no consta en `rfcs:`."
    pending = [item for item in successors if states.get(item, ("",))[0] != DONE]
    if pending:
        return f"la sustituta {_listed(pending)} de la RFC '{identity}' no está en `done`."
    return ""


def _successors(block: dict) -> list:
    value = block.get("superseded_by")
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _scope_closure(target: _Target) -> list:
    try:
        declared = extract_actions(target.text)
    except (ActionSchemaError, yaml.YAMLError) as exc:
        return [f"{target.where}: {exc}"]
    if not isinstance(declared, list):
        return [f"{target.where}: `actions:` debe ser una lista, no {type(declared).__name__}."]
    problems = []
    for position, element in enumerate(declared, start=1):
        status = element.get("status") if isinstance(element, dict) else None
        if status == COMPLETED:
            continue
        label = _text(element, "id") if isinstance(element, dict) else ""
        if not label:
            label = f"actions[{position}]"
        problems.append(
            f"{target.where}: la acción '{label}' no está en `completed`; su estado es {status!r}."
        )
    return problems


def _evidence_closure(target: _Target) -> list:
    evidence = target.data.get("evidence")
    if isinstance(evidence, list) and evidence:
        return []
    return [
        f"{target.where}: la acción '{target.subject}' no declara evidencia, "
        "que `completed` exige conforme a AC_TEMPLATE.md."
    ]


def _summary_closure(project: Path, target: _Target) -> list:
    artifact = target.subject
    if artifact.startswith(EXECUTION_PREFIX):
        def matches(data: dict) -> bool:
            execution = _source(data, "execution")
            return execution == artifact or execution.startswith(artifact + "/")
    else:
        def matches(data: dict) -> bool:
            return _source(data, "artifact") == artifact
    return _blocking(project, target, matches)


def _blocking(project: Path, target: _Target, matches) -> list:
    problems = []
    for _, path in record_files(project):
        if not FINDING_FILE_PATTERN.fullmatch(path.name):
            continue
        where = relative(project, path)
        try:
            data = load_mapping(project, path)
        except ScanError as exc:
            problems.append(str(exc))
            continue
        if data.get("severity") not in BLOCKING_SEVERITIES or data.get("state") != BLOCKING_STATE:
            continue
        if matches(data):
            problems.append(
                f"{where}: hallazgo `{data.get('severity')}` en `{BLOCKING_STATE}` "
                f"bloquea {target.family.label} '{target.subject}'."
            )
    return problems


def _source(data: dict, field: str) -> str:
    source = data.get("source")
    return _text(source, field) if isinstance(source, dict) else ""


def _text(data, field: str) -> str:
    value = data.get(field) if isinstance(data, dict) else None
    return value if isinstance(value, str) else ""


def _listed(items: list) -> str:
    return ", ".join(f"'{item}'" for item in items)

import re
from pathlib import Path
from typing import Optional

import yaml

from .counters import next_action_id
from .documents import YAML_BLOCK, DocumentError, document_identity
from .paths import require_project_directory, resolve_origin
from .templates import load_template

ACTION_TEMPLATE = "action_template.yaml"
ACTIONS_FIELD = re.compile(r"^actions:[ \t]*(?P<value>[^ \t].*)?$")
LIST_ITEM = re.compile(r"^(?P<indent>[ ]*)-[ \t]")
DEFAULT_ITEM_INDENT = "  "
ACTION_ID_PATTERN = re.compile(r"ACT-[0-9]{5,}")
EVIDENCE_ID_PATTERN = re.compile(r"EVD-[0-9]{5,}")
ACTION_TYPES = frozenset(
    {"analysis", "plan", "decision", "implementation", "test", "evidence", "documentation"}
)
ACTION_STATUSES = frozenset(
    {"pending", "blocked", "in-progress", "completed", "cancelled", "superseded"}
)
ACTOR_LABELS = frozenset({"human", "agent", "ci"})
ACTOR_PROHIBITION = "..."
ACTION_FIELDS = frozenset(
    {"id", "type", "status", "actor", "depends_on", "deliverable", "evidence"}
)
UNRESOLVED = (None, "")


class ActionSchemaError(Exception):
    pass


class ActionError(Exception):
    pass


def _actor_error(value) -> str:
    if not isinstance(value, str):
        return f"`actor` debe ser una etiqueta, no {type(value).__name__}"
    parts = [part.strip() for part in value.split("|")]
    if parts == [ACTOR_PROHIBITION]:
        return ""
    if ACTOR_PROHIBITION in parts:
        return f"`actor` no admite combinar '{ACTOR_PROHIBITION}' con otras etiquetas"
    unknown = [part for part in parts if part not in ACTOR_LABELS]
    if unknown:
        return f"`actor` contiene etiquetas fuera de DEFINITIONS.md: {', '.join(repr(u) for u in unknown)}"
    if len(set(parts)) != len(parts):
        return f"`actor` repite etiquetas: {value!r}"
    return ""


def _reference_list_error(value, pattern: re.Pattern, field: str) -> str:
    if not isinstance(value, list):
        return f"`{field}` debe ser una lista, no {type(value).__name__}"
    for entry in value:
        if not isinstance(entry, str) or not pattern.fullmatch(entry):
            return f"`{field}` contiene una referencia inválida: {entry!r}"
    return ""


def actions_block(text: str) -> tuple[int, int]:
    spans = []
    for match in YAML_BLOCK.finditer(text):
        try:
            data = yaml.safe_load(match.group(1))
        except yaml.YAMLError as exc:
            raise ActionSchemaError(f"Bloque `yaml` ilegible: {exc}") from exc
        if isinstance(data, dict) and "actions" in data:
            spans.append((match.start(1), match.end(1)))
    if not spans:
        raise ActionSchemaError("Ningún bloque `yaml` del documento declara el campo `actions:`.")
    if len(spans) > 1:
        raise ActionSchemaError("Varios bloques `yaml` declaran `actions:`; el documento es ambiguo.")
    return spans[0]


def extract_actions(text: str):
    start, end = actions_block(text)
    return yaml.safe_load(text[start:end])["actions"]


def validate_actions(actions) -> list[str]:
    if not isinstance(actions, list):
        raise ActionSchemaError(f"`actions:` debe ser una lista, no {type(actions).__name__}.")
    findings: list[str] = []
    declared: dict[str, str] = {}
    for position, action in enumerate(actions, start=1):
        where = f"actions[{position}]"
        if not isinstance(action, dict):
            findings.append(f"{where}: debe ser un mapeo, no {type(action).__name__}.")
            continue

        action_id = action.get("id")
        if action_id in UNRESOLVED:
            findings.append(f"{where}: falta el identificador `id`.")
        elif not isinstance(action_id, str) or not ACTION_ID_PATTERN.fullmatch(action_id):
            findings.append(f"{where}: identificador inválido: {action_id!r}.")
        else:
            if action_id in declared:
                findings.append(f"{action_id}: identificador repetido; ya aparece en {declared[action_id]}.")
            else:
                declared[action_id] = where
            where = action_id

        for field in sorted(set(action) - ACTION_FIELDS):
            findings.append(f"{where}: campo ajeno al esquema: '{field}'.")

        for field, domain in (("type", ACTION_TYPES), ("status", ACTION_STATUSES)):
            value = action.get(field)
            if value in UNRESOLVED:
                continue
            if not isinstance(value, str) or value not in domain:
                findings.append(f"{where}: `{field}` fuera de dominio: {value!r}.")

        actor = action.get("actor")
        if actor not in UNRESOLVED:
            error = _actor_error(actor)
            if error:
                findings.append(f"{where}: {error}.")

        deliverable = action.get("deliverable")
        if deliverable not in UNRESOLVED and not isinstance(deliverable, str):
            findings.append(f"{where}: `deliverable` debe ser una ruta o descripción textual.")

        for field, pattern in (("depends_on", ACTION_ID_PATTERN), ("evidence", EVIDENCE_ID_PATTERN)):
            value = action.get(field)
            if value in UNRESOLVED:
                continue
            error = _reference_list_error(value, pattern, field)
            if error:
                findings.append(f"{where}: {error}.")
    return findings


def validate_rfc_actions(text: str) -> list[str]:
    return validate_actions(extract_actions(text))


def append_action(text: str, element: dict) -> str:
    start, end = actions_block(text)
    lines = text[start:end].split("\n")
    index = _field_line(lines)
    value = (ACTIONS_FIELD.match(lines[index])["value"] or "").strip()
    if value not in ("", "[]"):
        raise ActionSchemaError(
            "El campo `actions:` no está en forma de bloque; no se puede insertar una acción."
        )
    position = _list_end(lines, index)
    indent = _item_indent(lines, index, position)
    if value == "[]":
        lines[index] = "actions:"
    lines[position:position] = _rendered(element, indent).split("\n")
    updated = text[:start] + "\n".join(lines) + text[end:]
    actions_block(updated)
    return updated


def _field_line(lines: list[str]) -> int:
    for index, line in enumerate(lines):
        if ACTIONS_FIELD.match(line):
            return index
    raise ActionSchemaError(
        "El campo `actions:` no está en el nivel superior del bloque; "
        "no se puede insertar una acción."
    )


def _list_end(lines: list[str], index: int) -> int:
    last = index + 1
    for position in range(index + 1, len(lines)):
        line = lines[position]
        if line.strip() and not line.startswith((" ", "\t", "-")):
            break
        if line.strip():
            last = position + 1
    return last


def _item_indent(lines: list[str], index: int, position: int) -> str:
    for line in lines[index + 1 : position]:
        match = LIST_ITEM.match(line)
        if match:
            return match["indent"]
    return DEFAULT_ITEM_INDENT


def _rendered(element: dict, indent: str) -> str:
    dumped = yaml.dump([element], default_flow_style=False, allow_unicode=True, sort_keys=False)
    return "\n".join(
        f"{indent}{line}" if line else "" for line in dumped.rstrip("\n").split("\n")
    )


def create_action(
    root: Path,
    project_name: str,
    rfc: str,
    type_: Optional[str] = None,
    status: Optional[str] = None,
    actor: Optional[str] = None,
    deliverable: Optional[str] = None,
    depends_on: Optional[tuple[str, ...]] = None,
    evidence: Optional[tuple[str, ...]] = None,
) -> tuple[str, Path]:
    try:
        project = require_project_directory(root, project_name)
        path = _rfc_document(root, project_name, project, rfc)
        text = path.read_text()
        if not document_identity(text, "rfc"):
            raise ValueError(f"'{rfc}' no declara el campo 'rfc:'.")
        element = dict(load_template(root, ACTION_TEMPLATE))
        for field, value in (
            ("type", type_), ("status", status), ("actor", actor), ("deliverable", deliverable)
        ):
            if value is not None:
                element[field] = value
        for field, values in (("depends_on", depends_on), ("evidence", evidence)):
            if values:
                element[field] = list(values)
        declared = extract_actions(text)
        if not isinstance(declared, list):
            declared = []
        taken = {
            action["id"]
            for action in declared
            if isinstance(action, dict) and isinstance(action.get("id"), str)
        }
        action_id, _ = next_action_id(project / "manifest.yaml", taken)
        element["id"] = action_id
        findings = validate_actions([element])
        if findings:
            raise ValueError(" ".join(findings))
        path.write_text(append_action(text, element))
    except (ActionSchemaError, DocumentError, ValueError, OSError, yaml.YAMLError) as exc:
        raise ActionError(str(exc)) from exc
    return action_id, path


def _rfc_document(root: Path, project_name: str, project: Path, rfc: str) -> Path:
    resolve_origin(root, project_name, project, rfc)
    path = project / rfc
    if not path.is_file():
        raise ValueError(f"'{rfc}' no es un archivo del proyecto.")
    return path

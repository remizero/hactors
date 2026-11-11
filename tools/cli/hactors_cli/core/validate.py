import re
from pathlib import Path

from .action import ActionSchemaError, extract_actions, validate_rfc_actions
from .documents import DocumentError, yaml_blocks
from .paths import (
    RUN_CHILD_TYPES,
    RUN_PATTERN,
    RUN_TYPES,
    require_project_directory,
    require_run_directory,
)
from .scan import (
    FINDING_FILE_PATTERN,
    HARNESS_REF_PATTERN,
    PLAN_LOCATIONS,
    REFERENCE_FIELDS,
    TESTS_DIRNAME,
    WORKFLOW_REF_PATTERN,
    WORKFLOWS_DIRNAME,
    ScanError,
    adr_documents,
    documents,
    harness_catalogs,
    harness_package,
    load_mapping,
    read,
    record_files,
    relative,
    run_identity,
    run_manifests,
    task_documents,
    workflow_package,
)
from .state import STATE_FILE, StateError, load_state
from .summary import SUMMARY_SUFFIX
from .task import normalize_task_ref

BLOCKING_SEVERITIES = frozenset({"critical", "high"})
BLOCKING_STATE = "open"
TASK_CLOSED_STATUS = "done"
RELATION_FIELDS = frozenset({"source", "target", "relation"})
COUNTER_ID_PATTERNS = {
    "task": re.compile(r"TASK-([0-9]{5,})"),
    "action": re.compile(r"ACT-([0-9]{5,})"),
    "plan": re.compile(r"PLAN-([0-9]{5,})"),
    "test": re.compile(r"TEST-([0-9]{5,})"),
    "harness": re.compile(r"HRN-([0-9]{5,})"),
    "workflow_run": re.compile(r"workflow_run_([0-9]{6,})"),
    "evidence": re.compile(r"EVD-([0-9]{5,})"),
    "finding": re.compile(r"FND-([0-9]{5,})"),
    "adr": re.compile(r"ADR-([0-9]{5,})"),
}
# El catálogo WORKFLOW no consume contador: se redacta con el número que tendrá
# su workflow_run, así que su identidad se observa bajo el contador unificado.
WORKFLOW_DEFINITION_PATTERN = re.compile(r"WORKFLOW-([0-9]{5,})")
# Un segmento de identidad de RFC es de tipo solo si es una letra de tipo seguida
# de cifras; los modificadores (AM, AR, REV, V2, PATCH, FX) tienen un segundo
# carácter no numérico y por tanto no coinciden.
RFC_TYPE_SEGMENT = re.compile(r"([AFITD])([0-9]{5,})")
RECORD_COUNTERS = (("EVD-", "evidence"), ("FND-", "finding"))
KNOWN_COUNTERS = (
    frozenset(COUNTER_ID_PATTERNS)
    | frozenset(RUN_TYPES)
    | {f"rfc_{letter}" for letter in "afitd"}
)
ARTIFACT_PREFIXES = (
    "TASK-",
    "ACT-",
    "PLAN-",
    "ADR-",
    "EVD-",
    "FND-",
    "HRN-",
    "RFC-",
    "TEST-",
    "WORKFLOW-",
)
RFC_EDGE_FIELDS = {
    "origin": ("derives", True),
    "depends_on": ("depends-on", False),
    "supersedes": ("supersedes", False),
    "superseded_by": ("supersedes", True),
}


def _task_statuses(project: Path) -> tuple[dict, list[str]]:
    headers, problems = task_documents(project)
    statuses: dict[str, str] = {}
    for stem, data in headers.items():
        execution = data.get("execution")
        status = execution.get("status") if isinstance(execution, dict) else None
        statuses[stem] = status if isinstance(status, str) else ""
    return statuses, problems


def _plan_documents(project: Path) -> tuple[dict, list[str]]:
    return documents(project, tuple(f"{location}/*.md" for location in PLAN_LOCATIONS), "id")


def _test_documents(project: Path) -> tuple[dict, list[str]]:
    return documents(project, (f"{TESTS_DIRNAME}/*.md",), "id")


def _task_from_execution(project: Path, execution) -> str:
    if not isinstance(execution, str) or not execution:
        return ""
    parts = execution.split("/")
    if parts[0] != "hactors" or len(parts) < 2:
        return ""
    manifest = project / "hactors" / parts[1] / "manifest.yaml"
    if not manifest.is_file():
        return ""
    try:
        identity = run_identity(project, "workflow_run", manifest.parent, manifest)
    except ScanError:
        return ""
    task_ref = identity.get("task_ref")
    if not isinstance(task_ref, str) or not task_ref:
        return ""
    try:
        return normalize_task_ref(task_ref)
    except ValueError:
        return ""


def origin_task(project: Path, data: dict) -> str:
    source = data.get("source")
    if not isinstance(source, dict):
        return ""
    task_id = _task_from_execution(project, source.get("execution"))
    if task_id:
        return task_id
    for field in ("task", "artifact"):
        declared = source.get(field)
        if not isinstance(declared, str) or not declared:
            continue
        try:
            return normalize_task_ref(declared)
        except ValueError:
            continue
    return ""


def _run_instances(project: Path) -> tuple[list, list[str]]:
    instances: list[tuple[str, Path, dict]] = []
    problems: list[str] = []
    for run_type, directory, manifest in run_manifests(project):
        try:
            identity = run_identity(project, run_type, directory, manifest)
        except ScanError as exc:
            problems.append(str(exc))
            identity = None
        instances.append((run_type, directory, identity))
    return instances, problems


def _check_references(
    project: Path, instances: list, rfc_ids: dict, plan_ids: dict, test_ids: dict
) -> list[str]:
    findings: list[str] = []
    for run_type, directory, identity in instances:
        field = REFERENCE_FIELDS.get(run_type)
        if field is None or identity is None:
            continue
        where = relative(project, directory)
        reference = identity.get(field)
        if not isinstance(reference, str) or not reference:
            continue
        if run_type == "workflow_run":
            expected = f"tasks/{reference}.md"
            resolved = (project / "tasks" / f"{reference}.md").is_file()
        elif run_type == "rfc_run":
            expected = "una RFC en rfcs/"
            resolved = reference in rfc_ids
        elif run_type == "plan_run":
            expected = "un PLAN en plans/ o docs/plans/"
            resolved = reference in plan_ids
        elif run_type == "test_run":
            expected = f"un TEST en {TESTS_DIRNAME}/"
            resolved = reference in test_ids
        else:
            try:
                package = harness_package(project, reference)
            except ScanError as exc:
                findings.append(f"{where}: {exc}")
                continue
            expected = relative(project, package)
            resolved = package.is_file()
        if not resolved:
            findings.append(f"{where}: `{field}` '{reference}' no resuelve a {expected}.")
    return findings


def _check_hierarchy(project: Path, instances: list) -> list[str]:
    findings: list[str] = []
    for run_type, directory, identity in instances:
        where = relative(project, directory)
        parent = RUN_PATTERN.fullmatch(directory.parent.name)
        parent_type = parent[1] if parent else directory.parent.name
        if run_type not in RUN_CHILD_TYPES.get(parent_type, ()):
            findings.append(
                f"{where}: jerarquía inválida: {run_type} no puede vivir dentro de {parent_type}."
            )
        if identity is None:
            continue
        if identity.get("id") != directory.name:
            findings.append(
                f"{where}: `identity.id` no coincide con su componente de ruta '{directory.name}'."
            )
    return findings


def _workflow_definitions(project: Path) -> list[str]:
    directory = project / "workflows"
    if not directory.is_dir():
        return []
    pattern = WORKFLOW_DEFINITION_PATTERN
    return sorted(
        entry.name
        for entry in directory.iterdir()
        if entry.is_dir() and pattern.fullmatch(entry.name)
    )


def _rfc_type(identity: str) -> tuple[str, str]:
    for segment in reversed(identity.split("-")):
        match = RFC_TYPE_SEGMENT.fullmatch(segment)
        if match:
            return f"rfc_{match[1].lower()}", match[2]
    return "", ""


def _note(observed: dict, counter: str, identity: str, digits: str, present: bool = True) -> None:
    number = int(digits)
    entry = observed.setdefault(counter, [0, "", 0])
    if number > entry[0]:
        entry[0] = number
        entry[1] = identity
    if present:
        entry[2] += 1


def _observed_counters(
    project: Path,
    rfc_ids: dict,
    plan_ids: list,
    test_ids: list,
    catalogs: list,
    statuses: dict,
    instances: list,
    records: list,
    adrs: list,
) -> dict:
    observed: dict[str, tuple[int, str]] = {}
    documents_by_counter = [("task", stem) for stem in statuses]
    documents_by_counter.extend(("plan", identity) for identity in plan_ids)
    documents_by_counter.extend(("test", identity) for identity in test_ids)
    documents_by_counter.extend(("harness", identity) for identity, _, _ in catalogs)
    documents_by_counter.extend(
        (counter, identity)
        for identity, _ in records
        for prefix, counter in RECORD_COUNTERS
        if identity.startswith(prefix)
    )
    documents_by_counter.extend(("adr", identity) for identity, _ in adrs)
    for counter, identity in documents_by_counter:
        match = COUNTER_ID_PATTERNS[counter].fullmatch(identity)
        if match:
            _note(observed, counter, identity, match[1])
    for identity in _workflow_definitions(project):
        match = WORKFLOW_DEFINITION_PATTERN.fullmatch(identity)
        if match:
            _note(observed, "workflow_run", identity, match[1], present=False)
    for identity, path in rfc_ids.items():
        counter, digits = _rfc_type(identity)
        if counter:
            _note(observed, counter, identity, digits)
        try:
            actions = extract_actions(read(project, path))
        except (ActionSchemaError, ScanError):
            continue
        for element in actions if isinstance(actions, list) else []:
            element_identity = element.get("id") if isinstance(element, dict) else None
            if not isinstance(element_identity, str):
                continue
            match = COUNTER_ID_PATTERNS["action"].fullmatch(element_identity)
            if match:
                _note(observed, "action", element_identity, match[1])
    for run_type, directory, _ in instances:
        if RUN_PATTERN.fullmatch(directory.name):
            digits = directory.name[len(run_type) + 1 :]
            _note(observed, run_type, directory.name, digits)
    return observed


def _check_counters(manifest: dict, observed: dict) -> list[str]:
    counters = manifest.get("counters")
    if not isinstance(counters, dict):
        return [f"manifest.yaml: `counters` debe ser un mapeo, no {type(counters).__name__}."]
    findings: list[str] = []
    for counter in sorted(set(counters) | set(observed)):
        if counter not in KNOWN_COUNTERS:
            continue
        declared = counters.get(counter)
        if type(declared) is not int or declared < 0:
            findings.append(f"manifest.yaml: el contador `{counter}` no es un entero no negativo.")
            continue
        number, identity, present = observed.get(counter, (0, "", 0))
        if declared < number:
            findings.append(
                f"manifest.yaml: el contador `{counter}` vale {declared} y existe la identidad "
                f"'{identity}'; debe ser mayor o igual que cualquier identidad de su tipo."
            )
        elif declared != present:
            findings.append(
                f"manifest.yaml: el contador `{counter}` vale {declared} y hay {present} "
                f"identidad(es) de su tipo presente(s); debe igualar exactamente esa cantidad."
            )
    return findings


def _check_blocking_findings(project: Path, statuses: dict) -> list[str]:
    findings: list[str] = []
    for path in sorted(project.rglob("FND-*.yaml")):
        if not FINDING_FILE_PATTERN.fullmatch(path.name):
            continue
        where = relative(project, path)
        try:
            data = load_mapping(project, path)
        except ScanError as exc:
            findings.append(str(exc))
            continue
        if data.get("severity") not in BLOCKING_SEVERITIES or data.get("state") != BLOCKING_STATE:
            continue
        task_id = origin_task(project, data)
        if not task_id or statuses.get(task_id) != TASK_CLOSED_STATUS:
            continue
        findings.append(
            f"{where}: hallazgo `{data.get('severity')}` en `{BLOCKING_STATE}` "
            f"con su TASK de origen {task_id} cerrada en `{TASK_CLOSED_STATUS}`."
        )
    return findings


def _check_actions(project: Path, rfc_ids: dict) -> list[str]:
    findings: list[str] = []
    for path in rfc_ids.values():
        where = relative(project, path)
        try:
            findings.extend(
                f"{where}: {item}" for item in validate_rfc_actions(read(project, path))
            )
        except (ActionSchemaError, ScanError) as exc:
            findings.append(f"{where}: {exc}")
    return findings


def _identity_set(
    rfc_ids: dict,
    plan_ids: dict,
    test_ids: dict,
    statuses: dict,
    catalogs: list,
    records: list,
    adrs: list,
) -> set[str]:
    identities = set(rfc_ids) | set(plan_ids) | set(test_ids) | set(statuses)
    identities.update(identity for identity, _ in records)
    identities.update(identity for identity, _, _ in catalogs)
    identities.update(identity for identity, _ in adrs)
    return identities


def artifact_identities(project: Path) -> set[str]:
    rfc_ids, _ = documents(project, ("rfcs/*.md",), "rfc", skip_suffixes=(SUMMARY_SUFFIX,))
    plan_ids, _ = _plan_documents(project)
    test_ids, _ = _test_documents(project)
    statuses, _ = _task_statuses(project)
    catalogs, _ = harness_catalogs(project)
    return _identity_set(
        rfc_ids,
        plan_ids,
        test_ids,
        statuses,
        catalogs,
        record_files(project),
        adr_documents(project),
    )


def target_problem(project: Path, target: str, identities: set[str]) -> str:
    artifact = target.partition("#")[0]
    if HARNESS_REF_PATTERN.fullmatch(artifact):
        expected = harness_package(project, artifact)
    elif artifact.startswith("HRN-"):
        expected = project / "harnesses" / artifact / "manifest.yaml"
    elif WORKFLOW_REF_PATTERN.fullmatch(artifact):
        expected = workflow_package(project, artifact)
    elif artifact.startswith("WORKFLOW-"):
        expected = project / WORKFLOWS_DIRNAME / artifact / "manifest.yaml"
    elif artifact.startswith(ARTIFACT_PREFIXES):
        if artifact in identities:
            return ""
        return "no resuelve a ningún artefacto del proyecto."
    else:
        return ""
    if expected.is_file():
        return ""
    return f"no resuelve a {relative(project, expected)}."


def _project_manifest(project: Path) -> tuple[dict, list[str]]:
    try:
        return load_mapping(project, project / "manifest.yaml"), []
    except ScanError as exc:
        return {}, [str(exc)]


def _relations(manifest: dict) -> tuple[list, list[str]]:
    relations = manifest.get("relations")
    if relations in (None, []):
        return [], []
    if not isinstance(relations, list):
        return [], [f"manifest.yaml: `relations` debe ser una lista, no {type(relations).__name__}."]
    return relations, []


def _check_relation_targets(project: Path, relations: list, identities: set[str]) -> list[str]:
    findings: list[str] = []
    for position, element in enumerate(relations, start=1):
        where = f"manifest.yaml: relations[{position}]"
        if not isinstance(element, dict):
            findings.append(f"{where}: debe ser un mapeo, no {type(element).__name__}.")
            continue
        findings.extend(
            f"{where}: campo ajeno al esquema: '{field}'."
            for field in element
            if field not in RELATION_FIELDS
        )
        target = element.get("target")
        if not isinstance(target, str) or not target:
            continue
        problem = target_problem(project, target, identities)
        if problem:
            findings.append(f"{where}: `target` '{target}' {problem}")
    return findings


def _recorded_edges(relations: list) -> set[tuple[str, str, str]]:
    edges = set()
    for element in relations:
        if not isinstance(element, dict):
            continue
        values = [element.get(field) for field in ("source", "target", "relation")]
        if all(isinstance(value, str) and value for value in values):
            edges.add(tuple(values))
    return edges


def _relation_entries(source: str, entries) -> list[tuple[tuple, str]]:
    declared = []
    if not isinstance(entries, list):
        return declared
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        target, relation = entry.get("target"), entry.get("relation")
        if isinstance(target, str) and target and isinstance(relation, str) and relation:
            declared.append(((source, target, relation), "relations"))
    return declared


def _rfc_edges(identity: str, text: str) -> list[tuple[tuple, str]]:
    block = {}
    try:
        for candidate in yaml_blocks(text):
            if isinstance(candidate, dict) and candidate.get("rfc"):
                block = candidate
                break
    except DocumentError:
        return []
    declared = []
    for field, (relation, inverted) in RFC_EDGE_FIELDS.items():
        value = block.get(field)
        if isinstance(value, str) and value:
            value = [value]
        if not isinstance(value, list):
            continue
        for item in value:
            if not isinstance(item, str) or not item:
                continue
            edge = (item, identity, relation) if inverted else (identity, item, relation)
            declared.append((edge, field))
    declared.extend(_relation_entries(identity, block.get("relations")))
    return declared


def _declared_edges(
    project: Path, rfc_ids: dict, test_ids: dict, catalogs: list
) -> tuple[list, list[str]]:
    edges: list[tuple[tuple, str, str]] = []
    problems: list[str] = []
    for identity, path in rfc_ids.items():
        where = relative(project, path)
        try:
            text = read(project, path)
        except ScanError as exc:
            problems.append(str(exc))
            continue
        edges.extend((edge, where, field) for edge, field in _rfc_edges(identity, text))
    for identity, path in test_ids.items():
        where = relative(project, path)
        try:
            blocks = yaml_blocks(read(project, path))
        except (DocumentError, ScanError) as exc:
            problems.append(str(exc))
            continue
        block = next(
            (item for item in blocks if isinstance(item, dict) and item.get("id") == identity), {}
        )
        edges.extend(
            (edge, where, field)
            for edge, field in _relation_entries(identity, block.get("relations"))
        )
    for identity, path in record_files(project):
        where = relative(project, path)
        try:
            data = load_mapping(project, path)
        except ScanError as exc:
            problems.append(str(exc))
            continue
        edges.extend(
            (edge, where, field) for edge, field in _relation_entries(identity, data.get("relations"))
        )
    for identity, path, data in catalogs:
        where = relative(project, path)
        edges.extend(
            (edge, where, field) for edge, field in _relation_entries(identity, data.get("relations"))
        )
        versions = data.get("versions")
        if not isinstance(versions, list):
            continue
        for version in versions:
            if not isinstance(version, dict) or not isinstance(version.get("version"), int):
                continue
            exact = f"{identity}@v{version['version']:03d}"
            edges.extend(
                (edge, where, field)
                for edge, field in _relation_entries(exact, version.get("relations"))
            )
    return edges, problems


def _check_relation_completeness(
    project: Path, recorded: set, rfc_ids: dict, test_ids: dict, catalogs: list
) -> list[str]:
    edges, findings = _declared_edges(project, rfc_ids, test_ids, catalogs)
    seen: set[tuple] = set()
    for edge, where, field in edges:
        if edge in recorded or edge in seen:
            continue
        seen.add(edge)
        source, target, relation = edge
        findings.append(
            f"{where}: el campo `{field}` declara la arista "
            f"{{source: {source}, target: {target}, relation: {relation}}}, "
            "que no consta en `relations` del manifest."
        )
    return findings


def _check_active_state(root: Path, project_name: str) -> list[str]:
    try:
        state = load_state(root)
    except StateError as exc:
        return [f"{STATE_FILE}: {exc}"]
    run_path = state["active_run_path"]
    if state["active_project"] != project_name or not run_path:
        return []
    try:
        require_run_directory(root, project_name, run_path)
    except (ValueError, OSError) as exc:
        return [f"{STATE_FILE}: la instancia activa '{run_path}' no es válida: {exc}"]
    return []


def validate_project(root: Path, project_name: str) -> list[str]:
    project = require_project_directory(root, project_name)
    rfc_ids, findings = documents(project, ("rfcs/*.md",), "rfc", skip_suffixes=(SUMMARY_SUFFIX,))
    plan_ids, plan_problems = _plan_documents(project)
    test_ids, test_problems = _test_documents(project)
    statuses, task_problems = _task_statuses(project)
    catalogs, catalog_problems = harness_catalogs(project)
    records = record_files(project)
    adrs = adr_documents(project)
    instances, instance_problems = _run_instances(project)
    identities = _identity_set(rfc_ids, plan_ids, test_ids, statuses, catalogs, records, adrs)
    manifest, manifest_problems = _project_manifest(project)
    relations, relation_problems = _relations(manifest)
    findings.extend(plan_problems)
    findings.extend(test_problems)
    findings.extend(task_problems)
    findings.extend(catalog_problems)
    findings.extend(instance_problems)
    findings.extend(manifest_problems)
    findings.extend(relation_problems)
    findings.extend(_check_references(project, instances, rfc_ids, plan_ids, test_ids))
    findings.extend(_check_hierarchy(project, instances))
    if not manifest_problems:
        observed = _observed_counters(
            project, rfc_ids, plan_ids, test_ids, catalogs, statuses, instances, records, adrs
        )
        findings.extend(_check_counters(manifest, observed))
    findings.extend(_check_relation_targets(project, relations, identities))
    recorded = _recorded_edges(relations)
    findings.extend(
        _check_relation_completeness(project, recorded, rfc_ids, test_ids, catalogs)
    )
    findings.extend(_check_blocking_findings(project, statuses))
    findings.extend(_check_actions(project, rfc_ids))
    findings.extend(_check_active_state(root, project_name))
    return findings

from pathlib import Path

from .action import ActionSchemaError, validate_rfc_actions
from .documents import DocumentError, yaml_blocks
from .paths import require_project_directory
from .scan import (
    FINDING_FILE_PATTERN,
    HARNESS_REF_PATTERN,
    PLAN_LOCATIONS,
    REFERENCE_FIELDS,
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
)
from .summary import SUMMARY_SUFFIX
from .task import normalize_task_ref

BLOCKING_SEVERITIES = frozenset({"critical", "high"})
BLOCKING_STATE = "open"
TASK_CLOSED_STATUS = "done"
UNRESOLVED_REFERENCE_FIELDS = frozenset({"test_ref"})
RELATION_FIELDS = frozenset({"source", "target", "relation"})
ARTIFACT_PREFIXES = ("TASK-", "AC-", "PLAN-", "ADR-", "EVD-", "FND-", "HRN-", "RFC-")
IDENTITY_UNDEFINED_PREFIXES = ("TEST-",)
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


def _origin_task(project: Path, data: dict) -> str:
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


def _check_references(project: Path, rfc_ids: dict, plan_ids: dict) -> list[str]:
    findings: list[str] = []
    for run_type, directory, manifest in run_manifests(project):
        field = REFERENCE_FIELDS.get(run_type)
        if field is None or field in UNRESOLVED_REFERENCE_FIELDS:
            continue
        where = relative(project, directory)
        try:
            identity = run_identity(project, run_type, directory, manifest)
        except ScanError as exc:
            findings.append(str(exc))
            continue
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
        task_id = _origin_task(project, data)
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
    project: Path, rfc_ids: dict, plan_ids: dict, statuses: dict, catalogs: list
) -> set[str]:
    identities = set(rfc_ids) | set(plan_ids) | set(statuses)
    identities.update(identity for identity, _ in record_files(project))
    identities.update(identity for identity, _, _ in catalogs)
    identities.update(identity for identity, _ in adr_documents(project))
    return identities


def artifact_identities(project: Path) -> set[str]:
    rfc_ids, _ = documents(project, ("rfcs/*.md",), "rfc", skip_suffixes=(SUMMARY_SUFFIX,))
    plan_ids, _ = documents(
        project, tuple(f"{location}/*.md" for location in PLAN_LOCATIONS), "id"
    )
    statuses, _ = _task_statuses(project)
    catalogs, _ = harness_catalogs(project)
    return _identity_set(project, rfc_ids, plan_ids, statuses, catalogs)


def target_problem(project: Path, target: str, identities: set[str]) -> str:
    artifact = target.partition("#")[0]
    if artifact.startswith(IDENTITY_UNDEFINED_PREFIXES):
        return ""
    if HARNESS_REF_PATTERN.fullmatch(artifact):
        expected = harness_package(project, artifact)
    elif artifact.startswith("HRN-"):
        expected = project / "harnesses" / artifact / "manifest.yaml"
    elif artifact.startswith(ARTIFACT_PREFIXES):
        if artifact in identities:
            return ""
        return "no resuelve a ningún artefacto del proyecto."
    else:
        return ""
    if expected.is_file():
        return ""
    return f"no resuelve a {relative(project, expected)}."


def _project_relations(project: Path) -> tuple[list, list[str]]:
    try:
        data = load_mapping(project, project / "manifest.yaml")
    except ScanError as exc:
        return [], [str(exc)]
    relations = data.get("relations")
    if relations in (None, []):
        return [], []
    if not isinstance(relations, list):
        return [], [f"manifest.yaml: `relations` debe ser una lista, no {type(relations).__name__}."]
    return relations, []


def _check_relation_targets(project: Path, identities: set[str]) -> list[str]:
    relations, findings = _project_relations(project)
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


def _manifest_edges(project: Path) -> set[tuple[str, str, str]]:
    relations, _ = _project_relations(project)
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


def _declared_edges(project: Path, rfc_ids: dict, catalogs: list) -> tuple[list, list[str]]:
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


def _check_relation_completeness(project: Path, rfc_ids: dict, catalogs: list) -> list[str]:
    edges, findings = _declared_edges(project, rfc_ids, catalogs)
    recorded = _manifest_edges(project)
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


def validate_project(root: Path, project_name: str) -> list[str]:
    project = require_project_directory(root, project_name)
    rfc_ids, findings = documents(project, ("rfcs/*.md",), "rfc", skip_suffixes=(SUMMARY_SUFFIX,))
    plan_ids, plan_problems = documents(
        project, tuple(f"{location}/*.md" for location in PLAN_LOCATIONS), "id"
    )
    statuses, task_problems = _task_statuses(project)
    catalogs, catalog_problems = harness_catalogs(project)
    identities = _identity_set(project, rfc_ids, plan_ids, statuses, catalogs)
    findings.extend(plan_problems)
    findings.extend(task_problems)
    findings.extend(catalog_problems)
    findings.extend(_check_references(project, rfc_ids, plan_ids))
    findings.extend(_check_relation_targets(project, identities))
    findings.extend(_check_relation_completeness(project, rfc_ids, catalogs))
    findings.extend(_check_blocking_findings(project, statuses))
    findings.extend(_check_actions(project, rfc_ids))
    return findings

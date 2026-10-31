import re
from pathlib import Path

import yaml

from .action import ActionSchemaError, validate_rfc_actions
from .documents import DocumentError, document_identity, front_matter
from .paths import RUN_PATTERN, require_project_directory
from .summary import SUMMARY_SUFFIX
from .task import normalize_task_ref

BLOCKING_SEVERITIES = frozenset({"critical", "high"})
BLOCKING_STATE = "open"
TASK_CLOSED_STATUS = "done"
HARNESS_REF_PATTERN = re.compile(r"(HRN-[0-9]{5,})@(v[0-9]{3,})")
FINDING_FILE_PATTERN = re.compile(r"FND-[0-9]{5,}\.yaml")
REFERENCE_FIELDS = {
    "workflow_run": "task_ref",
    "rfc_run": "rfc_ref",
    "plan_run": "plan_ref",
    "harness_run": "harness_ref",
}
PLAN_LOCATIONS = ("plans", "docs/plans")


class ValidateError(Exception):
    pass


def _relative(project: Path, path: Path) -> str:
    return path.relative_to(project).as_posix()


def _read(project: Path, path: Path) -> str:
    try:
        return path.read_text()
    except OSError as exc:
        raise ValidateError(f"No se puede leer '{_relative(project, path)}': {exc}") from exc


def _load_mapping(project: Path, path: Path) -> dict:
    try:
        data = yaml.safe_load(_read(project, path))
    except yaml.YAMLError as exc:
        raise ValidateError(f"YAML ilegible en '{_relative(project, path)}': {exc}") from exc
    if not isinstance(data, dict):
        raise ValidateError(f"'{_relative(project, path)}' no es un mapeo YAML.")
    return data


def _documents(
    project: Path, patterns: tuple[str, ...], field: str, skip_suffixes: tuple[str, ...] = ()
) -> tuple[dict, list[str]]:
    identities: dict[str, Path] = {}
    problems: list[str] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for path in sorted(project.rglob(pattern)):
            if "hactors" in path.relative_to(project).parts or path in seen:
                continue
            if path.name.endswith(skip_suffixes):
                continue
            seen.add(path)
            try:
                identity = document_identity(_read(project, path), field)
            except (DocumentError, ValidateError) as exc:
                problems.append(f"{_relative(project, path)}: {exc}")
                continue
            if identity is None:
                problems.append(f"{_relative(project, path)}: no declara '{field}:'.")
                continue
            if identity in identities:
                problems.append(
                    f"{_relative(project, path)}: identidad '{identity}' repetida; "
                    f"ya la declara {_relative(project, identities[identity])}."
                )
                continue
            identities[identity] = path
    return identities, problems


def _run_manifests(project: Path):
    hactors = project / "hactors"
    if hactors.is_symlink() or not hactors.is_dir():
        return
    for manifest in sorted(hactors.rglob("manifest.yaml")):
        match = RUN_PATTERN.fullmatch(manifest.parent.name)
        if match:
            yield match[1], manifest.parent, manifest


def _run_identity(project: Path, run_type: str, directory: Path, manifest: Path) -> dict:
    data = _load_mapping(project, manifest)
    if run_type == "workflow_run":
        data = data.get(directory.name, {})
        if not isinstance(data, dict):
            raise ValidateError(f"'{_relative(project, manifest)}' no envuelve su workflow_run con un mapeo.")
    identity = data.get("identity")
    return identity if isinstance(identity, dict) else {}


def _task_statuses(project: Path) -> tuple[dict, list[str]]:
    statuses: dict[str, str] = {}
    problems: list[str] = []
    tasks = project / "tasks"
    if tasks.is_symlink() or not tasks.is_dir():
        return statuses, problems
    for path in sorted(tasks.glob("TASK-*.md")):
        try:
            execution = front_matter(_read(project, path)).get("execution")
        except (DocumentError, ValidateError) as exc:
            problems.append(f"{_relative(project, path)}: {exc}")
            continue
        status = execution.get("status") if isinstance(execution, dict) else None
        statuses[path.stem] = status if isinstance(status, str) else ""
    return statuses, problems


def _harness_package(project: Path, reference: str) -> Path:
    match = HARNESS_REF_PATTERN.fullmatch(reference)
    if not match:
        raise ValidateError(
            f"Referencia de HARNESS inválida: '{reference}'; se espera 'HRN-nnnnn@vNNN'."
        )
    harness_id, version = match.groups()
    return project / "harnesses" / harness_id / "versions" / version / "harness.yaml"


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
        identity = _run_identity(project, "workflow_run", manifest.parent, manifest)
    except ValidateError:
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
    for run_type, directory, manifest in _run_manifests(project):
        field = REFERENCE_FIELDS.get(run_type)
        if field is None:
            continue
        where = _relative(project, directory)
        try:
            identity = _run_identity(project, run_type, directory, manifest)
        except ValidateError as exc:
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
                package = _harness_package(project, reference)
            except ValidateError as exc:
                findings.append(f"{where}: {exc}")
                continue
            expected = _relative(project, package)
            resolved = package.is_file()
        if not resolved:
            findings.append(f"{where}: `{field}` '{reference}' no resuelve a {expected}.")
    return findings


def _check_blocking_findings(project: Path, statuses: dict) -> list[str]:
    findings: list[str] = []
    for path in sorted(project.rglob("FND-*.yaml")):
        if not FINDING_FILE_PATTERN.fullmatch(path.name):
            continue
        where = _relative(project, path)
        try:
            data = _load_mapping(project, path)
        except ValidateError as exc:
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
        where = _relative(project, path)
        try:
            findings.extend(f"{where}: {item}" for item in validate_rfc_actions(_read(project, path)))
        except (ActionSchemaError, ValidateError) as exc:
            findings.append(f"{where}: {exc}")
    return findings


def validate_project(root: Path, project_name: str) -> list[str]:
    project = require_project_directory(root, project_name)
    rfc_ids, findings = _documents(project, ("rfcs/*.md",), "rfc", skip_suffixes=(SUMMARY_SUFFIX,))
    plan_ids, plan_problems = _documents(
        project, tuple(f"{location}/*.md" for location in PLAN_LOCATIONS), "id"
    )
    statuses, task_problems = _task_statuses(project)
    findings.extend(plan_problems)
    findings.extend(task_problems)
    findings.extend(_check_references(project, rfc_ids, plan_ids))
    findings.extend(_check_blocking_findings(project, statuses))
    findings.extend(_check_actions(project, rfc_ids))
    return findings

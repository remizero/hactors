import re
from pathlib import Path

import yaml

from .documents import DocumentError, document_identity, front_matter, yaml_blocks
from .paths import RUN_PATTERN
from .summary import SUMMARY_FILENAME, SUMMARY_SUFFIX

DECISIONS_DIRNAME = "decisions"
HARNESSES_DIRNAME = "harnesses"
RFCS_DIRNAME = "rfcs"
TASKS_DIRNAME = "tasks"
PLAN_LOCATIONS = ("plans", "docs/plans")
EVIDENCE_FILE_PATTERN = re.compile(r"EVD-[0-9]{5,}\.yaml")
FINDING_FILE_PATTERN = re.compile(r"FND-[0-9]{5,}\.yaml")
RECORD_FILE_PATTERNS = (EVIDENCE_FILE_PATTERN, FINDING_FILE_PATTERN)
ADR_FILE_PATTERN = re.compile(r"ADR-[0-9]{5,}")
HARNESS_REF_PATTERN = re.compile(r"(HRN-[0-9]{5,})@(v[0-9]{3,})")
SUMMARY_PATTERNS = (f"{RFCS_DIRNAME}/*{SUMMARY_SUFFIX}", f"hactors/*/{SUMMARY_FILENAME}")
REFERENCE_FIELDS = {
    "workflow_run": "task_ref",
    "rfc_run": "rfc_ref",
    "plan_run": "plan_ref",
    "test_run": "test_ref",
    "harness_run": "harness_ref",
}
STATE_BLOCKS = {"workflow_run": "global_state"}
RUN_STATE_BLOCK = "state"


class ScanError(Exception):
    pass


def relative(project: Path, path: Path) -> str:
    return path.relative_to(project).as_posix()


def read(project: Path, path: Path) -> str:
    try:
        return path.read_text()
    except OSError as exc:
        raise ScanError(f"No se puede leer '{relative(project, path)}': {exc}") from exc


def load_mapping(project: Path, path: Path) -> dict:
    try:
        data = yaml.safe_load(read(project, path))
    except yaml.YAMLError as exc:
        raise ScanError(f"YAML ilegible en '{relative(project, path)}': {exc}") from exc
    if not isinstance(data, dict):
        raise ScanError(f"'{relative(project, path)}' no es un mapeo YAML.")
    return data


def documents(
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
                identity = document_identity(read(project, path), field)
            except (DocumentError, ScanError) as exc:
                problems.append(f"{relative(project, path)}: {exc}")
                continue
            if identity is None:
                problems.append(f"{relative(project, path)}: no declara '{field}:'.")
                continue
            if identity in identities:
                problems.append(
                    f"{relative(project, path)}: identidad '{identity}' repetida; "
                    f"ya la declara {relative(project, identities[identity])}."
                )
                continue
            identities[identity] = path
    return identities, problems


def blocks(project: Path, path: Path) -> list:
    try:
        return yaml_blocks(read(project, path))
    except (DocumentError, ScanError) as exc:
        raise ScanError(str(exc)) from exc


def header(project: Path, path: Path) -> dict:
    try:
        return front_matter(read(project, path))
    except (DocumentError, ScanError) as exc:
        raise ScanError(str(exc)) from exc


def task_documents(project: Path) -> tuple[dict, list[str]]:
    headers: dict[str, dict] = {}
    problems: list[str] = []
    tasks = project / TASKS_DIRNAME
    if tasks.is_symlink() or not tasks.is_dir():
        return headers, problems
    for path in sorted(tasks.glob("TASK-*.md")):
        try:
            headers[path.stem] = header(project, path)
        except ScanError as exc:
            headers[path.stem] = {}
            problems.append(f"{relative(project, path)}: {exc}")
    return headers, problems


def adr_documents(project: Path) -> list[tuple[str, Path]]:
    decisions = project / DECISIONS_DIRNAME
    if decisions.is_symlink() or not decisions.is_dir():
        return []
    found = []
    for path in sorted(decisions.glob("ADR-*.md")):
        match = ADR_FILE_PATTERN.match(path.name)
        if match:
            found.append((match[0], path))
    return found


def summary_documents(project: Path) -> list[Path]:
    found: set[Path] = set()
    for pattern in SUMMARY_PATTERNS:
        found.update(project.rglob(pattern))
    return sorted(found)


def record_files(project: Path) -> list[tuple[str, Path]]:
    records = []
    for path in sorted(project.rglob("*.yaml")):
        if any(pattern.fullmatch(path.name) for pattern in RECORD_FILE_PATTERNS):
            records.append((path.stem, path))
    return records


def harness_package(project: Path, reference: str) -> Path:
    match = HARNESS_REF_PATTERN.fullmatch(reference)
    if not match:
        raise ScanError(
            f"Referencia de HARNESS inválida: '{reference}'; se espera 'HRN-nnnnn@vNNN'."
        )
    harness_id, version = match.groups()
    return project / HARNESSES_DIRNAME / harness_id / "versions" / version / "harness.yaml"


def harness_catalogs(project: Path) -> tuple[list, list[str]]:
    catalogs: list[tuple[str, Path, dict]] = []
    problems: list[str] = []
    harnesses = project / HARNESSES_DIRNAME
    if harnesses.is_symlink() or not harnesses.is_dir():
        return catalogs, problems
    for path in sorted(harnesses.glob("HRN-*/manifest.yaml")):
        where = relative(project, path)
        try:
            data = load_mapping(project, path)
        except ScanError as exc:
            problems.append(str(exc))
            continue
        identity = data.get("id")
        catalogs.append(
            (identity if isinstance(identity, str) and identity else path.parent.name, path, data)
        )
        if not isinstance(identity, str) or not identity:
            problems.append(f"{where}: no declara 'id:'.")
    return catalogs, problems


def run_manifests(project: Path):
    hactors = project / "hactors"
    if hactors.is_symlink() or not hactors.is_dir():
        return
    for manifest in sorted(hactors.rglob("manifest.yaml")):
        match = RUN_PATTERN.fullmatch(manifest.parent.name)
        if match:
            yield match[1], manifest.parent, manifest


def run_identity(project: Path, run_type: str, directory: Path, manifest: Path) -> dict:
    data = load_mapping(project, manifest)
    if run_type == "workflow_run":
        data = data.get(directory.name, {})
        if not isinstance(data, dict):
            raise ScanError(
                f"'{relative(project, manifest)}' no envuelve su workflow_run con un mapeo."
            )
    identity = data.get("identity")
    return identity if isinstance(identity, dict) else {}


def run_manifest(project: Path, run_type: str, directory: Path, manifest: Path) -> dict:
    data = load_mapping(project, manifest)
    if run_type == "workflow_run":
        wrapped = data.get(directory.name, {})
        data = wrapped if isinstance(wrapped, dict) else {}
    return data

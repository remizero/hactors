import json
from datetime import date, datetime, timezone
from pathlib import Path

from .action import ActionSchemaError, extract_actions
from .paths import RUN_PATTERN, VIEWS_DIRNAME, project_candidates, require_project_directory
from .scan import (
    EVIDENCE_FILE_PATTERN,
    PLAN_LOCATIONS,
    REFERENCE_FIELDS,
    RFCS_DIRNAME,
    RUN_STATE_BLOCK,
    STATE_BLOCKS,
    TASKS_DIRNAME,
    TESTS_DIRNAME,
    ScanError,
    adr_documents,
    blocks,
    documents,
    harness_catalogs,
    header,
    load_mapping,
    read,
    record_files,
    relative,
    run_manifest,
    run_manifests,
    summary_documents,
    task_documents,
)
from .summary import SUMMARY_SUFFIX
from .validate import validate_project

MODEL_SCHEMA = "hactors-model/1.0"
MODEL_FILENAME = "project.json"
PROJECT_FILE = "project.yaml"
MANIFEST_FILE = "manifest.yaml"


class ModelError(Exception):
    pass


def build_model(root: Path, project_name: str) -> dict:
    project = require_project_directory(root, project_name)
    try:
        manifest = load_mapping(project, project / MANIFEST_FILE)
    except ScanError:
        manifest = {}

    artifacts: list[dict] = []
    for family in (_tasks, _rfcs, _plans, _tests, _decisions, _summaries, _records, _harnesses):
        artifacts.extend(family(project))

    counters = manifest.get("counters")
    relations = manifest.get("relations")
    return {
        "schema": MODEL_SCHEMA,
        "project": project_name,
        "description": _description(project),
        "generated_at": generated_at(),
        "counters": _jsonable(counters) if isinstance(counters, dict) else {},
        "artifacts": artifacts,
        "edges": [_jsonable(edge) for edge in relations if isinstance(edge, dict)]
        if isinstance(relations, list)
        else [],
        "runs": _runs(project),
        "problems": validate_project(root, project_name),
    }


def root_models(root: Path) -> list[dict]:
    entries = []
    for name in project_candidates(root):
        try:
            entries.append({"name": name, "model": build_model(root, name), "error": ""})
        except (ValueError, ScanError) as exc:
            entries.append({"name": name, "model": {}, "error": str(exc)})
    return entries


def generated_at() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_model(root: Path, project_name: str) -> Path:
    try:
        project = require_project_directory(root, project_name)
        model = build_model(root, project_name)
        directory = project / VIEWS_DIRNAME
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / MODEL_FILENAME
        path.write_text(json.dumps(model, indent=2, ensure_ascii=False, sort_keys=False) + "\n")
    except (ValueError, OSError, TypeError, ScanError) as exc:
        raise ModelError(str(exc)) from exc
    return path


def _jsonable(value):
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _text(data: dict, field: str) -> str:
    value = data.get(field)
    return value if isinstance(value, str) else ""


def _stamp(value) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value if isinstance(value, str) else ""


def _entry(kind: str, identity: str, path: str, title: str = "", status: str = "", actor: str = "", **extra) -> dict:
    entry = {"id": identity, "kind": kind, "path": path, "title": title, "status": status, "actor": actor}
    entry.update(extra)
    return entry


def _mapping(project: Path, path: Path) -> dict:
    try:
        return load_mapping(project, path)
    except ScanError:
        return {}


def _header(project: Path, path: Path) -> dict:
    try:
        return header(project, path)
    except ScanError:
        return {}


def _block(project: Path, path: Path, field: str) -> dict:
    for candidate in blocks(project, path):
        if isinstance(candidate, dict) and candidate.get(field):
            return candidate
    return {}


def _description(project: Path) -> str:
    path = project / PROJECT_FILE
    if not path.is_file():
        return ""
    return _text(_mapping(project, path), "description")


def _tasks(project: Path) -> list[dict]:
    headers, _ = task_documents(project)
    entries = []
    for stem, data in sorted(headers.items()):
        execution = data.get("execution")
        status = _text(execution, "status") if isinstance(execution, dict) else ""
        entries.append(
            _entry(
                "task", stem, f"{TASKS_DIRNAME}/{stem}.md",
                _text(data, "task"), status, _text(data, "actor"),
            )
        )
    return entries


def _actions(project: Path, path: Path) -> list[dict]:
    try:
        declared = extract_actions(read(project, path))
    except (ActionSchemaError, ScanError):
        return []
    if not isinstance(declared, list):
        return []
    return [
        {
            "id": _text(element, "id"),
            "type": _text(element, "type"),
            "status": _text(element, "status"),
            "actor": _text(element, "actor"),
        }
        for element in declared
        if isinstance(element, dict)
    ]


def _rfcs(project: Path) -> list[dict]:
    identities, _ = documents(
        project, (f"{RFCS_DIRNAME}/*.md",), "rfc", skip_suffixes=(SUMMARY_SUFFIX,)
    )
    entries = []
    for identity, path in sorted(identities.items(), key=lambda item: relative(project, item[1])):
        block = _block(project, path, "rfc")
        entries.append(
            _entry(
                "rfc", identity, relative(project, path),
                _text(block, "title"), _text(block, "status"),
                actions=_actions(project, path),
            )
        )
    return entries


def _plans(project: Path) -> list[dict]:
    identities, _ = documents(
        project, tuple(f"{location}/*.md" for location in PLAN_LOCATIONS), "id"
    )
    entries = []
    for identity, path in sorted(identities.items(), key=lambda item: relative(project, item[1])):
        block = _block(project, path, "id")
        entries.append(
            _entry(
                "plan", identity, relative(project, path),
                _text(block, "title"), _text(block, "status"),
            )
        )
    return entries


def _tests(project: Path) -> list[dict]:
    identities, _ = documents(project, (f"{TESTS_DIRNAME}/*.md",), "id")
    entries = []
    for identity, path in sorted(identities.items(), key=lambda item: relative(project, item[1])):
        block = _block(project, path, "id")
        entries.append(
            _entry(
                "test", identity, relative(project, path),
                _text(block, "title"), _text(block, "status"),
            )
        )
    return entries


def _decisions(project: Path) -> list[dict]:
    entries = []
    for identity, path in adr_documents(project):
        data = _header(project, path)
        entries.append(
            _entry(
                "adr", identity, relative(project, path),
                _text(data, "title"), _text(data, "status"),
            )
        )
    return entries


def _summaries(project: Path) -> list[dict]:
    entries = []
    for path in summary_documents(project):
        data = _header(project, path)
        entries.append(
            _entry(
                "summary", _text(data, "artifact"), relative(project, path),
                _text(data, "title"), _text(data, "status"),
            )
        )
    return entries


def _records(project: Path) -> list[dict]:
    entries = []
    for stem, path in record_files(project):
        evidence = bool(EVIDENCE_FILE_PATTERN.fullmatch(path.name))
        data = _mapping(project, path)
        entries.append(
            _entry(
                "evidence" if evidence else "finding",
                stem,
                relative(project, path),
                _text(data, "title"),
                "" if evidence else _text(data, "state"),
            )
        )
    return entries


def _harnesses(project: Path) -> list[dict]:
    catalogs, _ = harness_catalogs(project)
    entries = []
    for identity, path, data in catalogs:
        versions = []
        declared = data.get("versions")
        if isinstance(declared, list):
            for version in declared:
                if not isinstance(version, dict):
                    continue
                number = version.get("version")
                versions.append({
                    "version": number if isinstance(number, int) else "",
                    "status": _text(version, "status"),
                    "published": _stamp(version.get("published")),
                })
        entries.append(
            _entry(
                "harness", identity, relative(project, path), _text(data, "title"),
                versions=versions,
            )
        )
    return entries


def _runs(project: Path) -> list[dict]:
    entries = []
    for run_type, directory, manifest in run_manifests(project):
        try:
            data = run_manifest(project, run_type, directory, manifest)
        except ScanError:
            continue
        identity = data.get("identity")
        identity = identity if isinstance(identity, dict) else {}
        block = data.get(STATE_BLOCKS.get(run_type, RUN_STATE_BLOCK))
        block = block if isinstance(block, dict) else {}
        field = REFERENCE_FIELDS.get(run_type, "")
        parent = directory.parent.name
        entries.append({
            "id": _text(identity, "id") or directory.name,
            "kind": run_type,
            "path": relative(project, directory),
            "status": _text(block, "status"),
            "reference": _text(identity, field) if field else "",
            "parent": parent if RUN_PATTERN.fullmatch(parent) else "",
            "blocked_reason": _text(block, "blocked_reason"),
        })
    return entries

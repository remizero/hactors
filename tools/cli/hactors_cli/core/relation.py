from pathlib import Path

import yaml

from .counters import persist_manifest
from .paths import require_project_directory
from .validate import ValidateError, artifact_identities, target_problem

RELATION_FIELDS = ("source", "target", "relation")


class RelationError(Exception):
    pass


def relate(root: Path, project_name: str, source: str, target: str, relation: str) -> Path:
    try:
        project = require_project_directory(root, project_name)
        edge = _checked_edge(project, source, target, relation)
        manifest = project / "manifest.yaml"
        with manifest.open() as f:
            data = yaml.safe_load(f)
        recorded = data.get("relations")
        if recorded is None:
            recorded = []
        if not isinstance(recorded, list):
            raise ValueError(f"`relations` debe ser una lista, no {type(recorded).__name__}.")
        _reject_duplicate(recorded, edge)
        recorded.append(edge)
        data["relations"] = recorded
        persist_manifest(manifest, data)
    except (ValueError, OSError, yaml.YAMLError, ValidateError) as exc:
        raise RelationError(str(exc)) from exc
    return manifest


def _checked_edge(project: Path, source: str, target: str, relation: str) -> dict:
    for field, value in (("source", source), ("target", target), ("relation", relation)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"`{field}` requiere un valor no vacío.")
    problem = target_problem(project, target, artifact_identities(project))
    if problem:
        raise ValueError(f"`target` '{target}' {problem}")
    return {"source": source, "target": target, "relation": relation}


def _reject_duplicate(recorded: list, edge: dict) -> None:
    for position, element in enumerate(recorded, start=1):
        if not isinstance(element, dict):
            continue
        if all(element.get(field) == edge[field] for field in RELATION_FIELDS):
            raise ValueError(
                f"La arista ya consta en relations[{position}]; el grafo no la duplica."
            )

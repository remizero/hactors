import re
from pathlib import Path

from .project import ProjectError, validate_name

HACTORS_MARKERS = ("specs/templates", "projects")


def find_hactors_root(start: Path) -> Path:
    current = start.resolve()
    for directory in [current, *current.parents]:
        if all((directory / marker).exists() for marker in HACTORS_MARKERS):
            return directory
    return current


def project_dir(root: Path, name: str) -> Path:
    return root / "projects" / name


def require_run_directory(root: Path, project_name: str, *run_ids: str) -> Path:
    if not isinstance(project_name, str):
        raise ValueError("Nombre de proyecto inválido en el contexto activo.")
    try:
        validate_name(project_name)
    except ProjectError as exc:
        raise ValueError(str(exc)) from exc

    project = project_dir(root, project_name)
    if not project.resolve().is_relative_to((root / "projects").resolve()):
        raise ValueError("El proyecto está fuera del directorio projects.")
    if not project.is_dir() or not (project / "manifest.yaml").is_file():
        raise ValueError(f"Proyecto no encontrado o sin manifest: '{project_name}'.")
    if not (project / "manifest.yaml").resolve().is_relative_to(project.resolve()):
        raise ValueError("El manifest del proyecto está fuera de su directorio.")

    directory = project / "hactors"
    for prefix, run_id in zip(("workflow_run", "task_run", "rfc_run"), run_ids):
        if not isinstance(run_id, str) or not re.fullmatch(rf"{prefix}_[0-9]{{6,}}", run_id):
            raise ValueError(f"Identificador de {prefix} inválido: '{run_id}'.")
        directory /= run_id
        if not directory.resolve().is_relative_to(project.resolve()):
            raise ValueError(f"El {prefix} está fuera del directorio del proyecto.")
        if not directory.is_dir() or not (directory / "manifest.yaml").is_file():
            raise ValueError(f"{prefix} no encontrado o sin manifest: '{run_id}'.")
    return directory

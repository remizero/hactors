import re
from pathlib import Path

import yaml

from .project import ProjectError, validate_name

HACTORS_MARKERS = ("specs/templates", "projects")
RUN_PATTERN = re.compile(r"(workflow_run|task_run|rfc_run|plan_run|test_run|harness_run)_[0-9]{6,}")
RUN_CHILD_TYPES = {
    "hactors": ("workflow_run",),
    "workflow_run": ("task_run",),
    "task_run": ("rfc_run",),
    "rfc_run": ("plan_run", "test_run"),
    "plan_run": ("rfc_run",),
    "test_run": ("harness_run",),
    "harness_run": (),
}


def find_hactors_root(start: Path) -> Path:
    current = start.resolve()
    for directory in [current, *current.parents]:
        if all((directory / marker).exists() for marker in HACTORS_MARKERS):
            return directory
    return current


def project_dir(root: Path, name: str) -> Path:
    return root / "projects" / name


def _load_manifest(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise ValueError(f"Manifest YAML inválido: '{path}'.") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Manifest inválido: '{path}'.")
    return data


def require_project_directory(root: Path, project_name: str) -> Path:
    if not isinstance(project_name, str):
        raise ValueError("Nombre de proyecto inválido en el contexto activo.")
    try:
        validate_name(project_name)
    except ProjectError as exc:
        raise ValueError(str(exc)) from exc

    project = project_dir(root, project_name)
    if not project.resolve().is_relative_to((root / "projects").resolve()):
        raise ValueError("El proyecto está fuera del directorio projects.")
    manifest = project / "manifest.yaml"
    if not project.is_dir() or not manifest.is_file():
        raise ValueError(f"Proyecto no encontrado o sin manifest: '{project_name}'.")
    if not manifest.resolve().is_relative_to(project.resolve()):
        raise ValueError("El manifest del proyecto está fuera de su directorio.")
    if _load_manifest(manifest).get("project") != project_name:
        raise ValueError("El nombre del proyecto no coincide con su manifest.")
    return project


def require_run_directory(
    root: Path, project_name: str, run_path: str, child_type: str = ""
) -> Path:
    project = require_project_directory(root, project_name)
    if not isinstance(run_path, str):
        raise ValueError("Ruta de ejecución inválida: se requiere una cadena.")
    parts = run_path.split("/")
    if len(parts) < 2 or parts[0] != "hactors":
        raise ValueError("Ruta de ejecución inválida: use una ruta completa desde 'hactors/'.")

    directory = project / "hactors"
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("El directorio hactors no existe o es un enlace simbólico.")
    parent_type = "hactors"
    seen = set()
    for run_id in parts[1:]:
        match = RUN_PATTERN.fullmatch(run_id)
        if not match:
            raise ValueError(f"Identificador inválido en la ruta de ejecución: '{run_id}'.")
        run_type = match[1]
        if run_type not in RUN_CHILD_TYPES[parent_type]:
            raise ValueError(f"Jerarquía inválida: {run_type} no puede vivir dentro de {parent_type}.")
        if run_id in seen:
            raise ValueError(f"Identificador repetido en la ruta: '{run_id}'.")
        seen.add(run_id)
        directory /= run_id
        manifest = directory / "manifest.yaml"
        if directory.is_symlink() or manifest.is_symlink():
            raise ValueError("La ruta de ejecución no admite enlaces simbólicos.")
        if not directory.is_dir() or not manifest.is_file():
            raise ValueError(f"{run_type} no encontrado o sin manifest: '{run_id}'.")
        if not directory.resolve().is_relative_to(project.resolve()):
            raise ValueError("La ejecución está fuera del directorio del proyecto.")
        data = _load_manifest(manifest)
        if run_type == "workflow_run":
            if set(data) != {run_id} or not isinstance(data[run_id], dict):
                raise ValueError("La clave envolvente del manifest no coincide con el workflow_run.")
            data = data[run_id]
        identity = data.get("identity")
        if not isinstance(identity, dict) or identity.get("id") != run_id:
            raise ValueError(f"La identidad del manifest no coincide con '{run_id}'.")
        parent_type = run_type

    if child_type and child_type not in RUN_CHILD_TYPES[parent_type]:
        raise ValueError(
            f"No se puede crear un {child_type} dentro de un {parent_type}. "
            "Seleccione el padre con 'hactors use-run <ruta>'."
        )
    return directory


def resolve_origin(root: Path, project_name: str, project: Path, origin: str) -> tuple[Path, str]:
    if not isinstance(origin, str) or not origin.strip():
        raise ValueError("Origen inválido: use una ruta relativa al proyecto.")
    parts = origin.split("/")
    if Path(origin).is_absolute() or "\\" in origin or any(part in ("", ".", "..") for part in parts):
        raise ValueError("Origen inválido: use una ruta relativa al proyecto sin '.' ni '..'.")
    if parts[0] == "hactors":
        if len(parts) < 2:
            raise ValueError("Origen inválido: 'hactors' no identifica una ejecución ni un artefacto.")
        return require_run_directory(root, project_name, origin), "execution"

    path = project / origin
    if path.is_symlink():
        raise ValueError("El origen no admite enlaces simbólicos.")
    if not path.exists():
        raise ValueError(f"Artefacto de origen no encontrado: '{origin}'.")
    if not path.resolve().is_relative_to(project.resolve()):
        raise ValueError("El origen está fuera del directorio del proyecto.")
    return (path if path.is_dir() else path.parent), "artifact"

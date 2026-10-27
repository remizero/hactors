import re
from datetime import datetime, timezone
from pathlib import Path

from .templates import load_template, render_manifest_yaml, render_project_yaml

PROJECT_SUBDIRS = ("hactors", "rfcs", "standards")
PROJECT_TEMPLATE = "project_template.yaml"
MANIFEST_TEMPLATE = "manifest_template.yaml"
NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
NAME_MAX_LENGTH = 64


class ProjectError(Exception):
    pass


class ProjectAlreadyExistsError(ProjectError):
    pass


class InvalidProjectNameError(ProjectError):
    pass


def validate_name(name: str) -> None:
    if not name:
        raise InvalidProjectNameError("El nombre del proyecto no puede estar vacío.")
    if len(name) > NAME_MAX_LENGTH:
        raise InvalidProjectNameError(
            f"El nombre excede {NAME_MAX_LENGTH} caracteres: '{name}'."
        )
    if not NAME_PATTERN.match(name):
        raise InvalidProjectNameError(
            f"Nombre inválido '{name}'. Solo se permiten letras, dígitos, guion y guion bajo."
        )


def create_project(name: str, hactors_root: Path, description: str = "") -> Path:
    validate_name(name)

    target = hactors_root / "projects" / name
    if target.exists():
        raise ProjectAlreadyExistsError(
            f"Ya existe un proyecto en '{target}'."
        )

    for subdir in PROJECT_SUBDIRS:
        (target / subdir).mkdir(parents=True, exist_ok=True)

    project_template = load_template(hactors_root, PROJECT_TEMPLATE)
    manifest_template = load_template(hactors_root, MANIFEST_TEMPLATE)

    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    (target / "project.yaml").write_text(
        render_project_yaml(project_template, name, created_at, description)
    )
    (target / "manifest.yaml").write_text(
        render_manifest_yaml(manifest_template, name)
    )

    return target

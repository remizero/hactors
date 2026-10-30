from pathlib import Path
from typing import Optional

import yaml

from .counters import next_evidence_id
from .paths import require_project_directory, require_run_directory
from .templates import load_template, render_yaml

EVIDENCE_TEMPLATE = "evidence_template.yaml"
EXECUTION_ROOT = "hactors"


class EvidenceError(Exception):
    pass


def _origin_location(root: Path, project_name: str, project: Path, origin: str) -> tuple[Path, str]:
    if not isinstance(origin, str) or not origin.strip():
        raise ValueError("Origen inválido: use una ruta relativa al proyecto.")
    parts = origin.split("/")
    if Path(origin).is_absolute() or "\\" in origin or any(part in ("", ".", "..") for part in parts):
        raise ValueError("Origen inválido: use una ruta relativa al proyecto sin '.' ni '..'.")
    if parts[0] == EXECUTION_ROOT:
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


def create_evidence(
    root: Path,
    project_name: str,
    origin: str,
    title: Optional[str] = None,
    kind: Optional[str] = None,
    recorded: Optional[str] = None,
) -> Path:
    try:
        project = require_project_directory(root, project_name)
        directory, source_field = _origin_location(root, project_name, project, origin)
        template = load_template(root, EVIDENCE_TEMPLATE)
        if not isinstance(template.get("source"), dict):
            raise ValueError("La plantilla de evidencia requiere un bloque source.")
        data = dict(template)
        for field, value in (("title", title), ("kind", kind), ("recorded", recorded)):
            if value is not None:
                data[field] = value
        source = dict(template["source"])
        source[source_field] = origin
        data["source"] = source
        evidence_id, _ = next_evidence_id(project / "manifest.yaml", directory)
        data["id"] = evidence_id
        path = directory / f"{evidence_id}.yaml"
        path.write_text(render_yaml(data))
    except FileExistsError as exc:
        raise EvidenceError(f"Ya existe una evidencia en '{exc.filename}'.") from exc
    except (ValueError, OSError, yaml.YAMLError) as exc:
        raise EvidenceError(str(exc)) from exc
    return path

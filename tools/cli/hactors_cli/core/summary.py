import errno
from pathlib import Path, PurePosixPath
from typing import Optional

import yaml

from .paths import require_project_directory, resolve_origin
from .templates import load_template, render_frontmatter

SUMMARY_TEMPLATE = "summary_template.yaml"
SUMMARY_FILENAME = "SUMMARY.md"
SUMMARY_SUFFIX = " - Summary.md"
SUMMARY_REFERENCE = "Estructura y secciones: `specs/templates/SUMMARY_TEMPLATE.md`."


class SummaryError(Exception):
    pass


def render_summary(data: dict) -> str:
    return render_frontmatter(data, SUMMARY_REFERENCE)


def create_summary(
    root: Path,
    project_name: str,
    origin: str,
    title: Optional[str] = None,
    status: Optional[str] = None,
    final_state: Optional[str] = None,
    target_state: Optional[str] = None,
    date: Optional[str] = None,
) -> Path:
    try:
        project = require_project_directory(root, project_name)
        directory, source_field = resolve_origin(root, project_name, project, origin)
        template = load_template(root, SUMMARY_TEMPLATE)
        data = dict(template)
        for field, value in (
            ("title", title), ("status", status), ("final_state", final_state),
            ("target_state", target_state), ("date", date),
        ):
            if value is not None:
                data[field] = value
        data["artifact"] = origin
        data["level"] = "workflow_run" if source_field == "execution" else "rfc"
        path = _summary_path(project, directory, origin, source_field)
        if path.exists() or path.is_symlink():
            raise FileExistsError(errno.EEXIST, "Ya existe un resumen", str(path))
        path.write_text(render_summary(data))
    except FileExistsError as exc:
        raise SummaryError(f"Ya existe un resumen en '{exc.filename}'.") from exc
    except (ValueError, OSError, yaml.YAMLError) as exc:
        raise SummaryError(str(exc)) from exc
    return path


def _summary_path(project: Path, directory: Path, origin: str, source_field: str) -> Path:
    parts = PurePosixPath(origin).parts
    if source_field == "execution":
        if len(parts) != 2:
            raise ValueError(
                "Solo un workflow_run tiene resumen propio; lo registrado en las instancias "
                "intermedias se agrega al resumen de su RFC o al global."
            )
        return directory / SUMMARY_FILENAME
    target = project / origin
    if parts[0] != "rfcs" or len(parts) != 2 or not target.is_file():
        raise ValueError(
            "El resumen de una RFC se crea junto a su archivo en 'rfcs/'; "
            f"origen inválido: '{origin}'."
        )
    return directory / f"{target.stem}{SUMMARY_SUFFIX}"

import re
from pathlib import Path
from typing import Optional

import yaml

from .counters import next_adr_id
from .paths import require_project_directory
from .templates import load_template, render_frontmatter

ADR_TEMPLATE = "adr_template.yaml"
DECISIONS_DIRNAME = "decisions"
NAME_SEPARATOR = " — "
ADR_REFERENCE = "Estructura y secciones: `specs/templates/ADR_TEMPLATE.md`."
SLUG_SEPARATOR = re.compile(r"\W+")


class AdrError(Exception):
    pass


def render_adr(data: dict) -> str:
    return render_frontmatter(data, ADR_REFERENCE)


def descriptive_name(title: str) -> str:
    if not isinstance(title, str):
        raise ValueError(f"El título de una decisión debe ser textual, no {type(title).__name__}.")
    name = SLUG_SEPARATOR.sub("-", title.strip().lower()).strip("-")
    if not name:
        raise ValueError(f"El título no produce un nombre descriptivo: '{title}'.")
    return name


def create_adr(
    root: Path,
    project_name: str,
    title: str,
    status: Optional[str] = None,
    date: Optional[str] = None,
) -> tuple[str, Path]:
    try:
        project = require_project_directory(root, project_name)
        directory = project / DECISIONS_DIRNAME
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"El directorio '{DECISIONS_DIRNAME}/' del proyecto no existe.")
        data = dict(load_template(root, ADR_TEMPLATE))
        for field, value in (("title", title), ("status", status), ("date", date)):
            if value is not None:
                data[field] = value
        suffix = f"{NAME_SEPARATOR}{descriptive_name(title)}.md"
        adr_id, _ = next_adr_id(project / "manifest.yaml", directory, suffix)
        data["adr"] = adr_id
        path = directory / f"{adr_id}{suffix}"
        path.write_text(render_adr(data))
    except FileExistsError as exc:
        raise AdrError(f"Ya existe una decisión en '{exc.filename}'.") from exc
    except (ValueError, OSError, yaml.YAMLError) as exc:
        raise AdrError(str(exc)) from exc
    return adr_id, path

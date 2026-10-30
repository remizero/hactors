from pathlib import Path
from typing import Optional

import yaml

from .counters import next_finding_id
from .paths import require_project_directory, resolve_origin
from .templates import load_template, render_yaml

FINDING_TEMPLATE = "finding_template.yaml"


class FindingError(Exception):
    pass


def create_finding(
    root: Path,
    project_name: str,
    origin: str,
    title: Optional[str] = None,
    kind: Optional[str] = None,
    severity: Optional[str] = None,
    opened: Optional[str] = None,
    updated: Optional[str] = None,
) -> tuple[str, Path]:
    try:
        project = require_project_directory(root, project_name)
        directory, source_field = resolve_origin(root, project_name, project, origin)
        template = load_template(root, FINDING_TEMPLATE)
        if not isinstance(template.get("source"), dict):
            raise ValueError("La plantilla de hallazgo requiere un bloque source.")
        data = dict(template)
        for field, value in (
            ("title", title), ("kind", kind), ("severity", severity),
            ("opened", opened), ("updated", updated),
        ):
            if value is not None:
                data[field] = value
        source = dict(template["source"])
        source[source_field] = origin
        data["source"] = source
        finding_id, _ = next_finding_id(project / "manifest.yaml", directory)
        data["id"] = finding_id
        path = directory / f"{finding_id}.yaml"
        path.write_text(render_yaml(data))
    except FileExistsError as exc:
        raise FindingError(f"Ya existe un hallazgo en '{exc.filename}'.") from exc
    except (ValueError, OSError, yaml.YAMLError) as exc:
        raise FindingError(str(exc)) from exc
    return finding_id, path

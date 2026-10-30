from pathlib import Path
from typing import Optional

import yaml

from .counters import next_evidence_id
from .paths import require_project_directory, resolve_origin
from .templates import load_template, render_yaml

EVIDENCE_TEMPLATE = "evidence_template.yaml"


class EvidenceError(Exception):
    pass


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
        directory, source_field = resolve_origin(root, project_name, project, origin)
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

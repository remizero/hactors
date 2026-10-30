from pathlib import Path
from typing import Optional

import yaml

from .counters import next_finding_id
from .paths import require_project_directory, resolve_origin
from .templates import load_template, render_yaml

FINDING_TEMPLATE = "finding_template.yaml"
FINDINGS_FILE = "findings.yaml"


class FindingError(Exception):
    pass


def _load_findings(path: Path) -> list:
    if path.is_symlink():
        raise ValueError("El registro de hallazgos no admite enlaces simbólicos.")
    if not path.is_file():
        return []
    try:
        data = yaml.safe_load(path.read_text())
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ValueError(f"Registro de hallazgos inválido: '{path}'.") from exc
    if data is None:
        return []
    if not isinstance(data, list):
        raise ValueError(f"El registro de hallazgos debe ser una lista: '{path}'.")
    if any(not isinstance(entry, dict) for entry in data):
        raise ValueError(f"El registro de hallazgos contiene una entrada que no es un mapeo: '{path}'.")
    return data


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
        _, source_field = resolve_origin(root, project_name, project, origin)
        template = load_template(root, FINDING_TEMPLATE)
        if not isinstance(template.get("source"), dict):
            raise ValueError("La plantilla de hallazgo requiere un bloque source.")
        path = project / FINDINGS_FILE
        findings = _load_findings(path)
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
        finding_id, _ = next_finding_id(
            project / "manifest.yaml", {entry.get("id") for entry in findings}
        )
        data["id"] = finding_id
        path.write_text(render_yaml([*findings, data]))
    except (ValueError, OSError, yaml.YAMLError) as exc:
        raise FindingError(str(exc)) from exc
    return finding_id, path

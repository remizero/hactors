from pathlib import Path
from typing import Optional

import yaml

from .counters import next_counter_id
from .paths import require_run_directory
from .state import set_active_run
from .templates import load_template, render_run_yaml

HARNESS_RUN_PREFIX = "harness_run"
HARNESS_RUN_TEMPLATE = "harness_run_template.yaml"


class HarnessRunError(Exception):
    pass


def create_harness_run(
    hactors_root: Path,
    project_name: str,
    parent_run_path: str,
    harness_ref: Optional[str] = None,
    content_ref: Optional[str] = None,
) -> Path:
    try:
        parent = require_run_directory(
            hactors_root, project_name, parent_run_path, child_type=HARNESS_RUN_PREFIX
        )
        template = load_template(hactors_root, HARNESS_RUN_TEMPLATE)
        if not isinstance(template.get("identity"), dict):
            raise ValueError("La plantilla de harness_run requiere un bloque identity.")
        data = {**template, "identity": dict(template["identity"])}
        if harness_ref is not None:
            data["identity"]["harness_ref"] = harness_ref
        if content_ref is not None:
            data["identity"]["content_ref"] = content_ref
        manifest_path = hactors_root / "projects" / project_name / "manifest.yaml"
        run_id, _ = next_counter_id(manifest_path, "harness_run", HARNESS_RUN_PREFIX, parent)
        run_dir = parent / run_id
        run_dir.mkdir()
        (run_dir / "manifest.yaml").write_text(render_run_yaml(data, id_value=run_id))
    except FileExistsError as exc:
        raise HarnessRunError(f"Ya existe una instancia en '{exc.filename}'.") from exc
    except (ValueError, OSError, yaml.YAMLError) as exc:
        raise HarnessRunError(str(exc)) from exc
    set_active_run(hactors_root, project_name, f"{parent_run_path}/{run_id}")
    return run_dir

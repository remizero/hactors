from pathlib import Path

import yaml

from .counters import next_counter_id
from .paths import require_run_directory
from .state import set_active_run
from .templates import load_template, render_run_yaml

RFC_RUN_PREFIX = "rfc_run"
RFC_RUN_TEMPLATE = "rfc_run_template.yaml"


class RfcRunError(Exception):
    pass


def create_rfc_run(
    hactors_root: Path,
    project_name: str,
    parent_run_path: str,
    rfc_ref: str = "",
) -> Path:
    try:
        parent = require_run_directory(
            hactors_root, project_name, parent_run_path, child_type=RFC_RUN_PREFIX
        )
        template = load_template(hactors_root, RFC_RUN_TEMPLATE)
        manifest_path = hactors_root / "projects" / project_name / "manifest.yaml"
        run_id, _ = next_counter_id(manifest_path, "rfc_run", RFC_RUN_PREFIX, parent)
        run_dir = parent / run_id
        run_dir.mkdir()
        (run_dir / "manifest.yaml").write_text(
            render_run_yaml(template, id_value=run_id, ref_value=rfc_ref, ref_field="rfc_ref")
        )
    except FileExistsError as exc:
        raise RfcRunError(f"Ya existe una instancia en '{exc.filename}'.") from exc
    except (ValueError, OSError, yaml.YAMLError) as exc:
        raise RfcRunError(str(exc)) from exc
    set_active_run(hactors_root, project_name, f"{parent_run_path}/{run_id}")
    return run_dir

from pathlib import Path

import yaml

from .counters import next_counter_id
from .paths import require_run_directory
from .state import set_active_run
from .templates import load_template, render_run_yaml

PLAN_RUN_PREFIX = "plan_run"
PLAN_RUN_TEMPLATE = "plan_run_template.yaml"


class PlanRunError(Exception):
    pass


def create_plan_run(
    hactors_root: Path,
    project_name: str,
    parent_run_path: str,
    plan_ref: str = "",
) -> Path:
    try:
        parent = require_run_directory(
            hactors_root, project_name, parent_run_path, child_type=PLAN_RUN_PREFIX
        )
        template = load_template(hactors_root, PLAN_RUN_TEMPLATE)
        manifest_path = hactors_root / "projects" / project_name / "manifest.yaml"
        run_id, _ = next_counter_id(manifest_path, "plan_run", PLAN_RUN_PREFIX, parent)
        run_dir = parent / run_id
        run_dir.mkdir()
        (run_dir / "manifest.yaml").write_text(
            render_run_yaml(template, id_value=run_id, ref_value=plan_ref, ref_field="plan_ref")
        )
    except FileExistsError as exc:
        raise PlanRunError(f"Ya existe una instancia en '{exc.filename}'.") from exc
    except (ValueError, OSError, yaml.YAMLError) as exc:
        raise PlanRunError(str(exc)) from exc
    set_active_run(hactors_root, project_name, f"{parent_run_path}/{run_id}")
    return run_dir

from pathlib import Path

from .counters import next_counter_id
from .paths import require_run_directory
from .templates import load_template, render_run_yaml

PLAN_RUN_PREFIX = "plan_run"
PLAN_RUN_TEMPLATE = "plan_run_template.yaml"


class PlanRunError(Exception):
    pass


def create_plan_run(
    hactors_root: Path,
    project_name: str,
    workflow_run_id: str,
    task_run_id: str,
    rfc_run_id: str,
    plan_ref: str = "",
) -> Path:
    try:
        rfc_dir = require_run_directory(
            hactors_root, project_name, workflow_run_id, task_run_id, rfc_run_id
        )
        template = load_template(hactors_root, PLAN_RUN_TEMPLATE)
    except (ValueError, OSError) as exc:
        raise PlanRunError(str(exc)) from exc

    manifest_path = hactors_root / "projects" / project_name / "manifest.yaml"
    run_id, _ = next_counter_id(manifest_path, "plan_run", PLAN_RUN_PREFIX)
    run_dir = rfc_dir / run_id
    try:
        run_dir.mkdir()
    except FileExistsError as exc:
        raise PlanRunError(f"Ya existe una instancia en '{run_dir}'.") from exc

    (run_dir / "manifest.yaml").write_text(
        render_run_yaml(template, id_value=run_id, ref_value=plan_ref, ref_field="plan_ref")
    )
    return run_dir

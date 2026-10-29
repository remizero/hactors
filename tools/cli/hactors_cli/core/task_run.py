from pathlib import Path

from .counters import next_counter_id
from .state import set_current_task_run
from .templates import load_template, render_run_yaml

TASK_RUN_PREFIX = "task_run"
TASK_RUN_TEMPLATE = "task_run_template.yaml"


class TaskRunError(Exception):
    pass


def create_task_run(
    hactors_root: Path,
    project_name: str,
    workflow_run_id: str,
) -> Path:
    project_dir = hactors_root / "projects" / project_name
    if not project_dir.is_dir():
        raise TaskRunError(f"Proyecto no encontrado: '{project_name}'.")

    workflow_dir = project_dir / "hactors" / workflow_run_id
    if not workflow_dir.is_dir():
        raise TaskRunError(
            f"Workflow run no encontrado: '{workflow_run_id}' en proyecto '{project_name}'."
        )

    manifest_path = project_dir / "manifest.yaml"
    run_id, _ = next_counter_id(manifest_path, "task_run", TASK_RUN_PREFIX)

    run_dir = workflow_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    template = load_template(hactors_root, TASK_RUN_TEMPLATE)
    (run_dir / "manifest.yaml").write_text(render_run_yaml(template, id_value=run_id))

    set_current_task_run(hactors_root, run_id)
    return run_dir

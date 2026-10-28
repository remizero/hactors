from pathlib import Path

from .counters import next_counter_id
from .state import set_current_workflow_run
from .templates import load_template, render_run_yaml

WORKFLOW_PREFIX = "workflow_run"
WORKFLOW_TEMPLATE = "workflow_run_manifest_template.yaml"


class WorkflowError(Exception):
    pass


def create_workflow(hactors_root: Path, project_name: str, task_ref: str = "") -> Path:
    project_dir = hactors_root / "projects" / project_name
    if not project_dir.is_dir():
        raise WorkflowError(f"Proyecto no encontrado: '{project_name}'.")

    manifest_path = project_dir / "manifest.yaml"
    run_id, _ = next_counter_id(manifest_path, "workflow_run", WORKFLOW_PREFIX)

    run_dir = project_dir / "hactors" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    template = load_template(hactors_root, WORKFLOW_TEMPLATE)
    (run_dir / "manifest.yaml").write_text(
        render_run_yaml(
            template, id_value=run_id, ref_value=task_ref, ref_field="task_ref", wrapper_key=run_id
        )
    )

    set_current_workflow_run(hactors_root, run_id)

    return run_dir

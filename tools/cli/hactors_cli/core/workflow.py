from pathlib import Path

import yaml

from .counters import next_counter_id
from .paths import require_project_directory
from .state import set_active_run
from .templates import load_template, render_run_yaml

WORKFLOW_PREFIX = "workflow_run"
WORKFLOW_TEMPLATE = "workflow_run_manifest_template.yaml"


class WorkflowError(Exception):
    pass


def create_workflow(hactors_root: Path, project_name: str, task_ref: str = "") -> Path:
    try:
        project = require_project_directory(hactors_root, project_name)
        parent = project / "hactors"
        if parent.is_symlink() or not parent.is_dir():
            raise ValueError("El directorio hactors no existe o es un enlace simbólico.")
        template = load_template(hactors_root, WORKFLOW_TEMPLATE)
        run_id, _ = next_counter_id(project / "manifest.yaml", "workflow_run", WORKFLOW_PREFIX, parent)
        run_dir = parent / run_id
        run_dir.mkdir()
        (run_dir / "manifest.yaml").write_text(
            render_run_yaml(
                template, id_value=run_id, ref_value=task_ref, ref_field="task_ref", wrapper_key=run_id
            )
        )
    except FileExistsError as exc:
        raise WorkflowError(f"Ya existe una instancia en '{exc.filename}'.") from exc
    except (ValueError, OSError, yaml.YAMLError) as exc:
        raise WorkflowError(str(exc)) from exc
    set_active_run(hactors_root, project_name, f"hactors/{run_id}")
    return run_dir

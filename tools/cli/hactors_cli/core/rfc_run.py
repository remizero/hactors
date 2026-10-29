from pathlib import Path

from .counters import next_counter_id
from .paths import require_run_directory
from .state import set_current_rfc_run
from .templates import load_template, render_run_yaml

RFC_RUN_PREFIX = "rfc_run"
RFC_RUN_TEMPLATE = "rfc_run_template.yaml"


class RfcRunError(Exception):
    pass


def create_rfc_run(
    hactors_root: Path,
    project_name: str,
    workflow_run_id: str,
    task_run_id: str,
    rfc_ref: str = "",
) -> Path:
    try:
        task_dir = require_run_directory(hactors_root, project_name, workflow_run_id, task_run_id)
        template = load_template(hactors_root, RFC_RUN_TEMPLATE)
    except (ValueError, OSError) as exc:
        raise RfcRunError(str(exc)) from exc

    manifest_path = hactors_root / "projects" / project_name / "manifest.yaml"
    run_id, _ = next_counter_id(manifest_path, "rfc_run", RFC_RUN_PREFIX)
    run_dir = task_dir / run_id
    try:
        run_dir.mkdir()
    except FileExistsError as exc:
        raise RfcRunError(f"Ya existe una instancia en '{run_dir}'.") from exc

    (run_dir / "manifest.yaml").write_text(
        render_run_yaml(template, id_value=run_id, ref_value=rfc_ref, ref_field="rfc_ref")
    )
    set_current_rfc_run(hactors_root, run_id)
    return run_dir

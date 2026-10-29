from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.state import (
    NoActiveProjectError,
    NoActiveWorkflowRunError,
    require_active_project,
    require_active_workflow_run,
)
from ..core.task_run import TaskRunError, create_task_run


@click.command("create-task-run")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def create_task_run_cmd(root: Optional[Path]) -> None:
    """Crear un nuevo task_run dentro del workflow_run activo."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())

    try:
        project_name = require_active_project(hactors_root)
        workflow_run_id = require_active_workflow_run(hactors_root)
    except (NoActiveProjectError, NoActiveWorkflowRunError) as exc:
        raise click.ClickException(str(exc)) from exc

    try:
        run_dir = create_task_run(hactors_root, project_name, workflow_run_id)
    except TaskRunError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Task run creado en: {run_dir}")

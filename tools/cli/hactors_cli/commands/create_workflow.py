from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.state import StateError, require_active_project
from ..core.workflow import WorkflowError, create_workflow


@click.command("create-workflow")
@click.option(
    "--task-ref",
    default="",
    help="Identificador de la TASK asociada.",
)
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def create_workflow_cmd(task_ref: str, root: Optional[Path]) -> None:
    """Crear un nuevo workflow_run en el proyecto activo."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())

    try:
        project_name = require_active_project(hactors_root)
        run_dir = create_workflow(hactors_root, project_name, task_ref)
    except (StateError, WorkflowError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Workflow creado en: {run_dir}")

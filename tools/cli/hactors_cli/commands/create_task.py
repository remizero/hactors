from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.state import StateError, require_active_project
from ..core.task import TaskError, create_task


@click.command("create-task")
@click.option("--task", default=None, help="Descripción breve en imperativo.")
@click.option("--actor", default=None, help="Ejecutor autorizado; se registra literalmente, sin validar el glosario.")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def create_task_cmd(task: Optional[str], actor: Optional[str], root: Optional[Path]) -> None:
    """Crear una TASK-nnnnn en tasks/ con su cabecera, sin validar su contenido."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        task_id, path = create_task(hactors_root, project_name, task, actor)
    except (StateError, TaskError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"TASK {task_id} creada en: {path}")

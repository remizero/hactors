from pathlib import Path, PurePosixPath
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.state import StateError, require_active_project, require_active_run_path
from ..core.summary import SummaryError, create_summary


def _active_workflow_run(hactors_root: Path) -> str:
    return "/".join(PurePosixPath(require_active_run_path(hactors_root)).parts[:2])


@click.command("create-summary")
@click.option(
    "--origin",
    default=None,
    help=(
        "Ruta relativa al proyecto de la RFC en 'rfcs/' o del workflow_run en 'hactors/'. "
        "Si se omite, se usa el workflow_run de la instancia activa."
    ),
)
@click.option("--title", default=None, help="Descripción breve del resultado.")
@click.option(
    "--status",
    default=None,
    help="Fase del resumen: 'in-progress' o 'consolidated'; se registra literalmente, sin validar el vocabulario.",
)
@click.option("--final-state", default=None, help="Estado final justificable; se registra literalmente.")
@click.option("--target-state", default=None, help="Estado objetivo; se registra literalmente.")
@click.option("--date", default=None, help="Fecha YYYY-MM-DD; se registra literalmente.")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def create_summary_cmd(
    origin: Optional[str],
    title: Optional[str],
    status: Optional[str],
    final_state: Optional[str],
    target_state: Optional[str],
    date: Optional[str],
    root: Optional[Path],
) -> None:
    """Crear el archivo de resumen de una RFC o de un workflow_run, sin validar su contenido."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        if origin is None:
            origin = _active_workflow_run(hactors_root)
        path = create_summary(
            hactors_root, project_name, origin, title, status, final_state, target_state, date
        )
    except (StateError, SummaryError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Resumen creado en: {path}")

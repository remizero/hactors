from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.rfc_run import RfcRunError, create_rfc_run
from ..core.state import StateError, require_active_project, require_active_run_path


@click.command("create-rfc-run")
@click.option("--rfc-ref", default="", help="Identificador de la RFC asociada.")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def create_rfc_run_cmd(rfc_ref: str, root: Optional[Path]) -> None:
    """Crear un nuevo rfc_run dentro del task_run o plan_run seleccionado."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        parent_run_path = require_active_run_path(hactors_root)
        run_dir = create_rfc_run(hactors_root, project_name, parent_run_path, rfc_ref)
    except (StateError, RfcRunError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"RFC run creado en: {run_dir}")

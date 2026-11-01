from pathlib import Path
from typing import Optional

import click

from ..core.model import ModelError, write_model
from ..core.paths import find_hactors_root
from ..core.scan import ScanError
from ..core.state import StateError, require_active_project


@click.command("export")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def export_cmd(root: Optional[Path]) -> None:
    """Proyectar el modelo de lectura del proyecto activo en `views/project.json`."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        path = write_model(hactors_root, project_name)
    except (StateError, ScanError, ModelError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Modelo de '{project_name}' exportado a: {path}")

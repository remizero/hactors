from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.state import StateError, set_active_project


@click.command("use-project")
@click.argument("name")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def use_project_cmd(name: str, root: Optional[Path]) -> None:
    """Establecer el proyecto activo y limpiar la selección de ejecución."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        set_active_project(hactors_root, name)
    except StateError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Proyecto activo: {name}")

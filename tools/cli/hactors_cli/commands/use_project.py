from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.state import NoActiveProjectError, set_active_project


@click.command("use-project")
@click.argument("name")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def use_project_cmd(name: str, root: Optional[Path]) -> None:
    """Establecer el proyecto activo sobre el cual operan los comandos."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())

    project_dir = hactors_root / "projects" / name
    if not project_dir.is_dir():
        raise click.ClickException(f"Proyecto no encontrado: '{name}'.")

    set_active_project(hactors_root, name)
    click.echo(f"Proyecto activo: {name}")

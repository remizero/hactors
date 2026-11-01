from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.view import ViewError, render_views


@click.command("render")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def render_cmd(root: Optional[Path]) -> None:
    """Dibujar el visor de `projects/views/` y el tablero de cada proyecto, sin exigir proyecto activo."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        written = render_views(hactors_root)
    except (ViewError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    for path in written:
        click.echo(f"Vista escrita: {path}")

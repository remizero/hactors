from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.relation import RelationError, relate
from ..core.state import StateError, require_active_project


@click.command("relate")
@click.option("--source", required=True, help="Artefacto del que parte el vínculo.")
@click.option(
    "--target",
    required=True,
    help=(
        "Artefacto al que llega, con un fragmento '#<identificador>' opcional. "
        "Se comprueba que resuelva; el fragmento no."
    ),
)
@click.option(
    "--relation",
    required=True,
    help="Tipo de vínculo, en la dirección que fija su especificación; se registra literalmente.",
)
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def relate_cmd(
    source: str, target: str, relation: str, root: Optional[Path]
) -> None:
    """Registrar una arista en `relations` del manifest del proyecto activo, sin reparar el grafo."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        manifest = relate(hactors_root, project_name, source, target, relation)
    except (StateError, RelationError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Relación registrada en: {manifest}")

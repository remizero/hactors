from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.state import StateError, require_active_project
from ..core.transition import TransitionError, transition


@click.command("transition")
@click.option(
    "--artifact",
    required=True,
    help="Ruta relativa al proyecto del archivo cuyo estado se reescribe; un TRV también se resuelve en la raíz.",
)
@click.option("--to", required=True, help="Estado destino, del vocabulario de la familia del artefacto.")
@click.option(
    "--id",
    "identity",
    default=None,
    help="`ACT-nnnnn` del elemento de `actions:` cuando el estado no pertenece al archivo entero.",
)
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def transition_cmd(artifact: str, to: str, identity: Optional[str], root: Optional[Path]) -> None:
    """Reescribir el estado documental de un artefacto del proyecto activo, sin decidirlo ni propagarlo."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        subject, where, previous = transition(hactors_root, project_name, artifact, to, identity)
    except (StateError, TransitionError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"{subject} en '{where}': {previous} → {to}")

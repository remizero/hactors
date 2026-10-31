from pathlib import Path
from typing import Optional

import click

from ..core.action import ActionError, create_action
from ..core.paths import find_hactors_root
from ..core.state import StateError, require_active_project


@click.command("create-action")
@click.option("--rfc", required=True, help="Ruta relativa al proyecto del archivo de la RFC.")
@click.option("--type", "type_", default=None, help="Tipo de acción de AC_TEMPLATE.md.")
@click.option("--status", default=None, help="Estado inicial de AC_TEMPLATE.md; por omisión, `pending`.")
@click.option(
    "--actor",
    default=None,
    help="Etiqueta de actor que ejecuta la acción, sin el envoltorio `[actor: ]`.",
)
@click.option("--deliverable", default=None, help="Artefacto o ruta que la acción produce.")
@click.option("--depends-on", multiple=True, help="`AC-nnnnn` que deben completarse antes; repetible.")
@click.option("--evidence", multiple=True, help="`EVD-nnnnn` que respaldan el resultado; repetible.")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def create_action_cmd(
    rfc: str,
    type_: Optional[str],
    status: Optional[str],
    actor: Optional[str],
    deliverable: Optional[str],
    depends_on: tuple[str, ...],
    evidence: tuple[str, ...],
    root: Optional[Path],
) -> None:
    """Añadir una acción derivada AC al campo `actions:` de una RFC, sin redactar su contenido."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        action_id, path = create_action(
            hactors_root, project_name, rfc, type_, status, actor, deliverable, depends_on, evidence
        )
    except (StateError, ActionError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Acción {action_id} registrada en: {path}")

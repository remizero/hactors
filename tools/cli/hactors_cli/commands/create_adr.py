from pathlib import Path
from typing import Optional

import click

from ..core.adr import AdrError, create_adr
from ..core.paths import find_hactors_root
from ..core.state import StateError, require_active_project


@click.command("create-adr")
@click.option("--title", required=True, help="Descripción breve de la decisión; deriva el nombre del archivo.")
@click.option(
    "--status",
    default=None,
    help="Estado de la decisión; se registra literalmente, sin validar el vocabulario.",
)
@click.option("--date", default=None, help="Fecha YYYY-MM-DD del registro; se registra literalmente.")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def create_adr_cmd(
    title: str, status: Optional[str], date: Optional[str], root: Optional[Path]
) -> None:
    """Crear una decisión ADR en `decisions/`, sin redactar su contexto ni aprobarla."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        adr_id, path = create_adr(hactors_root, project_name, title, status, date)
    except (StateError, AdrError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Decisión {adr_id} creada en: {path}")

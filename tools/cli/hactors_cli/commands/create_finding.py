from pathlib import Path
from typing import Optional

import click

from ..core.finding import FindingError, create_finding
from ..core.paths import find_hactors_root
from ..core.state import StateError, require_active_project, require_active_run_path


@click.command("create-finding")
@click.option(
    "--origin",
    default=None,
    help=(
        "Ruta relativa al proyecto del artefacto o de la ejecución que originó la observación. "
        "Si se omite, se usa la instancia activa."
    ),
)
@click.option("--title", default=None, help="Descripción concisa del hecho observado.")
@click.option("--kind", default=None, help="Tipo de hallazgo; se registra literalmente, sin validar el tipo normativo.")
@click.option("--severity", default=None, help="Severidad; se registra literalmente, sin validar el valor normativo.")
@click.option("--opened", default=None, help="Fecha YYYY-MM-DD de registro; se registra literalmente.")
@click.option("--updated", default=None, help="Fecha YYYY-MM-DD de última modificación; se registra literalmente.")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def create_finding_cmd(
    origin: Optional[str],
    title: Optional[str],
    kind: Optional[str],
    severity: Optional[str],
    opened: Optional[str],
    updated: Optional[str],
    root: Optional[Path],
) -> None:
    """Registrar un hallazgo FND junto al artefacto o ejecución que lo originó, sin validar su contenido."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        if origin is None:
            origin = require_active_run_path(hactors_root)
        finding_id, path = create_finding(
            hactors_root, project_name, origin, title, kind, severity, opened, updated
        )
    except (StateError, FindingError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Hallazgo {finding_id} registrado en: {path}")

from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.state import StateError, require_active_project
from ..core.validate import ValidateError, validate_project


@click.command("validate")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def validate_cmd(root: Optional[Path]) -> None:
    """Comprobar referencias, hallazgos bloqueantes y `actions:` del proyecto activo, sin reparar nada."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        problems = validate_project(hactors_root, project_name)
    except (StateError, ValidateError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    if not problems:
        click.echo(f"Proyecto '{project_name}' sin inconsistencias.")
        return
    for problem in problems:
        click.echo(problem)
    click.echo(f"{len(problems)} inconsistencia(s) en el proyecto '{project_name}'.")
    raise click.exceptions.Exit(1)

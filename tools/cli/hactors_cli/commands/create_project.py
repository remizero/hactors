from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.project import (
    InvalidProjectNameError,
    ProjectAlreadyExistsError,
    ProjectError,
    create_project,
)


@click.command("create-project")
@click.argument("name")
@click.option(
    "-d",
    "--description",
    default="",
    help="Descripción del proyecto.",
)
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def create_project_cmd(name: str, description: str, root: Optional[Path]) -> None:
    """Crear un nuevo proyecto HACTORS."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())

    try:
        target = create_project(name, hactors_root, description)
    except InvalidProjectNameError as exc:
        raise click.BadParameter(str(exc), param_hint="'NAME'") from exc
    except ProjectAlreadyExistsError as exc:
        raise click.ClickException(str(exc)) from exc
    except ProjectError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Proyecto creado en: {target}")

from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.state import StateError, require_active_project, require_active_run_path
from ..core.test_run import TestRunError, create_test_run


@click.command("create-test-run")
@click.option("--test-ref", default="", help="Identificador del TEST asociado.")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def create_test_run_cmd(test_ref: str, root: Optional[Path]) -> None:
    """Crear y seleccionar un nuevo test_run dentro del rfc_run seleccionado."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        parent_run_path = require_active_run_path(hactors_root)
        run_dir = create_test_run(hactors_root, project_name, parent_run_path, test_ref)
    except (StateError, TestRunError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Test run creado en: {run_dir}")

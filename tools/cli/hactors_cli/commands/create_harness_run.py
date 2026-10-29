from pathlib import Path
from typing import Optional

import click

from ..core.harness_run import HarnessRunError, create_harness_run
from ..core.paths import find_hactors_root
from ..core.state import StateError, require_active_project, require_active_run_path


@click.command("create-harness-run")
@click.option("--harness-ref", default=None, help="Referencia declarada a la versión exacta del HRN; no se valida.")
@click.option("--content-ref", default=None, help="Referencia declarada al contenido publicado; no se resuelve ni verifica.")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def create_harness_run_cmd(
    harness_ref: Optional[str], content_ref: Optional[str], root: Optional[Path]
) -> None:
    """Crear y seleccionar un harness_run bajo el test_run activo, sin ejecutar su receta."""
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        parent_run_path = require_active_run_path(hactors_root)
        run_dir = create_harness_run(hactors_root, project_name, parent_run_path, harness_ref, content_ref)
    except (StateError, HarnessRunError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Harness run creado en: {run_dir}")

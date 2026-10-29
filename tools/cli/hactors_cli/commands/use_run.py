from pathlib import Path
from typing import Optional

import click

from ..core.paths import find_hactors_root
from ..core.state import (
    StateError,
    require_active_project,
    select_parent_run,
    set_active_run,
)


@click.command("use-run")
@click.argument("run_path", required=False)
@click.option("--parent", is_flag=True, help="Seleccionar el padre inmediato de la instancia activa.")
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directorio raíz de HACTORS. Por defecto se detecta desde el directorio actual.",
)
def use_run_cmd(run_path: Optional[str], parent: bool, root: Optional[Path]) -> None:
    """Seleccionar una ruta completa de ejecución relativa al proyecto activo."""
    if (run_path is None and not parent) or (run_path is not None and parent):
        raise click.UsageError("Indique una ruta completa o --parent, pero no ambos.")
    if run_path == "":
        raise click.ClickException("Ruta de ejecución inválida: no puede estar vacía.")
    hactors_root = root if root is not None else find_hactors_root(Path.cwd())
    try:
        project_name = require_active_project(hactors_root)
        if parent:
            selected = select_parent_run(hactors_root)
        else:
            set_active_run(hactors_root, project_name, run_path)
            selected = run_path
    except StateError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Contexto activo: {project_name} / {selected or '(sin instancia)'}")

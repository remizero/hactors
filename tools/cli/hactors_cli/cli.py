import click

from .commands.create_plan_run import create_plan_run_cmd
from .commands.create_project import create_project_cmd
from .commands.create_rfc_run import create_rfc_run_cmd
from .commands.create_task_run import create_task_run_cmd
from .commands.create_test_run import create_test_run_cmd
from .commands.create_workflow import create_workflow_cmd
from .commands.use_project import use_project_cmd
from .commands.use_run import use_run_cmd


@click.group()
@click.version_option(package_name="hactors-cli")
def cli() -> None:
    """HACTORS — herramienta CLI para gestionar proyectos."""


cli.add_command(create_project_cmd)
cli.add_command(use_project_cmd)
cli.add_command(use_run_cmd)
cli.add_command(create_workflow_cmd)
cli.add_command(create_task_run_cmd)
cli.add_command(create_rfc_run_cmd)
cli.add_command(create_plan_run_cmd)
cli.add_command(create_test_run_cmd)

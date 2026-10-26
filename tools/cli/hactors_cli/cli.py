import click

from .commands.create_project import create_project_cmd


@click.group()
@click.version_option(package_name="hactors-cli")
def cli() -> None:
    """HACTORS — herramienta CLI para gestionar proyectos."""


cli.add_command(create_project_cmd)

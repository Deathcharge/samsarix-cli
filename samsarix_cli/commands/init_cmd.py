"""The project initialization command."""

from pathlib import Path

import click

from samsarix_cli.scaffold import ScaffoldError, scaffold_project
from samsarix_cli.templates import DEFAULT_TEMPLATE, TEMPLATE_NAMES


@click.command("init")
@click.argument(
    "destination",
    type=click.Path(path_type=Path, file_okay=False, resolve_path=False),
)
@click.option(
    "--template",
    type=click.Choice(TEMPLATE_NAMES, case_sensitive=False),
    default=DEFAULT_TEMPLATE,
    show_default=True,
    help="Starter to generate.",
)
@click.option(
    "--name",
    "project_name",
    help="Project name; defaults to the destination directory name.",
)
@click.option(
    "--git/--no-git",
    "initialize_git",
    default=True,
    show_default=True,
    help="Initialize an empty Git repository (no commit is created).",
)
def init(
    destination: Path,
    template: str,
    project_name: str | None,
    initialize_git: bool,
) -> None:
    """Create a new project at DESTINATION.

    Generation is all-or-nothing. Samsarix refuses to replace an existing path
    and removes its temporary staging directory if any step fails.
    """
    try:
        result = scaffold_project(
            destination=destination,
            project_name=project_name,
            template_name=template.lower(),
            initialize_git=initialize_git,
        )
    except ScaffoldError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Created {result.project_name!r} with the {result.template_name} template.")
    click.echo(f"Location: {result.destination}")
    click.echo(f"Files: {len(result.files)}")
    click.echo(f"Git: {'initialized' if result.git_initialized else 'not initialized'}")
    click.echo("")
    click.echo("Next:")
    click.echo(f'  cd "{result.destination}"')
    click.echo("  Read README.md for setup and run commands.")
    click.echo(f'  samsarix check "{result.destination}"')

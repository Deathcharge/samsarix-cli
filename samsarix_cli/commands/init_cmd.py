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
    default=None,
    show_default=DEFAULT_TEMPLATE,
    help="Built-in starter to generate.",
)
@click.option(
    "--template-pack",
    type=click.Path(
        path_type=Path,
        exists=True,
        file_okay=False,
        resolve_path=False,
    ),
    help="Local declarative template-pack directory.",
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
    template: str | None,
    template_pack: Path | None,
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
            template_name=template.lower() if template is not None else None,
            template_pack=template_pack,
            initialize_git=initialize_git,
        )
    except ScaffoldError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(
        f"Created {result.project_name!r} with the {result.template_name} "
        f"{result.template_kind} template."
    )
    click.echo(f"Template version: {result.template_version}")
    click.echo(f"Template digest: {result.template_digest}")
    click.echo(f"Location: {result.destination}")
    click.echo(f"Files: {len(result.files)}")
    click.echo(f"Git: {'initialized' if result.git_initialized else 'not initialized'}")
    click.echo("")
    click.echo("Next:")
    click.echo(f'  cd "{result.destination}"')
    click.echo("  Read README.md for setup and run commands.")
    click.echo(f'  samsarix check "{result.destination}"')

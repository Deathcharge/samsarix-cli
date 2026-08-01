"""Preview an exact generation plan without writing a project."""

import json
from pathlib import Path

import click

from samsarix_cli.scaffold import ScaffoldError, plan_project
from samsarix_cli.templates import DEFAULT_TEMPLATE, TEMPLATE_NAMES


@click.command("plan")
@click.argument(
    "destination",
    type=click.Path(path_type=Path, file_okay=False, resolve_path=False),
)
@click.option(
    "--template",
    type=click.Choice(TEMPLATE_NAMES, case_sensitive=False),
    default=None,
    show_default=DEFAULT_TEMPLATE,
    help="Built-in starter to preview.",
)
@click.option(
    "--template-pack",
    type=click.Path(
        path_type=Path,
        exists=True,
        file_okay=False,
        resolve_path=True,
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
    help="Include Git initialization in the plan.",
)
@click.option("--json", "as_json", is_flag=True, help="Emit stable JSON for automation.")
def plan(
    destination: Path,
    template: str | None,
    template_pack: Path | None,
    project_name: str | None,
    initialize_git: bool,
    as_json: bool,
) -> None:
    """Preview generation at DESTINATION without changing the filesystem."""
    try:
        project_plan = plan_project(
            destination=destination,
            project_name=project_name,
            template_name=template.lower() if template is not None else None,
            template_pack=template_pack,
            initialize_git=initialize_git,
        )
    except ScaffoldError as exc:
        raise click.ClickException(str(exc)) from exc

    payload = {
        "destination": str(project_plan.destination),
        "files": list(project_plan.files),
        "git": project_plan.git_requested,
        "module_name": project_plan.module_name,
        "project_name": project_plan.project_name,
        "template": {
            "digest": project_plan.template_digest,
            "kind": project_plan.template_kind,
            "name": project_plan.template_name,
            "version": project_plan.template_version,
        },
    }
    if as_json:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
        return

    click.echo(f"Project: {project_plan.project_name} ({project_plan.module_name})")
    click.echo(f"Destination: {project_plan.destination}")
    click.echo(
        f"Template: {project_plan.template_name} {project_plan.template_version} "
        f"({project_plan.template_kind})"
    )
    click.echo(f"Digest: {project_plan.template_digest}")
    click.echo(f"Git: {'initialize' if project_plan.git_requested else 'skip'}")
    click.echo("Files:")
    for path in project_plan.files:
        click.echo(f"  {path}")

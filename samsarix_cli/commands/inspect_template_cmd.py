"""Inspect a local template pack without executing or rendering it."""

import json
from pathlib import Path

import click

from samsarix_cli.template_pack import TemplatePackError, load_template_pack


@click.command("inspect-template")
@click.argument(
    "template_pack",
    type=click.Path(
        path_type=Path,
        exists=True,
        file_okay=False,
        resolve_path=True,
    ),
)
@click.option("--json", "as_json", is_flag=True, help="Emit stable JSON for automation.")
def inspect_template(template_pack: Path, as_json: bool) -> None:
    """Validate and describe TEMPLATE_PACK without executing template code."""
    try:
        pack = load_template_pack(template_pack)
    except TemplatePackError as exc:
        raise click.ClickException(str(exc)) from exc

    payload = {
        "description": pack.description,
        "digest": pack.digest,
        "files": [template_file.path for template_file in pack.files],
        "name": pack.name,
        "path": str(pack.root),
        "placeholders": ["@@PROJECT_NAME@@", "@@MODULE_NAME@@", "@@COMMAND_NAME@@"],
        "version": pack.version,
    }
    if as_json:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
        return

    click.echo(f"Template: {pack.name} {pack.version}")
    click.echo(f"Description: {pack.description}")
    click.echo(f"Path: {pack.root}")
    click.echo(f"Digest: {pack.digest}")
    click.echo("Files:")
    for template_file in pack.files:
        click.echo(f"  {template_file.path}")

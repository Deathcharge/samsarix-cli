"""List the built-in starters."""

import json

import click

from helix_cli.templates import TEMPLATE_SPECS


@click.command("templates")
@click.option("--json", "as_json", is_flag=True, help="Emit stable JSON for automation.")
def templates(as_json: bool) -> None:
    """List the project templates included in this installation."""
    if as_json:
        payload = [
            {
                "name": spec.name,
                "summary": spec.summary,
                "run_command": spec.run_command,
            }
            for spec in TEMPLATE_SPECS
        ]
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
        return

    click.echo("Built-in templates:")
    for spec in TEMPLATE_SPECS:
        click.echo(f"  {spec.name:<10} {spec.summary}")

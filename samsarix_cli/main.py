"""Command-line entry point for Samsarix CLI."""

import click

from samsarix_cli import __version__
from samsarix_cli.commands.check_cmd import check
from samsarix_cli.commands.init_cmd import init
from samsarix_cli.commands.inspect_template_cmd import inspect_template
from samsarix_cli.commands.plan_cmd import plan
from samsarix_cli.commands.templates_cmd import templates

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "max_content_width": 100,
}


@click.group(context_settings=CONTEXT_SETTINGS, no_args_is_help=True)
@click.version_option(version=__version__, prog_name="samsarix")
def cli() -> None:
    """Create honest, independent Python project starters.

    Samsarix works locally, makes no network requests, and does not require a
    hosted service. Start with `samsarix templates`, then create a project
    with `samsarix init PATH`.
    """


cli.add_command(init)
cli.add_command(templates)
cli.add_command(check)
cli.add_command(plan)
cli.add_command(inspect_template)


if __name__ == "__main__":  # pragma: no cover - covered through samsarix_cli.__main__
    cli()

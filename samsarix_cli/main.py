"""Command-line entry point for Samsarix CLI."""

import click

from samsarix_cli import __version__
from samsarix_cli.commands.check_cmd import check
from samsarix_cli.commands.init_cmd import init
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


if __name__ == "__main__":  # pragma: no cover - covered through samsarix_cli.__main__
    cli()

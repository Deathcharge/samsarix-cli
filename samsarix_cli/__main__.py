"""Allow ``python -m samsarix_cli`` to behave like the installed command."""

from samsarix_cli.main import cli

if __name__ == "__main__":
    cli()

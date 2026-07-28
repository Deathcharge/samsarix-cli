"""Allow ``python -m helix_cli`` to behave like the installed command."""

from helix_cli.main import cli

if __name__ == "__main__":
    cli()

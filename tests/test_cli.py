"""Command-level behavior and output contracts."""

import json
import runpy
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from samsarix_cli import __version__
from samsarix_cli.main import cli


def test_help_is_ascii_safe_and_describes_only_real_commands() -> None:
    result = CliRunner().invoke(cli, ["--help"])

    assert result.exit_code == 0
    result.output.encode("cp1252")
    assert "init" in result.output
    assert "templates" in result.output
    assert "check" in result.output
    assert "deploy" not in result.output
    assert "monitor" not in result.output


def test_version_uses_package_version() -> None:
    result = CliRunner().invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == f"samsarix, version {__version__}"


def test_python_module_entrypoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["samsarix", "--version"])

    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("samsarix_cli", run_name="__main__")

    assert exit_info.value.code == 0


def test_templates_support_human_and_json_output() -> None:
    runner = CliRunner()
    human = runner.invoke(cli, ["templates"])
    machine = runner.invoke(cli, ["templates", "--json"])

    assert human.exit_code == 0
    assert "fastapi" in human.output
    assert "Discord bot" in human.output
    payload = json.loads(machine.output)
    assert machine.exit_code == 0
    assert [item["name"] for item in payload] == ["fastapi", "flask", "streamlit", "discord"]


def test_init_and_check_complete_the_primary_cli_journey() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        initialized = runner.invoke(cli, ["init", "demo-api", "--no-git"])
        checked = runner.invoke(cli, ["check", "demo-api"])
        checked_json = runner.invoke(cli, ["check", "demo-api", "--json"])

        assert initialized.exit_code == 0
        assert "Created 'demo-api' with the fastapi template." in initialized.output
        assert "Git: not initialized" in initialized.output
        assert checked.exit_code == 0
        assert checked.output.startswith("OK:")
        assert checked_json.exit_code == 0
        assert json.loads(checked_json.output)["valid"] is True
        assert Path("demo-api/README.md").is_file()


def test_init_reports_validation_errors_without_tracebacks() -> None:
    result = CliRunner().invoke(cli, ["init", "bad name", "--no-git"])

    assert result.exit_code == 1
    assert "Error: Project names must start with a letter" in result.output
    assert "Traceback" not in result.output


def test_check_reports_missing_manifest_and_nonzero_json_status() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("ordinary-project").mkdir()
        human = runner.invoke(cli, ["check", "ordinary-project"])
        machine = runner.invoke(cli, ["check", "ordinary-project", "--json"])

        assert human.exit_code == 1
        assert "missing .samsarix/project.json manifest" in human.output
        assert machine.exit_code == 1
        payload = json.loads(machine.output)
        assert payload["valid"] is False


def test_unknown_template_is_a_usage_error() -> None:
    result = CliRunner().invoke(cli, ["init", "demo", "--template", "unknown"])

    assert result.exit_code == 2
    assert "Invalid value for '--template'" in result.output

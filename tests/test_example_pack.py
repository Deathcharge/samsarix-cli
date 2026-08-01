"""Executable evidence that the published example pack remains usable."""

import json
import tomllib
from pathlib import Path

from samsarix_cli.scaffold import plan_project, scaffold_project
from samsarix_cli.template_pack import load_template_pack
from samsarix_cli.validation import check_project

_EXAMPLE_PACK = Path(__file__).parents[1] / "examples" / "team-service"


def test_team_service_example_is_inspectable_and_deterministic(tmp_path: Path) -> None:
    first = load_template_pack(_EXAMPLE_PACK)
    second = load_template_pack(_EXAMPLE_PACK)

    assert first.name == "team-service"
    assert first.version == "1.0.1"
    assert first.digest == second.digest
    assert tuple(template_file.path for template_file in first.files) == (
        ".github/workflows/ci.yml",
        ".gitignore",
        "README.md",
        "pyproject.toml",
        "src/@@MODULE_NAME@@/__init__.py",
        "src/@@MODULE_NAME@@/main.py",
        "tests/test_health.py",
    )

    plan = plan_project(
        destination=tmp_path / "planned-service",
        project_name="orders-api",
        template_name=None,
        template_pack=_EXAMPLE_PACK,
        initialize_git=False,
    )
    assert plan.template_digest == first.digest
    assert "src/orders_api/main.py" in plan.files
    assert not plan.destination.exists()


def test_team_service_example_generates_valid_python_project(tmp_path: Path) -> None:
    destination = tmp_path / "orders-api"
    result = scaffold_project(
        destination=destination,
        project_name=None,
        template_name=None,
        template_pack=_EXAMPLE_PACK,
        initialize_git=False,
    )

    assert result.template_kind == "local"
    assert result.template_name == "team-service"
    assert check_project(destination, strict=True).is_valid

    manifest = json.loads((destination / ".samsarix/project.json").read_text(encoding="utf-8"))
    assert manifest["template_digest"] == result.template_digest
    assert manifest["template_version"] == "1.0.1"
    assert manifest["schema_version"] == 2

    python_files = list(destination.rglob("*.py"))
    assert python_files
    for python_file in python_files:
        compile(python_file.read_text(encoding="utf-8"), str(python_file), "exec")


def test_team_service_source_pyproject_is_valid_before_rendering() -> None:
    pyproject = tomllib.loads(
        (_EXAMPLE_PACK / "template/pyproject.toml").read_text(encoding="utf-8")
    )

    assert pyproject["project"]["scripts"] == {"@@COMMAND_NAME@@": "@@MODULE_NAME@@.main:main"}

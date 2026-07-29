"""Generation invariants for every bundled template."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

import samsarix_cli.scaffold as scaffold_module
from samsarix_cli.scaffold import ScaffoldError, scaffold_project, validate_project_name
from samsarix_cli.templates import TEMPLATE_NAMES, render_project
from samsarix_cli.validation import check_project


@pytest.mark.parametrize("template_name", TEMPLATE_NAMES)
def test_every_template_is_complete_valid_toml_and_valid_python(
    tmp_path: Path, template_name: str
) -> None:
    destination = tmp_path / f"sample-{template_name}"

    result = scaffold_project(
        destination=destination,
        project_name=None,
        template_name=template_name,
        initialize_git=False,
    )

    assert result.destination == destination.resolve()
    assert result.module_name == f"sample_{template_name}"
    assert result.template_name == template_name
    assert not result.git_initialized
    assert check_project(destination).is_valid
    assert "helix-collective" not in (destination / "pyproject.toml").read_text(encoding="utf-8")
    assert "hosted service" in (destination / "README.md").read_text(encoding="utf-8")

    python_files = sorted(destination.rglob("*.py"))
    assert python_files
    for python_file in python_files:
        compile(python_file.read_text(encoding="utf-8"), str(python_file), "exec")


def test_project_name_override_controls_distribution_and_module_names(tmp_path: Path) -> None:
    destination = tmp_path / "directory-name"

    result = scaffold_project(
        destination=destination,
        project_name="Useful_API",
        template_name="fastapi",
        initialize_git=False,
    )

    manifest = json.loads((destination / ".samsarix/project.json").read_text(encoding="utf-8"))
    assert result.project_name == "Useful_API"
    assert result.module_name == "useful_api"
    assert manifest["project_name"] == "Useful_API"
    assert (destination / "src/useful_api/main.py").is_file()


@pytest.mark.parametrize(
    "project_name",
    ["", "9lives", "has space", "has.dot", "slash/name", "class", "NUL", "x" * 65],
)
def test_invalid_or_nonportable_project_names_are_rejected(project_name: str) -> None:
    with pytest.raises(ScaffoldError):
        validate_project_name(project_name)


def test_existing_destination_is_never_modified(tmp_path: Path) -> None:
    destination = tmp_path / "existing"
    destination.mkdir()
    sentinel = destination / "keep.txt"
    sentinel.write_text("user data", encoding="utf-8")

    with pytest.raises(ScaffoldError, match="Destination already exists"):
        scaffold_project(
            destination=destination,
            project_name=None,
            template_name="fastapi",
            initialize_git=False,
        )

    assert sentinel.read_text(encoding="utf-8") == "user data"
    assert list(destination.iterdir()) == [sentinel]


def test_unknown_template_is_rejected_by_the_library_api(tmp_path: Path) -> None:
    with pytest.raises(ScaffoldError, match="Unknown template"):
        scaffold_project(
            destination=tmp_path / "demo",
            project_name=None,
            template_name="unknown",
            initialize_git=False,
        )

    with pytest.raises(ValueError, match="Unknown template"):
        render_project("demo", "demo", "unknown")


def test_partial_generation_is_cleaned_up(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    destination = tmp_path / "broken"
    real_write_file = scaffold_module._write_file

    def fail_on_readme(root: Path, relative_path: str, content: str) -> None:
        if relative_path == "README.md":
            raise OSError("simulated disk failure")
        real_write_file(root, relative_path, content)

    monkeypatch.setattr(scaffold_module, "_write_file", fail_on_readme)

    with pytest.raises(ScaffoldError, match="Project generation failed"):
        scaffold_project(
            destination=destination,
            project_name=None,
            template_name="fastapi",
            initialize_git=False,
        )

    assert not destination.exists()
    assert not list(tmp_path.glob(".broken.samsarix-*"))


def test_cancelled_generation_is_cleaned_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "cancelled"

    def cancel(_root: Path, _relative_path: str, _content: str) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(scaffold_module, "_write_file", cancel)

    with pytest.raises(KeyboardInterrupt):
        scaffold_project(
            destination=destination,
            project_name=None,
            template_name="fastapi",
            initialize_git=False,
        )

    assert not destination.exists()
    assert not list(tmp_path.glob(".cancelled.samsarix-*"))


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is not installed")
def test_requested_git_repository_is_real_and_has_no_synthetic_commit(tmp_path: Path) -> None:
    destination = tmp_path / "git-project"

    result = scaffold_project(
        destination=destination,
        project_name=None,
        template_name="flask",
        initialize_git=True,
    )
    work_tree = subprocess.run(
        ["git", "-C", str(destination), "rev-parse", "--is-inside-work-tree"],
        check=True,
        capture_output=True,
        text=True,
    )
    history = subprocess.run(
        ["git", "-C", str(destination), "rev-list", "--all", "--count"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.git_initialized
    assert work_tree.stdout.strip() == "true"
    assert history.stdout.strip() == "0"


def test_missing_git_is_actionable_and_atomic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "without-git"
    monkeypatch.setattr(shutil, "which", lambda _command: None)

    with pytest.raises(ScaffoldError, match="retry with --no-git"):
        scaffold_project(
            destination=destination,
            project_name=None,
            template_name="fastapi",
            initialize_git=True,
        )

    assert not destination.exists()

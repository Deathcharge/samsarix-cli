"""Safe, atomic project generation."""

import json
import keyword
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from samsarix_cli import __version__
from samsarix_cli.templates import TEMPLATE_BY_NAME, render_project

_PROJECT_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
_WINDOWS_RESERVED_NAMES = {
    "AUX",
    "CON",
    "NUL",
    "PRN",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


class ScaffoldError(RuntimeError):
    """A safe-to-display project generation failure."""


@dataclass(frozen=True, slots=True)
class ScaffoldResult:
    """Facts about a successfully created project."""

    destination: Path
    files: tuple[str, ...]
    git_initialized: bool
    module_name: str
    project_name: str
    template_name: str


def validate_project_name(project_name: str) -> str:
    """Validate the distribution name and return its import-package name."""
    if not _PROJECT_NAME.fullmatch(project_name):
        raise ScaffoldError(
            "Project names must start with a letter, contain only letters, numbers, "
            "hyphens, or underscores, and be at most 64 characters."
        )
    if project_name.upper() in _WINDOWS_RESERVED_NAMES:
        raise ScaffoldError(f"{project_name!r} is a reserved path name on Windows.")

    module_name = project_name.lower().replace("-", "_")
    if keyword.iskeyword(module_name):
        raise ScaffoldError(f"{project_name!r} cannot be used as a Python package name.")
    return module_name


def _write_file(root: Path, relative_path: str, content: str) -> None:
    target = root.joinpath(*relative_path.split("/"))
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as file_handle:
        file_handle.write(content)


def _initialize_git(project: Path) -> None:
    git = shutil.which("git")
    if git is None:
        raise ScaffoldError("Git was requested but is not installed; retry with --no-git.")

    try:
        completed = subprocess.run(
            [git, "init", "--quiet", str(project)],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ScaffoldError("Git initialization failed; retry with --no-git.") from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()
        suffix = f" ({detail[-1]})" if detail else ""
        raise ScaffoldError(f"Git initialization failed{suffix}; retry with --no-git.")


def scaffold_project(
    *,
    destination: Path,
    project_name: str | None,
    template_name: str,
    initialize_git: bool,
) -> ScaffoldResult:
    """Create a complete project without ever replacing an existing path."""
    if template_name not in TEMPLATE_BY_NAME:
        raise ScaffoldError(f"Unknown template: {template_name}")

    requested_destination = destination.expanduser()
    selected_name = project_name or requested_destination.name
    module_name = validate_project_name(selected_name)
    resolved_destination = requested_destination.resolve(strict=False)

    if resolved_destination.exists() or resolved_destination.is_symlink():
        raise ScaffoldError(f"Destination already exists: {resolved_destination}")

    parent = resolved_destination.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ScaffoldError(f"Could not create destination parent: {parent}") from exc

    staging: Path | None = None
    try:
        staging = Path(
            tempfile.mkdtemp(prefix=f".{resolved_destination.name}.samsarix-", dir=parent)
        )
        files = render_project(selected_name, module_name, template_name)
        manifest_path = ".samsarix/project.json"
        manifest = {
            "files": sorted((*files, manifest_path)),
            "generator": "samsarix-cli",
            "generator_version": __version__,
            "module_name": module_name,
            "project_name": selected_name,
            "schema_version": 1,
            "template": template_name,
        }
        files[manifest_path] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"

        for relative_path, content in files.items():
            _write_file(staging, relative_path, content)

        if initialize_git:
            _initialize_git(staging)

        os.replace(staging, resolved_destination)
        staging = None
    except ScaffoldError:
        raise
    except (OSError, ValueError) as exc:
        raise ScaffoldError(f"Project generation failed: {exc}") from exc
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)

    return ScaffoldResult(
        destination=resolved_destination,
        files=tuple(sorted(files)),
        git_initialized=initialize_git,
        module_name=module_name,
        project_name=selected_name,
        template_name=template_name,
    )

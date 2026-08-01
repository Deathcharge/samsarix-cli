"""Safe, atomic project generation."""

import hashlib
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
from samsarix_cli.template_pack import TemplatePackError, load_template_pack
from samsarix_cli.templates import DEFAULT_TEMPLATE, TEMPLATE_BY_NAME, render_project

_PROJECT_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
_MAX_MANIFEST_BYTES = 64 * 1024
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
    template_digest: str
    template_kind: str
    template_name: str
    template_version: str


@dataclass(frozen=True, slots=True)
class ProjectPlan:
    """A complete generation plan produced without writing to the destination."""

    destination: Path
    files: tuple[str, ...]
    git_requested: bool
    module_name: str
    project_name: str
    template_digest: str
    template_kind: str
    template_name: str
    template_version: str
    _contents: tuple[tuple[str, str], ...]


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


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _builtin_digest(template_name: str) -> str:
    identity = f"samsarix-builtin-template-v1\0{template_name}\0{__version__}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def plan_project(
    *,
    destination: Path,
    project_name: str | None,
    template_name: str | None,
    template_pack: Path | None = None,
    initialize_git: bool,
) -> ProjectPlan:
    """Build an exact project plan without creating or changing any path."""
    if template_name is not None and template_pack is not None:
        raise ScaffoldError("Choose either --template or --template-pack, not both.")

    requested_destination = destination.expanduser()
    selected_name = project_name or requested_destination.name
    module_name = validate_project_name(selected_name)
    resolved_destination = requested_destination.resolve(strict=False)
    if resolved_destination.exists() or resolved_destination.is_symlink():
        raise ScaffoldError(f"Destination already exists: {resolved_destination}")

    if template_pack is None:
        selected_template = template_name or DEFAULT_TEMPLATE
        if selected_template not in TEMPLATE_BY_NAME:
            raise ScaffoldError(f"Unknown template: {selected_template}")
        files = render_project(selected_name, module_name, selected_template)
        template_kind = "builtin"
        template_version = __version__
        template_digest = _builtin_digest(selected_template)
    else:
        try:
            pack = load_template_pack(template_pack)
            files = pack.render(selected_name, module_name)
        except TemplatePackError as exc:
            raise ScaffoldError(str(exc)) from exc
        selected_template = pack.name
        template_kind = "local"
        template_version = pack.version
        template_digest = pack.digest

    manifest_path = ".samsarix/project.json"
    file_hashes = {path: _content_hash(content) for path, content in sorted(files.items())}
    manifest = {
        "file_hashes": file_hashes,
        "files": sorted((*files, manifest_path)),
        "generator": "samsarix-cli",
        "generator_version": __version__,
        "module_name": module_name,
        "project_name": selected_name,
        "schema_version": 2,
        "template": selected_template,
        "template_digest": template_digest,
        "template_kind": template_kind,
        "template_version": template_version,
    }
    rendered_manifest = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if len(rendered_manifest.encode("utf-8")) > _MAX_MANIFEST_BYTES:
        raise ScaffoldError(
            f"Generated manifest exceeds the {_MAX_MANIFEST_BYTES}-byte safety limit."
        )
    files[manifest_path] = rendered_manifest
    return ProjectPlan(
        destination=resolved_destination,
        files=tuple(sorted(files)),
        git_requested=initialize_git,
        module_name=module_name,
        project_name=selected_name,
        template_digest=template_digest,
        template_kind=template_kind,
        template_name=selected_template,
        template_version=template_version,
        _contents=tuple(sorted(files.items())),
    )


def scaffold_project(
    *,
    destination: Path,
    project_name: str | None,
    template_name: str | None,
    template_pack: Path | None = None,
    initialize_git: bool,
) -> ScaffoldResult:
    """Create a complete project without ever replacing an existing path."""
    plan = plan_project(
        destination=destination,
        project_name=project_name,
        template_name=template_name,
        template_pack=template_pack,
        initialize_git=initialize_git,
    )
    parent = plan.destination.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ScaffoldError(f"Could not create destination parent: {parent}") from exc

    staging: Path | None = None
    try:
        staging = Path(tempfile.mkdtemp(prefix=f".{plan.destination.name}.samsarix-", dir=parent))
        for relative_path, content in plan._contents:
            _write_file(staging, relative_path, content)

        if initialize_git:
            _initialize_git(staging)

        os.replace(staging, plan.destination)
        staging = None
    except ScaffoldError:
        raise
    except (OSError, ValueError) as exc:
        raise ScaffoldError(f"Project generation failed: {exc}") from exc
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)

    return ScaffoldResult(
        destination=plan.destination,
        files=plan.files,
        git_initialized=initialize_git,
        module_name=plan.module_name,
        project_name=plan.project_name,
        template_digest=plan.template_digest,
        template_kind=plan.template_kind,
        template_name=plan.template_name,
        template_version=plan.template_version,
    )

"""Validation for the bounded, untrusted generated-project manifest."""

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from samsarix_cli.scaffold import ScaffoldError, validate_project_name
from samsarix_cli.templates import TEMPLATE_BY_NAME

_MANIFEST_PATH = Path(".samsarix/project.json")
_MAX_MANIFEST_BYTES = 64 * 1024
_MAX_PYPROJECT_BYTES = 1024 * 1024
_MAX_TRACKED_FILES = 256


@dataclass(frozen=True, slots=True)
class CheckResult:
    """Structural validation outcome suitable for CLI and API consumers."""

    project: Path
    issues: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues


def _read_bounded(path: Path, limit: int, label: str) -> bytes:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValueError(f"cannot read {label}: {exc}") from exc
    if size > limit:
        raise ValueError(f"{label} exceeds the {limit}-byte safety limit")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read {label}: {exc}") from exc


def _load_manifest(path: Path) -> dict[str, Any]:
    raw = _read_bounded(path, _MAX_MANIFEST_BYTES, "manifest")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"manifest is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("manifest root must be a JSON object")
    return payload


def _safe_relative_path(value: object) -> PurePosixPath | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
        return None
    return relative


def _check_manifest_fields(manifest: dict[str, Any], issues: list[str]) -> None:
    if manifest.get("schema_version") != 1:
        issues.append("manifest schema_version must be 1")
    if manifest.get("generator") != "samsarix-cli":
        issues.append("manifest generator must be 'samsarix-cli'")

    project_name = manifest.get("project_name")
    module_name = manifest.get("module_name")
    if not isinstance(project_name, str):
        issues.append("manifest project_name must be a string")
    else:
        try:
            expected_module = validate_project_name(project_name)
        except ScaffoldError as exc:
            issues.append(f"manifest project_name is invalid: {exc}")
        else:
            if module_name != expected_module:
                issues.append(f"manifest module_name must be {expected_module!r}")

    if manifest.get("template") not in TEMPLATE_BY_NAME:
        issues.append("manifest template is not supported by this Samsarix CLI")


def _check_files(project: Path, manifest: dict[str, Any], issues: list[str]) -> None:
    values = manifest.get("files")
    if not isinstance(values, list):
        issues.append("manifest files must be a JSON array")
        return
    if len(values) > _MAX_TRACKED_FILES:
        issues.append(f"manifest files exceeds the {_MAX_TRACKED_FILES}-entry safety limit")
        return
    if len(values) != len(set(value for value in values if isinstance(value, str))):
        issues.append("manifest files contains duplicate paths")

    module_name = manifest.get("module_name")
    template_name = manifest.get("template")
    if isinstance(module_name, str) and template_name in TEMPLATE_BY_NAME:
        test_file = "tests/test_config.py" if template_name == "discord" else "tests/test_app.py"
        required_paths = {
            ".gitignore",
            ".samsarix/project.json",
            "README.md",
            "pyproject.toml",
            f"src/{module_name}/__init__.py",
            f"src/{module_name}/main.py",
            test_file,
        }
        declared_paths = {value for value in values if isinstance(value, str)}
        for missing_path in sorted(required_paths - declared_paths):
            issues.append(f"manifest does not declare required file: {missing_path}")

    for value in values:
        relative = _safe_relative_path(value)
        if relative is None:
            issues.append(f"manifest contains an unsafe file path: {value!r}")
            continue
        candidate = project.joinpath(*relative.parts)
        try:
            resolved_candidate = candidate.resolve(strict=False)
        except OSError:
            issues.append(f"cannot resolve generated file: {relative.as_posix()}")
            continue
        if not resolved_candidate.is_relative_to(project):
            issues.append(f"generated file resolves outside the project: {relative.as_posix()}")
        elif not candidate.is_file():
            issues.append(f"generated file is missing: {relative.as_posix()}")


def _check_pyproject(project: Path, manifest: dict[str, Any], issues: list[str]) -> None:
    path = project / "pyproject.toml"
    if not path.is_file():
        return
    try:
        resolved_path = path.resolve(strict=False)
    except OSError:
        issues.append("cannot resolve pyproject.toml")
        return
    if not resolved_path.is_relative_to(project):
        issues.append("pyproject.toml resolves outside the project")
        return
    try:
        data = tomllib.loads(_read_bounded(path, _MAX_PYPROJECT_BYTES, "pyproject.toml").decode())
    except (UnicodeDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        issues.append(f"pyproject.toml is invalid: {exc}")
        return

    project_table = data.get("project")
    if not isinstance(project_table, dict):
        issues.append("pyproject.toml must contain a [project] table")
        return
    if project_table.get("name") != manifest.get("project_name"):
        issues.append("pyproject.toml project.name does not match the manifest")
    if project_table.get("requires-python") != ">=3.11":
        issues.append("pyproject.toml project.requires-python must be '>=3.11'")


def check_project(project: Path) -> CheckResult:
    """Validate a generated project without following manifest paths outside it."""
    resolved_project = project.expanduser().resolve(strict=False)
    issues: list[str] = []
    if not resolved_project.is_dir():
        return CheckResult(resolved_project, ("project directory does not exist",))

    manifest_path = resolved_project / _MANIFEST_PATH
    if not manifest_path.is_file():
        return CheckResult(resolved_project, ("missing .samsarix/project.json manifest",))
    try:
        resolved_manifest = manifest_path.resolve(strict=False)
    except OSError:
        return CheckResult(resolved_project, ("cannot resolve .samsarix/project.json manifest",))
    if not resolved_manifest.is_relative_to(resolved_project):
        return CheckResult(resolved_project, ("manifest resolves outside the project",))

    try:
        manifest = _load_manifest(manifest_path)
    except ValueError as exc:
        return CheckResult(resolved_project, (str(exc),))

    _check_manifest_fields(manifest, issues)
    _check_files(resolved_project, manifest, issues)
    _check_pyproject(resolved_project, manifest, issues)
    return CheckResult(resolved_project, tuple(issues))

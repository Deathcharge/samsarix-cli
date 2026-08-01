"""Validation for the bounded, untrusted generated-project manifest."""

import hashlib
import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from samsarix_cli.scaffold import ScaffoldError, validate_project_name
from samsarix_cli.templates import TEMPLATE_BY_NAME

_MANIFEST_PATH = Path(".samsarix/project.json")
_MAX_MANIFEST_BYTES = 64 * 1024
_MAX_PYPROJECT_BYTES = 1024 * 1024
_MAX_GENERATED_FILES = 256
_MAX_TRACKED_FILES = _MAX_GENERATED_FILES + 1
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_LOCAL_TEMPLATE_NAME = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
_INVALID_WINDOWS_CHARACTERS = frozenset('<>:"|?*')
_WINDOWS_RESERVED_NAMES = {
    "AUX",
    "CON",
    "NUL",
    "PRN",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


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
    for part in relative.parts:
        if (
            part.endswith((" ", "."))
            or any(
                character in _INVALID_WINDOWS_CHARACTERS or ord(character) < 32
                for character in part
            )
            or part.split(".", 1)[0].upper() in _WINDOWS_RESERVED_NAMES
        ):
            return None
    return relative


def _check_manifest_fields(manifest: dict[str, Any], issues: list[str]) -> None:
    schema_version = manifest.get("schema_version")
    if schema_version not in {1, 2}:
        issues.append("manifest schema_version must be 1 or 2")
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

    template_name = manifest.get("template")
    if schema_version == 2:
        template_kind = manifest.get("template_kind")
        if template_kind not in {"builtin", "local"}:
            issues.append("manifest template_kind must be 'builtin' or 'local'")
        elif template_kind == "builtin" and template_name not in TEMPLATE_BY_NAME:
            issues.append("manifest built-in template is not supported by this Samsarix CLI")
        elif template_kind == "local" and (
            not isinstance(template_name, str) or not _LOCAL_TEMPLATE_NAME.fullmatch(template_name)
        ):
            issues.append("manifest local template name is invalid")

        template_version = manifest.get("template_version")
        if not isinstance(template_version, str) or not template_version:
            issues.append("manifest template_version must be a non-empty string")
        template_digest = manifest.get("template_digest")
        if not isinstance(template_digest, str) or not _SHA256.fullmatch(template_digest):
            issues.append("manifest template_digest must be a lowercase SHA-256 digest")
    elif template_name not in TEMPLATE_BY_NAME:
        issues.append("manifest template is not supported by this Samsarix CLI")


def _check_files(project: Path, manifest: dict[str, Any], issues: list[str]) -> None:
    values = manifest.get("files")
    if not isinstance(values, list):
        issues.append("manifest files must be a JSON array")
        return
    if len(values) > _MAX_TRACKED_FILES:
        issues.append(f"manifest files exceeds the {_MAX_TRACKED_FILES}-entry safety limit")
        return
    portable_values = [value.casefold() for value in values if isinstance(value, str)]
    if len(portable_values) != len(set(portable_values)):
        issues.append("manifest files contains duplicate paths")

    declared_paths = {value for value in values if isinstance(value, str)}
    manifest_relative = _MANIFEST_PATH.as_posix()
    if manifest_relative not in declared_paths:
        issues.append(f"manifest does not declare required file: {manifest_relative}")
    if manifest.get("schema_version") == 2 and declared_paths <= {manifest_relative}:
        issues.append("manifest must declare at least one generated file")

    module_name = manifest.get("module_name")
    template_name = manifest.get("template")
    template_kind = manifest.get("template_kind", "builtin")
    if (
        isinstance(module_name, str)
        and template_kind == "builtin"
        and template_name in TEMPLATE_BY_NAME
    ):
        test_file = "tests/test_config.py" if template_name == "discord" else "tests/test_app.py"
        required_paths = {
            ".gitignore",
            "README.md",
            "pyproject.toml",
            f"src/{module_name}/__init__.py",
            f"src/{module_name}/main.py",
            test_file,
        }
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
        elif candidate.is_symlink():
            issues.append(f"generated file is not a regular file: {relative.as_posix()}")
        elif not candidate.is_file():
            issues.append(f"generated file is missing: {relative.as_posix()}")


def _check_file_hashes(
    project: Path,
    manifest: dict[str, Any],
    issues: list[str],
    *,
    strict: bool,
) -> None:
    if manifest.get("schema_version") != 2:
        if strict:
            issues.append("strict drift checking requires a schema_version 2 manifest")
        return

    hashes = manifest.get("file_hashes")
    if not isinstance(hashes, dict):
        issues.append("manifest file_hashes must be a JSON object")
        return
    if len(hashes) > _MAX_GENERATED_FILES:
        issues.append(f"manifest file_hashes exceeds the {_MAX_GENERATED_FILES}-entry safety limit")
        return
    portable_hash_paths = [value.casefold() for value in hashes]
    if len(portable_hash_paths) != len(set(portable_hash_paths)):
        issues.append("manifest file_hashes contains duplicate paths")

    files = manifest.get("files")
    if isinstance(files, list):
        expected_paths = {
            value
            for value in files
            if isinstance(value, str) and value != _MANIFEST_PATH.as_posix()
        }
        actual_paths = set(hashes)
        for path in sorted(expected_paths - actual_paths):
            issues.append(f"manifest file_hashes does not declare generated file: {path}")
        for path in sorted(actual_paths - expected_paths):
            issues.append(f"manifest file_hashes contains undeclared file: {path}")

    for value, expected_digest in hashes.items():
        relative = _safe_relative_path(value)
        if relative is None:
            issues.append(f"manifest file_hashes contains an unsafe file path: {value!r}")
            continue
        if not isinstance(expected_digest, str) or not _SHA256.fullmatch(expected_digest):
            issues.append(f"manifest file_hashes contains an invalid SHA-256 digest: {value}")
            continue
        if not strict:
            continue

        candidate = project.joinpath(*relative.parts)
        try:
            resolved_candidate = candidate.resolve(strict=False)
        except OSError:
            continue
        if (
            not resolved_candidate.is_relative_to(project)
            or candidate.is_symlink()
            or not candidate.is_file()
        ):
            continue
        try:
            content = _read_bounded(
                candidate,
                _MAX_PYPROJECT_BYTES,
                f"generated file {relative.as_posix()}",
            )
        except ValueError as exc:
            issues.append(str(exc))
            continue
        actual_digest = hashlib.sha256(content).hexdigest()
        if actual_digest != expected_digest:
            issues.append(f"generated file was modified: {relative.as_posix()}")


def _check_pyproject(project: Path, manifest: dict[str, Any], issues: list[str]) -> None:
    if manifest.get("template_kind", "builtin") != "builtin":
        return
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


def check_project(project: Path, *, strict: bool = False) -> CheckResult:
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
    _check_file_hashes(resolved_project, manifest, issues, strict=strict)
    _check_pyproject(resolved_project, manifest, issues)
    return CheckResult(resolved_project, tuple(issues))

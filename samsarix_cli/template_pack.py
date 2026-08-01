"""Bounded, non-executing local template packs."""

import hashlib
import os
import re
import stat
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

METADATA_FILENAME = "samsarix-template.toml"
TEMPLATE_DIRECTORY = "template"
MAX_METADATA_BYTES = 64 * 1024
MAX_TEMPLATE_FILES = 256
MAX_TEMPLATE_ENTRIES = 1024
MAX_TEMPLATE_FILE_BYTES = 1024 * 1024
MAX_TEMPLATE_TOTAL_BYTES = 4 * 1024 * 1024

_PACK_NAME = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
_PACK_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,63}$")
_TOKEN = re.compile(r"@@[^@\r\n]+@@")
_TOKENS = ("@@PROJECT_NAME@@", "@@MODULE_NAME@@", "@@COMMAND_NAME@@")
_INVALID_WINDOWS_CHARACTERS = frozenset('<>:"|?*')
_WINDOWS_RESERVED_NAMES = {
    "AUX",
    "CON",
    "NUL",
    "PRN",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


class TemplatePackError(ValueError):
    """A safe-to-display template-pack validation failure."""


@dataclass(frozen=True, slots=True)
class TemplateFile:
    """One validated UTF-8 file stored in a template pack."""

    path: str
    content: str


@dataclass(frozen=True, slots=True)
class TemplatePack:
    """Validated metadata and files for a non-executing local template."""

    description: str
    digest: str
    files: tuple[TemplateFile, ...]
    name: str
    root: Path
    version: str

    def render(self, project_name: str, module_name: str) -> dict[str, str]:
        """Substitute the three supported values into safe paths and text."""
        values = {
            "@@COMMAND_NAME@@": project_name.lower().replace("_", "-"),
            "@@MODULE_NAME@@": module_name,
            "@@PROJECT_NAME@@": project_name,
        }
        rendered: dict[str, str] = {}
        portable_paths: set[str] = set()
        for template_file in self.files:
            path = _substitute(template_file.path, values, label=template_file.path)
            _validate_rendered_path(path)
            portable_path = path.casefold()
            if portable_path in portable_paths:
                raise TemplatePackError(f"template renders duplicate file path: {path}")
            portable_paths.add(portable_path)
            rendered[path] = _substitute(template_file.content, values, label=template_file.path)
        return rendered


def _read_bounded(path: Path, limit: int, label: str) -> bytes:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise TemplatePackError(f"cannot read {label}: {exc}") from exc
    if size > limit:
        raise TemplatePackError(f"{label} exceeds the {limit}-byte safety limit")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise TemplatePackError(f"cannot read {label}: {exc}") from exc


def _is_link_like(path: Path, label: str) -> bool:
    """Detect symbolic links and Windows reparse points without following them."""
    try:
        information = path.lstat()
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise TemplatePackError(f"cannot inspect {label}: {exc}") from exc
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    file_attributes = getattr(information, "st_file_attributes", 0)
    return stat.S_ISLNK(information.st_mode) or bool(file_attributes & reparse_flag)


def _metadata(path: Path) -> tuple[str, str, str]:
    raw = _read_bounded(path, MAX_METADATA_BYTES, "template metadata")
    try:
        parsed = tomllib.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise TemplatePackError(f"template metadata is not valid UTF-8 TOML: {exc}") from exc

    expected_keys = {"description", "name", "schema_version", "version"}
    unknown_keys = sorted(set(parsed) - expected_keys)
    if unknown_keys:
        raise TemplatePackError(f"template metadata contains unknown key: {unknown_keys[0]}")
    if parsed.get("schema_version") != 1:
        raise TemplatePackError("template schema_version must be 1")

    name = parsed.get("name")
    if not isinstance(name, str) or not _PACK_NAME.fullmatch(name):
        raise TemplatePackError(
            "template name must start with a lowercase letter, contain only lowercase letters, "
            "numbers, or hyphens, and be at most 64 characters"
        )
    version = parsed.get("version")
    if not isinstance(version, str) or not _PACK_VERSION.fullmatch(version):
        raise TemplatePackError(
            "template version must be a 1-64 character identifier containing only letters, "
            "numbers, dots, underscores, plus signs, or hyphens"
        )
    description = parsed.get("description")
    if (
        not isinstance(description, str)
        or not description.strip()
        or len(description) > 256
        or "\n" in description
        or "\r" in description
    ):
        raise TemplatePackError(
            "template description must be one non-empty line of at most 256 characters"
        )
    return name, version, description.strip()


def _unknown_token(value: str) -> str | None:
    for match in _TOKEN.findall(value):
        if match not in _TOKENS:
            return str(match)
    return None


def _validate_source_path(path: str) -> None:
    relative = PurePosixPath(path)
    if (
        relative.is_absolute()
        or not relative.parts
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise TemplatePackError(f"template contains an unsafe file path: {path}")
    unknown = _unknown_token(path)
    if unknown is not None:
        raise TemplatePackError(
            f"template file path uses unsupported placeholder {unknown}: {path}"
        )


def _validate_rendered_path(path: str) -> None:
    relative = PurePosixPath(path)
    if (
        relative.is_absolute()
        or not relative.parts
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise TemplatePackError(f"template renders an unsafe file path: {path}")
    first = relative.parts[0].casefold()
    if first in {".git", ".samsarix"}:
        raise TemplatePackError(f"template cannot write reserved generator path: {path}")
    for part in relative.parts:
        if (
            not part
            or part.endswith((" ", "."))
            or any(
                character in _INVALID_WINDOWS_CHARACTERS or ord(character) < 32
                for character in part
            )
            or part.split(".", 1)[0].upper() in _WINDOWS_RESERVED_NAMES
        ):
            raise TemplatePackError(f"template renders a non-portable file path: {path}")


def _substitute(value: str, replacements: dict[str, str], *, label: str) -> str:
    unknown = _unknown_token(value)
    if unknown is not None:
        raise TemplatePackError(f"template file uses unsupported placeholder {unknown}: {label}")
    rendered = value
    for token, replacement in replacements.items():
        rendered = rendered.replace(token, replacement)
    return rendered


def _digest(name: str, version: str, description: str, files: list[TemplateFile]) -> str:
    digest = hashlib.sha256()
    for value in ("samsarix-template-pack-v1", name, version, description):
        digest.update(value.encode("utf-8"))
        digest.update(b"\0")
    for template_file in files:
        digest.update(template_file.path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(template_file.content.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def load_template_pack(path: Path) -> TemplatePack:
    """Load a local template directory without following links or executing code."""
    requested = path.expanduser()
    if _is_link_like(requested, "template pack root"):
        raise TemplatePackError("template pack root cannot be a symbolic link or reparse point")
    resolved = requested.resolve(strict=False)
    if not resolved.is_dir():
        raise TemplatePackError(f"template pack directory does not exist: {resolved}")

    metadata_path = resolved / METADATA_FILENAME
    if _is_link_like(metadata_path, "template metadata") or not metadata_path.is_file():
        raise TemplatePackError(f"template pack must contain a regular {METADATA_FILENAME} file")
    name, version, description = _metadata(metadata_path)

    template_root = resolved / TEMPLATE_DIRECTORY
    if _is_link_like(template_root, "template directory") or not template_root.is_dir():
        raise TemplatePackError(
            f"template pack must contain a regular {TEMPLATE_DIRECTORY}/ directory"
        )

    files: list[TemplateFile] = []
    total_bytes = 0
    pending = [template_root]
    entry_count = 0
    try:
        while pending:
            directory = pending.pop()
            with os.scandir(directory) as entries:
                for entry in entries:
                    entry_count += 1
                    if entry_count > MAX_TEMPLATE_ENTRIES:
                        raise TemplatePackError(
                            f"template exceeds the {MAX_TEMPLATE_ENTRIES}-entry safety limit"
                        )
                    candidate = Path(entry.path)
                    relative = candidate.relative_to(template_root).as_posix()
                    if entry.is_symlink() or _is_link_like(candidate, f"template entry {relative}"):
                        raise TemplatePackError(
                            f"template cannot contain symbolic links or reparse points: {relative}"
                        )
                    if entry.is_dir(follow_symlinks=False):
                        pending.append(candidate)
                        continue
                    if not entry.is_file(follow_symlinks=False):
                        raise TemplatePackError(f"template contains a non-regular file: {relative}")
                    if len(files) >= MAX_TEMPLATE_FILES:
                        raise TemplatePackError(
                            f"template exceeds the {MAX_TEMPLATE_FILES}-file safety limit"
                        )
                    _validate_source_path(relative)
                    raw = _read_bounded(
                        candidate,
                        MAX_TEMPLATE_FILE_BYTES,
                        f"template file {relative}",
                    )
                    total_bytes += len(raw)
                    if total_bytes > MAX_TEMPLATE_TOTAL_BYTES:
                        raise TemplatePackError(
                            "template files exceed the "
                            f"{MAX_TEMPLATE_TOTAL_BYTES}-byte total safety limit"
                        )
                    try:
                        content = raw.decode("utf-8")
                    except UnicodeDecodeError as exc:
                        raise TemplatePackError(
                            f"template file is not valid UTF-8 text: {relative}"
                        ) from exc
                    content = content.replace("\r\n", "\n").replace("\r", "\n")
                    unknown = _unknown_token(content)
                    if unknown is not None:
                        raise TemplatePackError(
                            f"template file uses unsupported placeholder {unknown}: {relative}"
                        )
                    files.append(TemplateFile(relative, content))
    except TemplatePackError:
        raise
    except OSError as exc:
        raise TemplatePackError(f"cannot enumerate template files: {exc}") from exc

    if not files:
        raise TemplatePackError("template pack must contain at least one template file")
    files.sort(key=lambda template_file: template_file.path)
    digest = _digest(name, version, description, files)
    return TemplatePack(description, digest, tuple(files), name, resolved, version)

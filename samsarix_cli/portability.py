"""Shared cross-platform filename rules."""

INVALID_WINDOWS_CHARACTERS = frozenset('<>:"|?*')
WINDOWS_RESERVED_NAMES = {
    "AUX",
    "CON",
    "NUL",
    "PRN",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


def is_portable_path_part(part: str) -> bool:
    """Return whether a relative path component is portable to Windows."""
    return not (
        not part
        or "\\" in part
        or part.endswith((" ", "."))
        or any(character in INVALID_WINDOWS_CHARACTERS or ord(character) < 32 for character in part)
        or part.split(".", 1)[0].upper() in WINDOWS_RESERVED_NAMES
    )

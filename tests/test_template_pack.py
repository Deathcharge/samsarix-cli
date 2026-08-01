"""Safety and rendering contracts for local template packs."""

import os
from pathlib import Path

import pytest

import samsarix_cli.template_pack as template_pack_module
from samsarix_cli.template_pack import (
    TemplateFile,
    TemplatePack,
    TemplatePackError,
    load_template_pack,
)


def _pack(tmp_path: Path, files: dict[str, str | bytes] | None = None) -> Path:
    root = tmp_path / "pack"
    template = root / "template"
    template.mkdir(parents=True)
    (root / "samsarix-template.toml").write_text(
        """\
schema_version = 1
name = "company-api"
version = "1.2.0"
description = "Company API service standard"
""",
        encoding="utf-8",
    )
    selected_files = files or {
        "README.md": "# @@PROJECT_NAME@@\n",
        "src/@@MODULE_NAME@@/__init__.py": '"""@@PROJECT_NAME@@ package."""\n',
        "run.txt": "@@COMMAND_NAME@@\n",
    }
    for relative_path, content in selected_files.items():
        target = template.joinpath(*relative_path.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8", newline="")
    return root


def test_valid_pack_is_deterministic_and_renders_supported_values(tmp_path: Path) -> None:
    root = _pack(tmp_path)

    first = load_template_pack(root)
    second = load_template_pack(root)
    rendered = first.render("Useful_API", "useful_api")

    assert first.name == "company-api"
    assert first.version == "1.2.0"
    assert first.description == "Company API service standard"
    assert len(first.digest) == 64
    assert first.digest == second.digest
    assert rendered == {
        "README.md": "# Useful_API\n",
        "run.txt": "useful-api\n",
        "src/useful_api/__init__.py": '"""Useful_API package."""\n',
    }


@pytest.mark.parametrize(
    ("metadata", "message"),
    [
        ("schema_version = 2\n", "schema_version must be 1"),
        (
            'schema_version = 1\nname = "Bad_Name"\nversion = "1"\ndescription = "ok"\n',
            "template name must start with a lowercase letter",
        ),
        (
            'schema_version = 1\nname = "pack"\nversion = "bad version"\ndescription = "ok"\n',
            "template version must be",
        ),
        (
            'schema_version = 1\nname = "pack"\nversion = "1"\ndescription = ""\n',
            "template description must be",
        ),
        (
            'schema_version = 1\nname = "pack"\nversion = "1"\ndescription = "ok"\nextra = true\n',
            "unknown key: extra",
        ),
    ],
)
def test_metadata_contract_is_strict(tmp_path: Path, metadata: str, message: str) -> None:
    root = _pack(tmp_path)
    (root / "samsarix-template.toml").write_text(metadata, encoding="utf-8")

    with pytest.raises(TemplatePackError, match=message):
        load_template_pack(root)


def test_metadata_and_template_directory_are_required(tmp_path: Path) -> None:
    root = tmp_path / "pack"
    root.mkdir()

    with pytest.raises(TemplatePackError, match="must contain a regular samsarix-template.toml"):
        load_template_pack(root)

    (root / "samsarix-template.toml").write_text(
        'schema_version = 1\nname = "pack"\nversion = "1"\ndescription = "ok"\n',
        encoding="utf-8",
    )
    with pytest.raises(TemplatePackError, match="must contain a regular template/ directory"):
        load_template_pack(root)


def test_unknown_tokens_are_rejected_in_paths_and_content(tmp_path: Path) -> None:
    content_pack = _pack(tmp_path / "content", {"README.md": "@@SECRET@@"})
    path_pack = _pack(tmp_path / "path", {"@@SECRET@@.txt": "safe"})
    numbered_pack = _pack(tmp_path / "numbered", {"README.md": "@@SECRET_1@@"})

    with pytest.raises(TemplatePackError, match="unsupported placeholder @@SECRET@@"):
        load_template_pack(content_pack)
    with pytest.raises(TemplatePackError, match="unsupported placeholder @@SECRET@@"):
        load_template_pack(path_pack)
    with pytest.raises(TemplatePackError, match="unsupported placeholder @@SECRET_1@@"):
        load_template_pack(numbered_pack)


def test_template_must_contain_utf8_regular_files(tmp_path: Path) -> None:
    binary_pack = _pack(tmp_path / "binary", {"image.bin": b"\xff"})
    empty_pack = _pack(tmp_path / "empty", {})
    for child in (empty_pack / "template").rglob("*"):
        if child.is_file():
            child.unlink()

    with pytest.raises(TemplatePackError, match="not valid UTF-8 text"):
        load_template_pack(binary_pack)
    with pytest.raises(TemplatePackError, match="at least one template file"):
        load_template_pack(empty_pack)


def test_file_size_count_and_total_size_are_bounded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    file_pack = _pack(tmp_path / "file", {"large.txt": "12345"})
    count_pack = _pack(tmp_path / "count", {"one.txt": "1", "two.txt": "2"})
    total_pack = _pack(tmp_path / "total", {"one.txt": "123", "two.txt": "456"})

    monkeypatch.setattr(template_pack_module, "MAX_TEMPLATE_FILE_BYTES", 4)
    with pytest.raises(TemplatePackError, match="4-byte safety limit"):
        load_template_pack(file_pack)

    monkeypatch.setattr(template_pack_module, "MAX_TEMPLATE_FILE_BYTES", 1024)
    monkeypatch.setattr(template_pack_module, "MAX_TEMPLATE_FILES", 1)
    with pytest.raises(TemplatePackError, match="1-file safety limit"):
        load_template_pack(count_pack)

    monkeypatch.setattr(template_pack_module, "MAX_TEMPLATE_FILES", 256)
    monkeypatch.setattr(template_pack_module, "MAX_TEMPLATE_TOTAL_BYTES", 5)
    with pytest.raises(TemplatePackError, match="5-byte total safety limit"):
        load_template_pack(total_pack)


def test_directory_enumeration_is_bounded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _pack(tmp_path, {"README.md": "safe"})
    for index in range(3):
        (root / "template" / f"empty-{index}").mkdir()
    monkeypatch.setattr(template_pack_module, "MAX_TEMPLATE_ENTRIES", 3)

    with pytest.raises(TemplatePackError, match="3-entry safety limit"):
        load_template_pack(root)


def test_links_are_rejected_instead_of_followed(tmp_path: Path) -> None:
    root = _pack(tmp_path)
    external = tmp_path / "outside.txt"
    external.write_text("private", encoding="utf-8")
    link = root / "template/link.txt"
    try:
        os.symlink(external, link)
    except OSError as exc:
        pytest.skip(f"file symlinks are unavailable: {exc}")

    with pytest.raises(
        TemplatePackError,
        match="cannot contain symbolic links or reparse points: link.txt",
    ):
        load_template_pack(root)


def test_pack_root_cannot_be_a_link(tmp_path: Path) -> None:
    root = _pack(tmp_path)
    link = tmp_path / "pack-link"
    try:
        os.symlink(root, link, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlinks are unavailable: {exc}")

    with pytest.raises(TemplatePackError, match="root cannot be a symbolic link"):
        load_template_pack(link)


def test_render_rejects_reserved_nonportable_and_duplicate_paths(tmp_path: Path) -> None:
    reserved = load_template_pack(_pack(tmp_path / "reserved", {".samsarix/data": "x"}))
    nonportable = TemplatePack(
        description="test",
        digest="0" * 64,
        files=(TemplateFile("bad:name", "x"),),
        name="nonportable",
        root=tmp_path,
        version="1",
    )
    duplicate = load_template_pack(
        _pack(
            tmp_path / "duplicate",
            {"@@PROJECT_NAME@@.txt": "one", "demo.TXT": "two"},
        )
    )

    with pytest.raises(TemplatePackError, match="reserved generator path"):
        reserved.render("demo", "demo")
    with pytest.raises(TemplatePackError, match="non-portable file path"):
        nonportable.render("demo", "demo")
    with pytest.raises(TemplatePackError, match="duplicate file path"):
        duplicate.render("demo", "demo")


def test_digest_changes_with_metadata_path_or_content(tmp_path: Path) -> None:
    original = _pack(tmp_path / "original", {"README.md": "one"})
    content = _pack(tmp_path / "content", {"README.md": "two"})
    path = _pack(tmp_path / "path", {"OTHER.md": "one"})
    metadata = _pack(tmp_path / "metadata", {"README.md": "one"})
    metadata_file = metadata / "samsarix-template.toml"
    metadata_file.write_text(
        metadata_file.read_text(encoding="utf-8").replace("1.2.0", "1.2.1"),
        encoding="utf-8",
    )

    digests = {
        load_template_pack(candidate).digest for candidate in (original, content, path, metadata)
    }
    assert len(digests) == 4

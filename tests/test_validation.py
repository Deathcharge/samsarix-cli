"""Adversarial checks for untrusted generated-project metadata."""

import json
import os
from pathlib import Path

import pytest

from samsarix_cli.scaffold import scaffold_project
from samsarix_cli.validation import check_project


def _project(tmp_path: Path) -> Path:
    destination = tmp_path / "validated-project"
    scaffold_project(
        destination=destination,
        project_name=None,
        template_name="fastapi",
        initialize_git=False,
    )
    return destination


def _manifest(project: Path) -> tuple[Path, dict[str, object]]:
    path = project / ".samsarix/project.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def test_missing_generated_file_is_reported(tmp_path: Path) -> None:
    project = _project(tmp_path)
    (project / "README.md").unlink()

    result = check_project(project)

    assert not result.is_valid
    assert "generated file is missing: README.md" in result.issues


def test_manifest_path_traversal_is_rejected_without_reading_outside(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, manifest = _manifest(project)
    files = manifest["files"]
    assert isinstance(files, list)
    files.append("../outside.txt")
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = check_project(project)

    assert not result.is_valid
    assert "manifest contains an unsafe file path: '../outside.txt'" in result.issues


def test_backslash_paths_are_rejected_on_every_platform(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, manifest = _manifest(project)
    manifest["files"] = ["..\\outside.txt"]
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = check_project(project)

    assert "manifest contains an unsafe file path: '..\\\\outside.txt'" in result.issues


def test_duplicate_manifest_entries_are_reported(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, manifest = _manifest(project)
    files = manifest["files"]
    assert isinstance(files, list)
    files.append(files[0])
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = check_project(project)

    assert "manifest files contains duplicate paths" in result.issues


def test_manifest_paths_must_be_portable_and_case_distinct(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, manifest = _manifest(project)
    files = manifest["files"]
    assert isinstance(files, list)
    files.extend(["readme.md", "bad:name"])
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = check_project(project)

    assert "manifest files contains duplicate paths" in result.issues
    assert "manifest contains an unsafe file path: 'bad:name'" in result.issues


def test_manifest_cannot_omit_the_required_file_contract(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, manifest = _manifest(project)
    files = manifest["files"]
    assert isinstance(files, list)
    files.remove("README.md")
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = check_project(project)

    assert "manifest does not declare required file: README.md" in result.issues


def test_local_manifest_must_declare_itself_and_generated_content(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, manifest = _manifest(project)
    manifest.update(
        {
            "files": [],
            "file_hashes": {},
            "template": "local-pack",
            "template_kind": "local",
            "template_version": "1",
        }
    )
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = check_project(project)

    assert "manifest does not declare required file: .samsarix/project.json" in result.issues
    assert "manifest must declare at least one generated file" in result.issues


def test_metadata_symlinks_cannot_escape_the_project(tmp_path: Path) -> None:
    project = _project(tmp_path)
    external = tmp_path / "external.json"
    external.write_text("{}", encoding="utf-8")
    manifest = project / ".samsarix/project.json"
    manifest.unlink()
    try:
        os.symlink(external, manifest)
    except OSError as exc:
        pytest.skip(f"file symlinks are unavailable: {exc}")

    result = check_project(project)

    assert result.issues == ("manifest resolves outside the project",)


def test_external_pyproject_is_reported_but_not_parsed(tmp_path: Path) -> None:
    project = _project(tmp_path)
    external = tmp_path / "external.toml"
    external.write_text("not = [valid", encoding="utf-8")
    pyproject = project / "pyproject.toml"
    pyproject.unlink()
    try:
        os.symlink(external, pyproject)
    except OSError as exc:
        pytest.skip(f"file symlinks are unavailable: {exc}")

    result = check_project(project)

    assert "generated file resolves outside the project: pyproject.toml" in result.issues
    assert "pyproject.toml resolves outside the project" in result.issues
    assert not any(issue.startswith("pyproject.toml is invalid") for issue in result.issues)


def test_invalid_manifest_json_is_a_bounded_failure(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, _manifest_data = _manifest(project)
    path.write_text("not-json", encoding="utf-8")

    result = check_project(project)

    assert not result.is_valid
    assert result.issues[0].startswith("manifest is not valid UTF-8 JSON")


def test_manifest_root_must_be_an_object(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, _manifest_data = _manifest(project)
    path.write_text("[]", encoding="utf-8")

    result = check_project(project)

    assert result.issues == ("manifest root must be a JSON object",)


def test_manifest_must_be_utf8(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, _manifest_data = _manifest(project)
    path.write_bytes(b"\xff")

    result = check_project(project)

    assert result.issues[0].startswith("manifest is not valid UTF-8 JSON")


def test_oversized_manifest_is_rejected_before_parsing(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, _manifest_data = _manifest(project)
    path.write_text(" " * (64 * 1024 + 1), encoding="utf-8")

    result = check_project(project)

    assert result.issues == ("manifest exceeds the 65536-byte safety limit",)


def test_manifest_identity_fields_are_validated(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, manifest = _manifest(project)
    manifest.update(
        {
            "generator": "other",
            "module_name": "wrong",
            "schema_version": 3,
            "template": "unknown",
        }
    )
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = check_project(project)

    assert "manifest schema_version must be 1 or 2" in result.issues
    assert "manifest generator must be 'samsarix-cli'" in result.issues
    assert "manifest module_name must be 'validated_project'" in result.issues
    assert "manifest template is not supported by this Samsarix CLI" in result.issues


def test_schema_one_manifest_remains_compatible(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, manifest = _manifest(project)
    manifest["schema_version"] = 1
    for field in ("file_hashes", "template_digest", "template_kind", "template_version"):
        del manifest[field]
    path.write_text(json.dumps(manifest), encoding="utf-8")

    assert check_project(project).is_valid
    strict_result = check_project(project, strict=True)
    assert strict_result.issues == ("strict drift checking requires a schema_version 2 manifest",)


def test_strict_check_reports_modified_generated_content(tmp_path: Path) -> None:
    project = _project(tmp_path)
    readme = project / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "local edit\n", encoding="utf-8")

    assert check_project(project).is_valid
    result = check_project(project, strict=True)

    assert "generated file was modified: README.md" in result.issues


def test_schema_two_hash_contract_is_validated_without_strict_mode(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, manifest = _manifest(project)
    hashes = manifest["file_hashes"]
    assert isinstance(hashes, dict)
    del hashes["README.md"]
    hashes["untracked.txt"] = "not-a-digest"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    result = check_project(project)

    assert "manifest file_hashes does not declare generated file: README.md" in result.issues
    assert "manifest file_hashes contains undeclared file: untracked.txt" in result.issues
    assert "manifest file_hashes contains an invalid SHA-256 digest: untracked.txt" in result.issues


def test_manifest_project_name_type_and_value_are_validated(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, manifest = _manifest(project)
    manifest["project_name"] = 7
    path.write_text(json.dumps(manifest), encoding="utf-8")
    wrong_type = check_project(project)

    manifest["project_name"] = "bad name"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    invalid_value = check_project(project)

    assert "manifest project_name must be a string" in wrong_type.issues
    assert any(
        issue.startswith("manifest project_name is invalid") for issue in invalid_value.issues
    )


def test_manifest_files_type_and_count_are_bounded(tmp_path: Path) -> None:
    project = _project(tmp_path)
    path, manifest = _manifest(project)
    manifest["files"] = "README.md"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    wrong_type = check_project(project)

    manifest["files"] = [f"file-{index}" for index in range(258)]
    path.write_text(json.dumps(manifest), encoding="utf-8")
    too_many = check_project(project)

    assert "manifest files must be a JSON array" in wrong_type.issues
    assert "manifest files exceeds the 257-entry safety limit" in too_many.issues


def test_manifest_and_pyproject_identity_must_agree(tmp_path: Path) -> None:
    project = _project(tmp_path)
    pyproject = project / "pyproject.toml"
    contents = pyproject.read_text(encoding="utf-8")
    pyproject.write_text(
        contents.replace('name = "validated-project"', 'name = "other"'),
        encoding="utf-8",
    )

    result = check_project(project)

    assert "pyproject.toml project.name does not match the manifest" in result.issues


def test_pyproject_contract_is_validated(tmp_path: Path) -> None:
    project = _project(tmp_path)
    pyproject = project / "pyproject.toml"
    pyproject.write_text("[tool.example]\nvalue = true\n", encoding="utf-8")
    missing_project = check_project(project)

    pyproject.write_text(
        '[project]\nname = "validated-project"\nrequires-python = ">=3.12"\n',
        encoding="utf-8",
    )
    wrong_python = check_project(project)

    pyproject.write_text("not = [valid", encoding="utf-8")
    invalid_toml = check_project(project)

    assert "pyproject.toml must contain a [project] table" in missing_project.issues
    assert "pyproject.toml project.requires-python must be '>=3.11'" in wrong_python.issues
    assert any(issue.startswith("pyproject.toml is invalid") for issue in invalid_toml.issues)


def test_non_project_directory_is_reported_by_library_api(tmp_path: Path) -> None:
    result = check_project(tmp_path / "missing")

    assert result.issues == ("project directory does not exist",)

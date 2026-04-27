from pathlib import Path

import pytest

import modules.security.crypto.checksum_validator as checksum_module
from modules.security.crypto.checksum_validator import (
    BuildIntegrityValidator,
    SecurityError,
    validate_production_integrity,
)


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_generate_checksums_only_keeps_critical_files(tmp_path: Path) -> None:
    _write_file(tmp_path / "modules" / "reflexia" / "core.py", "print('ok')")
    _write_file(tmp_path / "docs" / "readme.md", "# not critical")
    _write_file(tmp_path / "docker-compose.yml", "services: {}")

    validator = BuildIntegrityValidator(base_dir=tmp_path)
    checksums = validator.generate_checksums()

    assert "modules/reflexia/core.py" in checksums
    assert "docker-compose.yml" in checksums
    assert "docs/readme.md" not in checksums


def test_save_manifest_and_validate_integrity_success(tmp_path: Path) -> None:
    _write_file(tmp_path / "modules" / "assistantia" / "core.py", "print('safe')")
    validator = BuildIntegrityValidator(base_dir=tmp_path)

    checksums = validator.generate_checksums()
    manifest_path = validator.save_manifest(  # pyright: ignore[reportUnknownMemberType]
        checksums, metadata={"build_id": "b-1"}
    )
    assert manifest_path.exists()

    assert validator.validate_integrity(manifest_path=manifest_path) is True


def test_validate_integrity_raises_when_manifest_missing(tmp_path: Path) -> None:
    validator = BuildIntegrityValidator(base_dir=tmp_path)
    with pytest.raises(SecurityError):
        validator.validate_integrity()


def test_validate_integrity_detects_modified_and_new_files(tmp_path: Path) -> None:
    target_file = tmp_path / "modules" / "assistantia" / "core.py"
    _write_file(target_file, "print('v1')")
    validator = BuildIntegrityValidator(base_dir=tmp_path)

    manifest_path = validator.save_manifest(  # pyright: ignore[reportUnknownMemberType]
        validator.generate_checksums()
    )
    _write_file(target_file, "print('v2')")
    _write_file(tmp_path / "scripts" / "new_script.py", "print('new')")

    with pytest.raises(SecurityError):
        validator.validate_integrity(manifest_path=manifest_path)

    assert validator.violations_log.exists()
    log_content = validator.violations_log.read_text(encoding="utf-8")
    assert "MODIFIED:" in log_content
    assert "UNAUTHORIZED:" in log_content


def test_quick_check_without_manifest_returns_empty_dict(tmp_path: Path) -> None:
    validator = BuildIntegrityValidator(base_dir=tmp_path)
    assert validator.quick_check() == {}


def test_quick_check_returns_false_for_missing_or_unknown_files(tmp_path: Path) -> None:
    target_file = tmp_path / "modules" / "assistantia" / "core.py"
    _write_file(target_file, "print('v1')")
    validator = BuildIntegrityValidator(base_dir=tmp_path)
    validator.save_manifest(validator.generate_checksums())  # pyright: ignore[reportUnknownMemberType]

    target_file.unlink()
    result = validator.quick_check(
        critical_files=["modules/assistantia/core.py", "modules/security/__init__.py"]
    )
    assert result["modules/assistantia/core.py"] is False
    assert result["modules/security/__init__.py"] is False


def test_validate_production_integrity_returns_false_on_security_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise_security_error(self: BuildIntegrityValidator) -> bool:
        raise SecurityError("boom")

    monkeypatch.setattr(BuildIntegrityValidator, "validate_integrity", _raise_security_error)
    assert validate_production_integrity() is False


def test_generate_build_manifest_uses_injected_base_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _write_file(tmp_path / "modules" / "assistantia" / "core.py", "print('manifest')")

    class _FakeValidator(BuildIntegrityValidator):
        def __init__(self) -> None:
            super().__init__(base_dir=tmp_path)

    monkeypatch.setattr(checksum_module, "BuildIntegrityValidator", _FakeValidator)
    monkeypatch.setattr(checksum_module, "_get_git_commit", lambda: "deadbeef")

    manifest_path = checksum_module.generate_build_manifest()
    assert manifest_path.exists()

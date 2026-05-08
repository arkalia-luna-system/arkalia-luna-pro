from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from modules.security.crypto.vault_manager import ArkaliaVault, VaultError, migrate_from_env_file


def test_migrate_from_env_file_raises_when_source_cannot_be_read(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.env"
    vault = ArkaliaVault(base_dir=tmp_path)

    # Fichier absent: comportement attendu = 0 migration, pas d'exception
    assert migrate_from_env_file(missing_file, vault) == 0


def test_migrate_from_env_file_raises_when_backup_fails(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("TOKEN=abc", encoding="utf-8")
    vault = ArkaliaVault(base_dir=tmp_path)

    def raise_on_backup(*_args: object, **_kwargs: object) -> int:
        raise OSError("read-only fs")

    monkeypatch.setattr(Path, "write_text", raise_on_backup)

    with pytest.raises(VaultError, match="Failed to backup env file"):
        migrate_from_env_file(env_file, vault, backup_env=True)


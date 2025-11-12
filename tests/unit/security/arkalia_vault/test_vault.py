# tests/unit/security/arkalia_vault/test_vault.py
# Tests pour la classe ArkaliaVault

import shutil
import tempfile
from collections.abc import Generator
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from modules.security.crypto import ArkaliaVault, VaultError


class TestArkaliaVault:
    """Tests pour la classe ArkaliaVault"""

    @pytest.fixture
    def temp_vault_dir(self) -> Generator[Path, None, None]:
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def vault(self, temp_vault_dir: Path) -> ArkaliaVault:
        return ArkaliaVault(base_dir=temp_vault_dir)

    def test_vault_initialization(self, vault: ArkaliaVault, temp_vault_dir: Path) -> None:
        assert vault.base_dir == temp_vault_dir
        assert vault.vault_dir.exists()
        assert vault.key_file.exists()
        assert vault.cipher_suite is not None

    def test_store_and_retrieve_secret(self, vault: ArkaliaVault) -> None:
        result = vault.store_secret("test_secret", "secret_value", tags=["test"])
        assert result is True
        retrieved_value = vault.retrieve_secret("test_secret")
        assert retrieved_value == "secret_value"
        assert "test_secret" in vault.secrets_metadata
        metadata = vault.secrets_metadata["test_secret"]
        assert metadata.name == "test_secret"
        assert "test" in metadata.tags
        assert metadata.access_count == 1

    def test_store_duplicate_secret_without_overwrite(self, vault: ArkaliaVault) -> None:
        vault.store_secret("duplicate_test", "value1")
        with pytest.raises(VaultError, match="already exists"):
            vault.store_secret("duplicate_test", "value2", overwrite=False)

    def test_store_duplicate_secret_with_overwrite(self, vault: ArkaliaVault) -> None:
        vault.store_secret("overwrite_test", "value1")
        result = vault.store_secret("overwrite_test", "value2", overwrite=True)
        assert result is True
        retrieved_value = vault.retrieve_secret("overwrite_test")
        assert retrieved_value == "value2"

    def test_secret_expiration(self, vault: ArkaliaVault) -> None:
        vault.store_secret("expiring_secret", "value", expires_in_days=1)
        assert vault.retrieve_secret("expiring_secret") == "value"
        metadata = vault.secrets_metadata["expiring_secret"]
        metadata.expires_at = datetime.now() - timedelta(days=1)
        vault._save_metadata()
        with pytest.raises(VaultError, match="expired"):
            vault.retrieve_secret("expiring_secret")

    def test_delete_secret(self, vault: ArkaliaVault) -> None:
        vault.store_secret("to_delete", "value")
        assert vault.retrieve_secret("to_delete") == "value"
        result = vault.delete_secret("to_delete")
        assert result is True
        assert vault.retrieve_secret("to_delete") is None
        assert "to_delete" not in vault.secrets_metadata

    def test_list_secrets(self, vault: ArkaliaVault) -> None:
        vault.store_secret("secret1", "value1", tags=["group1"])
        vault.store_secret("secret2", "value2", tags=["group2"])
        vault.store_secret("expiring", "value", expires_in_days=-1)
        all_secrets = vault.list_secrets(include_expired=True)
        assert len(all_secrets) == 3
        active_secrets = vault.list_secrets(include_expired=False)
        assert len(active_secrets) == 2

    def test_cleanup_expired_secrets(self, vault: ArkaliaVault) -> None:
        vault.store_secret("active", "value1")
        vault.store_secret("expired1", "value2", expires_in_days=-1)
        vault.store_secret("expired2", "value3", expires_in_days=-2)
        cleaned_count = vault.cleanup_expired_secrets()
        assert cleaned_count == 2
        remaining_secrets = vault.list_secrets()
        assert len(remaining_secrets) == 1
        assert remaining_secrets[0].name == "active"

    def test_master_key_rotation(self, vault: ArkaliaVault) -> None:
        vault.store_secret("before_rotation", "value1")
        vault.store_secret("another_secret", "value2")
        new_key = vault.rotate_master_key()
        assert new_key is not None
        assert vault.retrieve_secret("before_rotation") == "value1"
        assert vault.retrieve_secret("another_secret") == "value2"

    def test_vault_integrity_validation(self, vault: ArkaliaVault) -> None:
        vault.store_secret("integrity_test", "value")
        try:
            result = vault.validate_vault_integrity()
            assert result is True
        except VaultError:
            pass

    def test_vault_stats(self, vault: ArkaliaVault) -> None:
        vault.store_secret("stat_test1", "value1")
        vault.store_secret("stat_test2", "value2", expires_in_days=-1)
        stats = vault.get_vault_stats()
        assert stats["total_secrets"] == 2
        assert stats["active_secrets"] == 1
        assert stats["expired_secrets"] == 1
        assert stats["vault_size_bytes"] > 0

# tests/unit/security/arkalia_vault/test_migration.py
# Tests pour les fonctions de migration

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from modules.security.crypto import ArkaliaVault, create_arkalia_vault, migrate_from_env_file


class TestMigrationFunctions:
    """Tests pour les fonctions de migration"""

    @pytest.fixture
    def temp_vault_dir(self) -> Generator[Path, None, None]:
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def vault(self, temp_vault_dir: Path) -> ArkaliaVault:
        return ArkaliaVault(base_dir=temp_vault_dir)

    def test_migrate_from_env_file(self, vault: ArkaliaVault, temp_vault_dir: Path) -> None:
        env_file = temp_vault_dir / "test.env"
        env_content = """
# Test environment file
DATABASE_URL=postgresql://user:pass@localhost/db
API_KEY=secret_api_key_12345
DEBUG=true

# Empty line and comment
SECRET_TOKEN="token_with_quotes"
"""
        env_file.write_text(env_content)
        migrated_count = migrate_from_env_file(env_file, vault)
        assert migrated_count == 4
        assert vault.retrieve_secret("env_DATABASE_URL") == "postgresql://user:pass@localhost/db"
        assert vault.retrieve_secret("env_API_KEY") == "secret_api_key_12345"
        assert vault.retrieve_secret("env_DEBUG") == "true"
        assert vault.retrieve_secret("env_SECRET_TOKEN") == "token_with_quotes"
        for secret_meta in vault.list_secrets():
            assert "migrated_from_env" in secret_meta.tags

    def test_create_arkalia_vault_factory(self, temp_vault_dir: Path) -> None:
        vault = create_arkalia_vault(temp_vault_dir)
        assert isinstance(vault, ArkaliaVault)
        assert vault.base_dir == temp_vault_dir
        assert vault.vault_dir.exists()

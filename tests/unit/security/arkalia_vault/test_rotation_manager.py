# tests/unit/security/arkalia_vault/test_rotation_manager.py
# Tests pour le gestionnaire de rotation

import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from modules.security.crypto import ArkaliaVault, RotationManager, RotationPolicy, RotationStrategy


class TestRotationManager:
    """Tests pour le gestionnaire de rotation"""

    @pytest.fixture
    def temp_vault_dir(self) -> Path:
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def vault(self, temp_vault_dir: Path) -> ArkaliaVault:
        return ArkaliaVault(base_dir=temp_vault_dir)

    @pytest.fixture
    def rotation_manager(self, vault: ArkaliaVault) -> RotationManager:
        return RotationManager(vault)

    def test_add_rotation_policy(self, rotation_manager: RotationManager) -> None:
        policy = RotationPolicy(
            name="test_secret", strategy=RotationStrategy.TIME_BASED, interval_days=7
        )
        rotation_manager.add_policy(policy)
        assert "test_secret" in rotation_manager.policies
        assert rotation_manager.policies["test_secret"].interval_days == 7

    def test_time_based_rotation_check(
        self, rotation_manager: RotationManager, vault: ArkaliaVault
    ) -> None:
        vault.store_secret("time_test", "old_value")
        policy = RotationPolicy(
            name="time_test", strategy=RotationStrategy.TIME_BASED, interval_days=1
        )
        rotation_manager.add_policy(policy)
        metadata = vault.secrets_metadata["time_test"]
        metadata.created_at = datetime.now() - timedelta(days=2)
        vault._save_metadata()
        needs_rotation, reason = rotation_manager.check_rotation_needed("time_test")
        assert needs_rotation is True
        assert "Time-based rotation needed" in reason

    def test_access_count_rotation_check(
        self, rotation_manager: RotationManager, vault: ArkaliaVault
    ) -> None:
        vault.store_secret("access_test", "value")
        policy = RotationPolicy(
            name="access_test",
            strategy=RotationStrategy.ACCESS_COUNT,
            max_access_count=3,
        )
        rotation_manager.add_policy(policy)
        metadata = vault.secrets_metadata["access_test"]
        metadata.access_count = 5
        vault._save_metadata()
        needs_rotation, reason = rotation_manager.check_rotation_needed("access_test")
        assert needs_rotation is True
        assert "Access count rotation needed" in reason

    def test_secret_rotation(self, rotation_manager: RotationManager, vault: ArkaliaVault) -> None:
        vault.store_secret("rotate_me", "old_value")
        policy = RotationPolicy(
            name="rotate_me", strategy=RotationStrategy.MANUAL, auto_generate=True
        )
        rotation_manager.add_policy(policy)
        result = rotation_manager.rotate_secret("rotate_me")
        assert result is True
        new_value = vault.retrieve_secret("rotate_me")
        assert new_value != "old_value"
        assert new_value is not None
        backup_secrets = [s for s in vault.list_secrets() if "backup" in s.name]
        assert len(backup_secrets) > 0

    def test_bulk_rotation_check(
        self, rotation_manager: RotationManager, vault: ArkaliaVault
    ) -> None:
        for i in range(3):
            secret_name = f"bulk_test_{i}"
            vault.store_secret(secret_name, f"value_{i}")
            policy = RotationPolicy(
                name=secret_name, strategy=RotationStrategy.TIME_BASED, interval_days=1
            )
            rotation_manager.add_policy(policy)
        metadata = vault.secrets_metadata["bulk_test_1"]
        metadata.created_at = datetime.now() - timedelta(days=2)
        vault._save_metadata()
        results = rotation_manager.bulk_rotation_check()
        assert len(results) == 3
        assert results["bulk_test_1"][0] is True
        assert results["bulk_test_0"][0] is False

# tests/unit/security/arkalia_vault/test_token_manager.py
# Tests pour le gestionnaire de tokens

import shutil
import tempfile
from pathlib import Path

import pytest

from modules.security.crypto import ArkaliaVault, TokenManager, TokenStatus, TokenType


class TestTokenManager:
    """Tests pour le gestionnaire de tokens"""

    @pytest.fixture
    def temp_vault_dir(self) -> Path:
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def vault(self, temp_vault_dir: Path) -> ArkaliaVault:
        return ArkaliaVault(base_dir=temp_vault_dir)

    @pytest.fixture
    def token_manager(self, vault: ArkaliaVault) -> TokenManager:
        return TokenManager(vault)

    def test_generate_session_token(self, token_manager: TokenManager) -> None:
        token_id, token_value = token_manager.generate_token(
            token_type=TokenType.SESSION,
            user_id="user123",
            permissions=["read", "write"],
            expires_in_hours=24,
        )
        assert token_id.startswith("session_")
        assert token_value is not None
        assert token_id in token_manager.token_metadata
        metadata = token_manager.token_metadata[token_id]
        assert metadata.associated_user == "user123"
        assert metadata.permissions == ["read", "write"]

    def test_generate_api_key(self, token_manager: TokenManager) -> None:
        token_id, token_value = token_manager.generate_token(
            token_type=TokenType.API_KEY,
            service_id="service123",
            permissions=["api_access"],
        )
        assert token_id.startswith("api_key_")
        assert token_value.startswith("ak_api_key_")
        metadata = token_manager.token_metadata[token_id]
        assert metadata.associated_service == "service123"

    def test_validate_token(self, token_manager: TokenManager) -> None:
        token_id, token_value = token_manager.generate_token(
            token_type=TokenType.API_KEY,
            service_id="test_service",
            permissions=["read"],
        )
        is_valid, metadata, reason = token_manager.validate_token(token_value)
        assert is_valid is True
        assert metadata is not None
        assert metadata.token_id == token_id
        assert reason == "Valid"

    def test_revoke_token(self, token_manager: TokenManager) -> None:
        token_id, token_value = token_manager.generate_token(
            token_type=TokenType.SESSION, user_id="test_user"
        )
        result = token_manager.revoke_token(token_id)
        assert result is True
        is_valid, metadata, reason = token_manager.validate_token(token_value)
        assert is_valid is False
        assert "revoked" in reason.lower()

    def test_cleanup_expired_tokens(self, token_manager: TokenManager) -> None:
        token_id, token_value = token_manager.generate_token(
            token_type=TokenType.SESSION,
            user_id="test_user",
            expires_in_hours=-1,
        )
        cleaned_count = token_manager.cleanup_expired_tokens()
        assert cleaned_count == 1
        assert (
            token_id not in token_manager.token_metadata
            or token_manager.token_metadata[token_id].status == TokenStatus.REVOKED
        )

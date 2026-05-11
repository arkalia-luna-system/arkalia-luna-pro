import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from modules.security.crypto import ArkaliaVault, TokenManager, TokenType


@pytest.fixture
def temp_vault_dir() -> Generator[Path, None, None]:
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def token_manager(temp_vault_dir: Path) -> TokenManager:
    vault = ArkaliaVault(base_dir=temp_vault_dir)
    return TokenManager(vault)


def test_validate_token_denies_missing_required_permission(token_manager: TokenManager) -> None:
    _, token_value = token_manager.generate_token(  # pyright: ignore[reportUnknownMemberType]
        token_type=TokenType.API_KEY,
        service_id="service-alpha",
        permissions=["read"],
    )

    is_valid, metadata, reason = token_manager.validate_token(
        token_value, required_permissions=["read", "write"]
    )

    assert is_valid is False
    assert metadata is not None
    assert reason == "Insufficient permissions"


def test_refresh_token_returns_new_access_token(token_manager: TokenManager) -> None:
    _, refresh_token = token_manager.generate_token(  # pyright: ignore[reportUnknownMemberType]
        token_type=TokenType.REFRESH_TOKEN,
        user_id="user-42",
        permissions=["read"],
        expires_in_hours=12,
    )

    new_access_id, new_access_value = token_manager.refresh_token(refresh_token)

    assert new_access_id is not None
    assert new_access_value is not None
    assert new_access_id in token_manager.token_metadata
    assert token_manager.token_metadata[new_access_id].token_type == TokenType.ACCESS_TOKEN

    # Le refresh token est one-time: une seconde utilisation doit échouer.
    second_access_id, second_access_value = token_manager.refresh_token(refresh_token)
    assert second_access_id is None
    assert second_access_value is None


def test_custom_claims_cannot_override_reserved_jwt_fields(token_manager: TokenManager) -> None:
    token_id, token_value = token_manager.generate_token(  # pyright: ignore[reportUnknownMemberType]
        token_type=TokenType.ACCESS_TOKEN,  # pyright: ignore[reportUnknownMemberType]
        user_id="user-claims",
        permissions=["read"],
        custom_claims={
            "permissions": ["admin"],  # doit être ignoré
            "token_type": "api_key",  # doit être ignoré
            "ctx_trace_id": "trace-123",  # autorisé
        },
    )

    is_valid, metadata, reason = token_manager.validate_token(token_value)
    assert is_valid is True, reason
    assert metadata is not None
    assert metadata.token_id == token_id
    assert metadata.permissions == ["read"]


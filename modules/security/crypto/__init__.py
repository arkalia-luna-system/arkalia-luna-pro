"""
Module crypto de sécurité.

Ce module contient les composants de cryptographie et de gestion des secrets :
- Vault manager pour le stockage sécurisé
- Rotation de secrets
- Gestion du cycle de vie des tokens
- Validation d'intégrité des builds
"""

# 🔐 modules/security/crypto/__init__.py
# Cryptographie et intégrité Arkalia-LUNA

from .checksum_validator import BuildIntegrityValidator, SecurityError
from .secret_rotation import (
    RotationManager,
    RotationPolicy,
    RotationStrategy,
    SecretGenerator,
    create_access_based_policy,
    create_daily_rotation_policy,
    create_monthly_rotation_policy,
    create_weekly_rotation_policy,
)
from .token_lifecycle import (
    TokenManager,
    TokenMetadata,
    TokenStatus,
    TokenType,
    create_api_key,
    create_session_token,
)
from .vault_manager import (
    ArkaliaVault,
    SecretMetadata,
    VaultError,
    create_arkalia_vault,
    migrate_from_env_file,
)

# from .merkle_chains import SnapshotMerkleChain
# from .env_encryption import EnvironmentCrypto

__all__ = [
    # Base integrity validation
    "BuildIntegrityValidator",
    "SecurityError",
    # Arkalia Vault Enterprise
    "ArkaliaVault",
    "VaultError",
    "SecretMetadata",
    "create_arkalia_vault",
    "migrate_from_env_file",
    # Secret Rotation System
    "RotationManager",
    "RotationPolicy",
    "RotationStrategy",
    "SecretGenerator",
    "create_daily_rotation_policy",
    "create_weekly_rotation_policy",
    "create_monthly_rotation_policy",
    "create_access_based_policy",
    # Token Lifecycle Management
    "TokenManager",
    "TokenType",
    "TokenStatus",
    "TokenMetadata",
    "create_session_token",
    "create_api_key",
]

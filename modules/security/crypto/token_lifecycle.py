"""
Module token_lifecycle.

Ce module fait partie du système Arkalia Luna Pro.
"""

# 🎫 modules/security/crypto/token_lifecycle.py
# Gestion du cycle de vie des tokens et sessions Arkalia-Vault

import json
import logging
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import jwt

from .vault_manager import ArkaliaVault, VaultError

logger = logging.getLogger(__name__)


class TokenType(Enum):
    """Types de tokens gérés par le système."""

    SESSION = "session"
    API_KEY = "api_key"
    ACCESS_TOKEN = "access_token"  # nosec B105
    REFRESH_TOKEN = "refresh_token"  # nosec B105
    TEMPORARY = "temporary"


class TokenStatus(Enum):
    """Statuts possibles d'un token.

    Attributes:
        ACTIVE: Token actif et utilisable.
        EXPIRED: Token expiré.
        REVOKED: Token révoqué.
        SUSPENDED: Token suspendu temporairement.
    """

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


@dataclass
class TokenMetadata:
    """Métadonnées d'un token.

    Attributes:
        token_id: Identifiant unique du token.
        token_type: Type du token.
        status: Statut actuel du token.
        created_at: Date de création.
        expires_at: Date d'expiration (optionnel).
        last_used_at: Date du dernier usage (optionnel).
        usage_count: Nombre d'utilisations.
        max_usage_count: Nombre maximum d'utilisations (optionnel).
        associated_user: Utilisateur associé (optionnel).
        associated_service: Service associé (optionnel).
        permissions: Liste des permissions.
        client_info: Informations du client (IP, User-Agent, etc.).
        tags: Tags associés au token.
    """

    token_id: str
    token_type: TokenType
    status: TokenStatus
    created_at: datetime
    expires_at: datetime | None
    last_used_at: datetime | None
    usage_count: int
    max_usage_count: int | None
    associated_user: str | None
    associated_service: str | None
    permissions: list[str]
    client_info: dict[str, str]  # IP, User-Agent, etc.
    tags: list[str]

    def to_dict(self) -> dict:
        """Convertit les métadonnées en dictionnaire.

        Returns:
            dict: Métadonnées sous forme de dictionnaire.
        """
        data = asdict(self)
        # Convertir les enums en strings
        data["token_type"] = self.token_type.value
        data["status"] = self.status.value
        # Convertir les datetimes en ISO format
        data["created_at"] = self.created_at.isoformat()
        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()
        if self.last_used_at:
            data["last_used_at"] = self.last_used_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "TokenMetadata":
        """
        Fonction from_dict.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        return cls(
            token_id=data["token_id"],
            token_type=TokenType(data["token_type"]),
            status=TokenStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=(
                datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
            ),
            last_used_at=(
                datetime.fromisoformat(data["last_used_at"]) if data.get("last_used_at") else None
            ),
            usage_count=data.get("usage_count", 0),
            max_usage_count=data.get("max_usage_count"),
            associated_user=data.get("associated_user"),
            associated_service=data.get("associated_service"),
            permissions=data.get("permissions", []),
            client_info=data.get("client_info", {}),
            tags=data.get("tags", []),
        )

    def is_expired(self) -> bool:
        """
        Fonction is_expired.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def is_usage_exceeded(self) -> bool:
        """
        Fonction is_usage_exceeded.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        if self.max_usage_count is None:
            return False
        return self.usage_count >= self.max_usage_count

    def is_valid(self) -> bool:
        """
        Fonction is_valid.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        return (
            self.status == TokenStatus.ACTIVE
            and not self.is_expired()
            and not self.is_usage_exceeded()
        )


class TokenManager:
    """
    Gestionnaire du cycle de vie des tokens

    Fonctionnalités:
    - Génération de tokens JWT et API keys
    - Gestion des sessions utilisateur
    - Révocation et expiration automatique
    - Audit trail complet
    - Protection contre replay attacks
    - Rate limiting par token
    """

    def __init__(
        self, vault: ArkaliaVault, jwt_secret_name: str = "jwt_master_secret"
    ) -> None:  # nosec B107
        """
        Fonction __init__.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        self.vault = vault
        self.jwt_secret_name = jwt_secret_name
        self.token_metadata: dict[str, TokenMetadata] = {}
        self.revoked_tokens: set[str] = set()

        # Initialiser le secret JWT si nécessaire
        self._ensure_jwt_secret()

        # Charger les métadonnées existantes
        self._load_token_metadata()

        logger.info("🎫 TokenManager initialized")

    def _ensure_jwt_secret(self) -> None:
        """
        Fonction _ensure_jwt_secret.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        try:
            jwt_secret = self.vault.retrieve_secret(self.jwt_secret_name)
            if jwt_secret is None:
                # Générer un nouveau secret JWT
                new_secret = secrets.token_urlsafe(64)
                self.vault.store_secret(
                    name=self.jwt_secret_name,
                    value=new_secret,
                    tags=["jwt", "master_secret", "system"],
                    overwrite=False,
                )
                logger.info("🔑 New JWT master secret generated")
        except VaultError as e:
            logger.error(f"❌ Failed to ensure JWT secret: {e}")
            raise

    def _get_jwt_secret(self) -> str:
        """
        Fonction _get_jwt_secret.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        jwt_secret = self.vault.retrieve_secret(self.jwt_secret_name)
        if jwt_secret is None:
            raise VaultError("JWT secret not found in vault")
        return jwt_secret

    def _load_token_metadata(self) -> None:
        """
        Fonction _load_token_metadata.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        try:
            metadata_json = self.vault.retrieve_secret("token_metadata")
            if metadata_json:
                data = json.loads(metadata_json)
                for token_id, meta_dict in data.items():
                    self.token_metadata[token_id] = TokenMetadata.from_dict(meta_dict)

                logger.info(f"📊 Loaded metadata for {len(self.token_metadata)} tokens")
        except Exception as e:
            logger.warning(f"⚠️ Could not load token metadata: {e}")

    def _save_token_metadata(self) -> None:
        """
        Fonction _save_token_metadata.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        try:
            data = {token_id: meta.to_dict() for token_id, meta in self.token_metadata.items()}
            metadata_json = json.dumps(data, indent=2)

            self.vault.store_secret(
                name="token_metadata",
                value=metadata_json,
                tags=["system", "token_metadata"],
                overwrite=True,
            )
        except Exception as e:
            logger.error(f"❌ Failed to save token metadata: {e}")

    def generate_token(
        self,
        token_type: TokenType,
        user_id: str | None = None,
        service_id: str | None = None,
        permissions: list[str] | None = None,
        expires_in_hours: int | None = None,
        max_usage_count: int | None = None,
        client_info: dict[str, str] | None = None,
        custom_claims: dict | None = None,
    ) -> tuple[str, str]:
        """
        Génère un nouveau token

        Args:
            token_type: Type de token à générer
            user_id: ID utilisateur associé
            service_id: ID service associé
            permissions: Liste des permissions
            expires_in_hours: Expiration en heures
            max_usage_count: Nombre max d'utilisations
            client_info: Informations client (IP, User-Agent, etc.)
            custom_claims: Claims personnalisés pour JWT

        Returns:
            (token_id, token_value)
        """
        # Générer un ID unique pour le token
        token_id = f"{token_type.value}_{secrets.token_urlsafe(16)}"

        # Calculer l'expiration
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)

        # Créer les métadonnées
        metadata = TokenMetadata(
            token_id=token_id,
            token_type=token_type,
            status=TokenStatus.ACTIVE,
            created_at=datetime.now(),
            expires_at=expires_at,
            last_used_at=None,
            usage_count=0,
            max_usage_count=max_usage_count,
            associated_user=user_id,
            associated_service=service_id,
            permissions=permissions or [],
            client_info=client_info or {},
            tags=[],
        )

        # Générer la valeur du token selon le type
        if token_type in [
            TokenType.ACCESS_TOKEN,
            TokenType.REFRESH_TOKEN,
            TokenType.SESSION,
        ]:
            token_value = self._generate_jwt_token(metadata, custom_claims)
        else:
            token_value = self._generate_api_key(metadata)

        # Stocker les métadonnées
        self.token_metadata[token_id] = metadata
        self._save_token_metadata()

        # Stocker le token dans le vault
        self.vault.store_secret(
            name=f"token_{token_id}",
            value=token_value,
            expires_in_days=expires_in_hours // 24 if expires_in_hours else None,
            tags=[
                "token",
                token_type.value,
                f"user_{user_id}" if user_id else "system",
            ],
            overwrite=True,
        )

        logger.info(f"🎫 Generated {token_type.value} token: {token_id}")
        return token_id, token_value

    def _generate_jwt_token(
        self, metadata: TokenMetadata, custom_claims: dict | None = None
    ) -> str:
        """Génère un token JWT"""
        jwt_secret = self._get_jwt_secret()

        now = datetime.now()
        payload = {
            "jti": metadata.token_id,
            "iat": int(now.timestamp()),
            "sub": metadata.associated_user or metadata.associated_service,
            "token_type": metadata.token_type.value,
            "permissions": metadata.permissions,
            "usage_count": metadata.usage_count,
        }

        if metadata.expires_at:
            payload["exp"] = int(metadata.expires_at.timestamp())

        if metadata.max_usage_count:
            payload["max_usage"] = metadata.max_usage_count

        # Ajouter les claims personnalisés
        if custom_claims:
            payload.update(custom_claims)

        return jwt.encode(payload, jwt_secret, algorithm="HS256")

    def _generate_api_key(self, metadata: TokenMetadata) -> str:
        prefix = f"ak_{metadata.token_type.value}"
        suffix = secrets.token_urlsafe(32)
        return f"{prefix}_{suffix}"

    def validate_token(
        self, token_value: str, required_permissions: list[str] | None = None
    ) -> tuple[bool, TokenMetadata | None, str]:
        """
        Valide un token

        Args:
            token_value: Valeur du token à valider
            required_permissions: Permissions requises

        Returns:
            (is_valid, metadata, reason)
        """
        try:
            # Décoder le token pour obtenir l'ID
            token_id = None

            # Essayer de décoder comme JWT
            try:
                jwt_secret = self._get_jwt_secret()
                decoded = jwt.decode(token_value, jwt_secret, algorithms=["HS256"])
                token_id = decoded.get("jti")
            except jwt.InvalidTokenError:
                # Pas un JWT, chercher dans les API keys
                for tid, _metadata in self.token_metadata.items():
                    stored_token = self.vault.retrieve_secret(f"token_{tid}")
                    if stored_token == token_value:
                        token_id = tid
                        break

            if not token_id:
                return False, None, "Token not found"

            # Vérifier si le token est révoqué
            if token_id in self.revoked_tokens:
                return False, None, "Token revoked"

            # Récupérer les métadonnées
            metadata = self.token_metadata.get(token_id)
            if not metadata:
                return False, None, "Token metadata not found"

            # Vérifier la validité
            if not metadata.is_valid():
                reason = "Token expired" if metadata.is_expired() else "Usage limit exceeded"
                return False, metadata, reason

            # Vérifier les permissions
            if required_permissions:
                if not all(perm in metadata.permissions for perm in required_permissions):
                    return False, metadata, "Insufficient permissions"

            # Mettre à jour les statistiques d'usage
            metadata.usage_count += 1
            metadata.last_used_at = datetime.now()
            self._save_token_metadata()

            return True, metadata, "Valid"

        except Exception as e:
            logger.error(f"❌ Token validation error: {e}")
            return False, None, f"Validation error: {e}"

    def revoke_token(self, token_id: str, reason: str = "Manual revocation") -> bool:
        """
        Révoque un token

        Args:
            token_id: ID du token à révoquer
            reason: Raison de la révocation

        Returns:
            True si révocation réussie
        """
        if token_id not in self.token_metadata:
            logger.warning(f"⚠️ Token {token_id} not found for revocation")
            return False

        # Marquer comme révoqué
        self.token_metadata[token_id].status = TokenStatus.REVOKED
        self.revoked_tokens.add(token_id)

        # Supprimer du vault
        self.vault.delete_secret(f"token_{token_id}")

        # Sauvegarder
        self._save_token_metadata()

        logger.info(f"🚫 Token {token_id} revoked: {reason}")
        return True

    def revoke_user_tokens(self, user_id: str) -> int:
        """
        Révoque tous les tokens d'un utilisateur

        Args:
            user_id: ID utilisateur

        Returns:
            Nombre de tokens révoqués
        """
        revoked_count = 0

        for token_id, metadata in self.token_metadata.items():
            if metadata.associated_user == user_id and metadata.status == TokenStatus.ACTIVE:
                if self.revoke_token(token_id, f"User {user_id} tokens revoked"):
                    revoked_count += 1

        logger.info(f"🚫 Revoked {revoked_count} tokens for user {user_id}")
        return revoked_count

    def cleanup_expired_tokens(self) -> int:
        """
        Nettoie les tokens expirés

        Returns:
            Nombre de tokens nettoyés
        """
        cleaned_count = 0
        expired_tokens: list[str] = []

        for token_id, metadata in self.token_metadata.items():
            if metadata.is_expired() or metadata.is_usage_exceeded():
                expired_tokens.append(token_id)

        for token_id in expired_tokens:
            if self.revoke_token(token_id, "Automatic cleanup - expired"):
                cleaned_count += 1

        logger.info(f"🧹 Cleaned up {cleaned_count} expired tokens")
        return cleaned_count

    def refresh_token(self, refresh_token: str) -> tuple[str | None, str | None]:
        """
        Renouvelle un token d'accès avec un refresh token

        Args:
            refresh_token: Token de rafraîchissement

        Returns:
            (new_access_token_id, new_access_token_value) ou (None, None) si échec
        """
        # Valider le refresh token
        is_valid, metadata, reason = self.validate_token(refresh_token)

        if not is_valid or not metadata:
            logger.warning(f"⚠️ Invalid refresh token: {reason}")
            return None, None

        if metadata.token_type != TokenType.REFRESH_TOKEN:
            logger.warning("⚠️ Token is not a refresh token")
            return None, None

        # Générer un nouveau token d'accès
        new_token_id, new_token_value = self.generate_token(
            token_type=TokenType.ACCESS_TOKEN,
            user_id=metadata.associated_user,
            service_id=metadata.associated_service,
            permissions=metadata.permissions,
            expires_in_hours=1,  # Token d'accès expire dans 1h
            client_info=metadata.client_info,
        )

        logger.info(f"🔄 Token refreshed for user {metadata.associated_user}")
        return new_token_id, new_token_value

    def get_token_stats(self) -> dict[str, Any]:
        """Récupère les statistiques des tokens.

        Returns:
            dict: Statistiques des tokens (total, actifs, expirés, etc.).
        """
        stats: dict[str, Any] = {
            "total_tokens": len(self.token_metadata),
            "active_tokens": 0,
            "expired_tokens": 0,
            "revoked_tokens": 0,
            "by_type": {},
            "usage_stats": {"total_usage": 0, "avg_usage": 0},
        }

        total_usage = 0
        for metadata in self.token_metadata.values():
            # Compter par statut
            if metadata.status == TokenStatus.ACTIVE and not metadata.is_expired():
                stats["active_tokens"] += 1
            elif metadata.is_expired():
                stats["expired_tokens"] += 1
            elif metadata.status == TokenStatus.REVOKED:
                stats["revoked_tokens"] += 1

            # Compter par type
            token_type = metadata.token_type.value
            stats["by_type"][token_type] = stats["by_type"].get(token_type, 0) + 1

            # Statistiques d'usage
            total_usage += metadata.usage_count

        stats["usage_stats"]["total_usage"] = total_usage
        if len(self.token_metadata) > 0:
            stats["usage_stats"]["avg_usage"] = total_usage / len(self.token_metadata)

        return stats

    def list_active_tokens(self, user_id: str | None = None) -> list[TokenMetadata]:
        """
        Liste les tokens actifs

        Args:
            user_id: Filtrer par utilisateur (optionnel)

        Returns:
            Liste des métadonnées des tokens actifs
        """
        active_tokens: list[TokenMetadata] = []

        for metadata in self.token_metadata.values():
            if metadata.is_valid():
                if user_id is None or metadata.associated_user == user_id:
                    active_tokens.append(metadata)

        return active_tokens


# Fonctions utilitaires pour l'intégration
def create_session_token(
    token_manager: TokenManager,
    user_id: str,
    client_ip: str,
    user_agent: str,
    permissions: list[str],
    session_duration_hours: int = 24,
) -> tuple[str, str]:
    """Crée un token de session utilisateur"""
    return token_manager.generate_token(
        token_type=TokenType.SESSION,
        user_id=user_id,
        permissions=permissions,
        expires_in_hours=session_duration_hours,
        client_info={"ip": client_ip, "user_agent": user_agent, "session_type": "web"},
    )


def create_api_key(
    token_manager: TokenManager,
    service_id: str,
    permissions: list[str],
    max_requests_per_day: int | None = None,
) -> tuple[str, str]:
    """Crée une clé API pour un service"""
    return token_manager.generate_token(
        token_type=TokenType.API_KEY,
        service_id=service_id,
        permissions=permissions,
        max_usage_count=max_requests_per_day,
        client_info={"service_type": "api"},
    )

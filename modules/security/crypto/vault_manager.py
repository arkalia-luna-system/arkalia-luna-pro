"""
Module vault_manager.

Ce module fait partie du système Arkalia Luna Pro.
"""

# 🔐 modules/security/crypto/vault_manager.py
# Arkalia-Vault Enterprise - Gestionnaire de secrets sécurisé

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from cryptography.fernet import Fernet

from .checksum_validator import BuildIntegrityValidator, SecurityError
from core.ark_logger import ark_logger


class VaultError(SecurityError):
    """Exception levée lors d'une erreur dans la gestion du vault de secrets."""

    pass


class SecretMetadata:
    """Métadonnées associées à un secret stocké dans le vault."""

    def __init__(
        self,
        name: str,
        created_at: datetime,
        expires_at: datetime | None = None,
        tags: list[str] | None = None,
    ):
        self.name = name
        self.created_at = created_at
        self.expires_at = expires_at
        self.tags = tags or []
        self.access_count = 0
        self.last_accessed: datetime | None = None

    def to_dict(self) -> dict:
        """
        Fonction to_dict.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "tags": self.tags,
            "access_count": self.access_count,
            "last_accessed": (self.last_accessed.isoformat() if self.last_accessed else None),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SecretMetadata":
        """
        Fonction from_dict.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        metadata = cls(
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=(datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None),
            tags=data.get("tags", []),
        )
        metadata.access_count = data.get("access_count", 0)
        if data.get("last_accessed"):
            metadata.last_accessed = datetime.fromisoformat(data["last_accessed"])
        return metadata


class ArkaliaVault(BuildIntegrityValidator):
    """
    Arkalia-Vault Enterprise - Extension sécurisée du validateur existant

    Fonctionnalités:
    - Stockage sécurisé des secrets (chiffrement Fernet)
    - Rotation automatique des clés
    - Gestion du cycle de vie des secrets
    - Audit trail complet
    - Intégration avec l'intégrité existante
    """

    def __init__(self, base_dir: Path | None = None, master_key: bytes | None = None) -> None:
        """
        Fonction __init__.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        # Initialiser la classe parente
        super().__init__(base_dir)

        # Configuration Vault
        self.vault_dir = self.base_dir / "security" / "vault"
        self.secrets_file = self.vault_dir / "secrets.encrypted"
        self.metadata_file = self.vault_dir / "metadata.json"
        self.audit_log = self.vault_dir / "audit.log"
        self.key_file = self.vault_dir / ".vault_key"

        # Créer les répertoires nécessaires
        self.vault_dir.mkdir(parents=True, exist_ok=True)

        # Initialiser la cryptographie
        self.cipher_suite = self._initialize_encryption(master_key)

        # Charger les métadonnées existantes
        self.secrets_metadata: dict[str, SecretMetadata] = self._load_metadata()

        ark_logger.info(
            "🔐 ArkaliaVault initialized successfully", extra={"arkalia_module": "security"}
        )

    def _initialize_encryption(self, master_key: bytes | None = None) -> Fernet:
        if master_key:
            # Utiliser la clé fournie
            key = master_key
        elif self.key_file.exists():
            # Charger la clé existante
            key = self.key_file.read_bytes()
        else:
            # Générer une nouvelle clé
            key = Fernet.generate_key()
            # Sauvegarder la clé de manière sécurisée
            self.key_file.write_bytes(key)
            os.chmod(self.key_file, 0o600)  # Lecture seule pour le propriétaire
            ark_logger.info(
                "🔑 New vault master key generated", extra={"arkalia_module": "security"}
            )

        return Fernet(key)

    def _load_metadata(self) -> dict[str, SecretMetadata]:
        if not self.metadata_file.exists():
            return {}

        try:
            with open(self.metadata_file) as f:
                data = json.load(f)

            metadata: dict[str, Any] = {}
            for name, meta_dict in data.items():
                metadata[name] = SecretMetadata.from_dict(meta_dict)

            return metadata
        except Exception as e:
            ark_logger.error(
                f"❌ Error loading metadata: {e}", extra={"arkalia_module": "security"}
            )
            return {}

    def _save_metadata(self) -> None:
        data = {name: meta.to_dict() for name, meta in self.secrets_metadata.items()}

        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_secrets(self) -> dict[str, str]:
        if not self.secrets_file.exists():
            return {}

        try:
            encrypted_data = self.secrets_file.read_bytes()
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            secrets_dict: dict[str, str] = json.loads(decrypted_data.decode())
            return secrets_dict
        except Exception as e:
            ark_logger.error(f"❌ Error loading secrets: {e}", extra={"arkalia_module": "security"})
            raise VaultError(f"Failed to decrypt vault: {e}") from e

    def _save_secrets(self, secrets: dict[str, str]) -> None:
        try:
            json_data = json.dumps(secrets, indent=2).encode()
            encrypted_data = self.cipher_suite.encrypt(json_data)
            self.secrets_file.write_bytes(encrypted_data)
            os.chmod(self.secrets_file, 0o600)
        except Exception as e:
            ark_logger.error(f"❌ Error saving secrets: {e}", extra={"arkalia_module": "security"})
            raise VaultError(f"Failed to encrypt vault: {e}") from e

    def _audit_log_entry(self, action: str, secret_name: str, details: str = "") -> None:
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | {action} | {secret_name} | {details}\n"

        with open(self.audit_log, "a") as f:
            f.write(log_entry)

    def store_secret(
        self,
        name: str,
        value: str,
        expires_in_days: int | None = None,
        tags: list[str] | None = None,
        overwrite: bool = False,
    ) -> bool:
        """
        Stocke un secret dans le vault

        Args:
            name: Nom du secret
            value: Valeur du secret
            expires_in_days: Expiration en jours (optionnel)
            tags: Tags pour classification
            overwrite: Autoriser l'écrasement

        Returns:
            True si stockage réussi

        Raises:
            VaultError: Si erreur de stockage
        """
        if not overwrite and name in self.secrets_metadata:
            raise VaultError(f"Secret '{name}' already exists. Use overwrite=True to replace.")

        # Charger les secrets existants
        secrets = self._load_secrets()

        # Ajouter le nouveau secret
        secrets[name] = value

        # Créer les métadonnées
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)

        self.secrets_metadata[name] = SecretMetadata(
            name=name, created_at=datetime.now(), expires_at=expires_at, tags=tags or []
        )

        # Sauvegarder
        self._save_secrets(secrets)
        self._save_metadata()

        # Audit log
        self._audit_log_entry("STORE", name, f"tags={tags}, expires={expires_at}")

        ark_logger.info(
            f"🔐 Secret '{name}' stored successfully", extra={"arkalia_module": "security"}
        )
        return True

    def retrieve_secret(self, name: str) -> str | None:
        """
        Récupère un secret du vault

        Args:
            name: Nom du secret

        Returns:
            Valeur du secret ou None si introuvable

        Raises:
            VaultError: Si secret expiré
        """
        if name not in self.secrets_metadata:
            ark_logger.warning(f"⚠️ Secret '{name}' not found", extra={"arkalia_module": "security"})
            return None

        metadata = self.secrets_metadata[name]

        # Vérifier l'expiration
        if metadata.expires_at and datetime.now() > metadata.expires_at:
            ark_logger.warning(
                f"⚠️ Secret '{name}' has expired", extra={"arkalia_module": "security"}
            )
            self._audit_log_entry("ACCESS_DENIED", name, "EXPIRED")
            raise VaultError(f"Secret '{name}' has expired")

        # Charger et récupérer le secret
        secrets = self._load_secrets()
        value = secrets.get(name)

        if value is None:
            ark_logger.error(
                f"❌ Secret '{name}' found in metadata but missing from vault",
                extra={"arkalia_module": "security"},
            )
            return None

        # Mettre à jour les statistiques d'accès
        metadata.access_count += 1
        metadata.last_accessed = datetime.now()
        self._save_metadata()

        # Audit log
        self._audit_log_entry("RETRIEVE", name, f"access_count={metadata.access_count}")

        return value

    def delete_secret(self, name: str) -> bool:
        """
        Supprime un secret du vault

        Args:
            name: Nom du secret

        Returns:
            True si suppression réussie
        """
        if name not in self.secrets_metadata:
            ark_logger.warning(
                f"⚠️ Secret '{name}' not found for deletion", extra={"arkalia_module": "security"}
            )
            return False

        # Charger et supprimer le secret
        secrets = self._load_secrets()
        if name in secrets:
            del secrets[name]
            self._save_secrets(secrets)

        # Supprimer les métadonnées
        del self.secrets_metadata[name]
        self._save_metadata()

        # Audit log
        self._audit_log_entry("DELETE", name)

        ark_logger.info(
            f"🗑️ Secret '{name}' deleted successfully", extra={"arkalia_module": "security"}
        )
        return True

    def list_secrets(self, include_expired: bool = False) -> list[SecretMetadata]:
        """
        Liste tous les secrets avec leurs métadonnées

        Args:
            include_expired: Inclure les secrets expirés

        Returns:
            Liste des métadonnées des secrets
        """
        secrets: list[Any] = []
        now = datetime.now()

        for metadata in self.secrets_metadata.values():
            if include_expired or not metadata.expires_at or now <= metadata.expires_at:
                secrets.append(metadata)

        return secrets

    def cleanup_expired_secrets(self) -> int:
        """
        Supprime tous les secrets expirés

        Returns:
            Nombre de secrets supprimés
        """
        now = datetime.now()
        expired_secrets: list[Any] = []

        for name, metadata in self.secrets_metadata.items():
            if metadata.expires_at and now > metadata.expires_at:
                expired_secrets.append(name)

        for name in expired_secrets:
            self.delete_secret(name)

        ark_logger.info(
            f"🧹 Cleaned up {len(expired_secret, extra={"arkalia_module": "security"})} expired secrets",
            extra={"arkalia_module": "security"},
        )
        return len(expired_secrets)

    def rotate_master_key(self, new_key: bytes | None = None) -> bytes:
        """
        Effectue la rotation de la clé maître

        Args:
            new_key: Nouvelle clé (générée si None)

        Returns:
            Nouvelle clé générée

        Raises:
            VaultError: Si erreur de rotation
        """
        ark_logger.info("🔄 Starting master key rotation...", extra={"arkalia_module": "security"})

        # Charger tous les secrets avec l'ancienne clé
        secrets = self._load_secrets()

        # Générer ou utiliser la nouvelle clé
        if new_key is None:
            new_key = Fernet.generate_key()

        # Créer un nouveau cipher avec la nouvelle clé
        new_cipher = Fernet(new_key)

        # Sauvegarder l'ancienne clé pour rollback
        backup_key_file = self.vault_dir / f".vault_key.backup.{int(datetime.now().timestamp())}"
        if self.key_file.exists():
            backup_key_file.write_bytes(self.key_file.read_bytes())

        try:
            # Mettre à jour le cipher
            self.cipher_suite = new_cipher

            # Sauvegarder la nouvelle clé
            self.key_file.write_bytes(new_key)
            os.chmod(self.key_file, 0o600)

            # Re-chiffrer tous les secrets avec la nouvelle clé
            self._save_secrets(secrets)

            # Audit log
            self._audit_log_entry("KEY_ROTATION", "SYSTEM", f"secrets_count={len(secrets)}")

            ark_logger.info(
                "✅ Master key rotation completed successfully",
                extra={"arkalia_module": "security"},
            )
            return new_key

        except Exception as e:
            # Rollback en cas d'erreur
            if backup_key_file.exists():
                self.key_file.write_bytes(backup_key_file.read_bytes())
                self.cipher_suite = self._initialize_encryption()

            ark_logger.error(f"❌ Key rotation failed: {e}", extra={"arkalia_module": "security"})
            raise VaultError(f"Key rotation failed: {e}") from e

    def validate_vault_integrity(self) -> bool:
        """
        Valide l'intégrité complète du vault

        Combine la validation des checksums (classe parente)
        avec la validation spécifique du vault

        Returns:
            True si intégrité OK

        Raises:
            VaultError: Si violation d'intégrité
        """
        ark_logger.info("🔍 Validating vault integrity...", extra={"arkalia_module": "security"})

        # 1. Validation des checksums génériques (classe parente)
        try:
            super().validate_integrity()
        except SecurityError as e:
            raise VaultError(f"Base integrity validation failed: {e}") from e

        # 2. Validation spécifique du vault
        violations: list[Any] = []

        # Vérifier que les fichiers vault existent
        required_files = [self.key_file, self.metadata_file, self.audit_log]
        for file_path in required_files:
            if not file_path.exists():
                violations.append(f"Missing vault file: {file_path}")

        # Vérifier que le vault peut être déchiffré
        try:
            secrets = self._load_secrets()
            metadata_count = len(self.secrets_metadata)
            secrets_count = len(secrets)

            if metadata_count != secrets_count:
                violations.append(
                    f"Metadata/secrets count mismatch: {metadata_count} vs {secrets_count}"
                )

        except Exception as e:
            violations.append(f"Vault decryption failed: {e}")

        # Vérifier les permissions des fichiers sensibles
        sensitive_files = [self.key_file, self.secrets_file]
        for file_path in sensitive_files:
            if file_path.exists():
                file_stat = file_path.stat()
                # Vérifier que seul le propriétaire peut lire (mode 600)
                if file_stat.st_mode & 0o077 != 0:
                    violations.append(f"Insecure permissions on {file_path}")

        if violations:
            violation_msg = "; ".join(violations)
            self._audit_log_entry("INTEGRITY_VIOLATION", "SYSTEM", violation_msg)
            raise VaultError(f"Vault integrity violations: {violation_msg}")

        ark_logger.info(
            "✅ Vault integrity validation PASSED", extra={"arkalia_module": "security"}
        )
        return True

    def get_vault_stats(self) -> dict:
        """
        Récupère les statistiques du vault.

        Returns:
            dict: Dictionnaire contenant les statistiques du vault :
                - total_secrets: Nombre total de secrets
                - active_secrets: Nombre de secrets actifs (non expirés)
                - expired_secrets: Nombre de secrets expirés
                - vault_size_bytes: Taille du fichier vault en octets
                - last_key_rotation: Date de la dernière rotation de clé
                - audit_log_size: Nombre d'entrées dans le log d'audit
        """
        secrets = self.list_secrets(include_expired=True)
        expired_count = len([s for s in secrets if s.expires_at and datetime.now() > s.expires_at])

        return {
            "total_secrets": len(secrets),
            "active_secrets": len(secrets) - expired_count,
            "expired_secrets": expired_count,
            "vault_size_bytes": (
                self.secrets_file.stat().st_size if self.secrets_file.exists() else 0
            ),
            "last_key_rotation": (
                self.key_file.stat().st_mtime if self.key_file.exists() else None
            ),
            "audit_log_size": (self.audit_log.stat().st_size if self.audit_log.exists() else 0),
        }

    def security_health_check(self) -> dict:
        """
        Vérification de santé sécurisée pour l'orchestrateur enhanced

        Returns:
            Dict avec score de sécurité et statistiques
        """
        try:
            # Validation de l'intégrité du vault
            integrity_ok = self.validate_vault_integrity()

            # Statistiques du vault
            stats = self.get_vault_stats()

            # Calcul du score de sécurité (0.0 à 1.0)
            score = 1.0
            if not integrity_ok:
                score -= 0.5
            if stats["expired_secrets"] > 0:
                score -= 0.2
            if stats["total_secrets"] == 0:
                score -= 0.1

            # Nettoyer les secrets expirés automatiquement
            cleaned = self.cleanup_expired_secrets()

            return {
                "score": max(score, 0.0),
                "secrets_count": stats["total_secrets"],
                "active_secrets": stats["active_secrets"],
                "expired_cleaned": cleaned,
                "integrity_status": "ok" if integrity_ok else "corrupted",
                "vault_size_mb": round(stats["vault_size_bytes"] / 1024 / 1024, 2),
                "audit_entries": stats.get("audit_log_size", 0),
                "last_check": datetime.now().isoformat(),
            }

        except Exception as e:
            ark_logger.error(
                f"❌ Security health check failed: {e}", extra={"arkalia_module": "security"}
            )
            return {
                "score": 0.0,
                "error": str(e),
                "secrets_count": 0,
                "last_check": datetime.now().isoformat(),
            }


# Fonctions utilitaires pour migration douce depuis .env
def migrate_from_env_file(
    env_file_path: str | Path, vault: ArkaliaVault, backup_env: bool = True
) -> int:
    """
    Migre les secrets depuis un fichier .env vers le vault

    Args:
        env_file_path: Chemin vers le fichier .env
        vault: Instance ArkaliaVault
        backup_env: Créer une sauvegarde du .env

    Returns:
        Nombre de secrets migrés
    """
    env_path = Path(env_file_path)

    if not env_path.exists():
        ark_logger.warning(
            f"⚠️ .env file not found: {env_path}", extra={"arkalia_module": "security"}
        )
        return 0

    # Backup du fichier .env si demandé
    if backup_env:
        backup_path = env_path.parent / f"{env_path.name}.backup.{int(datetime.now().timestamp())}"
        backup_path.write_text(env_path.read_text())
        ark_logger.info(
            f"📦 .env backed up to: {backup_path}", extra={"arkalia_module": "security"}
        )

    # Parser le fichier .env
    secrets_migrated = 0

    with open(env_path) as f:
        for _line_num, line in enumerate(f, 1):
            line = line.strip()

            # Ignorer les commentaires et lignes vides
            if not line or line.startswith("#"):
                continue

            # Parser KEY=VALUE
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("\"'")  # Enlever les quotes

                try:
                    vault.store_secret(
                        name=f"env_{key}",
                        value=value,
                        tags=["migrated_from_env"],
                        overwrite=True,
                    )
                    secrets_migrated += 1
                    ark_logger.info(f"✅ Migrated: {key}", extra={"arkalia_module": "security"})

                except Exception as e:
                    ark_logger.error(
                        f"❌ Failed to migrate {key}: {e}", extra={"arkalia_module": "security"}
                    )

    ark_logger.info(
        f"🚀 Migration completed: {secrets_migrated} secrets migrated from {env_path}",
        extra={"arkalia_module": "security"},
    )
    return secrets_migrated


def create_arkalia_vault(base_dir: Path | None = None) -> ArkaliaVault:
    """
    Crée une nouvelle instance d'ArkaliaVault.

    Args:
        base_dir: Répertoire de base pour le vault. Si None, utilise le répertoire courant.

    Returns:
        ArkaliaVault: Instance du vault créé.
    """
    return ArkaliaVault(base_dir)

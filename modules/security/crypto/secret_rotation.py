"""
Module secret_rotation.

Ce module fait partie du système Arkalia Luna Pro.
"""

# 🔄 modules/security/crypto/secret_rotation.py
# Système de rotation automatique des secrets Arkalia-Vault

import secrets
import string
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from .vault_manager import ArkaliaVault
from core.ark_logger import ark_logger


class RotationStrategy(Enum):
    MANUAL = "manual"
    TIME_BASED = "time_based"
    ACCESS_COUNT = "access_count"
    CONDITIONAL = "conditional"


@dataclass
class RotationPolicy:
    """Politique de rotation pour un secret.

    Attributes:
        name: Nom de la politique.
        strategy: Stratégie de rotation à utiliser.
        interval_days: Intervalle en jours pour TIME_BASED.
        max_access_count: Nombre maximum d'accès pour ACCESS_COUNT.
        condition_callback: Fonction de condition pour CONDITIONAL.
        auto_generate: Génération automatique du nouveau secret.
        generation_pattern: Pattern de génération.
        custom_generator: Générateur personnalisé.
        notification_callback: Callback de notification.
    """

    name: str
    strategy: RotationStrategy
    interval_days: int | None = None
    max_access_count: int | None = None
    condition_callback: Callable | None = None
    auto_generate: bool = True
    generation_pattern: str = "secure_random"  # secure_random, alphanumeric, custom
    custom_generator: Callable | None = None
    notification_callback: Callable | None = None


class SecretGenerator:
    """Générateur de secrets sécurisés pour la rotation."""

    @staticmethod
    def generate_secure_random(length: int = 32) -> str:
        """Génère un secret aléatoire sécurisé.

        Args:
            length: Longueur du secret (défaut: 32).

        Returns:
            str: Secret généré.
        """
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def generate_alphanumeric(length: int = 24) -> str:
        """Génère un secret alphanumérique.

        Args:
            length: Longueur du secret (défaut: 24).

        Returns:
            str: Secret alphanumérique généré.
        """
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def generate_api_key(prefix: str = "ak", length: int = 40) -> str:
        """Génère une clé API avec préfixe.

        Args:
            prefix: Préfixe de la clé (défaut: "ak").
            length: Longueur totale de la clé (défaut: 40).

        Returns:
            str: Clé API générée.
        """
        suffix = SecretGenerator.generate_alphanumeric(length - len(prefix) - 1)
        return f"{prefix}_{suffix}"

    @staticmethod
    def generate_jwt_secret(length: int = 64) -> str:
        """Génère un secret JWT sécurisé.

        Args:
            length: Longueur du secret (défaut: 64).

        Returns:
            str: Secret JWT généré.
        """
        return secrets.token_urlsafe(length)


class RotationManager:
    """
    Gestionnaire de rotation automatique des secrets

    Fonctionnalités:
    - Rotation basée sur le temps, l'usage ou des conditions
    - Génération automatique de nouveaux secrets
    - Notifications de rotation
    - Rollback en cas de problème
    - Audit trail complet
    """

    def __init__(self, vault: ArkaliaVault) -> None:
        """
        Fonction __init__.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        self.vault = vault
        self.policies: dict[str, RotationPolicy] = {}
        self.rotation_history: list[dict] = []

    def add_policy(self, policy: RotationPolicy) -> None:
        """Ajoute une politique de rotation.

        Args:
            policy: Politique de rotation à ajouter.
        """
        self.policies[policy.name] = policy
        ark_logger.info(
            f"📋 Rotation policy added for: {policy.name}", extra={"arkalia_module": "security"}
        )

    def remove_policy(self, secret_name: str) -> None:
        """Supprime une politique de rotation.

        Args:
            secret_name: Nom du secret dont la politique doit être supprimée.
        """
        if secret_name in self.policies:
            del self.policies[secret_name]
            ark_logger.info(
                f"🗑️ Rotation policy removed for: {secret_name}",
                extra={"arkalia_module": "security"},
            )

    def check_rotation_needed(self, secret_name: str) -> tuple[bool, str]:
        """
        Vérifie si un secret nécessite une rotation

        Returns:
            (needs_rotation, reason)
        """
        if secret_name not in self.policies:
            return False, "No rotation policy"

        policy = self.policies[secret_name]

        # Vérifier que le secret existe
        secrets_list = self.vault.list_secrets(include_expired=True)
        secret_metadata = None
        for meta in secrets_list:
            if meta.name == secret_name:
                secret_metadata = meta
                break

        if not secret_metadata:
            return False, "Secret not found"

        now = datetime.now()

        # Stratégie TIME_BASED
        if policy.strategy == RotationStrategy.TIME_BASED and policy.interval_days:
            age_days = (now - secret_metadata.created_at).days
            if age_days >= policy.interval_days:
                return True, f"Time-based rotation needed (age: {age_days} days)"

        # Stratégie ACCESS_COUNT
        if policy.strategy == RotationStrategy.ACCESS_COUNT and policy.max_access_count:
            if secret_metadata.access_count >= policy.max_access_count:
                return (
                    True,
                    f"Access count rotation needed (count: {secret_metadata.access_count})",
                )

        # Stratégie CONDITIONAL
        if policy.strategy == RotationStrategy.CONDITIONAL and policy.condition_callback:
            try:
                if policy.condition_callback(secret_metadata):
                    return True, "Conditional rotation triggered"
            except Exception as e:
                ark_logger.error(
                    f"❌ Error in rotation condition callback: {e}",
                    extra={"arkalia_module": "security"},
                )

        return False, "No rotation needed"

    def rotate_secret(self, secret_name: str, new_value: str | None = None) -> bool:
        """
        Effectue la rotation d'un secret

        Args:
            secret_name: Nom du secret à faire tourner
            new_value: Nouvelle valeur (générée automatiquement si None)

        Returns:
            True si rotation réussie
        """
        if secret_name not in self.policies:
            ark_logger.error(
                f"❌ No rotation policy for secret: {secret_name}",
                extra={"arkalia_module": "security"},
            )
            return False

        policy = self.policies[secret_name]

        try:
            # Récupérer l'ancienne valeur pour backup
            old_value = self.vault.retrieve_secret(secret_name)
            if old_value is None:
                ark_logger.error(
                    f"❌ Cannot rotate non-existent secret: {secret_name}",
                    extra={"arkalia_module": "security"},
                )
                return False

            # Générer ou utiliser la nouvelle valeur
            if new_value is None and policy.auto_generate:
                new_value = self._generate_new_value(policy)

            if new_value is None:
                ark_logger.error(
                    f"❌ No new value provided and auto-generation disabled for: {secret_name}",
                    extra={"arkalia_module": "security"},
                )
                return False

            # Créer un backup du secret avec timestamp
            backup_name = f"{secret_name}_backup_{int(datetime.now().timestamp())}"
            self.vault.store_secret(
                name=backup_name,
                value=old_value,
                expires_in_days=30,  # Backup expire dans 30 jours
                tags=["rotation_backup", f"original_{secret_name}"],
                overwrite=True,
            )

            # Stocker la nouvelle valeur
            # Récupérer les métadonnées actuelles pour préserver les tags
            current_metadata = None
            for meta in self.vault.list_secrets(include_expired=True):
                if meta.name == secret_name:
                    current_metadata = meta
                    break

            existing_tags = current_metadata.tags if current_metadata else []
            rotation_tags = existing_tags + [
                "rotated",
                f"rotated_at_{datetime.now().strftime('%Y%m%d')}",
            ]

            self.vault.store_secret(
                name=secret_name, value=new_value, tags=rotation_tags, overwrite=True
            )

            # Enregistrer l'historique de rotation
            rotation_record = {
                "secret_name": secret_name,
                "rotated_at": datetime.now().isoformat(),
                "strategy": policy.strategy.value,
                "backup_name": backup_name,
                "reason": self.check_rotation_needed(secret_name)[1],
            }
            self.rotation_history.append(rotation_record)

            # Notification si configurée
            if policy.notification_callback:
                try:
                    policy.notification_callback(secret_name, rotation_record)
                except Exception as e:
                    ark_logger.error(
                        f"⚠️ Notification callback failed: {e}", extra={"arkalia_module": "security"}
                    )

            ark_logger.info(
                f"🔄 Secret '{secret_name}' rotated successfully",
                extra={"arkalia_module": "security"},
            )
            return True

        except Exception as e:
            ark_logger.error(
                f"❌ Failed to rotate secret '{secret_name}': {e}",
                extra={"arkalia_module": "security"},
            )
            return False

    def _generate_new_value(self, policy: RotationPolicy) -> str:
        if policy.custom_generator:
            result = policy.custom_generator()
            if not isinstance(result, str):
                raise ValueError("Custom generator must return a string")
            return result

        if policy.generation_pattern == "secure_random":
            return SecretGenerator.generate_secure_random()
        elif policy.generation_pattern == "alphanumeric":
            return SecretGenerator.generate_alphanumeric()
        elif policy.generation_pattern == "api_key":
            return SecretGenerator.generate_api_key()
        elif policy.generation_pattern == "jwt_secret":
            return SecretGenerator.generate_jwt_secret()
        else:
            # Fallback sécurisé
            return SecretGenerator.generate_secure_random()

    def bulk_rotation_check(self) -> dict[str, tuple[bool, str]]:
        """
        Vérifie tous les secrets avec des politiques de rotation

        Returns:
            Dict {secret_name: (needs_rotation, reason)}
        """
        results: dict[str, Any] = {}
        for secret_name in self.policies.keys():
            results[secret_name] = self.check_rotation_needed(secret_name)
        return results

    def auto_rotate_due_secrets(self) -> dict[str, bool]:
        """
        Effectue la rotation automatique de tous les secrets éligibles

        Returns:
            Dict {secret_name: rotation_success}
        """
        rotation_check = self.bulk_rotation_check()
        results: dict[str, Any] = {}
        for secret_name, (needs_rotation, reason) in rotation_check.items():
            if needs_rotation:
                ark_logger.info(
                    f"🔄 Auto-rotating {secret_name}: {reason}",
                    extra={"arkalia_module": "security"},
                )
                results[secret_name] = self.rotate_secret(secret_name)
            else:
                ark_logger.debug(
                    f"⏭️ Skipping {secret_name}: {reason}", extra={"arkalia_module": "security"}
                )
        return results

    def rollback_rotation(self, secret_name: str) -> bool:
        """
        Effectue le rollback d'une rotation récente

        Args:
            secret_name: Nom du secret à restaurer

        Returns:
            True si rollback réussi
        """
        # Trouver le backup le plus récent
        recent_backup = None
        recent_timestamp = 0

        for backup_meta in self.vault.list_secrets(include_expired=True):
            if (
                backup_meta.name.startswith(f"{secret_name}_backup_")
                and "rotation_backup" in backup_meta.tags
            ):
                # Extraire le timestamp du nom
                try:
                    timestamp_str = backup_meta.name.split("_backup_")[1]
                    timestamp = int(timestamp_str)

                    if timestamp > recent_timestamp:
                        recent_timestamp = timestamp
                        recent_backup = backup_meta
                except ValueError:
                    continue

        if not recent_backup:
            ark_logger.error(
                f"❌ No backup found for secret: {secret_name}",
                extra={"arkalia_module": "security"},
            )
            return False

        try:
            # Récupérer la valeur de backup
            backup_value = self.vault.retrieve_secret(recent_backup.name)
            if backup_value is None:
                ark_logger.error(
                    f"❌ Could not retrieve backup value for: {secret_name}",
                    extra={"arkalia_module": "security"},
                )
                return False

            # Restaurer la valeur originale
            self.vault.store_secret(
                name=secret_name,
                value=backup_value,
                tags=["rollback_restored", f"restored_from_{recent_backup.name}"],
                overwrite=True,
            )

            # Enregistrer le rollback dans l'historique
            rollback_record = {
                "secret_name": secret_name,
                "rolled_back_at": datetime.now().isoformat(),
                "backup_used": recent_backup.name,
                "action": "rollback",
            }
            self.rotation_history.append(rollback_record)

            ark_logger.info(
                f"↩️ Secret '{secret_name}' rolled back successfully",
                extra={"arkalia_module": "security"},
            )
            return True

        except Exception as e:
            ark_logger.error(
                f"❌ Failed to rollback secret '{secret_name}': {e}",
                extra={"arkalia_module": "security"},
            )
            return False

    def cleanup_old_backups(self, max_age_days: int = 90) -> int:
        """
        Nettoie les anciens backups de rotation

        Args:
            max_age_days: Age maximum des backups en jours

        Returns:
            Nombre de backups supprimés
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0

        for backup_meta in self.vault.list_secrets(include_expired=True):
            if "rotation_backup" in backup_meta.tags and backup_meta.created_at < cutoff_date:
                if self.vault.delete_secret(backup_meta.name):
                    deleted_count += 1

        ark_logger.info(
            f"🧹 Cleaned up {deleted_count} old rotation backups",
            extra={"arkalia_module": "security"},
        )
        return deleted_count

    def get_rotation_stats(self) -> dict:
        """
        Récupère les statistiques de rotation.

        Returns:
            dict: Dictionnaire contenant :
                - total_policies: Nombre total de politiques
                - total_rotations: Nombre total de rotations effectuées
                - recent_rotations_7d: Rotations des 7 derniers jours
                - strategy_distribution: Distribution par stratégie
                - last_rotation: Dernière rotation effectuée
        """
        total_policies = len(self.policies)
        total_rotations = len(self.rotation_history)

        # Statistiques par stratégie
        strategy_stats: dict[str, Any] = {}
        for policy in self.policies.values():
            strategy = policy.strategy.value
            strategy_stats[strategy] = strategy_stats.get(strategy, 0) + 1

        # Rotations récentes (7 derniers jours)
        recent_rotations: list[Any] = []
        cutoff_date = datetime.now() - timedelta(days=7)

        for record in self.rotation_history:
            if datetime.fromisoformat(record["rotated_at"]) > cutoff_date:
                recent_rotations.append(record)

        return {
            "total_policies": total_policies,
            "total_rotations": total_rotations,
            "recent_rotations_7d": len(recent_rotations),
            "strategy_distribution": strategy_stats,
            "last_rotation": (self.rotation_history[-1] if self.rotation_history else None),
        }


# Fonctions de politiques prédéfinies
def create_daily_rotation_policy(secret_name: str) -> RotationPolicy:
    """
    Crée une politique de rotation quotidienne.

    Args:
        secret_name: Nom du secret pour lequel créer la politique.

    Returns:
        RotationPolicy: Politique configurée pour rotation quotidienne.
    """
    return RotationPolicy(
        name=secret_name,
        strategy=RotationStrategy.TIME_BASED,
        interval_days=1,
        auto_generate=True,
        generation_pattern="secure_random",
    )


def create_weekly_rotation_policy(secret_name: str) -> RotationPolicy:
    """
    Crée une politique de rotation hebdomadaire.

    Args:
        secret_name: Nom du secret pour lequel créer la politique.

    Returns:
        RotationPolicy: Politique configurée pour rotation hebdomadaire.
    """
    return RotationPolicy(
        name=secret_name,
        strategy=RotationStrategy.TIME_BASED,
        interval_days=7,
        auto_generate=True,
        generation_pattern="secure_random",
    )


def create_monthly_rotation_policy(secret_name: str) -> RotationPolicy:
    """
    Crée une politique de rotation mensuelle.

    Args:
        secret_name: Nom du secret pour lequel créer la politique.

    Returns:
        RotationPolicy: Politique configurée pour rotation mensuelle.
    """
    """Crée une politique de rotation mensuelle.

    Args:
        secret_name: Nom du secret.

    Returns:
        RotationPolicy: Politique de rotation mensuelle.
    """
    return RotationPolicy(
        name=secret_name,
        strategy=RotationStrategy.TIME_BASED,
        interval_days=30,
        auto_generate=True,
        generation_pattern="secure_random",
    )


def create_access_based_policy(secret_name: str, max_accesses: int = 100) -> RotationPolicy:
    """Crée une politique de rotation basée sur le nombre d'accès.

    Args:
        secret_name: Nom du secret pour lequel créer la politique.
        max_accesses: Nombre maximum d'accès avant rotation (défaut: 100).

    Returns:
        RotationPolicy: Politique configurée pour rotation basée sur l'accès.
    """
    return RotationPolicy(
        name=secret_name,
        strategy=RotationStrategy.ACCESS_COUNT,
        max_access_count=max_accesses,
        auto_generate=True,
        generation_pattern="secure_random",
    )

#!/usr/bin/env python3
"""
🔧 ConfigManager - Gestion intelligente de la configuration
🎯 Principe SOLID SRP : Responsabilité unique - Configuration
🛡️ Préservation des mécanismes de sécurité
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.ark_logger import ark_logger


@dataclass
class CoreConfig:
    """Configuration de base du Core"""

    debug_mode: bool = False
    log_level: str = "INFO"
    max_retries: int = 3
    timeout: float = 30.0
    enable_watchdogs: bool = True
    enable_metrics: bool = True
    enable_alerts: bool = True


class ConfigManager:
    """
    🎯 Gestionnaire de configuration centralisé
    🛡️ Préservation des mécanismes de sécurité
    """

    def __init__(self, config_path: str | None = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config: dict[str, Any] = {}
        self._core_config = CoreConfig()
        self._initialized = False

        # Initialisation automatique
        self.initialize()

    def _get_default_config_path(self) -> str:
        """Chemin par défaut de la configuration"""
        return str(Path(__file__).parent.parent.parent.parent / "config" / "core_config.json")

    def initialize(self) -> bool:
        """
        🚀 Initialisation de la configuration
        ✅ Chargement intelligent avec fallbacks
        """
        try:
            ark_logger.info("🔧 Initialisation ConfigManager...", extra={"arkalia_module": "core"})

            # Chargement de la configuration
            self._load_config()

            # Validation de la configuration
            self._validate_config()

            # Application des paramètres
            self._apply_config()

            self._initialized = True
            ark_logger.info(
                "✅ ConfigManager initialisé avec succès", extra={"arkalia_module": "core"}
            )
            return True

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur initialisation ConfigManager : {e}", extra={"arkalia_module": "core"}
            )
            # Fallback vers configuration par défaut
            self._load_default_config()
            return False

    def _load_config(self) -> None:
        """Chargement de la configuration depuis le fichier (synchrone)"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, encoding="utf-8") as f:
                    self._config = json.load(f)
                ark_logger.info(
                    f"📄 Configuration chargée depuis {self.config_path}",
                    extra={"arkalia_module": "core"},
                )
            else:
                ark_logger.warning(
                    f"⚠️ Fichier de config non trouvé : {self.config_path}",
                    extra={"arkalia_module": "core"},
                )
                self._load_default_config()
        except Exception as e:
            ark_logger.error(f"❌ Erreur chargement config : {e}", extra={"arkalia_module": "core"})
            self._load_default_config()

    async def _load_config_async(self) -> None:
        """Chargement asynchrone de la configuration (optimisé pour performance)"""
        try:
            import aiofiles

            if os.path.exists(self.config_path):
                async with aiofiles.open(self.config_path, encoding="utf-8") as f:
                    content = await f.read()
                    self._config = json.loads(content)
                ark_logger.info(
                    f"📄 Configuration chargée async depuis {self.config_path}",
                    extra={"arkalia_module": "core"},
                )
            else:
                ark_logger.warning(
                    f"⚠️ Fichier de config non trouvé : {self.config_path}",
                    extra={"arkalia_module": "core"},
                )
                self._load_default_config()
        except ImportError:
            # Fallback vers méthode synchrone si aiofiles non disponible
            self._load_config()
        except Exception as e:
            ark_logger.error(
                f"❌ Erreur chargement config async : {e}",
                extra={"arkalia_module": "core"},
            )
            self._load_default_config()

    def _load_default_config(self) -> None:
        """Chargement de la configuration par défaut"""
        self._config = {
            "core": asdict(self._core_config),
            "modules": {
                "zeroia": {"enabled": True, "max_decisions": 1000},
                "sandozia": {"enabled": True, "analysis_depth": "medium"},
                "reflexia": {"enabled": True, "panic_threshold": 0.8},
                "assistantia": {"enabled": True, "max_conversations": 100},
                "helloria": {"enabled": True, "port": 8000},
                "monitoring": {"enabled": True, "metrics_interval": 30},
                "security": {"enabled": True, "encryption_level": "high"},
            },
            "watchdogs": {
                "reflexia_panic": {"enabled": True, "threshold": 0.9},
                "zeroia_circuit": {"enabled": True, "failure_threshold": 5},
                "sandozia_anomaly": {"enabled": True, "sensitivity": 0.7},
            },
        }
        ark_logger.info("📄 Configuration par défaut chargée", extra={"arkalia_module": "core"})

    def _validate_config(self) -> None:
        """Validation de la configuration"""
        required_sections = ["core", "modules", "watchdogs"]
        for section in required_sections:
            if section not in self._config:
                ark_logger.warning(
                    f"⚠️ Section manquante : {section}", extra={"arkalia_module": "core"}
                )
                self._config[section] = {}

    def _apply_config(self) -> None:
        """Application de la configuration"""
        # Configuration du logging via ark_logger
        # Note: ark_logger gère son propre niveau de logging
        # Pas besoin de configurer logging standard
        if "core" in self._config:
            core_config = self._config["core"]
            if "log_level" in core_config:
                # ark_logger gère son propre niveau, pas besoin de logging standard
                pass

    def get_config(self, section: str | None = None) -> dict[str, Any]:
        """
        📄 Récupération de la configuration
        :param section: Section spécifique (None = tout)
        :return: Configuration
        """
        if not self._initialized:
            self.initialize()

        if section is None:
            result = self._config.copy()
            return result if isinstance(result, dict) else {}

        result = self._config.get(section, {}).copy()
        return result if isinstance(result, dict) else {}

    def get_watchdog_config(self, watchdog_name: str) -> dict[str, Any]:
        """
        🛡️ Configuration d'un watchdog spécifique
        :param watchdog_name: Nom du watchdog
        :return: Configuration du watchdog
        """
        watchdogs_config = self.get_config("watchdogs")
        result = watchdogs_config.get(watchdog_name, {})
        return result if isinstance(result, dict) else {}

    def set_config(self, section: str, key: str, value: Any) -> bool:
        """
        ✏️ Modification de la configuration
        :param section: Section de configuration
        :param key: Clé à modifier
        :param value: Nouvelle valeur
        :return: True si modification réussie
        """
        try:
            if section not in self._config:
                self._config[section] = {}

            self._config[section][key] = value
            ark_logger.info(
                f"✏️ Configuration mise à jour : {section}.{key} = {value}",
                extra={"arkalia_module": "core"},
            )
            return True

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur modification config : {e}", extra={"arkalia_module": "core"}
            )
            return False

    def save_config(self) -> bool:
        """
        💾 Sauvegarde de la configuration (synchrone)
        :return: True si sauvegarde réussie
        """
        try:
            # Création du répertoire si nécessaire
            config_dir = Path(self.config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)

            ark_logger.info(
                f"💾 Configuration sauvegardée : {self.config_path}",
                extra={"arkalia_module": "core"},
            )
            return True

        except Exception as e:
            ark_logger.error(f"❌ Erreur sauvegarde config : {e}", extra={"arkalia_module": "core"})
            return False

    async def save_config_async(self) -> bool:
        """
        💾 Sauvegarde asynchrone de la configuration (optimisé pour performance)
        :return: True si sauvegarde réussie
        """
        try:
            import aiofiles

            # Création du répertoire si nécessaire
            config_dir = Path(self.config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)

            content = json.dumps(self._config, indent=2, ensure_ascii=False)
            async with aiofiles.open(self.config_path, "w", encoding="utf-8") as f:
                await f.write(content)

            ark_logger.info(
                f"💾 Configuration sauvegardée async : {self.config_path}",
                extra={"arkalia_module": "core"},
            )
            return True

        except ImportError:
            # Fallback vers méthode synchrone si aiofiles non disponible
            return self.save_config()
        except Exception as e:
            ark_logger.error(
                f"❌ Erreur sauvegarde config async : {e}",
                extra={"arkalia_module": "core"},
            )
            return False

    def reload_config(self) -> bool:
        """
        🔄 Rechargement de la configuration
        :return: True si rechargement réussi
        """
        ark_logger.info("🔄 Rechargement de la configuration...", extra={"arkalia_module": "core"})
        return self.initialize()

    def health_check(self) -> dict[str, Any]:
        """
        🏥 Vérification de santé du ConfigManager
        :return: Statut de santé
        """
        return {
            "module": "config_manager",
            "status": "healthy" if self._initialized else "uninitialized",
            "config_path": self.config_path,
            "sections": list(self._config.keys()),
            "modules_configured": len(self.get_config("modules")),
            "watchdogs_configured": len(self.get_config("watchdogs")),
        }

    def get_environment_config(self) -> dict[str, Any]:
        """
        🌍 Configuration depuis les variables d'environnement
        :return: Configuration environnement
        """
        env_config: dict[str, Any] = {}
        env_mappings = {
            "ARKALIA_DEBUG": "core.debug_mode",
            "ARKALIA_LOG_LEVEL": "core.log_level",
            "ARKALIA_MAX_RETRIES": "core.max_retries",
            "ARKALIA_TIMEOUT": "core.timeout",
        }

        for env_var, config_path in env_mappings.items():
            if env_var in os.environ:
                value_str = os.environ[env_var]
                # Conversion des types
                if config_path.endswith("debug_mode"):
                    value: Any = value_str.lower() in ("true", "1", "yes")
                elif config_path.endswith(("max_retries", "timeout")):
                    value = float(value_str) if "." in value_str else int(value_str)
                else:
                    value = value_str

                env_config[config_path] = value

        return env_config

    def load_toml_config(self, file_path: str | Path) -> dict[str, Any]:
        """
        📄 Charge une configuration TOML avec cache

        Args:
            file_path: Chemin vers le fichier TOML

        Returns:
            Configuration chargée
        """
        from modules.utils.helpers import load_toml_cached

        file_path_str = str(file_path)
        try:
            return load_toml_cached(file_path_str)
        except Exception as e:
            ark_logger.warning(
                f"⚠️ Erreur chargement TOML {file_path_str}: {e}", extra={"arkalia_module": "core"}
            )
            return {}

    def get_module_config(self, module_name: str) -> dict[str, Any]:
        """
        🔧 Récupère la configuration d'un module spécifique

        Args:
            module_name: Nom du module (reflexia, sandozia, etc.)

        Returns:
            Configuration du module
        """
        modules_config = self.get_config("modules")
        result = modules_config.get(module_name, {})
        return result if isinstance(result, dict) else {}


# Instance par défaut (lazy loading pour économiser la RAM)
_default_config_manager: ConfigManager | None = None


def get_default_config_manager() -> ConfigManager:
    """Récupère l'instance par défaut du ConfigManager (lazy loading)"""
    global _default_config_manager
    if _default_config_manager is None:
        _default_config_manager = ConfigManager()
    return _default_config_manager


# Alias pour compatibilité (lazy)
class _LazyConfigManager:
    """Wrapper lazy pour default_config_manager"""

    def __getattr__(self, name: str) -> Any:
        return getattr(get_default_config_manager(), name)


default_config_manager = _LazyConfigManager()

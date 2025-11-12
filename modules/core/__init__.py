#!/usr/bin/env python3
"""
🧠 Core SOLID - Cœur intelligent du système Arkalia Luna Pro
🎯 Objectif : Orchestration sans perte de redondance
🛡️ Principe : Centralisation intelligente avec watchdogs préservés
📅 Version : 1.0.0
👤 Author : Athalia
"""

from typing import Any, Optional

from core.ark_logger import ark_logger

# Import des composants principaux
try:
    from .config import ConfigManager
    from .factories import ModuleFactory, ServiceFactory
    from .health import HealthMonitor
    from .interfaces import IHealthCheck, IModule, IOrchestrator
    from .orchestrator import CoreOrchestrator
except ImportError as e:
    ark_logger.warning(
        f"⚠️ Composants core non encore implémentés : {e}", extra={"arkalia_module": "core"}
    )
    CoreOrchestrator = None
    HealthMonitor = None
    ConfigManager = None
    IModule = None
    IOrchestrator = None
    IHealthCheck = None
    ModuleFactory = None
    ServiceFactory = None


class CoreManager:
    """
    🎯 Gestionnaire principal du Core SOLID
    🛡️ Préservation des mécanismes de sécurité
    """

    def __init__(self):
        self.orchestrator = None
        self.health_monitor = None
        self.config_manager = None
        self._initialized = False

    def initialize(self) -> bool:
        """
        🚀 Initialisation intelligente du Core
        ✅ Validation des dépendances
        🛡️ Préservation des watchdogs
        """
        try:
            ark_logger.info("🧠 Initialisation Core SOLID...", extra={"arkalia_module": "core"})
            if ConfigManager is not None:
                self.config_manager = ConfigManager()
            if HealthMonitor is not None:
                self.health_monitor = HealthMonitor()
            if CoreOrchestrator is not None:
                try:
                    self.orchestrator = CoreOrchestrator()
                except TypeError:
                    self.orchestrator = CoreOrchestrator(None)
            # Validation de l'initialisation
            self._validate_initialization()
            self._initialized = True
            ark_logger.info(
                "✅ Core SOLID initialisé avec succès", extra={"arkalia_module": "core"}
            )
            return True
        except Exception as e:
            ark_logger.error(
                f"❌ Erreur initialisation Core : {e}", extra={"arkalia_module": "core"}
            )
            return False

    def _validate_initialization(self) -> None:
        """Validation de l'initialisation"""
        if ConfigManager is not None and not self.config_manager:
            raise ValueError("ConfigManager non initialisé")
        if HealthMonitor is not None and not self.health_monitor:
            raise ValueError("HealthMonitor non initialisé")
        if CoreOrchestrator is not None and not self.orchestrator:
            raise ValueError("CoreOrchestrator non initialisé")

    def get_orchestrator(self):
        """Récupération de l'orchestrateur"""
        if not self._initialized:
            ark_logger.warning(
                "⚠️ Core non initialisé, initialisation automatique...",
                extra={"arkalia_module": "core"},
            )
            if not self.initialize():
                return None
        return self.orchestrator

    def get_health_monitor(self):
        """Récupération du moniteur de santé"""
        if not self._initialized:
            if not self.initialize():
                return None
        return self.health_monitor

    def health_check(self) -> dict[str, Any]:
        """Vérification de santé du Core"""
        return {
            "module": "core",
            "status": "healthy" if self._initialized else "uninitialized",
            "version": "1.0.0",
            "components": {
                "orchestrator": self.orchestrator is not None,
                "health_monitor": self.health_monitor is not None,
                "config_manager": self.config_manager is not None,
            },
        }


# Instance globale du Core Manager
_core_manager = CoreManager()


def create_core():
    """
    🏭 Factory pour créer le core avec configuration optimale
    🛡️ Préservation des mécanismes de sécurité
    """
    if not _core_manager._initialized:
        if not _core_manager.initialize():
            raise RuntimeError("Impossible d'initialiser le Core SOLID")

    return _core_manager.get_orchestrator()


def get_core_manager() -> CoreManager:
    """Récupération du gestionnaire Core"""
    return _core_manager


def health_check() -> dict[str, Any]:
    """Vérification de santé publique"""
    return _core_manager.health_check()


# Interface publique simplifiée
def launch_core() -> bool:
    """
    🚀 Lancement du Core SOLID
    🎯 Point d'entrée principal pour l'orchestration
    """
    try:
        orchestrator = create_core()
        if orchestrator:
            ark_logger.info("🚀 Core SOLID lancé avec succès", extra={"arkalia_module": "core"})
            return True
        else:
            ark_logger.error(
                "❌ Impossible de créer l'orchestrateur", extra={"arkalia_module": "core"}
            )
            return False
    except Exception as e:
        ark_logger.error(f"❌ Erreur lancement Core : {e}", extra={"arkalia_module": "core"})
        return False


# Instance par défaut (pour compatibilité)
try:
    default_core = create_core()
except Exception:
    default_core = None
    ark_logger.warning(
        "⚠️ Core par défaut non disponible (composants en cours de développement)",
        extra={"arkalia_module": "core"},
    )


# Interface de compatibilité avec l'ancien arkalia_master
def get_core_status() -> dict[str, Any]:
    """Interface de compatibilité pour l'ancien arkalia_master"""
    return {
        "status": "core_solid_v1.0.0",
        "health": health_check(),
        "ready": _core_manager._initialized,
    }


if __name__ == "__main__":
    # Test du module Core
    print("🧠 Test Core SOLID...")
    status = health_check()
    print(f"📊 Statut : {status}")

    if launch_core():
        print("✅ Core SOLID opérationnel")
    else:
        print("❌ Erreur Core SOLID")

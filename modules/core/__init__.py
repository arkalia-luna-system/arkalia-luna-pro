#!/usr/bin/env python3
"""
🧠 Core SOLID - Cœur intelligent du système Arkalia Luna Pro
🎯 Objectif : Orchestration sans perte de redondance
🛡️ Principe : Centralisation intelligente avec watchdogs préservés
📅 Version : 1.0.0
👤 Author : Athalia
"""

from typing import TYPE_CHECKING, Any

from core.ark_logger import ark_logger

# Import des composants principaux
if TYPE_CHECKING:
    from .config import ConfigManager as _ConfigManager  # noqa: F401
    from .factories import ModuleFactory as _ModuleFactory  # noqa: F401
    from .factories import ServiceFactory as _ServiceFactory  # noqa: F401
    from .health import HealthMonitor as _HealthMonitor  # noqa: F401
    from .interfaces import (
        IHealthCheck as _IHealthCheck,  # noqa: F401
    )
    from .interfaces import (
        IModule as _IModule,  # noqa: F401
    )
    from .interfaces import (
        IOrchestrator as _IOrchestrator,  # noqa: F401
    )
    from .orchestrator import CoreOrchestrator as _CoreOrchestrator  # noqa: F401

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
    # Utiliser Any pour éviter les erreurs de type
    CoreOrchestrator = None  # type: ignore[assignment, misc]
    HealthMonitor = None  # type: ignore[assignment, misc]
    ConfigManager = None  # type: ignore[assignment, misc]
    IModule = None  # type: ignore[assignment, misc]
    IOrchestrator = None  # type: ignore[assignment, misc]
    IHealthCheck = None  # type: ignore[assignment, misc]
    ModuleFactory = None  # type: ignore[assignment, misc]
    ServiceFactory = None  # type: ignore[assignment, misc]


class CoreManager:
    """
    🎯 Gestionnaire principal du Core SOLID
    🛡️ Préservation des mécanismes de sécurité
    """

    def __init__(self) -> None:
        self.orchestrator: Any = None
        self.health_monitor: Any = None
        self.config_manager: Any = None
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

    def get_orchestrator(self) -> Any:
        """Récupération de l'orchestrateur"""
        if not self._initialized:
            ark_logger.warning(
                "⚠️ Core non initialisé, initialisation automatique...",
                extra={"arkalia_module": "core"},
            )
            if not self.initialize():
                return None
        return self.orchestrator

    def get_health_monitor(self) -> Any:
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


# Instance globale du Core Manager (lazy loading pour économiser la RAM)
_core_manager: CoreManager | None = None


def _get_core_manager() -> CoreManager:
    """Récupère l'instance du Core Manager (lazy loading)"""
    global _core_manager
    if _core_manager is None:
        _core_manager = CoreManager()
    return _core_manager


def create_core() -> Any:
    """
    🏭 Factory pour créer le core avec configuration optimale
    🛡️ Préservation des mécanismes de sécurité
    """
    core_mgr = _get_core_manager()
    if not core_mgr._initialized:
        if not core_mgr.initialize():
            raise RuntimeError("Impossible d'initialiser le Core SOLID")

    return core_mgr.get_orchestrator()


def get_core_manager() -> CoreManager:
    """Récupération du gestionnaire Core"""
    return _get_core_manager()


def health_check() -> dict[str, Any]:
    """Vérification de santé publique"""
    return _get_core_manager().health_check()


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


# Instance par défaut (lazy loading pour économiser la RAM)
_default_core: Any | None = None


def get_default_core() -> Any | None:
    """Récupère l'instance par défaut du core (lazy loading)"""
    global _default_core
    if _default_core is None:
        try:
            _default_core = create_core()
        except Exception:
            ark_logger.warning(
                "⚠️ Core par défaut non disponible (composants en cours de développement)",
                extra={"arkalia_module": "core"},
            )
            _default_core = False  # Marqueur pour éviter de réessayer
    return _default_core if _default_core is not False else None


# Alias pour compatibilité (lazy)
class _LazyCore:
    """Wrapper lazy pour default_core"""

    def __getattr__(self, name: str) -> Any:
        core = get_default_core()
        if core is None:
            raise AttributeError(f"default_core n'est pas disponible: {name}")
        return getattr(core, name)


default_core = _LazyCore()


# Interface de compatibilité avec l'ancien arkalia_master
def get_core_status() -> dict[str, Any]:
    """Interface de compatibilité pour l'ancien arkalia_master"""
    core_mgr = _get_core_manager()
    return {
        "status": "core_solid_v1.0.0",
        "health": health_check(),
        "ready": core_mgr._initialized,
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

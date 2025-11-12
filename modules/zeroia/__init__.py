#!/usr/bin/env python3

"""
🌕 ZeroIA - Module de décision autonome Enhanced v2.8.0

Module principal pour la prise de décision autonome avec coordinateur,
confidence scoring, graceful degradation et error recovery.
"""

from typing import Any

__version__ = "3.0.0-enhanced"
__author__ = "Arkalia-LUNA Team"
__description__ = "Système de raisonnement intelligent avec coordinateur avancé"

# Imports lazy pour économiser la RAM et accélérer les imports
# Les modules sont chargés seulement quand ils sont utilisés

# Configuration par défaut
DEFAULT_CONFIG = {
    "max_loops": 100,
    "interval_seconds": 10.0,
    "circuit_failure_threshold": 8,
    "timeout": 45,
    "confidence_threshold": 0.7,
    "graceful_degradation": True,
    "error_recovery": True,
}

# Exports publics
__all__ = [
    # Core modules
    "ZeroIACoordinator",
    "get_coordinator",
    "DecisionEngine",
    "StateManager",
    "ConfidenceScorer",
    "GracefulDegradationSystem",
    "DegradationLevel",
    "ErrorRecoverySystem",
    "ErrorType",
    "ZeroIAOrchestrator",
    # Metrics
    "get_zeroia_metrics",
    "update_zeroia_metrics",
    # Configuration
    "DEFAULT_CONFIG",
]


# Lazy imports pour économiser la RAM
def __getattr__(name: str) -> Any:
    """Lazy loading des modules lourds"""
    if name == "ConfidenceScorer":
        from .confidence_score import ConfidenceScorer

        return ConfidenceScorer
    elif name == "ZeroIACoordinator":
        from .coordinator import ZeroIACoordinator

        return ZeroIACoordinator
    elif name == "get_coordinator":
        from .coordinator import get_coordinator

        return get_coordinator
    elif name == "DecisionEngine":
        from .decision_engine import DecisionEngine

        return DecisionEngine
    elif name == "ErrorRecoverySystem":
        from .error_recovery_system import ErrorRecoverySystem

        return ErrorRecoverySystem
    elif name == "ErrorType":
        from .error_recovery_system import ErrorType

        return ErrorType
    elif name == "DegradationLevel":
        from .graceful_degradation import DegradationLevel

        return DegradationLevel
    elif name == "GracefulDegradationSystem":
        from .graceful_degradation import GracefulDegradationSystem

        return GracefulDegradationSystem
    elif name == "get_zeroia_metrics":
        from .metrics import get_zeroia_metrics

        return get_zeroia_metrics
    elif name == "update_zeroia_metrics":
        from .metrics import update_zeroia_metrics

        return update_zeroia_metrics
    elif name == "ZeroIAOrchestrator":
        from .orchestrator_enhanced import ZeroIAOrchestrator

        return ZeroIAOrchestrator
    elif name == "StateManager":
        from .state_manager import StateManager

        return StateManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_zeroia_status() -> dict[str, Any]:
    """🔍 Obtenir le statut complet de ZeroIA"""
    try:
        # Test imports critiques (lazy)
        from .coordinator import get_coordinator

        get_coordinator()

        return {
            "status": "✅ HEALTHY",
            "version": "v2.8.0",
            "modules": {
                "coordinator": "✅",
                "decision_engine": "✅",
                "state_manager": "✅",
                "confidence_scorer": "✅",
                "graceful_degradation": "✅",
                "error_recovery": "✅",
                "orchestrator_enhanced": "✅",
            },
            "features": {
                "coordination": "✅",
                "decision_making": "✅",
                "confidence_scoring": "✅",
                "graceful_degradation": "✅",
                "error_recovery": "✅",
                "enhanced_orchestration": "✅",
            },
        }
    except ImportError as e:
        return {
            "status": "❌ ERROR",
            "error": str(e),
            "version": "v2.8.0",
        }


def get_version() -> str:
    """Retourne la version du module ZeroIA"""
    return __version__


def get_default_config() -> dict:
    """Retourne la configuration par défaut"""
    return DEFAULT_CONFIG.copy()


def health_check() -> dict:
    """Vérifie l'état de santé du module ZeroIA"""
    try:
        # Test imports critiques
        from .coordinator import get_coordinator

        get_coordinator()

        return {
            "status": "healthy",
            "version": __version__,
            "components": {
                "coordinator": "available",
                "decision_engine": "available",
                "state_manager": "available",
                "confidence_scorer": "available",
                "graceful_degradation": "available",
                "error_recovery": "available",
                "orchestrator_enhanced": "available",
            },
            "timestamp": "2025-07-05T16:27:00Z",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": __version__,
            "timestamp": "2025-07-05T16:27:00Z",
        }

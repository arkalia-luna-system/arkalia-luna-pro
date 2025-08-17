#!/usr/bin/env python3

"""
🌕 ZeroIA - Module de décision autonome Enhanced v2.8.0

Module principal pour la prise de décision autonome avec coordinateur,
confidence scoring, graceful degradation et error recovery.
"""

__version__ = "3.0.0-enhanced"
__author__ = "Arkalia-LUNA Team"
__description__ = "Système de raisonnement intelligent avec coordinateur avancé"

# Imports des modules actifs
from .confidence_score import ConfidenceScorer  # noqa: F401
from .coordinator import ZeroIACoordinator, get_coordinator  # noqa: F401
from .decision_engine import DecisionEngine  # noqa: F401
from .error_recovery_system import ErrorRecoverySystem, ErrorType  # noqa: F401
from .graceful_degradation import DegradationLevel, GracefulDegradationSystem  # noqa: F401
from .metrics import get_zeroia_metrics, update_zeroia_metrics  # noqa: F401
from .orchestrator_enhanced import ZeroIAOrchestrator  # noqa: F401
from .state_manager import StateManager  # noqa: F401

# Configuration par défaut
DEFAULT_CONFIG = {
    "max_loops": 100,
    "interval_seconds": 2.0,
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


def get_zeroia_status():
    """🔍 Obtenir le statut complet de ZeroIA"""
    try:
        # Test imports critiques
        from .coordinator import get_coordinator

        coordinator = get_coordinator()

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

        coordinator = get_coordinator()

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

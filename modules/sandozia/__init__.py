# 🧠 modules/sandozia/__init__.py
# Sandozia Intelligence Croisée - Phase 2 v3.x

"""
Sandozia Intelligence Croisée

Système d'intelligence collaborative pour Arkalia-LUNA v3.x
- Corrélation signaux IA/logs/historique
- Détection incohérences et dérives
- Recommandations IA croisées
- Raisonnement multi-agent
"""

from typing import Any

__version__ = "3.0.0-phase2"
__author__ = "Arkalia-LUNA System"

__all__ = [
    "SandoziaCore",
    "CrossModuleValidator",
    "BehaviorAnalyzer",
    "CollaborativeReasoning",
    "SandoziaMetrics",
]


# Lazy imports pour économiser la RAM et accélérer les imports
def __getattr__(name: str) -> Any:
    """Lazy loading des modules lourds"""
    if name == "SandoziaCore":
        from .core.sandozia_core import SandoziaCore

        return SandoziaCore
    elif name == "CrossModuleValidator":
        from .validators import CrossModuleValidator

        return CrossModuleValidator
    elif name == "BehaviorAnalyzer":
        from .analyzer.behavior import BehaviorAnalyzer

        return BehaviorAnalyzer
    elif name == "CollaborativeReasoning":
        from .reasoning.collaborative import CollaborativeReasoning

        return CollaborativeReasoning
    elif name == "SandoziaMetrics":
        from .utils.metrics import SandoziaMetrics

        return SandoziaMetrics
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

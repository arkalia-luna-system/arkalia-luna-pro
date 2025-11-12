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

from .analyzer.behavior import BehaviorAnalyzer
from .core.sandozia_core import SandoziaCore
from .reasoning.collaborative import CollaborativeReasoning
from .utils.metrics import SandoziaMetrics
from .validators import CrossModuleValidator

__version__ = "3.0.0-phase2"
__author__ = "Arkalia-LUNA System"

__all__ = [
    "SandoziaCore",
    "CrossModuleValidator",
    "BehaviorAnalyzer",
    "CollaborativeReasoning",
    "SandoziaMetrics",
]

"""
Module validators de Sandozia.

Ce module contient les validateurs pour la validation croisée entre modules.
CrossModuleValidator a été migré vers modules.utils.validators.crossmodule_validator
"""

# 🧠 modules/sandozia/validators/__init__.py
# Validators pour Sandozia Intelligence Croisée

# CrossModuleValidator migré vers utils/validators (Phase 4)
from modules.utils.validators.crossmodule_validator import CrossModuleValidator

__all__ = ["CrossModuleValidator"]

#!/usr/bin/env python3
"""
🌕 ZeroIA - Compatibilité ZeroIA Core
------------------------------------

Ce module fournit une fine couche de compatibilité autour de l'implémentation
ZeroIA Enhanced existante, afin de :
- satisfaire les anciens scripts qui importent ``modules.zeroia.core`` ;
- fournir une classe ``ZeroIACore`` simple, avec une méthode ``get_status`` ;
- permettre l'exécution via ``python -m modules.zeroia.core`` (Docker ZeroIA) ;
- réexporter les primitives publiques du package ``modules.zeroia`` pour
  les anciens chemins d'import.
"""

from __future__ import annotations

from typing import Any, Dict

from . import (
    ConfidenceScorer,
    DecisionEngine,
    DegradationLevel,
    ErrorRecoverySystem,
    ErrorType,
    GracefulDegradationSystem,
    StateManager,
    ZeroIAOrchestrator,
    ZeroIACoordinator,
    DEFAULT_CONFIG,
    get_coordinator,
    get_version,
    get_zeroia_status,
)


class ZeroIACore:
    """
    Façade légère autour de ZeroIAOrchestrator.

    Interface minimale :
    - ``get_status()`` : renvoie un dict de statut haut niveau.
    """

    def __init__(self) -> None:
        self._orchestrator = ZeroIAOrchestrator()

    def get_status(self) -> Dict[str, Any]:
        """
        Retourne le statut courant de ZeroIA, en se basant sur get_zeroia_status().
        """
        status = get_zeroia_status()
        return status


def get_zeroia_core() -> ZeroIACore:
    """
    Utilitaire de compatibilité : retourne une instance de ``ZeroIACore``.
    """
    return ZeroIACore()


def get_core_status() -> dict[str, Any]:
    """
    Retourne un statut synthétique du "core" ZeroIA.

    Cette fonction est fournie pour certains anciens appels qui
    s'attendaient à un statut depuis `modules.zeroia.core`.
    """

    status = get_zeroia_status()
    return {
        "component": "zeroia_core",
        "status": status.get("status", "UNKNOWN"),
        "details": status,
    }


__all__ = [
    # Façade & helpers
    "ZeroIACore",
    "get_zeroia_core",
    "get_core_status",
    # Exports principaux (compatibilité)
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
    # Utilitaires
    "DEFAULT_CONFIG",
    "get_zeroia_status",
    "get_version",
]


def main() -> None:
    """
    Point d'entrée simple pour ``python -m modules.zeroia.core``.
    Affiche le statut sur la sortie standard.
    """
    core = ZeroIACore()
    status = core.get_status()
    print(status.get("status", "UNKNOWN"))


if __name__ == "__main__":
    main()


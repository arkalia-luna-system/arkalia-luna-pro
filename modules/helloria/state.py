"""
Module state.

Ce module fait partie du système Arkalia Luna Pro.
Utilise StorageManager pour la gestion d'état (Phase 4 - fusionné).
"""

from typing import Any

from modules.core.storage import get_storage

# Compatibilité : HelloriaStateManager fusionné avec StorageManager
# Utilise StorageManager.get_helloria_state() et save_helloria_state()


def load_helloria_state(state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Charge l'état Helloria depuis StorageManager.

    Args:
        state: État par défaut (non utilisé, conservé pour compatibilité).

    Returns:
        dict: État Helloria chargé depuis StorageManager ou état par défaut.
    """
    storage = get_storage()
    return storage.get_helloria_state()


def save_helloria_state(state: dict[str, Any]) -> None:
    """Sauvegarde l'état Helloria via StorageManager.

    Args:
        state: État à sauvegarder.
    """
    storage = get_storage()
    storage.save_helloria_state(state)


IS_HELLORIA = True

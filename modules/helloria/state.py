"""
Module state.

Ce module fait partie du système Arkalia Luna Pro.
"""

import logging
from pathlib import Path
from typing import Any, Optional

import toml

from modules.utils.helpers import read_state_safe, save_toml_safe

logger = logging.getLogger(__name__)


class HelloriaStateManager:
    """
    Classe HelloriaStateManager.

    Cette classe fait partie du système Arkalia Luna Pro.
    """

    def __init__(self, path: str = "state/helloria_state.toml") -> None:
        """
        Fonction __init__.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        self.path = path
        self.state: dict[str, Any] = {}

    def load(self) -> None:
        """
        Fonction load.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        self.state = read_state_safe(Path(self.path))

    def save(self) -> None:
        """
        Fonction save.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        save_toml_safe(self.state, Path(self.path))


def load_helloria_state(state: dict[str, Any]) -> dict[str, Any]:
    """Charge l'état Helloria depuis le fichier TOML.

    Args:
        state: État par défaut (non utilisé, conservé pour compatibilité).

    Returns:
        dict: État Helloria chargé depuis le fichier ou état par défaut.
    """
    loaded = read_state_safe(Path("state/helloria_state.toml"))
    if not loaded:
        return {"status": "inactive"}
    return loaded


def save_helloria_state(state: dict[str, Any]) -> None:
    """Sauvegarde l'état Helloria dans le fichier TOML.

    Args:
        state: État à sauvegarder.
    """
    save_toml_safe(state, Path("state/helloria_state.toml"))


IS_HELLORIA = True

"""
ZeroIA State Writer - Module de gestion d'état Enterprise
========================================================

Ce module fournit des fonctions robustes pour la gestion des états TOML/JSON
avec optimisations de performance et intégrité des données.

Fonctionnalités principales:
- Sauvegarde atomique avec vérification de hash
- Gestion optimisée des fichiers TOML/JSON
- Health checks pour les états ZeroIA
- Cache et optimisations performance

Version: 2.7.1-enhanced
Auteur: Arkalia-LUNA Project
"""

import hashlib
import os
from typing import Any

import toml


def file_hash(path: str) -> str:
    """
    Calcule le hash SHA256 d'un fichier pour détecter les changements.

    Cette fonction est utilisée pour optimiser les écritures en évitant
    de réécrire des fichiers identiques.

    Args:
        path (str): Chemin vers le fichier à hasher

    Returns:
        str: Hash SHA256 du fichier, chaîne vide si fichier inexistant

    Example:
        >>> hash_val = file_hash("state/zeroia_state.toml")
        >>> ark_logger.info(f"Hash du fichier: {hash_val}", extra={"module": "utils"})
    """
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_health(path: str) -> bool:
    """
    Vérifie la santé d'un état ZeroIA via son fichier TOML.

    Cette fonction détermine si ZeroIA est dans un état opérationnel
    en analysant les flags 'active' dans le fichier d'état.

    Args:
        path (str): Chemin vers le fichier d'état TOML à vérifier

    Returns:
        bool: True si ZeroIA est actif et en bonne santé, False sinon

    Note:
        - Supporte l'override FORCE_ZEROIA_OK=1 pour les tests
        - Gère gracieusement les fichiers corrompus ou manquants

    Example:
        >>> is_healthy = check_health("modules/zeroia/state/zeroia_state.toml")
        >>> status = "OK" if is_healthy else "DOWN"
        >>> ark_logger.info(f"ZeroIA status: {status}", extra={"module": "utils"})
    """
    try:
        data = toml.load(path)
        if os.getenv("FORCE_ZEROIA_OK") == "1":
            return True
        return bool(data.get("active") is True or data.get("zeroia", {}).get("active") is True)
    except (toml.TomlDecodeError, OSError, TypeError):
        return False


def load_zeroia_state(path: str) -> dict[str, Any]:
    """
    Charge un fichier d'état ZeroIA TOML avec gestion d'erreurs.

    Fonction utilitaire pour charger de façon robuste les états ZeroIA.
    Utilisée principalement par les modules de monitoring et de récupération.

    Args:
        path (str): Chemin vers le fichier d'état TOML

    Returns:
        dict[str, Any]: Dictionnaire contenant l'état ZeroIA

    Raises:
        toml.TomlDecodeError: Si fichier TOML invalide
        FileNotFoundError: Si fichier inexistant
        OSError: Si erreur d'accès fichier

    Example:
        >>> state = load_zeroia_state("modules/zeroia/state/zeroia_state.toml")
        >>> last_decision = state.get("decision", {}).get("last_decision")
    """
    with open(path, encoding="utf-8") as f:
        return toml.load(f)


# === API publique du module ===
# Note: save_json_if_changed, save_toml_if_changed, write_state_json
# ont été migrés vers modules/utils/helpers/io_safe.py
__all__ = [
    "check_health",
    "file_hash",
    "load_zeroia_state",
]

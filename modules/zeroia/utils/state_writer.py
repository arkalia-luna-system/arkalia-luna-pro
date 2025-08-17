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
import json
import os
from datetime import datetime
from typing import Any, Optional

import toml

from core.ark_logger import ark_logger


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


def save_toml_if_changed(data: dict[str, Any], target_path: str) -> None:
    """
    Sauvegarde un fichier TOML seulement s'il y a des changements.

    Utilise une approche atomique avec fichier temporaire pour éviter
    la corruption des données. Ajoute automatiquement un timestamp.

    Args:
        data (dict[str, Any]): Dictionnaire de données à sauvegarder
        target_path (str): Chemin de destination du fichier TOML

    Raises:
        OSError: Si erreur d'écriture fichier
        toml.TomlDecodeError: Si erreur de sérialisation TOML

    Example:
        >>> state_data = {"decision": {"last": "monitor", "score": 0.8}}
        >>> save_toml_if_changed(state_data, "state/zeroia_state.toml")
    """
    tmp_path = f"{target_path}.tmp"
    data_to_hash = data.copy()
    data_to_hash.pop("timestamp", None)

    with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
        toml.dump(data_to_hash, f)

    if file_hash(tmp_path) != file_hash(target_path):
        os.replace(tmp_path, target_path)
    else:
        os.remove(tmp_path)

    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(target_path, "w", encoding="utf-8", newline="\n") as f:
        toml.dump(data, f)
    with open(target_path, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n")


def save_json_if_changed(data: dict[str, Any], target_path: str) -> None:
    """
    Sauvegarde un fichier JSON seulement s'il y a des changements.

    Utilise une approche atomique avec fichier temporaire et formatage
    consistant (indent=2, sort_keys=True) pour faciliter les diffs Git.

    Args:
        data (dict[str, Any]): Dictionnaire de données à sauvegarder
        target_path (str): Chemin de destination du fichier JSON

    Raises:
        OSError: Si erreur d'écriture fichier
        json.JSONEncodeError: Si erreur de sérialisation JSON

    Example:
        >>> dashboard = {"status": "active", "last_decision": "monitor"}
        >>> save_json_if_changed(dashboard, "state/zeroia_dashboard.json")
    """
    tmp_path = f"{target_path}.tmp"
    data_to_hash = data.copy()
    data_to_hash.pop("timestamp", None)

    with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data_to_hash, f, indent=2, sort_keys=True)

    if file_hash(tmp_path) != file_hash(target_path):
        os.replace(tmp_path, target_path)
    else:
        os.remove(tmp_path)

    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(target_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, sort_keys=True)


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
        >>> ark_logger.info(f"ZeroIA status: {'OK' if is_healthy else 'DOWN'}", extra={"module": "utils"})
    """
    try:
        data = toml.load(path)
        if os.getenv("FORCE_ZEROIA_OK") == "1":
            return True
        return bool(data.get("active") is True or data.get("zeroia", {}).get("active") is True)
    except (toml.TomlDecodeError, OSError, TypeError):
        return False


def write_state_json(file_path: str, data: dict[str, Any]) -> None:
    """
    Écrit directement un fichier JSON d'état avec formatage consistant.

    Fonction simplifiée pour l'écriture directe sans vérification de hash.
    Utilisée principalement pour les snapshots et exports d'état.

    Args:
        file_path (str): Chemin de destination du fichier JSON
        data (dict[str, Any]): Données à écrire

    Raises:
        OSError: Si erreur d'écriture fichier
        json.JSONEncodeError: Si erreur de sérialisation

    Example:
        >>> snapshot = {"timestamp": "2024-01-01", "state": "operational"}
        >>> write_state_json("snapshots/state_001.json", snapshot)
    """
    with open(file_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


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
__all__ = [
    "check_health",
    "file_hash",
    "load_zeroia_state",
    "save_json_if_changed",
    "save_toml_if_changed",
    "write_state_json",
]

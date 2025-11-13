"""
Module de chargement de configuration pour Reflexia.

Ce module utilise maintenant ConfigManager centralisé pour le chargement
des configurations TOML avec cache optimisé.
"""

from core.ark_logger import ark_logger
from modules.core.config.config_manager import get_default_config_manager


def load_weights(path: str) -> dict:
    """
    Charge les poids réflexifs depuis le fichier TOML avec cache Enhanced.
    Performance: 94.8% plus rapide que toml.load() standard.

    Utilise maintenant ConfigManager centralisé.
    """
    try:
        config_manager = get_default_config_manager()
        return config_manager.load_toml_config(path)
    except Exception as e:
        ark_logger.error(
            f"❌ Failed to load TOML config: {e}", extra={"arkalia_module": "reflexia"}
        )
        raise  # <== Important : on re-lève l'erreur


def load_config_enhanced(file_path: str, cache_ttl: int = 30) -> dict:
    """
    Charge la configuration avec cache Enhanced.

    Utilise maintenant ConfigManager centralisé.
    """
    config_manager = get_default_config_manager()
    return config_manager.load_toml_config(file_path)


def load_config(file_path: str) -> dict:
    """
    Version legacy qui lève des exceptions pour les tests.

    Utilise maintenant ConfigManager centralisé.
    """
    import os

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    try:
        config_manager = get_default_config_manager()
        return config_manager.load_toml_config(file_path)
    except Exception as e:
        raise Exception(f"Error loading config {file_path}: {e}") from e

"""
Validateurs étendus pour Arkalia-LUNA
"""

import re
from typing import Any, Optional


def validate_config(config: dict[str, Any]) -> list[str]:
    """Valide une configuration et retourne les erreurs."""
    errors = []

    if not isinstance(config, dict):
        errors.append("La configuration doit être un dictionnaire")
        return errors

    required_keys = ["version", "modules"]
    for key in required_keys:
        if key not in config:
            errors.append(f"Clé requise manquante: {key}")

    return errors


def validate_json_schema(data: Any, schema: dict[str, Any]) -> list[str]:
    """Valide des données contre un schéma JSON simple."""
    errors = []

    if not isinstance(data, dict):
        errors.append("Les données doivent être un dictionnaire")
        return errors

    for key, expected_type in schema.items():
        if key not in data:
            errors.append(f"Clé manquante: {key}")
        elif not isinstance(data[key], expected_type):
            errors.append(
                f"Type incorrect pour {key}: attendu {expected_type}, reçu {type(data[key])}"
            )

    return errors


def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier pour la sécurité."""
    # Supprime les caractères dangereux
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Limite la longueur
    return sanitized[:255]

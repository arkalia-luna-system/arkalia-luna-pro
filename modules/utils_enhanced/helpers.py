"""
Helpers étendus pour Arkalia-LUNA
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def safe_json_load(file_path: Path) -> Any:
    """Charge un fichier JSON de manière sécurisée."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.warning(f"Erreur lors du chargement de {file_path}: {e}")
        return None


def safe_json_save(data: dict[str, Any], file_path: Path) -> bool:
    """Sauvegarde des données JSON de manière sécurisée."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de {file_path}: {e}")
        return False


def ensure_directory(path: Path) -> bool:
    """Crée un répertoire s'il n'existe pas."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la création du répertoire {path}: {e}")
        return False

"""Utilitaires de sauvegarde pour le module ZeroIA.

Ce module fournit des fonctions pour sauvegarder et restaurer
l'état du module ZeroIA.
"""
import shutil
from pathlib import Path

from core.ark_logger import ark_logger

STATE_PATH = Path("modules/zeroia/state/zeroia_state.toml")
BACKUP_PATH = Path("modules/zeroia/state/zeroia_state_backup.toml")


def save_backup() -> None:
    """Sauvegarde automatique de l'état ZeroIA.

    Crée une copie de sauvegarde du fichier d'état actuel.
    """
    if STATE_PATH.exists():
        shutil.copy2(STATE_PATH, BACKUP_PATH)
        ark_logger.info("🧪 Backup auto effectué.", extra={"arkalia_module": "utils"})
    else:
        ark_logger.info("⚠️ Aucun fichier d'état à sauvegarder.", extra={"arkalia_module": "utils"})

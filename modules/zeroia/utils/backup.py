import shutil
from pathlib import Path

from core.ark_logger import ark_logger

STATE_PATH = Path("modules/zeroia/state/zeroia_state.toml")
BACKUP_PATH = Path("modules/zeroia/state/zeroia_state_backup.toml")


def save_backup() -> None:
    if STATE_PATH.exists():
        shutil.copy2(STATE_PATH, BACKUP_PATH)
        ark_logger.info("🧪 Backup auto effectué.", extra={"module": "utils"})
    else:
        ark_logger.info("⚠️ Aucun fichier d'état à sauvegarder.", extra={"module": "utils"})

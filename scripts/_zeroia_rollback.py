#!/usr/bin/env python3
# 🔄 ZeroIA Rollback — Arkalia LUNA v2.6.x

import argparse
import shutil
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("modules/zeroia/state/zeroia_state.toml")
SNAPSHOT_FILE = Path("modules/zeroia/state/zeroia_state_snapshot.toml")
BACKUP_FILE = Path("modules/zeroia/state/zeroia_state_backup.toml")
LOG_FILE = Path("logs/zeroia_rollback.log")
FAILURE_LOG = Path("logs/failure_analysis.md")

__all__ = [
    "backup_current_state",
    "restore_snapshot",
    "log_failure",
    "log",
    "rollback_from_backup",
    "parse_arguments",
    "main",
]


def log(msg: str, silent: bool = False) -> None:
    """Log message to rollback.log and print if not silent."""
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[rollback] {msg}\n")
    except Exception as e:
        print(f"[rollback] Erreur : {e}")
    if not silent:
        print(msg)


def backup_current_state(silent: bool = False) -> None:
    """Crée une sauvegarde de l'état ZeroIA actuel.

    Args:
        silent: Mode silencieux (défaut: False).
    """
    if STATE_FILE.exists():
        shutil.copy2(STATE_FILE, BACKUP_FILE)
        log(f"🗄️  Backup du fichier actuel effectué : {BACKUP_FILE}", silent)


def restore_snapshot(silent: bool = False) -> bool:
    """Restaure un snapshot de l'état ZeroIA.

    Args:
        silent: Mode silencieux (défaut: False).

    Returns:
        bool: True si la restauration a réussi, False sinon.
    """
    if not SNAPSHOT_FILE.exists():
        log("❌ Aucun fichier snapshot à restaurer.", silent)
        return False
    shutil.copy2(SNAPSHOT_FILE, STATE_FILE)
    log("✅ Snapshot restauré dans zeroia_state.toml", silent)
    return True


def log_failure() -> None:
    """Enregistre un échec dans le log de failures."""
    FAILURE_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        with FAILURE_LOG.open("a", encoding="utf-8") as f:
            f.write("\n")
            f.write(f"## 🛑 Échec détecté : {datetime.now().isoformat()}\n")
            f.write("**Raison :** Restauration du snapshot ZeroIA exécutée manuellement.\n")
    except Exception as e:
        log(f"❌ Impossible d'écrire dans le journal d'échec : {e}")


def rollback_from_backup(silent: bool = False) -> None:
    """Effectue un rollback depuis le backup.

    Args:
        silent: Mode silencieux (défaut: False).
    """
    if not BACKUP_FILE.exists():
        log("❌ Rollback impossible : aucun backup trouvé.", silent)
        return
    try:
        shutil.copy2(BACKUP_FILE, STATE_FILE)
        log("✅ Rollback effectué depuis backup.", silent)
    except Exception as e:
        log(f"❌ Erreur lors du rollback : {e}", silent)


def parse_arguments() -> argparse.Namespace:
    """Parse les arguments de ligne de commande.

    Returns:
        argparse.Namespace: Arguments parsés.
    """
    parser = argparse.ArgumentParser(description="ZeroIA Rollback Script")
    parser.add_argument(
        "--no-rollback",
        action="store_true",
        help="Ne pas restaurer (utiliser uniquement le backup)",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Désactive les impressions console (mode CI)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    backup_current_state(silent=args.silent)
    if args.no_rollback:
        log("Rollback désactivé via --no-rollback", silent=args.silent)
        return

    if restore_snapshot(silent=args.silent):
        log_failure()
    rollback_from_backup(silent=args.silent)

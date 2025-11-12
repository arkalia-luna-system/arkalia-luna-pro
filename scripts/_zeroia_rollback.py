#!/usr/bin/env python3
# 🔄 ZeroIA Rollback — Arkalia LUNA v2.6.x

import argparse
import shutil
from datetime import datetime
from pathlib import Path


# Résoudre les chemins depuis le répertoire de travail courant
def get_state_file() -> Path:
    """Retourne le chemin du fichier d'état, résolu depuis le répertoire de travail courant."""
    return Path.cwd() / "modules" / "zeroia" / "state" / "zeroia_state.toml"


def get_snapshot_file() -> Path:
    """Retourne le chemin du fichier snapshot, résolu depuis le répertoire de travail courant."""
    return Path.cwd() / "modules" / "zeroia" / "state" / "zeroia_state_snapshot.toml"


def get_backup_file() -> Path:
    """Retourne le chemin du fichier backup, résolu depuis le répertoire de travail courant."""
    return Path.cwd() / "modules" / "zeroia" / "state" / "zeroia_state_backup.toml"


def get_log_file() -> Path:
    """Retourne le chemin du fichier de log, résolu depuis le répertoire de travail courant."""
    return Path.cwd() / "logs" / "zeroia_rollback.log"


def get_failure_log() -> Path:
    """Retourne le chemin du fichier de log d'échec, résolu depuis le répertoire de travail courant."""
    return Path.cwd() / "logs" / "failure_analysis.md"


# Pour compatibilité avec les tests qui patch ces variables
# Ne pas initialiser ici car Path.cwd() est résolu au moment de l'import
# Les tests peuvent patcher ces variables, sinon elles seront résolues dynamiquement
STATE_FILE: Path | None = None
SNAPSHOT_FILE: Path | None = None
BACKUP_FILE: Path | None = None
LOG_FILE: Path | None = None
FAILURE_LOG: Path | None = None

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
        # Résoudre le chemin dynamiquement
        if LOG_FILE is not None and LOG_FILE.is_absolute():
            log_file = LOG_FILE
        else:
            log_file = get_log_file()
        # Créer le répertoire parent si nécessaire
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(f"[rollback] {msg}\n")
    except Exception as e:
        if not silent:
            print(f"[rollback] Erreur : {e}")
    if not silent:
        print(msg)


def backup_current_state(silent: bool = False) -> None:
    """Crée une sauvegarde de l'état ZeroIA actuel.

    Args:
        silent: Mode silencieux (défaut: False).
    """
    # Résoudre les chemins dynamiquement depuis le répertoire de travail courant
    # Toujours utiliser les fonctions de résolution pour garantir le bon chemin
    # Utiliser Path.cwd() pour résoudre depuis le répertoire de travail actuel
    # Si STATE_FILE est un Path absolu (patché par les tests), l'utiliser tel quel
    if STATE_FILE is not None and STATE_FILE.is_absolute():
        state_file = STATE_FILE
        if BACKUP_FILE is not None and BACKUP_FILE.is_absolute():
            backup_file = BACKUP_FILE
        else:
            backup_file = get_backup_file()
    else:
        # Utiliser les fonctions de résolution pour obtenir les chemins dynamiques
        state_file = get_state_file()
        backup_file = get_backup_file()

    if state_file.exists():
        # Créer le répertoire parent si nécessaire
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(state_file, backup_file)
            log(f"🗄️  Backup du fichier actuel effectué : {backup_file}", silent)
        except Exception as e:
            log(f"❌ Erreur lors de la création du backup : {e}", silent)
            raise
    else:
        log(f"⚠️  Fichier d'état introuvable : {state_file}", silent)


def restore_snapshot(silent: bool = False) -> bool:
    """Restaure un snapshot de l'état ZeroIA.

    Args:
        silent: Mode silencieux (défaut: False).

    Returns:
        bool: True si la restauration a réussi, False sinon.
    """
    # Résoudre les chemins dynamiquement
    if SNAPSHOT_FILE is not None and SNAPSHOT_FILE.is_absolute():
        snapshot_file = SNAPSHOT_FILE
        state_file = (
            STATE_FILE
            if (STATE_FILE is not None and STATE_FILE.is_absolute())
            else get_state_file()
        )
    else:
        snapshot_file = get_snapshot_file()
        state_file = get_state_file()

    if not snapshot_file.exists():
        log("❌ Aucun fichier snapshot à restaurer.", silent)
        return False
    # Créer le répertoire parent si nécessaire
    state_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(snapshot_file, state_file)
    log("✅ Snapshot restauré dans zeroia_state.toml", silent)
    return True


def log_failure() -> None:
    """Enregistre un échec dans le log de failures."""
    # Résoudre le chemin dynamiquement
    if FAILURE_LOG is not None and FAILURE_LOG.is_absolute():
        failure_log = FAILURE_LOG
    else:
        failure_log = get_failure_log()

    failure_log.parent.mkdir(parents=True, exist_ok=True)
    try:
        with failure_log.open("a", encoding="utf-8") as f:
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
    # Résoudre les chemins dynamiquement
    if BACKUP_FILE is not None and BACKUP_FILE.is_absolute():
        backup_file = BACKUP_FILE
        state_file = (
            STATE_FILE
            if (STATE_FILE is not None and STATE_FILE.is_absolute())
            else get_state_file()
        )
    else:
        backup_file = get_backup_file()
        state_file = get_state_file()

    if not backup_file.exists():
        log("❌ Rollback impossible : aucun backup trouvé.", silent)
        return
    try:
        # Créer le répertoire parent si nécessaire
        state_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_file, state_file)
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

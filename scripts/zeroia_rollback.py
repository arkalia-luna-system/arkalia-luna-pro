#!/usr/bin/env python3
"""
Script de rollback pour ZeroIA.
Permet de restaurer un état précédent en cas de problème.
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.ark_logger import ark_logger

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import toml

try:
    from modules.utils.helpers.io_safe import read_state_safe
    from modules.zeroia.failsafe import restore_backup
except ImportError as e:
    print(f"Erreur d'import: {e}")
    print("Vérifiez que le PYTHONPATH inclut le répertoire racine du projet")
    sys.exit(1)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("zeroia_rollback")


def parse_args() -> argparse.Namespace:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description="Script de rollback pour ZeroIA")
    parser.add_argument(
        "--snapshot",
        type=str,
        help="Chemin vers le snapshot à restaurer",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force le rollback même si ZeroIA est actif",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Mode silencieux (pas de logs)",
    )
    return parser.parse_args()


def check_zeroia_status() -> bool:
    """Vérifie si ZeroIA est actif."""
    try:
        state = read_state_safe("data/zeroia/state.toml")
        if not state:
            return False
        return bool(state.get("status", {}).get("active", False))
    except Exception:
        return False


def backup_current_state() -> str:
    """Crée une sauvegarde de l'état actuel."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data/zeroia/backups/state_backup_{timestamp}.toml"

    # Créer le répertoire de sauvegarde si nécessaire
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)

    # Copier l'état actuel
    if os.path.exists("data/zeroia/state.toml"):
        import shutil

        shutil.copy2("data/zeroia/state.toml", backup_path)

    return backup_path


def main() -> None:
    """Point d'entrée principal."""
    args = parse_args()

    if args.silent:
        logger.setLevel(logging.WARNING)

    try:
        # Vérifier si ZeroIA est actif
        if check_zeroia_status() and not args.force:
            logger.warning("ZeroIA est actif. Utilisez --force pour forcer le rollback.")
            sys.exit(1)

        # Créer une sauvegarde de l'état actuel
        backup_path = backup_current_state()
        logger.info(f"Sauvegarde créée : {backup_path}")

        # Restaurer le snapshot si spécifié
        if args.snapshot:
            restore_backup(args.snapshot, "data/zeroia/state.toml")
            logger.info(f"Snapshot restauré : {args.snapshot}")

        sys.exit(0)
    except Exception as e:
        logger.error(f"Erreur lors du rollback : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

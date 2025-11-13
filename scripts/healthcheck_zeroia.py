#!/usr/bin/env python3
"""
Healthcheck IA ZeroIA — Vérification de l'état cognitif

Ce script vérifie l'état de santé de ZeroIA en validant :
- L'existence et la validité du fichier d'état TOML
- La présence des champs requis dans l'état
"""
# ✅ Healthcheck IA ZeroIA — Vérification de l'état cognitif

import datetime
import os
import sys
from pathlib import Path

import toml

# Ajouter le chemin du projet pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ark_logger import ark_logger

DEFAULT_STATE_PATH = "modules/zeroia/state/zeroia_state.toml"
REQUIRED_FIELDS = ["last_decision", "confidence_score", "justification", "timestamp"]


def check_state_file() -> int:
    """Vérifie la validité du fichier d'état ZeroIA.

    Returns:
        int: Code de sortie (0=OK, 1=champs manquants, 2=fichier introuvable).
    """
    # Utiliser la variable d'environnement ou le chemin par défaut
    state_path = os.environ.get("ZEROIA_STATE_PATH", DEFAULT_STATE_PATH)

    if not os.path.exists(state_path):
        print("❌ Fichier d'état introuvable.")
        ark_logger.info("❌ Fichier d'état introuvable.", extra={"arkalia_module": "scripts"})
        return 2

    try:
        with open(state_path) as f:
            data = toml.load(f)
    except toml.TomlDecodeError as e:
        print(f"❌ Erreur TOML : {e}")
        ark_logger.info(f"❌ Erreur TOML : {e}", extra={"arkalia_module": "scripts"})
        return 2

    decision_block = data.get("decision", {})
    missing = [f for f in REQUIRED_FIELDS if f not in decision_block]

    if missing:
        print(f"⚠️ Champs manquants : {missing}")
        ark_logger.info(f"⚠️ Champs manquants : {missing}", extra={"arkalia_module": "scripts"})
        return 1

    print("✅ État ZeroIA valide.")
    ark_logger.info("✅ État ZeroIA valide.", extra={"arkalia_module": "scripts"})
    return 0


if __name__ == "__main__":
    code = check_state_file()
    now = datetime.datetime.now().isoformat()
    ark_logger.info(f"📆 Vérification effectuée à : {now}", extra={"arkalia_module": "scripts"})
    sys.exit(code)

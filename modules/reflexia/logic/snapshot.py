"""
Module de snapshot pour Reflexia.

Ce module gère la sauvegarde et le chargement des snapshots d'état Reflexia.
"""
import json
import os
from datetime import datetime
from pathlib import Path

SNAPSHOT_FILE = Path("modules/reflexia/state/reflexia_state.toml")

# ✅ Crée le dossier si manquant
os.makedirs(SNAPSHOT_FILE.parent, exist_ok=True)


def save_snapshot(metrics: dict, status: str):
    """
    Sauvegarde l'état réflexif dans un fichier .toml (contenu simulé en JSON).
    """
    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics,
        "status": status,
    }
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

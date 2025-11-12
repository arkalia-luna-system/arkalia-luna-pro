#!/usr/bin/env python3
"""
Script de correction pour Pyright/Cursor.

Ce script corrige les problèmes de configuration Pyright en :
- Créant le fichier __init__.py manquant dans modules/
- Ajoutant PYTHONPATH dans .env si nécessaire
"""
from pathlib import Path

from core.ark_logger import ark_logger

ROOT = Path(__file__).resolve().parent.parent
MODULES = ROOT / "modules"
ENV_FILE = ROOT / ".env"


def ensure_init_py() -> None:
    """
    Vérifie et crée le fichier __init__.py dans modules/ si nécessaire.
    """
    init_path = MODULES / "__init__.py"
    if not init_path.exists():
        init_path.touch()
        ark_logger.info(f"✅ Créé : {init_path}", extra={"arkalia_module": "scripts"})
    else:
        ark_logger.info(f"✔️ Déjà présent : {init_path}", extra={"arkalia_module": "scripts"})


def ensure_env_py_path() -> None:
    """Configure le chemin Python dans le fichier .env."""
    """
    Vérifie et ajoute PYTHONPATH dans .env si nécessaire.
    """
    if ENV_FILE.exists():
        content = ENV_FILE.read_text()
        if "PYTHONPATH" in content:
            ark_logger.info(
                "✔️ PYTHONPATH déjà présent dans .env", extra={"arkalia_module": "scripts"}
            )
            return
    with open(ENV_FILE, "a") as f:
        f.write("\nPYTHONPATH=./modules\n")
    ark_logger.info(f"✅ PYTHONPATH ajouté à {ENV_FILE}", extra={"arkalia_module": "scripts"})


def main() -> None:
    """Fonction principale du script de correction Pyright."""
    """
    Fonction principale exécutant les corrections Pyright.
    """
    ark_logger.info("🔧 Patch Pyright / Cursor en cours…", extra={"arkalia_module": "scripts"})
    ensure_init_py()
    ensure_env_py_path()
    ark_logger.info(
        "✅ Terminé. Recharge Cursor (⇧⌘P > Reload Window)", extra={"arkalia_module": "scripts"}
    )


if __name__ == "__main__":
    main()

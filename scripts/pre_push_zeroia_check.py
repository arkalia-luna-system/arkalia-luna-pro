#!/usr/bin/env python3
"""
Pre-push ZeroIA Validator — Arkalia LUNA v2.6.x

Ce script valide l'état de ZeroIA avant un push Git :
- Vérifie la validité du fichier TOML d'état
- Détecte l'exposition de tokens PAT GitHub
"""
# 🚫 Pre-push ZeroIA Validator — Arkalia LUNA v2.6.x

import re
from pathlib import Path

try:
    from core.ark_logger import ark_logger
except ImportError:
    # Fallback si l'import échoue
    import logging

    _fallback_logger = logging.getLogger("arkalia")
    _fallback_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    _fallback_logger.addHandler(handler)
    ark_logger = _fallback_logger  # type: ignore[assignment]

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

STATE_FILE = Path("state/zeroia_state.toml")
DASHBOARD_FILE = Path("state/zeroia_dashboard.json")
ENV_FILES = list(Path(".").rglob("*.env"))


def check_toml_validity() -> bool:
    """Vérifie la validité du fichier TOML d'état ZeroIA.

    Returns:
        bool: True si le fichier est valide, False sinon.
    """
    try:
        with STATE_FILE.open("rb") as f:
            tomllib.load(f)
        print("✅ Fichier TOML valide.")
        ark_logger.info("✅ Fichier TOML valide.", extra={"arkalia_module": "scripts"})
        return True
    except Exception as e:
        print(f"❌ Erreur de parsing TOML: {e}")
        ark_logger.info(f"❌ Erreur de parsing TOML: {e}", extra={"arkalia_module": "scripts"})
        return False


def check_pat_exposure() -> bool:
    """Vérifie l'exposition de tokens PAT GitHub dans les fichiers.

    Returns:
        bool: True si aucun token n'est exposé, False sinon.
    """
    pat_regex = re.compile(r"ghp_[A-Za-z0-9]{36,}")
    for file in ENV_FILES:
        content = file.read_text(errors="ignore")
        if pat_regex.search(content):
            ark_logger.info(
                f"⚠️ Token PAT détecté dans : {file}", extra={"arkalia_module": "scripts"}
            )
            return False
    return True


if __name__ == "__main__":
    errors = []

    if not check_toml_validity():
        errors.append("Invalid TOML")

    if not check_pat_exposure():
        errors.append("PAT exposé")

    if errors:
        print("🚫 Pre-push bloqué.")
        ark_logger.info("🚫 Pre-push bloqué.", extra={"arkalia_module": "scripts"})
        exit(1)

    print("🛡️ Tous les contrôles ZeroIA sont OK.")
    ark_logger.info("🛡️ Tous les contrôles ZeroIA sont OK.", extra={"arkalia_module": "scripts"})
    exit(0)

#!/usr/bin/env python3
# 🚫 Pre-push ZeroIA Validator — Arkalia LUNA v2.6.x

import re

from core.ark_logger import ark_logger

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

from pathlib import Path

STATE_FILE = Path("modules/zeroia/state/zeroia_state.toml")
DASHBOARD_FILE = Path("state/zeroia_dashboard.json")
ENV_FILES = list(Path(".").rglob("*.env"))


def check_toml_validity() -> None:
    try:
        with STATE_FILE.open("rb") as f:
            tomllib.load(f)
        ark_logger.info("✅ Fichier TOML valide.", extra={"arkalia_module": "scripts"})
        return True
    except Exception as e:
        ark_logger.info(f"❌ Erreur de parsing TOML: {e}", extra={"arkalia_module": "scripts"})
        return False


def check_pat_exposure() -> None:
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
        ark_logger.info("🚫 Pre-push bloqué.", extra={"arkalia_module": "scripts"})
        exit(1)

    ark_logger.info("🛡️ Tous les contrôles ZeroIA sont OK.", extra={"arkalia_module": "scripts"})
    exit(0)

# 📊 Arkalia IA Monitor
# Affiche un état synthétique de la cognition ZeroIA

import json
import subprocess  # nosec
import sys
from pathlib import Path

import requests
import toml

from core.ark_logger import ark_logger

STATE_PATH = Path("modules/zeroia/state/zeroia_state.toml")
DASHBOARD_PATH = Path("state/zeroia_dashboard.json")
LOG_FILE = Path("logs/failure_analysis.md")


def check_docker_status() -> None:
    try:
        result = subprocess.run(
            [sys.executable, "docker_status.py"],
            capture_output=True,
            text=True,
            check=True,
            shell=False,
        )  # nosec
        if result.stdout:
            ark_logger.info(
                "\n🐳 Docker — Conteneurs en cours d'exécution", extra={"module": "scripts"}
            )
            ark_logger.info(result.stdout, extra={"module": "scripts"})
        else:
            ark_logger.info(
                "\n🐳 Docker — Aucun conteneur en cours d'exécution", extra={"module": "scripts"}
            )
    except subprocess.CalledProcessError as e:
        ark_logger.info(f"💥 Erreur Docker : {e}", extra={"module": "scripts"})


def ping_reflexia() -> None:
    try:
        response = requests.get("http://reflexia-endpoint/ping", timeout=5)
        if response.status_code == 200:
            ark_logger.info("\n🔗 Reflexia — Actif", extra={"module": "scripts"})
        else:
            ark_logger.info("\n🔗 Reflexia — Inactif", extra={"module": "scripts"})
    except requests.RequestException as e:
        ark_logger.info(f"💥 Erreur Reflexia : {e}", extra={"module": "scripts"})


def display_recent_errors() -> None:
    ark_logger.info("\n📝 Dernières erreurs connues", extra={"module": "scripts"})
    if LOG_FILE.exists():
        with LOG_FILE.open("r", encoding="utf-8") as f:
            lines = f.readlines()
            ark_logger.info(
                "".join(lines[-5:], extra={"module": "scripts"})
            )  # Affiche les 5 dernières lignes du fichier de log
    else:
        ark_logger.info("Aucune erreur connue.", extra={"module": "scripts"})


if __name__ == "__main__":
    ark_logger.info("\n📄 ZeroIA — TOML State", extra={"module": "scripts"})
    try:
        data = toml.load(STATE_PATH)
        ark_logger.info(toml.dumps(data, extra={"module": "scripts"}))
    except Exception as e:
        ark_logger.info(f"💥 Erreur lecture TOML : {e}", extra={"module": "scripts"})

    ark_logger.info("\n📊 ZeroIA — Dashboard JSON", extra={"module": "scripts"})
    try:
        data = json.loads(DASHBOARD_PATH.read_text())
        ark_logger.info(json.dumps(data, indent=2, extra={"module": "scripts"}))
    except Exception as e:
        ark_logger.info(f"💥 Erreur lecture JSON : {e}", extra={"module": "scripts"})

    check_docker_status()
    ping_reflexia()
    display_recent_errors()

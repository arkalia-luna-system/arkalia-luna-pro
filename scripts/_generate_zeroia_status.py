"""
Script de génération automatique du statut ZeroIA.

Ce script génère un fichier Markdown avec le statut actuel de ZeroIA,
incluant les logs Docker et les dernières décisions prises.
"""

# scripts/_generate_zeroia_status.py

import datetime
import os
import subprocess  # nosec
import sys
from pathlib import Path

from core.ark_logger import ark_logger

OUTPUT_FILE = "docs/logs/zeroia_status.md"


def get_container_logs(container_name: str, tail: int = 50) -> str:
    """Récupère les logs d'un conteneur Docker.

    Args:
        container_name: Nom du conteneur.
        tail: Nombre de lignes à récupérer (défaut: 50).

    Returns:
        str: Logs du conteneur.
    """
    try:
        logs = subprocess.check_output(
            ["docker", "logs", container_name, "--tail", str(tail)],
            stderr=subprocess.DEVNULL,
        )  # nosec
        return logs.decode("utf-8", errors="ignore")
    except subprocess.CalledProcessError:
        return ""


def get_container_status(container_name: str) -> str:
    """Récupère le statut d'un conteneur Docker.

    Args:
        container_name: Nom du conteneur.

    Returns:
        str: Statut du conteneur.
    """
    try:
        status = subprocess.check_output(
            ["docker", "inspect", "-f", "{{.State.Status}}", container_name]
        )  # nosec
        return status.decode("utf-8").strip()
    except subprocess.CalledProcessError:
        return "unknown"


def parse_decisions(logs: str) -> list[str]:
    """Parse les décisions ZeroIA depuis les logs.

    Args:
        logs: Logs du conteneur.

    Returns:
        list: Liste des décisions trouvées.
    """
    lines = logs.splitlines()
    return [line.strip() for line in lines if "ZeroIA decided" in line]


def write_markdown(status: str, decisions: list[str]) -> None:
    """Écrit le statut ZeroIA dans un fichier Markdown.

    Args:
        status: Statut du conteneur.
        decisions: Liste des décisions récentes.
    """
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# 🤖 ZeroIA — Statut automatique\n\n")
        f.write(f"- 🕰️ Dernière mise à jour : `{timestamp}`\n")
        f.write("- 📦 Conteneur : `zeroia`\n")
        f.write(f"- 🔄 Statut Docker : `{status}`\n\n")

        if decisions:
            f.write("## 🧠 Dernières décisions IA\n\n")
            for d in decisions[-10:]:
                f.write(f"- {d}\n")
        else:
            f.write("Aucune décision récente détectée.\n")

    ark_logger.info(f"✅ Statut écrit dans {OUTPUT_FILE}", extra={"arkalia_module": "scripts"})


def get_file_info(filepath: str) -> str:
    """Affiche les informations d'un fichier.

    Args:
        filepath: Chemin du fichier.

    Returns:
        str: Informations sur le fichier.
    """
    p = Path(filepath)
    if not p.exists():
        return f"- ❌ {filepath} (not found)"
    size = p.stat().st_size
    mtime = datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    return f"- ✅ `{filepath}` — **{size} bytes**, modifié le *{mtime}*"


def main() -> None:
    """Fonction principale de génération du statut ZeroIA."""
    container = "zeroia"
    if not os.path.exists("docs/logs"):
        os.makedirs("docs/logs")

    status = get_container_status(container)
    logs = get_container_logs(container, tail=100)
    decisions = parse_decisions(logs)

    if not logs:
        ark_logger.info(
            "❌ Impossible de récupérer les logs de ZeroIA.", extra={"arkalia_module": "scripts"}
        )
        sys.exit(1)

    write_markdown(status, decisions)


if __name__ == "__main__":
    main()

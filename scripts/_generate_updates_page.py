"""Script de génération de la page des dernières mises à jour.

Ce script génère automatiquement une page listant les dernières mises à jour
depuis l'historique Git.
"""

import subprocess  # nosec
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ark_logger: Any
try:
    from core.ark_logger import ark_logger
except Exception:  # pragma: no cover - fallback utilitaire
    import logging

    ark_logger = logging.getLogger("arkalia-updates")
    if not ark_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        ark_logger.addHandler(handler)
    ark_logger.setLevel(logging.INFO)

# Supprimer les fichiers ._* (pollution macOS)
for file in Path("docs/releases").glob("._*"):
    file.unlink()


def main(**kwargs: Any) -> None:
    """Génère la page des dernières mises à jour depuis Git.

    Args:
        **kwargs: Arguments optionnels (non utilisés actuellement).
    """
    ark_logger.info("✅ Hook exécuté : génération des updates", extra={"arkalia_module": "scripts"})

    repo_path = Path(kwargs.get("repo_path", Path.cwd()))
    output_file = Path(kwargs.get("output_file", "docs/releases/dernieres_updates.md"))
    command = [
        "git",
        "log",
        "--pretty=format:%h - %s (%ad)",
        "--abbrev-commit",
        "--date=short",
        "-n",
        "10",
    ]

    try:
        result = subprocess.run(
            command, cwd=repo_path, capture_output=True, text=True, check=True
        )  # nosec
        output_file.parent.mkdir(parents=True, exist_ok=True)

        new_content = "# 🔄 Dernières mises à jour\n" + result.stdout.strip() + "\n"
        if output_file.exists() and output_file.read_text(encoding="utf-8") == new_content:
            ark_logger.info(
                "✅ Aucun changement détecté, pas d'écriture nécessaire.",
                extra={"arkalia_module": "scripts"},
            )
            return

        with output_file.open("w", encoding="utf-8") as f:
            f.write(new_content)

        # Nettoyage explicite du sidecar AppleDouble éventuel du fichier cible
        apple_double = output_file.parent / f"._{output_file.name}"
        if apple_double.exists():
            apple_double.unlink()

        ark_logger.info(
            f"✅ Updates page générée avec {len(result.stdout.strip().splitlines())} "
            "commits récents.",
            extra={"arkalia_module": "scripts"},
        )

        # Supprimer les fichiers macOS invisibles s'ils existent
        for file in output_file.parent.glob("._*"):
            file.unlink()
    except subprocess.CalledProcessError as e:
        ark_logger.info(
            f"Erreur lors de l'exécution de la commande git: {e}",
            extra={"arkalia_module": "scripts"},
        )


if __name__ == "__main__":
    main()

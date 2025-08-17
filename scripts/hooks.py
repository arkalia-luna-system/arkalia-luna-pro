# scripts/hooks.py

import subprocess  # nosec

from core.ark_logger import ark_logger


def run_sitemap_generator(config=None) -> None:
    import os
    import sys

    script_path = os.path.join("scripts", "sitemap_generator.py")
    if not os.path.exists(script_path):
        ark_logger.info(
            f"[hooks] ❌ Script non trouvé : {script_path}",
            file=sys.stderr,
            extra={"module": "scripts"},
        )
        return

    try:
        subprocess.run([sys.executable, script_path], check=True)  # nosec
        ark_logger.info("[hooks] ✅ Sitemap généré avec succès", extra={"module": "scripts"})
    except subprocess.CalledProcessError as e:
        ark_logger.info(
            f"[hooks] ❌ Erreur lors de l'exécution du sitemap : {e}",
            file=sys.stderr,
            extra={"module": "scripts"},
        )

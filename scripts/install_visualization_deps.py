#!/usr/bin/env python3
"""
📊 Installation des dépendances de visualisation Arkalia-LUNA
Installe les packages nécessaires pour les graphiques et dashboards
"""

import subprocess
import sys
from pathlib import Path

from core.ark_logger import ark_logger


def install_package(package: str) -> bool:
    """Installe un package avec pip"""
    try:
        ark_logger.info(f"📦 Installation de {package}...", extra={"module": "scripts"})
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        ark_logger.info(f"✅ {package} installé avec succès", extra={"module": "scripts"})
        return True
    except subprocess.CalledProcessError as e:
        ark_logger.info(f"❌ Erreur installation {package}: {e}", extra={"module": "scripts"})
        return False


def main():
    """Installe toutes les dépendances de visualisation"""
    ark_logger.info(
        "🌕 Installation des dépendances de visualisation Arkalia-LUNA...",
        extra={"module": "scripts"},
    )

    # Packages de visualisation
    packages = [
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.15.0",
        "kaleido>=0.2.1",  # Pour export PNG de Plotly
        "jupyter>=1.0.0",
        "ipywidgets>=8.0.0",
    ]

    success_count = 0
    total_count = len(packages)

    for package in packages:
        if install_package(package):
            success_count += 1

    ark_logger.info(
        f"\n📊 Résumé: {success_count}/{total_count} packages installés",
        extra={"module": "scripts"},
    )

    if success_count == total_count:
        ark_logger.info(
            "🎉 Toutes les dépendances installées avec succès !", extra={"module": "scripts"}
        )
        ark_logger.info("\n🚀 Vous pouvez maintenant utiliser:", extra={"module": "scripts"})
        ark_logger.info("   python3 scripts/arkalia_visualizations.py", extra={"module": "scripts"})
        return True
    else:
        ark_logger.info(
            "⚠️ Certains packages n'ont pas pu être installés", extra={"module": "scripts"}
        )
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

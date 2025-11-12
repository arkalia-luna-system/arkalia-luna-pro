#!/usr/bin/env python3
"""
Script pour vérifier les tests skipped dans Arkalia-LUNA Pro
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Fonction principale pour vérifier les tests skipped."""
    print("🔍 Vérification des tests skipped - Arkalia-LUNA Pro")
    print("=" * 60)

    # Vérifier que nous sommes dans le bon répertoire
    if not Path("pyproject.toml").exists():
        print("❌ Erreur: pyproject.toml non trouvé. Exécutez depuis la racine du projet.")
        sys.exit(1)

    try:
        # Collecter les tests avec marqueurs chaos et performance
        print("\n📊 Collecte des tests chaos et performance...")
        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "--collect-only",
                "-q",
                "-m",
                "chaos or performance",
                "--disable-warnings",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ Tests collectés avec succès")
            print("\n📋 Résumé des tests collectés:")
            print(result.stdout)
        else:
            print("⚠️ Erreur lors de la collecte:")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print("⏰ Timeout lors de la collecte des tests")
    except Exception as e:
        print(f"❌ Erreur: {e}")

    print("\n💡 Conseils:")
    print("- Utilisez 'ARK_FORCE_OLLAMA=true pytest -m performance' pour forcer les tests Ollama")
    print("- Utilisez 'ARK_RUN_CHAOS=true pytest -m chaos' pour exécuter les tests de chaos")
    print("- Vérifiez manuellement les conditions skipif si nécessaire")


if __name__ == "__main__":
    main()

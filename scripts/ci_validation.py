#!/usr/bin/env python3
"""
Script de validation CI pour Arkalia-LUNA
Vérifie les points critiques sans échouer sur les erreurs mineures
"""

import importlib
import subprocess
import sys
from pathlib import Path

from core.ark_logger import ark_logger


def run_command(cmd: list[str], description: str) -> bool:
    """Exécute une commande et retourne le succès"""
    ark_logger.info(f"🔍 {description}...", extra={"arkalia_module": "scripts"})
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            ark_logger.info(f"✅ {description} - SUCCÈS", extra={"arkalia_module": "scripts"})
            return True
        else:
            ark_logger.info(f"❌ {description} - ÉCHEC", extra={"arkalia_module": "scripts"})
            if result.stderr:
                ark_logger.info(f"Erreur: {result.stderr}", extra={"arkalia_module": "scripts"})
            return False
    except subprocess.TimeoutExpired:
        ark_logger.info(f"⏰ {description} - TIMEOUT", extra={"arkalia_module": "scripts"})
        return False
    except Exception as e:
        ark_logger.info(f"💥 {description} - ERREUR: {e}", extra={"arkalia_module": "scripts"})
        return False


def check_imports() -> bool:
    """Vérifie que les imports principaux fonctionnent"""
    ark_logger.info(
        "🔍 Vérification des imports principaux...", extra={"arkalia_module": "scripts"}
    )

    test_modules = [
        "modules.zeroia.core",
        "modules.reflexia.core",
        "modules.assistantia.core",
        "modules.helloria.core",
        "modules.security.core",
    ]

    for module_name in test_modules:
        try:
            importlib.import_module(module_name)
            ark_logger.info(f"✅ import {module_name}", extra={"arkalia_module": "scripts"})
        except Exception as e:
            ark_logger.info(f"❌ import {module_name} - {e}", extra={"arkalia_module": "scripts"})
            return False

    return True


def check_config_files() -> bool:
    """Vérifie que les fichiers de configuration existent"""
    ark_logger.info(
        "🔍 Vérification des fichiers de configuration...", extra={"arkalia_module": "scripts"}
    )

    required_files = [
        "pyproject.toml",
        "requirements.txt",
        ".pre-commit-config.yaml",
        "mkdocs.yml",
        ".github/workflows/ci.yml",
        ".github/workflows/docs.yml",
    ]

    for file_path in required_files:
        if Path(file_path).exists():
            ark_logger.info(f"✅ {file_path}", extra={"arkalia_module": "scripts"})
        else:
            ark_logger.info(f"❌ {file_path} - MANQUANT", extra={"arkalia_module": "scripts"})
            return False

    return True


def check_test_structure() -> bool:
    """Vérifie la structure des tests"""
    ark_logger.info(
        "🔍 Vérification de la structure des tests...", extra={"arkalia_module": "scripts"}
    )

    test_dirs = [
        "tests/unit",
        "tests/integration",
        "tests/security",
        "tests/performance",
        "tests/chaos",
    ]

    for test_dir in test_dirs:
        if Path(test_dir).exists():
            test_files = list(Path(test_dir).rglob("test_*.py"))
            if test_files:
                ark_logger.info(
                    f"✅ {test_dir} ({len(test_files)} fichiers)",
                    extra={"arkalia_module": "scripts"},
                )
            else:
                ark_logger.info(
                    f"⚠️ {test_dir} - Aucun test trouvé", extra={"arkalia_module": "scripts"}
                )
        else:
            ark_logger.info(f"❌ {test_dir} - MANQUANT", extra={"arkalia_module": "scripts"})
            return False

    return True


def main() -> int:
    """Point d'entrée principal"""
    ark_logger.info("🚀 Validation CI Arkalia-LUNA", extra={"arkalia_module": "scripts"})
    ark_logger.info("=" * 50, extra={"arkalia_module": "scripts"})

    checks = [
        ("Configuration", check_config_files),
        ("Structure des tests", check_test_structure),
        ("Imports principaux", check_imports),
        ("Formatage", lambda: run_command(["black", "--check", "."], "Vérification formatage")),
        ("Linting", lambda: run_command(["ruff", "check", "."], "Vérification linting")),
        (
            "Tests unitaires",
            lambda: run_command(["pytest", "tests/unit/", "-v", "--tb=short"], "Tests unitaires"),
        ),
    ]

    results = []
    for name, check_func in checks:
        ark_logger.info(f"\n📋 {name}", extra={"arkalia_module": "scripts"})
        ark_logger.info("-" * 30, extra={"arkalia_module": "scripts"})
        success = check_func()
        results.append((name, success))

    # Rapport final
    ark_logger.info("\n" + "=" * 50, extra={"arkalia_module": "scripts"})
    ark_logger.info("📊 RAPPORT FINAL", extra={"arkalia_module": "scripts"})
    ark_logger.info("=" * 50, extra={"arkalia_module": "scripts"})

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        ark_logger.info(f"{status} {name}", extra={"arkalia_module": "scripts"})

    ark_logger.info(
        f"\n🎯 Résultat: {passed}/{total} vérifications réussies",
        extra={"arkalia_module": "scripts"},
    )

    if passed == total:
        ark_logger.info(
            "🎉 Toutes les vérifications CI sont passées !", extra={"arkalia_module": "scripts"}
        )
        return 0
    else:
        ark_logger.info("⚠️ Certaines vérifications ont échoué", extra={"arkalia_module": "scripts"})
        return 1


if __name__ == "__main__":
    sys.exit(main())

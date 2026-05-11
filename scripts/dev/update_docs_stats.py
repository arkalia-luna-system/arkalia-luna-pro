#!/usr/bin/env python3
"""
Script pour mettre à jour automatiquement les statistiques de tests
dans toute la documentation Arkalia-LUNA.
"""

import re
from pathlib import Path

from core.ark_logger import ark_logger

# Statistiques actuelles exactes
CURRENT_STATS = {
    "tests_passed": 373,
    "tests_total": 374,
    "success_rate": "99.7%",
    "coverage": "36%",
}

# Anciennes statistiques à remplacer
OLD_STATS = [
    {"passed": 375, "total": 388, "rate": "96.6%"},
    {"passed": 369, "total": 388, "rate": "95.1%"},
    {"passed": 367, "total": 388, "rate": "94.6%"},
    {"passed": 366, "total": 372, "rate": "98.4%"},
]


def update_file_stats(file_path):
    """Met à jour les statistiques dans un fichier"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Remplacer toutes les anciennes statistiques
        for old_stat in OLD_STATS:
            # Pattern pour X/Y tests PASSED (Z%)
            pattern1 = (
                f"{old_stat['passed']}/{old_stat['total']} tests PASSED \\({old_stat['rate']}\\)"
            )
            replacement1 = (
                f"{CURRENT_STATS['tests_passed']}/{CURRENT_STATS['tests_total']} "
                f"tests PASSED ({CURRENT_STATS['success_rate']})"
            )
            content = re.sub(pattern1, replacement1, content)

            # Pattern pour X/Y PASSED (Z%)
            pattern2 = f"{old_stat['passed']}/{old_stat['total']} PASSED \\({old_stat['rate']}\\)"
            replacement2 = (
                f"{CURRENT_STATS['tests_passed']}/{CURRENT_STATS['tests_total']} "
                f"tests PASSED ({CURRENT_STATS['success_rate']})"
            )
            content = re.sub(pattern2, replacement2, content)

            # Pattern pour Tests : X/Y (Z%)
            pattern3 = f"Tests : {old_stat['passed']}/{old_stat['total']} \\({old_stat['rate']}\\)"
            replacement3 = (
                f"Tests : {CURRENT_STATS['tests_passed']}/{CURRENT_STATS['tests_total']} "
                f"({CURRENT_STATS['success_rate']})"
            )
            content = re.sub(pattern3, replacement3, content)

        # Remplacer les badges de coverage
        content = re.sub(
            r"coverage-\d+\.?\d*%25", f"coverage-{CURRENT_STATS['coverage']}25", content
        )

        # Remplacer les messages génériques
        content = re.sub(
            r"fonctionne à 100%",
            f"fonctionne à {CURRENT_STATS['success_rate']}",
            content,
        )
        content = re.sub(
            r"96\.6% Tests Réussis",
            f"{CURRENT_STATS['success_rate']} Tests Réussis",
            content,
        )

        # Sauvegarder si des changements ont été faits
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            ark_logger.info(f"✅ Mis à jour : {file_path}", extra={"arkalia_module": "scripts"})
            return True
        else:
            ark_logger.info(
                f"ℹ️  Aucun changement : {file_path}", extra={"arkalia_module": "scripts"}
            )
            return False

    except Exception as e:
        raise RuntimeError(f"Erreur update docs stats: {e}") from e


def main():
    """Met à jour toutes les statistiques dans la documentation"""
    docs_dir = Path("docs")
    updated_files = 0

    ark_logger.info(
        f"🔄 Mise à jour des statistiques vers "
        f"{CURRENT_STATS['tests_passed']}/{CURRENT_STATS['tests_total']} "
        f"({CURRENT_STATS['success_rate']})",
        extra={"arkalia_module": "scripts"},
    )
    ark_logger.info(
        f"📊 Coverage : {CURRENT_STATS['coverage']}", extra={"arkalia_module": "scripts"}
    )
    ark_logger.info("")

    # Parcourir tous les fichiers .md dans docs/
    for md_file in docs_dir.rglob("*.md"):
        if update_file_stats(md_file):
            updated_files += 1

    ark_logger.info("")
    ark_logger.info(
        f"🎉 Terminé ! {updated_files} fichiers mis à jour", extra={"arkalia_module": "scripts"}
    )


if __name__ == "__main__":
    main()

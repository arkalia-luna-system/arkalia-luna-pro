#!/usr/bin/env python3
"""
Script pour corriger automatiquement les annotations de type manquantes dans les tests.
Ajoute -> None sur toutes les fonctions de test qui n'ont pas d'annotation de retour.
"""

import os
import re
import sys
from pathlib import Path

from core.ark_logger import ark_logger


def fix_file_annotations(file_path: str) -> int:
    """Corrige les annotations de type dans un fichier."""
    fixed_count = 0

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Pattern pour trouver les définitions de fonctions sans annotation de retour
    # Exclut les fonctions qui ont déjà des annotations ou des décorateurs
    pattern = r"^(\s*def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*):\s*$"

    lines = content.split("\n")
    new_lines = []

    for i, line in enumerate(lines):
        if re.match(pattern, line):
            # Vérifie si la ligne suivante n'est pas un docstring ou une annotation
            next_line_idx = i + 1
            while next_line_idx < len(lines) and lines[next_line_idx].strip() == "":
                next_line_idx += 1

            if next_line_idx < len(lines):
                next_line = lines[next_line_idx].strip()
                # Si la ligne suivante n'est pas un docstring et qu'il n'y a pas déjà une annotation
                if (
                    not next_line.startswith('"""')
                    and not next_line.startswith("'''")
                    and "->" not in line
                ):
                    # Ajoute -> None
                    new_line = line.rstrip() + " -> None:"
                    new_lines.append(new_line)
                    fixed_count += 1
                    continue

        new_lines.append(line)

    if fixed_count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        ark_logger.info(
            f"✅ {file_path}: {fixed_count} annotations ajoutées",
            extra={"arkalia_module": "scripts"},
        )

    return fixed_count


def main():
    """Fonction principale."""
    total_fixed = 0

    # Dossiers à traiter
    test_dirs = ["tests/", "scripts/", "modules/"]

    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue

        for root, _dirs, files in os.walk(test_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        fixed = fix_file_annotations(file_path)
                        total_fixed += fixed
                    except Exception as e:
                        ark_logger.info(
                            f"❌ Erreur sur {file_path}: {e}", extra={"arkalia_module": "scripts"}
                        )

    ark_logger.info(
        f"\n🎯 Total: {total_fixed} annotations ajoutées", extra={"arkalia_module": "scripts"}
    )

    if total_fixed > 0:
        ark_logger.info(
            "\n🔄 Relance Mypy pour vérifier les corrections...",
            extra={"arkalia_module": "scripts"},
        )
        os.system("mypy . --install-types --non-interactive | head -20")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🔧 Script de correction des violations ark_logger.info("") restantes
📝 Conforme cahier des charges v4.0
🔧 Version: 2.8.0
👤 Author: Athalia
📅 Created: 2025-06-27
"""

import re
import subprocess
from pathlib import Path


def fix_remaining_prints():
    """Corrige les violations ark_logger.info("") restantes"""

    # Trouver tous les fichiers avec ark_logger.info("") restants
    result = subprocess.run(
        ["grep", "-r", "print(", "--include=*.py", "."], capture_output=True, text=True
    )

    if not result.stdout.strip():
        print("✅ Aucune violation ark_logger.info(" ") restante !")
        return

    files_to_fix = {}
    for line in result.stdout.strip().split("\n"):
        if ":" in line:
            file_path, content = line.split(":", 1)
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(content.strip())

    print(f"🔧 Correction de {len(files_to_fix)} fichiers...")

    for file_path in files_to_fix:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Remplacer ark_logger.info("") vides par ark_logger.info("")
            content = re.sub(r"print\(\)", 'ark_logger.info("")', content)

            # Remplacer ark_logger.info("") par ark_logger.info("")
            content = re.sub(r'print\(""\)', 'ark_logger.info("")', content)

            # Remplacer ark_logger.info("") par ark_logger.info("")
            content = re.sub(r"print\(''\)", 'ark_logger.info("")', content)

            # Ajouter l'import si nécessaire
            if "ark_logger" in content and "from core.ark_logger import ark_logger" not in content:
                lines = content.split("\n")
                import_added = False

                for i, line in enumerate(lines):
                    if line.strip().startswith("import ") or line.strip().startswith("from "):
                        if not import_added:
                            lines.insert(i, "from core.ark_logger import ark_logger")
                            import_added = True
                            break

                if not import_added:
                    lines.insert(0, "from core.ark_logger import ark_logger")

                content = "\n".join(lines)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ Corrigé: {file_path}")

        except Exception as e:
            print(f"❌ Erreur {file_path}: {e}")


def main():
    """Fonction principale"""
    print("🔧 === CORRECTION VIOLATIONS PRINT() RESTANTES ===")
    print("   Conforme cahier des charges v4.0")
    ark_logger.info("")

    fix_remaining_prints()

    # Vérification finale
    result = subprocess.run(
        ["grep", "-r", "print(", "--include=*.py", "."], capture_output=True, text=True
    )

    remaining = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

    print("\n🔍 Vérification finale:")
    print(f"  🚨 Violations restantes: {remaining}")

    if remaining == 0:
        print("🎉 Toutes les violations ark_logger.info(" ") ont été éliminées !")
    else:
        print(f"⚠️ Il reste {remaining} violations à corriger manuellement")
        print("📋 Violations restantes:")
        for line in result.stdout.strip().split("\n")[:10]:
            print(f"  {line}")


if __name__ == "__main__":
    main()

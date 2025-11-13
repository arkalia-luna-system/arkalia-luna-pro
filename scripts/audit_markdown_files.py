#!/usr/bin/env python3
"""
Script d'audit et de correction des fichiers Markdown
Vérifie les dates, le langage professionnel, et la cohérence avec le projet
"""

import re
from datetime import datetime
from pathlib import Path

# Mots d'argot à éviter
ARGOT_WORDS = [
    "vachement",
    "d'aller",
    "daller",
    "trop",
    "pas pro",
    "pas professionnel",
    "super",
    "génial",
    "cool",
    "sympa",
]

# Dates obsolètes à remplacer
OLD_DATES = [
    r"5 juillet 2025",
    r"4 juillet 2025",
    r"juillet 2025",
    r"janvier 2025",
    r"Janvier 2025",
    r"27 Juillet 2025",
]

# Date cible
TARGET_DATE = "novembre 2025"
TARGET_DATE_FULL = "2025-11-13"

# Version actuelle
CURRENT_VERSION = "2.8.0"


def find_markdown_files(root_dir: Path) -> list[Path]:
    """Trouve tous les fichiers .md"""
    md_files = []
    exclude_dirs = {
        ".venv",
        "venv",
        "node_modules",
        ".git",
        "__pycache__",
        "htmlcov",
        "site",
        "archive",
    }

    for path in root_dir.rglob("*.md"):
        # Ignorer les fichiers macOS cachés
        if path.name.startswith("._"):
            continue
        # Ignorer les fichiers dans les dossiers exclus
        if any(excluded in path.parts for excluded in exclude_dirs):
            continue
        md_files.append(path)
    return sorted(md_files)


def check_file(file_path: Path) -> dict:
    """Analyse un fichier .md et retourne les problèmes trouvés"""
    issues = {"old_dates": [], "argot": [], "wrong_version": [], "lines": []}

    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Vérifier les dates obsolètes
            for old_date in OLD_DATES:
                if re.search(old_date, line, re.IGNORECASE):
                    issues["old_dates"].append((i, line.strip()))

            # Vérifier l'argot
            for argot in ARGOT_WORDS:
                if argot.lower() in line.lower():
                    issues["argot"].append((i, line.strip()))

            # Vérifier la version (si mentionnée)
            if "v2.9.0" in line or "v3.0" in line or "v3.x" in line:
                if CURRENT_VERSION not in line:
                    issues["wrong_version"].append((i, line.strip()))

        return issues
    except Exception as e:
        print(f"Erreur lecture {file_path}: {e}")
        return issues


def fix_file(file_path: Path) -> bool:
    """Corrige un fichier .md"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # Remplacer les dates obsolètes
        for old_date in OLD_DATES:
            content = re.sub(old_date, TARGET_DATE, content, flags=re.IGNORECASE)

        # Remplacer v2.9.0 par v2.8.0 si c'est une référence incorrecte
        # (mais garder v2.9.0 si c'est dans un contexte de roadmap future)
        if (
            "v2.9.0" in content
            and "roadmap" not in content.lower()
            and "futur" not in content.lower()
        ):
            content = re.sub(r"v2\.9\.0", CURRENT_VERSION, content)

        # Remplacer v3.x par v2.8.0 si c'est une référence incorrecte
        if (
            "v3.x" in content
            and "roadmap" not in content.lower()
            and "futur" not in content.lower()
        ):
            content = re.sub(r"v3\.x", CURRENT_VERSION, content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Erreur correction {file_path}: {e}")
        return False


def main():
    """Fonction principale"""
    root_dir = Path(__file__).parent.parent
    md_files = find_markdown_files(root_dir)

    print(f"📋 Analyse de {len(md_files)} fichiers Markdown...\n")

    total_issues = {"old_dates": 0, "argot": 0, "wrong_version": 0, "fixed": 0}

    files_with_issues = []

    for md_file in md_files:
        issues = check_file(md_file)

        if any(issues.values()):
            files_with_issues.append((md_file, issues))
            total_issues["old_dates"] += len(issues["old_dates"])
            total_issues["argot"] += len(issues["argot"])
            total_issues["wrong_version"] += len(issues["wrong_version"])

    # Afficher les résultats
    if files_with_issues:
        print("⚠️  Fichiers avec problèmes:\n")
        for file_path, issues in files_with_issues:
            print(f"📄 {file_path.relative_to(root_dir)}")
            if issues["old_dates"]:
                print(f"   📅 Dates obsolètes: {len(issues['old_dates'])}")
            if issues["argot"]:
                print(f"   💬 Langage non professionnel: {len(issues['argot'])}")
            if issues["wrong_version"]:
                print(f"   🔢 Version incorrecte: {len(issues['wrong_version'])}")
            print()
    else:
        print("✅ Aucun problème détecté!\n")

    # Corriger les fichiers
    print("🔧 Correction des fichiers...\n")
    for md_file in md_files:
        if fix_file(md_file):
            total_issues["fixed"] += 1
            print(f"✅ Corrigé: {md_file.relative_to(root_dir)}")

    print("\n📊 Résumé:")
    print(f"   - Dates obsolètes trouvées: {total_issues['old_dates']}")
    print(f"   - Langage non professionnel: {total_issues['argot']}")
    print(f"   - Versions incorrectes: {total_issues['wrong_version']}")
    print(f"   - Fichiers corrigés: {total_issues['fixed']}")


if __name__ == "__main__":
    main()

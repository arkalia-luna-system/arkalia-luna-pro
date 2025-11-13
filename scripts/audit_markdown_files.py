#!/usr/bin/env python3
"""
Script d'audit et de correction des fichiers Markdown
Vérifie les dates, le langage professionnel, et la cohérence avec le projet
"""

import re
from pathlib import Path

# Mots d'argot à éviter
ARGOT_WORDS = [
    "vachement",
    "d'aller",
    "daller",
    "pas pro",
    "pas professionnel",
    "super",
    "génial",
    "cool",
    "sympa",
]

# Outils/services obsolètes à supprimer ou remplacer
OBSOLETE_SERVICES = [
    r"notion",
    r"Notion",
    r"NOTION",
    r"slack",
    r"Slack",
    r"SLACK",
    r"trello",
    r"jira",
    r"confluence",
    r"atlassian",
]

# Ports obsolètes à vérifier
OBSOLETE_PORTS = [
    r":9000",
    r"port 9000",
    r"localhost:9000",
    r":8081",
    r"port 8081",
    r"localhost:8081",
    r":5173",
    r"port 5173",
    r"localhost:5173",
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


def check_file(file_path: Path) -> dict[str, list]:
    """Analyse un fichier .md et retourne les problèmes trouvés"""
    issues: dict[str, list] = {
        "old_dates": [],
        "argot": [],
        "wrong_version": [],
        "obsolete_services": [],
        "obsolete_ports": [],
        "lines": [],
    }

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

            # Vérifier les services obsolètes
            for service in OBSOLETE_SERVICES:
                if re.search(service, line, re.IGNORECASE):
                    issues["obsolete_services"].append((i, line.strip()))

            # Vérifier les ports obsolètes
            for port in OBSOLETE_PORTS:
                if re.search(port, line, re.IGNORECASE):
                    issues["obsolete_ports"].append((i, line.strip()))

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

        # Supprimer les références aux services obsolètes (Notion, Slack, etc.)
        lines = content.split("\n")
        new_lines = []

        for line in lines:
            # Pour Notion, supprimer ou remplacer
            if re.search(r"\bnotion\b", line, re.IGNORECASE):
                line_lower = line.lower()
                # Si la ligne ne contient que la référence à Notion, la supprimer
                if (
                    len(line.strip()) < 100
                    and "http" not in line_lower
                    and line.strip().count("notion") == 1
                ):
                    continue  # Supprimer cette ligne
                else:
                    # Remplacer la référence par "documentation"
                    line = re.sub(
                        r"\bnotion\b",
                        "documentation",
                        line,
                        flags=re.IGNORECASE,
                    )

            # Pour Slack, remplacer par "notifications" ou "alertes"
            if re.search(r"\bslack\b", line, re.IGNORECASE):
                # Dans un contexte d'alertes, remplacer par "alertes"
                if "alerte" in line.lower() or "notification" in line.lower():
                    line = re.sub(
                        r"\bslack\b",
                        "alertes",
                        line,
                        flags=re.IGNORECASE,
                    )
                else:
                    line = re.sub(
                        r"\bslack\b",
                        "notifications",
                        line,
                        flags=re.IGNORECASE,
                    )

            # Pour les autres services obsolètes (Trello, Jira, etc.), supprimer les lignes simples
            for service in ["trello", "jira", "confluence", "atlassian"]:
                if re.search(rf"\b{service}\b", line, re.IGNORECASE):
                    if len(line.strip()) < 80 and line.strip().count(service) == 1:
                        continue  # Supprimer cette ligne

            # Toujours ajouter la ligne (modifiée ou non)
            new_lines.append(line)

        content = "\n".join(new_lines)

        # Supprimer les références aux ports obsolètes (9000, 8081, 5173)
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            should_skip = False
            for port_pattern in OBSOLETE_PORTS:
                if re.search(port_pattern, line, re.IGNORECASE):
                    # Si c'est une ligne de lien HTML ou référence, la supprimer
                    if (
                        "http://localhost" in line
                        or "href" in line.lower()
                        or "<a" in line.lower()
                        or "port" in line.lower()
                    ):
                        # Vérifier si c'est une ligne complète de lien
                        if (
                            line.strip().startswith("<a")
                            or line.strip().startswith("http://localhost")
                            or (line.strip().startswith("-") and "port" in line.lower())
                        ):
                            should_skip = True
                            break
            if not should_skip:
                new_lines.append(line)
        content = "\n".join(new_lines)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Erreur correction {file_path}: {e}")
        return False


def main() -> None:
    """Fonction principale"""
    root_dir = Path(__file__).parent.parent
    md_files = find_markdown_files(root_dir)

    print(f"📋 Analyse de {len(md_files)} fichiers Markdown...\n")

    total_issues = {
        "old_dates": 0,
        "argot": 0,
        "wrong_version": 0,
        "obsolete_services": 0,
        "obsolete_ports": 0,
        "fixed": 0,
    }

    files_with_issues = []

    for md_file in md_files:
        issues = check_file(md_file)

        if any(issues.values()):
            files_with_issues.append((md_file, issues))
            total_issues["old_dates"] += len(issues["old_dates"])
            total_issues["argot"] += len(issues["argot"])
            total_issues["wrong_version"] += len(issues["wrong_version"])
            total_issues["obsolete_services"] += len(issues["obsolete_services"])
            total_issues["obsolete_ports"] += len(issues["obsolete_ports"])

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
            if issues["obsolete_services"]:
                print(f"   🔌 Services obsolètes: {len(issues['obsolete_services'])}")
            if issues["obsolete_ports"]:
                print(f"   🔌 Ports obsolètes: {len(issues['obsolete_ports'])}")
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
    print(f"   - Services obsolètes: {total_issues['obsolete_services']}")
    print(f"   - Ports obsolètes: {total_issues['obsolete_ports']}")
    print(f"   - Fichiers corrigés: {total_issues['fixed']}")


if __name__ == "__main__":
    main()

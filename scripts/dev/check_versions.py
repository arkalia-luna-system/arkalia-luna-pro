#!/usr/bin/env python3
"""
🔍 Script de vérification de cohérence des versions
📝 Vérifie que les versions sont cohérentes dans tous les fichiers de config
🔧 Version: 2.8.0
👤 Author: Athalia
📅 Created: 2025-01-27
"""

import re
import sys
from pathlib import Path

import toml


def extract_version_from_file(file_path: Path) -> str | None:
    """Extrait la version d'un fichier."""
    try:
        if file_path.suffix == ".toml":
            data = toml.load(file_path)
            # Chercher dans différents chemins possibles
            version = (
                data.get("project", {}).get("version")
                or data.get("tool", {}).get("poetry", {}).get("version")
                or data.get("bumpver", {}).get("current_version")
                or data.get("version")
            )
            return str(version) if version else None
        elif file_path.name == "requirements.txt":
            # Chercher une ligne avec arkalia-luna-pro ou version commentée
            content = file_path.read_text()
            for line in content.split("\n"):
                if "arkalia-luna-pro" in line and "==" in line:
                    match = re.search(r"==([0-9]+\.[0-9]+\.[0-9]+)", line)
                    return match.group(1) if match else None
                # Chercher dans les commentaires de version
                if "Version:" in line:
                    match = re.search(r"Version:\s*([0-9]+\.[0-9]+\.[0-9]+)", line)
                    return match.group(1) if match else None
        elif file_path.name == "version.toml":
            data = toml.load(file_path)
            return str(data.get("bumpver", {}).get("current_version", ""))
    except Exception as e:
        print(f"⚠️ Erreur lecture {file_path}: {e}")
    return None


def check_versions() -> bool:
    """Vérifie la cohérence des versions."""
    print("🔍 Vérification de cohérence des versions...")

    # Fichiers à vérifier
    version_files = [Path("pyproject.toml"), Path("version.toml"), Path("requirements.txt")]

    versions = {}
    for file_path in version_files:
        if file_path.exists():
            version = extract_version_from_file(file_path)
            if version:
                versions[file_path.name] = version
                print(f"✅ {file_path.name}: {version}")
            else:
                print(f"⚠️ {file_path.name}: version non trouvée")
        else:
            print(f"⚠️ {file_path.name}: fichier non trouvé")

    if not versions:
        print("❌ Aucune version trouvée")
        return False

    # Vérifier la cohérence
    unique_versions = set(versions.values())
    if len(unique_versions) == 1:
        print(f"✅ Toutes les versions sont cohérentes: {list(unique_versions)[0]}")
        return True
    else:
        print("❌ Versions incohérentes:")
        for file_name, version in versions.items():
            print(f"   {file_name}: {version}")
        return False


def main() -> None:
    """Fonction principale."""
    success = check_versions()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

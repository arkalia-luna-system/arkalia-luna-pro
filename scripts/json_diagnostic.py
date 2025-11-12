#!/usr/bin/env python3
"""
🔍 Diagnostic des fichiers JSON - Arkalia Luna Pro
Analyse tous les fichiers JSON pour identifier les zones problématiques
"""

import csv
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class JSONDiagnostic:
    """Diagnostic des fichiers JSON du projet.

    Attributes:
        root_path: Chemin racine du projet.
        json_files: Liste des fichiers JSON trouvés.
        analysis: Résultats de l'analyse.
    """

    def __init__(self, root_path: str = "."):
        """Initialise le diagnostic JSON.

        Args:
            root_path: Chemin racine du projet (défaut: ".").
        """
        self.root_path = Path(root_path)
        self.json_files: list[dict] = []
        self.analysis: dict[str, Any] = {
            "summary": {},
            "by_size": [],
            "by_directory": defaultdict(list),
            "by_type": defaultdict(list),
            "large_files": [],
            "cache_files": [],
            "data_files": [],
            "config_files": [],
            "report_files": [],
        }

    def scan_json_files(self):
        """Scanne tous les fichiers JSON du projet"""
        print("🔍 Scan des fichiers JSON en cours...")

        for file_path in self.root_path.rglob("*.json"):
            try:
                stat = file_path.stat()
                size = stat.st_size

                file_info = {
                    "path": str(file_path.relative_to(self.root_path)),
                    "size": size,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "directory": str(file_path.parent.relative_to(self.root_path)),
                    "filename": file_path.name,
                    "is_large": size > 1024 * 1024,  # > 1MB
                    "is_cache": self._is_cache_file(file_path),
                    "is_data": self._is_data_file(file_path),
                    "is_config": self._is_config_file(file_path),
                    "is_report": self._is_report_file(file_path),
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                }

                self.json_files.append(file_info)

                # Classer par taille
                if file_info["is_large"]:
                    self.analysis["large_files"].append(file_info)

                # Classer par type
                if file_info["is_cache"]:
                    self.analysis["cache_files"].append(file_info)
                elif file_info["is_data"]:
                    self.analysis["data_files"].append(file_info)
                elif file_info["is_config"]:
                    self.analysis["config_files"].append(file_info)
                elif file_info["is_report"]:
                    self.analysis["report_files"].append(file_info)

                # Classer par répertoire
                self.analysis["by_directory"][file_info["directory"]].append(file_info)

            except Exception as e:
                print(f"⚠️ Erreur sur {file_path}: {e}")

        # Trier par taille
        self.analysis["by_size"] = sorted(self.json_files, key=lambda x: x["size"], reverse=True)

        # Résumé
        total_size = sum(f["size"] for f in self.json_files)
        self.analysis["summary"] = {
            "total_files": len(self.json_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "large_files": len(self.analysis["large_files"]),
            "cache_files": len(self.analysis["cache_files"]),
            "data_files": len(self.analysis["data_files"]),
            "config_files": len(self.analysis["config_files"]),
            "report_files": len(self.analysis["report_files"]),
        }

    def _is_cache_file(self, file_path: Path) -> bool:
        """Détecte les fichiers de cache"""
        cache_patterns = [
            r"\.cache",
            r"cache",
            r"\.pytest_cache",
            r"\.mypy_cache",
            r"\.ruff_cache",
            r"__pycache__",
            r"\.data\.json$",
            r"\.meta\.json$",
            r"coverage",
            r"\.coverage",
        ]
        return any(re.search(pattern, str(file_path)) for pattern in cache_patterns)

    def _is_data_file(self, file_path: Path) -> bool:
        """Détecte les fichiers de données"""
        data_patterns = [
            r"data",
            r"state",
            r"snapshot",
            r"metrics",
            r"results",
            r"output",
            r"export",
        ]
        return any(re.search(pattern, str(file_path)) for pattern in data_patterns)

    def _is_config_file(self, file_path: Path) -> bool:
        """Détecte les fichiers de configuration"""
        config_patterns = [
            r"config",
            r"settings",
            r"\.schema\.json$",
            r"package\.json",
            r"tsconfig",
            r"\.eslintrc",
            r"\.prettierrc",
        ]
        return any(re.search(pattern, str(file_path)) for pattern in config_patterns)

    def _is_report_file(self, file_path: Path) -> bool:
        """Détecte les fichiers de rapport"""
        report_patterns = [
            r"report",
            r"audit",
            r"analysis",
            r"bandit",
            r"coverage",
            r"test.*results",
            r"benchmark",
        ]
        return any(re.search(pattern, str(file_path)) for pattern in report_patterns)

    def generate_report(self, output_file: str = "json_diagnostic_report.md"):
        """Génère un rapport markdown"""
        self.scan_json_files()

        report = f"""# 📊 DIAGNOSTIC FICHIERS JSON - Arkalia Luna Pro

**Date d'analyse :** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Racine analysée :** {self.root_path.absolute()}

## 📈 RÉSUMÉ GLOBAL

- **Total fichiers JSON :** {self.analysis["summary"]["total_files"]}
- **Taille totale :** {self.analysis["summary"]["total_size_mb"]} MB
- **Fichiers volumineux (>1MB) :** {self.analysis["summary"]["large_files"]}
- **Fichiers de cache :** {self.analysis["summary"]["cache_files"]}
- **Fichiers de données :** {self.analysis["summary"]["data_files"]}
- **Fichiers de config :** {self.analysis["summary"]["config_files"]}
- **Fichiers de rapport :** {self.analysis["summary"]["report_files"]}

## 🚨 FICHIERS VOLUMINEUX (>1MB)

"""

        for file in self.analysis["large_files"][:20]:  # Top 20
            report += f"- `{file['path']}` ({file['size_mb']} MB) - {file['modified']}\n"

        report += "\n## 📁 RÉPARTITION PAR RÉPERTOIRE\n\n"

        # Top 10 répertoires avec le plus de fichiers JSON
        dir_counts = {k: len(v) for k, v in self.analysis["by_directory"].items()}
        top_dirs = sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        for directory, count in top_dirs:
            total_size = sum(f["size_mb"] for f in self.analysis["by_directory"][directory])
            report += f"- **{directory}** : {count} fichiers ({total_size:.2f} MB)\n"

        report += "\n## 🗂️ DÉTAIL PAR TYPE\n\n"

        report += "### 🧹 Fichiers de cache\n"
        for file in self.analysis["cache_files"][:10]:
            report += f"- `{file['path']}` ({file['size_mb']} MB)\n"

        report += "\n### 📊 Fichiers de données\n"
        for file in self.analysis["data_files"][:10]:
            report += f"- `{file['path']}` ({file['size_mb']} MB)\n"

        report += "\n### ⚙️ Fichiers de configuration\n"
        for file in self.analysis["config_files"][:10]:
            report += f"- `{file['path']}` ({file['size_mb']} MB)\n"

        report += "\n### 📋 Fichiers de rapport\n"
        for file in self.analysis["report_files"][:10]:
            report += f"- `{file['path']}` ({file['size_mb']} MB)\n"

        # Recommandations
        report += """## 🎯 RECOMMANDATIONS

### 🚨 Actions immédiates :
"""

        if self.analysis["summary"]["cache_files"] > 1000:
            report += "- **Nettoyer les caches** : Supprimer `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`\n"

        if self.analysis["summary"]["large_files"] > 10:
            report += (
                "- **Archiver les gros fichiers** : Déplacer les fichiers > 1MB dans `archive/`\n"
            )

        if self.analysis["summary"]["total_files"] > 10000:
            report += "- **Optimiser Git** : Ajouter `*.json` au `.gitignore` sauf les configs importantes\n"

        report += """### 🔄 Actions à moyen terme :
- Mettre en place une rotation automatique des rapports
- Créer un système d'archivage automatique
- Optimiser la génération de métadonnées

### 📊 Métriques à surveiller :
- Nombre total de fichiers JSON
- Taille totale des fichiers JSON
- Fichiers volumineux
- Répartition par répertoire

---
*Rapport généré automatiquement par JSONDiagnostic*
"""

        # Sauvegarder le rapport
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ Rapport généré : {output_file}")
        return output_file

    def generate_csv(self, output_file: str = "json_files.csv"):
        """Génère un fichier CSV avec tous les fichiers JSON"""
        self.scan_json_files()

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["path", "size_mb", "directory", "filename", "type", "modified"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for file_info in self.analysis["by_size"]:
                # Déterminer le type
                if file_info["is_cache"]:
                    file_type = "cache"
                elif file_info["is_data"]:
                    file_type = "data"
                elif file_info["is_config"]:
                    file_type = "config"
                elif file_info["is_report"]:
                    file_type = "report"
                else:
                    file_type = "other"

                writer.writerow(
                    {
                        "path": file_info["path"],
                        "size_mb": file_info["size_mb"],
                        "directory": file_info["directory"],
                        "filename": file_info["filename"],
                        "type": file_type,
                        "modified": file_info["modified"],
                    }
                )

        print(f"✅ CSV généré : {output_file}")
        return output_file


def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Diagnostic des fichiers JSON Arkalia Luna Pro")
    parser.add_argument("--root", default=".", help="Racine du projet à analyser")
    parser.add_argument("--output", default="json_diagnostic_report.md", help="Fichier de sortie")
    parser.add_argument("--csv", action="store_true", help="Générer aussi un fichier CSV")
    parser.add_argument("--verbose", action="store_true", help="Mode verbeux")

    args = parser.parse_args()

    diagnostic = JSONDiagnostic(args.root)

    if args.verbose:
        print("🔍 Démarrage du diagnostic JSON...")

    # Générer le rapport markdown
    markdown_file = diagnostic.generate_report(args.output)

    # Générer le CSV si demandé
    if args.csv:
        csv_file = diagnostic.generate_csv()
        print(f"📊 Rapports générés : {markdown_file} et {csv_file}")
    else:
        print(f"📊 Rapport généré : {markdown_file}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🔍 Analyseur de Structure Arkalia Luna Pro
Génère un rapport détaillé de la structure du projet
"""

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class StructureAnalyzer:
    """Analyseur de structure du projet.

    Attributes:
        root_path: Chemin racine du projet.
        analysis: Résultats de l'analyse.
    """

    def __init__(self, root_path: str = "."):
        """Initialise l'analyseur de structure.

        Args:
            root_path: Chemin racine du projet (défaut: ".").
        """
        self.root_path = Path(root_path)
        self.analysis: dict[str, Any] = {
            "summary": {},
            "files_by_type": defaultdict(list),
            "files_by_size": defaultdict(list),
            "potential_issues": [],
            "duplicates": [],
            "empty_files": [],
            "large_files": [],
            "backup_files": [],
            "log_files": [],
            "test_files": [],
            "config_files": [],
            "docker_files": [],
            "documentation_files": [],
            "python_modules": [],
            "scripts": [],
            "structure_tree": {},
        }

    def analyze_file(self, file_path: Path) -> dict:
        """Analyse un fichier individuel"""
        try:
            stat = file_path.stat()
            size = stat.st_size

            file_info = {
                "path": str(file_path.relative_to(self.root_path)),
                "size": size,
                "size_mb": round(size / (1024 * 1024), 2),
                "extension": file_path.suffix,
                "is_empty": size == 0,
                "is_large": size > 1024 * 1024,  # > 1MB
                "is_backup": self._is_backup_file(file_path),
                "is_log": self._is_log_file(file_path),
                "is_test": self._is_test_file(file_path),
                "is_config": self._is_config_file(file_path),
                "is_docker": self._is_docker_file(file_path),
                "is_documentation": self._is_documentation_file(file_path),
                "is_python": file_path.suffix == ".py",
                "is_script": self._is_script_file(file_path),
            }

            return file_info
        except Exception as e:
            return {"path": str(file_path), "error": str(e)}

    def _is_backup_file(self, file_path: Path) -> bool:
        """Détecte les fichiers de backup"""
        backup_patterns = [
            r"\.backup\.",
            r"\.bak$",
            r"\.old$",
            r"\.tmp$",
            r"\.swp$",
            r"\.orig$",
            r"backup_",
            r"_backup",
        ]
        return any(re.search(pattern, file_path.name) for pattern in backup_patterns)

    def _is_log_file(self, file_path: Path) -> bool:
        """Détecte les fichiers de logs"""
        log_patterns = [r"\.log$", r"_log\.", r"log_", r"\.out$", r"\.err$"]
        return any(re.search(pattern, file_path.name) for pattern in log_patterns)

    def _is_test_file(self, file_path: Path) -> bool:
        """Détecte les fichiers de tests"""
        test_patterns = [r"test_", r"_test\.", r"\.test\.", r"tests/", r"/test"]
        return any(re.search(pattern, str(file_path)) for pattern in test_patterns)

    def _is_config_file(self, file_path: Path) -> bool:
        """Détecte les fichiers de configuration"""
        config_extensions = [".toml", ".yml", ".yaml", ".json", ".ini", ".cfg", ".conf"]
        config_patterns = [
            r"config",
            r"settings",
            r"\.env",
            r"requirements",
            r"pyproject",
            r"pytest",
            r"mkdocs",
        ]
        return file_path.suffix in config_extensions or any(
            re.search(pattern, file_path.name) for pattern in config_patterns
        )

    def _is_docker_file(self, file_path: Path) -> bool:
        """Détecte les fichiers Docker"""
        docker_patterns = [r"Dockerfile", r"docker-compose", r"\.dockerfile"]
        return any(re.search(pattern, file_path.name) for pattern in docker_patterns)

    def _is_documentation_file(self, file_path: Path) -> bool:
        """Détecte les fichiers de documentation"""
        doc_extensions = [".md", ".rst", ".txt", ".html"]
        doc_patterns = [
            r"README",
            r"CHANGELOG",
            r"LICENSE",
            r"CONTRIBUTING",
            r"ARCHITECTURE",
            r"PLAN_",
            r"RAPPORT_",
            r"BILAN_",
            r"CI_",
            r"WORKFLOW_",
        ]
        return file_path.suffix in doc_extensions or any(
            re.search(pattern, file_path.name) for pattern in doc_patterns
        )

    def _is_script_file(self, file_path: Path) -> bool:
        """Détecte les fichiers de scripts"""
        script_patterns = [
            r"\.sh$",
            r"\.py$",
            r"\.js$",
            r"\.ts$",
            r"run_",
            r"script",
            r"ark-",
            r"install_",
            r"fix_",
            r"demo_",
        ]
        return any(re.search(pattern, file_path.name) for pattern in script_patterns)

    def find_duplicates(self, files_info: list) -> list:
        """Trouve les fichiers en double"""
        duplicates = []
        file_names = defaultdict(list)

        for file_info in files_info:
            if "error" not in file_info:
                file_names[file_info["path"].split("/")[-1]].append(file_info)

        for name, files in file_names.items():
            if len(files) > 1:
                duplicates.append({"name": name, "files": files})

        return duplicates

    def analyze_structure(self) -> dict[str, Any]:
        """Analyse complète de la structure"""
        print("🔍 Analyse de la structure en cours...")

        all_files: list[dict[str, Any]] = []
        total_size = 0
        file_count = 0

        # Parcourir tous les fichiers
        for file_path in self.root_path.rglob("*"):
            if file_path.is_file():
                # Ignorer les fichiers système
                if any(
                    part.startswith(".")
                    and part not in [".py", ".md", ".yml", ".yaml", ".toml", ".json"]
                    for part in file_path.parts
                ):
                    continue

                file_info = self.analyze_file(file_path)
                if "error" not in file_info:
                    all_files.append(file_info)
                    total_size += file_info["size"]
                    file_count += 1

                    # Classer par type
                    if file_info["is_empty"]:
                        self.analysis["empty_files"].append(file_info)
                    if file_info["is_large"]:
                        self.analysis["large_files"].append(file_info)
                    if file_info["is_backup"]:
                        self.analysis["backup_files"].append(file_info)
                    if file_info["is_log"]:
                        self.analysis["log_files"].append(file_info)
                    if file_info["is_test"]:
                        self.analysis["test_files"].append(file_info)
                    if file_info["is_config"]:
                        self.analysis["config_files"].append(file_info)
                    if file_info["is_docker"]:
                        self.analysis["docker_files"].append(file_info)
                    if file_info["is_documentation"]:
                        self.analysis["documentation_files"].append(file_info)
                    if file_info["is_python"]:
                        self.analysis["python_modules"].append(file_info)
                    if file_info["is_script"]:
                        self.analysis["scripts"].append(file_info)

        # Résumé
        self.analysis["summary"] = {
            "total_files": file_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "empty_files": len(self.analysis["empty_files"]),
            "large_files": len(self.analysis["large_files"]),
            "backup_files": len(self.analysis["backup_files"]),
            "log_files": len(self.analysis["log_files"]),
            "test_files": len(self.analysis["test_files"]),
            "config_files": len(self.analysis["config_files"]),
            "docker_files": len(self.analysis["docker_files"]),
            "documentation_files": len(self.analysis["documentation_files"]),
            "python_modules": len(self.analysis["python_modules"]),
            "scripts": len(self.analysis["scripts"]),
        }

        # Trouver les doublons
        self.analysis["duplicates"] = self.find_duplicates(all_files)

        # Identifier les problèmes potentiels
        self._identify_potential_issues()

        return self.analysis

    def _identify_potential_issues(self):
        """Identifie les problèmes potentiels"""
        issues: list[dict] = []

        # Fichiers volumineux
        large_files = [f for f in self.analysis["large_files"] if f["size_mb"] > 5]
        if large_files:
            issues.append(
                {
                    "type": "large_files",
                    "description": f"{len(large_files)} fichiers > 5MB détectés",
                    "files": large_files,
                }
            )

        # Fichiers de backup
        if self.analysis["backup_files"]:
            issues.append(
                {
                    "type": "backup_files",
                    "description": f"{len(self.analysis['backup_files'])} fichiers de backup détectés",
                    "files": self.analysis["backup_files"],
                }
            )

        # Fichiers vides
        if self.analysis["empty_files"]:
            issues.append(
                {
                    "type": "empty_files",
                    "description": f"{len(self.analysis['empty_files'])} fichiers vides détectés",
                    "files": self.analysis["empty_files"],
                }
            )

        # Doublons
        if self.analysis["duplicates"]:
            issues.append(
                {
                    "type": "duplicates",
                    "description": f"{len(self.analysis['duplicates'])} noms de fichiers en double",
                    "files": self.analysis["duplicates"],
                }
            )

        self.analysis["potential_issues"] = issues

    def generate_report(self, output_file: str = "structure_analysis_report.md"):
        """Génère un rapport markdown"""
        analysis = self.analyze_structure()

        report = f"""# 📊 RAPPORT D'ANALYSE DE STRUCTURE - Arkalia Luna Pro

**Date d'analyse :** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Racine analysée :** {self.root_path.absolute()}

## 📈 RÉSUMÉ GLOBAL

- **Total fichiers :** {analysis["summary"]["total_files"]}
- **Taille totale :** {analysis["summary"]["total_size_mb"]} MB
- **Fichiers Python :** {analysis["summary"]["python_modules"]}
- **Scripts :** {analysis["summary"]["scripts"]}
- **Tests :** {analysis["summary"]["test_files"]}
- **Configuration :** {analysis["summary"]["config_files"]}
- **Documentation :** {analysis["summary"]["documentation_files"]}
- **Docker :** {analysis["summary"]["docker_files"]}

## ⚠️ PROBLÈMES POTENTIELS

"""

        for issue in analysis["potential_issues"]:
            report += f"### {issue['type'].upper()}\n"
            report += f"{issue['description']}\n\n"

            if issue["type"] == "large_files":
                for file in issue["files"][:10]:  # Limiter à 10
                    report += f"- `{file['path']}` ({file['size_mb']} MB)\n"
            elif issue["type"] == "duplicates":
                for dup in issue["files"][:5]:  # Limiter à 5
                    report += f"- **{dup['name']}** :\n"
                    for file in dup["files"]:
                        report += f"  - `{file['path']}`\n"
            else:
                for file in issue["files"][:10]:  # Limiter à 10
                    report += f"- `{file['path']}`\n"

            report += "\n"

        # Détail par catégorie
        report += """## 📁 DÉTAIL PAR CATÉGORIE

### 🐍 Modules Python
"""
        for file in analysis["python_modules"][:20]:  # Limiter à 20
            report += f"- `{file['path']}` ({file['size_mb']} MB)\n"

        report += "\n### 🔧 Scripts\n"
        for file in analysis["scripts"][:20]:  # Limiter à 20
            report += f"- `{file['path']}` ({file['size_mb']} MB)\n"

        report += "\n### 🧪 Tests\n"
        for file in analysis["test_files"][:20]:  # Limiter à 20
            report += f"- `{file['path']}` ({file['size_mb']} MB)\n"

        report += "\n### ⚙️ Configuration\n"
        for file in analysis["config_files"][:20]:  # Limiter à 20
            report += f"- `{file['path']}` ({file['size_mb']} MB)\n"

        report += "\n### 🐳 Docker\n"
        for file in analysis["docker_files"]:
            report += f"- `{file['path']}` ({file['size_mb']} MB)\n"

        report += "\n### 📚 Documentation\n"
        for file in analysis["documentation_files"][:20]:  # Limiter à 20
            report += f"- `{file['path']}` ({file['size_mb']} MB)\n"

        # Recommandations
        report += """## 🎯 RECOMMANDATIONS

### 🚨 Actions immédiates :
"""

        if analysis["potential_issues"]:
            for issue in analysis["potential_issues"]:
                if issue["type"] == "large_files":
                    report += "- **Nettoyer les fichiers volumineux** (> 5MB)\n"
                elif issue["type"] == "backup_files":
                    report += "- **Supprimer les fichiers de backup** automatiques\n"
                elif issue["type"] == "empty_files":
                    report += "- **Vérifier les fichiers vides** et les supprimer si inutiles\n"
                elif issue["type"] == "duplicates":
                    report += "- **Consolider les fichiers en double**\n"

        report += """### 🔄 Actions à moyen terme :
- Organiser les scripts par catégorie
- Standardiser les configurations
- Mettre en place une rotation des logs
- Créer une structure de dossiers plus claire

### 📊 Métriques à surveiller :
- Taille totale du projet
- Nombre de fichiers par catégorie
- Fichiers volumineux
- Doublons

---
*Rapport généré automatiquement par StructureAnalyzer*
"""

        # Sauvegarder le rapport
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ Rapport généré : {output_file}")
        return output_file

    def generate_json_report(self, output_file: str = "structure_analysis.json"):
        """Génère un rapport JSON détaillé"""
        analysis = self.analyze_structure()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"✅ Rapport JSON généré : {output_file}")
        return output_file


def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyseur de structure Arkalia Luna Pro")
    parser.add_argument("--root", default=".", help="Racine du projet à analyser")
    parser.add_argument(
        "--output", default="structure_analysis_report.md", help="Fichier de sortie"
    )
    parser.add_argument("--json", action="store_true", help="Générer aussi un rapport JSON")
    parser.add_argument("--verbose", action="store_true", help="Mode verbeux")

    args = parser.parse_args()

    analyzer = StructureAnalyzer(args.root)

    if args.verbose:
        print("🔍 Démarrage de l'analyse...")

    # Générer le rapport markdown
    markdown_file = analyzer.generate_report(args.output)

    # Générer le rapport JSON si demandé
    if args.json:
        json_file = analyzer.generate_json_report()
        print(f"📊 Rapports générés : {markdown_file} et {json_file}")
    else:
        print(f"📊 Rapport généré : {markdown_file}")


if __name__ == "__main__":
    main()

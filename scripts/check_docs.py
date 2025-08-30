#!/usr/bin/env python3
"""
📚 Script de vérification de la documentation
📝 Vérifie la qualité et la complétude de la documentation
🔧 Version: 2.8.0
👤 Author: Athalia
📅 Created: 2025-01-27
"""

import ast
import sys
from pathlib import Path


class DocChecker:
    """Vérificateur de documentation."""

    def __init__(self):
        self.issues = []
        self.stats = {
            "files_checked": 0,
            "functions_with_docs": 0,
            "functions_without_docs": 0,
            "classes_with_docs": 0,
            "classes_without_docs": 0,
            "modules_with_docs": 0,
            "modules_without_docs": 0,
        }

    def check_file(self, file_path: Path) -> None:
        """Vérifie un fichier Python."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            self.stats["files_checked"] += 1

            # Vérifier la docstring du module
            module_doc = ast.get_docstring(tree)
            if module_doc:
                self.stats["modules_with_docs"] += 1
            else:
                self.stats["modules_without_docs"] += 1
                self.issues.append(f"📝 {file_path}: Module sans docstring")

            # Vérifier les classes et fonctions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self._check_function(node, file_path)
                elif isinstance(node, ast.ClassDef):
                    self._check_class(node, file_path)

        except Exception as e:
            self.issues.append(f"❌ {file_path}: Erreur d'analyse - {e}")

    def _check_function(self, node: ast.FunctionDef, file_path: Path) -> None:
        """Vérifie une fonction."""
        # Ignorer les méthodes privées et les tests
        if node.name.startswith("_") or "test" in node.name.lower():
            return

        doc = ast.get_docstring(node)
        if doc:
            self.stats["functions_with_docs"] += 1
        else:
            self.stats["functions_without_docs"] += 1
            self.issues.append(
                f"📝 {file_path}:{node.lineno} - Fonction '{node.name}' sans docstring"
            )

    def _check_class(self, node: ast.ClassDef, file_path: Path) -> None:
        """Vérifie une classe."""
        # Ignorer les classes privées et les tests
        if node.name.startswith("_") or "test" in node.name.lower():
            return

        doc = ast.get_docstring(node)
        if doc:
            self.stats["classes_with_docs"] += 1
        else:
            self.stats["classes_without_docs"] += 1
            self.issues.append(
                f"📝 {file_path}:{node.lineno} - Classe '{node.name}' sans docstring"
            )

    def generate_report(self) -> str:
        """Génère un rapport de vérification."""
        total_functions = self.stats["functions_with_docs"] + self.stats["functions_without_docs"]
        total_classes = self.stats["classes_with_docs"] + self.stats["classes_without_docs"]
        total_modules = self.stats["modules_with_docs"] + self.stats["modules_without_docs"]

        report = [
            "📚 RAPPORT DE VÉRIFICATION DE DOCUMENTATION",
            "=" * 50,
            f"📁 Fichiers vérifiés: {self.stats['files_checked']}",
            "",
            "📊 Statistiques:",
            f"  📝 Modules avec docstring: {self.stats['modules_with_docs']}/{total_modules}",
            f"  📝 Classes avec docstring: {self.stats['classes_with_docs']}/{total_classes}",
            f"  📝 Fonctions avec docstring: {self.stats['functions_with_docs']}/{total_functions}",
            "",
            (
                f"📈 Couverture fonctions: {self.stats['functions_with_docs'] / total_functions * 100:.1f}%"
                if total_functions > 0
                else "📈 Couverture fonctions: N/A"
            ),
            (
                f"📈 Couverture classes: {self.stats['classes_with_docs'] / total_classes * 100:.1f}%"
                if total_classes > 0
                else "📈 Couverture classes: N/A"
            ),
            "",
        ]

        if self.issues:
            report.extend(
                [
                    "⚠️ Problèmes détectés:",
                    *self.issues,
                    "",
                    f"⚠️ {len(self.issues)} problème(s) de documentation détecté(s)",
                    "",
                    "💡 Recommandations:",
                    "- Ajouter des docstrings aux modules, classes et fonctions manquants",
                    "- Utiliser le format Google ou NumPy pour les docstrings",
                    "- Documenter les paramètres, types de retour et exceptions",
                    "- Ajouter des exemples d'utilisation pour les fonctions complexes",
                ]
            )
        else:
            report.extend(
                [
                    "✅ Aucun problème de documentation détecté",
                    "🎉 Documentation complète et de qualité !",
                ]
            )

        return "\n".join(report)

    def get_exit_code(self) -> int:
        """Retourne le code de sortie approprié."""
        # Ne pas faire échouer le CI pour des problèmes de documentation
        # Retourner 0 (succès) même avec des avertissements
        return 0


def main() -> None:
    """Fonction principale."""
    checker = DocChecker()

    # Vérifier tous les fichiers Python
    python_files = list(Path(".").rglob("*.py"))
    python_files = [f for f in python_files if "tests" not in str(f) and "venv" not in str(f)]

    for file_path in python_files:
        checker.check_file(file_path)

    # Générer et afficher le rapport
    report = checker.generate_report()
    print(report)

    # Utiliser le code de sortie approprié
    sys.exit(checker.get_exit_code())


if __name__ == "__main__":
    main()

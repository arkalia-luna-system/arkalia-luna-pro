#!/usr/bin/env python3
"""
📊 Script de validation et amélioration de la couverture des tests
📝 Analyse la couverture actuelle et propose des améliorations
🔧 Version: 2.8.0
👤 Author: Athalia
📅 Created: 2025-01-27
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class CoverageAnalyzer:
    """Analyseur de couverture des tests."""

    def __init__(self) -> None:
        self.modules_info: dict[str, dict] = {}
        self.test_files: list[Path] = []
        self.untested_modules: list[str] = []

    def analyze_modules(self) -> None:
        """Analyse tous les modules du projet."""
        modules_dir = Path("modules")
        if not modules_dir.exists():
            print("❌ Répertoire modules/ non trouvé")
            return

        print("🔍 Analyse des modules...")

        for py_file in modules_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            module_path = str(py_file.relative_to(Path(".")))
            module_name = str(py_file.relative_to(modules_dir)).replace("/", ".")

            # Compter les lignes de code
            try:
                with open(py_file, encoding="utf-8") as f:
                    lines = f.readlines()
                    code_lines = [
                        line for line in lines if line.strip() and not line.strip().startswith("#")
                    ]
                    total_lines = len(lines)
                    code_lines_count = len(code_lines)
            except Exception as e:
                print(f"⚠️ Erreur lecture {py_file}: {e}")
                continue

            self.modules_info[module_path] = {
                "module_name": module_name,
                "total_lines": total_lines,
                "code_lines": code_lines_count,
                "has_tests": False,
                "test_file": None,
            }

    def analyze_tests(self) -> None:
        """Analyse les fichiers de test existants."""
        tests_dir = Path("tests")
        if not tests_dir.exists():
            print("❌ Répertoire tests/ non trouvé")
            return

        print("🧪 Analyse des tests...")

        for test_file in tests_dir.rglob("test_*.py"):
            self.test_files.append(test_file)

            # Identifier le module testé
            test_path = str(test_file.relative_to(tests_dir))
            if "unit" in test_path:
                # Test unitaire
                module_name = (
                    test_path.replace("unit/", "").replace("/test_", "/").replace(".py", "")
                )
                for module_path in self.modules_info:
                    if module_name in module_path:
                        self.modules_info[module_path]["has_tests"] = True
                        self.modules_info[module_path]["test_file"] = str(test_file)
                        break

    def generate_coverage_report(self) -> str:
        """Génère un rapport de couverture détaillé."""
        total_modules = len(self.modules_info)
        tested_modules = sum(1 for info in self.modules_info.values() if info["has_tests"])
        untested_modules = total_modules - tested_modules

        total_lines = sum(info["total_lines"] for info in self.modules_info.values())
        total_code_lines = sum(info["code_lines"] for info in self.modules_info.values())

        report = [
            "📊 RAPPORT D'ANALYSE DE COUVERTURE",
            "=" * 50,
            f"📁 Modules analysés: {total_modules}",
            f"🧪 Modules testés: {tested_modules}",
            f"❌ Modules non testés: {untested_modules}",
            f"📝 Lignes totales: {total_lines}",
            f"💻 Lignes de code: {total_code_lines}",
            "",
            (
                f"📈 Couverture modules: {tested_modules/total_modules*100:.1f}%"
                if total_modules > 0
                else "📈 Couverture modules: N/A"
            ),
            "",
        ]

        if untested_modules > 0:
            report.extend(
                [
                    "⚠️ Modules sans tests:",
                    *[
                        f"  - {path}"
                        for path, info in self.modules_info.items()
                        if not info["has_tests"]
                    ],
                    "",
                    "💡 Recommandations:",
                    "- Créer des tests unitaires pour les modules non testés",
                    "- Commencer par les modules les plus simples",
                    "- Utiliser des mocks pour les dépendances externes",
                    "- Ajouter des tests d'intégration pour les modules complexes",
                ]
            )
        else:
            report.extend(
                ["✅ Tous les modules ont des tests !", "🎉 Couverture complète atteinte !"]
            )

        return "\n".join(report)

    def suggest_test_improvements(self) -> str:
        """Suggère des améliorations pour les tests."""
        suggestions = [
            "🚀 AMÉLIORATIONS SUGGÉRÉES POUR LES TESTS",
            "=" * 50,
            "",
            "1. 📝 Tests unitaires manquants:",
        ]

        # Identifier les modules sans tests
        for module_path, info in self.modules_info.items():
            if not info["has_tests"]:
                suggestions.append(
                    f"   - Créer tests/unit/{info['module_name'].replace('.', '/')}/test_{info['module_name'].split('.')[-1]}.py"
                )

        suggestions.extend(
            [
                "",
                "2. 🔧 Tests d'intégration:",
                "   - Créer tests/integration/test_module_interactions.py",
                "   - Tester les interactions entre modules",
                "",
                "3. ⚡ Tests de performance:",
                "   - Créer tests/performance/test_module_performance.py",
                "   - Mesurer les temps de réponse",
                "",
                "4. 🔒 Tests de sécurité:",
                "   - Créer tests/security/test_module_security.py",
                "   - Tester la validation des entrées",
                "",
                "5. 🧹 Nettoyage:",
                "   - Supprimer les tests cassés",
                "   - Optimiser les tests lents",
                "   - Améliorer la couverture des branches",
            ]
        )

        return "\n".join(suggestions)


def main() -> None:
    """Fonction principale."""
    analyzer = CoverageAnalyzer()

    # Analyser les modules et tests
    analyzer.analyze_modules()
    analyzer.analyze_tests()

    # Générer les rapports
    coverage_report = analyzer.generate_coverage_report()
    suggestions = analyzer.suggest_test_improvements()

    print(coverage_report)
    print("\n" + "=" * 50 + "\n")
    print(suggestions)

    # Retourner un code de sortie approprié
    total_modules = len(analyzer.modules_info)
    tested_modules = sum(1 for info in analyzer.modules_info.values() if info["has_tests"])

    if tested_modules / total_modules < 0.5:  # Moins de 50% de couverture
        print("\n⚠️ Couverture faible détectée - CI pourrait échouer")
        sys.exit(1)
    else:
        print("\n✅ Couverture acceptable - CI devrait passer")
        sys.exit(0)


if __name__ == "__main__":
    main()

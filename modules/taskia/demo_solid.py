#!/usr/bin/env python3
"""
🌕 TaskIA SOLID Demo
📝 Démonstration du refactoring SOLID
🔧 Version: 2.0.0
👤 Author: Athalia
📅 Created: 2025-01-27
"""

import os
import sys
from typing import Any

from modules.taskia.core_refactored import TaskIACore
from modules.taskia.factories.formatter_factory import FormatterFactory
from modules.taskia.factories.service_factory import ServiceFactory
from modules.taskia.interfaces.formatter_interface import IFormatter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def demo_solid_principles():
    """Démonstration des principes SOLID appliqués."""

    print("🚀 DÉMONSTRATION SOLID TASKIA")
    print("=" * 50)

    # Données de test
    test_context = {
        "projet": "Arkalia Luna Pro",
        "module": "TaskIA",
        "version": "2.0.0",
        "principe": "SOLID",
        "statut": "Refactorisé",
        "formateurs": ["summary", "json", "markdown", "html"],
    }

    # 1. DÉMONSTRATION SRP (Single Responsibility)
    print("\n📋 1. PRINCIPE SRP - Responsabilités Uniques")
    print("-" * 40)

    core = TaskIACore()
    print("✅ Core initialisé avec responsabilité unique")
    print(f"✅ Formateurs disponibles: {core.get_available_formatters()}")

    # 2. DÉMONSTRATION OCP (Open/Closed)
    print("\n🔓 2. PRINCIPE OCP - Ouvert/Fermé")
    print("-" * 40)

    # Test de tous les formateurs sans modifier le code existant
    formatters_to_test = ["summary", "json", "markdown", "html"]

    for fmt_type in formatters_to_test:
        try:
            result = core.process_task(test_context, format_type=fmt_type)
            print(f"✅ Formateur {fmt_type}: OK")
            print(f"   Résultat (premiers 100 chars): {result[:100]}...")
        except Exception as e:
            print(f"❌ Formateur {fmt_type}: ERREUR - {e}")

    # 3. DÉMONSTRATION LSP (Liskov Substitution)
    print("\n🔄 3. PRINCIPE LSP - Substitution de Liskov")
    print("-" * 40)

    # Tous les formateurs peuvent être substitués
    factory = FormatterFactory()
    formatters = [
        factory.create_formatter("summary"),
        factory.create_formatter("json"),
        factory.create_formatter("markdown"),
        factory.create_formatter("html"),
    ]

    for formatter in formatters:
        result = formatter.format(test_context)
        print(f"✅ {formatter.get_format_type()}: {len(result)} caractères")

    # 4. DÉMONSTRATION ISP (Interface Segregation)
    print("\n🎯 4. PRINCIPE ISP - Ségrégation des Interfaces")
    print("-" * 40)

    # Chaque interface a une responsabilité spécifique
    print("✅ IFormatter: Interface spécifique au formatage")
    print("✅ ITaskProcessor: Interface spécifique au traitement")
    print("✅ IHealthChecker: Interface spécifique à la santé")

    # 5. DÉMONSTRATION DIP (Dependency Inversion)
    print("\n🔄 5. PRINCIPE DIP - Inversion des Dépendances")
    print("-" * 40)

    # Injection de dépendances
    service_factory = ServiceFactory()
    custom_core = TaskIACore(service_factory=service_factory)

    print("✅ Core créé avec injection de dépendances")
    print("✅ Dépend des interfaces, pas des implémentations")

    # Test avec injection
    result = custom_core.process_task(test_context, format_type="json")
    print(f"✅ Résultat avec injection: {len(result)} caractères")

    # 6. DÉMONSTRATION EXTENSIBILITÉ
    print("\n�� 6. EXTENSIBILITÉ - Nouveaux Formateurs")
    print("-" * 40)

    # Ajout d'un nouveau formateur sans modifier le code existant
    class CsvFormatter(IFormatter):
        """Formateur CSV pour les données TaskIA."""

        def format(self, data: dict[str, Any]) -> str:
            """
            Formate les données en CSV.

            Args:
                data: Dictionnaire de données à formater.

            Returns:
                str: Données formatées en CSV.
            """
            lines = [f"{k},{v}" for k, v in data.items()]
            return "\n".join(lines)

        def get_format_type(self) -> str:
            """
            Retourne le type de format.

            Returns:
                str: Type de format ("csv").
            """
            return "csv"

    # Enregistrement du nouveau formateur
    factory.register_formatter("csv", CsvFormatter)
    print("✅ Nouveau formateur CSV ajouté sans modification du code existant")

    # Test du nouveau formateur
    try:
        result = core.process_task(test_context, format_type="csv")
        print(f"✅ Formateur CSV: {len(result)} caractères")
    except Exception as e:
        print(f"❌ Formateur CSV: ERREUR - {e}")

    # 7. DÉMONSTRATION SANTÉ
    print("\n🏥 7. VÉRIFICATION DE SANTÉ")
    print("-" * 40)

    health = core.check_health()
    print(f"✅ Santé: {health['status']}")
    print(f"✅ Module: {health['module']}")
    print(f"✅ Version: {health['version']}")

    print("\n🎉 DÉMONSTRATION SOLID TERMINÉE AVEC SUCCÈS!")
    print("=" * 50)


if __name__ == "__main__":
    demo_solid_principles()

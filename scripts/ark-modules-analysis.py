#!/usr/bin/env python3
"""
🔍 ARKALIA MODULES ANALYSIS - Détection des modules non intégrés
Analyse tous les composants disponibles vs ceux intégrés dans l'orchestrateur
"""

from pathlib import Path

from core.ark_logger import ark_logger


class ArkaliaModulesAnalyzer:
    """Analyse complète des modules Arkalia disponibles vs intégrés"""

    def __init__(self) -> None:
        self.project_root = Path(".")
        self.modules_dir = self.project_root / "modules"

        # Modules actuellement intégrés dans l'orchestrateur
        self.integrated_modules = {
            "zeroia",
            "reflexia",
            "assistantia",
            "sandozia",
            "taskia",
            "helloria",
            "nyxalia",
            "security",
            "monitoring",
            "utils",
        }

        # Composants trouvés
        self.discovered_modules: dict[str, list[str]] = {}
        self.missing_integrations: list[dict] = []

    def scan_all_modules(self) -> None:
        """Scan complet de tous les modules disponibles"""
        ark_logger.info(
            "🔍 ANALYSE COMPLÈTE DES MODULES ARKALIA", extra={"arkalia_module": "scripts"}
        )
        ark_logger.info("=" * 60, extra={"arkalia_module": "scripts"})

        # Scan modules/ directory
        if self.modules_dir.exists():
            for module_dir in self.modules_dir.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith("__"):
                    self.scan_module_directory(module_dir)

        # Scan helloria à la racine
        helloria_root = self.project_root / "helloria"
        if helloria_root.exists():
            self.scan_module_directory(helloria_root)

        # Analyser les résultats
        self.analyze_integration_gaps()

    def scan_module_directory(self, module_path: Path) -> None:
        """Scan un répertoire de module spécifique"""
        module_name = module_path.name
        components = []

        for file_path in module_path.rglob("*.py"):
            if file_path.name != "__init__.py" and not file_path.name.startswith("test_"):
                relative_path = file_path.relative_to(module_path)
                component_name = str(relative_path).replace(".py", "").replace("/", ".")
                components.append(component_name)

        self.discovered_modules[module_name] = components

        # Identifier les composants spéciaux
        self.identify_special_components(module_name, components)

    def identify_special_components(self, module_name: str, components: list[str]) -> None:
        """Identifie les composants spéciaux qui pourraient être intégrés"""

        special_patterns = {
            "core": "Module principal",
            "manager": "Gestionnaire système",
            "orchestrator": "Orchestrateur local",
            "reactor": "Réacteur cognitif",
            "analyzer": "Analyseur de données",
            "validator": "Validateur de système",
            "monitor": "Moniteur système",
            "recovery": "Système de récupération",
            "degradation": "Dégradation gracieuse",
            "vault": "Gestionnaire de secrets",
            "chronalia": "Gestionnaire temporel",
            "behavior": "Analyse comportementale",
            "collaborative": "Intelligence collaborative",
            "crossmodule": "Validation inter-modules",
            "cognitive": "Processus cognitifs",
        }

        for component in components:
            for pattern, description in special_patterns.items():
                if pattern in component.lower():
                    # Vérifier si ce composant est intégré
                    is_integrated = self.is_component_integrated(module_name, component)

                    if not is_integrated:
                        self.missing_integrations.append(
                            {
                                "module": module_name,
                                "component": component,
                                "type": description,
                                "priority": self.get_priority(component),
                                "integration_suggestion": self.suggest_integration(
                                    module_name, component
                                ),
                            }
                        )

    def is_component_integrated(self, module_name: str, component: str) -> bool:
        """Vérifie si un composant est déjà intégré dans l'orchestrateur"""

        # Lecture de l'orchestrateur pour vérifier les imports
        orchestrator_file = self.project_root / "modules/arkalia_master/orchestrator_ultimate.py"

        if not orchestrator_file.exists():
            return False

        try:
            with open(orchestrator_file) as f:
                content = f.read()

            # Vérifier si le composant est importé ou utilisé
            component_patterns = [
                f"from ..{module_name}.{component}",
                f"import {component}",
                f"{component}(",
                f"{component.split('.')[-1]}(",  # Dernière partie du nom
            ]

            return any(pattern in content for pattern in component_patterns)

        except Exception:
            return False

    def get_priority(self, component: str) -> str:
        """Détermine la priorité d'intégration"""
        high_priority = ["manager", "orchestrator", "reactor", "recovery", "vault"]
        medium_priority = ["analyzer", "validator", "monitor", "chronalia", "cognitive"]

        component_lower = component.lower()

        if any(pattern in component_lower for pattern in high_priority):
            return "HIGH"
        elif any(pattern in component_lower for pattern in medium_priority):
            return "MEDIUM"
        else:
            return "LOW"

    def suggest_integration(self, module_name: str, component: str) -> str:
        """Suggère comment intégrer le composant"""

        suggestions = {
            "vault_manager": "Intégrer dans phase SECURITY pour gestion secrets",
            "chronalia": "Ajouter dans mode DEEP_ANALYSIS pour gestion temporelle",
            "cognitive_reactor": "Intégrer dans cycles pour réactions automatiques",
            "behavior": "Ajouter dans phase MONITORING pour analyse comportementale",
            "collaborative": "Intégrer avec SandozIA pour intelligence collaborative",
            "crossmodule": "Utiliser pour validation inter-modules",
            "error_recovery_system": "Intégrer dans circuit breaker global",
            "graceful_degradation": "Ajouter pour dégradation gracieuse système",
            "confidence_score": "Intégrer dans ZeroIA pour scoring décisions",
            "model_integrity": "Ajouter dans phase SECURITY pour intégrité",
            "token_lifecycle": "Intégrer pour gestion tokens sécurisés",
            "secret_rotation": "Ajouter pour rotation automatique secrets",
        }

        for pattern, suggestion in suggestions.items():
            if pattern in component:
                return suggestion

        return f"Évaluer intégration dans {module_name.upper()}"

    def analyze_integration_gaps(self) -> None:
        """Analyse les lacunes d'intégration"""
        ark_logger.info(
            f"\n📊 MODULES DÉCOUVERTS : {len(self.discovered_modules)}",
            extra={"arkalia_module": "scripts"},
        )
        ark_logger.info(
            f"🔗 MODULES INTÉGRÉS    : {len(self.integrated_modules)}",
            extra={"arkalia_module": "scripts"},
        )
        ark_logger.info(
            f"⚠️ COMPOSANTS MANQUÉS  : {len(self.missing_integrations)}",
            extra={"arkalia_module": "scripts"},
        )

    def print_detailed_report(self) -> None:
        """Affiche le rapport détaillé"""
        ark_logger.info(
            "\n🔍 RAPPORT DÉTAILLÉ - MODULES NON INTÉGRÉS", extra={"arkalia_module": "scripts"}
        )
        ark_logger.info("=" * 80, extra={"arkalia_module": "scripts"})

        # Trier par priorité
        high_priority = [m for m in self.missing_integrations if m["priority"] == "HIGH"]
        medium_priority = [m for m in self.missing_integrations if m["priority"] == "MEDIUM"]
        low_priority = [m for m in self.missing_integrations if m["priority"] == "LOW"]

        # Afficher par priorité
        for priority, items in [
            ("🔥 HAUTE PRIORITÉ", high_priority),
            ("⚠️ MOYENNE PRIORITÉ", medium_priority),
            ("💡 BASSE PRIORITÉ", low_priority),
        ]:
            if items:
                ark_logger.info(f"\n{priority}:", extra={"arkalia_module": "scripts"})
                ark_logger.info("-" * 50, extra={"arkalia_module": "scripts"})

                for item in items:
                    ark_logger.info(
                        f"📦 {item['module']}.{item['component']}",
                        extra={"arkalia_module": "scripts"},
                    )
                    ark_logger.info(f"   Type: {item['type']}", extra={"arkalia_module": "scripts"})
                    ark_logger.info(
                        f"   💡 {item['integration_suggestion']}",
                        extra={"arkalia_module": "scripts"},
                    )
                    ark_logger.info("")

    def generate_integration_code(self) -> None:
        """Génère le code d'intégration suggéré"""
        ark_logger.info("\n🚀 CODE D'INTÉGRATION SUGGÉRÉ", extra={"arkalia_module": "scripts"})
        ark_logger.info("=" * 60, extra={"arkalia_module": "scripts"})

        high_priority = [m for m in self.missing_integrations if m["priority"] == "HIGH"]

        if high_priority:
            ark_logger.info("# === IMPORTS À AJOUTER ===", extra={"arkalia_module": "scripts"})
            for item in high_priority:
                module_path = f"..{item['module']}.{item['component']}"
                component_class = item["component"].split(".")[-1]
                ark_logger.info(
                    f"from {module_path} import {component_class}",
                    extra={"arkalia_module": "scripts"},
                )

            ark_logger.info(
                "\n# === INITIALISATION DANS initialize_modules() ===",
                extra={"arkalia_module": "scripts"},
            )
            for item in high_priority:
                component_name = item["component"].split(".")[-1]
                module_key = f"{item['module']}_{component_name.lower()}"
                ark_logger.info(
                    f'        initialization_results["{module_key}"] = '
                    f'ModuleWrapper("{module_key}", {item["module"]}_component)',
                    extra={"arkalia_module": "scripts"},
                )
                module_key = f"{item['module']}_{component_name.lower()}"
                ark_logger.info(
                    f'        initialization_results["{module_key}"] = "✅ SUCCESS"',
                    extra={"arkalia_module": "scripts"},
                )
                ark_logger.info("    except Exception as e:", extra={"arkalia_module": "scripts"})
                module_key = f"{item['module']}_{component_name.lower()}"
                ark_logger.info(
                    f'        initialization_results["{module_key}"] = f"❌ ERROR: {{e}}"',
                    extra={"arkalia_module": "scripts"},
                )
                ark_logger.info("")


def main() -> None:
    """Point d'entrée principal"""
    analyzer = ArkaliaModulesAnalyzer()
    analyzer.scan_all_modules()
    analyzer.print_detailed_report()
    analyzer.generate_integration_code()


if __name__ == "__main__":
    main()

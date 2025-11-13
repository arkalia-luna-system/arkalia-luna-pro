#!/usr/bin/env python3
"""
🚀 Script de Démo CLI Arkalia-LUNA Pro
Scénarios de démonstration reproductibles pour experts

Usage:
    python scripts/launch_demo_scenario.py --scenario security
    python scripts/launch_demo_scenario.py --scenario performance
    python scripts/launch_demo_scenario.py --scenario learning
    python scripts/launch_demo_scenario.py --all
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Ajout du chemin des modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from modules.monitoring.prometheus_metrics import metrics
    from modules.reflexia.core import launch_reflexia_check
    from modules.sandozia.analyzer.behavior import BehaviorAnalyzer
    from modules.sandozia.core.sandozia_core import SandoziaCore
    from modules.security.crypto.vault_manager import ArkaliaVault
    from modules.zeroia import ZeroIACoordinator
except ImportError as e:
    print(f"❌ Erreur import modules: {e}")
    print("Assurez-vous d'être dans le répertoire arkalia-luna-pro")
    sys.exit(1)

# Configuration logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ArkaliaDemoCLI:
    """Démo CLI Arkalia-LUNA avec scénarios reproductibles"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "scenarios": [],
            "metrics": {},
            "status": "completed",
        }

        # Initialisation des modules
        self.zeroia = ZeroIACoordinator()
        self.sandozia = SandoziaCore()
        self.security = ArkaliaVault()
        self.behavior_analyzer = BehaviorAnalyzer()

        print("🌕 Arkalia-LUNA Demo CLI initialisé")

    def print_header(self, title: str):
        """Affiche un en-tête de section"""
        print(f"\n{'=' * 60}")
        print(f"🎯 {title}")
        print(f"{'=' * 60}")

    def print_step(self, step: str, status: str = "✅"):
        """Affiche une étape"""
        print(f"{status} {step}")

    def print_metrics(self, metrics_data: dict[str, Any]):
        """Affiche les métriques"""
        print("\n📊 Métriques:")
        for key, value in metrics_data.items():
            print(f"   • {key}: {value}")

    def scenario_security_incident(self) -> dict[str, Any]:
        """Scénario 1: Incident de sécurité"""
        self.print_header("SCÉNARIO 1: INCIDENT DE SÉCURITÉ")

        scenario = {
            "name": "security_incident",
            "steps": [],
            "start_time": time.time(),
            "description": "Détection et réponse à une tentative d'intrusion",
        }

        # 1. Simulation d'une tentative d'intrusion
        self.print_step("1. Simulation tentative d'intrusion SQL Injection")
        suspicious_request = {
            "client_ip": "192.168.1.100",
            "endpoint": "/admin/delete",
            "method": "POST",
            "payload": "'; DROP TABLE users; --",
            "timestamp": time.time(),
        }
        scenario["steps"].append(
            {"step": "simulate_attack", "data": suspicious_request, "timestamp": time.time()}
        )

        # 2. Scan de sécurité
        self.print_step("2. Scan de sécurité")
        try:
            # Simulation d'un scan de sécurité
            scan_result = {
                "threat_level": "high" if "DROP TABLE" in suspicious_request["payload"] else "low",
                "blocked": True,
                "reason": "SQL injection detected",
                "timestamp": time.time(),
            }
            scenario["steps"].append(
                {"step": "security_scan", "result": scan_result, "timestamp": time.time()}
            )
            print(f"   🚨 Niveau de menace: {scan_result.get('threat_level', 'unknown')}")
            print(f"   🛡️ Bloqué: {scan_result.get('blocked', False)}")
        except Exception as e:
            print(f"   ⚠️ Erreur scan sécurité: {e}")

        # 3. Décision ZeroIA
        self.print_step("3. Décision ZeroIA")
        try:
            # Simulation d'une décision
            decision_result = {
                "decision": "block_ip",
                "confidence": 0.95,
                "reason": "security_threat_detected",
            }
            scenario["steps"].append(
                {"step": "zeroia_decision", "result": decision_result, "timestamp": time.time()}
            )
            print(f"   🧠 Décision: {decision_result.get('decision', 'unknown')}")
        except Exception as e:
            print(f"   ⚠️ Erreur décision ZeroIA: {e}")

        # 4. Analyse comportementale Sandozia
        self.print_step("4. Analyse comportementale Sandozia")
        try:
            # Utiliser le behavior analyzer
            self.behavior_analyzer.add_metric_sample("security", "threat_level", 0.9)
            analysis_result = self.behavior_analyzer.analyze_behavior()
            scenario["steps"].append(
                {"step": "sandozia_analysis", "result": analysis_result, "timestamp": time.time()}
            )
            health_score = analysis_result.get("behavioral_health_score", 0)
            print(f"   🔍 Score santé comportementale: {health_score:.2f}")
        except Exception as e:
            print(f"   ⚠️ Erreur analyse Sandozia: {e}")

        scenario["end_time"] = time.time()
        scenario["duration"] = scenario["end_time"] - scenario["start_time"]

        self.results["scenarios"].append(scenario)
        return scenario

    def scenario_performance_optimization(self) -> dict[str, Any]:
        """Scénario 2: Optimisation de performance"""
        self.print_header("SCÉNARIO 2: OPTIMISATION DE PERFORMANCE")

        scenario = {
            "name": "performance_optimization",
            "steps": [],
            "start_time": time.time(),
            "description": "Détection et optimisation des performances système",
        }

        # 1. Collecte métriques système
        self.print_step("1. Collecte métriques système")
        try:
            system_metrics = launch_reflexia_check()
            scenario["steps"].append(
                {"step": "collect_metrics", "data": system_metrics, "timestamp": time.time()}
            )

            metrics_data = system_metrics.get("metrics", {})
            print(f"   💻 CPU: {metrics_data.get('cpu', 0)}%")
            print(f"   🧠 RAM: {metrics_data.get('ram', 0)}%")
            print(f"   ⏱️ Latence: {metrics_data.get('latency', 0)}ms")
        except Exception as e:
            print(f"   ⚠️ Erreur collecte métriques: {e}")

        # 2. Analyse performance
        self.print_step("2. Analyse performance")
        try:
            performance_analysis = {
                "cpu_usage": metrics_data.get("cpu", 0),
                "ram_usage": metrics_data.get("ram", 0),
                "latency": metrics_data.get("latency", 0),
                "timestamp": time.time(),
            }

            # Détection de problèmes
            issues = []
            if performance_analysis["cpu_usage"] > 80:
                issues.append("CPU élevé")
            if performance_analysis["ram_usage"] > 85:
                issues.append("RAM élevée")
            if performance_analysis["latency"] > 100:
                issues.append("Latence élevée")

            scenario["steps"].append(
                {
                    "step": "performance_analysis",
                    "data": performance_analysis,
                    "issues": issues,
                    "timestamp": time.time(),
                }
            )

            if issues:
                print(f"   ⚠️ Problèmes détectés: {', '.join(issues)}")
            else:
                print("   ✅ Performance normale")
        except Exception as e:
            print(f"   ⚠️ Erreur analyse performance: {e}")

        # 3. Décision d'optimisation
        self.print_step("3. Décision d'optimisation")
        try:
            optimization_decision = self.zeroia.make_decision("performance_optimization")
            scenario["steps"].append(
                {
                    "step": "optimization_decision",
                    "result": optimization_decision,
                    "timestamp": time.time(),
                }
            )
            print(f"   🧠 Action recommandée: {optimization_decision.get('action', 'monitor')}")
        except Exception as e:
            print(f"   ⚠️ Erreur décision optimisation: {e}")

        scenario["end_time"] = time.time()
        scenario["duration"] = scenario["end_time"] - scenario["start_time"]

        self.results["scenarios"].append(scenario)
        return scenario

    def scenario_adaptive_learning(self) -> dict[str, Any]:
        """Scénario 3: Apprentissage adaptatif"""
        self.print_header("SCÉNARIO 3: APPRENTISSAGE ADAPTATIF")

        scenario = {
            "name": "adaptive_learning",
            "steps": [],
            "start_time": time.time(),
            "description": "Démonstration de l'apprentissage adaptatif du système",
        }

        # 1. Initialisation Cognitive Reactor
        self.print_step("1. Initialisation Cognitive Reactor")
        try:
            # Simulation d'un état cognitif
            cognitive_status = {
                "status": "active",
                "reactions_enabled": True,
                "confidence_score": 0.85,
            }
            scenario["steps"].append(
                {"step": "cognitive_init", "data": cognitive_status, "timestamp": time.time()}
            )
            print(f"   🧠 État cognitif: {cognitive_status.get('status', 'unknown')}")
        except Exception as e:
            print(f"   ⚠️ Erreur Cognitive Reactor: {e}")

        # 2. Simulation d'apprentissage
        self.print_step("2. Simulation d'apprentissage")
        try:
            learning_data = {
                "pattern_type": "user_behavior",
                "data_points": 100,
                "accuracy": 0.85,
                "timestamp": time.time(),
            }

            # Simulation d'amélioration
            learning_data["accuracy"] += 0.02  # Amélioration simulée

            scenario["steps"].append(
                {"step": "learning_simulation", "data": learning_data, "timestamp": time.time()}
            )

            print(f"   📈 Précision: {learning_data['accuracy']:.2f}")
            print(f"   📊 Points de données: {learning_data['data_points']}")
        except Exception as e:
            print(f"   ⚠️ Erreur simulation apprentissage: {e}")

        # 3. Adaptation du comportement
        self.print_step("3. Adaptation du comportement")
        try:
            adaptation_result = {
                "old_threshold": 0.8,
                "new_threshold": 0.82,
                "adaptation_reason": "amélioration_précision",
                "timestamp": time.time(),
            }

            scenario["steps"].append(
                {"step": "behavior_adaptation", "data": adaptation_result, "timestamp": time.time()}
            )

            old_threshold = adaptation_result["old_threshold"]
            new_threshold = adaptation_result["new_threshold"]
            print(f"   🔄 Seuil adapté: {old_threshold} → {new_threshold}")
        except Exception as e:
            print(f"   ⚠️ Erreur adaptation: {e}")

        scenario["end_time"] = time.time()
        scenario["duration"] = scenario["end_time"] - scenario["start_time"]

        self.results["scenarios"].append(scenario)
        return scenario

    def collect_final_metrics(self):
        """Collecte les métriques finales"""
        self.print_header("MÉTRIQUES FINALES")

        try:
            # Métriques système
            system_metrics = launch_reflexia_check()
            self.results["metrics"]["system"] = system_metrics.get("metrics", {})

            # Métriques Prometheus
            metrics.generate_metrics()
            self.results["metrics"]["prometheus"] = "collected"

            # Statistiques des scénarios
            total_duration = sum(s["duration"] for s in self.results["scenarios"])
            total_steps = sum(len(s["steps"]) for s in self.results["scenarios"])

            self.results["metrics"]["demo_stats"] = {
                "total_scenarios": len(self.results["scenarios"]),
                "total_duration": total_duration,
                "total_steps": total_steps,
                "avg_duration": (
                    total_duration / len(self.results["scenarios"])
                    if self.results["scenarios"]
                    else 0
                ),
            }

            print(f"📊 Scénarios exécutés: {len(self.results['scenarios'])}")
            print(f"⏱️ Durée totale: {total_duration:.2f}s")
            print(f"📋 Étapes totales: {total_steps}")

        except Exception as e:
            print(f"⚠️ Erreur collecte métriques finales: {e}")

    def save_results(self, filename: str = "demo_cli_results.json"):
        """Sauvegarde les résultats"""
        try:
            with open(filename, "w") as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"💾 Résultats sauvegardés: {filename}")
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde: {e}")

    def run_scenario(self, scenario_name: str):
        """Exécute un scénario spécifique"""
        scenarios = {
            "security": self.scenario_security_incident,
            "performance": self.scenario_performance_optimization,
            "learning": self.scenario_adaptive_learning,
        }

        if scenario_name in scenarios:
            scenarios[scenario_name]()
        else:
            print(f"❌ Scénario inconnu: {scenario_name}")
            print(f"Scénarios disponibles: {', '.join(scenarios.keys())}")

    def run_all_scenarios(self):
        """Exécute tous les scénarios"""
        print("🚀 EXÉCUTION DE TOUS LES SCÉNARIOS")

        self.scenario_security_incident()
        self.scenario_performance_optimization()
        self.scenario_adaptive_learning()

        self.collect_final_metrics()
        self.save_results()


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description="Arkalia-LUNA Demo CLI")
    parser.add_argument(
        "--scenario", choices=["security", "performance", "learning"], help="Scénario à exécuter"
    )
    parser.add_argument("--all", action="store_true", help="Exécuter tous les scénarios")
    parser.add_argument(
        "--output", default="demo_cli_results.json", help="Fichier de sortie pour les résultats"
    )

    args = parser.parse_args()

    demo = ArkaliaDemoCLI()

    try:
        if args.all:
            demo.run_all_scenarios()
        elif args.scenario:
            demo.run_scenario(args.scenario)
            demo.collect_final_metrics()
            demo.save_results(args.output)
        else:
            print("❌ Spécifiez --scenario ou --all")
            parser.print_help()
            sys.exit(1)

        print("\n✅ Démo terminée avec succès!")

    except KeyboardInterrupt:
        print("\n⚠️ Démo interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur lors de la démo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

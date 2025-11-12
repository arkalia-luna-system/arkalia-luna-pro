"""
Arkalia Score Generator
Génère un score cognitif global en temps réel
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import toml

from modules.core.optimizations.optimization_integrator import OptimizationIntegrator
from modules.core.storage import get_storage

logger = logging.getLogger(__name__)


class ArkaliaScoreGenerator:
    """Générateur de score cognitif global Arkalia-LUNA"""

    def __init__(self, config_path: str = "config/arkalia_score.toml"):
        self.config_path = Path(config_path)
        self.storage = get_storage()
        self.optimizer = OptimizationIntegrator()
        self.score_history: list[dict[str, Any]] = []
        self.max_history_size = 100

        # Seuils par défaut
        self.thresholds = {
            "zeroia_confidence": 0.7,
            "reflexia_alerts": 5,
            "sandozia_integrity": 0.8,
            "cognitive_load": 0.6,
            "system_health": 0.8,
        }

        self._load_config()
        logger.info("ArkaliaScoreGenerator initialisé")

    def _load_config(self):
        """Charge la configuration des seuils"""
        try:
            if self.config_path.exists():
                config = toml.load(self.config_path)
                if "thresholds" in config:
                    self.thresholds.update(config["thresholds"])
                logger.info("Configuration des seuils chargée")
        except Exception as e:
            logger.warning(f"Erreur chargement config: {e}")

    def get_zeroia_confidence(self) -> float:
        """Récupère le niveau de confiance ZeroIA"""
        try:
            # Récupérer les métriques ZeroIA
            metrics = self.storage.get_metrics("zeroia")

            # Calculer la confiance basée sur les décisions récentes
            recent_decisions = metrics.get("recent_decisions", [])
            if not recent_decisions:
                return 0.5  # Confiance neutre

            # Analyser la qualité des décisions
            successful_decisions = sum(1 for d in recent_decisions if d.get("success", False))
            total_decisions = len(recent_decisions)

            if total_decisions == 0:
                return 0.5

            confidence = successful_decisions / total_decisions

            # Ajuster avec la cohérence des décisions
            decision_types = [d.get("type", "") for d in recent_decisions]
            type_consistency = (
                len(set(decision_types)) / len(decision_types) if decision_types else 0
            )

            final_confidence = (confidence * 0.7) + (type_consistency * 0.3)
            return min(max(final_confidence, 0.0), 1.0)

        except Exception as e:
            logger.error(f"Erreur calcul confiance ZeroIA: {e}")
            return 0.3  # Confiance faible en cas d'erreur

    def get_reflexia_alerts(self) -> int:
        """Récupère le nombre d'alertes Reflexia actives"""
        try:
            # Récupérer les alertes actives
            alerts = self.storage.get_state("reflexia", "active_alerts", [])
            return len(alerts)
        except Exception as e:
            logger.error(f"Erreur récupération alertes Reflexia: {e}")
            return 0

    def get_sandozia_integrity(self) -> float:
        """Récupère le score d'intégrité Sandozia"""
        try:
            # Récupérer les métriques Sandozia
            metrics = self.storage.get_metrics("sandozia")

            # Calculer l'intégrité basée sur les analyses
            analysis_count = metrics.get("analysis_count", 0)
            anomaly_count = metrics.get("anomaly_count", 0)

            if analysis_count == 0:
                return 0.5  # Intégrité neutre

            # Ratio d'anomalies détectées vs analyses
            anomaly_ratio = anomaly_count / analysis_count

            # Score d'intégrité (plus d'anomalies = moins d'intégrité)
            integrity = 1.0 - min(anomaly_ratio, 1.0)

            # Ajuster avec la cohérence des analyses
            consistency_score = metrics.get("consistency_score", 0.8)

            final_integrity = (integrity * 0.6) + (consistency_score * 0.4)
            return min(max(final_integrity, 0.0), 1.0)

        except Exception as e:
            logger.error(f"Erreur calcul intégrité Sandozia: {e}")
            return 0.4  # Intégrité faible en cas d'erreur

    def get_cognitive_load(self) -> float:
        """Récupère la charge cognitive globale"""
        try:
            # Récupérer les métriques de performance
            cache_metrics = self.storage.get_metrics("cache")
            lb_metrics = self.storage.get_metrics("load_balancer")
            cb_metrics = self.storage.get_metrics("circuit_breaker")

            # Calculer la charge basée sur plusieurs facteurs
            factors = []

            # Cache miss ratio
            cache_hits = cache_metrics.get("hits", 0)
            cache_misses = cache_metrics.get("misses", 0)
            total_cache = cache_hits + cache_misses
            if total_cache > 0:
                miss_ratio = cache_misses / total_cache
                factors.append(miss_ratio)

            # Load balancer stress
            active_backends = lb_metrics.get("active_backends", 1)
            total_backends = lb_metrics.get("total_backends", 1)
            if total_backends > 0:
                stress_ratio = 1.0 - (active_backends / total_backends)
                factors.append(stress_ratio)

            # Circuit breaker state
            cb_state = cb_metrics.get("state", "closed")
            if cb_state == "open":
                factors.append(1.0)  # Charge maximale
            elif cb_state == "half-open":
                factors.append(0.5)  # Charge moyenne
            else:
                factors.append(0.1)  # Charge faible

            # CPU et mémoire (si disponibles)
            system_metrics = self.storage.get_metrics("system")
            cpu_usage = system_metrics.get("cpu_usage", 0.5)
            memory_usage = system_metrics.get("memory_usage", 0.5)

            factors.extend([cpu_usage, memory_usage])

            # Moyenne pondérée des facteurs
            if factors:
                cognitive_load = sum(factors) / len(factors)
                return min(max(cognitive_load, 0.0), 1.0)

            return 0.5  # Charge neutre

        except Exception as e:
            logger.error(f"Erreur calcul charge cognitive: {e}")
            return 0.5

    def get_system_health(self) -> float:
        """Récupère la santé globale du système"""
        try:
            # Récupérer les métriques de santé
            health_metrics = self.storage.get_metrics("health")

            # Calculer la santé basée sur plusieurs indicateurs
            indicators = []

            # Watchdogs
            watchdog_status = health_metrics.get("watchdog_status", {})
            active_watchdogs = sum(1 for status in watchdog_status.values() if status == "healthy")
            total_watchdogs = len(watchdog_status) if watchdog_status else 1
            watchdog_health = active_watchdogs / total_watchdogs
            indicators.append(watchdog_health)

            # Erreurs système
            error_count = health_metrics.get("error_count", 0)
            total_operations = health_metrics.get("total_operations", 1)
            error_ratio = error_count / total_operations
            error_health = 1.0 - min(error_ratio, 1.0)
            indicators.append(error_health)

            # Temps de réponse
            avg_response_time = health_metrics.get("avg_response_time", 1000)
            max_response_time = health_metrics.get("max_response_time", 5000)
            if max_response_time > 0:
                response_health = 1.0 - (avg_response_time / max_response_time)
                indicators.append(response_health)

            # Disponibilité des modules
            module_status = health_metrics.get("module_status", {})
            if module_status:
                available_modules = sum(
                    1 for status in module_status.values() if status == "available"
                )
                total_modules = len(module_status)
                availability_health = available_modules / total_modules
                indicators.append(availability_health)

            # Moyenne des indicateurs
            if indicators:
                system_health = sum(indicators) / len(indicators)
                return min(max(system_health, 0.0), 1.0)

            return 0.8  # Santé par défaut

        except Exception as e:
            logger.error(f"Erreur calcul santé système: {e}")
            return 0.6

    def calculate_global_score(self) -> dict[str, Any]:
        """Calcule le score cognitif global"""
        try:
            # Récupérer tous les scores
            zeroia_confidence = self.get_zeroia_confidence()
            reflexia_alerts = self.get_reflexia_alerts()
            sandozia_integrity = self.get_sandozia_integrity()
            cognitive_load = self.get_cognitive_load()
            system_health = self.get_system_health()

            # Calculer le score global pondéré
            weights = {
                "zeroia_confidence": 0.25,
                "reflexia_alerts": 0.20,
                "sandozia_integrity": 0.20,
                "cognitive_load": 0.15,
                "system_health": 0.20,
            }

            # Normaliser les alertes (moins d'alertes = meilleur score)
            alert_score = max(0.0, 1.0 - (reflexia_alerts / 10.0))

            # Score global
            global_score = (
                zeroia_confidence * weights["zeroia_confidence"]
                + alert_score * weights["reflexia_alerts"]
                + sandozia_integrity * weights["sandozia_integrity"]
                + (1.0 - cognitive_load) * weights["cognitive_load"]  # Inverser la charge
                + system_health * weights["system_health"]
            )

            # Déterminer le statut
            if global_score >= 0.8:
                status = "excellent"
            elif global_score >= 0.6:
                status = "good"
            elif global_score >= 0.4:
                status = "warning"
            else:
                status = "critical"

            # Créer le score complet
            score_data: dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "global_score": round(global_score, 3),
                "status": status,
                "components": {
                    "zeroia_confidence": round(zeroia_confidence, 3),
                    "reflexia_alerts": reflexia_alerts,
                    "sandozia_integrity": round(sandozia_integrity, 3),
                    "cognitive_load": round(cognitive_load, 3),
                    "system_health": round(system_health, 3),
                },
                "thresholds": self.thresholds,
                "alerts": [],
            }

            # Ajouter des alertes si les seuils sont dépassés
            if zeroia_confidence < self.thresholds["zeroia_confidence"]:
                score_data["alerts"].append(
                    {
                        "type": "zeroia_confidence_low",
                        "value": zeroia_confidence,
                        "threshold": self.thresholds["zeroia_confidence"],
                    }
                )

            if reflexia_alerts > self.thresholds["reflexia_alerts"]:
                score_data["alerts"].append(
                    {
                        "type": "reflexia_alerts_high",
                        "value": reflexia_alerts,
                        "threshold": self.thresholds["reflexia_alerts"],
                    }
                )

            if sandozia_integrity < self.thresholds["sandozia_integrity"]:
                score_data["alerts"].append(
                    {
                        "type": "sandozia_integrity_low",
                        "value": sandozia_integrity,
                        "threshold": self.thresholds["sandozia_integrity"],
                    }
                )

            if cognitive_load > self.thresholds["cognitive_load"]:
                score_data["alerts"].append(
                    {
                        "type": "cognitive_load_high",
                        "value": cognitive_load,
                        "threshold": self.thresholds["cognitive_load"],
                    }
                )

            if system_health < self.thresholds["system_health"]:
                score_data["alerts"].append(
                    {
                        "type": "system_health_low",
                        "value": system_health,
                        "threshold": self.thresholds["system_health"],
                    }
                )

            # Sauvegarder dans l'historique
            self.score_history.append(score_data)
            if len(self.score_history) > self.max_history_size:
                self.score_history.pop(0)

            # Sauvegarder le score actuel
            self.storage.save_state("arkalia_score", score_data, "current")

            return score_data

        except Exception as e:
            logger.error(f"Erreur calcul score global: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "global_score": 0.0,
                "status": "error",
                "error": str(e),
            }

    def generate_score_file(self, output_path: str = "arkalia_score.toml"):
        """Génère le fichier de score au format TOML"""
        try:
            score_data = self.calculate_global_score()

            # Convertir en format TOML
            toml_data = {
                "arkalia_score": {
                    "timestamp": score_data["timestamp"],
                    "global_score": score_data["global_score"],
                    "status": score_data["status"],
                    "components": score_data["components"],
                    "thresholds": score_data["thresholds"],
                    "alerts_count": len(score_data["alerts"]),
                }
            }

            # Écrire le fichier
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                toml.dump(toml_data, f)

            logger.info(f"Score généré: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erreur génération fichier score: {e}")
            return None

    def get_score_history(self, limit: int = 10) -> list:
        """Récupère l'historique des scores"""
        return self.score_history[-limit:] if self.score_history else []

    def get_trend(self) -> str:
        """Calcule la tendance du score"""
        if len(self.score_history) < 2:
            return "stable"

        recent_scores = [s["global_score"] for s in self.score_history[-5:]]
        if len(recent_scores) < 2:
            return "stable"

        # Calculer la tendance
        first_half = sum(recent_scores[: len(recent_scores) // 2]) / (len(recent_scores) // 2)
        second_half = sum(recent_scores[len(recent_scores) // 2 :]) / (len(recent_scores) // 2)

        diff = second_half - first_half

        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "declining"
        else:
            return "stable"


def main():
    """Fonction principale pour générer le score"""
    print("🧠 Arkalia Score Generator")
    print("=" * 40)

    generator = ArkaliaScoreGenerator()

    # Générer le score
    score = generator.calculate_global_score()

    print(f"📊 Score Global: {score['global_score']:.3f}")
    print(f"📈 Statut: {score['status']}")
    print(f"⏰ Timestamp: {score['timestamp']}")

    print("\n🔍 Composants:")
    for component, value in score["components"].items():
        print(f"   {component}: {value}")

    if score["alerts"]:
        print(f"\n🚨 Alertes ({len(score['alerts'])}):")
        for alert in score["alerts"]:
            print(f"   - {alert['type']}: {alert['value']} (seuil: {alert['threshold']})")

    # Générer le fichier
    output_file = generator.generate_score_file()
    if output_file:
        print(f"\n💾 Score sauvegardé: {output_file}")

    # Afficher la tendance
    trend = generator.get_trend()
    print(f"📈 Tendance: {trend}")

    print("\n✅ Score généré avec succès!")


if __name__ == "__main__":
    main()

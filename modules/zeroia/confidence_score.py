#!/usr/bin/env python3
"""
🧠 [CONFIDENCE SCORE] - Roadmap S4-P1 Arkalia-LUNA
Mémoire explicable et scoring décisionnel avancé pour ZeroIA

Fonctionnalités:
- Scoring de confiance multi-facteurs
- Historique décisionnel avec contexte
- Explication des choix IA
- Détection de patterns et apprentissage
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import toml

from core.ark_logger import ark_logger


class ConfidenceScorer:
    """Système de scoring de confiance avec mémoire explicable pour ZeroIA"""

    def __init__(self, state_file: str = "modules/zeroia/state/confidence_memory.toml") -> None:
        self.state_file = Path(state_file)
        self.decision_history: list[dict[str, Any]] = []
        self.pattern_weights = {
            "consistency": 0.25,  # Cohérence avec historique
            "system_health": 0.20,  # État système
            "response_time": 0.15,  # Temps de réponse
            "resource_efficiency": 0.15,  # Efficacité ressources
            "context_relevance": 0.15,  # Pertinence contexte
            "error_rate": 0.10,  # Taux d'erreur
        }
        self.memory = self._load_memory()
        self.confidence_threshold = 0.7
        self.load_config()

    def load_config(self) -> dict[str, Any]:
        """Charge la configuration depuis le fichier TOML."""
        try:
            with open("config/confidence.toml") as f:
                data = toml.load(f)
                return data if isinstance(data, dict) else {}
        except FileNotFoundError:
            return {"threshold": 0.7, "decay_rate": 0.1}
        except Exception:
            return {"threshold": 0.7, "decay_rate": 0.1}

    def _load_memory(self) -> dict:
        """Charge la mémoire décisionnelle"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return toml.load(f)
            except Exception as e:
                ark_logger.info(
                    f"⚠️ [CONFIDENCE] Erreur chargement mémoire: {e}", extra={"module": "zeroia"}
                )

        return {
            "decision_patterns": {},
            "successful_contexts": [],
            "error_contexts": [],
            "performance_metrics": [],
            "learning_weights": self.pattern_weights.copy(),
            "last_update": datetime.now().isoformat(),
        }

    def _save_memory(self):
        """Sauvegarde la mémoire décisionnelle"""
        try:
            self.memory["last_update"] = datetime.now().isoformat()
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.state_file, "w") as f:
                toml.dump(self.memory, f)
        except Exception as e:
            ark_logger.info(
                f"❌ [CONFIDENCE] Erreur sauvegarde mémoire: {e}", extra={"module": "zeroia"}
            )

    def calculate_confidence(
        self, decision: str, context: dict, system_metrics: dict | None = None
    ) -> tuple[float, dict]:
        """
        Calcule le score de confiance avec explication détaillée

        Returns:
            tuple[float, Dict]: (score_confiance, explication_détaillée)
        """
        start_time = time.time()

        # Métriques par défaut si non fournies
        if system_metrics is None:
            system_metrics = {
                "cpu": context.get("cpu", 50.0),
                "ram": context.get("ram", 60.0),
                "response_time_ms": 100,
            }

        # Calcul des scores individuels
        scores: dict[str, Any] = {}
        explanations: dict[str, Any] = {}

        # 1. Score de cohérence avec l'historique
        consistency_score, consistency_explanation = self._score_consistency(decision, context)
        scores["consistency"] = consistency_score
        explanations["consistency"] = consistency_explanation

        # 2. Score de santé système
        health_score, health_explanation = self._score_system_health(system_metrics)
        scores["system_health"] = health_score
        explanations["system_health"] = health_explanation

        # 3. Score de temps de réponse
        response_score, response_explanation = self._score_response_time(system_metrics)
        scores["response_time"] = response_score
        explanations["response_time"] = response_explanation

        # 4. Score d'efficacité ressources
        efficiency_score, efficiency_explanation = self._score_resource_efficiency(system_metrics)
        scores["resource_efficiency"] = efficiency_score
        explanations["resource_efficiency"] = efficiency_explanation

        # 5. Score de pertinence contextuelle
        relevance_score, relevance_explanation = self._score_context_relevance(decision, context)
        scores["context_relevance"] = relevance_score
        explanations["context_relevance"] = relevance_explanation

        # 6. Score basé sur taux d'erreur
        error_score, error_explanation = self._score_error_rate(decision)
        scores["error_rate"] = error_score
        explanations["error_rate"] = error_explanation

        # Score de confiance final pondéré
        final_score = sum(
            scores[factor] * self.memory["learning_weights"][factor] for factor in scores
        )

        # Normalisation entre 0 et 1
        final_score = max(0.0, min(1.0, final_score))

        # Calcul temps de traitement
        processing_time = (time.time() - start_time) * 1000

        # Construction de l'explication complète
        explanation = {
            "final_score": round(final_score, 3),
            "processing_time_ms": round(processing_time, 2),
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
            "factor_scores": {k: round(v, 3) for k, v in scores.items()},
            "factor_weights": self.memory["learning_weights"],
            "explanations": explanations,
            "confidence_level": self._categorize_confidence(final_score),
            "recommendations": self._generate_recommendations(scores, final_score),
        }

        # Mise à jour de la mémoire
        self._update_memory(decision, context, final_score, explanation)

        return final_score, explanation

    def _score_consistency(self, decision: str, context: dict) -> tuple[float, str]:
        """Score la cohérence avec les décisions passées"""
        if not self.memory["decision_patterns"]:
            return 0.5, "Pas d'historique disponible pour comparaison"

        similar_contexts = 0
        consistent_decisions = 0

        for past_context, past_decision in self.memory["decision_patterns"].items():
            try:
                past_ctx = json.loads(past_context)
                similarity = self._calculate_context_similarity(context, past_ctx)

                if similarity > 0.7:  # Contexte similaire
                    similar_contexts += 1
                    if past_decision == decision:
                        consistent_decisions += 1
            except Exception:  # nosec B110
                # Skip invalid pattern data - needed for robustness
                pass

        if similar_contexts == 0:
            return 0.6, "Nouveau type de contexte, apprentissage en cours"

        consistency_ratio = consistent_decisions / similar_contexts

        explanation = (
            f"Décision cohérente avec {consistent_decisions}/{similar_contexts} "
            f"contextes similaires passés ({consistency_ratio:.1%})"
        )

        return consistency_ratio, explanation

    def _score_system_health(self, metrics: dict) -> tuple[float, str]:
        """Score la santé système actuelle"""
        cpu = metrics.get("cpu", 50.0)
        ram = metrics.get("ram", 50.0)

        # Score basé sur la charge système (inversé)
        cpu_score = max(0, (100 - cpu) / 100)
        ram_score = max(0, (100 - ram) / 100)

        health_score = (cpu_score + ram_score) / 2

        explanation = f"Système: CPU {cpu:.1f}%, RAM {ram:.1f}% - "
        if health_score > 0.8:
            explanation += "Excellent état"
        elif health_score > 0.6:
            explanation += "Bon état"
        elif health_score > 0.4:
            explanation += "État dégradé"
        else:
            explanation += "État critique"

        return health_score, explanation

    def _score_response_time(self, metrics: dict) -> tuple[float, str]:
        """Score le temps de réponse"""
        response_time = metrics.get("response_time_ms", 100)

        # Score basé sur temps de réponse (optimal < 200ms)
        if response_time < 50:
            score = 1.0
            level = "Excellent"
        elif response_time < 100:
            score = 0.9
            level = "Très bon"
        elif response_time < 200:
            score = 0.7
            level = "Bon"
        elif response_time < 500:
            score = 0.5
            level = "Moyen"
        else:
            score = 0.2
            level = "Lent"

        explanation = f"Temps de réponse: {response_time}ms - {level}"
        return score, explanation

    def _score_resource_efficiency(self, metrics: dict) -> tuple[float, str]:
        """Score l'efficacité des ressources"""
        cpu = metrics.get("cpu", 50.0)
        ram = metrics.get("ram", 50.0)

        # Zone optimale: 20-60% CPU, 30-70% RAM
        cpu_efficiency = 1.0 - abs(40 - cpu) / 60  # Optimal à 40%
        ram_efficiency = 1.0 - abs(50 - ram) / 50  # Optimal à 50%

        cpu_efficiency = max(0, cpu_efficiency)
        ram_efficiency = max(0, ram_efficiency)

        efficiency = (cpu_efficiency + ram_efficiency) / 2

        explanation = f"Efficacité ressources: CPU {cpu_efficiency:.1%}, RAM {ram_efficiency:.1%}"
        return efficiency, explanation

    def _score_context_relevance(self, decision: str, context: dict) -> tuple[float, str]:
        """Score la pertinence du contexte pour la décision"""
        # Chercher dans context directement ou dans context["status"]
        status = context.get("status", {})
        required_fields = ["cpu", "ram"]
        present_fields = sum(1 for field in required_fields if field in context or field in status)

        # Score de base sur complétude du contexte
        completeness = present_fields / len(required_fields)

        # Bonus pour contexte détaillé
        detail_bonus = min(0.2, len(context) * 0.05)

        relevance = min(1.0, completeness + detail_bonus)

        explanation = (
            f"Contexte: {present_fields}/{len(required_fields)} champs requis, "
            f"{len(context)} champs total"
        )

        return relevance, explanation

    def _score_error_rate(self, decision: str) -> tuple[float, str]:
        """Score basé sur le taux d'erreur historique"""
        error_contexts = self.memory.get("error_contexts", [])
        total_decisions = len(self.memory.get("decision_patterns", {}))

        if total_decisions == 0:
            return 0.8, "Pas d'historique d'erreur disponible"

        error_rate = len(error_contexts) / total_decisions
        error_score = max(0, 1.0 - error_rate * 2)  # Pénalité x2 pour erreurs

        error_count = len(error_contexts)
        explanation = f"Taux d'erreur historique: {error_rate:.1%} ({error_count} erreurs)"
        return error_score, explanation

    def _calculate_context_similarity(self, ctx1: dict, ctx2: dict) -> float:
        """Calcule la similarité entre deux contextes"""
        common_keys = set(ctx1.keys()) & set(ctx2.keys())
        if not common_keys:
            return 0.0

        similarities: list[Any] = []
        for key in common_keys:
            val1, val2 = ctx1[key], ctx2[key]

            if isinstance(val1, int | float) and isinstance(val2, int | float):
                # Similarité numérique (distance normalisée)
                max_val = max(abs(val1), abs(val2), 1)
                similarity = 1.0 - abs(val1 - val2) / max_val
                similarities.append(similarity)
            elif val1 == val2:
                # Égalité exacte
                similarities.append(1.0)
            else:
                # Différence
                similarities.append(0.0)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def _categorize_confidence(self, score: float) -> str:
        """Catégorise le niveau de confiance"""
        if score >= 0.9:
            return "Très élevée"
        elif score >= 0.7:
            return "Élevée"
        elif score >= 0.5:
            return "Moyenne"
        elif score >= 0.3:
            return "Faible"
        else:
            return "Très faible"

    def _generate_recommendations(self, scores: dict, final_score: float) -> list[str]:
        """Génère des recommandations d'amélioration"""
        recommendations: list[Any] = []

        # Analyse des scores faibles
        for factor, score in scores.items():
            if score < 0.4:
                if factor == "system_health":
                    recommendations.append("🔧 Optimiser l'utilisation des ressources système")
                elif factor == "response_time":
                    recommendations.append("⚡ Améliorer les performances de traitement")
                elif factor == "consistency":
                    recommendations.append("🎯 Réviser la cohérence décisionnelle")
                elif factor == "context_relevance":
                    recommendations.append("📊 Enrichir le contexte décisionnel")
                elif factor == "error_rate":
                    recommendations.append("🛠️ Réduire le taux d'erreur")

        # Recommandations globales
        if final_score < 0.5:
            recommendations.append("⚠️ Score de confiance faible - révision recommandée")
        elif final_score > 0.9:
            recommendations.append("✅ Excellente performance - maintenir la qualité")

        return recommendations

    def _update_memory(self, decision: str, context: dict, score: float, explanation: dict):
        """Met à jour la mémoire décisionnelle"""
        try:
            # Ajouter à l'historique des patterns
            context_key = json.dumps(context, sort_keys=True)
            self.memory["decision_patterns"][context_key] = decision

            # Historique des métriques de performance
            if "performance_metrics" not in self.memory:
                self.memory["performance_metrics"] = []

            metric_entry = {
                "timestamp": datetime.now().isoformat(),
                "decision": decision,
                "confidence_score": score,
                "processing_time_ms": explanation["processing_time_ms"],
                "factor_scores": explanation["factor_scores"],
            }

            self.memory["performance_metrics"].append(metric_entry)

            # Limiter l'historique (garder 1000 dernières entrées)
            if len(self.memory["performance_metrics"]) > 1000:
                self.memory["performance_metrics"] = self.memory["performance_metrics"][-1000:]

            # Apprentissage adaptatif des poids
            self._adaptive_weight_learning(score, explanation["factor_scores"])

            # Sauvegarde périodique
            self._save_memory()

        except Exception as e:
            ark_logger.info(
                f"❌ [CONFIDENCE] Erreur mise à jour mémoire: {e}", extra={"module": "zeroia"}
            )

    def _adaptive_weight_learning(self, final_score: float, factor_scores: dict):
        """Apprentissage adaptatif des poids basé sur la performance"""
        if final_score > 0.8:  # Bonne décision
            # Renforcer les facteurs qui ont bien scoré
            for factor, score in factor_scores.items():
                if score > 0.7:
                    self.memory["learning_weights"][factor] *= 1.05
        elif final_score < 0.4:  # Mauvaise décision
            # Réduire l'influence des facteurs mal scorés
            for factor, score in factor_scores.items():
                if score < 0.3:
                    self.memory["learning_weights"][factor] *= 0.95

        # Normalisation des poids pour garder la somme à 1.0
        total_weight = sum(self.memory["learning_weights"].values())
        for factor in self.memory["learning_weights"]:
            self.memory["learning_weights"][factor] /= total_weight

    def get_memory_summary(self) -> dict:
        """Retourne un résumé de la mémoire décisionnelle"""
        metrics = self.memory.get("performance_metrics", [])

        if not metrics:
            return {"status": "Aucune donnée historique"}

        recent_metrics = metrics[-100:]  # 100 dernières décisions

        num_metrics = len(recent_metrics)
        confidence_sum = sum(m["confidence_score"] for m in recent_metrics)
        processing_sum = sum(m["processing_time_ms"] for m in recent_metrics)
        avg_confidence = confidence_sum / num_metrics
        avg_processing = processing_sum / num_metrics

        decision_counts: dict[str, Any] = {}
        for m in recent_metrics:
            decision = m["decision"]
            decision_counts[decision] = decision_counts.get(decision, 0) + 1

        return {
            "total_decisions": len(metrics),
            "recent_decisions": len(recent_metrics),
            "average_confidence": round(avg_confidence, 3),
            "average_processing_time_ms": round(avg_processing, 2),
            "decision_distribution": decision_counts,
            "current_weights": self.memory["learning_weights"],
            "last_update": self.memory["last_update"],
        }

    def update_confidence(self, decision_id: str, new_confidence: float) -> None:
        """Met à jour le score de confiance pour une décision."""
        for decision in self.decision_history:
            if decision.get("id") == decision_id:
                decision["confidence"] = new_confidence
                decision["updated_at"] = datetime.now().isoformat()
                break

    def get_average_confidence(self) -> float:
        """Retourne la moyenne des scores de confiance."""
        if not self.decision_history:
            return 0.0
        total = sum(d.get("confidence", 0.0) for d in self.decision_history)
        return total / len(self.decision_history)

    def decay_confidence(self, days: int = 7) -> None:
        """Applique une décroissance temporelle aux scores de confiance."""
        cutoff_date = datetime.now() - timedelta(days=days)
        for decision in self.decision_history:
            decision_date = datetime.fromisoformat(decision.get("created_at", "1970-01-01"))
            if decision_date < cutoff_date:
                current_confidence = decision.get("confidence", 0.0)
                decayed_confidence = current_confidence * 0.9
                decision["confidence"] = max(0.1, decayed_confidence)

    def save_confidence_data(self) -> None:
        """Sauvegarde les données de confiance."""
        try:
            with open("state/confidence_data.json", "w") as f:
                json.dump(self.decision_history, f, indent=2)
        except Exception:
            pass  # Ignore les erreurs d'écriture

    def load_confidence_data(self) -> None:
        """Charge les données de confiance."""
        try:
            with open("state/confidence_data.json") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.decision_history = data
        except FileNotFoundError:
            self.decision_history = []
        except Exception:
            self.decision_history = []


def main():
    """Test du système de scoring de confiance"""
    scorer = ConfidenceScorer()

    # Test avec un contexte exemple
    test_context = {
        "cpu": 45.0,
        "ram": 60.0,
        "disk_usage": 30.0,
        "active_connections": 15,
    }

    test_decision = "normal"

    ark_logger.info("🧠 [CONFIDENCE SCORER] Test du système...", extra={"module": "zeroia"})

    system_metrics = {"cpu": 45.0, "ram": 60.0, "response_time_ms": 120}
    confidence, explanation = scorer.calculate_confidence(
        test_decision, test_context, system_metrics
    )

    ark_logger.info(f"\n📊 Score de confiance: {confidence:.3f}", extra={"module": "zeroia"})
    ark_logger.info(f"🎯 Niveau: {explanation['confidence_level']}", extra={"module": "zeroia"})
    ark_logger.info(
        f"⏱️ Temps de traitement: {explanation['processing_time_ms']}ms", extra={"module": "zeroia"}
    )

    ark_logger.info("\n🔍 Détail des facteurs:", extra={"module": "zeroia"})
    for factor, score in explanation["factor_scores"].items():
        ark_logger.info(f"  • {factor}: {score:.3f}", extra={"module": "zeroia"})

    ark_logger.info("\n💡 Recommandations:", extra={"module": "zeroia"})
    for rec in explanation["recommendations"]:
        ark_logger.info(f"  {rec}", extra={"module": "zeroia"})

    ark_logger.info("\n📈 Résumé mémoire:", extra={"module": "zeroia"})
    summary = scorer.get_memory_summary()
    for key, value in summary.items():
        ark_logger.info(f"  • {key}: {value}", extra={"module": "zeroia"})


if __name__ == "__main__":
    main()

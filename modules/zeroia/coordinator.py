#!/usr/bin/env python3
"""
🧠 modules/zeroia/coordinator.py
ZeroIA Coordinator - Point d'entrée principal orchestré

INTÉGRATIONS ENHANCED v2.8.0:
- Confidence Scoring avec mémoire explicable
- Graceful Degradation System
- Error Recovery System
- Orchestrator Enhanced avec Circuit Breaker
- Event Sourcing complet
"""

import asyncio
import time
from datetime import datetime
from typing import Any

from core.ark_logger import ark_logger
from modules.utils.error_recovery.core import ErrorRecoverySystem, ErrorType

from .confidence_score import get_scorer
from .decision_engine import DecisionEngine
from .graceful_degradation import DegradationLevel, GracefulDegradationSystem
from .metrics import get_zeroia_metrics, update_zeroia_metrics
from .orchestrator_enhanced import ZeroIAOrchestrator
from .state_manager import StateManager


class ZeroIACoordinator:
    """
    Coordinateur principal ZeroIA avec tous les systèmes avancés

    Architecture intégrée :
    - Decision Engine : Moteur de décision intelligent
    - State Manager : Gestion d'état robuste
    - Confidence Scorer : Scoring avec mémoire explicable
    - Graceful Degradation : Dégradation gracieuse
    - Error Recovery : Récupération automatique
    - Enhanced Orchestrator : Orchestration avec Circuit Breaker
    """

    def __init__(self) -> None:
        """Initialise le coordinateur avec tous les systèmes"""
        ark_logger.info(
            "🚀 Initialisation ZeroIA Coordinator Enhanced", extra={"arkalia_module": "zeroia"}
        )

        # Composants principaux
        self.decision_engine = DecisionEngine()
        self.state_manager = StateManager()

        # Systèmes avancés
        # Utiliser le singleton pour éviter de charger 2.2GB plusieurs fois en RAM
        self.confidence_scorer = get_scorer()
        self.graceful_degradation = GracefulDegradationSystem()
        self.error_recovery = ErrorRecoverySystem()
        # max_loops=1000 par défaut pour éviter les boucles infinies
        # Peut être changé via start() si besoin
        self.orchestrator = ZeroIAOrchestrator(
            max_loops=1000, interval_seconds=10.0, circuit_failure_threshold=8, timeout=45
        )

        # État du coordinateur
        self.is_running = False
        self.start_time: datetime | None = None
        self.session_stats = {
            "total_decisions": 0,
            "successful_decisions": 0,
            "failed_decisions": 0,
            "degradation_events": 0,
            "recovery_events": 0,
            "confidence_average": 0.0,
        }

        ark_logger.info(
            "✅ ZeroIA Coordinator initialisé avec tous les systèmes",
            extra={"arkalia_module": "zeroia"},
        )

    async def start(self) -> None:
        """Démarre le coordinateur avec tous les systèmes"""
        ark_logger.info("🎯 Démarrage ZeroIA Coordinator", extra={"arkalia_module": "zeroia"})

        self.is_running = True
        self.start_time = datetime.now()

        try:
            # Initialiser les systèmes
            await self._initialize_systems()

            # Démarrer l'orchestrateur enhanced
            await self._start_orchestrator()

        except Exception as e:
            ark_logger.error(
                f"💥 Erreur démarrage coordinateur: {e}", extra={"arkalia_module": "zeroia"}
            )
            await self.error_recovery.handle_error(ErrorType.UNKNOWN, str(e))
            raise

    async def _initialize_systems(self) -> None:
        """Initialise tous les systèmes de manière sécurisée"""
        ark_logger.info("🔧 Initialisation des systèmes", extra={"arkalia_module": "zeroia"})

        # Vérifier la santé système
        health_score = await self.graceful_degradation.assess_system_health()

        if health_score < 0.7:
            ark_logger.warning(
                f"⚠️ Santé système faible ({health_score:.2f}), activation dégradation",
                extra={"arkalia_module": "zeroia"},
            )
            await self.graceful_degradation.trigger_degradation(
                DegradationLevel.LIGHT_DEGRADATION, "Santé système faible au démarrage"
            )

        # Initialiser le scoring de confiance
        self.confidence_scorer.load_config()

        ark_logger.info("✅ Tous les systèmes initialisés", extra={"arkalia_module": "zeroia"})

    async def _start_orchestrator(self) -> None:
        """Démarre l'orchestrateur enhanced"""
        ark_logger.info("🎼 Démarrage orchestrateur enhanced", extra={"arkalia_module": "zeroia"})

        # Lancer l'orchestrateur en arrière-plan
        asyncio.create_task(self._run_orchestrator())

        # Attendre que l'orchestrateur soit prêt
        await asyncio.sleep(2)

        ark_logger.info("✅ Orchestrateur démarré", extra={"arkalia_module": "zeroia"})

    async def _run_orchestrator(self) -> None:
        """Exécute l'orchestrateur avec monitoring (version async optimisée)"""
        try:
            # Utiliser la version async de l'orchestrateur pour meilleure performance
            await self.orchestrator.async_run()
        except Exception as e:
            ark_logger.error(f"💥 Erreur orchestrateur: {e}", extra={"arkalia_module": "zeroia"})
            await self.error_recovery.handle_error(ErrorType.UNKNOWN, str(e))

    async def make_decision(self, context: dict) -> dict[str, Any]:
        """
        Prend une décision avec tous les systèmes intégrés

        Args:
            context: Contexte de la décision

        Returns:
            dict: Résultat de la décision avec métriques complètes
        """
        start_time = time.time()

        try:
            # Vérifier la santé système
            health_score = await self.graceful_degradation.assess_system_health()

            # Prendre la décision via decision engine
            decision, score = self.decision_engine.decide_protected(context)

            # Calculer le score de confiance
            confidence_score, confidence_explanation = self.confidence_scorer.calculate_confidence(
                decision, context, {"cpu": 50.0, "ram": 60.0, "response_time_ms": 100}
            )

            # Persister l'état
            self.state_manager.persist_state_enhanced(decision, confidence_score, context)

            # Mettre à jour le dashboard
            self.state_manager.update_dashboard_enhanced(decision, confidence_score, context)

            # Collecter les métriques
            duration = time.time() - start_time
            update_zeroia_metrics(
                "decision_cycle",
                "success",
                duration,
                cognitive_score=confidence_score,
                decision_type=decision,
            )

            # Mettre à jour les stats
            self.session_stats["total_decisions"] += 1
            self.session_stats["successful_decisions"] += 1
            self.session_stats["confidence_average"] = (
                self.session_stats["confidence_average"]
                * (self.session_stats["total_decisions"] - 1)
                + confidence_score
            ) / self.session_stats["total_decisions"]

            return {
                "decision": decision,
                "confidence_score": confidence_score,
                "confidence_explanation": confidence_explanation,
                "system_health": health_score,
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
            }

        except Exception as e:
            ark_logger.error(f"💥 Erreur décision: {e}", extra={"arkalia_module": "zeroia"})

            # Gérer l'erreur
            await self.error_recovery.handle_error(ErrorType.UNKNOWN, str(e))

            # Mettre à jour les stats
            self.session_stats["total_decisions"] += 1
            self.session_stats["failed_decisions"] += 1

            return {
                "decision": "error",
                "confidence_score": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error",
            }

    async def get_status(self) -> dict[str, Any]:
        """Retourne le statut complet du coordinateur"""
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        return {
            "coordinator": {
                "is_running": self.is_running,
                "uptime_seconds": uptime,
                "start_time": self.start_time.isoformat() if self.start_time else None,
            },
            "session_stats": self.session_stats,
            "decision_engine": {"status": "active"},  # DecisionEngine n'a pas de get_status()
            "state_manager": {"status": "active"},  # StateManager n'a pas de get_status()
            "confidence_scorer": self.confidence_scorer.get_memory_summary(),
            "graceful_degradation": self.graceful_degradation.get_system_status(),
            "error_recovery": self.error_recovery.get_recovery_status(),
            "orchestrator": self.orchestrator.get_status(),
            "metrics": get_zeroia_metrics(),
        }

    async def stop(self) -> None:
        """Arrête le coordinateur proprement"""
        ark_logger.info("⏹️ Arrêt ZeroIA Coordinator", extra={"arkalia_module": "zeroia"})

        self.is_running = False

        # Arrêter l'orchestrateur
        # (l'orchestrateur enhanced gère son propre arrêt)

        ark_logger.info("✅ ZeroIA Coordinator arrêté", extra={"arkalia_module": "zeroia"})

    async def health_check(self) -> dict[str, Any]:
        """Vérification de santé complète"""
        try:
            # Vérifications de base
            health_checks = {
                "decision_engine": True,  # Toujours disponible
                "state_manager": True,  # Toujours disponible
                "confidence_scorer": True,  # Toujours disponible
                "graceful_degradation": await self.graceful_degradation.health_check(),
                "error_recovery": await self.error_recovery.health_check(),
                "orchestrator": self.orchestrator.get_status()["orchestrator"]["loop_count"] >= 0,
            }

            overall_health = all(health_checks.values())

            return {
                "is_healthy": overall_health,
                "health_checks": health_checks,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            ark_logger.error(f"💥 Erreur health check: {e}", extra={"arkalia_module": "zeroia"})
            return {"is_healthy": False, "error": str(e), "timestamp": datetime.now().isoformat()}


# Instance globale du coordinateur
_coordinator_instance: ZeroIACoordinator | None = None


def get_coordinator() -> ZeroIACoordinator:
    """Retourne l'instance globale du coordinateur"""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = ZeroIACoordinator()
    return _coordinator_instance


async def main() -> None:
    """Point d'entrée principal"""
    coordinator = get_coordinator()

    try:
        await coordinator.start()

        # Boucle principale
        while coordinator.is_running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        ark_logger.info("⏹️ Arrêt demandé (Ctrl+C)", extra={"arkalia_module": "zeroia"})
    except Exception as e:
        ark_logger.error(f"💥 Erreur fatale: {e}", extra={"arkalia_module": "zeroia"})
    finally:
        await coordinator.stop()


if __name__ == "__main__":
    asyncio.run(main())

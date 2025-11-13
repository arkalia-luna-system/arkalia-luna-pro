"""
ReasonLoopEnhanced - Classe wrapper pour boucle de raisonnement améliorée
"""

import time
from datetime import datetime
from typing import Any

from core.ark_logger import ark_logger
from modules.zeroia.circuit_breaker import CircuitBreaker
from modules.zeroia.error_recovery_system import ErrorRecoverySystem
from modules.zeroia.event_store import EventStore
from modules.zeroia.graceful_degradation import GracefulDegradationSystem

from .loaders import REFLEXIA_STATE
from .loop import reason_loop_enhanced_with_recovery


class ReasonLoopEnhanced:
    """Boucle de raisonnement améliorée pour ZeroIA"""

    def __init__(self, config_path: str | None = None) -> None:
        self.event_store = EventStore()
        self.circuit_breaker = CircuitBreaker()
        self.error_recovery = ErrorRecoverySystem()
        self.graceful_degradation = GracefulDegradationSystem()

        # Configuration
        self.config = {
            "contradiction_threshold": 3,
            "contradiction_cooldown": 60,
            "min_confidence_score": 0.6,
            "decision_timeout": 30,
            "max_retries": 3,
            "sync_interval": 5,  # secondes
            "sync_timeout": 10,  # secondes
            "sync_retries": 3,
        }

        # État
        self.last_decision: str | None = None
        self.decision_count = 0
        self.contradiction_count = 0
        self.last_contradiction: datetime | None = None
        self.confidence_score = 0.85
        self.sync_state: dict[str, Any] = {
            "reflexia": "unknown",
            "last_sync": None,
            "sync_failures": 0,
        }

    def handle_contradiction(self, zeroia_state: str, reflexia_state: str) -> None:
        """Gère une contradiction entre ZeroIA et ReflexIA"""
        now = datetime.now()

        # Incrémenter le compteur de contradictions
        self.contradiction_count += 1
        self.last_contradiction = now

        # Réduire le score de confiance
        self.confidence_score *= 0.8

        # Logger la contradiction
        ark_logger.warning(f"⚠️ CONTRADICTION: ZeroIA={zeroia_state}, ReflexIA={reflexia_state}")

        # Vérifier si nous devons déclencher une récupération
        if self.contradiction_count >= self.config["contradiction_threshold"]:
            self._trigger_recovery()

    def _trigger_recovery(self) -> None:
        """Déclenche une procédure de récupération"""
        ark_logger.info(
            "🔄 Déclenchement de la procédure de récupération", extra={"arkalia_module": "zeroia"}
        )

        # Réinitialiser les compteurs
        self.contradiction_count = 0
        self.decision_count = 0

        # Forcer une synchronisation avec ReflexIA
        self._sync_with_reflexia()

        # Activer le circuit breaker
        self.circuit_breaker.trip()

    def _sync_with_reflexia(self) -> bool:
        """Synchronise avec ReflexIA"""
        try:
            # Simuler une synchronisation
            self.sync_state["reflexia"] = "synced"
            self.sync_state["last_sync"] = datetime.now().isoformat()
            self.sync_state["sync_failures"] = 0
            return True
        except Exception as e:
            ark_logger.error(f"🚨 Erreur synchronisation ReflexIA: {e}")
            if isinstance(self.sync_state["sync_failures"], int):
                self.sync_state["sync_failures"] += 1
            return False

    def _get_reflexia_state(self) -> str | None:
        """Récupère l'état de ReflexIA"""
        try:
            if REFLEXIA_STATE.exists():
                import toml

                state = toml.load(REFLEXIA_STATE)
                if isinstance(state, dict):
                    status = state.get("status", "unknown")
                    if isinstance(status, str):
                        return status
                return "unknown"
        except Exception as e:
            ark_logger.error(f"🚨 Erreur lecture état ReflexIA: {e}")
        return None

    def run_loop(self, max_iterations: int | None = None) -> None:
        """
        Exécute la boucle de raisonnement
        
        Args:
            max_iterations: Nombre maximum d'itérations (None = infini, déconseillé)
        """
        iteration_count = 0
        
        while True:
            try:
                # Vérifier limite d'itérations pour éviter boucles infinies
                if max_iterations is not None and iteration_count >= max_iterations:
                    ark_logger.info(
                        f"⏹️ Limite d'itérations atteinte ({max_iterations})",
                        extra={"arkalia_module": "zeroia"}
                    )
                    break
                
                iteration_count += 1
                decision, score = reason_loop_enhanced_with_recovery()
                self.decision_count += 1

                # Vérifier les contradictions
                reflexia_state = self._get_reflexia_state()
                if reflexia_state and reflexia_state != decision:
                    self.handle_contradiction(decision, reflexia_state)

                # Attendre avant la prochaine itération
                time.sleep(self.config["sync_interval"])

            except KeyboardInterrupt:
                ark_logger.info("⏹️ Arrêt demandé (Ctrl+C)", extra={"arkalia_module": "zeroia"})
                break
            except Exception as e:
                ark_logger.error(
                    f"🚨 Erreur dans la boucle: {e}", extra={"arkalia_module": "zeroia"}
                )
                time.sleep(10)
                # Continuer la boucle après erreur

#!/usr/bin/env python3
# 🔄 modules/zeroia/circuit_breaker.py
# Circuit Breaker Pattern pour ZeroIA

"""
Circuit Breaker pour ZeroIA - Protection cascade failures

Fonctionnalités :
- Circuit breaker avec états (CLOSED, OPEN, HALF_OPEN)
- Retry automatique avec backoff exponentiel
- Métriques et monitoring intégrés
- Event sourcing pour traçabilité
- Gestion d'erreurs spécialisées IA
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import toml

from core.ark_logger import ark_logger

from .event_store import EventStore, EventType


class CircuitState(Enum):
    """États du circuit breaker"""

    CLOSED = "closed"  # Normal, appels passent
    OPEN = "open"  # Circuit ouvert, appels bloqués
    HALF_OPEN = "half_open"  # Test, quelques appels passent


class ZeroIAError(Exception):
    """Exception de base pour ZeroIA"""

    pass


class CognitiveOverloadError(ZeroIAError):
    """Surcharge cognitive détectée"""

    pass


class DecisionIntegrityError(ZeroIAError):
    """Erreur d'intégrité des décisions"""

    pass


class SystemRebootRequired(ZeroIAError):
    """Redémarrage système requis"""

    pass


@dataclass
class CircuitMetrics:
    """Métriques du circuit breaker"""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    consecutive_failures: int = 0
    last_failure_time: datetime | None = None
    state_changes: int = 0
    total_trips: int = 0

    @property
    def failure_rate(self) -> float:
        """Taux d'échec (0.0 à 1.0)"""
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls

    @property
    def success_rate(self) -> float:
        """Taux de succès (0.0 à 1.0)"""
        return 1.0 - self.failure_rate


class CircuitBreaker:
    """
    Circuit Breaker pour ZeroIA

    Protège contre les cascades d'échecs avec :
    - Seuils configurables
    - Timeout automatique
    - Métriques détaillées
    - Event sourcing intégré
    """

    def __init__(
        self, name: str = "default", failure_threshold: int = 5, timeout: int = 60
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: datetime | None = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.contradiction_pairs: set[str] = set()
        self.load_state()
        self.event_store = EventStore()
        self.metrics = CircuitMetrics()

        ark_logger.info(
            f"🔄 CircuitBreaker initialisé: seuil={failure_threshold}, timeout={timeout}s",
            extra={"arkalia_module": "zeroia"},
        )

    def load_state(self) -> None:
        """Charge l'état du circuit breaker depuis le fichier."""
        try:
            with open(f"state/circuit_breaker_{self.name}.toml") as f:
                data = toml.load(f)
                if isinstance(data, dict):
                    self.failure_count = data.get("failure_count", 0)
                    self.state = data.get("state", "CLOSED")
                    last_failure_str = data.get("last_failure_time")
                    if last_failure_str:
                        self.last_failure_time = datetime.fromisoformat(last_failure_str)
        except FileNotFoundError:
            pass
        except Exception:
            pass

    def save_state(self) -> None:
        """Sauvegarde l'état du circuit breaker."""
        try:
            state_data = {
                "failure_count": self.failure_count,
                "state": self.state,
                "last_failure_time": (
                    self.last_failure_time.isoformat() if self.last_failure_time else None
                ),
            }
            with open(f"state/circuit_breaker_{self.name}.toml", "w") as f:
                toml.dump(state_data, f)
        except Exception:
            pass  # Ignore les erreurs d'écriture

    def handle_contradiction(
        self, service1: str, service2: str, decision1: str, decision2: str
    ) -> bool:
        """Gère une contradiction entre deux services"""
        contradiction_key = f"{service1}:{service2}:{decision1}:{decision2}"

        if contradiction_key not in self.contradiction_pairs:
            self.contradiction_pairs.add(contradiction_key)
            self.metrics.total_trips += 1
            ark_logger.warning(
                f"⚠️ Circuit ouvert après {len(self.contradiction_pairs)} contradictions",
                extra={"arkalia_module": "zeroia"},
            )
            return True

        return False

    def reset_contradictions(self):
        """Réinitialise le compteur de contradictions"""
        self.contradiction_pairs.clear()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Exécute une fonction protégée par le circuit breaker

        Args:
            func: Fonction à exécuter
            *args, **kwargs: Arguments de la fonction

        Returns:
            Résultat de la fonction

        Raises:
            SystemRebootRequired: Si circuit ouvert trop longtemps
            CognitiveOverloadError: Si surcharge détectée
        """
        self.metrics.total_calls += 1

        # Vérifier l'état du circuit
        if self.state == "OPEN":
            if self.should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                self._log_blocked_call()
                raise SystemRebootRequired(
                    f"Circuit breaker {self.name} is OPEN - trop d'échecs consécutifs "
                    f"({self.metrics.consecutive_failures})"
                )

        try:
            # Tenter l'appel directement (retry simplifié)
            result = func(*args, **kwargs)
            self.on_success()
            return result

        except Exception as e:
            self.on_failure(e)
            raise

    def _execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Exécute la fonction avec retry automatique mais sans masquer les exceptions"""
        # Première tentative sans retry pour les erreurs attendues
        try:
            return func(*args, **kwargs)
        except Exception:
            # Pour les autres erreurs, on peut utiliser tenacity
            # Mais ici on va simplifier pour éviter les problèmes de wrapping
            raise

    def on_success(self) -> None:
        """Gère un appel réussi"""
        self.metrics.successful_calls += 1
        self.metrics.consecutive_failures = 0
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None
        self.save_state()

        # Event sourcing
        self.event_store.add_event(
            EventType.CIRCUIT_SUCCESS,
            {
                "state": self.state,
                "success_rate": self.metrics.success_rate,
                "consecutive_failures": self.metrics.consecutive_failures,
            },
        )

    def on_failure(self, exception: Exception) -> None:
        """Gère un échec d'appel"""
        self.metrics.failed_calls += 1
        self.metrics.consecutive_failures += 1
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

        self.save_state()

        ark_logger.warning(
            f"🚨 CircuitBreaker échec: {exception} "
            f"(consécutif: {self.metrics.consecutive_failures})"
        )

        # Event sourcing
        self.event_store.add_event(
            EventType.CIRCUIT_FAILURE,
            {
                "state": self.state,
                "exception": str(exception),
                "consecutive_failures": self.metrics.consecutive_failures,
                "failure_rate": self.metrics.failure_rate,
            },
        )

    def _on_unexpected_error(self, exception: Exception) -> None:
        """Gère une erreur inattendue"""
        ark_logger.error(
            f"💥 CircuitBreaker erreur inattendue: {exception}", extra={"arkalia_module": "zeroia"}
        )
        self.metrics.failed_calls += 1

        # Event sourcing pour erreur critique
        self.event_store.add_event(
            EventType.SYSTEM_ERROR,
            {
                "state": self.state,
                "error": str(exception),
                "error_type": type(exception).__name__,
            },
        )

    def should_attempt_reset(self) -> bool:
        """Vérifie si on peut tenter une réinitialisation"""
        if self.last_failure_time is None:
            return True

        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.timeout

    def _transition_to_closed(self) -> None:
        """Transition vers l'état CLOSED"""
        old_state = self.state
        self.state = "CLOSED"
        self.metrics.state_changes += 1
        ark_logger.info(
            f"🔄 CircuitBreaker: {old_state} → {self.state}", extra={"arkalia_module": "zeroia"}
        )

        self.event_store.add_event(
            EventType.STATE_CHANGE,
            {
                "old_state": old_state,
                "new_state": self.state,
                "reason": "recovery_successful",
            },
        )

    def _transition_to_open(self) -> None:
        """Transition vers l'état OPEN"""
        old_state = self.state
        self.state = "OPEN"
        self.last_failure_time = datetime.now()
        self.metrics.state_changes += 1
        ark_logger.error(
            f"🚨 CircuitBreaker: {old_state} → {self.state} (seuil atteint)",
            extra={"arkalia_module": "zeroia"},
        )

        self.event_store.add_event(
            EventType.STATE_CHANGE,
            {
                "old_state": old_state,
                "new_state": self.state,
                "reason": "failure_threshold_exceeded",
                "consecutive_failures": self.metrics.consecutive_failures,
            },
        )

    def _transition_to_half_open(self) -> None:
        """Transition vers l'état HALF_OPEN"""
        old_state = self.state
        self.state = "HALF_OPEN"
        self.metrics.state_changes += 1
        ark_logger.info(
            f"🔄 CircuitBreaker: {old_state} → {self.state} (test recovery)",
            extra={"arkalia_module": "zeroia"},
        )

        self.event_store.add_event(
            EventType.STATE_CHANGE,
            {
                "old_state": old_state,
                "new_state": self.state,
                "reason": "timeout_reached",
            },
        )

    def _log_blocked_call(self) -> None:
        """Log d'un appel bloqué"""
        ark_logger.warning(
            f"🛑 CircuitBreaker bloque un appel (état: {self.state})",
            extra={"arkalia_module": "zeroia"},
        )

        self.event_store.add_event(
            EventType.CALL_BLOCKED,
            {
                "state": self.state,
                "consecutive_failures": self.metrics.consecutive_failures,
                "time_since_failure": (
                    (datetime.now() - self.last_failure_time).total_seconds()
                    if self.last_failure_time
                    else None
                ),
            },
        )

    def reset(self) -> None:
        """Réinitialise manuellement le circuit breaker"""
        old_state = self.state
        self.failure_count = 0
        self.state = "CLOSED"
        self.metrics.consecutive_failures = 0
        self.last_failure_time = None
        self.metrics.state_changes += 1
        self.save_state()

        ark_logger.info(
            f"🔄 CircuitBreaker réinitialisé manuellement: {old_state} → {self.state}",
            extra={"arkalia_module": "zeroia"},
        )

        self.event_store.add_event(
            EventType.MANUAL_RESET,
            {"old_state": old_state, "new_state": self.state},
        )

    def get_status(self) -> dict[str, Any]:
        """Retourne le statut complet du circuit breaker"""
        return {
            "name": self.name,
            "state": self.state,
            "metrics": {
                "total_calls": self.metrics.total_calls,
                "successful_calls": self.metrics.successful_calls,
                "failed_calls": self.metrics.failed_calls,
                "consecutive_failures": self.metrics.consecutive_failures,
                "failure_rate": self.metrics.failure_rate,
                "success_rate": self.metrics.success_rate,
                "state_changes": self.metrics.state_changes,
                "total_trips": self.metrics.total_trips,
            },
            "config": {
                "failure_threshold": self.failure_threshold,
                "timeout": self.timeout,
            },
            "last_failure_time": (
                self.last_failure_time.isoformat() if self.last_failure_time else None
            ),
        }

    def trip(self) -> None:
        """Déclenche le circuit breaker"""
        self.state = "OPEN"
        self.last_failure_time = datetime.now()
        ark_logger.warning("🔌 Circuit breaker déclenché", extra={"arkalia_module": "zeroia"})

        if self.event_store:
            self.event_store.store_event(
                "circuit_breaker_tripped",
                {
                    "state": self.state,
                    "failure_count": self.failure_count,
                    "last_failure": self.last_failure_time,
                },
            )

    def allow_request(self) -> bool:
        """Vérifie si une requête peut être autorisée"""
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            now = datetime.now()
            if (
                self.last_failure_time
                and (now - self.last_failure_time).total_seconds() >= self.timeout
            ):
                self.state = "HALF_OPEN"
                ark_logger.info(
                    "🔌 Circuit breaker en mode semi-ouvert", extra={"arkalia_module": "zeroia"}
                )
                return True
            return False

        # État HALF_OPEN
        return True

    def record_failure(self) -> None:
        """Enregistre un échec"""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.trip()

        if self.event_store:
            self.event_store.store_event(
                "circuit_breaker_failure",
                {"failure_count": self.failure_count, "state": self.state},
            )

    def record_success(self) -> None:
        """Enregistre un succès"""
        if self.state == "HALF_OPEN":
            self.reset()

        if self.event_store:
            self.event_store.store_event("circuit_breaker_success", {"state": self.state})

    def add_contradiction_pair(self, pair: str) -> None:
        """Ajoute une paire de contradictions."""
        self.contradiction_pairs.add(pair)

    def _handle_unexpected_error(self, error: Exception) -> None:
        """Gère les erreurs inattendues"""
        ark_logger.warning(
            f"Erreur inattendue dans Circuit Breaker: {error}", extra={"arkalia_module": "zeroia"}
        )
        self.metrics.unexpected_errors += 1

        # Enregistrer l'événement
        if self.event_store:
            try:
                self.event_store.add_event(
                    EventType.SYSTEM_ERROR,
                    {
                        "error_type": "unexpected_error",
                        "error_message": str(error),
                        "circuit_state": self.state.value,
                    },
                )
            except Exception as e:
                ark_logger.error(
                    f"Erreur lors de l'enregistrement de l'événement: {e}",
                    extra={"arkalia_module": "zeroia"},
                )

    def detect_contradictions(self, decisions: list[dict[str, Any]]) -> list[str]:
        """Détecte les contradictions dans les décisions."""
        contradictions: list[Any] = []
        for decision in decisions:
            decision_id = decision.get("id", "")
            if decision_id in self.contradiction_pairs:
                contradictions.append(decision_id)
        return contradictions

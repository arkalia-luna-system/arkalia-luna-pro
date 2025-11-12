#!/usr/bin/env python3
"""
🔌 Circuit Breaker - Disjoncteur intelligent global
🎯 Protection contre les défaillances en cascade
"""

import asyncio
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from core.ark_logger import ark_logger


class CircuitState(Enum):
    """États du circuit breaker"""

    CLOSED = "closed"  # Normal, requêtes autorisées
    OPEN = "open"  # Défaillance, requêtes bloquées
    HALF_OPEN = "half_open"  # Test de récupération


@dataclass
class CircuitBreakerConfig:
    """Configuration du circuit breaker"""

    failure_threshold: int = 5  # Nombre d'échecs avant ouverture
    recovery_timeout: int = 60  # Temps avant tentative de récupération (secondes)
    expected_exception: type = Exception  # Type d'exception à surveiller
    success_threshold: int = 2  # Nombre de succès pour fermer le circuit
    timeout: float | None = None  # Timeout des requêtes (secondes)
    enable_monitoring: bool = True  # Activer le monitoring


@dataclass
class CircuitBreakerMetrics:
    """Métriques du circuit breaker"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    circuit_opens: int = 0
    circuit_closes: int = 0
    last_failure_time: datetime | None = None
    last_success_time: datetime | None = None
    current_failure_count: int = 0
    current_success_count: int = 0


class CircuitBreaker:
    """
    🔌 Disjoncteur intelligent pour la résilience
    🎯 Protection automatique contre les défaillances
    """

    def __init__(self, name: str, config: CircuitBreakerConfig | None = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()

        # État du circuit
        self.state = CircuitState.CLOSED
        self.last_state_change = datetime.now()

        # Métriques
        self.metrics = CircuitBreakerMetrics()

        # Thread safety
        self._lock = threading.RLock()

        ark_logger.info(f"🔌 CircuitBreaker '{name}' initialisé", extra={"arkalia_module": "core"})

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Exécute une fonction avec protection du circuit breaker"""
        with self._lock:
            # Vérifier l'état du circuit
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._set_state(CircuitState.HALF_OPEN)
                    ark_logger.info(
                        f"🔌 Circuit '{self.name}' en mode half-open",
                        extra={"arkalia_module": "core"},
                    )
                else:
                    raise Exception(f"Circuit '{self.name}' ouvert - requête rejetée")

            # Exécuter la fonction
            start_time = time.time()
            success = False

            try:
                # Exécuter avec timeout si configuré
                if self.config.timeout:
                    result = self._execute_with_timeout(func, *args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                success = True
                self._on_success()
                return result

            except Exception as e:
                self._on_failure(e)
                raise e from e

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Exécute une fonction asynchrone avec protection"""
        with self._lock:
            # Vérifier l'état du circuit
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._set_state(CircuitState.HALF_OPEN)
                    ark_logger.info(
                        f"🔌 Circuit '{self.name}' en mode half-open",
                        extra={"arkalia_module": "core"},
                    )
                else:
                    raise Exception(f"Circuit '{self.name}' ouvert - requête rejetée")

            # Exécuter la fonction
            start_time = time.time()
            success = False

            try:
                # Exécuter avec timeout si configuré
                if self.config.timeout:
                    result = await self._execute_async_with_timeout(func, *args, **kwargs)
                else:
                    result = await func(*args, **kwargs)

                success = True
                self._on_success()
                return result

            except Exception as e:
                self._on_failure(e)
                raise e from e

    def get_state(self) -> CircuitState:
        """Récupère l'état actuel du circuit"""
        with self._lock:
            return self.state

    def get_metrics(self) -> dict[str, Any]:
        """Récupère les métriques du circuit breaker"""
        with self._lock:
            total_requests = self.metrics.total_requests
            success_rate = (
                self.metrics.successful_requests / total_requests * 100
                if total_requests > 0
                else 0.0
            )

            return {
                "name": self.name,
                "state": self.state.value,
                "last_state_change": self.last_state_change.isoformat(),
                "total_requests": total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "timeout_requests": self.metrics.timeout_requests,
                "success_rate": round(success_rate, 2),
                "current_failure_count": self.metrics.current_failure_count,
                "current_success_count": self.metrics.current_success_count,
                "circuit_opens": self.metrics.circuit_opens,
                "circuit_closes": self.metrics.circuit_closes,
                "last_failure_time": (
                    self.metrics.last_failure_time.isoformat()
                    if self.metrics.last_failure_time
                    else None
                ),
                "last_success_time": (
                    self.metrics.last_success_time.isoformat()
                    if self.metrics.last_success_time
                    else None
                ),
            }

    def reset(self) -> bool:
        """Force la réinitialisation du circuit"""
        with self._lock:
            self._set_state(CircuitState.CLOSED)
            self.metrics.current_failure_count = 0
            self.metrics.current_success_count = 0
            ark_logger.info(
                f"🔌 Circuit '{self.name}' réinitialisé manuellement",
                extra={"arkalia_module": "core"},
            )
            return True

    def _set_state(self, new_state: CircuitState) -> None:
        """Change l'état du circuit"""
        if self.state != new_state:
            self.state = new_state
            self.last_state_change = datetime.now()

            if new_state == CircuitState.OPEN:
                self.metrics.circuit_opens += 1
                ark_logger.warning(
                    f"🔌 Circuit '{self.name}' ouvert", extra={"arkalia_module": "core"}
                )
            elif new_state == CircuitState.CLOSED:
                self.metrics.circuit_closes += 1
                ark_logger.info(f"🔌 Circuit '{self.name}' fermé", extra={"arkalia_module": "core"})

    def _should_attempt_reset(self) -> bool:
        """Détermine si on doit tenter une réinitialisation"""
        if self.state != CircuitState.OPEN:
            return False

        time_since_open = datetime.now() - self.last_state_change
        return time_since_open.total_seconds() >= self.config.recovery_timeout

    def _on_success(self) -> None:
        """Gère un succès"""
        self.metrics.total_requests += 1
        self.metrics.successful_requests += 1
        self.metrics.last_success_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            self.metrics.current_success_count += 1
            if self.metrics.current_success_count >= self.config.success_threshold:
                self._set_state(CircuitState.CLOSED)
                self.metrics.current_success_count = 0
                self.metrics.current_failure_count = 0
                ark_logger.info(
                    f"🔌 Circuit '{self.name}' fermé après récupération",
                    extra={"arkalia_module": "core"},
                )
        else:
            # Reset les compteurs en mode fermé
            self.metrics.current_failure_count = 0

    def _on_failure(self, exception: Exception) -> None:
        """Gère un échec"""
        self.metrics.total_requests += 1
        self.metrics.failed_requests += 1
        self.metrics.last_failure_time = datetime.now()

        # Vérifier si c'est le type d'exception attendu
        if isinstance(exception, self.config.expected_exception):
            self.metrics.current_failure_count += 1

            if self.state == CircuitState.HALF_OPEN:
                # Retourner en mode ouvert
                self._set_state(CircuitState.OPEN)
                self.metrics.current_success_count = 0
                ark_logger.warning(
                    f"🔌 Circuit '{self.name}' rouvert après échec",
                    extra={"arkalia_module": "core"},
                )
            elif self.state == CircuitState.CLOSED:
                # Vérifier si on doit ouvrir le circuit
                if self.metrics.current_failure_count >= self.config.failure_threshold:
                    self._set_state(CircuitState.OPEN)
                    failure_count = self.metrics.current_failure_count
                    ark_logger.error(
                        f"🔌 Circuit '{self.name}' ouvert après {failure_count} échecs",
                        extra={"arkalia_module": "core"},
                    )

        ark_logger.debug(
            f"🔌 Échec circuit '{self.name}': {exception}", extra={"arkalia_module": "core"}
        )

    def _execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Exécute une fonction avec timeout"""
        try:
            # Utiliser asyncio pour le timeout même en mode synchrone
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def async_wrapper():
                return func(*args, **kwargs)

            result = loop.run_until_complete(
                asyncio.wait_for(async_wrapper(), timeout=self.config.timeout)
            )
            return result

        except asyncio.TimeoutError as err:
            self.metrics.timeout_requests += 1
            raise TimeoutError(f"Timeout après {self.config.timeout} secondes") from err
        finally:
            loop.close()

    async def _execute_async_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Exécute une fonction asynchrone avec timeout"""
        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout)
        except asyncio.TimeoutError as err:
            self.metrics.timeout_requests += 1
            raise TimeoutError(f"Timeout après {self.config.timeout} secondes") from err


class CircuitBreakerRegistry:
    """
    📋 Registre global des circuit breakers
    🎯 Gestion centralisée de tous les disjoncteurs
    """

    def __init__(self):
        self._circuits: dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()

        ark_logger.info("📋 CircuitBreakerRegistry initialisé", extra={"arkalia_module": "core"})

    def get_or_create(
        self, name: str, config: CircuitBreakerConfig | None = None
    ) -> CircuitBreaker:
        """Récupère ou crée un circuit breaker"""
        with self._lock:
            if name not in self._circuits:
                self._circuits[name] = CircuitBreaker(name, config)
                ark_logger.info(
                    f"📋 Circuit breaker créé: {name}", extra={"arkalia_module": "core"}
                )

            return self._circuits[name]

    def get(self, name: str) -> CircuitBreaker | None:
        """Récupère un circuit breaker existant"""
        with self._lock:
            return self._circuits.get(name)

    def remove(self, name: str) -> bool:
        """Supprime un circuit breaker"""
        with self._lock:
            if name in self._circuits:
                del self._circuits[name]
                ark_logger.info(
                    f"📋 Circuit breaker supprimé: {name}", extra={"arkalia_module": "core"}
                )
                return True
            return False

    def get_all_metrics(self) -> dict[str, dict[str, Any]]:
        """Récupère les métriques de tous les circuit breakers"""
        with self._lock:
            return {name: circuit.get_metrics() for name, circuit in self._circuits.items()}

    def reset_all(self) -> dict[str, bool]:
        """Réinitialise tous les circuit breakers"""
        with self._lock:
            results = {}
            for name, circuit in self._circuits.items():
                results[name] = circuit.reset()
            return results

    def get_global_stats(self) -> dict[str, Any]:
        """Récupère les statistiques globales"""
        with self._lock:
            total_circuits = len(self._circuits)
            open_circuits = sum(
                1 for c in self._circuits.values() if c.get_state() == CircuitState.OPEN
            )
            half_open_circuits = sum(
                1 for c in self._circuits.values() if c.get_state() == CircuitState.HALF_OPEN
            )
            closed_circuits = sum(
                1 for c in self._circuits.values() if c.get_state() == CircuitState.CLOSED
            )

            return {
                "total_circuits": total_circuits,
                "open_circuits": open_circuits,
                "half_open_circuits": half_open_circuits,
                "closed_circuits": closed_circuits,
                "circuits": list(self._circuits.keys()),
            }


# Instance globale
_registry: CircuitBreakerRegistry | None = None


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Récupère l'instance globale du registre"""
    global _registry
    if _registry is None:
        _registry = CircuitBreakerRegistry()
    return _registry


def circuit_breaker(name: str, config: CircuitBreakerConfig | None = None):
    """Décorateur pour protéger une fonction avec un circuit breaker"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            registry = get_circuit_breaker_registry()
            circuit = registry.get_or_create(name, config)
            return circuit.call(func, *args, **kwargs)

        async def async_wrapper(*args, **kwargs):
            registry = get_circuit_breaker_registry()
            circuit = registry.get_or_create(name, config)
            return await circuit.call_async(func, *args, **kwargs)

        # Retourner le wrapper approprié selon le type de fonction
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator

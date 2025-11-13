"""
Initialization - Initialisation des composants Reason Loop
"""

from typing import Any

from core.ark_logger import ark_logger
from modules.zeroia.circuit_breaker import CircuitBreaker
from modules.zeroia.error_recovery_system import ErrorRecoverySystem
from modules.zeroia.event_store import EventStore
from modules.zeroia.graceful_degradation import GracefulDegradationSystem

# === Instances globales Circuit Breaker et Event Store ===
circuit_breaker: CircuitBreaker | None = None
event_store: EventStore | None = None
error_recovery: ErrorRecoverySystem | None = None
graceful_degradation: GracefulDegradationSystem | None = None


def initialize_components() -> tuple[CircuitBreaker, EventStore]:
    """Rétrocompatibilité - initialise seulement CB + ES"""
    cb, es, _, _ = initialize_components_with_recovery()
    return cb, es


def initialize_components_with_recovery() -> tuple[Any, Any, Any, Any]:
    """Initialize components with singleton pattern to prevent repeated initialization"""
    global circuit_breaker, event_store, error_recovery, graceful_degradation

    if circuit_breaker is not None and event_store is not None:
        return circuit_breaker, event_store, error_recovery, graceful_degradation

    try:
        circuit_breaker = CircuitBreaker()
        event_store = EventStore()
        error_recovery = ErrorRecoverySystem()
        graceful_degradation = GracefulDegradationSystem()

        ark_logger.info(
            "🚀 Composants Enhanced + Error Recovery initialisés",
            extra={"arkalia_module": "zeroia"},
        )
        return circuit_breaker, event_store, error_recovery, graceful_degradation

    except Exception as e:
        ark_logger.error(
            f"❌ Erreur initialisation composants: {e}", extra={"arkalia_module": "zeroia"}
        )
        raise

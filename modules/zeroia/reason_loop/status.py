"""
Status - Fonctions de statut et monitoring
"""

from typing import Any

from core.ark_logger import ark_logger
from modules.zeroia.circuit_breaker import CircuitBreaker
from modules.zeroia.event_store import EventStore

from .initialization import initialize_components_with_recovery


def get_circuit_status() -> dict:
    """Retourne le statut du circuit breaker"""
    cb, es, _, _ = initialize_components_with_recovery()
    status = cb.get_status()
    if isinstance(status, dict):
        return status
    return {}


def get_event_analytics() -> dict:
    """Retourne les analytics des événements"""
    cb, es, _, _ = initialize_components_with_recovery()
    analytics = es.get_analytics()
    if isinstance(analytics, dict):
        return analytics
    return {}


def reset_circuit_breaker() -> None:
    """Réinitialise manuellement le circuit breaker"""
    cb, es, _, _ = initialize_components_with_recovery()
    cb.reset()
    ark_logger.info(
        "🔄 Circuit breaker réinitialisé manuellement", extra={"arkalia_module": "zeroia"}
    )


def cleanup_components(circuit_breaker: CircuitBreaker, event_store: EventStore) -> None:
    """
    Nettoie les composants enhanced à la fin de l'orchestration

    Args:
        circuit_breaker: Instance Circuit Breaker à nettoyer
        event_store: Instance Event Store à nettoyer
    """
    from modules.zeroia.event_store import EventType

    ark_logger.info("🧹 Cleanup des composants enhanced...", extra={"arkalia_module": "zeroia"})

    try:
        # Logs finaux du circuit breaker
        status = circuit_breaker.get_status()
        ark_logger.info(f"🔄 Circuit Breaker final - État: {status['state']}")
        ark_logger.info(f"📊 Métriques finales - Succès: {status['metrics']['success_rate']:.2f}%")

        # Analytics finaux event store
        analytics = event_store.get_analytics()
        ark_logger.info(f"📋 Event Store final - {analytics['total_events']} événements")

        # Event de cleanup
        event_store.add_event(
            EventType.STATE_CHANGE,
            {
                "action": "components_cleanup",
                "circuit_final_state": status["state"],
                "total_events": analytics["total_events"],
            },
            module="reason_loop_enhanced",
        )

        ark_logger.info("✅ Cleanup terminé avec succès", extra={"arkalia_module": "zeroia"})

    except Exception as e:
        ark_logger.error(f"⚠️ Erreur pendant cleanup: {e}")


def get_error_recovery_status() -> dict:
    """Retourne le statut du système Error Recovery"""
    try:
        _, _, error_recovery, _ = initialize_components_with_recovery()
        if error_recovery:
            status = error_recovery.get_recovery_status()
            if isinstance(status, dict):
                return status
        return {"status": "unavailable", "reason": "module_not_loaded"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_degradation_status() -> dict:
    """Retourne le statut du système Graceful Degradation"""
    try:
        _, _, _, graceful_degradation = initialize_components_with_recovery()
        if graceful_degradation:
            status = graceful_degradation.get_system_status()
            if isinstance(status, dict):
                return status
        return {"status": "unavailable", "reason": "module_not_loaded"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


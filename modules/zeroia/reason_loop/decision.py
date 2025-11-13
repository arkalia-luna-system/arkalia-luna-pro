"""
Decision - Logique de décision protégée par circuit breaker
"""

from datetime import datetime
from typing import Any

from modules.zeroia.circuit_breaker import CognitiveOverloadError, DecisionIntegrityError

# === Variables globales pour anti-répétition ===
LAST_DECISION: str | None = None
LAST_DECISION_TIME: datetime | None = None
MIN_DECISION_INTERVAL = 30  # seconds


def decide_protected(context: dict) -> tuple[str, float]:
    """
    Fonction de décision protégée par circuit breaker

    Args:
        context: Contexte système

    Returns:
        Tuple (décision, score de confiance)

    Raises:
        CognitiveOverloadError: Si surcharge détectée
        DecisionIntegrityError: Si intégrité compromise
    """
    status = context.get("status", {})
    severity = status.get("severity", "none")
    cpu = status.get("cpu", 0)

    # Validation des données d'entrée
    if not isinstance(cpu, int | float) or cpu < 0 or cpu > 100:
        raise DecisionIntegrityError(f"CPU invalide: {cpu} (doit être 0-100)")

    if severity not in ["none", "normal", "low", "medium", "high", "critical"]:
        raise DecisionIntegrityError(f"Severity invalide: {severity}")

    # Détection de surcharge cognitive
    if cpu > 95:
        raise CognitiveOverloadError(f"CPU critique: {cpu}% - système surchargé")

    # Logique de décision avec seuils adaptatifs
    if should_lower_cpu_threshold() and cpu > 70:
        return "reduce_load", 0.75
    if severity == "critical":
        return "emergency_shutdown", 1.0
    if cpu > 80:
        return "reduce_load", 0.8
    if cpu > 60:
        return "monitor", 0.6

    # Traiter "normal" comme "none" pour la logique de décision
    if severity in ["none", "normal"]:
        return "normal", 0.4

    return "monitor", 0.5


def should_process_decision(new_decision: str) -> bool:
    """Évite les répétitions excessives de la même décision"""
    global LAST_DECISION, LAST_DECISION_TIME

    current_time = datetime.now()

    # Si c'est une nouvelle décision différente, on l'accepte
    if new_decision != LAST_DECISION:
        LAST_DECISION = new_decision
        LAST_DECISION_TIME = current_time
        return True

    # Si c'est la même décision, on vérifie l'intervalle de temps
    if LAST_DECISION_TIME is None:
        LAST_DECISION_TIME = current_time
        return True

    time_diff = (current_time - LAST_DECISION_TIME).total_seconds()

    # On accepte la répétition seulement si assez de temps s'est écoulé
    if time_diff >= MIN_DECISION_INTERVAL:
        LAST_DECISION_TIME = current_time
        return True

    return False


def should_lower_cpu_threshold() -> bool:
    """
    Détermine si le seuil CPU doit être abaissé (logique simple, à adapter selon besoins).
    Ici, on retourne False par défaut (comportement safe).
    """
    return False


"""
📊 Métriques Prometheus standardisées pour Security

Métriques requises :
- arkalia_module_name
- arkalia_uptime_seconds
- arkalia_last_successful_interaction_timestamp
- arkalia_cognitive_score
"""

import time

from prometheus_client import Counter, Gauge, Histogram

# Métriques standardisées Arkalia-LUNA
arkalia_module_name = Gauge("arkalia_module_name", "Nom du module Arkalia", ["module"])

arkalia_uptime_seconds = Gauge(
    "arkalia_uptime_seconds", "Temps de fonctionnement du module en secondes", ["module"]
)

arkalia_last_successful_interaction_timestamp = Gauge(
    "arkalia_last_successful_interaction_timestamp",
    "Timestamp de la dernière interaction réussie",
    ["module"],
)

arkalia_cognitive_score = Gauge(
    "arkalia_cognitive_score", "Score cognitif du module (0.0-1.0)", ["module"]
)

# Métriques spécifiques Security
security_vault_secrets_total = Counter(
    "security_vault_secrets_total",
    "Nombre total de secrets dans le vault",
    ["secret_type", "status"],
)

security_rotation_events = Counter(
    "security_rotation_events_total",
    "Nombre d'événements de rotation de secrets",
    ["rotation_type", "status"],
)

security_integrity_violations = Counter(
    "security_integrity_violations_total",
    "Nombre de violations d'intégrité détectées",
    ["violation_type", "severity"],
)

security_audit_events = Counter(
    "security_audit_events_total", "Nombre d'événements d'audit", ["event_type", "level"]
)

security_sandbox_executions = Histogram(
    "security_sandbox_execution_duration_seconds",
    "Durée d'exécution dans le sandbox",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0],
)


# Initialisation des métriques standardisées
def init_security_metrics():
    """Initialise les métriques standardisées pour Security"""
    module_name = "security"

    # Définir le nom du module
    arkalia_module_name.labels(module=module_name).set(1)

    # Initialiser l'uptime
    start_time = time.time()
    arkalia_uptime_seconds.labels(module=module_name).set(start_time)

    # Initialiser le timestamp de dernière interaction
    arkalia_last_successful_interaction_timestamp.labels(module=module_name).set(start_time)

    # Initialiser le score cognitif (sera mis à jour par la logique)
    arkalia_cognitive_score.labels(module=module_name).set(0.90)


def update_security_metrics(
    event_type: str,
    status: str,
    duration: float | None = None,
    cognitive_score: float | None = None,
):
    """Met à jour les métriques Security"""
    module_name = "security"

    # Mettre à jour l'uptime
    arkalia_uptime_seconds.labels(module=module_name).set(time.time())

    # Mettre à jour le timestamp de dernière interaction si succès
    if status == "success":
        arkalia_last_successful_interaction_timestamp.labels(module=module_name).set(time.time())

    # Mettre à jour le score cognitif si fourni
    if cognitive_score is not None:
        arkalia_cognitive_score.labels(module=module_name).set(cognitive_score)

    # Enregistrer la durée si fournie
    if duration is not None:
        security_sandbox_executions.observe(duration)


def record_vault_secret(secret_type: str, status: str):
    """Enregistre un secret dans le vault"""
    security_vault_secrets_total.labels(secret_type=secret_type, status=status).inc()


def record_rotation_event(rotation_type: str, status: str):
    """Enregistre un événement de rotation"""
    security_rotation_events.labels(rotation_type=rotation_type, status=status).inc()


def record_integrity_violation(violation_type: str, severity: str):
    """Enregistre une violation d'intégrité"""
    security_integrity_violations.labels(violation_type=violation_type, severity=severity).inc()


def record_audit_event(event_type: str, level: str):
    """Enregistre un événement d'audit"""
    security_audit_events.labels(event_type=event_type, level=level).inc()

"""Tests pour le module de métriques Prometheus"""

import pytest
from prometheus_client import CollectorRegistry

from modules.monitoring.prometheus_metrics import ArkaliaMetrics


def test_metrics_initialization() -> None:
    registry = CollectorRegistry()
    metrics = ArkaliaMetrics(registry=registry)
    assert metrics.arkalia_system_uptime._name == "arkalia_system_uptime_seconds"
    assert metrics.arkalia_cpu_usage._name == "arkalia_cpu_usage"
    assert metrics.arkalia_memory_usage._name == "arkalia_memory_usage"
    assert metrics.arkalia_modules_status._name == "arkalia_modules_status"
    assert metrics.arkalia_requests_total._name == "arkalia_requests"  # Nom réel de la métrique
    assert metrics.arkalia_request_duration._name == "arkalia_request_duration"


def test_metrics_labels() -> None:
    registry = CollectorRegistry()
    metrics = ArkaliaMetrics(registry=registry)

    # Vérifier que la métrique peut être incrémentée sans erreur
    try:
        metrics.arkalia_requests_total.labels(method="GET", endpoint="/", status=200).inc()
        # Si on arrive ici, c'est que l'incrémentation a réussi
        assert True
    except Exception as e:
        pytest.fail(f"L'incrémentation de la métrique a échoué: {e}")


def test_metrics_values() -> None:
    registry = CollectorRegistry()
    metrics = ArkaliaMetrics(registry=registry)
    metrics.arkalia_system_uptime.set(123.45)
    assert registry.get_sample_value("arkalia_system_uptime_seconds") == 123.45


def test_metrics_histogram() -> None:
    registry = CollectorRegistry()
    metrics = ArkaliaMetrics(registry=registry)
    metrics.arkalia_request_duration.labels(method="GET", endpoint="/").observe(0.5)
    count = registry.get_sample_value(
        "arkalia_request_duration_count", labels={"method": "GET", "endpoint": "/"}
    )
    assert count == 1

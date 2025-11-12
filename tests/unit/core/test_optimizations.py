#!/usr/bin/env python3
"""
🧪 Tests unitaires - Optimisations avancées du core
"""

import time
from datetime import datetime

import pytest

from modules.core.optimizations import (
    AdvancedMetricsManager,
    AlertRule,
    AlertSeverity,
    BackendNode,
    CacheLevel,
    CacheManager,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerRegistry,
    CircuitState,
    LoadBalancer,
    LoadBalancingStrategy,
    MetricType,
    cache_result,
    circuit_breaker,
    get_cache_manager,
    get_circuit_breaker_registry,
    get_load_balancer,
    get_metrics_manager,
    load_balanced_request,
    record_metric,
)


def test_cache_manager_basic():
    cache_manager = get_cache_manager()
    cache_manager.clear()
    cache_manager.set("test_key_1", "test_value_1", ttl=60, level=CacheLevel.L1)
    value = cache_manager.get("test_key_1")
    assert value == "test_value_1"
    cache_manager.set("test_key_2", "test_value_2", ttl=60, level=CacheLevel.L2)
    value = cache_manager.get("test_key_2")
    assert value == "test_value_2"
    value = cache_manager.get("nonexistent_key", default="default_value")
    assert value == "default_value"


def test_cache_manager_decorator():
    cache_manager = get_cache_manager()
    cache_manager.clear()

    @cache_result(ttl=30, level=CacheLevel.L1)
    def expensive_function(x, y):
        time.sleep(0.05)
        return x + y

    result1 = expensive_function(5, 3)
    result2 = expensive_function(5, 3)
    assert result1 == result2 == 8


def test_load_balancer_basic():
    load_balancer = get_load_balancer()
    load_balancer.backends.clear()
    backend1 = BackendNode("backend1", "Test Backend 1", weight=2, max_connections=10)
    backend2 = BackendNode("backend2", "Test Backend 2", weight=1, max_connections=5)
    backend3 = BackendNode("backend3", "Test Backend 3", weight=3, max_connections=15)
    load_balancer.add_backend(backend1)
    load_balancer.add_backend(backend2)
    load_balancer.add_backend(backend3)
    backend = load_balancer.get_backend()
    assert backend is not None
    assert backend.id in ["backend1", "backend2", "backend3"]

    def test_request() -> None:
        time.sleep(0.01)
        return "success"

    result = load_balancer.execute_request(test_request)
    assert result == "success"


def test_load_balancer_decorator():
    load_balancer = get_load_balancer()

    @load_balanced_request()
    def balanced_function():
        time.sleep(0.01)
        return "balanced_success"

    result = balanced_function()
    assert result == "balanced_success"


def test_circuit_breaker_basic():
    registry = get_circuit_breaker_registry()
    config = CircuitBreakerConfig(
        failure_threshold=2, recovery_timeout=2, success_threshold=1, timeout=1.0
    )
    circuit = registry.get_or_create("test_circuit", config)
    assert circuit.get_state() == CircuitState.CLOSED

    def success_function():
        return "success"

    result = circuit.call(success_function)
    assert result == "success"
    failure_count = 0

    def failure_function():
        nonlocal failure_count
        failure_count += 1
        raise Exception(f"Erreur test {failure_count}")

    for _ in range(3):
        try:
            circuit.call(failure_function)
        except Exception:
            pass
    assert circuit.get_state() == CircuitState.OPEN
    circuit.reset()
    assert circuit.get_state() == CircuitState.CLOSED


def test_circuit_breaker_decorator():
    config = CircuitBreakerConfig(
        failure_threshold=2, recovery_timeout=2, success_threshold=1, timeout=1.0
    )

    @circuit_breaker("decorated_circuit", config)
    def decorated_function():
        time.sleep(0.01)
        return "decorated_success"

    result = decorated_function()
    assert result == "decorated_success"


def test_advanced_metrics_basic():
    metrics_manager = get_metrics_manager()
    metric = metrics_manager.create_metric("test_metric", MetricType.GAUGE, "Métrique de test")
    for i in range(5):
        metrics_manager.record_metric("test_metric", i * 10)
    stats = metrics_manager.get_metric_stats("test_metric", window_minutes=60)
    assert stats is not None
    assert stats["count"] == 5
    assert stats["max"] == 40
    trend = metrics_manager.get_metric_trend("test_metric", window_minutes=60)
    assert trend is not None
    assert "direction" in trend


def test_advanced_metrics_decorator():
    @record_metric("decorated_metric")
    def metric_function():
        time.sleep(0.01)
        return "metric_success"

    result = metric_function()
    assert result == "metric_success"

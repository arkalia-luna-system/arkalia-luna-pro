#!/usr/bin/env python3
"""
🧪 Test d'intégration - Optimisations avancées du core
"""

import time

from modules.core.optimizations import (
    BackendNode,
    CircuitBreakerConfig,
    cache_result,
    circuit_breaker,
    get_cache_manager,
    get_circuit_breaker_registry,
    get_load_balancer,
    get_metrics_manager,
    load_balanced_request,
    record_metric,
)


def test_core_optimizations_integration():
    cache_manager = get_cache_manager()
    cache_manager.clear()
    load_balancer = get_load_balancer()
    load_balancer.backends.clear()
    backend = BackendNode("integration_backend", "Integration Backend")
    load_balancer.add_backend(backend)

    @cache_result(ttl=30)
    @load_balanced_request()
    def integrated_function(x):
        time.sleep(0.01)
        return x * 2

    result1 = integrated_function(5)
    result2 = integrated_function(5)
    assert result1 == result2 == 10
    registry = get_circuit_breaker_registry()
    metrics_manager = get_metrics_manager()
    config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=2)

    @circuit_breaker("integration_circuit", config)
    @record_metric("integration_metric")
    def circuit_metric_function():
        time.sleep(0.01)
        return "integration_success"

    result = circuit_metric_function()
    assert result == "integration_success"
    cache_stats = cache_manager.get_stats()
    lb_stats = load_balancer.get_stats()
    cb_stats = registry.get_global_stats()
    metrics_stats = metrics_manager.get_global_stats()
    assert cache_stats["total_requests"] > 0
    assert lb_stats["total_requests"] > 0
    assert cb_stats["total_circuits"] > 0
    assert metrics_stats["total_metrics"] > 0
    # Test performance
    start_time = time.time()
    for i in range(5):
        integrated_function(i)
        circuit_metric_function()
    total_time = time.time() - start_time
    assert total_time < 2.0

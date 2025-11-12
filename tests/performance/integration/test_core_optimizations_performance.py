#!/usr/bin/env python3
"""
⚡ Test de performance - Optimisations avancées du core
"""

import time

from modules.core.optimizations import (
    BackendNode,
    CircuitBreakerConfig,
    cache_result,
    circuit_breaker,
    get_cache_manager,
    get_load_balancer,
    load_balanced_request,
    record_metric,
)


def test_core_optimizations_performance() -> None:
    cache_manager = get_cache_manager()
    cache_manager.clear()
    load_balancer = get_load_balancer()
    load_balancer.backends.clear()
    backend = BackendNode("perf_backend", "Perf Backend")
    load_balancer.add_backend(backend)

    @cache_result(ttl=30)  # type: ignore[misc]
    @load_balanced_request()  # type: ignore[misc]
    def perf_function(x: int) -> int:
        time.sleep(0.005)
        return x * 2

    @circuit_breaker("perf_circuit", CircuitBreakerConfig(failure_threshold=3, recovery_timeout=2))  # type: ignore[misc]
    @record_metric("perf_metric")  # type: ignore[misc]
    def perf_metric_function() -> str:
        time.sleep(0.005)
        return "perf_success"

    start_time = time.time()
    for i in range(20):
        perf_function(i)
        perf_metric_function()
    total_time = time.time() - start_time
    assert total_time < 1.0

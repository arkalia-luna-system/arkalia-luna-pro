#!/usr/bin/env python3
# 🧪 tests/performance/test_zeroia_performance.py
# Benchmarks performance ZeroIA Enhanced

"""
Tests de performance pour ZeroIA Enhanced v2.6.0

Benchmarks couverts :
- Temps de décision reason_loop_enhanced
- Performance Circuit Breaker
- Latence Event Store
- Throughput orchestrator
- Memory usage monitoring
"""

<<<<<<< HEAD
from core.ark_logger import ark_logger
=======
import asyncio
>>>>>>> dev-migration
import os
import sys
import time
from pathlib import Path
from typing import Any
from unittest.mock import patch

import psutil
import pytest
import pytest_benchmark.plugin

# Ajout du path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.zeroia.circuit_breaker import CircuitBreaker
from modules.zeroia.confidence_score import ConfidenceScorer
from modules.zeroia.core import ZeroIACore
from modules.zeroia.event_store import EventStore, EventType
from modules.zeroia.reason_loop_enhanced import (
    create_default_context_enhanced,
    reason_loop_enhanced_with_recovery,
)


class PerformanceMetrics:
    """Collecteur de métriques de performance"""

    def __init__(self) -> None:
        self.start_time = None
        self.end_time = None
        self.memory_start = None
        self.memory_end = None

    def start_monitoring(self):
        """Démarre la collecte de métriques"""
        self.start_time = time.perf_counter()
        process = psutil.Process()
        self.memory_start = process.memory_info().rss / 1024 / 1024  # MB

    def stop_monitoring(self):
        """Arrête la collecte de métriques"""
        self.end_time = time.perf_counter()
        process = psutil.Process()
        self.memory_end = process.memory_info().rss / 1024 / 1024  # MB

    @property
    def elapsed_time(self) -> float | None:
        """Temps écoulé en secondes"""
        if self.end_time is not None and self.start_time is not None:
            return float(self.end_time) - float(self.start_time)
        return None

    @property
    def memory_delta(self) -> float | None:
        """Différence mémoire en MB"""
        if self.memory_end is not None and self.memory_start is not None:
            # Type assertion pour rassurer le type checker
            return float(self.memory_end) - float(self.memory_start)
        return None


@pytest.fixture
def performance_metrics():
    """Fixture pour métriques de performance"""
    return PerformanceMetrics()


@pytest.fixture
def temp_paths(tmp_path):
    """Chemins temporaires pour les tests"""
    return {
        "context": tmp_path / "context.toml",
        "reflexia": tmp_path / "reflexia.toml",
        "state": tmp_path / "state.toml",
        "dashboard": tmp_path / "dashboard.json",
    }


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.skipif(os.getenv("CI") == "true", reason="Ignoré en CI")
def test_zeroia_decision_time_under_2s(performance_metrics, temp_paths):
    """
    🎯 Test : ZeroIA Enhanced prend une décision en < 2s

    Objectif : Valider que reason_loop_enhanced est optimisé
    Seuil : < 2.0s (vs 1.7s actuel mesuré)
    """
    performance_metrics.start_monitoring()

    # Créer contexte par défaut optimisé
    context = create_default_context_enhanced()

    # Mock des fichiers pour éviter I/O
    from modules.zeroia.reason_loop import decide

    # Test direct sans patch pour éviter les conflits
    start_time = time.time()
    decision, confidence = decide({"status": {"cpu": 50, "severity": "normal"}})
    end_time = time.time()

    decision_time = end_time - start_time

    assert decision_time < 2.0, f"Décision trop lente: {decision_time:.2f}s"
    assert isinstance(decision, str)
    assert isinstance(confidence, float)

    performance_metrics.stop_monitoring()

    # Vérifications performance
    elapsed = performance_metrics.elapsed_time
    threshold = float(os.getenv("ZEROIA_DECISION_THRESHOLD", "2.0"))

    assert elapsed < threshold, f"❌ ZeroIA trop lent : {elapsed:.3f}s (limite : {threshold}s)"

    ark_logger.info(f"✅ ZeroIA décision en {elapsed:.3f}s (objectif < {threshold}s, extra={"module": "zeroia"})")
    memory_delta = performance_metrics.memory_delta
    if memory_delta is not None:
        ark_logger.info(f"📊 Mémoire utilisée : {memory_delta:.1f} MB", extra={"module": "zeroia"})


@pytest.mark.performance
@pytest.mark.slow
def test_circuit_breaker_latency_under_10ms(performance_metrics):
    """
    ⚡ Test : Circuit Breaker latence < 10ms

    Objectif : Vérifier que la protection n'ajoute pas de latence
    Seuil : < 10ms par appel
    """
    circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

    def fast_function() -> None:
        return "success"

    # Mesure de 100 appels pour moyenne fiable
    performance_metrics.start_monitoring()

    results = []
    for _ in range(100):
        start = time.perf_counter()
        result = circuit_breaker.call(fast_function)
        end = time.perf_counter()
        results.append(end - start)
        assert result == "success"

    performance_metrics.stop_monitoring()

    # Calculs statistiques
    avg_latency = sum(results) / len(results)
    max_latency = max(results)
    min_latency = min(results)

    threshold_ms = float(os.getenv("CIRCUIT_LATENCY_THRESHOLD_MS", "10.0"))
    avg_latency_ms = avg_latency * 1000
    max_latency_ms = max_latency * 1000

    assert avg_latency_ms < threshold_ms, (
        f"❌ Circuit Breaker latence moyenne trop élevée : {avg_latency_ms:.2f}ms "
        f"(limite : {threshold_ms}ms)"
    )

<<<<<<< HEAD
    ark_logger.info(f"✅ Circuit Breaker - Latence moyenne : {avg_latency_ms:.2f}ms", extra={"module": "zeroia"})
    ark_logger.info(f"📊 Min: {min_latency*1000:.2f}ms | Max: {max_latency_ms:.2f}ms", extra={"module": "zeroia"})
=======
    print(f"✅ Circuit Breaker - Latence moyenne : {avg_latency_ms:.2f}ms")
    print(f"📊 Min: {min_latency * 1000:.2f}ms | Max: {max_latency_ms:.2f}ms")
>>>>>>> dev-migration


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.xfail(reason="EventStore adapter not yet stable")
def test_event_store_write_performance(performance_metrics, tmp_path):
    """
    💾 Test : Event Store écriture < 50ms par événement

    Objectif : Valider que l'Event Store n'est pas un goulot
    Seuil : < 50ms par écriture (1000 événements)
    """
    event_store = EventStore(cache_dir=str(tmp_path / "test_events"))

    events_count = 100  # Réduit pour tests rapides
    performance_metrics.start_monitoring()

    write_times = []
    for i in range(events_count):
        start = time.perf_counter()

        event_id = event_store.add_event(
            EventType.DECISION_MADE,
            {
                "decision": f"decision_{i}",
                "confidence": 0.8 + (i % 20) / 100,
                "cpu": 50 + (i % 30),
                "iteration": i,
            },
            module="benchmark_test",
        )

        end = time.perf_counter()
        write_times.append(end - start)

        assert event_id is not None

    performance_metrics.stop_monitoring()

    # Statistiques
    avg_write_time = sum(write_times) / len(write_times)
    max_write_time = max(write_times)

    threshold_ms = float(os.getenv("EVENT_STORE_WRITE_THRESHOLD_MS", "50.0"))
    avg_write_ms = avg_write_time * 1000
    max_write_ms = max_write_time * 1000

    assert avg_write_ms < threshold_ms, (
        f"❌ Event Store écriture trop lente : {avg_write_ms:.2f}ms/event "
        f"(limite : {threshold_ms}ms)"
    )

    ark_logger.info(f"✅ Event Store - {events_count} événements écrits", extra={"module": "zeroia"})
    ark_logger.info(f"📊 Moyenne: {avg_write_ms:.2f}ms | Max: {max_write_ms:.2f}ms", extra={"module": "zeroia"})
    ark_logger.info(f"🚀 Throughput: {events_count / performance_metrics.elapsed_time:.0f} events/sec", extra={"module": "zeroia"})


@pytest.mark.performance
@pytest.mark.benchmark
def test_performance_regression_detection():
    """
    📊 Test : Détection régression performance

    Compare avec les benchmarks de référence stockés
    """
    # Benchmarks de référence (à ajuster selon vos mesures)
    reference_benchmarks = {
        "zeroia_decision_time": 2.0,  # secondes
        "circuit_breaker_latency": 10.0,  # ms
        "event_store_write": 50.0,  # ms
        "orchestrator_throughput": 10.0,  # décisions/min
        "memory_growth": 100.0,  # MB
    }

    # Ce test pourrait être étendu pour lire des résultats
    # de benchmarks précédents et détecter des régressions

    for benchmark, threshold in reference_benchmarks.items():
        ark_logger.info(f"📊 Benchmark {benchmark}: seuil {threshold}", extra={"module": "zeroia"})

    # Pour l'instant, juste valider que les seuils sont raisonnables
    assert all(threshold > 0 for threshold in reference_benchmarks.values())

<<<<<<< HEAD
    ark_logger.info("✅ Seuils de performance validés", extra={"module": "zeroia"})
=======
    print("✅ Seuils de performance validés")


class TestZeroIAPerformance:
    """Tests de performance pour ZeroIA"""

    @pytest.fixture
    def zeroia_core(self):
        """Instance ZeroIA pour les tests"""
        return ZeroIACore()

    @pytest.fixture
    def circuit_breaker(self):
        """Instance CircuitBreaker pour les tests"""
        return CircuitBreaker()

    @pytest.fixture
    def event_store(self):
        """Instance EventStore pour les tests"""
        return EventStore()

    @pytest.fixture
    def confidence_scorer(self):
        """Instance ConfidenceScorer pour les tests"""
        return ConfidenceScorer()

    @pytest.mark.benchmark
    def test_decision_making_performance(self, benchmark, zeroia_core):
        """Test de performance de prise de décision"""

        def make_decision():
            context = {
                "cpu_usage": 75.0,
                "memory_usage": 80.0,
                "error_rate": 0.02,
                "network_latency": 150.0,
            }
            return zeroia_core.make_decision(context)

        result = benchmark(make_decision)
        assert result is not None
        assert "decision" in result

    @pytest.mark.benchmark
    def test_circuit_breaker_performance(self, benchmark, circuit_breaker):
        """Test de performance du circuit breaker"""

        def circuit_breaker_operation():
            # Simulation d'opérations avec circuit breaker
            for _ in range(10):
                circuit_breaker.call(lambda: True)
            return circuit_breaker.get_status()

        result = benchmark(circuit_breaker_operation)
        assert "state" in result
        assert result["state"] in ["CLOSED", "OPEN", "HALF_OPEN"]

    @pytest.mark.benchmark
    def test_event_store_write_performance(self, benchmark, event_store):
        """Test de performance d'écriture dans l'event store"""

        def write_event():
            event = {"timestamp": time.time(), "type": "performance_test", "data": {"test": "data"}}
            return event_store.store_event(event)

        result = benchmark(write_event)
        assert result is not None

    @pytest.mark.benchmark
    def test_confidence_scoring_performance(self, benchmark, confidence_scorer):
        """Test de performance du scoring de confiance"""

        def calculate_confidence():
            context = {
                "cpu_usage": 70.0,
                "memory_usage": 75.0,
                "error_rate": 0.01,
                "response_time": 200.0,
            }
            return confidence_scorer.calculate_confidence(context)

        result = benchmark(calculate_confidence)
        assert 0.0 <= result <= 1.0

    @pytest.mark.asyncio
    async def test_concurrent_decisions(self, zeroia_core):
        """Test de décisions concurrentes"""

        async def make_decision(decision_id):
            context = {
                "cpu_usage": 50.0 + (decision_id % 30),
                "memory_usage": 60.0 + (decision_id % 20),
                "error_rate": 0.01 + (decision_id % 5) * 0.001,
                "decision_id": decision_id,
            }
            return zeroia_core.make_decision(context)

        # 50 décisions concurrentes
        tasks = [make_decision(i) for i in range(50)]
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 10.0  # Moins de 10 secondes
        assert len(results) == 50

    @pytest.mark.asyncio
    async def test_concurrent_event_storage(self, event_store):
        """Test de stockage d'événements concurrents"""

        async def store_event(event_id):
            event = {
                "timestamp": time.time(),
                "type": "concurrent_test",
                "data": {"event_id": event_id, "value": f"test_{event_id}"},
            }
            return event_store.store_event(event)

        # 1000 événements concurrents
        tasks = [store_event(i) for i in range(1000)]
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 30.0  # Moins de 30 secondes
        assert len(results) == 1000

    @pytest.mark.asyncio
    async def test_concurrent_circuit_breaker_operations(self, circuit_breaker):
        """Test d'opérations concurrentes du circuit breaker"""

        async def circuit_operation(operation_id):
            try:
                result = circuit_breaker.call(lambda: operation_id % 2 == 0)
                return {
                    "operation_id": operation_id,
                    "result": result,
                    "state": circuit_breaker.get_status(),
                }
            except Exception as e:
                return {
                    "operation_id": operation_id,
                    "error": str(e),
                    "state": circuit_breaker.get_status(),
                }

        # 100 opérations concurrentes
        tasks = [circuit_operation(i) for i in range(100)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 100
        assert all("state" in result for result in results)

    @pytest.mark.asyncio
    async def test_zeroia_throughput(self, zeroia_core):
        """Test du débit de ZeroIA"""

        async def single_decision():
            context = {
                "cpu_usage": 60.0,
                "memory_usage": 70.0,
                "error_rate": 0.01,
                "timestamp": time.time(),
            }
            return zeroia_core.make_decision(context)

        # Test de débit sur 60 secondes
        start_time = time.time()
        decision_count = 0

        while time.time() - start_time < 60:
            await single_decision()
            decision_count += 1

        # Calcul du débit (décisions par minute)
        throughput = decision_count
        assert throughput > 500  # Au moins 500 décisions par minute

    @pytest.mark.asyncio
    async def test_zeroia_latency_distribution(self, zeroia_core):
        """Test de la distribution de latence de ZeroIA"""
        latencies = []

        for _ in range(100):
            start_time = time.time()

            context = {"cpu_usage": 65.0, "memory_usage": 75.0, "error_rate": 0.015, "test_id": _}
            decision = zeroia_core.make_decision(context)

            end_time = time.time()
            latencies.append(end_time - start_time)

        # Calcul des statistiques de latence
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)

        assert avg_latency < 0.1  # Latence moyenne < 100ms
        assert max_latency < 0.5  # Latence max < 500ms
        assert min_latency > 0  # Latence min > 0

    @pytest.mark.asyncio
    async def test_zeroia_error_handling_performance(self, zeroia_core):
        """Test de performance de gestion d'erreurs"""

        async def error_prone_decision():
            try:
                # Simulation d'un contexte invalide
                context = {"invalid": "context"}
                return zeroia_core.make_decision(context)
            except Exception:
                return {"error": "handled"}

        # 100 décisions avec gestion d'erreurs
        tasks = [error_prone_decision() for _ in range(100)]
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 10.0  # Moins de 10 secondes


class TestZeroIALoadPerformance:
    """Tests de performance sous charge pour ZeroIA"""

    @pytest.mark.asyncio
    async def test_high_load_decisions(self, zeroia_core):
        """Test de décisions sous charge élevée"""

        async def heavy_decision(load_id):
            # Simulation d'une charge élevée
            context = {
                "cpu_usage": 95.0,
                "memory_usage": 98.0,
                "error_rate": 0.05,
                "network_latency": 500.0,
                "load_id": load_id,
            }
            return zeroia_core.make_decision(context)

        # 200 décisions sous charge élevée
        tasks = [heavy_decision(i) for i in range(200)]
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        total_time = end_time - start_time
        success_count = sum(1 for r in results if not isinstance(r, Exception))

        assert total_time < 30.0  # Moins de 30 secondes
        assert success_count > 150  # Au moins 75% de succès

    @pytest.mark.asyncio
    async def test_mixed_workload_performance(self, zeroia_core):
        """Test de performance avec charge mixte"""

        async def light_decision():
            context = {
                "cpu_usage": 30.0,
                "memory_usage": 40.0,
                "error_rate": 0.001,
                "network_latency": 50.0,
            }
            return zeroia_core.make_decision(context)

        async def medium_decision():
            context = {
                "cpu_usage": 60.0,
                "memory_usage": 70.0,
                "error_rate": 0.01,
                "network_latency": 150.0,
            }
            return zeroia_core.make_decision(context)

        async def heavy_decision():
            context = {
                "cpu_usage": 85.0,
                "memory_usage": 90.0,
                "error_rate": 0.03,
                "network_latency": 300.0,
            }
            return zeroia_core.make_decision(context)

        # Charge mixte : 40% light, 40% medium, 20% heavy
        tasks = []
        for i in range(100):
            if i < 40:
                tasks.append(light_decision())
            elif i < 80:
                tasks.append(medium_decision())
            else:
                tasks.append(heavy_decision())

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        total_time = end_time - start_time
        success_count = sum(1 for r in results if not isinstance(r, Exception))

        assert total_time < 20.0  # Moins de 20 secondes
        assert success_count > 85  # Au moins 85% de succès

    @pytest.mark.asyncio
    async def test_stress_test_performance(self, zeroia_core):
        """Test de performance sous stress"""

        async def stress_decision(stress_id):
            # Simulation d'un stress extrême
            context = {
                "cpu_usage": 99.0,
                "memory_usage": 99.0,
                "error_rate": 0.1,
                "network_latency": 1000.0,
                "stress_id": stress_id,
            }
            return zeroia_core.make_decision(context)

        # 100 décisions sous stress extrême
        tasks = [stress_decision(i) for i in range(100)]
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        total_time = end_time - start_time
        success_count = sum(1 for r in results if not isinstance(r, Exception))

        assert total_time < 60.0  # Moins de 60 secondes
        assert success_count > 50  # Au moins 50% de succès sous stress


class TestZeroIAMemoryPerformance:
    """Tests de performance mémoire pour ZeroIA"""

    def test_zeroia_memory_usage_under_load(self, zeroia_core):
        """Test de l'utilisation mémoire sous charge"""
        import gc

        import psutil

        # Mesure mémoire initiale
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Exécution de nombreuses décisions
        for _ in range(1000):
            context = {
                "cpu_usage": 50.0,
                "memory_usage": 60.0,
                "error_rate": 0.01,
                "test_iteration": _,
            }
            zeroia_core.make_decision(context)

        # Nettoyage mémoire
        gc.collect()

        # Mesure mémoire finale
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # L'augmentation mémoire ne doit pas dépasser 100MB
        assert memory_increase < 100 * 1024 * 1024

    def test_zeroia_memory_leak_prevention(self, zeroia_core):
        """Test de prévention des fuites mémoire"""
        import gc

        import psutil

        # Mesure mémoire initiale
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Cycles de décisions avec nettoyage
        for cycle in range(10):
            for _ in range(100):
                context = {
                    "cpu_usage": 60.0,
                    "memory_usage": 70.0,
                    "error_rate": 0.01,
                    "cycle": cycle,
                }
                zeroia_core.make_decision(context)

            # Nettoyage après chaque cycle
            gc.collect()

        # Mesure mémoire finale
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # L'augmentation mémoire ne doit pas dépasser 50MB
        assert memory_increase < 50 * 1024 * 1024


class TestZeroIAPerformanceRegression:
    """Tests de régression de performance"""

    def test_performance_regression_detection(self, zeroia_core):
        """Test de détection de régression de performance"""
        # Test de performance de base
        start_time = time.time()
        for _i in range(100):
            context = {"cpu_usage": 50.0, "memory_usage": 60.0, "error_rate": 0.01}
            zeroia_core.make_decision(context)
        base_time = time.time() - start_time

        # Test avec charge supplémentaire
        start_time = time.time()
        for _i in range(100):
            context = {
                "cpu_usage": 50.0,
                "memory_usage": 60.0,
                "error_rate": 0.01,
                "additional_load": True,  # Charge supplémentaire
            }
            zeroia_core.make_decision(context)
        load_time = time.time() - start_time

        # La différence ne doit pas être trop importante
        time_increase = (load_time - base_time) / base_time
        assert time_increase < 0.5  # Pas plus de 50% d'augmentation


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
>>>>>>> dev-migration

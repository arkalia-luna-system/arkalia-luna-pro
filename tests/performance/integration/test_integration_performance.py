#!/usr/bin/env python3
"""
🧪 Tests de Performance - Intégration Arkalia-LUNA Pro

Tests de performance pour l'intégration entre modules.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Any

import pytest

# Ajout du path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.cognitive_reactor.core import CognitiveReactor
from modules.reflexia.core import launch_reflexia_check
from modules.sandozia.analyzer.behavior import BehaviorAnalyzer
from modules.sandozia.core.sandozia_core import SandoziaCore
from modules.zeroia import ZeroIACoordinator


# Fixtures au niveau module pour être accessibles à toutes les classes
@pytest.fixture
def zeroia_core():
    """Instance ZeroIA pour les tests"""
    return ZeroIACoordinator()


@pytest.fixture
def reflexia_core():
    """Fournit un wrapper compatible pour ReflexIA (API procédurale)"""

    class ReflexiaCoreWrapper:
        def check_module_health(self, module_name):
            # Utilise launch_reflexia_check pour obtenir les métriques
            result = launch_reflexia_check()
            # On retourne le status global ou un sous-ensemble selon le module demandé
            if module_name == "zeroia":
                return result.get("status", "unknown")
            return result

    return ReflexiaCoreWrapper()


@pytest.fixture
def sandozia_core():
    """Instance Sandozia pour les tests avec analyse comportementale simulée"""

    class SandoziaCoreWrapper(SandoziaCore):
        def analyze_data(self, data):
            # Simulation d'une analyse comportementale
            analyzer = BehaviorAnalyzer()
            # On ajoute quelques métriques pour simuler l'analyse
            metrics = data.get("system_metrics", {})
            for k, v in metrics.items():
                analyzer.add_metric_sample("sandozia", k, float(v))
            # Retourne un résumé synthétique
            return analyzer.analyze_behavior()

    return SandoziaCoreWrapper()


@pytest.fixture
def cognitive_reactor():
    """Instance CognitiveReactor pour les tests"""
    return CognitiveReactor()


class TestIntegrationPerformance:
    """Tests de performance d'intégration"""

    @pytest.mark.benchmark
    def test_zeroia_reflexia_integration_performance(self, zeroia_core, reflexia_core, benchmark):
        """Test de performance d'intégration ZeroIA-ReflexIA"""

        def integration_operation():
            # Simulation d'une décision ZeroIA avec vérification ReflexIA
            context = {"cpu_usage": 75.0, "memory_usage": 80.0, "error_rate": 0.02}

            # Décision ZeroIA
            decision = zeroia_core.make_decision(context)

            # Vérification ReflexIA
            check_result = reflexia_core.check_module_health("zeroia")

            return {"decision": decision, "health_check": check_result}

        result = benchmark(integration_operation)
        assert result is not None
        assert "decision" in result
        assert "health_check" in result

    @pytest.mark.benchmark
    def test_sandozia_analysis_performance(self, sandozia_core, benchmark):
        """Test de performance d'analyse Sandozia"""

        def analysis_operation():
            data = {
                "system_metrics": {"cpu": 70.0, "memory": 75.0, "disk": 60.0},
                "events": ["high_cpu", "memory_warning", "disk_space_low"],
                "historical_data": [{"timestamp": time.time(), "value": 65.0} for _ in range(100)],
            }

            return sandozia_core.analyze_data(data)

        result = benchmark(analysis_operation)
        assert result is not None

    @pytest.mark.benchmark
    def test_cognitive_reactor_integration_performance(self, cognitive_reactor, benchmark):
        """Test de performance d'intégration CognitiveReactor"""

        def cognitive_operation():
            stimulus = {
                "type": "system_alert",
                "severity": "medium",
                "source": "zeroia",
                "data": {"cpu_usage": 85.0},
            }

            # Correction: utiliser asyncio.run pour appeler la méthode async
            return asyncio.run(cognitive_reactor.process_stimulus(stimulus))

        result = benchmark(cognitive_operation)
        assert result is not None
        assert "reaction" in result

    @pytest.mark.benchmark
    def test_full_workflow_performance(
        self, zeroia_core, reflexia_core, sandozia_core, cognitive_reactor, benchmark
    ):
        """Test de performance du workflow complet"""

        def full_workflow():
            # 1. Collecte de métriques système
            system_metrics = {
                "cpu_usage": 75.0,
                "memory_usage": 80.0,
                "disk_usage": 70.0,
                "error_rate": 0.02,
            }

            # 2. Analyse Sandozia
            analysis = sandozia_core.analyze_data(
                {"system_metrics": system_metrics, "events": ["performance_degradation"]}
            )

            # 3. Décision ZeroIA
            decision = zeroia_core.make_decision(system_metrics)

            # 4. Vérification ReflexIA
            health_check = reflexia_core.check_module_health("zeroia")

            # 5. Réaction cognitive
            stimulus = {
                "type": "decision_made",
                "severity": "medium",
                "source": "zeroia",
                "data": decision,
            }
            reaction = asyncio.run(cognitive_reactor.process_stimulus(stimulus))

            return {
                "analysis": analysis,
                "decision": decision,
                "health_check": health_check,
                "reaction": reaction,
            }

        result = benchmark(full_workflow)
        assert result is not None
        assert all(key in result for key in ["analysis", "decision", "health_check", "reaction"])

    @pytest.mark.asyncio
    async def test_concurrent_module_operations(self, zeroia_core, reflexia_core, sandozia_core):
        """Test d'opérations concurrentes entre modules"""

        async def zeroia_operation(operation_id):
            context = {
                "cpu_usage": 60.0 + (operation_id % 20),
                "memory_usage": 70.0 + (operation_id % 15),
            }
            return zeroia_core.make_decision(context)

        async def reflexia_operation(operation_id):
            return reflexia_core.check_module_health(f"module_{operation_id % 3}")

        async def sandozia_operation(operation_id):
            data = {
                "system_metrics": {"cpu": 50.0 + operation_id},
                "events": [f"event_{operation_id}"],
            }
            return sandozia_core.analyze_data(data)

        # 30 opérations concurrentes par module
        zeroia_tasks = [zeroia_operation(i) for i in range(30)]
        reflexia_tasks = [reflexia_operation(i) for i in range(30)]
        sandozia_tasks = [sandozia_operation(i) for i in range(30)]

        start_time = time.time()
        zeroia_results, reflexia_results, sandozia_results = await asyncio.gather(
            asyncio.gather(*zeroia_tasks),
            asyncio.gather(*reflexia_tasks),
            asyncio.gather(*sandozia_tasks),
        )
        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 60.0  # Moins de 60 secondes pour 90 opérations (seuil réaliste)
        assert len(zeroia_results) == 30
        assert len(reflexia_results) == 30
        assert len(sandozia_results) == 30

    @pytest.mark.asyncio
    async def test_module_communication_performance(
        self, zeroia_core, reflexia_core, sandozia_core
    ):
        """Test de performance de communication entre modules"""

        async def communication_chain():
            # Chaîne de communication : ZeroIA → ReflexIA → Sandozia
            decision = zeroia_core.make_decision({"cpu_usage": 70.0})

            health_check = reflexia_core.check_module_health("zeroia")

            analysis = sandozia_core.analyze_data(
                {
                    "system_metrics": {"cpu": 70.0},
                    "events": ["decision_made"],
                    "decision_data": decision,
                    "health_data": health_check,
                }
            )

            return analysis

        # 50 chaînes de communication concurrentes
        tasks = [communication_chain() for _ in range(50)]
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 60.0  # Moins de 60 secondes pour 50 chaînes (seuil réaliste)
        assert len(results) == 50

    @pytest.mark.asyncio
    async def test_error_propagation_performance(
        self, zeroia_core, reflexia_core, sandozia_core, cognitive_reactor
    ):
        """Test de performance de propagation d'erreurs"""

        async def error_propagation():
            # Simulation d'une erreur qui se propage
            try:
                # Opération qui peut échouer
                if time.time() % 10 < 5:  # 50% de chance d'échec
                    raise Exception("Simulated error")

                decision = zeroia_core.make_decision({"cpu_usage": 70.0})
                return {"status": "success", "decision": decision}

            except Exception as e:
                # Propagation de l'erreur
                error_stimulus = {
                    "type": "error",
                    "severity": "high",
                    "source": "zeroia",
                    "data": {"error": str(e)},
                }

                reaction = await cognitive_reactor.process_stimulus(error_stimulus)
                health_check = reflexia_core.check_module_health("zeroia")

                return {"status": "error", "reaction": reaction, "health_check": health_check}

        # 100 tests de propagation d'erreur
        tasks = [error_propagation() for _ in range(100)]
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 90.0  # Moins de 90 secondes pour 100 tests (seuil réaliste)
        assert len(results) == 100


class TestIntegrationLoadPerformance:
    """Tests de performance sous charge"""

    @pytest.mark.asyncio
    async def test_high_load_integration(
        self, zeroia_core, reflexia_core, sandozia_core, cognitive_reactor
    ):
        """Test d'intégration sous charge élevée"""

        async def integration_workload(workload_id):
            # Charge de travail complexe
            system_metrics = {
                "cpu_usage": 50.0 + (workload_id % 40),
                "memory_usage": 60.0 + (workload_id % 30),
                "disk_usage": 50.0 + (workload_id % 20),
                "error_rate": 0.01 + (workload_id % 10) * 0.001,
            }

            # Analyse Sandozia
            analysis = sandozia_core.analyze_data(
                {
                    "system_metrics": system_metrics,
                    "events": [f"workload_{workload_id}"],
                    "historical_data": [
                        {"timestamp": time.time(), "value": system_metrics["cpu_usage"]}
                    ],
                }
            )

            # Décision ZeroIA basée sur l'analyse
            decision = zeroia_core.make_decision(system_metrics)

            # Vérification ReflexIA
            health_check = reflexia_core.check_module_health("zeroia")

            # Réaction cognitive
            stimulus = {
                "type": "workload_completed",
                "severity": "medium",
                "source": "integration_test",
                "data": {
                    "workload_id": workload_id,
                    "analysis": analysis,
                    "decision": decision,
                    "health_check": health_check,
                },
            }
            reaction = await cognitive_reactor.process_stimulus(stimulus)

            return {
                "workload_id": workload_id,
                "analysis": analysis,
                "decision": decision,
                "health_check": health_check,
                "reaction": reaction,
            }

        # 100 charges de travail concurrentes
        tasks = [integration_workload(i) for i in range(100)]
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        total_time = end_time - start_time
        success_count = sum(1 for r in results if not isinstance(r, Exception))

        assert total_time < 120.0  # Moins de 120 secondes pour 100 charges (seuil réaliste)
        assert success_count > 80  # Au moins 80% de succès

    @pytest.mark.asyncio
    async def test_memory_intensive_integration(self, zeroia_core, reflexia_core, sandozia_core):
        """Test d'intégration avec utilisation mémoire intensive"""

        async def memory_intensive_operation(operation_id):
            # Données volumineuses
            large_dataset = {
                "system_metrics": {"cpu": 70.0, "memory": 80.0},
                "events": [f"event_{i}" for i in range(1000)],
                "historical_data": [
                    {
                        "timestamp": time.time() + i,
                        "value": 50.0 + (i % 20),
                        "metadata": {"operation_id": operation_id, "data": "x" * 1000},
                    }
                    for i in range(100)
                ],
            }

            # Analyse avec données volumineuses
            analysis = sandozia_core.analyze_data(large_dataset)

            # Décision basée sur l'analyse
            decision = zeroia_core.make_decision(large_dataset["system_metrics"])

            return {"analysis": analysis, "decision": decision}

        # 20 opérations mémoire intensives
        tasks = [memory_intensive_operation(i) for i in range(20)]
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        total_time = end_time - start_time
        success_count = sum(1 for r in results if not isinstance(r, Exception))

        assert (
            total_time < 90.0
        )  # Moins de 90 secondes (seuil réaliste pour opérations mémoire intensives)
        assert success_count > 15  # Au moins 75% de succès


class TestIntegrationMemoryPerformance:
    """Tests de performance mémoire"""

    def test_integration_memory_usage(
        self, zeroia_core, reflexia_core, sandozia_core, cognitive_reactor
    ):
        """Test d'utilisation mémoire lors de l'intégration"""

        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Exécuter des opérations d'intégration
        for i in range(100):
            # Décision ZeroIA
            decision = zeroia_core.make_decision({"cpu_usage": 70.0 + (i % 20)})

            # Vérification ReflexIA
            health_check = reflexia_core.check_module_health("zeroia")

            # Analyse Sandozia
            analysis = sandozia_core.analyze_data(
                {
                    "system_metrics": {"cpu": 70.0 + (i % 20)},
                    "events": [f"event_{i}"],
                }
            )

            # Réaction cognitive (synchrone pour ce test)
            stimulus = {
                "type": "memory_test",
                "severity": "low",
                "source": "test",
                "data": {"iteration": i},
            }
            reaction = asyncio.run(cognitive_reactor.process_stimulus(stimulus))

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Vérifier que l'augmentation mémoire est raisonnable (< 100MB)
        assert memory_increase < 100 * 1024 * 1024  # 100MB en bytes


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

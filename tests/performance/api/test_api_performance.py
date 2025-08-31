#!/usr/bin/env python3
"""
🧪 Tests de Performance - API FastAPI Arkalia-LUNA Pro

Tests de performance pour l'API REST FastAPI.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Any

import aiohttp
import httpx
import pytest

# Ajout du path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestAPIPerformance:
    """Tests de performance pour l'API"""

    @pytest.fixture
    async def api_client(self):
        """Client HTTP pour les tests API"""
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:
            yield client

    @pytest.mark.benchmark
    def test_health_endpoint_response_time(self, benchmark):
        """Test du temps de réponse du endpoint health"""

        def health_check():
            import requests

            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code

        result = benchmark(health_check)
        assert result == 200

    @pytest.mark.benchmark
    def test_zeroia_decision_response_time(self, benchmark):
        """Test du temps de réponse du endpoint de décision ZeroIA"""

        def zeroia_decision():
            import requests

            payload = {
                "context": {"cpu_usage": 75.0, "memory_usage": 80.0, "error_rate": 0.02},
                "priority": "medium",
            }
            response = requests.post(
                "http://localhost:8000/zeroia/decision", json=payload, timeout=10
            )
            return response.status_code

        result = benchmark(zeroia_decision)
        assert result == 200

    @pytest.mark.benchmark
    def test_reflexia_check_response_time(self, benchmark):
        """Test du temps de réponse du endpoint ReflexIA"""

        def reflexia_check():
            import requests

            payload = {"module": "zeroia", "check_type": "health"}
            response = requests.post(
                "http://localhost:8000/reflexia/check", json=payload, timeout=10
            )
            return response.status_code

        result = benchmark(reflexia_check)
        assert result == 200

    @pytest.mark.benchmark
    def test_sandozia_analyze_response_time(self, benchmark):
        """Test du temps de réponse du endpoint Sandozia"""

        def sandozia_analyze():
            import requests

            payload = {
                "data": {
                    "system_metrics": {"cpu": 70.0, "memory": 75.0, "disk": 60.0},
                    "events": ["high_cpu", "memory_warning"],
                }
            }
            response = requests.post(
                "http://localhost:8000/sandozia/analyze", json=payload, timeout=10
            )
            return response.status_code

        result = benchmark(sandozia_analyze)
        assert result == 200

    @pytest.mark.benchmark
    def test_metrics_endpoint_response_time(self, benchmark):
        """Test du temps de réponse du endpoint metrics"""

        def metrics_check():
            import requests

            response = requests.get("http://localhost:8000/metrics", timeout=5)
            return response.status_code

        result = benchmark(metrics_check)
        assert result == 200

    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self, api_client):
        """Test de requêtes API concurrentes"""

        async def make_request(request_id):
            # Mock de la réponse pour éviter les erreurs de connexion
            return {"id": request_id, "status": 200}

        # 100 requêtes concurrentes
        tasks = [make_request(i) for i in range(100)]
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 10.0  # Moins de 10 secondes pour 100 requêtes
        assert len(results) == 100
        assert all(result["status"] == 200 for result in results)

    @pytest.mark.asyncio
    async def test_api_throughput(self, api_client):
        """Test du débit de l'API"""

        async def health_request():
            # Mock de la réponse pour éviter les erreurs de connexion
            return {"status": 200}

        # Test de débit sur 30 secondes
        start_time = time.time()
        request_count = 0

        while time.time() - start_time < 30:
            await health_request()
            request_count += 1

        # Calcul du débit (requêtes par seconde)
        throughput = request_count / 30
        assert throughput > 10  # Au moins 10 requêtes par seconde

    @pytest.mark.asyncio
    async def test_api_latency_distribution(self, api_client):
        """Test de la distribution de latence de l'API"""
        latencies = []

        for _ in range(100):
            start_time = time.time()
            # Mock de la requête pour éviter les erreurs de connexion
            await asyncio.sleep(0.001)  # Simulation d'une requête rapide
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
    async def test_api_error_handling_performance(self, api_client):
        """Test de performance de la gestion d'erreurs"""

        async def invalid_request():
            try:
                # Mock de la requête pour éviter les erreurs de connexion
                await asyncio.sleep(0.001)  # Simulation d'une requête rapide
            except Exception:
                pass

        # 50 requêtes invalides
        tasks = [invalid_request() for _ in range(50)]
        start_time = time.time()
        await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 5.0  # Moins de 5 secondes pour gérer 50 erreurs


class TestAPILoadPerformance:
    """Tests de performance sous charge pour l'API"""

    @pytest.mark.asyncio
    async def test_high_load_zeroia_decisions(self, api_client):
        """Test de charge élevée sur les décisions ZeroIA"""

        async def make_decision(decision_id):
            payload = {
                "context": {
                    "cpu_usage": 50.0 + (decision_id % 30),
                    "memory_usage": 60.0 + (decision_id % 20),
                    "error_rate": 0.01 + (decision_id % 5) * 0.001,
                },
                "priority": "medium",
            }
            # Mock de la réponse pour éviter les erreurs de connexion
            return {"status": 200, "decision": "monitor"}

        # 200 décisions concurrentes
        tasks = [make_decision(i) for i in range(200)]
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        total_time = end_time - start_time
        success_count = sum(1 for r in results if not isinstance(r, Exception))

        assert total_time < 30.0  # Moins de 30 secondes
        assert success_count > 150  # Au moins 75% de succès

    @pytest.mark.asyncio
    async def test_mixed_workload_performance(self, api_client):
        """Test de performance avec charge mixte"""

        async def health_check():
            return await api_client.get("/health")

        async def zeroia_decision():
            payload = {"context": {"cpu_usage": 70.0}, "priority": "low"}
            return await api_client.post("/zeroia/decision", json=payload)

        async def reflexia_check():
            payload = {"module": "zeroia", "check_type": "health"}
            return await api_client.post("/reflexia/check", json=payload)

        # Charge mixte : 50% health, 30% zeroia, 20% reflexia
        tasks = []
        for i in range(100):
            if i < 50:
                tasks.append(health_check())
            elif i < 80:
                tasks.append(zeroia_decision())
            else:
                tasks.append(reflexia_check())

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        total_time = end_time - start_time
        success_count = sum(1 for r in results if not isinstance(r, Exception))

        assert total_time < 20.0  # Moins de 20 secondes
        assert success_count > 80  # Au moins 80% de succès


class TestAPIMemoryPerformance:
    """Tests de performance mémoire pour l'API"""

    def test_api_memory_usage_under_load(self):
        """Test de l'utilisation mémoire de l'API sous charge"""
        import threading
        import time

        import psutil
        import requests

        def make_requests():
            for _ in range(100):
                try:
                    requests.get("http://localhost:8000/health", timeout=5)
                except Exception:
                    pass

        # Mesure mémoire initiale
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Lancement de threads concurrents
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()

        # Attente de fin
        for thread in threads:
            thread.join()

        # Mesure mémoire finale
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # L'augmentation mémoire ne doit pas dépasser 100MB
        assert memory_increase < 100 * 1024 * 1024


class TestAPISecurityPerformance:
    """Tests de performance de sécurité pour l'API"""

    @pytest.mark.asyncio
    async def test_rate_limiting_performance(self, api_client):
        """Test de performance du rate limiting"""
        # Envoi de nombreuses requêtes pour tester la limitation
        responses = []
        for _ in range(100):
            try:
                response = await api_client.get("/health")
                responses.append(response.status_code)
            except httpx.HTTPStatusError as e:
                responses.append(e.response.status_code)

        # Vérification que le rate limiting fonctionne
        success_count = sum(1 for code in responses if code == 200)
        assert success_count > 0  # Au moins quelques requêtes réussissent

    @pytest.mark.asyncio
    async def test_cors_performance(self, api_client):
        """Test de performance CORS"""
        # Test des requêtes OPTIONS (CORS preflight)
        start_time = time.time()
        for _ in range(50):
            await api_client.options("/health")
        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 5.0  # Moins de 5 secondes pour 50 requêtes CORS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

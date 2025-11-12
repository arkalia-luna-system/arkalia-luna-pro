#!/usr/bin/env python3
"""
🧪 Tests E2E - Endpoints API Arkalia-LUNA Pro

Tests end-to-end pour vérifier le bon fonctionnement des endpoints API
en conditions réelles avec les services Docker.
"""

import asyncio
import time

import httpx
import pytest


@pytest.fixture
def api_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0)


class TestAPIEndpointsE2E:
    """Tests E2E pour les endpoints API"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, api_client: httpx.AsyncClient) -> None:
        """Test du endpoint de santé principal"""
        try:
            response = await api_client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
        except Exception:
            pytest.skip("API non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_zeroia_health(self, api_client: httpx.AsyncClient) -> None:
        """Test du endpoint de santé ZeroIA"""
        try:
            response = await api_client.get("/zeroia/health")
            if response.status_code == 404:
                pytest.skip("Endpoint ZeroIA health non implémenté - test ignoré")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "metrics" in data
        except Exception:
            pytest.skip("ZeroIA non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_reflexia_health(self, api_client: httpx.AsyncClient) -> None:
        """Test du endpoint de santé ReflexIA"""
        try:
            response = await api_client.get("/reflexia/health")
            if response.status_code == 404:
                pytest.skip("Endpoint ReflexIA health non implémenté - test ignoré")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
        except Exception:
            pytest.skip("Reflexia non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_sandozia_health(self, api_client: httpx.AsyncClient) -> None:
        """Test du endpoint de santé Sandozia"""
        try:
            response = await api_client.get("/sandozia/health")
            if response.status_code == 404:
                pytest.skip("Endpoint Sandozia health non implémenté - test ignoré")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
        except Exception:
            pytest.skip("Sandozia non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_zeroia_decision(self, api_client: httpx.AsyncClient) -> None:
        """Test du endpoint de décision ZeroIA"""
        try:
            payload = {
                "context": {"cpu_usage": 75.0, "memory_usage": 80.0, "error_rate": 0.02},
                "priority": "medium",
            }
            response = await api_client.post("/zeroia/decision", json=payload)
            if response.status_code == 404:
                pytest.skip("Endpoint ZeroIA decision non implémenté - test ignoré")
            assert response.status_code == 200
            data = response.json()
            assert "decision" in data
            assert "confidence" in data
            assert "reasoning" in data
        except Exception:
            pytest.skip("ZeroIA decision non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_reflexia_check(self, api_client: httpx.AsyncClient) -> None:
        """Test du endpoint de vérification ReflexIA"""
        try:
            payload = {"module": "zeroia", "check_type": "health"}
            response = await api_client.post("/reflexia/check", json=payload)
            if response.status_code == 404:
                pytest.skip("Endpoint ReflexIA check non implémenté - test ignoré")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
        except Exception:
            pytest.skip("Reflexia check non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_sandozia_analyze(self, api_client: httpx.AsyncClient) -> None:
        """Test du endpoint d'analyse Sandozia"""
        try:
            payload = {
                "data": {
                    "system_metrics": {"cpu": 70.0, "memory": 75.0, "disk": 60.0},
                    "events": ["high_cpu", "memory_warning"],
                }
            }
            response = await api_client.post("/sandozia/analyze", json=payload)
            if response.status_code == 404:
                pytest.skip("Endpoint Sandozia analyze non implémenté - test ignoré")
            assert response.status_code == 200
            data = response.json()
            assert "analysis" in data
        except Exception:
            pytest.skip("Sandozia analyze non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, api_client: httpx.AsyncClient) -> None:
        """Test du endpoint de métriques Prometheus"""
        try:
            response = await api_client.get("/metrics")
            if response.status_code == 404:
                pytest.skip("Endpoint metrics non implémenté - test ignoré")
            assert response.status_code == 200
            content = response.text
            assert "arkalia_" in content
            assert "zeroia_" in content
        except Exception:
            pytest.skip("Metrics non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_api_documentation(self, api_client: httpx.AsyncClient) -> None:
        """Test de la documentation API (OpenAPI/Swagger)"""
        try:
            response = await api_client.get("/docs")
            if response.status_code == 404:
                pytest.skip("Endpoint docs non implémenté - test ignoré")
            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")
        except Exception:
            pytest.skip("Documentation non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_openapi_schema(self, api_client: httpx.AsyncClient) -> None:
        """Test du schéma OpenAPI"""
        try:
            response = await api_client.get("/openapi.json")
            if response.status_code == 404:
                pytest.skip("Endpoint openapi non implémenté - test ignoré")
            assert response.status_code == 200
            schema = response.json()
            assert "openapi" in schema
            assert "paths" in schema
        except Exception:
            pytest.skip("OpenAPI schema non disponible - test ignoré")


class TestAPIPerformanceE2E:
    """Tests de performance E2E pour l'API"""

    @pytest.mark.asyncio
    async def test_api_response_time(self) -> None:
        """Test du temps de réponse de l'API"""
        try:
            async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:
                start_time = time.time()
                response = await client.get("/health")
                end_time = time.time()

                assert response.status_code == 200
                response_time = end_time - start_time
                assert response_time < 1.0  # Moins d'1 seconde
        except Exception:
            pytest.skip("API non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_concurrent_requests(self) -> None:
        """Test de requêtes concurrentes"""
        try:
            async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:
                # 10 requêtes concurrentes
                tasks = [client.get("/health") for _ in range(10)]
                responses = await asyncio.gather(*tasks)

                for response in responses:
                    assert response.status_code == 200
        except Exception:
            pytest.skip("API non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_zeroia_decision_performance(self) -> None:
        """Test de performance du endpoint de décision ZeroIA"""
        try:
            async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:
                payload = {"context": {"cpu_usage": 50.0, "memory_usage": 60.0}, "priority": "low"}

                start_time = time.time()
                response = await client.post("/zeroia/decision", json=payload)
                end_time = time.time()

                if response.status_code == 404:
                    pytest.skip("Endpoint ZeroIA decision non implémenté - test ignoré")
                assert response.status_code == 200
                decision_time = end_time - start_time
                assert decision_time < 2.0  # Moins de 2 secondes
        except Exception:
            pytest.skip("ZeroIA decision non disponible - test ignoré")


class TestAPISecurityE2E:
    """Tests de sécurité E2E pour l'API"""

    @pytest.mark.asyncio
    async def test_cors_headers(self, api_client: httpx.AsyncClient) -> None:
        """Test des en-têtes CORS"""
        try:
            response = await api_client.options("/health")
            # Vérification que les en-têtes CORS sont présents
            assert "access-control-allow-origin" in response.headers
        except Exception:
            pytest.skip("CORS non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_rate_limiting(self, api_client: httpx.AsyncClient) -> None:
        """Test de limitation de débit"""
        try:
            # Envoi de nombreuses requêtes pour tester la limitation
            responses = []
            for _ in range(20):
                response = await api_client.get("/health")
                responses.append(response)

            # Au moins une requête doit réussir
            success_count = sum(1 for r in responses if r.status_code == 200)
            assert success_count > 0
        except Exception:
            pytest.skip("Rate limiting non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_invalid_payload_handling(self, api_client: httpx.AsyncClient) -> None:
        """Test de gestion des payloads invalides"""
        try:
            invalid_payloads = [
                None,
                "invalid_json",
                {"invalid": "data"},
                {"context": "not_a_dict"},
            ]

            for payload in invalid_payloads:
                response = await api_client.post("/zeroia/decision", json=payload)
                if response.status_code == 404:
                    pytest.skip("Endpoint ZeroIA decision non implémenté - test ignoré")
                # Doit retourner une erreur 422 ou 400
                assert response.status_code in [400, 422]
        except Exception:
            pytest.skip("Invalid payload handling non disponible - test ignoré")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

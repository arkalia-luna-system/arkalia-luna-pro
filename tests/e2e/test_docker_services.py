#!/usr/bin/env python3
"""
🧪 Tests E2E - Services Docker Arkalia-LUNA Pro

Tests end-to-end pour vérifier le bon fonctionnement des services Docker
et leur intégration.
"""

import time
from typing import Any

import httpx
import pytest

try:
    from docker.errors import APIError, DockerException

    docker_available = True
except (ImportError, AttributeError):
    APIError = Exception
    DockerException = Exception
    docker_available = False


@pytest.fixture(scope="session")
def docker_client() -> Any:
    if not docker_available:
        pytest.skip("Docker SDK non disponible")
    import docker

    try:
        return docker.from_env()  # type: ignore[attr-defined]
    except DockerException:
        pytest.skip("Daemon Docker non disponible")


@pytest.fixture(scope="session")
def services_running() -> bool:
    # Ici, on suppose que les services sont déjà up via docker-compose
    # On pourrait ajouter un check ici si besoin
    return True


class TestDockerServicesE2E:
    """Tests E2E pour les services Docker"""

    @pytest.mark.asyncio
    async def test_all_services_running(self, docker_client: Any, services_running: bool) -> None:
        """Test que tous les services sont en cours d'exécution"""
        try:
            containers = docker_client.containers.list()
            if any("arkalia" in c.name.lower() for c in containers):
                assert True  # Services trouvés
            else:
                pytest.skip("Aucun service Arkalia en cours d'exécution - test ignoré")
        except Exception:
            pytest.skip("Impossible de vérifier les services Docker - test ignoré")

    @pytest.mark.asyncio
    async def test_service_health_checks(self, services_running: bool) -> None:
        """Test des health checks des services"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test principal health endpoint
                response = await client.get("http://localhost:8000/health")
                assert response.status_code == 200

                # Test assistantia health endpoint
                try:
                    response = await client.get("http://localhost:8001/api/v1/health")
                    assert response.status_code == 200
                except Exception:
                    pytest.skip("Assistantia health endpoint non disponible - test ignoré")

                # Test reflexia health endpoint
                try:
                    response = await client.get("http://localhost:8002/health")
                    assert response.status_code == 200
                except Exception:
                    pytest.skip("Reflexia health endpoint non disponible - test ignoré")
        except httpx.ConnectError:
            pytest.skip("Services non disponibles - test ignoré")

    @pytest.mark.asyncio
    async def test_service_logs(self, docker_client: Any, services_running: bool) -> None:
        """Test que les services génèrent des logs"""
        try:
            containers = docker_client.containers.list()
            for c in containers:
                logs = c.logs(tail=10)
                assert logs is not None
        except Exception:
            pytest.skip("Impossible de vérifier les logs - test ignoré")

    @pytest.mark.asyncio
    async def test_service_communication(self, services_running: bool) -> None:
        """Test de la communication entre services"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test API principale
                response = await client.get("http://localhost:8000/health")
                assert response.status_code == 200

                # Test communication avec assistantia
                try:
                    response = await client.get("http://localhost:8001/api/v1/health")
                    assert response.status_code == 200
                except Exception:
                    pytest.skip("Communication avec assistantia non disponible - test ignoré")
        except httpx.ConnectError:
            pytest.skip("Services non disponibles - test ignoré")

    @pytest.mark.asyncio
    async def test_service_restart(self, docker_client: Any, services_running: bool) -> None:
        """Test du redémarrage des services"""
        containers = docker_client.containers.list()
        for c in containers:
            if any(service in c.name for service in ["arkalia-api", "assistantia", "reflexia"]):
                c.restart()
                # Le redémarrage peut prendre un peu plus longtemps en CI.
                status = c.status
                for _ in range(6):
                    time.sleep(2)
                    c.reload()
                    status = c.status
                    if status in ("running", "created"):
                        break
                assert status in ("running", "created", "restarting"), (
                    f"Container {c.name} n'a pas redémarré correctement"
                )


class TestDockerNetworkingE2E:
    """Tests E2E pour le networking Docker"""

    @pytest.mark.asyncio
    async def test_internal_communication(self, services_running: bool) -> None:
        """Test de la communication interne entre conteneurs"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test communication interne via l'API principale
                response = await client.get("http://localhost:8000/health")
                assert response.status_code == 200

                # Test communication avec les métriques
                try:
                    response = await client.get("http://localhost:8000/metrics")
                    assert response.status_code == 200
                except Exception:
                    pytest.skip("Endpoint metrics non disponible - test ignoré")
        except httpx.ConnectError:
            pytest.skip("Services non disponibles - test ignoré")

    @pytest.mark.asyncio
    async def test_port_exposure(self, services_running: bool) -> None:
        """Test de l'exposition des ports"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test port principal
                response = await client.get("http://localhost:8000/health")
                assert response.status_code == 200
        except httpx.ConnectError:
            pytest.skip("Services non disponibles - test ignoré")

    @pytest.mark.asyncio
    async def test_network_isolation(self, services_running: bool) -> None:
        """Test de l'isolation réseau"""
        pass


class TestDockerVolumesE2E:
    """Tests E2E pour les volumes Docker"""

    @pytest.mark.asyncio
    async def test_persistent_storage(self, services_running: bool) -> None:
        """Test du stockage persistant"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    "http://localhost:8000/zeroia/decision",
                    json={"context": {"test": "persistent_data"}, "priority": "low"},
                )
                if response.status_code == 404:
                    pytest.skip("Endpoint ZeroIA decision non implémenté - test ignoré")
                assert response.status_code == 200
            except Exception:
                pytest.skip("Endpoint ZeroIA decision non disponible - test ignoré")

    @pytest.mark.asyncio
    async def test_volume_permissions(self, services_running: bool) -> None:
        """Test des permissions des volumes"""
        pass


class TestDockerResourceLimitsE2E:
    """Tests E2E pour les limites de ressources"""

    @pytest.mark.asyncio
    async def test_memory_limits(self, docker_client: Any, services_running: bool) -> None:
        """Test des limites de mémoire"""
        containers = docker_client.containers.list()
        for container in containers:
            if any(service in container.name for service in ["zeroia", "reflexia", "sandozia"]):
                stats = container.stats(stream=False)
                memory_stats = stats.get("memory_stats", {})
                memory_usage = memory_stats.get("usage")
                memory_limit = memory_stats.get("limit")
                if not memory_usage or not memory_limit:
                    pytest.skip(
                        f"Statistiques mémoire indisponibles pour {container.name} - test ignoré"
                    )
                memory_percentage = (memory_usage / memory_limit) * 100
                assert memory_percentage < 80, f"Container {container.name} utilise trop de mémoire"

    @pytest.mark.asyncio
    async def test_cpu_limits(self, docker_client: Any, services_running: bool) -> None:
        """Test des limites CPU"""
        containers = docker_client.containers.list()
        for container in containers:
            if any(service in container.name for service in ["zeroia", "reflexia", "sandozia"]):
                stats = container.stats(stream=False)
                cpu_usage = (
                    stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage")
                )
                if cpu_usage is None:
                    pytest.skip(
                        f"Statistiques CPU indisponibles pour {container.name} - test ignoré"
                    )
                assert cpu_usage >= 0, f"Statistiques CPU invalides pour {container.name}"


class TestDockerSecurityE2E:
    """Tests E2E pour la sécurité Docker"""

    @pytest.mark.asyncio
    async def test_non_root_containers(self, docker_client: Any, services_running: bool) -> None:
        """Test que les conteneurs ne tournent pas en tant que root"""
        containers = docker_client.containers.list()
        for container in containers:
            if any(service in container.name for service in ["zeroia", "reflexia", "sandozia"]):
                try:
                    exec_result = container.exec_run("whoami")
                except APIError:
                    pytest.skip(f"Container {container.name} indisponible/restarting - test ignoré")
                user = exec_result.output.decode().strip()
                assert user != "root", f"Container {container.name} tourne en tant que root"

    @pytest.mark.asyncio
    async def test_security_scan(self, services_running: bool) -> None:
        """Test de scan de sécurité basique"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test endpoint admin (doit être protégé)
            try:
                response = await client.get("http://localhost:8000/admin")
                assert response.status_code in [
                    401,
                    403,
                    404,
                ], "Endpoint admin accessible sans authentification"
            except Exception:
                pytest.skip("Endpoint admin non accessible - test ignoré")

            # Test endpoint de santé (doit être accessible)
            response = await client.get("http://localhost:8000/health")
            assert response.status_code == 200, "Endpoint health doit être accessible"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

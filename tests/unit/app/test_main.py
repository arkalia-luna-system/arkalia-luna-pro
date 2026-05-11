"""Tests pour app/main.py"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from prometheus_client import CONTENT_TYPE_LATEST

from app.main import app, metrics

client = TestClient(app)


def test_root_endpoint() -> None:
    """Test de l'endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "🌕 Arkalia-LUNA Pro API"
    assert data["version"] == "2.8.0"
    assert data["status"] == "active"
    assert "assistantia" in data["modules"]
    assert "reflexia" in data["modules"]
    assert "zeroia" in data["modules"]
    assert isinstance(data["uptime"], float)
    assert datetime.fromisoformat(data["timestamp"])


def test_health_endpoint() -> None:
    """Test de l'endpoint health"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "arkalia-api"}


def test_zeroia_health_endpoint() -> None:
    """Test de l'endpoint health ZeroIA exposé par l'API principale."""
    response = client.get("/zeroia/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data or "error" in data


def test_reflexia_health_endpoint() -> None:
    """Test de l'endpoint health Reflexia exposé par le router /reflexia."""
    response = client.get("/reflexia/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_zeroia_decision_endpoint() -> None:
    """Test de l'endpoint de compatibilité /zeroia/decision."""
    response = client.post("/zeroia/decision", json={"context": {}, "priority": "low"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["module"] == "zeroia"
    assert data["decision"] == "accepted"


@patch("psutil.cpu_percent")
@patch("psutil.virtual_memory")
@patch("psutil.disk_usage")
def test_status_endpoint(mock_disk: MagicMock, mock_memory: MagicMock, mock_cpu: MagicMock) -> None:
    """Test de l'endpoint status"""
    # Configuration des mocks
    mock_cpu.return_value = 45.2
    mock_memory.return_value = MagicMock(percent=68.7)
    mock_disk.return_value = MagicMock(percent=72.1)

    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()

    assert data["service"] == "arkalia-api"
    assert data["version"] == "2.8.0"
    assert data["status"] == "active"
    assert isinstance(data["uptime_seconds"], float)
    assert data["modules"] == {"assistantia": "active", "reflexia": "active", "zeroia": "active"}
    assert data["metrics"] == "available"
    assert data["system"]["cpu_percent"] == 45.2
    assert data["system"]["memory_percent"] == 68.7
    assert data["system"]["disk_usage"] == 72.1


@patch("psutil.cpu_percent")
@patch("psutil.virtual_memory")
def test_metrics_endpoint(mock_memory: MagicMock, mock_cpu: MagicMock) -> None:
    """Test de l'endpoint metrics"""
    # Configuration des mocks
    mock_cpu.return_value = 45.2
    mock_memory.return_value = MagicMock(used=4096)

    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"] == CONTENT_TYPE_LATEST
    assert b"arkalia_system_uptime" in response.content
    assert b"arkalia_memory_usage" in response.content
    assert b"arkalia_cpu_usage" in response.content


@patch("psutil.cpu_percent", side_effect=Exception("Test error"))
def test_metrics_endpoint_error(mock_cpu: MagicMock) -> None:
    """Test de l'endpoint metrics avec erreur"""
    response = client.get("/metrics")
    assert response.status_code == 500
    assert "error" in response.json()
    assert "Test error" in response.json()["error"]


def test_metrics_middleware() -> None:
    """Test du middleware de métriques"""
    # Réinitialiser les compteurs
    metrics.arkalia_requests_total._metrics.clear()
    metrics.arkalia_request_duration._metrics.clear()

    # Faire une requête
    response = client.get("/", headers={"origin": "http://test.com"})
    assert response.status_code == 200

    # Vérifier les métriques
    found = False
    for metric in metrics.arkalia_requests_total._metrics.values():
        if metric._labelvalues == ("GET", "/", "200"):
            # Utiliser ._value.get() pour accéder à la valeur réelle
            assert metric._value.get() == 1  # type: ignore[attr-defined]
            found = True
            break
    if not found:
        pytest.fail("Métrique de requête non trouvée")

    # Vérifier la durée
    assert len(metrics.arkalia_request_duration._metrics) > 0


def test_cors_middleware() -> None:
    """Test de la configuration CORS"""
    allowed_origin = "http://localhost:5173"

    # Test avec une requête GET depuis une origine autorisée
    response = client.get("/", headers={"origin": allowed_origin})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == allowed_origin
    # Test avec une requête OPTIONS (preflight)
    response = client.options(
        "/",
        headers={
            "origin": allowed_origin,
            "access-control-request-method": "GET",
            "access-control-request-headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == allowed_origin
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "content-type" in response.headers["access-control-allow-headers"].lower()


def test_sensitive_endpoints_require_api_key_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ARKALIA_API_KEY", "unit-test-key")

    unauthorized = client.get("/status")
    assert unauthorized.status_code == 401

    authorized = client.get("/status", headers={"X-API-Key": "unit-test-key"})
    assert authorized.status_code == 200


def test_print_status(caplog: pytest.LogCaptureFixture) -> None:
    """Test de la fonction print_status"""
    from app.main import print_status

    print_status()

    # Vérifier que le message a été loggé
    assert "Arkalia-LUNA is active and running" in caplog.text

"""Tests pour app/main.py"""

import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import psutil
import pytest
from fastapi.testclient import TestClient
from prometheus_client import CONTENT_TYPE_LATEST

from app.main import app, metrics, start_time

client = TestClient(app)


def test_root_endpoint():
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


def test_health_endpoint():
    """Test de l'endpoint health"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "arkalia-api"}


@patch("psutil.cpu_percent")
@patch("psutil.virtual_memory")
@patch("psutil.disk_usage")
def test_status_endpoint(mock_disk, mock_memory, mock_cpu):
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
def test_metrics_endpoint(mock_memory, mock_cpu):
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
def test_metrics_endpoint_error(mock_cpu):
    """Test de l'endpoint metrics avec erreur"""
    response = client.get("/metrics")
    assert response.status_code == 500
    assert "error" in response.json()
    assert "Test error" in response.json()["error"]


def test_metrics_middleware():
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
            assert metric._value.get() == 1
            found = True
            break
    if not found:
        pytest.fail("Métrique de requête non trouvée")

    # Vérifier la durée
    assert len(metrics.arkalia_request_duration._metrics) > 0


def test_cors_middleware():
    """Test de la configuration CORS"""
    # Test avec une requête GET avec Origin
    response = client.get("/", headers={"origin": "http://test.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    # Accepter '*' ou l'origine demandée
    assert response.headers["access-control-allow-origin"] in ("*", "http://test.com")
    # Test avec une requête OPTIONS (preflight)
    response = client.options(
        "/",
        headers={
            "origin": "http://test.com",
            "access-control-request-method": "GET",
            "access-control-request-headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] in ("*", "http://test.com")
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "content-type" in response.headers["access-control-allow-headers"].lower()


def test_print_status(caplog):
    """Test de la fonction print_status"""
    from app.main import print_status

    print_status()

    # Vérifier que le message a été loggé
    assert "Arkalia-LUNA is active and running" in caplog.text

from unittest.mock import patch

from fastapi.testclient import TestClient

from core.ark_logger import ark_logger
from modules.assistantia.core import app


def test_print_routes():
    """Affiche les routes disponibles pour debug."""
    ark_logger.info("\n--- ROUTES DISPONIBLES ---", extra={"arkalia_module": "modules"})
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            ark_logger.info(
                f"{route.path} | methods: {route.methods}", extra={"arkalia_module": "modules"}
            )
    ark_logger.info("--- FIN ROUTES ---\n", extra={"arkalia_module": "modules"})


def test_chat_endpoint_success():
    """Teste l'endpoint /api/v1/chat avec un message valide."""
    with (
        patch(
            "modules.assistantia.core.real_query_ollama",
            return_value="Réponse simulée pour le test",
        ),
        patch("modules.assistantia.core._check_ollama_health", return_value=True),
    ):
        client = TestClient(app)
        response = client.post("/api/v1/chat", json={"message": "Bonjour"})
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 3


def test_chat_endpoint_empty_payload():
    """Teste l'endpoint /api/v1/chat avec un payload vide."""
    with (
        patch(
            "modules.assistantia.core.real_query_ollama",
            return_value="Réponse simulée pour le test",
        ),
        patch("modules.assistantia.core._check_ollama_health", return_value=True),
    ):
        client = TestClient(app)
        response = client.post("/api/v1/chat", json={})
        assert response.status_code == 422


def test_chat_endpoint_empty_message():
    """Teste l'endpoint /api/v1/chat avec un message vide."""
    with (
        patch(
            "modules.assistantia.core.real_query_ollama",
            return_value="Réponse simulée pour le test",
        ),
        patch("modules.assistantia.core._check_ollama_health", return_value=True),
    ):
        client = TestClient(app)
        response = client.post("/api/v1/chat", json={"message": ""})
        assert response.status_code == 422
        assert "String should have at least 1 character" in str(response.json()["detail"])


def test_chat_endpoint_missing_message():
    """Teste l'endpoint /api/v1/chat sans le champ message."""
    with (
        patch(
            "modules.assistantia.core.real_query_ollama",
            return_value="Réponse simulée pour le test",
        ),
        patch("modules.assistantia.core._check_ollama_health", return_value=True),
    ):
        client = TestClient(app)
        response = client.post("/api/v1/chat", json={"other_field": "value"})
        assert response.status_code == 422


def test_health_endpoint():
    """Teste l'endpoint /api/v1/health."""
    with patch("modules.assistantia.core._check_ollama_health", return_value=True):
        client = TestClient(app)
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "ollama_available" in data
        assert "arkalia_modules" in data
        assert "uptime" in data
        assert "version" in data


def test_metrics_endpoint():
    """Teste l'endpoint /api/v1/metrics."""
    client = TestClient(app)
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    # Les métriques Prometheus sont du texte brut
    assert "assistantia_prompts_total" in response.text


def test_models_endpoint():
    """Teste l'endpoint /api/v1/models."""
    with patch(
        "modules.assistantia.core.get_available_models", return_value={"models": ["mistral:latest"]}
    ):
        client = TestClient(app)
        response = client.get("/api/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data


def test_root_endpoint():
    """Teste l'endpoint racine /."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "AssistantIA"
    assert "version" in data
    assert data["status"] == "active"

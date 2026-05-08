from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from modules.assistantia.core import app


@pytest.fixture(scope="module")
def test_client() -> TestClient:
    """Client de test FastAPI pour tous les tests du module."""
    return TestClient(app)


def test_root_get(test_client: TestClient) -> None:
    """Teste l'endpoint racine (GET /) — tolère 404 si non défini."""
    response = test_client.get("/")
    assert response.status_code in [200, 404]


def test_chat_post(test_client: TestClient) -> None:
    """Teste l'endpoint POST /chat avec un message simple"""

    def mock_query_ollama(prompt: str, model: str = "mistral", temperature: float = 0.7) -> str:
        return "Tu as dit : Bonjour"

    with (
        patch("modules.assistantia.core.real_query_ollama", side_effect=mock_query_ollama),
        patch("modules.assistantia.core._check_ollama_health", return_value=True),
    ):
        response = test_client.post("/api/v1/chat", json={"message": "Bonjour"})
        assert response.status_code == 200

        response_data = response.json()
        assert "response" in response_data
        # La réponse contient le message mocké + contexte Arkalia
        response_text = response_data["response"]
        assert "Tu as dit : Bonjour" in response_text


def test_chat_post_empty_message(test_client: TestClient) -> None:
    """Teste l'endpoint /chat avec un message vide → 400 ou 422 attendu."""
    response = test_client.post("/api/v1/chat", json={"message": ""})
    assert response.status_code in [400, 422]
    detail = response.json()["detail"]
    if isinstance(detail, list):
        # Erreur 422 : liste d'erreurs de validation
        assert any("message" in (err.get("msg", "") + str(err.get("loc", ""))) for err in detail)
    else:
        # Erreur 400 : message d'erreur personnalisé
        assert "message" in detail.lower()


def test_chat_post_no_message_field(test_client: TestClient) -> None:
    """Teste l'endpoint /chat sans champ message → 422 attendu."""
    response = test_client.post("/api/v1/chat", json={})
    assert response.status_code == 422  # Erreur de validation automatique FastAPI


def test_chat_post_long_message(test_client: TestClient) -> None:
    """Teste l'endpoint POST /chat avec un message long"""
    long_msg = "A" * 1000

    def mock_query_ollama(prompt: str, model: str = "mistral", temperature: float = 0.7) -> str:
        return "Message reçu"

    with (
        patch("modules.assistantia.core.real_query_ollama", side_effect=mock_query_ollama),
        patch("modules.assistantia.core._check_ollama_health", return_value=True),
    ):
        response = test_client.post("/api/v1/chat", json={"message": long_msg})
        assert response.status_code == 200

        response_data = response.json()
        assert "response" in response_data
        # La réponse contient le message mocké + contexte Arkalia
        assert "Message reçu" in response_data["response"]


def test_sensitive_endpoints_require_api_key_when_configured(
    test_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ARKALIA_API_KEY", "assistantia-test-key")

    unauthorized_models = test_client.get("/api/v1/models")
    assert unauthorized_models.status_code == 401

    unauthorized_metrics = test_client.get("/api/v1/metrics")
    assert unauthorized_metrics.status_code == 401

    with patch(
        "modules.assistantia.core.get_available_models",
        return_value={"models": ["mistral:latest"]},
    ):
        authorized_models = test_client.get(
            "/api/v1/models", headers={"X-API-Key": "assistantia-test-key"}
        )
        assert authorized_models.status_code == 200

    authorized_metrics = test_client.get(
        "/api/v1/metrics", headers={"X-API-Key": "assistantia-test-key"}
    )
    assert authorized_metrics.status_code == 200

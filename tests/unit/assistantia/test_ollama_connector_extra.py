from typing import Any

import pytest
import requests

from modules.assistantia.utils import ollama_connector


def test_query_ollama_function_exists() -> None:
    assert hasattr(ollama_connector, "query_ollama")


def test_query_ollama_invalid_model(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock get_available_models pour retourner des modèles connus
    def mock_get_models() -> dict:
        return {"models": [{"name": "mistral:latest"}, {"name": "llama2:latest"}]}

    monkeypatch.setattr(ollama_connector, "get_available_models", mock_get_models)

    with pytest.raises(ValueError):
        ollama_connector.query_ollama("prompt", model="model-inconnu")


def test_query_ollama_bad_model(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock get_available_models pour retourner des modèles connus
    def mock_get_models() -> dict:
        return {"models": [{"name": "mistral:latest"}, {"name": "llama2:latest"}]}

    monkeypatch.setattr(ollama_connector, "get_available_models", mock_get_models)

    with pytest.raises(ValueError):
        ollama_connector.query_ollama("prompt", model="inconnu")


def test_query_ollama_empty_prompt() -> None:
    response = ollama_connector.query_ollama("", model="mistral")
    assert isinstance(response, str)
    assert response == "[⚠️ Réponse IA vide]"


def test_query_ollama_valid_prompt() -> None:
    response = ollama_connector.query_ollama("Hello", model="mistral")
    assert isinstance(response, str)
    assert response != "[⚠️ Réponse IA vide]"


def test_query_ollama_network_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_post(*args: Any, **kwargs: Any) -> None:
        raise requests.exceptions.ConnectionError

    monkeypatch.setattr("requests.post", mock_post)

    response = ollama_connector.query_ollama("Hello", model="mistral")
    assert "Erreur IA" in response


def test_query_ollama_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_post(*args: Any, **kwargs: Any) -> None:
        raise requests.exceptions.Timeout

    monkeypatch.setattr("requests.post", mock_post)

    response = ollama_connector.query_ollama("Hello", model="mistral")
    assert "Erreur IA" in response


def test_query_ollama_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class MockResponse:
        def __init__(self, status_code: int) -> None:
            self.status_code = status_code
            self.text = "Error"

        def json(self) -> dict[str, Any]:
            return {}

        def raise_for_status(self) -> None:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def mock_post(*args: Any, **kwargs: Any) -> MockResponse:
        return MockResponse(500)

    monkeypatch.setattr("requests.post", mock_post)

    response = ollama_connector.query_ollama("Hello", model="mistral")
    assert "Erreur IA" in response

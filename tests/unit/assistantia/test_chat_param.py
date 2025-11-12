from unittest.mock import patch

from fastapi.testclient import TestClient

from modules.assistantia.core import app

client = TestClient(app)


def test_chat_with_lang_and_mode() -> None:
    """Vérifie que les paramètres `lang` et `mode` sont acceptés."""
    payload = {"message": "Salut", "lang": "fr", "mode": "friendly"}
    with patch("modules.assistantia.core._check_ollama_health", return_value=True):
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        assert "response" in response.json()

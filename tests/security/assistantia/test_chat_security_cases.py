from unittest.mock import patch

from fastapi.testclient import TestClient

from modules.assistantia.core import app

client = TestClient(app)


def test_chat_sql_injection_like() -> None:
    """Teste la protection contre les tentatives d'injection SQL-like"""
    payload = {"message": "'; DROP TABLE users; --"}
    with (
        patch("modules.assistantia.core.real_query_ollama", return_value="Message sécurisé"),
        patch("modules.assistantia.core._check_ollama_health", return_value=True),
    ):
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        assert "response" in response.json()

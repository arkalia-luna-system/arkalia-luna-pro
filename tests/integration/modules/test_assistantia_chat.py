import pytest
from fastapi.testclient import TestClient

from modules.assistantia.core import app


@pytest.fixture(scope="module")
def test_client():
    """Client de test FastAPI pour tous les tests du module."""
    return TestClient(app)


def test_chat_post_empty_message(test_client: TestClient):
    """
    Teste l'endpoint /api/v1/chat avec un message vide.
    Erreur 422 attendue (validation Pydantic).
    """
    response = test_client.post("/api/v1/chat", json={"message": ""})
    assert response.status_code == 422
    assert "String should have at least 1 character" in str(response.json()["detail"])

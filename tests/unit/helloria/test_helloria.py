import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from modules.helloria.core import app

client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_echo() -> None:
    response = client.post("/echo", json={"message": "Salut"})
    assert response.status_code == 200
    assert response.json()["echo"] == "Salut"


def test_ping() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_status() -> None:
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_status_response_format() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/status")
        data = response.json()
        assert "status" in data
        assert data["status"] == "active"
        assert "service" in data
        assert "modules" in data

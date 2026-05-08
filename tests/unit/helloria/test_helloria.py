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


def test_sensitive_endpoints_require_api_key_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ARKALIA_API_KEY", "helloria-test-key")

    unauthorized_status = client.get("/status")
    assert unauthorized_status.status_code == 401

    unauthorized_metrics = client.get("/metrics")
    assert unauthorized_metrics.status_code == 401

    unauthorized_reflexia_check = client.get("/reflexia/reflexia/check")
    assert unauthorized_reflexia_check.status_code == 401

    unauthorized_reflexia_metrics = client.get("/reflexia/reflexia/metrics")
    assert unauthorized_reflexia_metrics.status_code == 401

    authorized_status = client.get("/status", headers={"X-API-Key": "helloria-test-key"})
    assert authorized_status.status_code == 200

    authorized_metrics = client.get("/metrics", headers={"X-API-Key": "helloria-test-key"})
    assert authorized_metrics.status_code == 200

    authorized_reflexia_check = client.get(
        "/reflexia/reflexia/check", headers={"X-API-Key": "helloria-test-key"}
    )
    assert authorized_reflexia_check.status_code == 200

    authorized_reflexia_metrics = client.get(
        "/reflexia/reflexia/metrics", headers={"X-API-Key": "helloria-test-key"}
    )
    assert authorized_reflexia_metrics.status_code == 200


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

from fastapi.testclient import TestClient

from modules.helloria.core import app

client = TestClient(app)


def test_core_api_contract_without_external_dependencies() -> None:
    root_response = client.get("/")
    assert root_response.status_code == 200
    assert "message" in root_response.json()

    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"

    echo_response = client.post("/echo", json={"message": "ping"})
    assert echo_response.status_code == 200
    assert echo_response.json()["echo"] == "ping"

    status_response = client.get("/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["service"] == "arkalia-api"
    assert status_data["status"] == "active"
    assert "system" in status_data


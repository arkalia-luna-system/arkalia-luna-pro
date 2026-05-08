from fastapi.testclient import TestClient

from modules.helloria.core import app

client = TestClient(app)


def test_docs_and_openapi_contract_local() -> None:
    docs_response = client.get("/docs")
    assert docs_response.status_code == 200
    assert "text/html" in docs_response.headers.get("content-type", "")

    openapi_response = client.get("/openapi.json")
    assert openapi_response.status_code == 200
    schema = openapi_response.json()
    assert "openapi" in schema
    assert "paths" in schema


def test_metrics_and_chat_validation_contract_local() -> None:
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert metrics_response.text

    invalid_chat_response = client.post(
        "/chat",
        content=b'{"message":"',
        headers={"Content-Type": "application/json"},
    )
    assert invalid_chat_response.status_code == 400
    assert invalid_chat_response.json()["detail"] == "Payload JSON invalide"


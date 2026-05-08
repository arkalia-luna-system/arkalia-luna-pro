import time

from fastapi.testclient import TestClient

from modules.helloria.core import app

client = TestClient(app)


def test_health_endpoint_local_response_time_budget() -> None:
    start = time.perf_counter()
    response = client.get("/health")
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    # Budget large pour éviter la flakiness tout en capturant les régressions majeures.
    assert elapsed < 1.0


def test_status_endpoint_local_response_time_budget() -> None:
    start = time.perf_counter()
    response = client.get("/status")
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 1.5


from fastapi.testclient import TestClient

from modules.helloria.core import app

client = TestClient(app)


def test_options_and_basic_resilience_contract_local() -> None:
    options_response = client.options("/health")
    # Selon middleware/routing, OPTIONS peut être 200/204/405 mais ne doit pas crasher.
    assert options_response.status_code in {200, 204, 405}

    # Vérifie qu'un payload inattendu ne provoque pas d'erreur serveur non gérée.
    invalid_echo_response = client.post("/echo", json={"unexpected": "value"})
    assert invalid_echo_response.status_code in {400, 422}

    # Vérifie qu'une route inexistante reste correctement isolée.
    unknown_route_response = client.get("/does-not-exist")
    assert unknown_route_response.status_code == 404


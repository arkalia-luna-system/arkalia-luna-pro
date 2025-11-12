# tests/test_base.py

from fastapi.testclient import TestClient

from modules.helloria.core import app  # Assure-toi que modules/helloria/core.py expose bien `app`

client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")
    data = response.json()
    assert response.status_code == 200
    assert "message" in data
    assert "Helloria" in data["message"] or "Arkalia" in data["message"]

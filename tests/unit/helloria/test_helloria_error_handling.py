from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

from modules.helloria import core as helloria_core

client = TestClient(helloria_core.app)


def test_chat_returns_400_on_invalid_json_payload() -> None:
    response = client.post(
        "/chat",
        content=b'{"message": "Salut"',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Payload JSON invalide"


def test_metrics_returns_500_when_fallback_raises(monkeypatch: MonkeyPatch) -> None:
    def fail_metrics() -> dict[str, float]:
        raise RuntimeError("boom")

    monkeypatch.setattr(helloria_core, "_get_fallback_metrics", fail_metrics)

    response = client.get("/metrics")
    assert response.status_code == 500
    assert response.json()["detail"] == "Erreur métriques Helloria"


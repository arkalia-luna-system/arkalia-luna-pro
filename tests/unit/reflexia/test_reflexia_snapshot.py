import json
from pathlib import Path

from modules.reflexia.logic.snapshot import save_snapshot


def test_snapshot_file_creation(tmp_path: Path) -> None:
    # Remplace le chemin du fichier temporairement
    test_file = tmp_path / "reflexia_state.toml"

    metrics = {"cpu": 50, "ram": 40, "latency": 200}
    status = "ok"

    # Simule un enregistrement
    from modules.reflexia.logic import snapshot

    snapshot.SNAPSHOT_FILE = test_file
    save_snapshot(metrics, status)

    assert test_file.exists()
    data = json.loads(test_file.read_text())
    assert data["status"] == "ok"
    assert "timestamp" in data

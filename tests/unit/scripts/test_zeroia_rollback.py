import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import toml

from scripts import _zeroia_rollback as zeroia_rollback

PROJECT_ROOT = Path(__file__).resolve().parents[3]


# 📁 Setup de répertoires temporaires pour simuler l'état ZeroIA
@pytest.fixture
def temp_env(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        state_file = tmp_path / "zeroia_state.toml"
        snapshot_file = tmp_path / "zeroia_state_snapshot.toml"
        backup_file = tmp_path / "zeroia_state_backup.toml"
        log_file = tmp_path / "zeroia_rollback.log"
        failure_log = tmp_path / "failure_analysis.md"

        # Initialisation fichiers
        state_file.write_text('timestamp = "TEST"\n[decision]\nlast_decision = "noop"\n')
        snapshot_file.write_text('timestamp = "SNAPSHOT"\n[decision]\nlast_decision = "snapshot"\n')

        # Patch chemins internes du module
        monkeypatch.setattr(zeroia_rollback, "STATE_FILE", state_file)
        monkeypatch.setattr(zeroia_rollback, "SNAPSHOT_FILE", snapshot_file)
        monkeypatch.setattr(zeroia_rollback, "BACKUP_FILE", backup_file)
        monkeypatch.setattr(zeroia_rollback, "LOG_FILE", log_file)
        monkeypatch.setattr(zeroia_rollback, "FAILURE_LOG", failure_log)

        yield {
            "state_file": state_file,
            "snapshot_file": snapshot_file,
            "backup_file": backup_file,
            "log_file": log_file,
            "failure_log": failure_log,
        }


def test_backup_current_state(temp_env) -> None:
    zeroia_rollback.backup_current_state()
    assert temp_env["backup_file"].exists()
    assert "timestamp" in temp_env["backup_file"].read_text()


def test_restore_snapshot_success(temp_env) -> None:
    assert zeroia_rollback.restore_snapshot() is True
    assert temp_env["state_file"].read_text().find("snapshot") != -1


def test_restore_snapshot_failure(monkeypatch, temp_env) -> None:
    monkeypatch.setattr(zeroia_rollback, "SNAPSHOT_FILE", Path("nonexistent.toml"))
    assert zeroia_rollback.restore_snapshot() is False


def test_log_failure(temp_env) -> None:
    zeroia_rollback.log_failure()
    assert temp_env["failure_log"].exists()
    assert "Échec détecté" in temp_env["failure_log"].read_text()


def test_log(temp_env) -> None:
    zeroia_rollback.log("test log line")
    content = temp_env["log_file"].read_text()
    assert "[rollback] test log line" in content


def test_rollback_success(temp_env) -> None:
    temp_env["backup_file"].write_text(
        'timestamp = "BACKUP"\n[decision]\nlast_decision = "rollback"\n'
    )
    zeroia_rollback.rollback_from_backup()
    assert "rollback" in temp_env["state_file"].read_text()


def test_rollback_failure(monkeypatch) -> None:
    monkeypatch.setattr(zeroia_rollback, "BACKUP_FILE", Path("nonexistent.toml"))
    monkeypatch.setattr(zeroia_rollback, "STATE_FILE", Path("state/zeroia_state.toml"))
    zeroia_rollback.rollback_from_backup()


def test_zeroia_rollback_script_runs(tmp_path: Path) -> None:
    """Test que le script de rollback s'exécute correctement."""

    # Créer un état de test
    state_dir = Path("data/zeroia")
    state_dir.mkdir(parents=True, exist_ok=True)

    test_state = {
        "status": {"active": True, "last_check": "2024-03-20T12:00:00", "decision": "continue"},
        "metrics": {"cpu_usage": 45.2, "memory_usage": 68.7, "response_time": 0.123},
    }

    state_file = state_dir / "state.toml"
    with open(state_file, "w", encoding="utf-8") as f:
        toml.dump(test_state, f)

    # Configurer l'environnement pour les imports
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + ":" + env.get("PYTHONPATH", "")

    # Exécuter le script avec --force
    result = subprocess.run(
        ["python", "scripts/zeroia_rollback.py", "--force", "--silent"],
        capture_output=True,
        text=True,
        env=env,
        cwd=PROJECT_ROOT,
    )

    # Vérifier que le script s'est exécuté avec succès
    assert (
        result.returncode == 0
    ), f"Script a échoué avec code {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"

    # Vérifier qu'un backup a été créé
    backup_dir = Path("data/backups")
    assert backup_dir.exists(), "Le répertoire de backup n'a pas été créé"
    assert any(backup_dir.iterdir()), "Aucun fichier de backup n'a été créé"

import os
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import toml

from scripts import _zeroia_rollback as zeroia_rollback

PROJECT_ROOT = Path(__file__).resolve().parents[3]


# 📁 Setup de répertoires temporaires pour simuler l'état ZeroIA
@pytest.fixture
def temp_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Path]]:
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


def test_backup_current_state(temp_env: dict[str, Path]) -> None:
    zeroia_rollback.backup_current_state()
    assert temp_env["backup_file"].exists()
    assert "timestamp" in temp_env["backup_file"].read_text()


def test_restore_snapshot_success(temp_env: dict[str, Path]) -> None:
    assert zeroia_rollback.restore_snapshot() is True
    assert temp_env["state_file"].read_text().find("snapshot") != -1


def test_restore_snapshot_failure(
    monkeypatch: pytest.MonkeyPatch, temp_env: dict[str, Path]
) -> None:
    monkeypatch.setattr(zeroia_rollback, "SNAPSHOT_FILE", Path("nonexistent.toml"))
    assert zeroia_rollback.restore_snapshot() is False


def test_log_failure(temp_env: dict[str, Path]) -> None:
    zeroia_rollback.log_failure()
    assert temp_env["failure_log"].exists()
    assert "Échec détecté" in temp_env["failure_log"].read_text()


def test_log(temp_env: dict[str, Path]) -> None:
    zeroia_rollback.log("test log line")
    content = temp_env["log_file"].read_text()
    assert "[rollback] test log line" in content


def test_rollback_success(temp_env: dict[str, Path]) -> None:
    temp_env["backup_file"].write_text(
        'timestamp = "BACKUP"\n[decision]\nlast_decision = "rollback"\n'
    )
    zeroia_rollback.rollback_from_backup()
    assert "rollback" in temp_env["state_file"].read_text()


def test_rollback_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(zeroia_rollback, "BACKUP_FILE", Path("nonexistent.toml"))
    monkeypatch.setattr(zeroia_rollback, "STATE_FILE", Path("state/zeroia_state.toml"))
    zeroia_rollback.rollback_from_backup()


def test_zeroia_rollback_script_runs(tmp_path: Path) -> None:
    """Test que le script de rollback s'exécute correctement."""

    # Créer les répertoires nécessaires
    state_dir = PROJECT_ROOT / "modules" / "zeroia" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Créer un fichier d'état de test
    test_state = {
        "status": {"active": True, "last_check": "2024-03-20T12:00:00", "decision": "continue"},
        "metrics": {"cpu_usage": 45.2, "memory_usage": 68.7, "response_time": 0.123},
    }

    state_file = state_dir / "zeroia_state.toml"
    with open(state_file, "w", encoding="utf-8") as f:
        toml.dump(test_state, f)

    # Vérifier que le fichier existe avant l'exécution
    assert state_file.exists(), f"Le fichier d'état n'a pas été créé à {state_file}"

    # Vérifier que le répertoire logs existe (nécessaire pour le script)
    assert logs_dir.exists(), f"Le répertoire logs n'existe pas à {logs_dir}"

    # Configurer l'environnement pour les imports
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + ":" + env.get("PYTHONPATH", "")

    # Exécuter le script avec --silent depuis PROJECT_ROOT
    result = subprocess.run(
        ["python", "scripts/_zeroia_rollback.py", "--silent"],
        capture_output=True,
        text=True,
        env=env,
        cwd=PROJECT_ROOT,
    )

    # Vérifier que le script s'est exécuté avec succès
    assert (
        result.returncode == 0
    ), f"Script a échoué avec code {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"

    # Vérifier qu'un backup a été créé dans le bon emplacement
    # Le script crée le backup seulement si STATE_FILE.exists()
    backup_file = state_dir / "zeroia_state_backup.toml"

    # Si le backup n'existe pas, vérifier si le fichier d'état existe toujours
    if not backup_file.exists():
        # Vérifier si le fichier d'état existe toujours
        state_exists = state_file.exists()
        # Vérifier si le répertoire existe
        dir_exists = state_dir.exists()
        # Vérifier les permissions
        error_msg = (
            f"Le fichier de backup n'a pas été créé à {backup_file}.\n"
            f"État du fichier: exists={state_exists}, path={state_file}\n"
            f"Répertoire: exists={dir_exists}, path={state_dir}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert backup_file.exists(), error_msg

    # Vérifier que le backup contient les bonnes données
    if backup_file.exists():
        backup_content = toml.loads(backup_file.read_text(encoding="utf-8"))
        # Le backup doit contenir soit "status" (format test), soit les champs du format réel
        assert (
            "status" in backup_content or "last_decision" in backup_content
        ), f"Le backup ne contient ni 'status' ni 'last_decision'. Contenu: {list(backup_content.keys())}"
        # Si c'est le format test, vérifier status
        if "status" in backup_content:
            assert (
                backup_content["status"]["active"] is True
            ), "Le backup n'a pas les bonnes données"

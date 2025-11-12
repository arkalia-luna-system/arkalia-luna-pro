import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import toml

from modules.zeroia.utils.state_writer import check_health

STATE_PATH = Path("modules/zeroia/state/zeroia_state.toml")


def test_healthcheck_active(tmp_path: Path) -> None:
    path = tmp_path / "zeroia_state.toml"
    path.write_text(
        """
active = true

[decision]
last_decision = "reduce_load"
confidence_score = 0.85
justification = "Test justification"
timestamp = "2024-01-01T00:00:00"
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/healthcheck_zeroia.py"],
        env={**os.environ, "ZEROIA_STATE_PATH": str(path)},
        capture_output=True,
        text=True,
        shell=False,
    )

    assert result.returncode == 0
    assert "✅" in result.stdout


def test_healthcheck_inactive(tmp_path: Path) -> None:
    path = tmp_path / "zeroia_state.toml"
    path.write_text(
        """
active = false

[decision]
last_decision = "monitor"
confidence_score = 0.85
justification = "Test justification"
timestamp = "2024-01-01T00:00:00"
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/healthcheck_zeroia.py"],
        env={**os.environ, "ZEROIA_STATE_PATH": str(path)},
        capture_output=True,
        text=True,
        shell=False,
    )

    assert result.returncode == 0  # Le script vérifie la structure, pas le statut actif
    assert "✅" in result.stdout


def test_healthcheck_missing(tmp_path: Path) -> None:
    # Utiliser un chemin temporaire sécurisé au lieu de /tmp
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".toml") as tmp_file:
        non_existent_path = tmp_file.name
    # Supprimer le fichier pour simuler un chemin inexistant
    import os

    if os.path.exists(non_existent_path):
        os.unlink(non_existent_path)

    result = subprocess.run(
        [sys.executable, "scripts/healthcheck_zeroia.py"],
        env={**os.environ, "ZEROIA_STATE_PATH": non_existent_path},
        capture_output=True,
        text=True,
        shell=False,
    )

    assert result.returncode == 2  # Code d'erreur pour fichier manquant
    assert "❌ Fichier d'état introuvable." in result.stdout


@pytest.mark.parametrize(
    "state_data, expected",
    [
        ({"active": True, "decision": {"last_decision": "reduce_load"}}, True),
        ({"active": False, "decision": {"last_decision": "monitor"}}, False),
        ({}, False),
        ({"active": "banana"}, False),
        ({"decision": {}}, False),
    ],
)
def test_check_health_various_states(
    tmp_path: Path, state_data: dict[str, Any], expected: bool
) -> None:
    file = tmp_path / "state.toml"
    file.write_text(toml.dumps(state_data), encoding="utf-8")
    assert check_health(str(file)) == expected


@patch.dict(os.environ, {"FORCE_ZEROIA_OK": "1"})
def test_healthcheck_passes_forced() -> None:
    assert check_health(str(STATE_PATH)) is True

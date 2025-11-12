from pathlib import Path
from unittest import mock

import pytest

from scripts._generate_zeroia_status import (
    get_container_logs,
    get_container_status,
    parse_decisions,
    write_markdown,
)

DUMMY_LOGS = """
ZeroIA decided: reduce_load (confidence=0.75)
🟢 ZeroIA loop started successfully
ZeroIA decided: activate_watchdog (confidence=0.89)
ZeroIA decided: reboot_module (confidence=0.42)
"""


@pytest.fixture
def dummy_output_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    # Rediriger le fichier vers un chemin temporaire
    output_file = tmp_path / "zeroia_status.md"
    monkeypatch.setattr("scripts._generate_zeroia_status.OUTPUT_FILE", str(output_file))
    return output_file


def test_parse_decisions() -> None:
    decisions: list[str] = parse_decisions(DUMMY_LOGS)
    assert len(decisions) == 3
    assert "reduce_load" in decisions[0]
    assert "watchdog" in decisions[1]
    assert "reboot_module" in decisions[2]


@mock.patch("subprocess.check_output")
def test_get_container_status(mock_subproc: mock.MagicMock) -> None:
    mock_subproc.return_value = b"running"
    status = get_container_status("zeroia")
    assert status == "running"


@mock.patch("subprocess.check_output")
def test_get_container_logs(mock_subproc: mock.MagicMock) -> None:
    mock_subproc.return_value = DUMMY_LOGS.encode("utf-8")
    logs = get_container_logs("zeroia", tail=10)
    assert "reduce_load" in logs
    assert logs.count("ZeroIA decided") == 3


def test_write_markdown(dummy_output_file: Path) -> None:
    status = "running"
    decisions = [
        "ZeroIA decided: reduce_load (confidence=0.75)",
        "ZeroIA decided: activate_watchdog (confidence=0.89)",
    ]
    write_markdown(status, decisions)

    content = dummy_output_file.read_text(encoding="utf-8")
    assert "# 🤖 ZeroIA — Statut automatique" in content
    assert "- 🔄 Statut Docker : `running`" in content
    assert "reduce_load" in content
    assert "activate_watchdog" in content

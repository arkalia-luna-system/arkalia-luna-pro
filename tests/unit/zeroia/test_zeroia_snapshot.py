from pathlib import Path

import pytest
import toml


@pytest.fixture
def sample_snapshot(tmp_path: Path) -> Path:
    snapshot_content = """
    [snapshot_1]
    key1 = "value1"
    key2 = "value2"

    [snapshot_2]
    key1 = "value3"
    key2 = "value4"
    """
    snapshot_file = tmp_path / "snapshot.toml"
    snapshot_file.write_text(snapshot_content)
    return snapshot_file


def test_read_multi_section_snapshot(sample_snapshot: Path) -> None:
    data = toml.load(sample_snapshot)
    assert "snapshot_1" in data
    assert "snapshot_2" in data
    assert data["snapshot_1"]["key1"] == "value1"
    assert data["snapshot_2"]["key1"] == "value3"


def test_memory_link_previous_snapshot() -> None:
    # Assuming memory_link is a function or object that provides previous_snapshot
    # This is a placeholder for the actual implementation
    memory_link: dict[str, str] = {"previous_snapshot": "snapshot_1"}
    assert memory_link["previous_snapshot"] == "snapshot_1"

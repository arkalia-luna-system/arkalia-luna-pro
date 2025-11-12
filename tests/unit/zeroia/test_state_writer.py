import json
import os
import time
from pathlib import Path
from typing import Any

import toml

from modules.utils.helpers import save_json_if_changed, save_json_safe, save_toml_if_changed

TMP_TOML = "tests/tmp/test_state.toml"
TMP_JSON = "tests/tmp/test_dashboard.json"


def read_toml(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data: dict[str, Any] = toml.load(f)
        return data


def read_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
        return data


def setup_module(module: Any) -> None:
    Path("tests/tmp").mkdir(parents=True, exist_ok=True)


def teardown_module(module: Any) -> None:
    for path in [TMP_TOML, TMP_JSON]:
        if os.path.exists(path):
            os.remove(path)


def test_save_toml_changes_written() -> None:
    state = {"foo": "bar"}
    save_toml_if_changed(state.copy(), TMP_TOML)
    initial = read_toml(TMP_TOML)
    initial.pop("timestamp", None)  # Exclure l'horodatage

    # Re-save without changes (should NOT overwrite)
    time.sleep(1)
    save_toml_if_changed(state.copy(), TMP_TOML)
    after = read_toml(TMP_TOML)
    after.pop("timestamp", None)  # Exclure l'horodatage

    assert initial == after, "No change expected if data unchanged"

    # Modify content
    time.sleep(1)
    state["foo"] = "baz"
    save_toml_if_changed(state, TMP_TOML)
    modified = read_toml(TMP_TOML)

    assert modified["foo"] == "baz", "Change should be written"


def test_save_json_changes_written() -> None:
    dashboard = {"status": "ok"}
    save_json_if_changed(dashboard.copy(), TMP_JSON)
    initial = read_json(TMP_JSON)
    initial.pop("timestamp", None)  # Exclure l'horodatage

    # Re-save without changes
    time.sleep(1)
    save_json_if_changed(dashboard.copy(), TMP_JSON)
    after = read_json(TMP_JSON)
    after.pop("timestamp", None)  # Exclure l'horodatage

    assert initial == after, "No change expected if data unchanged"

    # Modify
    time.sleep(1)
    dashboard["status"] = "updated"
    save_json_if_changed(dashboard, TMP_JSON)
    modified = read_json(TMP_JSON)

    assert modified["status"] == "updated", "Change should be written"


def test_write_state_json(tmp_path: Path) -> None:
    path = tmp_path / "test_state.json"
    data = {"status": "ok", "value": 42}
    save_json_safe(data, path)

    with open(path) as f:
        loaded = json.load(f)
    assert loaded == data

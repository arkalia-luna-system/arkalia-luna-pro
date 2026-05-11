from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from modules.assistantia import core as assistantia_core


@pytest.mark.asyncio
async def test_get_arkalia_context_uses_to_thread_for_file_reads(monkeypatch: MonkeyPatch) -> None:
    calls: list[str] = []

    async def fake_to_thread(
        func: Callable[..., Any], *args: object, **kwargs: object
    ) -> dict[str, str]:
        calls.append(func.__name__)
        return func(*args, **kwargs)

    monkeypatch.setattr(assistantia_core.asyncio, "to_thread", fake_to_thread)

    def path_exists(_self: Path) -> bool:
        return True

    def path_iterdir(_self: Path):
        return iter([Path("dummy")])

    monkeypatch.setattr(Path, "exists", path_exists)
    monkeypatch.setattr(Path, "iterdir", path_iterdir)

    def fake_json_reader(_path: Path) -> dict[str, str]:
        return {"last_decision": "ok"}

    def fake_toml_reader(_path: Path) -> dict[str, str]:
        return {"status": "active"}

    monkeypatch.setattr(assistantia_core, "_read_json_file_sync", fake_json_reader)
    monkeypatch.setattr(assistantia_core, "_read_toml_file_sync", fake_toml_reader)
    monkeypatch.setattr(assistantia_core.assistantia_context_quality, "set", Mock())

    context, quality = await assistantia_core.get_arkalia_context()

    assert "ZeroIA: ok" in context
    assert "Reflexia: active" in context
    assert "Cognitive: active" in context
    assert quality > 0.0
    assert "fake_json_reader" in calls
    assert calls.count("fake_toml_reader") >= 2


from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from modules.core.storage import JSONFileBackend, SQLiteBackend, TOMLFileBackend


class _FakeAioReadFile:
    def __init__(self, content: str) -> None:
        self._content = content

    async def __aenter__(self) -> _FakeAioReadFile:
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False

    async def read(self) -> str:
        return self._content


class _FakeAioWriteFile:
    def __init__(self) -> None:
        self.written = ""

    async def __aenter__(self) -> _FakeAioWriteFile:
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False

    async def write(self, content: str) -> None:
        self.written = content


@pytest.mark.asyncio
async def test_json_get_async_falls_back_when_aiofiles_missing(tmp_path: Path) -> None:
    backend = JSONFileBackend(str(tmp_path))
    assert backend.set("sample", {"hello": "world"})

    import builtins

    real_import = builtins.__import__

    def _fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "aiofiles":
            raise ImportError("aiofiles missing")
        return real_import(name, *args, **kwargs)

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(builtins, "__import__", _fake_import)
    try:
        result = await backend.get_async("sample")
    finally:
        monkeypatch.undo()

    assert result == {"hello": "world"}


@pytest.mark.asyncio
async def test_json_async_paths_with_fake_aiofiles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backend = JSONFileBackend(str(tmp_path))

    fake_writer = _FakeAioWriteFile()

    class _FakeAioFilesModule:
        @staticmethod
        def open(path: Path, mode: str = "r", encoding: str = "utf-8") -> Any:
            if "w" in mode:
                return fake_writer
            return _FakeAioReadFile('{"ok": true}')

    import builtins

    real_import = builtins.__import__

    def _fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "aiofiles":
            return _FakeAioFilesModule()
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)

    assert await backend.set_async("async_key", {"ok": True}) is True
    assert backend._cache["async_key"] == {"ok": True}  # pyright: ignore[reportPrivateUsage]
    (tmp_path / "async_key.json").write_text('{"ok": true}', encoding="utf-8")
    read_value = await backend.get_async("async_key")
    assert read_value == {"ok": True}


def test_toml_backend_basic_operations(tmp_path: Path) -> None:
    backend = TOMLFileBackend(str(tmp_path))
    payload = {"feature": {"enabled": True}, "retries": 3}

    assert backend.set("cfg", payload) is True
    assert backend.get("cfg") == payload
    assert backend.exists("cfg") is True
    assert "cfg" in backend.list_keys()
    assert backend.delete("cfg") is True
    assert backend.get("cfg", default={}) == {}


def test_toml_backend_returns_default_on_read_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backend = TOMLFileBackend(str(tmp_path))
    backend.set("broken", {"a": 1})

    def _raise_read_error(_path: Path) -> dict[str, Any]:
        raise RuntimeError("read failed")

    monkeypatch.setattr("modules.core.storage.backends.read_state_safe", _raise_read_error)
    assert backend.get("broken", default={"fallback": True}) == {"fallback": True}


def test_sqlite_backend_handles_connection_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backend = SQLiteBackend(str(tmp_path / "state.db"))

    @contextmanager
    def _broken_connection() -> Any:
        raise RuntimeError("db down")

    monkeypatch.setattr(backend, "_get_connection", _broken_connection)

    assert backend.get("k", default=123) == 123
    assert backend.set("k", {"v": 1}) is False
    assert backend.delete("k") is False
    assert backend.exists("k") is False
    assert backend.list_keys() == []


def test_json_and_toml_list_keys_return_empty_on_error(tmp_path: Path) -> None:
    json_backend = JSONFileBackend(str(tmp_path / "json"))
    toml_backend = TOMLFileBackend(str(tmp_path / "toml"))

    def _broken_glob(_pattern: str) -> Any:
        raise OSError("boom")

    broken_path = SimpleNamespace(glob=_broken_glob)
    json_backend.base_path = broken_path  # type: ignore[assignment]
    toml_backend.base_path = broken_path  # type: ignore[assignment]

    assert json_backend.list_keys() == []
    assert toml_backend.list_keys() == []

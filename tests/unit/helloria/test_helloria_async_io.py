from collections.abc import Callable
from typing import Any
from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from httpx import ASGITransport, AsyncClient

from modules.helloria import core as helloria_core


@pytest.mark.asyncio
async def test_status_uses_to_thread_for_system_metrics(monkeypatch: MonkeyPatch) -> None:
    async def fake_to_thread(
        func: Callable[..., Any], *args: object, **kwargs: object
    ) -> tuple[float, Mock, Mock]:
        assert func is helloria_core._collect_system_metrics  # pyright: ignore[reportPrivateUsage]
        return (
            10.0,
            Mock(percent=20.0, used=2 * 1024**3, total=8 * 1024**3),
            Mock(percent=30.0, used=10 * 1024**3, total=100 * 1024**3),
        )

    monkeypatch.setattr(helloria_core.asyncio, "to_thread", fake_to_thread)

    transport = ASGITransport(app=helloria_core.app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/status")

    assert response.status_code == 200
    data = response.json()
    assert data["system"]["cpu_percent"] == 10.0


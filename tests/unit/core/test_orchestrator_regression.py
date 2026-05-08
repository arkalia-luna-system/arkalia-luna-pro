from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from modules.core.orchestrator.core_orchestrator import CoreOrchestrator


@pytest.mark.asyncio
async def test_initialize_sets_running_before_starting_monitoring_tasks(monkeypatch: MonkeyPatch):
    orchestrator = CoreOrchestrator()

    async def fake_initialize_modules():
        return None

    async def fake_start_monitoring_tasks():
        assert orchestrator.is_running is True
        return None

    monkeypatch.setattr(orchestrator, "_initialize_modules", fake_initialize_modules)
    monkeypatch.setattr(orchestrator, "_start_monitoring_tasks", fake_start_monitoring_tasks)

    initialized = await orchestrator.initialize()
    assert initialized is True


@pytest.mark.asyncio
async def test_execute_module_accepts_degraded_health_status():
    orchestrator = CoreOrchestrator()
    orchestrator.health_monitor = Mock()
    orchestrator.health_monitor.check_health.return_value = {"status": "degraded"}

    module_instance = Mock()
    module_instance.health_check.return_value = {"status": "ok"}
    wrapper = Mock()
    wrapper.instance = module_instance

    result = await orchestrator._execute_module("dummy", wrapper)  # pyright: ignore[reportPrivateUsage]

    assert result["status"] == "success"
    module_instance.health_check.assert_called_once()


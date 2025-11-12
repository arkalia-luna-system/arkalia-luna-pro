#!/usr/bin/env python3
# 🔒 tests/unit/security/test_security_core_enhanced.py
# Tests pour modules/security/core.py (imports corrigés)

import importlib.util
from pathlib import Path

import pytest

# Ajout dynamique du module security.core
core_path = Path(__file__).resolve().parents[3] / "modules" / "security" / "core.py"
spec = importlib.util.spec_from_file_location("security.core", str(core_path))
if spec is not None and spec.loader is not None:
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    UsecurityConfig = core.UsecurityConfig
    UsecurityCore = core.UsecurityCore
    default_config = core.default_config
    default_core = core.default_core
    main = core.main
else:
    raise ImportError(f"Impossible d'importer le module security.core depuis {core_path}")


def test_usecurity_config_default_values() -> None:
    config = UsecurityConfig()
    assert config.enabled is True
    assert config.debug_mode is False
    assert config.max_retries == 3
    assert config.timeout == 30.0


def test_usecurity_config_custom_values() -> None:
    config = UsecurityConfig(enabled=False, debug_mode=True, max_retries=5, timeout=60.0)
    assert config.enabled is False
    assert config.debug_mode is True
    assert config.max_retries == 5
    assert config.timeout == 60.0


def test_usecurity_core_initialization() -> None:
    config = UsecurityConfig()
    core = UsecurityCore(config)
    assert core.config is config
    assert hasattr(core, "logger")


def test_usecurity_core_health_check() -> None:
    config = UsecurityConfig()
    core = UsecurityCore(config)
    health = core.health_check()
    assert health["module"] == "security"
    assert health["status"] == "healthy"
    assert health["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_usecurity_core_process() -> None:
    config = UsecurityConfig()
    core = UsecurityCore(config)
    data = {"test": "data"}
    result = await core.process(data)
    assert result["status"] == "success"
    assert result["data"] == data
    assert result["module"] == "security"


def test_default_config_and_core() -> None:
    assert isinstance(default_config, UsecurityConfig)
    assert isinstance(default_core, UsecurityCore)


@pytest.mark.asyncio
async def test_main_function(monkeypatch: pytest.MonkeyPatch) -> None:
    # On vérifie que main() s'exécute sans erreur
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    await main()

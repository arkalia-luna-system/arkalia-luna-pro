from pathlib import Path

from modules.core.config.config_manager import ConfigManager, get_default_config_manager


def test_default_config_manager_uses_fallback_when_file_missing(tmp_path: Path) -> None:
    """Le ConfigManager doit charger une config par défaut si le fichier n'existe pas."""
    missing_path = tmp_path / "does_not_exist.json"
    manager = ConfigManager(config_path=str(missing_path))

    core_cfg = manager.get_config("core")
    modules_cfg = manager.get_config("modules")
    watchdogs_cfg = manager.get_config("watchdogs")

    assert core_cfg.get("log_level") == "INFO"
    assert "zeroia" in modules_cfg
    assert "sandozia" in modules_cfg
    assert "reflexia" in modules_cfg
    assert "assistantia" in modules_cfg
    assert "reflexia_panic" in watchdogs_cfg


def test_get_default_config_manager_returns_singleton() -> None:
    """get_default_config_manager doit retourner toujours la même instance."""
    m1 = get_default_config_manager()
    m2 = get_default_config_manager()

    assert m1 is m2
    assert m1.health_check()["module"] == "config_manager"


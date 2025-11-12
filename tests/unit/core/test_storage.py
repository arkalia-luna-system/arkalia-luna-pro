"""Tests pour le module de stockage"""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from modules.core.storage import (
    JSONFileBackend,
    SQLiteBackend,
    StorageManager,
    get_storage,
    set_storage_backend,
)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Fixture pour créer un répertoire temporaire"""
    with tempfile.TemporaryDirectory() as temp:
        yield Path(temp)


@pytest.fixture
def json_backend(temp_dir: Path) -> JSONFileBackend:
    """Fixture pour créer un backend JSON"""
    return JSONFileBackend(str(temp_dir))


@pytest.fixture
def sqlite_backend(temp_dir: Path) -> SQLiteBackend:
    """Fixture pour créer un backend SQLite"""
    return SQLiteBackend(str(temp_dir / "test.db"))


def test_json_backend_basic_operations(json_backend: JSONFileBackend) -> None:
    """Test des opérations de base du backend JSON"""
    # Test set et get
    assert json_backend.set("test_key", {"value": 42})
    assert json_backend.get("test_key") == {"value": 42}

    # Test exists
    assert json_backend.exists("test_key")
    assert not json_backend.exists("nonexistent")

    # Test delete
    assert json_backend.delete("test_key")
    assert not json_backend.exists("test_key")
    assert json_backend.get("test_key") is None


def test_json_backend_list_keys(json_backend: JSONFileBackend) -> None:
    """Test du listage des clés du backend JSON"""
    # Créer quelques fichiers de test
    json_backend.set("test1", "value1")
    json_backend.set("test2", "value2")
    json_backend.set("other", "value3")

    # Test list_keys sans préfixe
    keys = json_backend.list_keys()
    assert len(keys) == 3
    assert "test1" in keys
    assert "test2" in keys
    assert "other" in keys

    # Test list_keys avec préfixe
    test_keys = json_backend.list_keys("test")
    assert len(test_keys) == 2
    assert "test1" in test_keys
    assert "test2" in test_keys


def test_sqlite_backend_basic_operations(sqlite_backend: SQLiteBackend) -> None:
    """Test des opérations de base du backend SQLite"""
    # Test set et get
    assert sqlite_backend.set("test_key", {"value": 42})
    assert sqlite_backend.get("test_key") == {"value": 42}

    # Test exists
    assert sqlite_backend.exists("test_key")
    assert not sqlite_backend.exists("nonexistent")

    # Test delete
    assert sqlite_backend.delete("test_key")
    assert not sqlite_backend.exists("test_key")
    assert sqlite_backend.get("test_key") is None


def test_storage_manager_module_operations(temp_dir: Path) -> None:
    """Test des opérations sur les modules du StorageManager"""
    manager = StorageManager(backend="json", base_path=str(temp_dir))

    # Test state
    assert manager.save_state("test_module", {"status": "active"})
    assert manager.get_state("test_module") == {"status": "active"}

    # Test config
    config = {"param1": "value1", "param2": 42}
    assert manager.save_config("test_module", config)
    assert manager.get_config("test_module") == config

    # Test metrics
    metrics = {"cpu": 45.2, "memory": 1024}
    assert manager.save_metrics("test_module", metrics)
    assert manager.get_metrics("test_module") == metrics

    # Test decision
    decision = {"action": "continue", "confidence": 0.95}
    assert manager.save_decision("test_module", "decision1", decision)
    assert manager.get_decision("test_module", "decision1") == decision


def test_storage_manager_backup_restore(temp_dir: Path) -> None:
    """Test des opérations de backup/restore du StorageManager"""
    manager = StorageManager(backend="json", base_path=str(temp_dir))

    # Créer des données de test
    manager.save_state("test_module", {"status": "active"})
    manager.save_config("test_module", {"param": "value"})
    manager.save_metrics("test_module", {"cpu": 45.2})

    # Créer un backup
    backup_path = str(temp_dir / "backup")
    assert manager.backup_module("test_module", backup_path)

    # Supprimer les données
    assert manager.delete_module_data("test_module")
    assert not manager.get_state("test_module")

    # Restaurer depuis le backup
    assert manager.restore_module("test_module", backup_path)
    assert manager.get_state("test_module") == {"status": "active"}
    assert manager.get_config("test_module") == {"param": "value"}
    assert manager.get_metrics("test_module") == {"cpu": 45.2}


def test_storage_singleton() -> None:
    """Test du singleton de stockage"""
    # Test get_storage par défaut
    storage1 = get_storage()
    storage2 = get_storage()
    assert storage1 is storage2

    # Test set_storage_backend
    set_storage_backend("sqlite", db_path=":memory:")
    storage3 = get_storage()
    assert storage3.get_state("test") is None  # Vérifie que c'est un nouveau backend SQLite
    assert storage3 is not storage1

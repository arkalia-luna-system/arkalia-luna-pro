"""
Storage Manager - Gestionnaire centralisé de stockage
"""

import json
from pathlib import Path
from typing import Any

from core.ark_logger import ark_logger
from modules.utils.helpers.io_safe import read_state_safe

from .backends import JSONFileBackend, SQLiteBackend, StorageBackend, TOMLFileBackend


class StorageManager:
    """Centralized storage manager for Arkalia-LUNA"""

    def __init__(self, backend: str = "json", **kwargs: Any):
        self.backend_type = backend
        if backend == "sqlite":
            self.backend: StorageBackend = SQLiteBackend(**kwargs)
        elif backend == "toml":
            self.backend = TOMLFileBackend(**kwargs)
        else:
            self.backend = JSONFileBackend(**kwargs)

        ark_logger.info(
            f"StorageManager initialisé avec backend: {backend}", extra={"arkalia_module": "core"}
        )

    def get_state(self, module: str, key: str = "state", default: Any = None) -> Any:
        """Get module state"""
        storage_key = f"{module}.{key}"
        return self.backend.get(storage_key, default)

    def save_state(self, module: str, data: Any, key: str = "state") -> bool:
        """Save module state"""
        storage_key = f"{module}.{key}"
        return self.backend.set(storage_key, data)

    def get_decision(self, module: str, decision_id: str) -> Any:
        """Get decision by ID"""
        storage_key = f"{module}.decisions.{decision_id}"
        return self.backend.get(storage_key)

    def save_decision(self, module: str, decision_id: str, data: Any) -> bool:
        """Save decision by ID"""
        storage_key = f"{module}.decisions.{decision_id}"
        return self.backend.set(storage_key, data)

    def get_config(self, module: str) -> dict[str, Any]:
        """Get module configuration"""
        result = self.backend.get(f"{module}.config", {})
        return result if isinstance(result, dict) else {}

    def save_config(self, module: str, config: dict[str, Any]) -> bool:
        """Save module configuration"""
        return self.backend.set(f"{module}.config", config)

    def get_metrics(self, module: str) -> dict[str, Any]:
        """Get module metrics"""
        result = self.backend.get(f"{module}.metrics", {})
        return result if isinstance(result, dict) else {}

    def save_metrics(self, module: str, metrics: dict[str, Any]) -> bool:
        """Save module metrics"""
        return self.backend.set(f"{module}.metrics", metrics)

    def list_module_data(self, module: str) -> list[str]:
        """List all data keys for a module"""
        prefix = f"{module}."
        return self.backend.list_keys(prefix)

    def delete_module_data(self, module: str) -> bool:
        """Delete all data for a module"""
        try:
            keys = self.list_module_data(module)
            for key in keys:
                self.backend.delete(key)
            return True
        except Exception as e:
            ark_logger.error(
                f"Erreur suppression données module {module}: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def backup_module(self, module: str, backup_path: str) -> bool:
        """Backup all module data"""
        try:
            data = {}
            keys = self.list_module_data(module)
            for key in keys:
                data[key] = self.backend.get(key)

            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            ark_logger.info(
                f"Backup module {module} créé: {backup_path}", extra={"arkalia_module": "core"}
            )
            return True
        except Exception as e:
            ark_logger.error(
                f"Erreur backup module {module}: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def restore_module(self, module: str, backup_path: str) -> bool:
        """Restore module data from backup"""
        try:
            backup_file = Path(backup_path)
            if backup_file.suffix == ".toml":
                data = read_state_safe(backup_file)
            else:
                with open(backup_file, encoding="utf-8") as f:
                    data = json.load(f)

            for key, value in data.items():
                self.backend.set(key, value)

            ark_logger.info(
                f"Module {module} restauré depuis: {backup_path}", extra={"arkalia_module": "core"}
            )
            return True
        except Exception as e:
            ark_logger.error(
                f"Erreur restauration module {module}: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def get_helloria_state(self) -> dict[str, Any]:
        """Get Helloria state (compatibilité avec HelloriaStateManager)"""
        result = self.get_state("helloria", "state", {"status": "inactive"})
        return result if isinstance(result, dict) else {"status": "inactive"}

    def save_helloria_state(self, state: dict[str, Any]) -> bool:
        """Save Helloria state (compatibilité avec HelloriaStateManager)"""
        return self.save_state("helloria", state, "state")


# Global storage instance (lazy loading pour économiser la RAM)
_storage: StorageManager | None = None


def get_storage() -> StorageManager:
    """Récupère l'instance globale du StorageManager (lazy loading)"""
    global _storage
    if _storage is None:
        _storage = StorageManager()
    return _storage


# Alias pour compatibilité (lazy)
class _LazyStorage:
    """Wrapper lazy pour storage"""

    def __getattr__(self, name: str) -> Any:
        return getattr(get_storage(), name)


storage = _LazyStorage()


def set_storage_backend(backend: str, **kwargs: Any) -> None:
    """Set storage backend globally"""
    global _storage, storage
    _storage = None  # Réinitialiser pour forcer la création d'une nouvelle instance
    _storage = StorageManager(backend, **kwargs)
    storage = _LazyStorage()  # Recréer le wrapper lazy


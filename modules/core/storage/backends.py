"""
Storage Backends - Implémentations concrètes des backends de stockage
"""

import json
import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from core.ark_logger import ark_logger
from modules.utils.helpers.io_safe import read_state_safe, save_toml_safe


class StorageBackend(ABC):
    """Abstract storage backend interface"""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> bool:
        """Set value by key"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value by key"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass

    @abstractmethod
    def list_keys(self, prefix: str = "") -> list[str]:
        """List all keys with optional prefix"""
        pass


class JSONFileBackend(StorageBackend):
    """JSON file-based storage backend"""

    def __init__(self, base_path: str = "state"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self._cache: dict[str, Any] = {}

    def _get_file_path(self, key: str) -> Path:
        """Get file path for key"""
        return self.base_path / f"{key}.json"

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from JSON file"""
        try:
            file_path = self._get_file_path(key)
            if not file_path.exists():
                return default

            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                self._cache[key] = data
                return data
        except Exception as e:
            ark_logger.error(f"Erreur lecture {key}: {e}", extra={"arkalia_module": "core"})
            return default

    def set(self, key: str, value: Any) -> bool:
        """Set value to JSON file"""
        try:
            file_path = self._get_file_path(key)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(value, f, indent=2, ensure_ascii=False, default=str)

            self._cache[key] = value
            return True
        except Exception as e:
            ark_logger.error(f"Erreur écriture {key}: {e}", extra={"arkalia_module": "core"})
            return False

    def delete(self, key: str) -> bool:
        """Delete JSON file"""
        try:
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
                self._cache.pop(key, None)
                return True
            return False
        except Exception as e:
            ark_logger.error(f"Erreur suppression {key}: {e}", extra={"arkalia_module": "core"})
            return False

    def exists(self, key: str) -> bool:
        """Check if JSON file exists"""
        return self._get_file_path(key).exists()

    def list_keys(self, prefix: str = "") -> list[str]:
        """List all JSON files with prefix"""
        try:
            pattern = f"{prefix}*.json" if prefix else "*.json"
            files = list(self.base_path.glob(pattern))
            return [f.stem for f in files]
        except Exception as e:
            ark_logger.error(f"Erreur listage clés: {e}", extra={"arkalia_module": "core"})
            return []


class TOMLFileBackend(StorageBackend):
    """TOML file-based storage backend"""

    def __init__(self, base_path: str = "state"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self._cache: dict[str, Any] = {}

    def _get_file_path(self, key: str) -> Path:
        """Get file path for key"""
        return self.base_path / f"{key}.toml"

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from TOML file"""
        try:
            file_path = self._get_file_path(key)
            if not file_path.exists():
                return default

            data = read_state_safe(file_path)
            if data:
                self._cache[key] = data
                return data
            return default
        except Exception as e:
            ark_logger.error(f"Erreur lecture TOML {key}: {e}", extra={"arkalia_module": "core"})
            return default

    def set(self, key: str, value: Any) -> bool:
        """Set value to TOML file"""
        try:
            file_path = self._get_file_path(key)
            save_toml_safe(value, file_path)
            self._cache[key] = value
            return True
        except Exception as e:
            ark_logger.error(f"Erreur écriture TOML {key}: {e}", extra={"arkalia_module": "core"})
            return False

    def delete(self, key: str) -> bool:
        """Delete TOML file"""
        try:
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
                self._cache.pop(key, None)
                return True
            return False
        except Exception as e:
            ark_logger.error(
                f"Erreur suppression TOML {key}: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def exists(self, key: str) -> bool:
        """Check if TOML file exists"""
        return self._get_file_path(key).exists()

    def list_keys(self, prefix: str = "") -> list[str]:
        """List all TOML files with prefix"""
        try:
            pattern = f"{prefix}*.toml" if prefix else "*.toml"
            files = list(self.base_path.glob(pattern))
            return [f.stem for f in files]
        except Exception as e:
            ark_logger.error(f"Erreur listage clés TOML: {e}", extra={"arkalia_module": "core"})
            return []


class SQLiteBackend(StorageBackend):
    """SQLite-based storage backend"""

    def __init__(self, db_path: str = "state/arkalia.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database"""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS storage (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()

    @contextmanager
    def _get_connection(self) -> Any:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from SQLite"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT value FROM storage WHERE key = ?", (key,))
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return default
        except Exception as e:
            ark_logger.error(f"Erreur lecture SQLite {key}: {e}", extra={"arkalia_module": "core"})
            return default

    def set(self, key: str, value: Any) -> bool:
        """Set value to SQLite"""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO storage (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                    (key, json.dumps(value, default=str)),
                )
                conn.commit()
                return True
        except Exception as e:
            ark_logger.error(f"Erreur écriture SQLite {key}: {e}", extra={"arkalia_module": "core"})
            return False

    def delete(self, key: str) -> bool:
        """Delete value from SQLite"""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM storage WHERE key = ?", (key,))
                conn.commit()
                return True
        except Exception as e:
            ark_logger.error(
                f"Erreur suppression SQLite {key}: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in SQLite"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT 1 FROM storage WHERE key = ?", (key,))
                return cursor.fetchone() is not None
        except Exception as e:
            ark_logger.error(
                f"Erreur vérification SQLite {key}: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def list_keys(self, prefix: str = "") -> list[str]:
        """List all keys with prefix"""
        try:
            with self._get_connection() as conn:
                if prefix:
                    cursor = conn.execute(
                        "SELECT key FROM storage WHERE key LIKE ?", (f"{prefix}%",)
                    )
                else:
                    cursor = conn.execute("SELECT key FROM storage")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            ark_logger.error(f"Erreur listage SQLite: {e}", extra={"arkalia_module": "core"})
            return []


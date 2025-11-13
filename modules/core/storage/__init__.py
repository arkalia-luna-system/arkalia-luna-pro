"""
Storage Abstraction Layer for Arkalia-LUNA Pro
Provides unified storage interface for all modules

Refactorisé en sous-modules pour améliorer la maintenabilité :
- backends.py : Implémentations des backends (JSON, TOML, SQLite)
- manager.py : StorageManager et fonctions globales
"""

from .backends import JSONFileBackend, SQLiteBackend, StorageBackend, TOMLFileBackend
from .manager import StorageManager, get_storage, set_storage_backend, storage

__all__ = [
    "StorageBackend",
    "JSONFileBackend",
    "TOMLFileBackend",
    "SQLiteBackend",
    "StorageManager",
    "get_storage",
    "set_storage_backend",
    "storage",
]


"""
Storage Abstraction Layer for Arkalia-LUNA Pro
Provides unified storage interface for all modules

⚠️ FICHIER DE COMPATIBILITÉ - Ce fichier réexporte depuis modules/core/storage/
Pour de nouveaux imports, utilisez directement : from modules.core.storage import ...
"""

# Réexport pour compatibilité avec les imports existants
from modules.core.storage import (
    JSONFileBackend,
    SQLiteBackend,
    StorageBackend,
    StorageManager,
    TOMLFileBackend,
    get_storage,
    set_storage_backend,
    storage,
)

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

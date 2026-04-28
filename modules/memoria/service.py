"""
Service de mémoire vectorielle pour Arkalia-LUNA.

Ce module fournit une API simple pour ajouter et rechercher des souvenirs
vectoriels persistés dans une base SQLite locale.
"""

from __future__ import annotations

import json
import math
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from core.ark_logger import ark_logger

from .embedding import deserialize_embedding, get_embedding, serialize_embedding


@dataclass
class MemoryRecord:
    id: int
    user_id: str
    memory_type: str
    title: str | None
    content: str
    created_at: datetime
    metadata: dict[str, Any]
    score: float | None = None


class VectorMemoryService:
    """
    Service de mémoire vectorielle basé sur SQLite.

    Schéma:
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL,
            metadata_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    def __init__(self, db_path: str = "state/memoria.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connection_ctx(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connection_ctx() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    metadata_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_user_type "
                "ON memories (user_id, memory_type, created_at DESC)"
            )
            conn.commit()

        ark_logger.info(
            f"VectorMemoryService initialisé sur {self.db_path}",
            extra={"arkalia_module": "memoria"},
        )

    def add_memory(
        self,
        user_id: str,
        memory_type: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        title: str | None = None,
    ) -> int:
        """
        Ajoute un souvenir vectoriel dans la base.

        Le contenu est encodé en vecteur via `get_embedding`, puis sérialisé
        en JSON avant d'être persisté dans la base SQLite.

        Args:
            user_id: Identifiant logique de l'utilisateur ou de la session.
            memory_type: Type fonctionnel du souvenir (project_idea, decision, etc.).
            content: Texte brut à encoder et stocker.
            metadata: Métadonnées JSON sérialisables associées au souvenir.
            title: Titre optionnel pour faciliter le debug ou l'affichage.

        Returns:
            Identifiant auto-incrémenté du souvenir inséré, ou -1 en cas d'erreur.
        """
        try:
            embedding_vec = get_embedding(content)
            embedding_raw = serialize_embedding(embedding_vec)
            metadata_json = json.dumps(metadata or {}, ensure_ascii=False)

            with self._connection_ctx() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO memories (
                        user_id,
                        memory_type,
                        title,
                        content,
                        embedding,
                        metadata_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, memory_type, title, content, embedding_raw, metadata_json),
                )
                conn.commit()
                last_id = cursor.lastrowid or 0
                return int(last_id)
        except Exception as exc:
            ark_logger.error(
                f"Erreur add_memory: {exc}", extra={"arkalia_module": "memoria"}
            )
            return -1

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calcule la similarité cosinus entre deux vecteurs numériques."""
        if not a or not b or len(a) != len(b):
            return 0.0
        num = sum(x * y for x, y in zip(a, b, strict=False))
        if num == 0.0:
            return 0.0
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        if na == 0.0 or nb == 0.0:
            return 0.0
        return num / (na * nb)

    def search_memory(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
        memory_type: str | None = None,
    ) -> list[MemoryRecord]:
        """
        Recherche les souvenirs les plus pertinents pour une requête.

        La fonction sélectionne d'abord un sous-ensemble récent de souvenirs
        pour l'utilisateur donné, calcule la similarité cosinus avec la
        requête et retourne les `top_k` résultats les mieux scorés.

        Args:
            user_id: Identifiant logique de l'utilisateur ou de la session.
            query: Texte décrivant ce que l'on cherche dans la mémoire.
            top_k: Nombre maximum de souvenirs à retourner (triés par score).
            memory_type: Filtre facultatif sur le type de souvenir.

        Returns:
            Liste triée de `MemoryRecord` avec un score de similarité rempli.
        """
        if not query.strip():
            return []

        try:
            query_vec = get_embedding(query)

            with self._connection_ctx() as conn:
                params: list[Any] = [user_id]
                # On conserve une requête statique et paramétrée pour éviter
                # toute interpolation dynamique dans le SQL.
                sql = (
                    "SELECT id, user_id, memory_type, title, content, embedding, "
                    "metadata_json, created_at "
                    "FROM memories "
                    "WHERE user_id = ? "
                )
                if memory_type:
                    sql += "AND memory_type = ? "
                    params.append(memory_type)
                sql += "ORDER BY created_at DESC LIMIT 200"

                cursor = conn.execute(sql, tuple(params))
                rows = cursor.fetchall()

            import json

            candidates: list[MemoryRecord] = []
            for row in rows:
                emb = deserialize_embedding(row[5])
                score = self._cosine_similarity(query_vec, emb)
                try:
                    raw_metadata = row[6]
                    metadata: dict[str, Any] = {}
                    if raw_metadata:
                        loaded: Any = json.loads(raw_metadata)
                        if isinstance(loaded, dict):
                            metadata = {
                                str(k): v for (k, v) in loaded.items()  # type: ignore[misc]
                            }
                except Exception:
                    metadata = {}

                rec = MemoryRecord(
                    id=int(row[0]),
                    user_id=str(row[1]),
                    memory_type=str(row[2]),
                    title=row[3],
                    content=str(row[4]),
                    created_at=datetime.fromisoformat(row[7])
                    if isinstance(row[7], str)
                    else datetime.now(),
                    metadata=metadata,
                    score=score,
                )
                candidates.append(rec)

            # Tri par score décroissant et limitation top_k
            candidates.sort(key=lambda r: (r.score or 0.0), reverse=True)
            return candidates[:top_k]
        except Exception as exc:
            ark_logger.error(
                f"Erreur search_memory: {exc}", extra={"arkalia_module": "memoria"}
            )
            return []

    def purge_user_memories(self, user_id: str) -> int:
        """
        Supprime toutes les mémoires pour un utilisateur donné.
        """
        try:
            with self._connection_ctx() as conn:
                cursor = conn.execute(
                    "DELETE FROM memories WHERE user_id = ?", (user_id,)
                )
                conn.commit()
                return int(cursor.rowcount or 0)
        except Exception as exc:
            ark_logger.error(
                f"Erreur purge_user_memories: {exc}",
                extra={"arkalia_module": "memoria"},
            )
            return 0

    def add_project_memory(
        self,
        user_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        title: str | None = None,
    ) -> int:
        """
        Ajoute un souvenir de type `project_idea`.
        """
        meta = dict(metadata or {})
        meta.setdefault("kind", "project_idea")
        return self.add_memory(
            user_id=user_id,
            memory_type="project_idea",
            content=content,
            metadata=meta,
            title=title,
        )

    def add_decision_memory(
        self,
        user_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        title: str | None = None,
    ) -> int:
        """
        Ajoute un souvenir de type `decision`.
        """
        meta = dict(metadata or {})
        meta.setdefault("kind", "decision")
        return self.add_memory(
            user_id=user_id,
            memory_type="decision",
            content=content,
            metadata=meta,
            title=title,
        )


_vector_memory_service: VectorMemoryService | None = None


def get_vector_memory_service() -> VectorMemoryService:
    """
    Retourne l'instance globale du service de mémoire vectorielle.
    """
    global _vector_memory_service
    if _vector_memory_service is None:
        _vector_memory_service = VectorMemoryService()
    return _vector_memory_service


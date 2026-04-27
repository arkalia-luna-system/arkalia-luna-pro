from pathlib import Path

import pytest

import modules.memoria.service as memoria_service_module
from modules.memoria import VectorMemoryService
from modules.memoria.service import get_vector_memory_service


def _make_tmp_db(tmp_name: str = "test_memoria.db") -> str:
    base = Path("state") / "tests"
    base.mkdir(parents=True, exist_ok=True)
    return str(base / tmp_name)


def test_add_and_search_memory_roundtrip() -> None:
    """Vérifie qu'un souvenir ajouté peut être retrouvé avec une requête proche."""
    db_path = _make_tmp_db()
    service = VectorMemoryService(db_path=db_path)

    user_id = "test-user"
    content = "Idée de projet Arkalia LUNA"

    mem_id = service.add_memory(
        user_id=user_id,
        memory_type="project_idea",
        content=content,
        metadata={"source": "unit-test"},
        title="Projet Arkalia",
    )

    assert mem_id > 0

    results = service.search_memory(user_id=user_id, query="projet arkalia", top_k=3)
    assert results, "Aucun résultat retourné pour une requête pourtant proche."
    assert any(r.id == mem_id for r in results)


def test_search_memory_empty_query_returns_empty_list() -> None:
    """Une requête vide ne doit jamais déclencher un appel à la base."""
    db_path = _make_tmp_db("test_memoria_empty_query.db")
    service = VectorMemoryService(db_path=db_path)

    results = service.search_memory(user_id="u", query="   ")
    assert results == []


def test_purge_user_memories_deletes_records() -> None:
    """Vérifie que les souvenirs d'un utilisateur peuvent être purgés."""
    db_path = _make_tmp_db("test_memoria_purge.db")
    service = VectorMemoryService(db_path=db_path)

    user_id = "to-purge"
    for i in range(3):
        assert (
            service.add_memory(
                user_id=user_id,
                memory_type="note",
                content=f"Note {i}",
                metadata=None,
            )
            > 0
        )

    deleted = service.purge_user_memories(user_id)
    assert deleted >= 3

    remaining = service.search_memory(user_id=user_id, query="Note", top_k=5)
    assert remaining == []


def test_search_memory_filters_by_memory_type_and_limits_top_k() -> None:
    db_path = _make_tmp_db("test_memoria_filter.db")
    service = VectorMemoryService(db_path=db_path)

    user_id = "filter-user"
    service.add_project_memory(user_id=user_id, content="Projet A", title="A")
    service.add_decision_memory(user_id=user_id, content="Decision B", title="B")
    service.add_project_memory(user_id=user_id, content="Projet C", title="C")

    results = service.search_memory(
        user_id=user_id,
        query="projet",
        memory_type="project_idea",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].memory_type == "project_idea"


def test_search_memory_handles_invalid_json_metadata() -> None:
    db_path = _make_tmp_db("test_memoria_invalid_metadata.db")
    service = VectorMemoryService(db_path=db_path)

    memory_id = service.add_memory(
        user_id="json-user",
        memory_type="note",
        content="Texte avec metadata corrompue",
    )
    assert memory_id > 0

    with service._connection_ctx() as conn:  # pyright: ignore[reportPrivateUsage]
        conn.execute("UPDATE memories SET metadata_json = ? WHERE id = ?", ("{broken", memory_id))
        conn.commit()

    results = service.search_memory(user_id="json-user", query="Texte")
    assert results
    assert results[0].metadata == {}


def test_add_memory_returns_minus_one_on_embedding_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = _make_tmp_db("test_memoria_add_error.db")
    service = VectorMemoryService(db_path=db_path)

    def _explode_embedding(_content: str) -> list[float]:
        raise RuntimeError("embedding unavailable")

    monkeypatch.setattr(memoria_service_module, "get_embedding", _explode_embedding)
    created_id = service.add_memory(
        user_id="err-user",
        memory_type="note",
        content="will fail",
    )
    assert created_id == -1


def test_search_memory_returns_empty_list_on_embedding_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = _make_tmp_db("test_memoria_search_error.db")
    service = VectorMemoryService(db_path=db_path)
    assert service.add_memory("s-user", "note", "bonjour") > 0

    def _explode_embedding(_query: str) -> list[float]:
        raise RuntimeError("query embedding failed")

    monkeypatch.setattr(memoria_service_module, "get_embedding", _explode_embedding)
    assert service.search_memory(user_id="s-user", query="bonjour") == []


def test_search_memory_handles_mismatched_vector_size(monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = _make_tmp_db("test_memoria_mismatch.db")
    service = VectorMemoryService(db_path=db_path)
    assert service.add_memory("u-mismatch", "note", "stored vector") > 0

    def _short_embedding(_q: str) -> list[float]:
        return [1.0, 2.0]

    monkeypatch.setattr(memoria_service_module, "get_embedding", _short_embedding)
    results = service.search_memory(user_id="u-mismatch", query="q")
    assert results
    assert results[0].score == 0.0


def test_search_memory_handles_zero_norm_and_zero_dot(monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = _make_tmp_db("test_memoria_zero_norm.db")
    service = VectorMemoryService(db_path=db_path)

    def _stored_embedding(_c: str) -> list[float]:
        return [0.0, 1.0]

    def _orthogonal_query(_q: str) -> list[float]:
        return [1.0, 0.0]

    def _zero_norm_query(_q: str) -> list[float]:
        return [0.0, 0.0]

    monkeypatch.setattr(memoria_service_module, "get_embedding", _stored_embedding)
    assert service.add_memory("u-zero", "note", "orthogonal") > 0
    monkeypatch.setattr(memoria_service_module, "get_embedding", _orthogonal_query)
    orthogonal = service.search_memory(user_id="u-zero", query="query")
    assert orthogonal and orthogonal[0].score == 0.0

    monkeypatch.setattr(memoria_service_module, "get_embedding", _zero_norm_query)
    zero_norm = service.search_memory(user_id="u-zero", query="query")
    assert zero_norm and zero_norm[0].score == 0.0


def test_purge_user_memories_returns_zero_on_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = _make_tmp_db("test_memoria_purge_error.db")
    service = VectorMemoryService(db_path=db_path)

    def _broken_connection_ctx():
        raise RuntimeError("db unavailable")
        yield

    monkeypatch.setattr(service, "_connection_ctx", _broken_connection_ctx)
    assert service.purge_user_memories("whoever") == 0


def test_get_vector_memory_service_returns_singleton() -> None:
    first = get_vector_memory_service()
    second = get_vector_memory_service()
    assert first is second


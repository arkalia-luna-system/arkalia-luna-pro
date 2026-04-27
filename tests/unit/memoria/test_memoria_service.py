from pathlib import Path

from modules.memoria import VectorMemoryService


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


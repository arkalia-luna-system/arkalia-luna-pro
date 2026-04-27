import math

import pytest

from modules.memoria import embedding


def test_get_embedding_without_model_uses_deterministic_fallback() -> None:
    vec = embedding.get_embedding("arkalia luna orchestrator")
    norm = math.sqrt(sum(v * v for v in vec))
    assert abs(norm - 1.0) < 1e-6
    assert len(vec) == 128


def test_get_embedding_returns_zeros_for_blank_input() -> None:
    assert embedding.get_embedding("   ") == [0.0] * 128


def test_get_embedding_uses_remote_when_model_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    monkeypatch.setenv("OLLAMA_HOST", "127.0.0.1")
    monkeypatch.setenv("OLLAMA_PORT", "11434")

    class _Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, list[float]]:
            return {"embedding": [1, 2.5, 3]}

    def _fake_post(url: str, json: dict[str, str], timeout: int) -> _Response:
        assert url == "http://127.0.0.1:11434/api/embeddings"
        assert json == {"model": "nomic-embed-text", "prompt": "hello"}
        assert timeout == 15
        return _Response()

    monkeypatch.setattr(embedding.requests, "post", _fake_post)
    assert embedding.get_embedding("hello") == [1.0, 2.5, 3.0]


def test_get_embedding_falls_back_when_remote_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    def _raise_error(*args: object, **kwargs: object) -> None:
        raise RuntimeError("network down")

    monkeypatch.setattr(embedding.requests, "post", _raise_error)

    vec = embedding.get_embedding("fallback test")
    assert len(vec) == 128
    assert any(v != 0.0 for v in vec)


def test_serialize_and_deserialize_embedding_roundtrip() -> None:
    raw = embedding.serialize_embedding([0.1, 0.2, 0.3])
    vec = embedding.deserialize_embedding(raw)
    assert vec == [0.1, 0.2, 0.3]


def test_deserialize_embedding_invalid_or_none_returns_empty_list() -> None:
    assert embedding.deserialize_embedding(None) == []
    assert embedding.deserialize_embedding(b"not-json") == []

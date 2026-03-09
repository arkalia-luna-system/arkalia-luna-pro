"""
Backend d'embeddings pour la mémoire vectorielle locale.

Stratégie :
- Tente d'utiliser l'API d'embeddings d'Ollama (si disponible).
- En cas d'échec (modèle absent, Ollama indisponible, etc.), bascule sur
  un encodage de secours léger pure-Python basé sur un hashing de tokens.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Iterable, List

import requests


def _get_ollama_base_url() -> str:
    host = os.getenv("OLLAMA_HOST", "host.docker.internal")
    port = os.getenv("OLLAMA_PORT", "11434")
    return f"http://{host}:{port}"


def _hash_fallback_embedding(text: str, dim: int = 128) -> list[float]:
    """
    Encodage de secours simple mais déterministe.

    On projette les tokens dans un espace de dimension fixe via SHA256
    puis on normalise.
    """
    if not text:
        return [0.0] * dim

    vec = [0.0] * dim
    tokens = text.lower().split()

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        # Utiliser les premiers octets pour répartir le token dans le vecteur
        for i in range(0, len(digest), 2):
            idx = digest[i] % dim
            vec[idx] += 1.0

    # Normalisation L2 simple
    norm = sum(v * v for v in vec) ** 0.5
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


def get_embedding(text: str) -> list[float]:
    """
    Retourne un embedding pour le texte donné.

    Essaie d'abord l'API d'embeddings d'Ollama avec le modèle défini par
    la variable d'environnement OLLAMA_EMBEDDING_MODEL. En cas d'erreur,
    utilise un fallback hashing.
    """
    text = text.strip()
    if not text:
        return [0.0] * 128

    model = os.getenv("OLLAMA_EMBEDDING_MODEL")
    if model:
        try:
            url = f"{_get_ollama_base_url()}/api/embeddings"
            payload = {"model": model, "prompt": text}
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Format attendu par Ollama: {"embedding": [floats...] }
            embedding = data.get("embedding")
            if isinstance(embedding, list) and embedding:
                # S'assurer qu'on renvoie des floats
                return [float(x) for x in embedding]
        except Exception:
            # On tombe sur le fallback silencieusement
            pass

    return _hash_fallback_embedding(text)


def serialize_embedding(vec: Iterable[float]) -> str:
    """Sérialise un vecteur en JSON pour stockage SQLite."""
    return json.dumps(list(vec))


def deserialize_embedding(raw: str | bytes | None) -> list[float]:
    """Désérialise un vecteur JSON depuis SQLite."""
    if raw is None:
        return []
    try:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            return [float(x) for x in data]
        return []
    except Exception:
        return []


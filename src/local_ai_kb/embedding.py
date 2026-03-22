from __future__ import annotations

from typing import Sequence

import requests

from local_ai_kb.config import OLLAMA_MODEL, OLLAMA_URL


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    response = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": OLLAMA_MODEL, "input": list(texts)},
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    embeddings = payload.get("embeddings", [])
    if len(embeddings) != len(texts):
        raise ValueError("Unexpected embedding count returned by Ollama")
    return embeddings

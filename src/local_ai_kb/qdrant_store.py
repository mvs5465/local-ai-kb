from __future__ import annotations

from typing import Iterable

from qdrant_client import QdrantClient
from qdrant_client.http import models

from local_ai_kb.config import QDRANT_COLLECTION, QDRANT_URL
from local_ai_kb.retrieval import RankedResult, rerank_results


def get_client() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL)


def ensure_collection(vector_size: int) -> None:
    client = get_client()
    collections = {item.name for item in client.get_collections().collections}
    if QDRANT_COLLECTION in collections:
        return
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE,
        ),
    )


def replace_points(points: Iterable[models.PointStruct]) -> None:
    client = get_client()
    client.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=models.FilterSelector(
            filter=models.Filter(must=[]),
        ),
    )
    client.upsert(collection_name=QDRANT_COLLECTION, points=list(points))


def search(
    query: str,
    embedding: list[float],
    limit: int,
    source_types: list[str] | None = None,
) -> list[RankedResult]:
    client = get_client()
    query_filter = None
    if source_types:
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="source_type",
                    match=models.MatchAny(any=source_types),
                )
            ]
        )

    hits = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=embedding,
        query_filter=query_filter,
        limit=max(limit * 5, 20),
        with_payload=True,
    ).points

    results: list[dict] = []
    for hit in hits:
        payload = hit.payload or {}
        results.append(
            {
                "score": hit.score,
                "path": payload.get("path", ""),
                "source_type": payload.get("source_type", ""),
                "source_name": payload.get("source_name", ""),
                "heading": payload.get("heading", ""),
                "text": payload.get("text", ""),
                "confidence": float(payload.get("confidence", 0.7)),
                "canonical": bool(payload.get("canonical", False)),
                "modified_at": payload.get("modified_at", ""),
            }
        )
    return rerank_results(query=query, hits=results, limit=limit)

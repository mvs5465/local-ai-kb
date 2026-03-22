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


def upsert_points(points: Iterable[models.PointStruct]) -> None:
    get_client().upsert(collection_name=QDRANT_COLLECTION, points=list(points))


def _build_filter(source_types: list[str] | None) -> models.Filter | None:
    if not source_types:
        return None
    return models.Filter(
        must=[
            models.FieldCondition(
                key="source_type",
                match=models.MatchAny(any=source_types),
            )
        ]
    )


def _payload_to_hit(payload: dict, score: float) -> dict:
    return {
        "score": score,
        "path": payload.get("path", ""),
        "source_type": payload.get("source_type", ""),
        "source_name": payload.get("source_name", ""),
        "heading": payload.get("heading", ""),
        "text": payload.get("text", ""),
        "confidence": float(payload.get("confidence", 0.7)),
        "canonical": bool(payload.get("canonical", False)),
        "modified_at": payload.get("modified_at", ""),
        "stale_after_days": payload.get("stale_after_days"),
        "deprecated": bool(payload.get("deprecated", False)),
        "tags": payload.get("tags", []),
    }


def lexical_candidates(limit: int, source_types: list[str] | None = None) -> list[dict]:
    client = get_client()
    query_filter = _build_filter(source_types)
    offset = None
    results: list[dict] = []

    while True:
        points, offset = client.scroll(
            collection_name=QDRANT_COLLECTION,
            scroll_filter=query_filter,
            with_payload=True,
            with_vectors=False,
            limit=256,
            offset=offset,
        )
        for point in points:
            payload = point.payload or {}
            results.append(_payload_to_hit(payload, 0.0))
        if offset is None:
            break

    return results


def search(
    query: str,
    embedding: list[float],
    limit: int,
    source_types: list[str] | None = None,
) -> list[RankedResult]:
    client = get_client()
    query_filter = _build_filter(source_types)

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
        results.append(_payload_to_hit(payload, float(hit.score)))

    merged: dict[tuple[str, str], dict] = {
        (item["path"], item["heading"]): item for item in results
    }
    for item in lexical_candidates(limit=limit, source_types=source_types):
        key = (item["path"], item["heading"])
        if key not in merged:
            merged[key] = item

    return rerank_results(query=query, hits=list(merged.values()), limit=limit)

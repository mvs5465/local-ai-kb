from __future__ import annotations

from pathlib import Path
import uuid

from qdrant_client.http import models

from local_ai_kb.chunking import chunk_markdown
from local_ai_kb.embedding import embed_texts
from local_ai_kb.qdrant_store import ensure_collection, replace_points
from local_ai_kb.sources import iter_source_files


def display_path(path: Path) -> str:
    try:
        return path.relative_to(Path.home()).as_posix()
    except ValueError:
        return path.as_posix()


def build_points() -> list[models.PointStruct]:
    points: list[models.PointStruct] = []
    chunk_texts: list[str] = []
    chunk_payloads: list[dict] = []

    for source_file in iter_source_files():
        path = source_file.path
        text = path.read_text(encoding="utf-8")
        for idx, chunk in enumerate(chunk_markdown(path, text)):
            chunk_text = chunk["text"]
            chunk_payloads.append(
                {
                    "path": display_path(path),
                    "heading": chunk["heading"],
                    "text": chunk_text,
                    "source_type": source_file.source_type,
                    "source_name": source_file.source_name,
                }
            )
            chunk_texts.append(f"{chunk['heading']}\n\n{chunk_text}")

    if not chunk_texts:
        return []

    embeddings = embed_texts(chunk_texts)
    ensure_collection(vector_size=len(embeddings[0]))

    for payload, embedding in zip(chunk_payloads, embeddings, strict=True):
        point_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"{payload['path']}::{payload['heading']}::{payload['text']}",
            )
        )
        points.append(
            models.PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload,
            )
        )

    return points


def main() -> None:
    points = build_points()
    if not points:
        print("No markdown files matched sources.yaml")
        return
    replace_points(points)
    print(f"Indexed {len(points)} chunks into Qdrant")


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path
import uuid

from qdrant_client.http import models

from local_ai_kb.chunking import chunk_markdown
from local_ai_kb.config import DOC_ROOTS
from local_ai_kb.embedding import embed_texts
from local_ai_kb.qdrant_store import ensure_collection, replace_points


def iter_source_files() -> list[Path]:
    files: list[Path] = []
    for root in DOC_ROOTS:
        if not root.exists():
            continue
        files.extend(sorted(root.rglob("*.md")))
    return files


def file_source_type(path: Path) -> str:
    parts = path.parts
    if "personal-memory" in parts:
        return "personal_memory"
    if "external" in parts:
        return "external_reference"
    return "internal_docs"


def build_points() -> list[models.PointStruct]:
    points: list[models.PointStruct] = []
    chunk_texts: list[str] = []
    chunk_payloads: list[dict] = []

    for path in iter_source_files():
        text = path.read_text(encoding="utf-8")
        for idx, chunk in enumerate(chunk_markdown(path, text)):
            chunk_text = chunk["text"]
            relative_path = path.relative_to(path.parents[2]).as_posix()
            chunk_payloads.append(
                {
                    "path": relative_path,
                    "heading": chunk["heading"],
                    "text": chunk_text,
                    "source_type": file_source_type(path),
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
        print("No markdown files found under docs/ or personal-memory/")
        return
    replace_points(points)
    print(f"Indexed {len(points)} chunks into Qdrant")


if __name__ == "__main__":
    main()

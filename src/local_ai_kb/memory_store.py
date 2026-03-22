from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re

from qdrant_client.http import models

from local_ai_kb.chunking import chunk_markdown
from local_ai_kb.embedding import embed_texts
from local_ai_kb.index_docs import display_path
from local_ai_kb.qdrant_store import upsert_points


SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    slug = SLUG_RE.sub("-", value.lower()).strip("-")
    return slug or "memory"


def _target_dir(kind: str, root_dir: Path) -> Path:
    if kind == "decision":
        return root_dir / "personal-memory" / "decisions"
    if kind == "gotcha":
        return root_dir / "personal-memory" / "gotchas"
    if kind == "preference":
        return root_dir / "personal-memory" / "preferences"
    return root_dir / "personal-memory" / "session-notes"


def write_memory(
    *,
    root_dir: Path,
    kind: str,
    title: str,
    summary: str,
    source: str = "",
    tags: list[str] | None = None,
) -> Path:
    tags = tags or []
    target_dir = _target_dir(kind, root_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = _slugify(title)
    path = target_dir / f"{timestamp}-{slug}.md"

    lines = [f"# {title}", ""]
    lines.append(f"- type: {kind}")
    lines.append(f"- created_at: {datetime.now(timezone.utc).isoformat()}")
    if source:
        lines.append(f"- source: {source}")
    if tags:
        lines.append(f"- tags: {', '.join(tags)}")
    lines.extend(["", summary.strip(), ""])

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def index_memory_file(path: Path, *, source_name: str = "personal-memory") -> int:
    text = path.read_text(encoding="utf-8")
    chunks = chunk_markdown(path, text)
    if not chunks:
        return 0

    modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    payloads: list[dict] = []
    chunk_texts: list[str] = []

    for chunk in chunks:
        payloads.append(
            {
                "path": display_path(path),
                "heading": chunk["heading"],
                "text": chunk["text"],
                "source_type": "personal_memory",
                "source_name": source_name,
                "confidence": 0.98,
                "canonical": True,
                "modified_at": modified_at,
                "stale_after_days": None,
                "deprecated": False,
                "tags": ["memory"],
            }
        )
        chunk_texts.append(f"{chunk['heading']}\n\n{chunk['text']}")

    embeddings = embed_texts(chunk_texts)
    points = []
    for payload, embedding in zip(payloads, embeddings, strict=True):
        point_id = str(
            __import__("uuid").uuid5(
                __import__("uuid").NAMESPACE_URL,
                f"{payload['path']}::{payload['heading']}::{payload['text']}",
            )
        )
        points.append(models.PointStruct(id=point_id, vector=embedding, payload=payload))

    upsert_points(points)
    return len(points)

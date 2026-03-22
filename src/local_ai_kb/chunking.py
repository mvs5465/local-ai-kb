from __future__ import annotations

from pathlib import Path


def chunk_markdown(path: Path, text: str, max_chars: int = 1200) -> list[dict]:
    lines = text.splitlines()
    chunks: list[dict] = []
    heading = path.stem
    buffer: list[str] = []

    def flush() -> None:
        content = "\n".join(buffer).strip()
        if not content:
            return
        chunks.append(
            {
                "heading": heading,
                "text": content,
            }
        )
        buffer.clear()

    for line in lines:
        if line.startswith("#"):
            flush()
            heading = line.lstrip("#").strip() or heading
            continue

        buffer.append(line)
        if sum(len(item) + 1 for item in buffer) >= max_chars:
            flush()

    flush()
    return chunks

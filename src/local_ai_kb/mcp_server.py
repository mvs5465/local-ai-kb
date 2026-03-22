from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from local_ai_kb.config import ROOT_DIR
from local_ai_kb.embedding import embed_texts
from local_ai_kb.memory_store import index_memory_file, write_memory
from local_ai_kb.qdrant_store import search
from local_ai_kb.retrieval import format_flags, format_snippet


host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT", "8090"))

SOURCE_TYPE_ALIASES = {
    "all": (),
    "any": (),
    "memory": ("personal_memory",),
    "memories": ("personal_memory",),
    "personal": ("personal_memory",),
    "personal_memory": ("personal_memory",),
    "document": ("internal_docs",),
    "documents": ("internal_docs",),
    "doc": ("internal_docs",),
    "docs": ("internal_docs",),
    "internal": ("internal_docs",),
    "internal_doc": ("internal_docs",),
    "internal_docs": ("internal_docs",),
    "guidance": ("internal_guidance",),
    "guide": ("internal_guidance",),
    "internal_guidance": ("internal_guidance",),
    "agents": ("internal_guidance",),
    "claude": ("internal_guidance",),
    "external": ("external_reference",),
    "external_reference": ("external_reference",),
    "reference": ("external_reference",),
    "references": ("external_reference",),
}


def _iter_source_type_tokens(source_types: list[str] | str | None) -> Iterable[str]:
    if source_types is None:
        return ()
    if isinstance(source_types, str):
        raw_values = source_types.split(",")
    else:
        raw_values = source_types
    return (value.strip().lower() for value in raw_values if value and value.strip())


def _normalize_source_types(source_types: list[str] | str | None) -> tuple[list[str] | None, list[str]]:
    normalized: list[str] = []
    unknown: list[str] = []

    for token in _iter_source_type_tokens(source_types):
        mapped = SOURCE_TYPE_ALIASES.get(token)
        if mapped is None:
            unknown.append(token)
            continue
        for item in mapped:
            if item not in normalized:
                normalized.append(item)

    return (normalized or None), unknown

mcp = FastMCP(
    "local-ai-kb",
    host=host,
    port=port,
    instructions=(
        "Use this knowledge base for local environment details, internal docs, durable personal memory, "
        "and copied external references. Prefer it early in environment-specific tasks and re-query it when "
        "the task scope narrows or when local decisions depend on org-specific knowledge. Treat returned hits "
        "as cited evidence with source type and path, not as unquestioned truth."
    ),
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


@mcp.tool(
    description=(
        "Search the local knowledge base for internal docs, external references, and personal durable memory. "
        "Use this for environment-specific questions, local process, design decisions, and recurring gotchas. "
        "Prefer omitting source_types unless you intentionally want to narrow the search. source_types accepts "
        "either a JSON list or a comma-separated string. Friendly filters are supported: memory, docs, guidance, "
        "external, or the exact types personal_memory, internal_docs, internal_guidance, external_reference."
    )
)
def search_kb(query: str, limit: int = 5, source_types: list[str] | str | None = None) -> str:
    embedding = embed_texts([query])[0]
    normalized_source_types, unknown_source_types = _normalize_source_types(source_types)
    results = search(
        query=query,
        embedding=embedding,
        limit=limit,
        source_types=normalized_source_types,
    )

    prefix_lines: list[str] = []
    if unknown_source_types:
        prefix_lines.append(
            "Ignored unknown source_types: "
            + ", ".join(unknown_source_types)
            + ". Valid filters are memory, docs, guidance, external."
        )
    if not results:
        if prefix_lines:
            prefix_lines.append("No matching KB entries found.")
            return "\n".join(prefix_lines)
        return "No matching KB entries found."

    lines = []
    for index, item in enumerate(results, start=1):
        lines.append(
            f"{index}. [{item.source_type}] {item.path} :: {item.heading} "
            f"(rank={item.score:.4f}, vector={item.raw_score:.4f}, lexical={item.lexical_score:.4f})"
        )
        if item.source_name:
            lines.append(f"source: {item.source_name}")
        lines.append(f"flags: {format_flags(item)}")
        lines.append(format_snippet(item.text))
        lines.append("")
    return "\n".join(prefix_lines + lines).strip()


@mcp.tool(
    description=(
        "Record a durable personal memory note into the local KB and index it immediately. "
        "Use this for stable decisions, gotchas, preferences, or short session notes worth keeping."
    )
)
def record_memory(
    title: str,
    summary: str,
    kind: str = "session-note",
    source: str = "",
    tags: list[str] | None = None,
) -> str:
    path = write_memory(
        root_dir=ROOT_DIR,
        kind=kind,
        title=title,
        summary=summary,
        source=source,
        tags=tags or [],
    )
    indexed = index_memory_file(Path(path), source_name="personal-memory")
    return f"Recorded memory at {path} and indexed {indexed} chunk(s)."


app = mcp.streamable_http_app()


if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port, log_level="info")

from __future__ import annotations

import os

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from local_ai_kb.embedding import embed_texts
from local_ai_kb.qdrant_store import search
from local_ai_kb.retrieval import format_snippet


host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT", "8090"))

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
        "Use this for environment-specific questions, local process, design decisions, and recurring gotchas."
    )
)
def search_kb(query: str, limit: int = 5, source_types: list[str] | None = None) -> str:
    embedding = embed_texts([query])[0]
    results = search(query=query, embedding=embedding, limit=limit, source_types=source_types)
    if not results:
        return "No matching KB entries found."

    lines = []
    for index, item in enumerate(results, start=1):
        lines.append(
            f"{index}. [{item.source_type}] {item.path} :: {item.heading} "
            f"(rank={item.score:.4f}, vector={item.raw_score:.4f})"
        )
        if item.source_name:
            lines.append(f"source: {item.source_name}")
        lines.append(format_snippet(item.text))
        lines.append("")
    return "\n".join(lines).strip()


app = mcp.streamable_http_app()


if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port, log_level="info")

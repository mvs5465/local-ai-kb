# AGENTS.md

Instructions for human + AI contributors in this repository.

## Product

- `local-ai-kb` is a lean personal knowledge base stack for local docs and durable memory.
- The repo owns source discovery, chunking, embeddings, Qdrant indexing, retrieval, and the FastMCP server surface.

## Architecture

- `src/local_ai_kb/index_docs.py` builds indexed chunks from configured markdown sources.
- `src/local_ai_kb/sources.py` expands and filters source files from `sources.yaml`.
- `src/local_ai_kb/retrieval.py` and `qdrant_store.py` handle search and vector-store integration.
- `src/local_ai_kb/mcp_server.py` exposes the KB tools.
- `docs/` and `personal-memory/` are first-class indexed inputs, not just repo docs.

## Working Rules

- Keep the KB honest: prefer improving source quality over adding speculative memory.
- Treat `sources.yaml` as the canonical place to broaden or narrow indexed inputs.
- Preserve the file-backed memory model; Qdrant is a retrieval layer, not the only store of record.
- When changing source discovery or ranking behavior, keep README guidance and actual behavior aligned.

## Verification

- Run `make index` after source or indexing changes.
- Run `make eval` when search behavior changes materially.
- Run `make run` only when you need the full local stack.

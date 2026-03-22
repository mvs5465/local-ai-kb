# local-ai-kb

Lean local knowledge base stack for personal docs and durable memory.

## Stack

- `Ollama` for local embeddings via `embeddinggemma`
- native `Qdrant` binary installed under `.local/bin/`
- `FastMCP` server on `http://127.0.0.1:8090/mcp`
- repo-local `docs/` and `personal-memory/` folders as the initial source set

## Commands

- `make run`: start Ollama, Qdrant, and the MCP server
- `make index`: index `docs/` and `personal-memory/` into Qdrant
- `make eval`: run the search eval cases in `evals/search_cases.yaml`
- `make stop`: stop the MCP server, Qdrant, and any Ollama process started by this repo

## Layout

```text
docs/
  internal/
  external/
personal-memory/
  decisions/
  gotchas/
  preferences/
  session-notes/
scripts/
sources.yaml
src/local_ai_kb/
```

## Notes

- `make run` pulls `embeddinggemma` if it is missing locally.
- Qdrant installs into `.local/bin/qdrant` and stores data under `.data/qdrant/`.
- Personal memory remains file-backed and portable; Qdrant is only the retrieval layer.
- Index sources are configured in `sources.yaml`. The default config includes top-level and one-level nested repo `README.md`, `AGENTS.md`, and `CLAUDE.md` files under `~/projects`, plus local `docs/` and `personal-memory/`.
- Each source block in `sources.yaml` supports `paths` plus optional `exclude_paths`, so you can add repo docs, guidance files, or other markdown sources without touching code.
- Source blocks can also carry `confidence` and `canonical` metadata, which the reranker uses when ordering results.
- The MCP server now exposes both `search_kb` and `record_memory`.
- `search_kb` works best without `source_types` by default; if you want to narrow, it accepts either a JSON list or a comma-separated string, and friendly aliases like `memory`, `docs`, `guidance`, and `external`.
- `record_memory` writes a markdown note into `personal-memory/` and indexes it immediately, so future sessions can capture durable notes without manual file editing.

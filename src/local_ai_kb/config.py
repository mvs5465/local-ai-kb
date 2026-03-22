from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
SOURCES_CONFIG = ROOT_DIR / "sources.yaml"

import os
QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "kb_chunks")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "embeddinggemma")

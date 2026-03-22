#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/.run"
QDRANT_SESSION="local-ai-kb-qdrant"
MCP_SESSION="local-ai-kb-mcp"

if tmux has-session -t "${MCP_SESSION}" 2>/dev/null; then
  tmux kill-session -t "${MCP_SESSION}"
  echo "Stopped MCP server"
fi

if tmux has-session -t "${QDRANT_SESSION}" 2>/dev/null; then
  tmux kill-session -t "${QDRANT_SESSION}"
  echo "Stopped Qdrant"
fi

if [[ -f "${RUN_DIR}/ollama.mode" ]]; then
  if [[ "$(cat "${RUN_DIR}/ollama.mode")" == "service" ]]; then
    brew services stop ollama >/dev/null 2>&1 || true
    echo "Stopped Ollama"
  elif [[ -f "${RUN_DIR}/ollama.pid" ]] && kill -0 "$(cat "${RUN_DIR}/ollama.pid")" 2>/dev/null; then
    kill "$(cat "${RUN_DIR}/ollama.pid")"
    rm -f "${RUN_DIR}/ollama.pid"
    echo "Stopped Ollama"
  fi
  rm -f "${RUN_DIR}/ollama.mode"
fi

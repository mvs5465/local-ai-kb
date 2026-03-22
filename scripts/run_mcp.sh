#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/.run"
SESSION_NAME="local-ai-kb-mcp"
mkdir -p "${RUN_DIR}"

"${ROOT_DIR}/scripts/setup_venv.sh"

if tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
  echo "MCP server already running on 127.0.0.1:8090"
  exit 0
fi

tmux new-session -d -s "${SESSION_NAME}" \
  "cd '${ROOT_DIR}' && exec env PYTHONPATH='${ROOT_DIR}/src' HOST='127.0.0.1' PORT='8090' QDRANT_URL='http://127.0.0.1:6333' QDRANT_COLLECTION='kb_chunks' OLLAMA_URL='http://127.0.0.1:11434' OLLAMA_MODEL='embeddinggemma' .venv/bin/python -m local_ai_kb.mcp_server >>'${RUN_DIR}/mcp.log' 2>&1"

for _ in $(seq 1 30); do
  status_code="$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8090/mcp || true)"
  if [[ "${status_code}" == "200" || "${status_code}" == "405" || "${status_code}" == "406" ]]; then
    break
  fi
  sleep 1
done

echo "MCP server ready at http://127.0.0.1:8090/mcp"

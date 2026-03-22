#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/.run"
mkdir -p "${RUN_DIR}"

if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "Ollama already running on 127.0.0.1:11434"
else
  if brew services start ollama >>"${RUN_DIR}/ollama.log" 2>&1; then
    echo "service" > "${RUN_DIR}/ollama.mode"
  else
    nohup env \
      OLLAMA_FLASH_ATTENTION="1" \
      OLLAMA_KV_CACHE_TYPE="q8_0" \
      ollama serve >"${RUN_DIR}/ollama.log" 2>&1 &
    echo $! > "${RUN_DIR}/ollama.pid"
    echo "pid" > "${RUN_DIR}/ollama.mode"
  fi

  for _ in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

if ! curl -fsS http://127.0.0.1:11434/api/tags | grep -q '"name":"embeddinggemma'; then
  ollama pull embeddinggemma >>"${RUN_DIR}/ollama.log" 2>&1
fi

echo "Ollama ready"

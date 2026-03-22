#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/.run"
SESSION_NAME="local-ai-kb-qdrant"
mkdir -p "${RUN_DIR}"

"${ROOT_DIR}/scripts/install_qdrant.sh"

if tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
  echo "Qdrant already running on 127.0.0.1:6333"
  exit 0
fi

tmux new-session -d -s "${SESSION_NAME}" \
  "cd '${ROOT_DIR}' && exec ./.local/bin/qdrant --config-path config/qdrant.yaml >>'${RUN_DIR}/qdrant.log' 2>&1"

for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:6333/collections >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "Qdrant ready"

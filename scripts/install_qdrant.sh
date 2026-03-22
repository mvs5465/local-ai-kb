#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${ROOT_DIR}/.local/bin"
RUN_DIR="${ROOT_DIR}/.run"
mkdir -p "${BIN_DIR}" "${RUN_DIR}" "${ROOT_DIR}/.data/qdrant/storage"

QDRANT_VERSION="${QDRANT_VERSION:-v1.17.0}"
ARCH="$(uname -m)"

case "${ARCH}" in
  arm64)
    ASSET="qdrant-aarch64-apple-darwin.tar.gz"
    ;;
  x86_64)
    ASSET="qdrant-x86_64-apple-darwin.tar.gz"
    ;;
  *)
    echo "Unsupported macOS architecture for native Qdrant install: ${ARCH}" >&2
    exit 1
    ;;
esac

if [[ -x "${BIN_DIR}/qdrant" ]]; then
  exit 0
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

cd "${TMP_DIR}"
curl -fsSLO "https://github.com/qdrant/qdrant/releases/download/${QDRANT_VERSION}/${ASSET}"
tar -xzf "${ASSET}"
mv qdrant "${BIN_DIR}/qdrant"
chmod +x "${BIN_DIR}/qdrant"

echo "Installed Qdrant ${QDRANT_VERSION} to ${BIN_DIR}/qdrant" >>"${RUN_DIR}/qdrant-install.log"

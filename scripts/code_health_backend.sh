#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/reports/code_health"

mkdir -p "${OUT_DIR}"

python3 -m pip install -q radon pydeps

radon cc -s -a "${ROOT_DIR}/backend/apps" > "${OUT_DIR}/radon_cc.txt"
radon cc -j "${ROOT_DIR}/backend/apps" > "${OUT_DIR}/radon_cc.json"
radon mi -s "${ROOT_DIR}/backend/apps" > "${OUT_DIR}/radon_mi.txt"
radon mi -j "${ROOT_DIR}/backend/apps" > "${OUT_DIR}/radon_mi.json"
radon raw "${ROOT_DIR}/backend/apps" > "${OUT_DIR}/radon_raw.txt"
radon hal "${ROOT_DIR}/backend/apps" > "${OUT_DIR}/radon_hal.txt"

pydeps "${ROOT_DIR}/backend/apps" \
  --max-bacon 2 \
  --show-deps \
  --deps-output "${OUT_DIR}/pydeps_deps.txt" \
  --show-dot \
  --dot-output "${OUT_DIR}/pydeps.dot" \
  --nodot \
  --no-output

echo "OK: ${OUT_DIR}"


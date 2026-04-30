#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 - <<'PY'
import os
import py_compile

root = "/workspace/backend/apps"
count = 0
for dirpath, dirnames, filenames in os.walk(root):
    for name in filenames:
        if name.endswith(".py"):
            path = os.path.join(dirpath, name)
            py_compile.compile(path, doraise=True)
            count += 1
print(count)
PY


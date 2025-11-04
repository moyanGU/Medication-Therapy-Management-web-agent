#!/bin/sh
set -eu

# 安全检查 dist 是否含有硬编码 127.0.0.1:8000（BusyBox兼容版）
# 通过 find 限定文件类型，再用 grep 检查，命中仅输出前 20 行，避免刷屏

DIR=${1:-dist}
if [ ! -d "$DIR" ]; then
  echo "[guard] 跳过：目录不存在 -> $DIR"
  exit 0
fi

# 收集命中样例（最多 20 行）
RESULT=$(find "$DIR" -type f \( -name '*.js' -o -name '*.css' -o -name '*.html' -o -name '*.map' \) -exec grep -n -E "127\\.0\\.0\\.1:8000" {} \; | head -n 20 || true)

if [ -n "$RESULT" ]; then
  echo "[guard] ERROR: 在 $DIR 中发现硬编码 127.0.0.1:8000"
  echo "$RESULT"
  exit 1
else
  echo "[guard] OK: 未发现硬编码 127.0.0.1:8000"
fi
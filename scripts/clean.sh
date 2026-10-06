#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
find "$ROOT/sources/normalized" "$ROOT/sources/manifests" "$ROOT/dataset/generated" \
  "$ROOT/dataset/train" "$ROOT/dataset/validation" "$ROOT/dataset/test" "$ROOT/logs" \
  -type f ! -name .gitkeep -delete
echo "Generated datasets, manifests, and logs were removed. Models and raw sources were preserved."

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

find "$MQDECK_ROOT/sources/normalized" "$MQDECK_ROOT/sources/manifests" \
  "$MQDECK_ROOT/dataset/generated" "$MQDECK_ROOT/dataset/train" \
  "$MQDECK_ROOT/dataset/validation" "$MQDECK_ROOT/dataset/test" "$MQDECK_ROOT/logs" \
  -type f ! -name .gitkeep -delete
echo "Generated datasets, manifests, and logs were removed. Models and raw sources were preserved."

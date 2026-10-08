#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

cd "$MQDECK_ROOT"
mkdir -p logs
PYTHON_BIN="$(python_bin)"
require_python "$PYTHON_BIN"
"$PYTHON_BIN" -m pipeline.prepare "$@" 2>&1 | tee logs/dataset.log

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p logs
PYTHON_BIN="${PYTHON_BIN:-$ROOT/.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN=python3
"$PYTHON_BIN" -m pipeline.prepare "$@" 2>&1 | tee logs/dataset.log

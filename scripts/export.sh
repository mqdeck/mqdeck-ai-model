#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

VERSION=""
SKIP_MERGE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="${2:-}"; shift 2 ;;
    --skip-merge) SKIP_MERGE=1; shift ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$VERSION" ]] || fail "--version is required."
validate_version "$VERSION"
cd "$MQDECK_ROOT"
mkdir -p logs
PYTHON_BIN="$(python_bin)"
require_python "$PYTHON_BIN"
{
  if [[ "$SKIP_MERGE" == "0" ]]; then
    "$PYTHON_BIN" -m training.merge_adapter --version "$VERSION"
  fi
  ./export/export_gguf.sh "$VERSION"
  while IFS= read -r quantization; do
    ./export/quantize.sh "$VERSION" "$quantization"
  done < <("$PYTHON_BIN" -c 'import yaml; print("\n".join(yaml.safe_load(open("config/model.yaml"))["gguf"]["quantizations"]))')
  "$PYTHON_BIN" export/create_manifest.py --version "$VERSION"
  "$PYTHON_BIN" export/release.py --version "$VERSION"
} 2>&1 | tee logs/export.log

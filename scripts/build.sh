#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

VERSION="$MQDECK_DEFAULT_VERSION"
PREPARE_ONLY=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: ./scripts/build-model.sh [VERSION] [OPTIONS]

Build the dataset, train the adapter, evaluate it, and export a GGUF release.

Options:
  --version VERSION     Release version (default: 0.1.0)
  --prepare-only        Prepare and validate the dataset without training
  --dry-run             Show the build phases without changing files
  -h, --help            Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      [[ $# -ge 2 ]] || fail "--version requires a value."
      VERSION="$2"
      shift 2
      ;;
    --prepare-only) PREPARE_ONLY=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    # Retained for compatibility. All builds already use only custom/ content.
    --custom-only) shift ;;
    -h|--help) usage; exit 0 ;;
    -*) fail "Unknown option: $1" ;;
    *) VERSION="$1"; shift ;;
  esac
done
validate_version "$VERSION"

printf 'MQDeck AI public build %s\n' "$VERSION"

if [[ "$DRY_RUN" == "1" ]]; then
  echo "No files or models will be changed."
  echo "[1/5] Prepare and validate local, licensed training data"
  if [[ "$PREPARE_ONLY" == "1" ]]; then
    echo "[2-5/5] Skipped (--prepare-only)"
  else
    echo "[2/5] Train the QLoRA adapter"
    echo "[3/5] Merge the adapter with the pinned base model"
    echo "[4/5] Run concept, safety, and language evaluation"
    echo "[5/5] Convert, quantize, and package the GGUF release"
  fi
  exit 0
fi

cd "$MQDECK_ROOT"
mkdir -p logs
PYTHON_BIN="$(python_bin)"
export PYTHON_BIN
require_python "$PYTHON_BIN"

info "[1/5] Preparing and validating the dataset"
./scripts/prepare.sh

if [[ "$PREPARE_ONLY" == "1" ]]; then
  info "Dataset ready: $MQDECK_ROOT/dataset"
  exit 0
fi

info "[2/5] Training the QLoRA adapter"
./scripts/train.sh --version "$VERSION"
info "[3/5] Merging the adapter"
"$PYTHON_BIN" -m training.merge_adapter --version "$VERSION" 2>&1 | tee -a logs/training.log
info "[4/5] Evaluating the model"
./scripts/evaluate.sh --version "$VERSION"
info "[5/5] Exporting the GGUF release"
./scripts/export.sh --version "$VERSION" --skip-merge
info "Build complete: $MQDECK_ROOT/models/releases/$VERSION"

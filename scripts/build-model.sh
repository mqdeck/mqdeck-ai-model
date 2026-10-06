#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=""
CUSTOM_ONLY=0
PREPARE_ONLY=0
DRY_RUN=0
PROFILE="public"

usage() {
  echo "Usage: build-model.sh --version VERSION [--custom-only] [--prepare-only] [--dry-run] [--profile public|private]"
}
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="${2:-}"; shift 2 ;;
    --custom-only) CUSTOM_ONLY=1; shift ;;
    --prepare-only) PREPARE_ONLY=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --profile) PROFILE="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done
[[ -n "$VERSION" ]] || { echo "--version is required" >&2; usage; exit 2; }
[[ "$PROFILE" == "public" || "$PROFILE" == "private" ]] || { echo "Invalid profile: $PROFILE" >&2; exit 2; }

echo "MQDeck AI Model Builder"
echo "======================="
echo "Version: $VERSION"
echo "Build profile: $PROFILE"
echo "Languages: English, Portuguese, Spanish"
echo "Language policy: answer in the question's language"
echo

if [[ "$DRY_RUN" == "1" ]]; then
  echo "Dry run; no files or models will be modified."
  echo "[1/16] Validate Python, configuration, dataset paths, and training environment"
  echo "[2/16] Remote collection disabled; use only explicitly licensed local content"
  echo "[3/16] Discover custom files"
  echo "[4/16] Normalize documents"
  echo "[5/16] Deduplicate by SHA-256"
  echo "[6/16] Apply $PROFILE license policy"
  echo "[7/16] Generate source-grounded examples"
  echo "[8/16] Validate safety, length, placeholders, duplicates, and provenance"
  echo "[9/16] Split train/validation/test deterministically"
  if [[ "$PREPARE_ONLY" == "1" ]]; then
    echo "[10-16/16] Skip training and model export (--prepare-only)"
  else
    echo "[10/16] Train QLoRA adapter"
    echo "[11/16] Save checkpoints and training metadata"
    echo "[12/16] Merge adapter with base model"
    echo "[13/16] Evaluate expected concepts"
    echo "[14/16] Convert merged model to F16 GGUF"
    echo "[15/16] Quantize configured GGUF variants"
    echo "[16/16] Create and checksum release models/releases/$VERSION"
  fi
  exit 0
fi

cd "$ROOT"
mkdir -p logs
PYTHON_BIN="${PYTHON_BIN:-$ROOT/.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN=python3
echo "[1/16] Environment"
"$PYTHON_BIN" -c 'import sys; print("       Python", sys.version.split()[0]); assert sys.version_info >= (3, 10)'

echo "[2/16] Sources: local, explicitly licensed content only"

echo "[3-9/16] Preparing and validating dataset"
PREPARE_ARGS=(--profile "$PROFILE")
if [[ "$CUSTOM_ONLY" == "1" ]]; then PREPARE_ARGS+=(--custom-only); fi
./scripts/prepare.sh "${PREPARE_ARGS[@]}"

if [[ "$PREPARE_ONLY" == "1" ]]; then
  echo "DONE"
  echo "Prepared dataset: $ROOT/dataset"
  exit 0
fi

echo "[10-11/16] Training adapter"
./scripts/train.sh --version "$VERSION"
echo "[12/16] Merging adapter"
"$PYTHON_BIN" -m training.merge_adapter --version "$VERSION" 2>&1 | tee -a logs/training.log
echo "[13/16] Evaluating model"
./scripts/evaluate.sh --version "$VERSION"
echo "[14-16/16] Converting, quantizing, and releasing"
./scripts/export.sh --version "$VERSION" --skip-merge
echo "DONE"
echo "Release: $ROOT/models/releases/$VERSION"

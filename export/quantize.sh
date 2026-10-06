#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:?Usage: quantize.sh VERSION [QUANTIZATION]}"
QUANTIZATION="${2:-Q4_K_M}"
LLAMA_DIR="${LLAMA_CPP_PATH:-$ROOT/work/llama.cpp}"
INPUT="$ROOT/models/releases/$VERSION/mqdeck-ai-$VERSION-F16.gguf"
OUTPUT="$ROOT/models/releases/$VERSION/mqdeck-ai-$VERSION-$QUANTIZATION.gguf"

QUANTIZE=""
for candidate in "$LLAMA_DIR/build/bin/llama-quantize" "$LLAMA_DIR/llama-quantize" "$LLAMA_DIR/quantize"; do
  if [[ -x "$candidate" ]]; then QUANTIZE="$candidate"; break; fi
done
if [[ -z "$QUANTIZE" ]]; then
  echo "llama-quantize was not found. Build llama.cpp with: cmake -B build && cmake --build build --config Release" >&2
  exit 2
fi
"$QUANTIZE" "$INPUT" "$OUTPUT" "$QUANTIZATION"
echo "$OUTPUT"

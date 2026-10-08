#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:?Usage: export_gguf.sh VERSION}"
LLAMA_DIR="${LLAMA_CPP_PATH:-$ROOT/work/llama.cpp}"
MERGED="$ROOT/models/merged/$VERSION"
RELEASE="$ROOT/models/releases/$VERSION"
F16="$RELEASE/mqdeck-ai-$VERSION-F16.gguf"

if [[ ! -d "$MERGED" ]]; then
  echo "Merged model not found: $MERGED" >&2
  exit 2
fi
if [[ ! -d "$LLAMA_DIR" ]]; then
  if [[ "${ALLOW_LLAMA_CPP_CLONE:-0}" != "1" ]]; then
    echo "llama.cpp not found. Set LLAMA_CPP_PATH or explicitly set ALLOW_LLAMA_CPP_CLONE=1." >&2
    exit 2
  fi
  git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$LLAMA_DIR"
fi
mkdir -p "$RELEASE"
DEFAULT_CONVERTER_PYTHON="$ROOT/work/llama.cpp-venv/bin/python"
if [[ -x "$DEFAULT_CONVERTER_PYTHON" ]]; then
  PYTHON_BIN="${LLAMA_CPP_PYTHON:-$DEFAULT_CONVERTER_PYTHON}"
else
  PYTHON_BIN="${LLAMA_CPP_PYTHON:-${PYTHON_BIN:-$ROOT/.venv/bin/python}}"
fi
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN=python3
CONVERTER="$LLAMA_DIR/convert_hf_to_gguf.py"
if [[ ! -f "$CONVERTER" ]]; then
  echo "Official conversion script not found: $CONVERTER" >&2
  exit 2
fi
"$PYTHON_BIN" "$CONVERTER" "$MERGED" --outfile "$F16" --outtype f16
echo "$F16"

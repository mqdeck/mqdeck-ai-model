#!/usr/bin/env bash
# Ubuntu + NVIDIA: prepare the machine and build the final GGUF.
# Usage, from a fresh checkout: ./scripts/ubuntu.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-0.1.0}"
LLAMA_DIR="${ROOT}/work/llama.cpp"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This script is for Ubuntu." >&2
  exit 1
fi

if [[ "${EUID}" -eq 0 ]]; then
  SUDO=()
else
  SUDO=(sudo)
fi

"${SUDO[@]}" apt-get update
"${SUDO[@]}" apt-get install -y python3 python3-venv python3-dev python3-pip build-essential cmake git

if ! command -v nvidia-smi >/dev/null 2>&1 || ! nvidia-smi >/dev/null 2>&1; then
  echo "Installing the NVIDIA driver. Reboot when apt finishes, then run ./scripts/ubuntu.sh again."
  "${SUDO[@]}" apt-get install -y nvidia-driver-570
  exit 0
fi

nvidia-smi

python3 -m venv "${ROOT}/.venv"
# shellcheck disable=SC1091
source "${ROOT}/.venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install torch --index-url https://download.pytorch.org/whl/cu128
python -m pip install -e "${ROOT}[train]"
python -m pip install torch --index-url https://download.pytorch.org/whl/cu128
python - <<'PY'
import torch
print("torch", torch.__version__, "cuda", torch.cuda.is_available())
if not torch.cuda.is_available():
    raise SystemExit("CUDA is not visible to PyTorch. Check the driver, reboot, and run this script again.")
print(torch.cuda.get_device_name(0))
PY

if [[ ! -d "${LLAMA_DIR}/.git" ]]; then
  git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "${LLAMA_DIR}"
fi
cmake -S "${LLAMA_DIR}" -B "${LLAMA_DIR}/build" -DGGML_CUDA=OFF
cmake --build "${LLAMA_DIR}/build" --target llama-quantize -j"$(nproc)"
if [[ -f "${LLAMA_DIR}/requirements/requirements-convert_hf_to_gguf.txt" ]]; then
  python -m pip install -r "${LLAMA_DIR}/requirements/requirements-convert_hf_to_gguf.txt"
fi

export ALLOW_LLAMA_CPP_CLONE=1
export LLAMA_CPP_PATH="${LLAMA_DIR}"
export PYTHON_BIN="${ROOT}/.venv/bin/python"
"${ROOT}/scripts/build-model.sh" --version "${VERSION}"

echo "Final model: ${ROOT}/models/releases/${VERSION}/mqdeck-ai-${VERSION}-Q4_K_M.gguf"

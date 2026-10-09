#!/usr/bin/env bash
# Prepare a supported Ubuntu NVIDIA host and build a complete MQDeck AI GGUF release.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

ORIGINAL_ARGS=("$@")
VERSION="$MQDECK_DEFAULT_VERSION"
PREPARE_ONLY=0
DRY_RUN=0
SKIP_SYSTEM_PACKAGES=0
INSTALL_DRIVER=1
TORCH_INDEX_URL="${MQDECK_TORCH_INDEX_URL:-https://download.pytorch.org/whl/cu128}"
TORCH_VERSION="${MQDECK_TORCH_VERSION:-}"
LLAMA_CPP_REF="${MQDECK_LLAMA_CPP_REF:-v0.6.0}"
LLAMA_DIR="${LLAMA_CPP_PATH:-$MQDECK_ROOT/work/llama.cpp}"
LLAMA_VENV="$MQDECK_ROOT/work/llama.cpp-venv"
CONSTRAINTS="$MQDECK_ROOT/requirements/ubuntu-cu128.lock"

usage() {
  cat <<'EOF'
Usage: ./scripts/run.sh [VERSION] [OPTIONS]

Prepare an Ubuntu NVIDIA machine and build the model in one command.

Options:
  --version VERSION         Release version (default: 0.1.0)
  --prepare-only            Build only the licensed dataset; no GPU is required
  --skip-system-packages    Do not run apt; use packages already on the host
  --no-driver-install       Do not install a missing NVIDIA driver
  --dry-run                 Show the actions without changing the machine
  -h, --help                Show this help

Advanced environment overrides:
  MQDECK_TORCH_INDEX_URL    PyTorch wheel index
  MQDECK_TORCH_VERSION      Override the compatible PyTorch version
  MQDECK_LLAMA_CPP_REF      llama.cpp tag or commit
  LLAMA_CPP_PATH            Existing llama.cpp checkout
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
    --skip-system-packages) SKIP_SYSTEM_PACKAGES=1; shift ;;
    --no-driver-install) INSTALL_DRIVER=0; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) fail "Unknown option: $1" ;;
    *) VERSION="$1"; shift ;;
  esac
done

validate_version "$VERSION"

if [[ "$DRY_RUN" == "1" ]]; then
  cat <<EOF
MQDeck AI Ubuntu setup and build $VERSION
No files, packages, drivers, or models will be changed.

[1/6] Validate Ubuntu x86-64 and available storage
[2/6] Install required Ubuntu packages
[3/6] Validate the NVIDIA driver and GPU
[4/6] Create .venv and install the pinned training stack
[5/6] Check out llama.cpp $LLAMA_CPP_REF and build llama-quantize
[6/6] Prepare data, train, evaluate, and export the GGUF release
EOF
  if [[ "$PREPARE_ONLY" == "1" ]]; then
    echo "GPU setup, training, and export will be skipped (--prepare-only)."
  fi
  exit 0
fi

[[ "$(uname -s)" == "Linux" ]] || fail "This script supports Ubuntu Linux only."
[[ "$(uname -m)" == "x86_64" ]] || fail "This automated setup supports x86-64 hosts only."
[[ -r /etc/os-release ]] || fail "Unable to identify the operating system."
# shellcheck disable=SC1091
source /etc/os-release
[[ "${ID:-}" == "ubuntu" ]] || fail "This script supports Ubuntu only; detected ${PRETTY_NAME:-unknown}."

case "${VERSION_ID:-}" in
  22.04|24.04) ;;
  *)
    echo "Warning: Ubuntu ${VERSION_ID:-unknown} is outside the supported set (22.04 and 24.04)." >&2
    ;;
esac

if [[ "$EUID" -eq 0 ]]; then
  SUDO=()
elif command -v sudo >/dev/null 2>&1; then
  SUDO=(sudo)
else
  SUDO=()
fi

install_recommended_driver() {
  command -v ubuntu-drivers >/dev/null 2>&1 ||
    fail "ubuntu-drivers is unavailable. Rerun without --skip-system-packages."
  if [[ "$EUID" -ne 0 && ${#SUDO[@]} -eq 0 ]]; then
    fail "sudo is required to install the NVIDIA driver."
  fi
  echo "Installing the compute driver recommended by Ubuntu for this GPU."
  "${SUDO[@]}" ubuntu-drivers install --gpgpu
  printf '\nThe driver was installed. Reboot the machine, return to the repository, and run the same command:\n  ./scripts/run.sh'
  if (( ${#ORIGINAL_ARGS[@]} > 0 )); then
    printf ' %q' "${ORIGINAL_ARGS[@]}"
  fi
  printf '\n'
  exit 10
}

cd "$MQDECK_ROOT"
available_kib="$(df -Pk "$MQDECK_ROOT" | awk 'NR == 2 {print $4}')"
required_kib=$((20 * 1024 * 1024))
if (( available_kib < required_kib )); then
  fail "At least 20 GiB of free storage is required in $MQDECK_ROOT."
fi

info "[1/6] Host validated: ${PRETTY_NAME}, x86-64"

if [[ "$SKIP_SYSTEM_PACKAGES" == "0" ]]; then
  if [[ "$EUID" -ne 0 && ${#SUDO[@]} -eq 0 ]]; then
    fail "sudo is required to install system packages."
  fi
  info "[2/6] Installing Ubuntu packages"
  "${SUDO[@]}" env DEBIAN_FRONTEND=noninteractive apt-get update
  "${SUDO[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    cmake \
    git \
    pciutils \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    ubuntu-drivers-common
else
  info "[2/6] Using existing Ubuntu packages"
fi

for command_name in cmake git python3; do
  command -v "$command_name" >/dev/null 2>&1 || fail "$command_name is required."
done

if [[ "$PREPARE_ONLY" == "0" ]]; then
  info "[3/6] Validating the NVIDIA driver"
  if ! command -v nvidia-smi >/dev/null 2>&1 || ! nvidia-smi >/dev/null 2>&1; then
    if [[ "$INSTALL_DRIVER" == "0" ]]; then
      fail "The NVIDIA driver is unavailable. Install the Ubuntu-recommended driver and rerun this command."
    fi
    command -v ubuntu-drivers >/dev/null 2>&1 ||
      fail "ubuntu-drivers is unavailable. Rerun without --skip-system-packages."
    if ! lspci | grep -qi 'NVIDIA'; then
      fail "No NVIDIA GPU was detected. Use an Ubuntu x86-64 host with a supported NVIDIA GPU."
    fi

    install_recommended_driver
  fi
  driver_version="$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n 1)"
  driver_major="${driver_version%%.*}"
  if [[ "$driver_major" =~ ^[0-9]+$ ]] && (( driver_major < 570 )); then
    if [[ "$INSTALL_DRIVER" == "0" ]]; then
      fail "NVIDIA driver $driver_version is too old for the pinned CUDA 12.8 stack (570 or newer is required)."
    fi
    install_recommended_driver
  fi
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
else
  info "[3/6] GPU setup skipped (--prepare-only)"
fi

info "[4/6] Creating the Python environment"
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi
PYTHON_BIN="$MQDECK_ROOT/.venv/bin/python"
export PYTHON_BIN
"$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel

python_version="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [[ -z "$TORCH_VERSION" ]]; then
  if "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 14) else 1)'; then
    TORCH_VERSION="2.9.1"
  else
    TORCH_VERSION="2.7.1"
  fi
fi

if [[ "$PREPARE_ONLY" == "1" ]]; then
  "$PYTHON_BIN" -m pip install -e "$MQDECK_ROOT"
  "$MQDECK_ROOT/scripts/build.sh" --version "$VERSION" --prepare-only
  info "Dataset ready: $MQDECK_ROOT/dataset"
  exit 0
fi

info "Installing PyTorch $TORCH_VERSION for Python $python_version"
"$PYTHON_BIN" -m pip install "torch==$TORCH_VERSION" --index-url "$TORCH_INDEX_URL"
"$PYTHON_BIN" -m pip install --constraint "$CONSTRAINTS" -e "$MQDECK_ROOT[train]"

"$PYTHON_BIN" - <<'PY'
import bitsandbytes
import torch

if not torch.cuda.is_available():
    raise SystemExit(
        "CUDA is not visible to PyTorch. Check the driver and Secure Boot, reboot, and rerun the script."
    )

device = torch.cuda.current_device()
properties = torch.cuda.get_device_properties(device)
capability = torch.cuda.get_device_capability(device)
vram_gib = properties.total_memory / 1024**3

print(f"PyTorch {torch.__version__}; CUDA runtime {torch.version.cuda}")
print(f"bitsandbytes {bitsandbytes.__version__}")
print(f"GPU: {properties.name}; compute capability {capability[0]}.{capability[1]}; {vram_gib:.1f} GiB VRAM")

if capability < (7, 0):
    raise SystemExit("This pinned CUDA stack requires NVIDIA compute capability 7.0 or newer.")
if vram_gib < 5.5:
    raise SystemExit("At least 6 GiB of GPU VRAM is required by the default training profile.")
PY

info "[5/6] Preparing llama.cpp $LLAMA_CPP_REF"
if [[ -n "${LLAMA_CPP_PATH:-}" ]]; then
  [[ -f "$LLAMA_DIR/convert_hf_to_gguf.py" ]] ||
    fail "LLAMA_CPP_PATH does not contain convert_hf_to_gguf.py: $LLAMA_DIR"
else
  if [[ ! -d "$LLAMA_DIR/.git" ]]; then
    git clone --filter=blob:none https://github.com/ggml-org/llama.cpp.git "$LLAMA_DIR"
  fi
  [[ -z "$(git -C "$LLAMA_DIR" status --short)" ]] ||
    fail "The managed llama.cpp checkout has local changes: $LLAMA_DIR"
  git -C "$LLAMA_DIR" fetch --depth 1 origin "$LLAMA_CPP_REF"
  git -C "$LLAMA_DIR" checkout --detach FETCH_HEAD
fi

cmake -S "$LLAMA_DIR" -B "$LLAMA_DIR/build" -DGGML_CUDA=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build "$LLAMA_DIR/build" --target llama-quantize --parallel "$(nproc)"

converter_requirements="$LLAMA_DIR/requirements/requirements-convert_hf_to_gguf.txt"
if [[ -f "$converter_requirements" ]]; then
  if [[ ! -x "$LLAMA_VENV/bin/python" ]]; then
    python3 -m venv "$LLAMA_VENV"
  fi
  "$LLAMA_VENV/bin/python" -m pip install --upgrade pip
  "$LLAMA_VENV/bin/python" -m pip install -r "$converter_requirements"
  export LLAMA_CPP_PYTHON="$LLAMA_VENV/bin/python"
fi

info "[6/6] Building MQDeck AI $VERSION"
export LLAMA_CPP_PATH="$LLAMA_DIR"
"$MQDECK_ROOT/scripts/build.sh" --version "$VERSION"

final_model="$MQDECK_ROOT/models/releases/$VERSION/mqdeck-ai-$VERSION-Q4_K_M.gguf"
info "Model ready: $final_model"

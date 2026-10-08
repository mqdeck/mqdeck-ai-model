#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

command -v python3 >/dev/null 2>&1 || fail "Python 3 was not found."
cd "$MQDECK_ROOT"

if [[ ! -x .venv/bin/python ]]; then
  info "Creating .venv"
  python3 -m venv .venv
fi

info "Installing development dependencies"
.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install -e '.[dev]'

info "Development environment ready"
echo "Run tests with: make test"
echo "For the complete Ubuntu GPU setup and model build, run: ./scripts/ubuntu.sh"

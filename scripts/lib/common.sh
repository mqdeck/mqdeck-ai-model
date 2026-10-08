#!/usr/bin/env bash

# Shared shell helpers. This file is sourced by the executable scripts.

MQDECK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MQDECK_DEFAULT_VERSION="0.1.0"

info() {
  printf '\n==> %s\n' "$*"
}

fail() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

python_bin() {
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    printf '%s\n' "$PYTHON_BIN"
  elif [[ -x "$MQDECK_ROOT/.venv/bin/python" ]]; then
    printf '%s\n' "$MQDECK_ROOT/.venv/bin/python"
  else
    printf '%s\n' "python3"
  fi
}

validate_version() {
  local version="$1"
  [[ "$version" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] ||
    fail "Invalid version '$version'. Use letters, numbers, dots, underscores, or hyphens."
}

require_python() {
  local executable="$1"
  command -v "$executable" >/dev/null 2>&1 ||
    fail "Python was not found. Run ./scripts/setup.sh or ./scripts/run.sh first."
  "$executable" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' ||
    fail "Python 3.10 or newer is required."
}

#!/usr/bin/env bash
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || exit 0
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  printf '%s\n' '{}'
  exit 0
fi

exec "$PYTHON_BIN" "$SCRIPT_DIR/log-session-start.py"
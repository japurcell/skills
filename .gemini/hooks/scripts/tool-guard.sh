#!/usr/bin/env bash

set -o pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="${SCRIPT_PATH%/*}"

if [[ "$SCRIPT_DIR" == "$SCRIPT_PATH" ]]; then
  SCRIPT_DIR="."
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  printf 'Tool Guardian skipped: required command not found: python3\n' >&2
  printf '%s\n' '{"decision":"allow","systemMessage":"Tool Guardian skipped: required command not found: python3."}'
  exit 0
fi

exec "$PYTHON_BIN" -I -S -B "$SCRIPT_DIR/tool-guard.py"

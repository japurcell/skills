#!/usr/bin/env bash
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || exit 0
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  printf 'Copilot/VS Code hook failure: Required command not found: python3\n' >&2
  printf '%s\n' '{"systemMessage":"Required skill context was NOT loaded. Required command not found: python3.","additionalContext":"Required skill context was NOT loaded.\n\nReason: Required command not found: python3.\n\nInstruction to agent: stop normal work, tell the user this hook failed, and ask them to fix the hook dependencies before proceeding."}'
  exit 0
fi

exec "$PYTHON_BIN" "$SCRIPT_DIR/load-required-skills.py"
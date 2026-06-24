#!/usr/bin/env bash
set -euo pipefail

emit_noop_json() {
  printf '%s\n' '{}'
  exit 0
}

warn_and_noop() {
  printf '%s\n' "$1" >&2
  emit_noop_json
}

command -v jq >/dev/null 2>&1 || warn_and_noop "log-before-agent: jq not found; skipping hook."

INPUT="$(cat)"

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$INPUT"; then
  warn_and_noop "log-before-agent: invalid JSON input; skipping hook."
fi

# Load audit library and initialize
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh" >/dev/null 2>&1 || warn_and_noop "log-before-agent: failed to load audit helpers; skipping hook."
audit_init >/dev/null 2>&1 || warn_and_noop "log-before-agent: failed to initialize audit logging; skipping hook."

session_id=$(jq -r '.session_id // empty' <<< "$INPUT")
timestamp=$(jq -r '.timestamp // empty' <<< "$INPUT")
prompt=$(jq -r '.prompt // empty' <<< "$INPUT")

# Log the tool usage attempt
audit_log_passive_event "$(basename "$0")" "[$timestamp] Prompt: $prompt, Session: $session_id"

emit_noop_json

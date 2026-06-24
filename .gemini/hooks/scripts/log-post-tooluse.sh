#!/usr/bin/env bash
set -euo pipefail

emit_allow_json() {
  printf '%s\n' '{"decision":"allow"}'
  exit 0
}

warn_and_allow() {
  printf '%s\n' "$1" >&2
  emit_allow_json
}

command -v jq >/dev/null 2>&1 || warn_and_allow "log-post-tooluse: jq not found; skipping hook."

INPUT="$(cat)"

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$INPUT"; then
  warn_and_allow "log-post-tooluse: invalid JSON input; skipping hook."
fi

# Load audit library and initialize
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh" >/dev/null 2>&1 || warn_and_allow "log-post-tooluse: failed to load audit helpers; skipping hook."
audit_init >/dev/null 2>&1 || warn_and_allow "log-post-tooluse: failed to initialize audit logging; skipping hook."

session_id=$(jq -r '.session_id // empty' <<< "$INPUT")
timestamp=$(jq -r '.timestamp // empty' <<< "$INPUT")
tool_name=$(jq -r '.tool_name // empty' <<< "$INPUT")
# Log the tool result
audit_log_passive_event "post-tooluse" "[$timestamp] Session: $session_id, Tool: $tool_name"

emit_allow_json

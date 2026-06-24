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

command -v jq >/dev/null 2>&1 || warn_and_noop "log-session-end: jq not found; skipping hook."

INPUT="$(cat)"

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$INPUT"; then
  warn_and_noop "log-session-end: invalid JSON input; skipping hook."
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load audit library and initialize
source "$SCRIPT_DIR/audit.sh" >/dev/null 2>&1 || warn_and_noop "log-session-end: failed to load audit helpers; skipping hook."
audit_init >/dev/null 2>&1 || warn_and_noop "log-session-end: failed to initialize audit logging; skipping hook."

# Log session end event
SESSION_ID=$(jq -r '.session_id // empty' <<< "$INPUT")
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT")
HOOK_EVENT_NAME=$(jq -r '.hook_event_name // empty' <<< "$INPUT")
REASON=$(jq -r '.reason // empty' <<< "$INPUT")

audit_log_passive_event "$(basename "$0")" "[$TIMESTAMP] Reason: $REASON, Hook: $HOOK_EVENT_NAME, Session: $SESSION_ID"

emit_noop_json

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

command -v jq >/dev/null 2>&1 || warn_and_noop "log-session-start: jq not found; skipping hook."

INPUT="$(cat)"

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$INPUT"; then
  warn_and_noop "log-session-start: invalid JSON input; skipping hook."
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load libraries and initialize
source "$SCRIPT_DIR/audit.sh" >/dev/null 2>&1 || warn_and_noop "log-session-start: failed to load audit helpers; skipping hook."
audit_init >/dev/null 2>&1 || warn_and_noop "log-session-start: failed to initialize audit logging; skipping hook."

# Log session start event
SESSION_ID=$(jq -r '.session_id // empty' <<< "$INPUT")
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT")
HOOK_EVENT_NAME=$(jq -r '.hook_event_name // empty' <<< "$INPUT")
TRANSCRIPT_PATH=$(jq -r '.transcript_path // empty' <<< "$INPUT")
CWD=$(jq -r '.cwd // empty' <<< "$INPUT")

audit_log_passive_event "$(basename "$0")" "[$TIMESTAMP] Transcript: $TRANSCRIPT_PATH, Hook: $HOOK_EVENT_NAME, CWD: $CWD, Session: $SESSION_ID"

emit_noop_json
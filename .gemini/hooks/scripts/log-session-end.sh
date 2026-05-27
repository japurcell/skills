#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load audit library and initialize
source "$SCRIPT_DIR/audit.sh"
audit_init

# Log session end event
SESSION_ID=$(jq -r '.session_id // empty' <<< "$INPUT")
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT")
HOOK_EVENT_NAME=$(jq -r '.hook_event_name // empty' <<< "$INPUT")
REASON=$(jq -r '.reason // empty' <<< "$INPUT")

audit_log_event "$(basename "$0")" "[$TIMESTAMP] Reason: $REASON, Hook: $HOOK_EVENT_NAME, Session: $SESSION_ID"

echo '{}'

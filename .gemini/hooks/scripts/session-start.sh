#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load libraries and initialize
source "$SCRIPT_DIR/audit.sh"
source "$SCRIPT_DIR/startup-context.sh"
audit_init

# Log session start event
SESSION_ID=$(jq -r '.session_id // empty' <<< "$INPUT")
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT")
HOOK_EVENT_NAME=$(jq -r '.hook_event_name // empty' <<< "$INPUT")
CWD=$(jq -r '.cwd // empty' <<< "$INPUT")

audit_log_event "$(basename "$0")" "[$TIMESTAMP] Hook: $HOOK_EVENT_NAME, CWD: $CWD, Session: $SESSION_ID"

# Emit startup context
CONTEXT="$(read_startup_additional_context "$HOOK_DIR/references/agent-start-context.json")"
JSON="$(emit_startup_context_payload "$CONTEXT" "$HOOK_EVENT_NAME")"

echo "$JSON"
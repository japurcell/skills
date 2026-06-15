#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"

if ! echo "$INPUT" | jq empty 2>/dev/null; then
  echo "Invalid JSON input" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load libraries and initialize
source "$SCRIPT_DIR/audit.sh"
audit_init

# Log session start event
SESSION_ID=$(jq -r '.session_id // empty' <<< "$INPUT")
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT")
HOOK_EVENT_NAME=$(jq -r '.hook_event_name // empty' <<< "$INPUT")
TRANSCRIPT_PATH=$(jq -r '.transcript_path // empty' <<< "$INPUT")
CWD=$(jq -r '.cwd // empty' <<< "$INPUT")

audit_log_event "$(basename "$0")" "[$TIMESTAMP] Transcript: $TRANSCRIPT_PATH, Hook: $HOOK_EVENT_NAME, CWD: $CWD, Session: $SESSION_ID"

echo '{}'
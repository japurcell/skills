#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"

require_cmd jq

INPUT="$(cat)"
SESSION_ID=$(jq -r '.sessionId // .session_id // empty' <<< "$INPUT") || { SESSION_ID=""; }
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT") || { TIMESTAMP=""; }
TOOL_NAME=$(jq -r '.toolName // .tool_name // empty' <<< "$INPUT")
TOOL_ARGS=$(jq -r '.toolArgs // .tool_input // empty' <<< "$INPUT")
ERROR_MESSAGE=$(jq -r '.error // empty' <<< "$INPUT")

audit_init

audit_log_event \
  "$(basename "$0")" \
  "[$TIMESTAMP] Session: $SESSION_ID, Tool: $TOOL_NAME, Args: $TOOL_ARGS, Error: $ERROR_MESSAGE"

# Can provide recovery guidance via additionalContext, exit code 2

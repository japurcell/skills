#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"
TOOL_NAME=$(jq -r '.toolName // .tool_name // empty' <<< "$INPUT")
TOOL_ARGS=$(jq -r '.toolArgs // .tool_input // empty' <<< "$INPUT")
ERROR_MESSAGE=$(jq -r '.error // empty' <<< "$INPUT")

setup_audit_log

append_audit_line "$AUDIT_LOG" \
  "log-tooluse-failure.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, Tool: $TOOL_NAME, Args: $TOOL_ARGS, Error: $ERROR_MESSAGE"

# Can provide recovery guidance via additionalContext, exit code 2

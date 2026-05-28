#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"
CWD=$(jq -r '.cwd // empty' <<< "$INPUT")
TOOL_NAME=$(jq -r '.toolName // .tool_name // empty' <<< "$INPUT")
TOOL_ARGS=$(jq -r '.toolArgs // .tool_input // empty' <<< "$INPUT")
TOOL_RESULT=$(jq -r '.toolResult.textResultForLlm // .tool_result.text_result_for_llm // empty' <<< "$INPUT")

setup_audit_log

append_audit_line "$AUDIT_LOG" \
  "log-post-tooluse.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, Tool: $TOOL_NAME, Args: $TOOL_ARGS, CWD: $CWD, Result: $TOOL_RESULT"

# Can provide recovery guidance via additionalContext, exit code 2

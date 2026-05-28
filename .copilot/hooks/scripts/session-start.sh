#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"
SOURCE=$(jq -r '.source // empty' <<< "$INPUT")
INITIAL_PROMPT=$(jq -r '.initialPrompt // .initial_prompt // empty' <<< "$INPUT")

setup_audit_log

append_audit_line "$AUDIT_LOG" \
  "session-start.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Source: $SOURCE, \
    Initial Prompt: $INITIAL_PROMPT"

if [[ ! -f "$STARTUP_CONTEXT_LIB" ]]; then
  echo "Missing startup context library: $STARTUP_CONTEXT_LIB" >&2
  exit 1
fi
source "$STARTUP_CONTEXT_LIB"

CONTEXT="$(read_startup_additional_context "$HOOK_DIR/references/agent-start-context.json")"
emit_startup_context_payload "$INPUT" "SessionStart" "$CONTEXT"

# Optional — cannot block creation. This also provides fallback context for VS Code
# child sessions if a runtime does not emit SubagentStart for runSubagent.

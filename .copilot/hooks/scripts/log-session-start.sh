#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"

require_cmd jq

INPUT="$(cat)"
SESSION_ID=$(jq -r '.sessionId // .session_id // empty' <<< "$INPUT") || { SESSION_ID=""; }
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT") || { TIMESTAMP=""; }
SOURCE=$(jq -r '.source // empty' <<< "$INPUT")
INITIAL_PROMPT=$(jq -r '.initialPrompt // .initial_prompt // empty' <<< "$INPUT")

audit_init

audit_log_event \
  "$(basename "$0")" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Source: $SOURCE, \
    Initial Prompt: $INITIAL_PROMPT"

# Optional — cannot block creation. This also provides fallback context for VS Code
# child sessions if a runtime does not emit SubagentStart for runSubagent.

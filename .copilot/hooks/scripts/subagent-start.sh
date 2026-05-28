#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"
TRANSCRIPT_PATH=$(jq -r '.transcriptPath // .transcript_path // empty' <<< "$INPUT")
AGENT_NAME=$(jq -r '.agentName // .agent_name // .agent_type // empty' <<< "$INPUT")
AGENT_ID=$(jq -r '.agentId // .agent_id // empty' <<< "$INPUT")
AGENT_DISPLAY_NAME=$(jq -r '.agentDisplayName // .agent_display_name // empty' <<< "$INPUT")
AGENT_DESCRIPTION=$(jq -r '.agentDescription // .agent_description // empty' <<< "$INPUT")

setup_audit_log

append_audit_line "$AUDIT_LOG" \
  "subagent-start.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Transcript: $TRANSCRIPT_PATH, \
    Agent: $AGENT_NAME, \
    Agent ID: $AGENT_ID, \
    Display Name: $AGENT_DISPLAY_NAME, \
    Description: $AGENT_DESCRIPTION"

if [[ ! -f "$STARTUP_CONTEXT_LIB" ]]; then
  echo "Missing startup context library: $STARTUP_CONTEXT_LIB" >&2
  exit 1
fi
source "$STARTUP_CONTEXT_LIB"

CONTEXT="$(read_startup_additional_context "$HOOK_DIR/references/agent-start-context.json")"
emit_startup_context_payload "$INPUT" "SubagentStart" "$CONTEXT"

# Optional — cannot block creation. Copilot CLI and VS Code use this when
# SubagentStart fires; SessionStart remains the fallback for runtimes that omit it.

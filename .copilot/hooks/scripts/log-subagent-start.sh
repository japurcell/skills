#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"
TRANSCRIPT_PATH=$(jq -r '.transcriptPath // .transcript_path // empty' <<< "$INPUT")
AGENT_NAME=$(jq -r '.agentName // .agent_name // .agent_type // empty' <<< "$INPUT")
AGENT_ID=$(jq -r '.agentId // .agent_id // empty' <<< "$INPUT")
AGENT_DISPLAY_NAME=$(jq -r '.agentDisplayName // .agent_display_name // empty' <<< "$INPUT")
AGENT_DESCRIPTION=$(jq -r '.agentDescription // .agent_description // empty' <<< "$INPUT")

audit_init

audit_log_event \
  "$(basename "$0")" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Transcript: $TRANSCRIPT_PATH, \
    Agent: $AGENT_NAME, \
    Agent ID: $AGENT_ID, \
    Display Name: $AGENT_DISPLAY_NAME, \
    Description: $AGENT_DESCRIPTION"

# Optional — cannot block creation. Copilot CLI and VS Code use this when
# SubagentStart fires; SessionStart remains the fallback for runtimes that omit it.

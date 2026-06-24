#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"

require_cmd jq

INPUT="$(cat)"
SESSION_ID=$(jq -r '.sessionId // .session_id // empty' <<< "$INPUT") || { SESSION_ID=""; }
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT") || { TIMESTAMP=""; }
TRANSCRIPT_PATH=$(jq -r '.transcriptPath // .transcript_path // empty' <<< "$INPUT")
AGENT_NAME=$(jq -r '.agentName // .agent_name // empty' <<< "$INPUT")
AGENT_DISPLAY_NAME=$(jq -r '.agentDisplayName // .agent_display_name // empty' <<< "$INPUT")
STOP_REASON=$(jq -r '.stopReason // .stop_reason // empty' <<< "$INPUT")

audit_init

audit_log_event \
  "$(basename "$0")" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Transcript: $TRANSCRIPT_PATH, \
    Agent: $AGENT_NAME, \
    Display Name: $AGENT_DISPLAY_NAME, \
    Stop Reason: $STOP_REASON"

# { decision: "block|allow", reason: "prompt for the next turn when decision is block" }

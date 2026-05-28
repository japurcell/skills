#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"
TRANSCRIPT_PATH=$(jq -r '.transcriptPath // .transcript_path // empty' <<< "$INPUT")
AGENT_NAME=$(jq -r '.agentName // .agent_name // empty' <<< "$INPUT")
AGENT_DISPLAY_NAME=$(jq -r '.agentDisplayName // .agent_display_name // empty' <<< "$INPUT")
STOP_REASON=$(jq -r '.stopReason // .stop_reason // empty' <<< "$INPUT")

setup_audit_log

append_audit_line "$AUDIT_LOG" \
  "log-subagent-stop.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Transcript: $TRANSCRIPT_PATH, \
    Agent: $AGENT_NAME, \
    Display Name: $AGENT_DISPLAY_NAME, \
    Stop Reason: $STOP_REASON"

# { decision: "block|allow", reason: "prompt for the next turn when decision is block" }

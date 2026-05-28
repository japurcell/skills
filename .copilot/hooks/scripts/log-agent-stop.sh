#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"
TRANSCRIPT_PATH=$(jq -r '.transcriptPath // .transcript_path // empty' <<< "$INPUT")
STOP_REASON=$(jq -r '.stopReason // .stop_reason // empty' <<< "$INPUT")

setup_audit_log

append_audit_line "$AUDIT_LOG" \
  "log-agent-stop.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Transcript: $TRANSCRIPT_PATH, \
    Stop Reason: $STOP_REASON"

# { decision: "block|allow", reason: "prompt for the next turn when decision is block" }

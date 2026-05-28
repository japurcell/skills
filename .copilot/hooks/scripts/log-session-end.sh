#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"
REASON=$(jq -r '.reason // empty' <<< "$INPUT")

setup_audit_log

append_audit_line "$AUDIT_LOG" \
  "log-session-end.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, Reason: $REASON"

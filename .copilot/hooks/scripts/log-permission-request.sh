#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"

setup_audit_log

append_audit_line "$AUDIT_LOG" \
  "log-permission-request.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, Input: $INPUT"

# { behavior: "allow|deny", message: "reason given to LLM for denying", interrupt: true|false }

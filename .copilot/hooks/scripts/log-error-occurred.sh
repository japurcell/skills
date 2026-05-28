#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"
ERROR_MESSAGE=$(jq -r '.error.message // empty' <<< "$INPUT")
ERROR_NAME=$(jq -r '.error.name // empty' <<< "$INPUT")
ERROR_STACK=$(jq -r '.error.stack // empty' <<< "$INPUT")
ERROR_CONTEXT=$(jq -r '.errorContext // .error_context // empty' <<< "$INPUT")
RECOVERABLE=$(jq -r '.recoverable // empty' <<< "$INPUT")

setup_audit_log

append_audit_line "$AUDIT_LOG" \
  "log-error-occurred.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Error Message: $ERROR_MESSAGE, \
    Error Name: $ERROR_NAME, \
    Error Stack: $ERROR_STACK, \
    Error Context: $ERROR_CONTEXT, \
    Recoverable: $RECOVERABLE"

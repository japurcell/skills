#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"

require_cmd jq

INPUT="$(cat)"
SESSION_ID=$(jq -r '.sessionId // .session_id // empty' <<< "$INPUT") || { SESSION_ID=""; }
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT") || { TIMESTAMP=""; }
ERROR_MESSAGE=$(jq -r '.error.message // empty' <<< "$INPUT")
ERROR_NAME=$(jq -r '.error.name // empty' <<< "$INPUT")
ERROR_STACK=$(jq -r '.error.stack // empty' <<< "$INPUT")
ERROR_CONTEXT=$(jq -r '.errorContext // .error_context // empty' <<< "$INPUT")
RECOVERABLE=$(jq -r '.recoverable // empty' <<< "$INPUT")

audit_init

audit_log_event \
  "$(basename "$0")" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Error Message: $ERROR_MESSAGE, \
    Error Name: $ERROR_NAME, \
    Error Stack: $ERROR_STACK, \
    Error Context: $ERROR_CONTEXT, \
    Recoverable: $RECOVERABLE"

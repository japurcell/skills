#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"

require_cmd jq

INPUT="$(cat)"
SESSION_ID=$(jq -r '.sessionId // .session_id // empty' <<< "$INPUT") || { SESSION_ID=""; }
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT") || { TIMESTAMP=""; }
MESSAGE=$(jq -r '.message // empty' <<< "$INPUT")
TITLE=$(jq -r '.title // empty' <<< "$INPUT")
NOTIFICATION_TYPE=$(jq -r '.notificationType // .notification_type // empty' <<< "$INPUT")

audit_init

audit_log_event \
  "$(basename "$0")" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Title: $TITLE, \
    Message: $MESSAGE, \
    Notification Type: $NOTIFICATION_TYPE"

# { "additionalContext": "injected into session as user message" }

#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"
MESSAGE=$(jq -r '.message // empty' <<< "$INPUT")
TITLE=$(jq -r '.title // empty' <<< "$INPUT")
NOTIFICATION_TYPE=$(jq -r '.notificationType // .notification_type // empty' <<< "$INPUT")

setup_audit_log

append_audit_line "$AUDIT_LOG" \
  "log-notification.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Title: $TITLE, \
    Message: $MESSAGE, \
    Notification Type: $NOTIFICATION_TYPE"

# { "additionalContext": "injected into session as user message" }

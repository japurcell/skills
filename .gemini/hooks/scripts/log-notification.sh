#!/usr/bin/env bash
set -euo pipefail

emit_noop_json() {
  printf '%s\n' '{}'
  exit 0
}

warn_and_noop() {
  printf '%s\n' "$1" >&2
  emit_noop_json
}

command -v jq >/dev/null 2>&1 || warn_and_noop "log-notification: jq not found; skipping hook."

INPUT="$(cat)"

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$INPUT"; then
  warn_and_noop "log-notification: invalid JSON input; skipping hook."
fi

# Initialize auditing (preserves $HOME/.gemini/ paths)
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh" >/dev/null 2>&1 || warn_and_noop "log-notification: failed to load audit helpers; skipping hook."
audit_init >/dev/null 2>&1 || warn_and_noop "log-notification: failed to initialize audit logging; skipping hook."

# Log notification event from Gemini
# session_id is the primary identifier; capture type, message, and details
audit_log_passive_event "$(basename "$0")" "$(jq -r '
  [
    "session_id: \(.session_id // empty)",
    "notification_type: \(.notification_type // empty)",
    "message: \(.message // empty)",
    "details: \(.details // {} | tojson)"
  ] | join(", ")
' <<<"$INPUT")"

emit_noop_json
#!/usr/bin/env bash
set -euo pipefail

# Initialize auditing (preserves $HOME/.gemini/ paths)
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"
audit_init

# Log notification event from Gemini
# session_id is the primary identifier; capture type, message, and details
audit_log_event "$(basename "$0")" "$(jq -r '
  [
    "session_id: \(.session_id // empty)",
    "notification_type: \(.notification_type // empty)",
    "message: \(.message // empty)",
    "details: \(.details // {} | tojson)"
  ] | join(", ")
')"

echo '{}'
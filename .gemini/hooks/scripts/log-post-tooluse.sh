#!/usr/bin/env bash
set -euo pipefail

# Load audit library and initialize
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"
audit_init

payload=$(cat)
session_id=$(jq -r '.session_id // empty' <<< "$payload")
timestamp=$(jq -r '.timestamp // empty' <<< "$payload")
tool_name=$(jq -r '.tool_name // empty' <<< "$payload")
tool_result=$(jq -r '.tool_response.llmContent // .tool_response.returnDisplay // .tool_response.error // empty' <<< "$payload")

# Log the tool result
audit_log_event "post-tooluse" "[$timestamp] Session: $session_id, Tool: $tool_name"

echo '{"decision": "allow"}'

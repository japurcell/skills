#!/usr/bin/env bash
set -euo pipefail

# Load audit library and initialize
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"
audit_init

payload=$(cat)
session_id=$(jq -r '.session_id // empty' <<< "$payload")
timestamp=$(jq -r '.timestamp // empty' <<< "$payload")
prompt=$(jq -r '.prompt // empty' <<< "$payload")

# Log the tool usage attempt
audit_log_event "$(basename "$0")" "[$timestamp] Prompt: $prompt, Session: $session_id"

echo '{}'

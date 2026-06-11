#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"
audit_init

payload="$(cat)"

session_id="$(jq -r '.session_id // empty' <<<"$payload")"
timestamp="$(jq -r '.timestamp // empty' <<<"$payload")"
tool_name="$(jq -r '.tool_name // empty' <<<"$payload")"
tool_args="$(jq -c '.tool_input // empty' <<<"$payload")"

audit_log_event "$(basename "$0")" \
  "[$timestamp] Session: $session_id, Tool: $tool_name, Args: $tool_args" >&2

exec rtk hook gemini <<<"$payload"
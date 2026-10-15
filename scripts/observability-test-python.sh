#!/usr/bin/env bash

set -euo pipefail

python_bin="$(command -v python3)"
script_path="${1:-}"

if [[ "${OBS_TEST_PROVIDER:-}" != "copilot" || "${script_path##*/}" != "send-event.py" ]]; then
  exec "$python_bin" "$@"
fi

payload="$(cat)"
if adapted_payload="$(jq -c '
  if type == "object" then
    (if has("session_id") then .sessionId = (.sessionId // .session_id) | del(.session_id) else . end)
    | del(.hook_event_name)
  else . end
' <<<"$payload" 2>/dev/null)"; then
  exec "$python_bin" "$@" <<<"$adapted_payload"
fi

exec "$python_bin" "$@" <<<"$payload"

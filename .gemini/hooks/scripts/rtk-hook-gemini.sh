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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_LIB="$SCRIPT_DIR/audit.sh"

command -v jq >/dev/null 2>&1 || warn_and_noop "rtk-hook-gemini: jq not found; skipping hook."
command -v rtk >/dev/null 2>&1 || warn_and_noop "rtk-hook-gemini: rtk not found; skipping hook."
[[ -r "$AUDIT_LIB" ]] || warn_and_noop "rtk-hook-gemini: audit library unavailable; skipping hook."
source "$AUDIT_LIB" >/dev/null 2>&1 || warn_and_noop "rtk-hook-gemini: failed to load audit helpers; skipping hook."
audit_init >/dev/null 2>&1 || warn_and_noop "rtk-hook-gemini: failed to initialize audit logging; skipping hook."

payload="$(cat)"

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$payload"; then
  warn_and_noop "rtk-hook-gemini: invalid JSON input; skipping hook."
fi

session_id="$(jq -r '.session_id // empty' <<<"$payload")"
timestamp="$(jq -r '.timestamp // empty' <<<"$payload")"
tool_name="$(jq -r '.tool_name // empty' <<<"$payload")"
tool_args="$(jq -c '.tool_input // empty' <<<"$payload")"

audit_log_event "$(basename "$0")" \
  "[$timestamp] Session: $session_id, Tool: $tool_name, Args: $tool_args" \
  >/dev/null 2>&1 || warn_and_noop "rtk-hook-gemini: failed to write audit event; skipping hook."

rewritten_output="$(
  rtk hook gemini <<<"$payload"
)" || warn_and_noop "rtk-hook-gemini: rtk rewrite failed; leaving tool input unchanged."

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$rewritten_output"; then
  warn_and_noop "rtk-hook-gemini: rtk rewrite returned invalid JSON; leaving tool input unchanged."
fi

printf '%s\n' "$rewritten_output"
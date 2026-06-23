#!/usr/bin/env bash

set -euo pipefail

INPUT="$(cat)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
AUDIT_LIB="$SCRIPT_DIR/audit.sh"

emit_response() {
  local decision="$1"
  local reason="${2:-}"
  local system_message="${3:-}"

  jq -nc \
    --arg decision "$decision" \
    --arg reason "$reason" \
    --arg system_message "$system_message" '
      { decision: $decision, suppressOutput: true } +
      (if $reason != "" then { reason: $reason } else {} end) +
      (if $system_message != "" then { systemMessage: $system_message } else {} end)
    '
  exit 0
}

emit_allow_without_jq() {
  printf 'Hedge Detector skipped: required command not found: jq\n' >&2
  printf '%s\n' '{"decision":"allow","systemMessage":"Hedge Detector skipped: required command not found: jq.","suppressOutput":true}'
  exit 0
}

command -v jq >/dev/null 2>&1 || emit_allow_without_jq

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$INPUT"; then
  emit_response "allow" "" "Hedge Detector skipped: invalid hook input JSON."
fi

if [[ ! -r "$AUDIT_LIB" ]]; then
  emit_response "allow" "" "Hedge Detector skipped: audit library unavailable."
fi

# shellcheck source=/dev/null
source "$AUDIT_LIB" >/dev/null 2>&1 || emit_response "allow" "" "Hedge Detector skipped: failed to load audit library."

audit_init >/dev/null 2>&1 || emit_response "allow" "" "Hedge Detector skipped: audit initialization failed."

SESSION_ID="$(jq -r '.session_id // empty' <<<"$INPUT" 2>/dev/null || true)"
TIMESTAMP="$(jq -r '.timestamp // empty' <<<"$INPUT" 2>/dev/null || true)"
HOOK_EVENT_NAME="$(jq -r '.hook_event_name // empty' <<<"$INPUT" 2>/dev/null || true)"
PROMPT="$(jq -r '.prompt // empty' <<<"$INPUT" 2>/dev/null || true)"
PROMPT_RESPONSE="$(jq -r '.prompt_response // empty' <<<"$INPUT" 2>/dev/null || true)"
STOP_HOOK_ACTIVE="$(jq -r '.stop_hook_active // false' <<<"$INPUT" 2>/dev/null || true)"

CERTAINTY_REGEX='\b(definitely|certainly|clearly|obviously|guarantee(d|s)?|undeniably|without doubt|no doubt|always|never)\b'
REVISION_REASON="Strong certainty detected without explicit support. Revise final answer with an 'Evidence:' section grounded in files, tools, or outputs you used, plus an 'Uncertainty:' section naming remaining assumptions or limits."

log_decision() {
  local decision="$1"
  local note="${2:-}"
  audit_log_event \
    "$(basename "$0")" \
    "[$TIMESTAMP] Hook: $HOOK_EVENT_NAME, Session: $SESSION_ID, Prompt: $PROMPT, Decision: $decision${note:+, Note: $note}" \
    >/dev/null 2>&1 || true
}

has_explicit_support() {
  local content="$1"
  printf '%s' "$content" | grep -qiE '(^|[[:space:]])Evidence:' &&
    printf '%s' "$content" | grep -qiE '(^|[[:space:]])Uncertainty:'
}

contains_strong_certainty() {
  local content="$1"
  printf '%s' "$content" | grep -qiE "$CERTAINTY_REGEX"
}

if [[ "$HOOK_EVENT_NAME" != "AfterAgent" ]]; then
  log_decision "allow" "unsupported event"
  emit_response "allow"
fi

if [[ -z "$PROMPT_RESPONSE" ]]; then
  log_decision "allow" "missing prompt_response"
  emit_response "allow"
fi

if [[ "$STOP_HOOK_ACTIVE" == "true" || "$STOP_HOOK_ACTIVE" == "True" ]]; then
  log_decision "allow" "retry active; avoiding loop"
  emit_response "allow"
fi

if ! contains_strong_certainty "$PROMPT_RESPONSE" || has_explicit_support "$PROMPT_RESPONSE"; then
  log_decision "allow"
  emit_response "allow"
fi

log_decision "deny"
emit_response "deny" "$REVISION_REASON" "$REVISION_REASON"

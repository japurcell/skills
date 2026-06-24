#!/usr/bin/env bash

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"

require_cmd jq

INPUT="$(cat)"

emit_decision() {
  local decision="$1"
  local reason="${2:-}"

  jq -nc \
    --arg decision "$decision" \
    --arg reason "$reason" '
      { decision: $decision } +
      (if $reason == "" then {} else { reason: $reason } end)
    '
  exit 0
}

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$INPUT"; then
  emit_decision "allow"
fi

SESSION_ID=$(jq -r '.sessionId // .session_id // empty' <<< "$INPUT") || { SESSION_ID=""; }
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT") || { TIMESTAMP=""; }

TRANSCRIPT_PATH="$(jq -r '.transcriptPath // .transcript_path // empty' <<<"$INPUT")"
STOP_REASON="$(jq -r '.stopReason // .stop_reason // empty' <<<"$INPUT")"

audit_init

CERTAINTY_REGEX='\b(definitely|certainly|clearly|obviously|guarantee(d|s)?|undeniably|without doubt|no doubt|always|never)\b'
REVISION_REASON="Strong certainty detected without explicit support. Revise final answer with an 'Evidence:' section grounded in files, tools, or outputs you used, plus an 'Uncertainty:' section naming remaining assumptions or limits."
STATE_ROOT="${HEDGE_DETECTOR_STATE_DIR:-${COPILOT_HOME:-$HOME/.copilot}/hooks/hedge-detector}"

sanitize_key() {
  printf '%s' "${1:-unknown}" | tr -c '[:alnum:]._-' '_'
}

extract_latest_assistant_message() {
  local transcript_path="${1:?transcript path required}"
  local line
  local parsed_line
  local latest='{}'

  while IFS= read -r line; do
    parsed_line="$(printf '%s\n' "$line" | sed -E 's/^[[:space:]]*[0-9]+\.[[:space:]]+//')"
    [[ "$parsed_line" == \{* ]] || continue

    if candidate="$(
      jq -rc '
        select(.type == "assistant.message") |
        {
          content: (.data.content // ""),
          turnId: (.data.turnId // .data.turn_id // "")
        }
      ' <<<"$parsed_line" 2>/dev/null
    )"; then
      [[ -n "$candidate" ]] && latest="$candidate"
    fi
  done <"$transcript_path"

  printf '%s\n' "$latest"
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

log_decision() {
  local decision="$1"
  local turn_id="$2"
  local note="${3:-}"

  audit_log_event \
    "$(basename "$0")" \
    "[$TIMESTAMP] Session: $SESSION_ID, Transcript: $TRANSCRIPT_PATH, Stop Reason: $STOP_REASON, Turn: $turn_id, Decision: $decision${note:+, Note: $note}"
}

if [[ -z "$TRANSCRIPT_PATH" || ! -r "$TRANSCRIPT_PATH" ]]; then
  log_decision "allow" "unknown" "transcript unavailable"
  emit_decision "allow"
fi

LATEST_MESSAGE="$(extract_latest_assistant_message "$TRANSCRIPT_PATH")"
MESSAGE_CONTENT="$(jq -r '.content // empty' <<<"$LATEST_MESSAGE")"
TURN_ID="$(jq -r '.turnId // empty' <<<"$LATEST_MESSAGE")"

if [[ -z "$MESSAGE_CONTENT" ]]; then
  log_decision "allow" "${TURN_ID:-unknown}" "no assistant message found"
  emit_decision "allow"
fi

if ! contains_strong_certainty "$MESSAGE_CONTENT" || has_explicit_support "$MESSAGE_CONTENT"; then
  log_decision "allow" "${TURN_ID:-unknown}"
  emit_decision "allow"
fi

mkdir -p "$STATE_ROOT"
STATE_FILE="$STATE_ROOT/$(sanitize_key "${SESSION_ID:-session}").$(sanitize_key "${TURN_ID:-turn}").json"

if [[ -f "$STATE_FILE" ]] && [[ "$(jq -r '.content // empty' "$STATE_FILE")" == "$MESSAGE_CONTENT" ]]; then
  log_decision "allow" "${TURN_ID:-unknown}" "repeat detected; avoiding loop"
  emit_decision "allow"
fi

jq -nc --arg content "$MESSAGE_CONTENT" '{content: $content}' >"$STATE_FILE"
log_decision "block" "${TURN_ID:-unknown}"
emit_decision "block" "$REVISION_REASON"

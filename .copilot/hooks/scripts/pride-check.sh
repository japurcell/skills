#!/usr/bin/env bash

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"

require_cmd jq
require_cmd flock

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

parse_input "$INPUT"

TRANSCRIPT_PATH="$(jq -r '.transcriptPath // .transcript_path // empty' <<<"$INPUT")"
STOP_REASON="$(jq -r '.stopReason // .stop_reason // empty' <<<"$INPUT")"

audit_init

STATE_ROOT="${PRIDE_CHECK_STATE_DIR:-${COPILOT_HOME:-$HOME/.copilot}/hooks/pride-check}"
EDIT_TOOL_REGEX='^(apply_patch|create|edit|str_replace_editor)$'
REVISION_REASON=$'Pride Check failed. This session changed code, so revise final answer with this exact section:\nPride Check:\n- Senior respect: concrete maintainability judgment tied to files or functions you changed.\n- Self-explaining: how naming or control flow explains itself now.\n- Edge cases: boundary, failure, or empty-state handling you covered.\n- Simplicity: why this is right level of abstraction without extra complexity.\n- Codebase better: adjacent cleanup, tests, docs, or dead-code removal you actually completed.\nIf needed, invoke the `pride-check` skill before revising.'

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

session_requires_pride_check() {
  local transcript_path="${1:?transcript path required}"
  local line
  local parsed_line
  local tool_name
  local assistant_content
  local dirty=0

  while IFS= read -r line; do
    parsed_line="$(printf '%s\n' "$line" | sed -E 's/^[[:space:]]*[0-9]+\.[[:space:]]+//')"
    [[ "$parsed_line" == \{* ]] || continue

    tool_name="$(
      jq -r '
        if .type == "tool.execution_start"
        then (.data.toolName // "")
        else empty
        end
      ' <<<"$parsed_line" 2>/dev/null
    )"

    if [[ -n "$tool_name" && "$tool_name" =~ $EDIT_TOOL_REGEX ]]; then
      dirty=1
      continue
    fi

    assistant_content="$(
      jq -r '
        if .type == "assistant.message"
        then (.data.content // "")
        else empty
        end
      ' <<<"$parsed_line" 2>/dev/null
    )"

    if [[ -n "$assistant_content" ]] && has_pride_check "$assistant_content"; then
      dirty=0
    fi
  done <"$transcript_path"

  [[ "$dirty" -eq 1 ]]
}

has_labeled_line() {
  local content="${1:-}"
  local label="${2:?label required}"

  printf '%s\n' "$content" | grep -qiE "^[[:space:]]*[-*]?[[:space:]]*${label}:[[:space:]]*[^[:space:]].{5,}$"
}

has_pride_check() {
  local content="${1:-}"

  printf '%s\n' "$content" | grep -qiE '^[[:space:]]*(\*\*)?Pride Check:(\*\*)?[[:space:]]*$' &&
    has_labeled_line "$content" 'Senior respect' &&
    has_labeled_line "$content" 'Self-explaining' &&
    has_labeled_line "$content" 'Edge cases' &&
    has_labeled_line "$content" 'Simplicity' &&
    has_labeled_line "$content" 'Codebase better'
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

if [[ -z "$MESSAGE_CONTENT" || -z "$TURN_ID" ]]; then
  log_decision "allow" "${TURN_ID:-unknown}" "no assistant message found"
  emit_decision "allow"
fi

mkdir -p "$STATE_ROOT"
STATE_FILE="$STATE_ROOT/$(sanitize_key "${SESSION_ID:-session}").json"

if ! session_requires_pride_check "$TRANSCRIPT_PATH"; then
  rm -f "$STATE_FILE"
  log_decision "allow" "$TURN_ID" "no outstanding session changes requiring Pride Check"
  emit_decision "allow"
fi

if has_pride_check "$MESSAGE_CONTENT"; then
  rm -f "$STATE_FILE"
  log_decision "allow" "$TURN_ID"
  emit_decision "allow"
fi

if [[ -f "$STATE_FILE" ]] && [[ "$(jq -r '.content // empty' "$STATE_FILE")" == "$MESSAGE_CONTENT" ]]; then
  log_decision "allow" "$TURN_ID" "repeat detected; avoiding loop"
  emit_decision "allow"
fi

jq -nc --arg content "$MESSAGE_CONTENT" '{content: $content}' >"$STATE_FILE"
log_decision "block" "$TURN_ID"
emit_decision "block" "$REVISION_REASON"

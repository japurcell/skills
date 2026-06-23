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
  printf 'Pride Check skipped: required command not found: jq\n' >&2
  printf '%s\n' '{"decision":"allow","systemMessage":"Pride Check skipped: required command not found: jq.","suppressOutput":true}'
  exit 0
}

command -v jq >/dev/null 2>&1 || emit_allow_without_jq

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$INPUT"; then
  emit_response "allow" "" "Pride Check skipped: invalid hook input JSON."
fi

if [[ ! -r "$AUDIT_LIB" ]]; then
  emit_response "allow" "" "Pride Check skipped: audit library unavailable."
fi

# shellcheck source=/dev/null
source "$AUDIT_LIB" >/dev/null 2>&1 || emit_response "allow" "" "Pride Check skipped: failed to load audit library."

audit_init >/dev/null 2>&1 || emit_response "allow" "" "Pride Check skipped: audit initialization failed."

SESSION_ID="$(jq -r '.session_id // empty' <<<"$INPUT" 2>/dev/null || true)"
TIMESTAMP="$(jq -r '.timestamp // empty' <<<"$INPUT" 2>/dev/null || true)"
HOOK_EVENT_NAME="$(jq -r '.hook_event_name // empty' <<<"$INPUT" 2>/dev/null || true)"
PROMPT="$(jq -r '.prompt // empty' <<<"$INPUT" 2>/dev/null || true)"
PROMPT_RESPONSE="$(jq -r '.prompt_response // empty' <<<"$INPUT" 2>/dev/null || true)"
STOP_HOOK_ACTIVE="$(jq -r '.stop_hook_active // false' <<<"$INPUT" 2>/dev/null || true)"
TRANSCRIPT_PATH="$(jq -r '.transcript_path // empty' <<<"$INPUT" 2>/dev/null || true)"

EDIT_TOOL_REGEX='^(replace|write_file)$'
REVISION_REASON=$'Pride Check failed. This session changed code, so revise final answer with this exact section:\nPride Check:\n- Senior respect: concrete maintainability judgment tied to files or functions you changed.\n- Self-explaining: how naming or control flow explains itself now.\n- Edge cases: boundary, failure, or empty-state handling you covered.\n- Simplicity: why this is right level of abstraction without extra complexity.\n- Codebase better: adjacent cleanup, tests, docs, or dead-code removal you actually completed.\nIf needed, invoke the `pride-check` skill before revising.'

log_decision() {
  local decision="$1"
  local note="${2:-}"
  audit_log_event \
    "$(basename "$0")" \
    "[$TIMESTAMP] Hook: $HOOK_EVENT_NAME, Session: $SESSION_ID, Prompt: $PROMPT, Transcript: $TRANSCRIPT_PATH, Decision: $decision${note:+, Note: $note}" \
    >/dev/null 2>&1 || true
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

message_content_text() {
  local message_json="${1:?message json required}"

  jq -r '
    [
      .content[]? |
      if type == "string" then .
      elif type == "object" then (.text // empty)
      else empty
      end
    ] | join("\n")
  ' <<<"$message_json" 2>/dev/null
}

session_requires_pride_check() {
  local transcript_path="${1:?transcript path required}"
  local message_json
  local tool_name
  local content
  local dirty=0

  while IFS= read -r message_json; do
    while IFS= read -r tool_name; do
      if [[ -n "$tool_name" && "$tool_name" =~ $EDIT_TOOL_REGEX ]]; then
        dirty=1
      fi
    done < <(jq -r '.toolCalls[]?.name // empty' <<<"$message_json" 2>/dev/null)

    content="$(message_content_text "$message_json")"
    if [[ -n "$content" ]] && has_pride_check "$content"; then
      dirty=0
    fi
  done < <(
    jq -rc '
      if type == "object" and ((.messages // null) | type) == "array" then
        .messages[]?
      elif type == "array" then
        .[]?
      else
        empty
      end
    ' "$transcript_path" 2>/dev/null
  )

  [[ "$dirty" -eq 1 ]]
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

if [[ -z "$TRANSCRIPT_PATH" || ! -r "$TRANSCRIPT_PATH" ]]; then
  log_decision "allow" "transcript unavailable"
  emit_response "allow"
fi

if ! session_requires_pride_check "$TRANSCRIPT_PATH"; then
  log_decision "allow" "no outstanding session changes requiring Pride Check"
  emit_response "allow"
fi

if has_pride_check "$PROMPT_RESPONSE"; then
  log_decision "allow"
  emit_response "allow"
fi

log_decision "deny"
emit_response "deny" "$REVISION_REASON" "$REVISION_REASON"

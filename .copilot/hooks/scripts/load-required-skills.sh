#!/usr/bin/env bash
set -o pipefail

# GitHub Copilot CLI / VS Code user-level hook.
#
# Intended only for:
# - Copilot CLI: sessionStart, subagentStart
# - VS Code: SessionStart, SubagentStart
#
# Contract:
# - stdin: hook input JSON
# - stdout: one final JSON object only
# - stderr: logs/errors only
# - exit 0: stdout is parsed as hook output JSON

INPUT=""
SESSION_ID=""
EVENT_NAME=""
SCRIPT_NAME="$(basename "$0")"

static_fail_no_jq() {
  printf 'Copilot/VS Code hook failure: Required command not found: jq\n' >&2

  # Cannot safely emit dynamic JSON without jq, so keep this static.
  printf '%s\n' '{"systemMessage":"Required skill context was NOT loaded. Required command not found: jq.","additionalContext":"Required skill context was NOT loaded.\n\nReason: Required command not found: jq.\n\nInstruction to agent: stop normal work, tell the user this hook failed, and ask them to fix the hook dependencies before proceeding."}'

  exit 0
}

command -v jq >/dev/null 2>&1 || static_fail_no_jq

sanitize_log_field() {
  printf '%s' "${1:-}" | tr '\r\n\t' '   '
}

trim_ws() {
  local s="${1:-}"

  # Trim leading whitespace.
  s="${s#"${s%%[![:space:]]*}"}"

  # Trim trailing whitespace.
  s="${s%"${s##*[![:space:]]}"}"

  printf '%s' "$s"
}

append_unique_skill_file() {
  local skill_file="${1:-}"
  local existing=""

  [[ -n "$skill_file" ]] || return 0

  for existing in "${REQUIRED_SKILL_FILES[@]}"; do
    if [[ "$existing" == "$skill_file" ]]; then
      return 0
    fi
  done

  REQUIRED_SKILL_FILES+=("$skill_file")
}

resolve_skill_file_path() {
  local skill_file="${1:-}"

  [[ -n "$skill_file" ]] || fail_with_context "Skill file path is empty"

  # Support ~/path in env-provided values.
  if [[ "$skill_file" == "~/"* ]]; then
    [[ -n "${HOME:-}" ]] || fail_with_context "Cannot expand ~/: HOME is not set"
    skill_file="$HOME/${skill_file#~/}"

  # Treat non-absolute paths as relative to SKILLS_DIR.
  elif [[ "$skill_file" != /* ]]; then
    skill_file="$SKILLS_DIR/$skill_file"
  fi

  printf '%s' "$skill_file"
}

merge_env_skill_files() {
  local raw="${1:-}"
  local normalized=""
  local item=""
  local resolved=""

  # AGENTS_REQUIRED_SKILL_FILES is optional.
  # If it is unset or empty, do nothing.
  [[ -n "$raw" ]] || return 0

  # Accept newline-, colon-, or comma-separated values.
  normalized="$raw"
  normalized="${normalized//$'\r'/$'\n'}"
  normalized="${normalized//:/$'\n'}"
  normalized="${normalized//,/$'\n'}"

  while IFS= read -r item || [[ -n "$item" ]]; do
    item="$(trim_ws "$item")"
    [[ -n "$item" ]] || continue

    resolved="$(resolve_skill_file_path "$item")"
    append_unique_skill_file "$resolved"
  done <<<"$normalized"
}

emit_output() {
  local message="${1:-}"
  local is_failure="${2:-0}"

  if [[ "$EVENT_NAME" == "SessionStart" || "$EVENT_NAME" == "SubagentStart" ]]; then
    # VS Code format. Include top-level additionalContext too; VS Code should
    # use hookSpecificOutput, while Copilot-compatible readers can use top-level.
    jq -nc \
      --arg ev "$EVENT_NAME" \
      --arg msg "$message" \
      --argjson is_failure "$is_failure" '
        {
          systemMessage:
            (
              if $is_failure
              then "Required skill context was NOT loaded."
              else empty
              end
            ),
          additionalContext: $msg,
          hookSpecificOutput: {
            hookEventName: $ev,
            additionalContext: $msg
          }
        }
      '
  else
    # Copilot CLI lower-camelcase sessionStart/subagentStart format.
    jq -nc \
      --arg msg "$message" \
      --argjson is_failure "$is_failure" '
        {
          systemMessage:
            (
              if $is_failure
              then "Required skill context was NOT loaded."
              else empty
              end
            ),
          additionalContext: $msg
        }
      '
  fi

  exit 0
}

fail_with_context() {
  local reason="${1:-Hook failed}"
  local safe_reason
  local safe_session_id

  safe_reason="$(sanitize_log_field "$reason")"
  safe_session_id="$(sanitize_log_field "$SESSION_ID")"

  printf 'Copilot/VS Code hook failure: %s\n' "$reason" >&2

  if declare -F audit_log_event >/dev/null; then
    audit_log_event \
      "$SCRIPT_NAME" \
      "[$(date +'%Y-%m-%d %H:%M:%S')] Error: $safe_reason, Session: $safe_session_id" \
      >/dev/null 2>&1 || true
  fi

  emit_output \
    "Required skill context was NOT loaded.

Reason: $reason

Instruction to agent: stop normal work, tell the user this hook failed, and ask them to fix the hook or required skill files before proceeding." \
    1
}

INPUT="$(cat)"

EVENT_NAME="$(
  jq -r '.hook_event_name // .hookEventName // empty' <<<"$INPUT" 2>/dev/null
)" || EVENT_NAME=""

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$INPUT"; then
  fail_with_context "Invalid hook input: expected a JSON object"
fi

SESSION_ID="$(
  jq -r '
    .sessionId //
    .session_id //
    empty |
    if type == "string" then .
    elif . == null then empty
    else tostring
    end
  ' <<<"$INPUT"
)" || SESSION_ID=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" \
  || fail_with_context "Failed to resolve script directory"

COMMON_SH="$SCRIPT_DIR/common.sh"

[[ -r "$COMMON_SH" ]] \
  || fail_with_context "Common hook library not readable: $COMMON_SH"

# Source common.sh while preserving stdout for final JSON only.
# shellcheck source=/dev/null
if ! source "$COMMON_SH" >/dev/null; then
  fail_with_context "Failed to source common hook library: $COMMON_SH"
fi

AUDIT_SH="$SCRIPT_DIR/audit.sh"

[[ -r "$AUDIT_SH" ]] \
  || fail_with_context "Audit hook library not readable: $AUDIT_SH"
  
if ! source "$AUDIT_SH" >/dev/null; then
  fail_with_context "Failed to source audit hook library: $AUDIT_SH"
fi

declare -F audit_init >/dev/null \
  || fail_with_context "audit_init function not found in audit.sh"

declare -F audit_log_event >/dev/null \
  || fail_with_context "audit_log_event function not found in audit.sh"

command -v flock >/dev/null 2>&1 \
  || fail_with_context "Required command not found: flock"

audit_init >/dev/null \
  || fail_with_context "audit_init failed"

if [[ -n "${COPILOT_SKILLS_DIR:-}" ]]; then
  SKILLS_DIR="$COPILOT_SKILLS_DIR"
elif [[ -n "${AGENTS_SKILLS_DIR:-}" ]]; then
  SKILLS_DIR="$AGENTS_SKILLS_DIR"
elif [[ -n "${HOME:-}" ]]; then
  SKILLS_DIR="$HOME/.agents/skills"
else
  fail_with_context "None of COPILOT_SKILLS_DIR, AGENTS_SKILLS_DIR, or HOME is set"
fi

declare -a REQUIRED_SKILL_FILES=()

merge_env_skill_files "${AGENTS_REQUIRED_SKILL_FILES:-}"

safe_session_id="$(sanitize_log_field "$SESSION_ID")"

if ((${#REQUIRED_SKILL_FILES[@]} == 0)); then
  audit_log_event \
    "$SCRIPT_NAME" \
    "[$(date +'%Y-%m-%d %H:%M:%S')] Message: No skills loaded, Event: $EVENT_NAME, Session: $safe_session_id" \
    >/dev/null 2>&1 \
    || fail_with_context "Failed to write audit event: No skills loaded"

  printf '%s\n' '{"systemMessage":"No skills loaded"}'
  exit 0
fi

CONTEXT_PAYLOAD=""

for REQUIRED_SKILL_FILE in "${REQUIRED_SKILL_FILES[@]}"; do
  SAFE_REQUIRED_SKILL_FILE="$(sanitize_log_field "$REQUIRED_SKILL_FILE")"

  [[ -n "$REQUIRED_SKILL_FILE" ]] || fail_with_context "Required skill file path is empty"
  [[ -f "$REQUIRED_SKILL_FILE" ]] || fail_with_context "Required skill file not found: $REQUIRED_SKILL_FILE"
  [[ -r "$REQUIRED_SKILL_FILE" ]] || fail_with_context "Required skill file not readable: $REQUIRED_SKILL_FILE"

  SKILL_CONTEXT="$(
    awk '
      BEGIN { in_header = 0; first_line = 1 }
      {
        line = $0
        sub(/\r$/, "", line)
        if (first_line) {
          first_line = 0
          if (line == "---") {
            in_header = 1
            next
          }
        }
        if (in_header) {
          if (line == "---") {
            in_header = 0
          }
          next
        }
        print
      }
    ' "$REQUIRED_SKILL_FILE"
  )" || fail_with_context "Failed to read skill file: $REQUIRED_SKILL_FILE"

  if [[ -n "$CONTEXT_PAYLOAD" ]]; then
    CONTEXT_PAYLOAD+=$'\n\n'
  fi

  CONTEXT_PAYLOAD+="<!-- BEGIN REQUIRED SKILL: $REQUIRED_SKILL_FILE -->"$'\n'
  CONTEXT_PAYLOAD+="$SKILL_CONTEXT"$'\n'
  CONTEXT_PAYLOAD+="<!-- END REQUIRED SKILL: $REQUIRED_SKILL_FILE -->"

  audit_log_event \
    "$SCRIPT_NAME" \
    "[$(date +'%Y-%m-%d %H:%M:%S')] Message: Loaded skill $SAFE_REQUIRED_SKILL_FILE, Event: $EVENT_NAME, Session: $safe_session_id" \
    >/dev/null 2>&1 \
    || fail_with_context "Failed to write audit event for skill: $REQUIRED_SKILL_FILE"
done

REQUIRED_SKILL_CONTEXT="Required skill context loaded.

$CONTEXT_PAYLOAD"

emit_output \
  "$REQUIRED_SKILL_CONTEXT" \
  0
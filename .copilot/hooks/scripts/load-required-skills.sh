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
CONTEXT_MODE=""
CANARY_TEXT='VERIFICATION_CANARY: copilot-sessionstart-test-7f3a91
If you can see this, say exactly: I_CAN_SEE_SESSIONSTART_CONTEXT'

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
      "$(basename "$0")" \
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

SKILL_FILES=(
  "$SKILLS_DIR/universal-guidelines/SKILL.md"
  "$SKILLS_DIR/cli-compression/SKILL.md"
  "$SKILLS_DIR/context-engineering/SKILL.md"
  "$SKILLS_DIR/caveman/SKILL.md"
)

SKILL_NAMES=(
  "universal-guidelines"
  "cli-compression"
  "context-engineering"
  "caveman"
)

SKILL_COMPACT_SUMMARIES=(
  "Behavioral guardrails: keep scope tight, verify changes, and fail safely on missing context."
  "CLI output compression: prefix shell commands with rtk and prefer concise command output."
  "Context discipline: load exact rules/files first, then minimal task packet before edits."
  "Compressed response style: terse language while preserving technical correctness and exact terms."
)

CONTEXT_MODE="${COPILOT_REQUIRED_SKILL_CONTEXT_MODE:-${COPILOT_REQUIRED_SKILLS_MODE:-compact}}"
CONTEXT_MODE="$(printf '%s' "$CONTEXT_MODE" | tr '[:upper:]' '[:lower:]')"

case "$CONTEXT_MODE" in
  compact|full) ;;
  *)
    fail_with_context "Invalid COPILOT_REQUIRED_SKILL_CONTEXT_MODE: $CONTEXT_MODE (expected compact or full)"
    ;;
esac

append_required_skill() {
  local path="${1:-}"

  [[ -n "$path" ]] \
    || fail_with_context "append_required_skill: path required"

  [[ -f "$path" ]] \
    || fail_with_context "Required skill file not found: $path"

  [[ -r "$path" ]] \
    || fail_with_context "Required skill file not readable: $path"

  cat "$path" >/dev/null \
    || fail_with_context "Failed to read skill file: $path"
}

for index in "${!SKILL_FILES[@]}"; do
  skill_file="${SKILL_FILES[$index]}"
  append_required_skill "$skill_file"

  safe_skill_file="$(sanitize_log_field "$skill_file")"
  safe_session_id="$(sanitize_log_field "$SESSION_ID")"

  audit_log_event \
    "$(basename "$0")" \
    "[$(date +'%Y-%m-%d %H:%M:%S')] Message: Appended skill $safe_skill_file ($CONTEXT_MODE), Event: $EVENT_NAME, Session: $safe_session_id" \
    >/dev/null 2>&1 \
    || fail_with_context "Failed to write audit event for skill: $skill_file"
done

build_full_context() {
  local full_context=""
  local path

  for path in "${SKILL_FILES[@]}"; do
    if [[ -n "$full_context" ]]; then
      full_context+=$'\n\n---\n\n'
    fi

    full_context+="$(cat "$path")"
  done

  full_context+=$'\n\n---\n\n'
  full_context+="$CANARY_TEXT"

  printf '%s' "$full_context"
}

build_compact_context() {
  local compact_context
  local index

  compact_context=$'Required skill context loaded (compact).\n\n'
  compact_context+=$'Mode: compact (set COPILOT_REQUIRED_SKILL_CONTEXT_MODE=full for full context).\n\n'
  compact_context+=$'Required skills:\n'

  for index in "${!SKILL_FILES[@]}"; do
    compact_context+="- ${SKILL_NAMES[$index]}: ${SKILL_COMPACT_SUMMARIES[$index]} path=${SKILL_FILES[$index]}"$'\n'
  done

  compact_context+=$'\n---\n\n'
  compact_context+="$CANARY_TEXT"

  printf '%s' "$compact_context"
}

if [[ "$CONTEXT_MODE" == "compact" ]]; then
  REQUIRED_SKILL_CONTEXT="$(build_compact_context)"
else
  REQUIRED_SKILL_CONTEXT="Required skill context loaded.

$(build_full_context)"
fi

emit_output \
  "$REQUIRED_SKILL_CONTEXT" \
  0
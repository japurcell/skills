#!/usr/bin/env bash
set -o pipefail

# Gemini CLI hook contract:
# - stdin: hook input JSON
# - stdout: final JSON only
# - stderr: logs/errors only
# - exit 0: structured hook result parsed by Gemini CLI

# jq is required for safe JSON output. Check it before using jq.
if ! command -v jq >/dev/null 2>&1; then
  printf '%s\n' '{"continue":false,"stopReason":"Required command not found: jq"}'
  exit 0
fi

hard_stop() {
  local reason="${1:-Hook failed}"
  printf 'Hook hard stop: %s\n' "$reason" >&2
  jq -nc --arg reason "$reason" \
    '{continue:false,stopReason:$reason,suppressOutput:true}'
  exit 0
}

sanitize_log_field() {
  # Prevent multi-line/control-character log injection.
  printf '%s' "${1:-}" | tr '\r\n\t' '   '
}

json_string_field() {
  local field="${1:-}"
  [[ -n "$field" ]] || hard_stop "json_string_field: field name required"

  jq -r --arg field "$field" '
    .[$field] //
    empty |
    if type == "string" then . else tostring end
  ' <<<"$INPUT"
}

INPUT="$(cat)"

if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$INPUT"; then
  hard_stop "Invalid hook input: expected a JSON object"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" \
  || hard_stop "Failed to resolve script directory"

SCRIPT_NAME="$(basename "$0")"

AUDIT_LIB="$SCRIPT_DIR/audit.sh"

[[ -r "$AUDIT_LIB" ]] || hard_stop "Audit library not readable: $AUDIT_LIB"

# Source audit library. Redirect stdout to stderr to preserve the strict stdout JSON rule.
# shellcheck source=/dev/null
if ! source "$AUDIT_LIB" >/dev/null; then
  hard_stop "Failed to source audit library: $AUDIT_LIB"
fi

declare -F audit_init >/dev/null || hard_stop "audit_init function not found in audit.sh"
declare -F audit_log_event >/dev/null || hard_stop "audit_log_event function not found in audit.sh"

if ! audit_init >/dev/null; then
  hard_stop "audit_init failed"
fi

SESSION_ID="$(json_string_field session_id)"
TIMESTAMP="$(json_string_field timestamp)"
HOOK_EVENT_NAME="$(json_string_field hook_event_name)"
CWD="$(json_string_field cwd)"

[[ -n "$HOOK_EVENT_NAME" ]] || hard_stop "Missing required field: hook_event_name"

# This script is a context-injection hook. These are the appropriate Gemini CLI events.
case "$HOOK_EVENT_NAME" in
  SessionStart|BeforeAgent|AfterTool)
    ;;
  *)
    hard_stop "Unsupported hook event for context injection: $HOOK_EVENT_NAME"
    ;;
esac

SAFE_SESSION_ID="$(sanitize_log_field "$SESSION_ID")"
SAFE_TIMESTAMP="$(sanitize_log_field "$TIMESTAMP")"
SAFE_HOOK_EVENT_NAME="$(sanitize_log_field "$HOOK_EVENT_NAME")"
SAFE_CWD="$(sanitize_log_field "$CWD")"

if ! audit_log_event \
  "$SCRIPT_NAME" \
  "[$SAFE_TIMESTAMP] Hook: $SAFE_HOOK_EVENT_NAME, CWD: $SAFE_CWD, Session: $SAFE_SESSION_ID" \
  >/dev/null; then
  hard_stop "Failed to write initial audit event"
fi

if [[ -n "${AGENTS_SKILLS_DIR:-}" ]]; then
  SKILLS_DIR="$AGENTS_SKILLS_DIR"
elif [[ -n "${HOME:-}" ]]; then
  SKILLS_DIR="$HOME/.agents/skills"
else
  hard_stop "Neither AGENTS_SKILLS_DIR nor HOME is set"
fi

REQUIRED_SKILL_FILE="$SKILLS_DIR/caveman/SKILL.md"

SAFE_REQUIRED_SKILL_FILE="$(sanitize_log_field "$REQUIRED_SKILL_FILE")"

[[ -n "$REQUIRED_SKILL_FILE" ]] || hard_stop "Required skill file path is empty"
[[ -f "$REQUIRED_SKILL_FILE" ]] || hard_stop "Required skill file not found: $REQUIRED_SKILL_FILE"
[[ -r "$REQUIRED_SKILL_FILE" ]] || hard_stop "Required skill file not readable: $REQUIRED_SKILL_FILE"

CONTEXT_PAYLOAD="$(
  cat "$REQUIRED_SKILL_FILE"
)" || hard_stop "Failed to read skill file: $REQUIRED_SKILL_FILE"

if ! audit_log_event \
  "$SCRIPT_NAME" \
  "[$SAFE_TIMESTAMP] Message: $SAFE_REQUIRED_SKILL_FILE loaded (caveman-only), Hook: $SAFE_HOOK_EVENT_NAME, CWD: $SAFE_CWD, Session: $SAFE_SESSION_ID" \
  >/dev/null; then
  hard_stop "Failed to write audit event for loaded skill: $REQUIRED_SKILL_FILE"
fi

# Final stdout JSON only.
#
# Required skill context stays in hookSpecificOutput.additionalContext. suppressOutput
# asks Gemini CLI to avoid logging hook metadata where supported.
jq -nc \
  --arg ev "$HOOK_EVENT_NAME" \
  --arg ctx "$CONTEXT_PAYLOAD" \
  '{
    hookSpecificOutput: {
      hookEventName: $ev,
      additionalContext: $ctx
    },
    systemMessage: "Required skill context loaded.",
    suppressOutput: true
  }'
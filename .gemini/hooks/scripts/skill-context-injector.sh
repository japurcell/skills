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

trim_ws() {
  local s="${1:-}"

  # Trim leading whitespace.
  s="${s#"${s%%[![:space:]]*}"}"

  # Trim trailing whitespace.
  s="${s%"${s##*[![:space:]]}"}"

  printf '%s' "$s"
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

  [[ -n "$skill_file" ]] || hard_stop "Skill file path is empty"

  # Support ~/path in env-provided values.
  if [[ "$skill_file" == "~/"* ]]; then
    [[ -n "${HOME:-}" ]] || hard_stop "Cannot expand ~/: HOME is not set"
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

# Built-in required skill files.
#
# Add more default required skills here as needed.
declare -a REQUIRED_SKILL_FILES=()

# Optional env var merged into REQUIRED_SKILL_FILES.
#
# Supported delimiters:
#   newline, colon, comma
#
# Relative paths are resolved under SKILLS_DIR.
#
# Examples:
#   export AGENTS_REQUIRED_SKILL_FILES="python/SKILL.md:security/SKILL.md"
#   export AGENTS_REQUIRED_SKILL_FILES="python/SKILL.md,security/SKILL.md"
#   export AGENTS_REQUIRED_SKILL_FILES=$'python/SKILL.md\nsecurity/SKILL.md'
merge_env_skill_files "${AGENTS_REQUIRED_SKILL_FILES:-}"

if ((${#REQUIRED_SKILL_FILES[@]} == 0)); then
  if ! audit_log_event \
    "$SCRIPT_NAME" \
    "[$SAFE_TIMESTAMP] Message: No skills loaded, Hook: $SAFE_HOOK_EVENT_NAME, CWD: $SAFE_CWD, Session: $SAFE_SESSION_ID" \
    >/dev/null; then
    hard_stop "Failed to write audit event"
  fi

  printf '%s\n' '{"systemMessage":"No skills loaded","suppressOutput":true}'
  exit 0
fi

CONTEXT_PAYLOAD=""
declare -a LOADED_SKILL_FILES=()

for REQUIRED_SKILL_FILE in "${REQUIRED_SKILL_FILES[@]}"; do
  SAFE_REQUIRED_SKILL_FILE="$(sanitize_log_field "$REQUIRED_SKILL_FILE")"

  [[ -n "$REQUIRED_SKILL_FILE" ]] || hard_stop "Required skill file path is empty"
  [[ -f "$REQUIRED_SKILL_FILE" ]] || hard_stop "Required skill file not found: $REQUIRED_SKILL_FILE"
  [[ -r "$REQUIRED_SKILL_FILE" ]] || hard_stop "Required skill file not readable: $REQUIRED_SKILL_FILE"

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
  )" || hard_stop "Failed to read skill file: $REQUIRED_SKILL_FILE"

  if [[ -n "$CONTEXT_PAYLOAD" ]]; then
    CONTEXT_PAYLOAD+=$'\n\n'
  fi

  CONTEXT_PAYLOAD+="<!-- BEGIN REQUIRED SKILL: $REQUIRED_SKILL_FILE -->"$'\n'
  CONTEXT_PAYLOAD+="$SKILL_CONTEXT"$'\n'
  CONTEXT_PAYLOAD+="<!-- END REQUIRED SKILL: $REQUIRED_SKILL_FILE -->"

  LOADED_SKILL_FILES+=("$REQUIRED_SKILL_FILE")

  if ! audit_log_event \
    "$SCRIPT_NAME" \
    "[$SAFE_TIMESTAMP] Message: loaded required skill file: $SAFE_REQUIRED_SKILL_FILE, Hook: $SAFE_HOOK_EVENT_NAME, CWD: $SAFE_CWD, Session: $SAFE_SESSION_ID" \
    >/dev/null; then
    hard_stop "Failed to write audit event for loaded skill: $REQUIRED_SKILL_FILE"
  fi
done

LOADED_COUNT="${#LOADED_SKILL_FILES[@]}"

# Final stdout JSON only.
#
# Required skill context stays in hookSpecificOutput.additionalContext. suppressOutput
# asks Gemini CLI to avoid logging hook metadata where supported.
jq -nc \
  --arg ev "$HOOK_EVENT_NAME" \
  --arg ctx "$CONTEXT_PAYLOAD" \
  --argjson count "$LOADED_COUNT" \
  '{
    hookSpecificOutput: {
      hookEventName: $ev,
      additionalContext: $ctx
    },
    systemMessage: "Required skill context loaded from \($count) file(s).",
    suppressOutput: true
  }'
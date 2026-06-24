#!/usr/bin/env bash

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/audit.sh"

require_cmd jq

INPUT="$(cat)"
SESSION_ID="$(jq -r '.sessionId // .session_id // empty' <<<"$INPUT")" || { SESSION_ID=""; }
TIMESTAMP="$(jq -r '.timestamp // empty' <<<"$INPUT")" || { TIMESTAMP=""; }
TOOL_NAME="$(jq -r '.toolName // .tool_name // empty' <<<"$INPUT")"

audit_init

log_event() {
  local message="$1"
  audit_log_event "$(basename "$0")" "[$TIMESTAMP] Session: $SESSION_ID, $message"
}

extract_patch_paths() {
  local patch_text="${1:-}"
  sed -n 's/^\*\*\* \(Add\|Update\) File: //p' <<<"$patch_text"
}

collect_direct_paths() {
  jq -r '
    [
      .toolArgs.path?,
      .toolArgs.filePath?,
      .tool_input.path?,
      .tool_input.filePath?
    ]
    | map(select(type == "string" and length > 0))
    | .[]
  ' <<<"$INPUT"

  local patch_text
  patch_text="$(
    jq -r '
      (.toolArgs // .tool_input // empty)
      | if type == "string" then . else empty end
    ' <<<"$INPUT"
  )"

  [[ -z "$patch_text" ]] || extract_patch_paths "$patch_text"
}

collect_event_paths() {
  [[ -n "$SESSION_ID" ]] || return 0

  local event_line
  local event_tool
  local event_path
  local patch_text

  while IFS= read -r event_line; do
    event_tool="$(jq -r 'select(.type == "tool.execution_start") | .data.toolName // empty' <<<"$event_line")"

    case "$event_tool" in
      create|edit)
        event_path="$(jq -r 'select(.type == "tool.execution_start") | .data.arguments.path // empty' <<<"$event_line")"
        [[ -z "$event_path" ]] || printf '%s\n' "$event_path"
        ;;
      apply_patch)
        patch_text="$(
          jq -r '
            select(.type == "tool.execution_start")
            | .data.arguments
            | if type == "string" then . else empty end
          ' <<<"$event_line"
        )"
        [[ -z "$patch_text" ]] || extract_patch_paths "$patch_text"
        ;;
    esac
  done < <(get_new_events "$SESSION_ID" "format")
}

run_formatter() {
  local path="$1"
  local command_display=""
  local -a command=()

  case "$path" in
    *.cs)
      command=(dotnet format --no-restore --include "$path")
      command_display="dotnet format --no-restore --include $path"
      ;;
    *.js|*.jsx|*.ts|*.tsx)
      command=(npx oxfmt "$path")
      command_display="npx oxfmt $path"
      ;;
    *)
      return 0
      ;;
  esac

  log_event "Command: $command_display"
  if "${command[@]}"; then
    return 0
  else
    local exit_code=$?
    log_event "Failure: $command_display (exit $exit_code)"
    return "$exit_code"
  fi
}

is_formattable_path() {
  local path="$1"
  case "$path" in
    *.cs|*.js|*.jsx|*.ts|*.tsx)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

log_event "Tool: $TOOL_NAME"

mapfile -t FILES < <(
  {
    collect_direct_paths
    collect_event_paths
  } | sed '/^$/d' | sort -u
)

for path in "${FILES[@]}"; do
  is_formattable_path "$path" || continue
  log_event "File: $path"
  run_formatter "$path"
done

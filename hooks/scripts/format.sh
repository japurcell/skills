#!/usr/bin/env bash

set -euo pipefail

INPUT="$(cat)"
SESSION_ID=$(echo "$INPUT" | jq -r '.sessionId // .session_id // empty')
TIMESTAMP=$(echo "$INPUT" | jq -r '.timestamp')
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // .tool_name // empty')
TOOL_ARGS=$(echo "$INPUT" | jq -r '.toolArgs // .tool_input // empty')
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COPILOT_HOME_DIR="${COPILOT_HOME:-$HOME/.copilot}"
AUDIT_LOG="${AUDIT_LOG:-$HOOK_DIR/audit.log}"
AUDIT_LOG_MAX_BYTES="${AUDIT_LOG_MAX_BYTES:-1048576}"
AUDIT_LOG_BACKUPS="${AUDIT_LOG_BACKUPS:-3}"
AUDIT_LOCK="${AUDIT_LOCK:-$AUDIT_LOG.lock}"
FILES=""

rotate_audit_log() {
  local current_size
  local backup

  [[ -f "$AUDIT_LOG" ]] || return 0

  current_size=$(wc -c < "$AUDIT_LOG")
  (( current_size < AUDIT_LOG_MAX_BYTES )) && return 0

  for ((backup=AUDIT_LOG_BACKUPS; backup >= 1; backup--)); do
    if [[ -f "$AUDIT_LOG.$backup" ]]; then
      if [[ "$backup" -eq "$AUDIT_LOG_BACKUPS" ]]; then
        rm -f "$AUDIT_LOG.$backup"
      else
        mv -f "$AUDIT_LOG.$backup" "$AUDIT_LOG.$((backup + 1))"
      fi
    fi
  done

  mv -f "$AUDIT_LOG" "$AUDIT_LOG.1"
}

append_audit_line() {
  local line="$1"
  printf '%s\n' "$line" >> "$AUDIT_LOG"
}

log_command_failure() {
  local command="$1"
  local status="$2"

  append_audit_line "[$TIMESTAMP] Session: $SESSION_ID, Failure: $command (exit $status)"
}

extract_patch_files() {
  local patch_text="$1"

  printf '%s\n' "$patch_text" | sed -n \
    -e 's/^\*\*\* Update File: //p' \
    -e 's/^\*\*\* Add File: //p' \
    -e 's/^\*\*\* Delete File: //p' \
    -e 's/^\*\*\* Move to: //p'
}

extract_direct_files() {
  echo "$INPUT" | jq -r '.toolArgs.path // .toolArgs.filePath // .toolArgs.file_path // .toolArgs.files[]? // .toolArgs.paths[]? // .tool_input.path // .tool_input.filePath // .tool_input.file_path // .tool_input.files[]? // .tool_input.paths[]? // empty'
}

extract_task_files() {
  local events_path="$COPILOT_HOME_DIR/session-state/$SESSION_ID/events.jsonl"
  local task_result
  local agent_id
  local parent_tool_call_id
  local task_files=""
  local event
  local child_tool_name
  local child_files=""
  local child_args=""

  [[ -f "$events_path" ]] || return 0

  task_result=$(echo "$INPUT" | jq -r '.toolResult.textResultForLlm // .tool_result.text_result_for_llm // empty')
  parent_tool_call_id=$(jq -r --arg current_args "$TOOL_ARGS" '
    select(.type == "tool.execution_start")
    | .data
    | select((.toolName // "") == "task")
    | select(.arguments == ($current_args | fromjson))
    | .toolCallId
  ' "$events_path" | tail -n 1)

  if [[ -z "$parent_tool_call_id" ]]; then
    [[ -n "$task_result" ]] || return 0

    agent_id=$(echo "$INPUT" | jq -r '.toolResult.toolTelemetry.restrictedProperties.agent_id // .toolResult.toolTelemetry.restrictedProperties.agentId // .tool_result.tool_telemetry.restricted_properties.agent_id // .tool_result.tool_telemetry.restricted_properties.agentId // empty')

    parent_tool_call_id=$(jq -r --arg result "$task_result" --arg agent_id "$agent_id" '
      select(.type == "tool.execution_complete")
      | .data
      | select(.success == true)
      | select((.result.content // "") == $result)
      | if $agent_id == "" then
          .toolCallId
        else
          select((.toolTelemetry.restrictedProperties.agent_id // .toolTelemetry.restrictedProperties.agentId // "") == $agent_id)
          | .toolCallId
        end
    ' "$events_path" | tail -n 1)
  fi

  [[ -n "$parent_tool_call_id" ]] || return 0

  while IFS= read -r event; do
    child_tool_name=$(jq -r '.toolName // empty' <<<"$event")
    child_files=""

    case "$child_tool_name" in
      apply_patch)
        child_args=$(jq -r '.arguments // empty' <<<"$event")
        child_files=$(extract_patch_files "$child_args")
        ;;
      create|edit)
        child_files=$(jq -r '.arguments.path // .arguments.filePath // .arguments.file_path // .arguments.files[]? // .arguments.paths[]? // empty' <<<"$event")
        ;;
    esac

    if [[ -n "$child_files" ]]; then
      task_files+="${child_files}"$'\n'
    fi
  done < <(
    jq -c --arg parent "$parent_tool_call_id" '
      select(.type == "tool.execution_start")
      | .data
      | select((.parentToolCallId // "") == $parent)
      | select((.toolName // "") == "apply_patch" or (.toolName // "") == "create" or (.toolName // "") == "edit")
    ' "$events_path"
  )

  printf '%s' "${task_files%$'\n'}"
}

if [ "$TOOL_NAME" = "apply_patch" ]; then
  FILES=$(extract_patch_files "$TOOL_ARGS")
elif [ "$TOOL_NAME" = "create" ] || [ "$TOOL_NAME" = "edit" ]; then
  FILES=$(extract_direct_files)
elif [ "$TOOL_NAME" = "task" ]; then
  FILES=$(extract_task_files)
fi

mkdir -p "$(dirname "$AUDIT_LOG")"

exec 9>"$AUDIT_LOCK"
flock -x 9
rotate_audit_log
append_audit_line "[$TIMESTAMP] Session: $SESSION_ID, Tool: $TOOL_NAME"

if [ -n "$FILES" ]; then
  while IFS= read -r FILE; do
    [[ -n "$FILE" ]] || continue

    append_audit_line "[$TIMESTAMP] Session: $SESSION_ID, File: $FILE"

    if [[ "$FILE" =~ \.(js|ts|jsx|tsx|mjs|cjs)$ ]]; then
      append_audit_line "[$TIMESTAMP] Session: $SESSION_ID, Command: npx oxfmt $FILE"
      if npx oxfmt "$FILE" 2>&1; then
        :
      else
        status=$?
        log_command_failure "npx oxfmt $FILE" "$status"
        exit "$status"
      fi
    fi

    if [[ "$FILE" =~ \.(cs)$ ]]; then
      append_audit_line "[$TIMESTAMP] Session: $SESSION_ID, Command: dotnet format --include $FILE"
      if dotnet format --include "$FILE" --severity error 2>&1; then
        :
      else
        status=$?
        log_command_failure "dotnet format --include $FILE" "$status"
        exit "$status"
      fi
    fi
  done <<< "$FILES"
fi

flock -u 9
exec 9>&-

echo '{"continue":true}'

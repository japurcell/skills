#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)"
parse_input "$INPUT"
TOOL_NAME=$(jq -r '.toolName // .tool_name // empty' <<< "$INPUT")
TOOL_ARGS=$(jq -r '.toolArgs // .tool_input // empty' <<< "$INPUT")

setup_audit_log

FILES=""
if [[ "$TOOL_NAME" == "apply_patch" ]]; then
  FILES=$(
    printf '%s\n' "$TOOL_ARGS" | sed -n \
      -e 's/^\*\*\* Update File: //p' \
      -e 's/^\*\*\* Add File: //p' \
      -e 's/^\*\*\* Delete File: //p' \
      -e 's/^\*\*\* Move to: //p'
  )
elif [[ "$TOOL_NAME" == "create" || "$TOOL_NAME" == "edit" ]]; then
  FILES=$(jq -r '
    .toolArgs.path //
    .toolArgs.files[]? //
    .toolArgs.paths[]? //
    .tool_input.path //
    .tool_input.files[]? //
    .tool_input.paths[]? //
    empty
  ' <<< "$INPUT")
elif [[ "$TOOL_NAME" == "task" || "$TOOL_NAME" == "read_agent" ]]; then
  NEW_EVENTS=$(get_new_events "$SESSION_ID" "format")
  if [[ -n "$NEW_EVENTS" ]]; then
    FILES_JSON=$(printf '%s' "$NEW_EVENTS" | jq -r '
      select(.type == "tool.execution_start") |
      .data |
      select(.toolName == "create" or .toolName == "edit") |
      .arguments |
      .path // .files[]? // .paths[]? // empty
    ')
    FILES_PATCH=$(printf '%s' "$NEW_EVENTS" | jq -r '
      select(.type == "tool.execution_start") |
      .data |
      select(.toolName == "apply_patch") |
      .arguments // empty
    ' | sed -n \
      -e 's/^\*\*\* Update File: //p' \
      -e 's/^\*\*\* Add File: //p' \
      -e 's/^\*\*\* Delete File: //p' \
      -e 's/^\*\*\* Move to: //p')
    FILES=$(printf '%s\n%s' "$FILES_JSON" "$FILES_PATCH" | sort -u)
  fi
fi

append_audit_line "$AUDIT_LOG" "format.sh" "[$TIMESTAMP] Session: $SESSION_ID, Tool: $TOOL_NAME"

if [[ -n "$FILES" ]]; then
  while IFS= read -r FILE; do
    [[ -n "$FILE" ]] || continue

    append_audit_line "$AUDIT_LOG" "format.sh" "[$TIMESTAMP] Session: $SESSION_ID, File: $FILE"

    if [[ "$FILE" =~ \.(js|ts|jsx|tsx|mjs|cjs)$ ]]; then
      if ! command -v npx >/dev/null 2>&1; then
        append_audit_line "$AUDIT_LOG" "format.sh" "[$TIMESTAMP] Session: $SESSION_ID, Skip: npx not found for $FILE"
        continue
      fi
      append_audit_line "$AUDIT_LOG" "format.sh" "[$TIMESTAMP] Session: $SESSION_ID, Command: npx oxfmt $FILE"
      oxfmt_output=$(npx oxfmt "$FILE" 2>&1) || {
        exit_code=$?
        append_audit_line "$AUDIT_LOG" "format.sh" "[$TIMESTAMP] Session: $SESSION_ID, Failure: npx oxfmt $FILE (exit $exit_code)"
        append_audit_line "$AUDIT_LOG" "format.sh" "[$TIMESTAMP] Session: $SESSION_ID, Error: npx oxfmt failed for $FILE, Output: $oxfmt_output"
        exit 1
      }
    fi

    if [[ "$FILE" =~ \.cs$ ]]; then
      if ! command -v dotnet >/dev/null 2>&1; then
        append_audit_line "$AUDIT_LOG" "format.sh" "[$TIMESTAMP] Session: $SESSION_ID, Skip: dotnet not found for $FILE"
        continue
      fi
      # Use src/ if it exists, otherwise use REPO_ROOT
      CD_TARGET="$REPO_ROOT"
      if [[ -d "$REPO_ROOT/src" ]]; then
        CD_TARGET="$REPO_ROOT/src"
      fi

      if ! cd "$CD_TARGET"; then
        append_audit_line "$AUDIT_LOG" "format.sh" "[$TIMESTAMP] Session: $SESSION_ID, Error: failed to cd to $CD_TARGET"
        exit 1
      fi

      append_audit_line "$AUDIT_LOG" "format.sh" "[$TIMESTAMP] Session: $SESSION_ID, Command: dotnet format --no-restore --include $FILE"
      dotnet_format_output=$(dotnet format --no-restore --include "$FILE" 2>&1) || {
        exit_code=$?
        append_audit_line "$AUDIT_LOG" "format.sh" "[$TIMESTAMP] Session: $SESSION_ID, Failure: dotnet format --no-restore --include $FILE (exit $exit_code)"
        append_audit_line "$AUDIT_LOG" "format.sh" "[$TIMESTAMP] Session: $SESSION_ID, Error: dotnet format failed for $FILE, Output: $dotnet_format_output"
        exit 1
      }
    fi
  done <<< "$FILES"
fi

echo '{"continue":true}'

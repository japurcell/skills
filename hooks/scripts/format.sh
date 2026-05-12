#!/usr/bin/env bash

set -euo pipefail

INPUT="$(cat)"
SESSION_ID=$(echo "$INPUT" | jq -r '.sessionId // .session_id // empty')
TIMESTAMP=$(echo "$INPUT" | jq -r '.timestamp')
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // .tool_name // empty')
TOOL_ARGS=$(echo "$INPUT" | jq -r '.toolArgs // .tool_input // empty')
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIT_LOG="${AUDIT_LOG:-$HOOK_DIR/audit.log}"
AUDIT_LOG_MAX_BYTES="${AUDIT_LOG_MAX_BYTES:-1048576}"
AUDIT_LOG_BACKUPS="${AUDIT_LOG_BACKUPS:-3}"
AUDIT_LOCK="${AUDIT_LOCK:-$AUDIT_LOG.lock}"

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

if [ "$TOOL_NAME" = "apply_patch" ]; then
  FILES=$(printf '%s\n' "$TOOL_ARGS" | sed -n -e 's/^\*\*\* Update File: //p' -e 's/^\*\*\* Add File: //p' -e 's/^\*\*\* Delete File: //p' -e 's/^\*\*\* Move to: //p')
elif [ "$TOOL_NAME" = "create" ] || [ "$TOOL_NAME" = "edit" ]; then
  FILES=$(echo "$INPUT" | jq -r '.toolArgs.path // .toolArgs.filePath // .toolArgs.file_path // .toolArgs.files[]? // .toolArgs.paths[]? // .tool_input.path // .tool_input.filePath // .tool_input.file_path // .tool_input.files[]? // .tool_input.paths[]? // empty')
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

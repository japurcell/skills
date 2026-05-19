#!/usr/bin/env bash
set -euo pipefail

require_cmd() {
  local cmd="${1:?require_cmd: command name required}"
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "Required command not found: $cmd" >&2
    exit 1
  }
}

cleanup() {
  local exit_code=$?
  if [[ -n "${LOCK_FD_OPENED:-}" ]]; then
    flock -u 9 || true
    exec 9>&- || true
  fi
  exit "$exit_code"
}

require_cmd jq
require_cmd flock

INPUT="$(cat)"
SESSION_ID=$(jq -r '.sessionId // .session_id // empty' <<< "$INPUT")
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT")
TOOL_NAME=$(jq -r '.toolName // .tool_name // empty' <<< "$INPUT")
TOOL_ARGS=$(jq -r '.toolArgs // .tool_input // empty' <<< "$INPUT")

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
HOOK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

AUDIT_LIB="$SCRIPT_DIR/audit.sh"
if [[ ! -f "$AUDIT_LIB" ]]; then
  echo "Missing audit library: $AUDIT_LIB" >&2
  exit 1
fi

# shellcheck source=/dev/null
source "$AUDIT_LIB"

AUDIT_LOG="${AUDIT_LOG:-$HOOK_DIR/audit.log}"
AUDIT_LOCK="${AUDIT_LOCK:-$AUDIT_LOG.lock}"

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
fi

mkdir -p "$(dirname "$AUDIT_LOG")"

trap cleanup EXIT

exec 9>"$AUDIT_LOCK"
LOCK_FD_OPENED=1
flock -x 9

rotate_audit_log "$AUDIT_LOG"
append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, Tool: $TOOL_NAME"

if [[ -n "$FILES" ]]; then
  while IFS= read -r FILE; do
    [[ -n "$FILE" ]] || continue

    append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, File: $FILE"

    if [[ "$FILE" =~ \.(js|ts|jsx|tsx|mjs|cjs)$ ]]; then
      require_cmd npx
      if ! oxfmt_output=$(npx oxfmt "$FILE" 2>&1); then
        append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, Error: npx oxfmt failed for $FILE, Output: $oxfmt_output"
        exit 1
      fi
      append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, Command: npx oxfmt $FILE"
    fi

    if [[ "$FILE" =~ \.cs$ ]]; then
      require_cmd dotnet
      if ! cd "$REPO_ROOT/src"; then
        append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, Error: failed to cd to $REPO_ROOT/src"
        exit 1
      fi

      if ! dotnet_format_output=$(dotnet format --no-restore --include "$FILE" 2>&1); then
        append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, Error: dotnet format failed for $FILE, Output: $dotnet_format_output"
        exit 1
      fi

      append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, Command: dotnet format --no-restore --include $FILE"
    fi
  done <<< "$FILES"
fi

echo '{"continue":true}'
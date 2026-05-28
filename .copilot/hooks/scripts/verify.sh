#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

require_cmd jq
require_cmd flock

INPUT="$(cat)" || { INPUT=""; }
parse_input "$INPUT"
setup_audit_log

TOOL_NAME=$(jq -r '.toolName // .tool_name // empty' <<< "$INPUT")
TOOL_ARGS=$(jq -r '.toolArgs // .tool_input // empty' <<< "$INPUT")

RELEVANT_FILES=""
if [[ "$TOOL_NAME" == "apply_patch" ]]; then
  RELEVANT_FILES=$(printf '%s\n' "$TOOL_ARGS" | grep -E '^\*\*\* (Update|Add|Delete) File: .*\.(cs|csproj|sln|sh|json|md)$' || true)
elif [[ "$TOOL_NAME" == "create" || "$TOOL_NAME" == "edit" ]]; then
  RELEVANT_FILES=$(jq -r '
    .toolArgs.path // .toolArgs.files[]? // .toolArgs.paths[]? //
    .tool_input.path // .tool_input.files[]? // .tool_input.paths[]? //
    empty
  ' <<< "$INPUT" | grep -E '\.(cs|csproj|sln|sh|json|md)$' || true)
elif [[ "$TOOL_NAME" == "task" || "$TOOL_NAME" == "read_agent" ]]; then
  # For subagents, check if they modified any relevant files in their session events
  NEW_EVENTS=$(get_new_events "$SESSION_ID" "verify")
  if [[ -n "$NEW_EVENTS" ]]; then
    RELEVANT_FILES=$(printf '%s' "$NEW_EVENTS" | jq -r '
      select(.type == "tool.execution_start") |
      .data |
      if .toolName == "create" or .toolName == "edit" then
        .arguments.path // .arguments.files[]? // .arguments.paths[]?
      elif .toolName == "apply_patch" then
        .arguments
      else
        empty
      end
    ' | grep -E '(\.(cs|csproj|sln|sh|json|md)$|^\*\*\* (Update|Add|Delete) File: .*\.(cs|csproj|sln|sh|json|md)$)' || true)
  fi
fi

if [[ -z "$RELEVANT_FILES" ]]; then
  append_audit_line "$AUDIT_LOG" "verify.sh" "[$TIMESTAMP] Session: $SESSION_ID, skipping verify.sh: No relevant files changed in $TOOL_NAME"
  echo '{"continue":true}'
  exit 0
fi

append_audit_line "$AUDIT_LOG" "verify.sh" "[$TIMESTAMP] Session: $SESSION_ID, REPO_ROOT: $REPO_ROOT, Tool: $TOOL_NAME"

while IFS= read -r FILE; do
  [[ -n "$FILE" ]] || continue
  append_audit_line "$AUDIT_LOG" "verify.sh" "[$TIMESTAMP] Session: $SESSION_ID, File: $FILE"
done <<< "$RELEVANT_FILES"

if ! cd "$REPO_ROOT/src" 2>/dev/null; then
  append_audit_line "$AUDIT_LOG" "verify.sh" "[$TIMESTAMP] Session: $SESSION_ID, skipping verify.sh: $REPO_ROOT/src not found"
  exit 0
fi

# Only proceed if we find C# project files
if ! find . -maxdepth 2 -name "*.csproj" -o -name "*.sln" | grep -q .; then
  append_audit_line "$AUDIT_LOG" "verify.sh" "[$TIMESTAMP] Session: $SESSION_ID, skipping verify.sh: No .csproj or .sln found in $REPO_ROOT/src"
  exit 0
fi

if ! command -v dotnet >/dev/null 2>&1; then
  append_audit_line "$AUDIT_LOG" "verify.sh" "[$TIMESTAMP] Session: $SESSION_ID, skipping verify.sh: dotnet command not found"
  exit 0
fi

build_output=$(dotnet build 2>&1) || {
  append_audit_line "$AUDIT_LOG" "verify.sh" "[$TIMESTAMP] Session: $SESSION_ID, dotnet build failed: $build_output"
  exit 1
}

test_output=$(dotnet test --no-build 2>&1) || {
  append_audit_line "$AUDIT_LOG" "verify.sh" "[$TIMESTAMP] Session: $SESSION_ID, dotnet test failed: $test_output"
  exit 1
}

append_audit_line "$AUDIT_LOG" "verify.sh" "[$TIMESTAMP] Session: $SESSION_ID, Command: dotnet build && dotnet test --no-build"
echo '{"continue":true}'

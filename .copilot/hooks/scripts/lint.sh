#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

require_cmd jq

readonly INPUT="$(cat)"
parse_input "$INPUT"

LINT_OUTPUT=""
LINT_EXIT=0

TOOL_NAME=$(jq -r '.tool_name // .toolName // empty' <<< "$INPUT")
FILE_PATH=$(jq -r '.tool_input.filePath // .toolArgs.path // .toolArgs.filePath // empty' <<< "$INPUT")

if [[ "$TOOL_NAME" != 'create_file' && "$TOOL_NAME" != "replace_string_in_file" && "$TOOL_NAME" != "edit" && "$TOOL_NAME" != "write_file" ]]; then
  exit 0
fi

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

if [[ "$FILE_PATH" =~ \.(js|ts|jsx|tsx|mjs|cjs)$ ]]; then
    if command -v npx >/dev/null 2>&1; then
      LINT_OUTPUT=$(npx oxfmt "$FILE_PATH" 2>&1) || { LINT_EXIT=$?; }
    fi
fi

if [[ "$FILE_PATH" =~ \.(cs)$ ]]; then
    if command -v dotnet >/dev/null 2>&1; then
      # Try to run from REPO_ROOT or src if it exists
      CD_TARGET="$REPO_ROOT"
      if [[ -d "$REPO_ROOT/src" ]]; then
        CD_TARGET="$REPO_ROOT/src"
      fi
      (cd "$CD_TARGET" && LINT_OUTPUT=$(dotnet format --include "$FILE_PATH" 2>&1)) || { LINT_EXIT=$?; }
    fi
fi

if [[ $LINT_EXIT -ne 0 ]]; then
    jq -n --arg reason "Linting failed for $FILE_PATH" \
          --arg context "$LINT_OUTPUT" \
        '{
            hookSpecificOutput: {
                hookEventName: "PreToolUse",
                permissionDecision: "deny",
                permissionDecisionReason: $reason,
                additionalContext: $context
            }
        }'
    exit 0
fi

echo '{"continue":true}'
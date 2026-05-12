#!/usr/bin/env bash

set -euo pipefail

readonly INPUT="$(cat)"
LINT_OUTPUT=""
LINT_EXIT=0

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.filePath // empty')

if [[ "$TOOL_NAME" != 'create_file' && "$TOOL_NAME" != "replace_string_in_file"  ]]; then
  exit 0
fi

if [[ "$FILE_PATH" =~ \.(js|ts|jsx|tsx|mjs|cjs)$ ]]; then
    LINT_OUTPUT=$(npx oxfmt "$FILE_PATH" 2>&1)
    LINT_EXIT=$?
fi

if [[ "$FILE_PATH" =~ \.(cs)$ ]]; then
    LINT_OUTPUT=$(dotnet format --include "$FILE_PATH" 2>&1)
    LINT_EXIT=$?
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
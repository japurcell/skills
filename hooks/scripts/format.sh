#!/usr/bin/env bash

set -euo pipefail

INPUT="$(cat)"
SESSION_ID=$(echo "$INPUT" | jq -r '.sessionId // .session_id // empty')
TIMESTAMP=$(echo "$INPUT" | jq -r '.timestamp')
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // .tool_name // empty')
TOOL_ARGS=$(echo "$INPUT" | jq -r '.toolArgs // .tool_input // empty')
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIT_LOG="${AUDIT_LOG:-$HOOK_DIR/audit.log}"

echo "[$TIMESTAMP] Session: $SESSION_ID, Tool: $TOOL_NAME" >> "$AUDIT_LOG"

if [ "$TOOL_NAME" = "apply_patch" ]; then
  FILES=$(printf '%s\n' "$TOOL_ARGS" | sed -n -e 's/^\*\*\* Update File: //p' -e 's/^\*\*\* Add File: //p' -e 's/^\*\*\* Delete File: //p' -e 's/^\*\*\* Move to: //p')
else
  FILES=$(echo "$INPUT" | jq -r '.toolArgs.files[]? // .toolArgs.path // .tool_input.files[]? // .tool_input.path // empty')
fi

if [ -n "$FILES" ]; then
  for FILE in $FILES; do
    echo "[$TIMESTAMP] Session: $SESSION_ID, File: $FILE" >> "$AUDIT_LOG"

    if [[ "$FILE" =~ \.(js|ts|jsx|tsx|mjs|cjs)$ ]]; then
        npx oxfmt "$FILE" 2>/dev/null
    fi

    if [[ "$FILE" =~ \.(cs)$ ]]; then
        dotnet format --include "$FILE" 2>/dev/null
    fi
  done
fi

echo '{"continue":true}'

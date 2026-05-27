#!/usr/bin/env bash

set -euo pipefail

read_startup_additional_context() {
  local context_file="${1:?read_startup_additional_context: context file required}"

  jq -er '.additionalContext' "$context_file"
}

emit_startup_context_payload() {
  local context="${1:?emit_startup_context_payload: context required}"
  local hook_event_name="${2:?emit_startup_context_payload: hook event name required}"

  jq -nc --arg ev "$hook_event_name" --arg ctx "$context" \
    '{hookSpecificOutput:{hookEventName:$ev,additionalContext:$ctx},systemMessage:$ctx}'
}

#!/usr/bin/env bash

set -euo pipefail

is_vscode_startup_payload() {
  local input="${1:?is_vscode_startup_payload: input required}"

  jq -e 'has("hook_event_name") or has("hookEventName") or has("session_id") or has("transcript_path")' \
    >/dev/null <<<"$input"
}

read_startup_additional_context() {
  local context_file="${1:?read_startup_additional_context: context file required}"

  jq -er '.additionalContext' "$context_file"
}

emit_startup_context_payload() {
  local input="${1:?emit_startup_context_payload: input required}"
  local default_event_name="${2:?emit_startup_context_payload: default event required}"
  local context="${3:?emit_startup_context_payload: context required}"
  local event_name

  if is_vscode_startup_payload "$input"; then
    event_name="$(jq -r --arg default_event_name "$default_event_name" \
      '.hook_event_name // .hookEventName // $default_event_name' <<<"$input")"

    jq -nc --arg ev "$event_name" --arg ctx "$context" \
      '{hookSpecificOutput:{hookEventName:$ev,additionalContext:$ctx}}'
  else
    jq -nc --arg ctx "$context" \
      '{additionalContext:$ctx}'
  fi
}

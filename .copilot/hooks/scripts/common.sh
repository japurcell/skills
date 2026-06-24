#!/usr/bin/env bash

# Common helpers for Copilot hooks.
# Intended to be sourced:
#   source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

set -euo pipefail

require_cmd() {
  local cmd="${1:?require_cmd: command name required}"
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "Required command not found: $cmd" >&2
    exit 1
  }
}

# Directory resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Resolve REPO_ROOT: try git first, then fallback to current directory
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
else
  REPO_ROOT="$(pwd)"
fi

get_new_events() {
  local session_id="${1:?get_new_events: session_id is required}"
  local script_id="${2:?get_new_events: script_id is required}"
  local events_file="${COPILOT_HOME:-$HOME/.copilot}/session-state/$session_id/events.jsonl"
  local state_dir="${COPILOT_HOME:-$HOME/.copilot}/session-state/$session_id"
  local state_file="$state_dir/last_line.$script_id"

  if [[ ! -f "$events_file" ]]; then
    return 0
  fi

  mkdir -p "$state_dir"

  local last_line
  last_line=$(cat "$state_file" 2>/dev/null || echo 0)
  
  local current_lines
  current_lines=$(wc -l < "$events_file")

  if (( current_lines > last_line )); then
    tail -n +$((last_line + 1)) "$events_file" | head -n $((current_lines - last_line))
    echo "$current_lines" > "$state_file"
  fi
}

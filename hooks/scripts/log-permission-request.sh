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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
HOOK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

AUDIT_LIB="$SCRIPT_DIR/audit.sh"

if [[ ! -f "$AUDIT_LIB" ]]; then
  echo "Missing audit library: $AUDIT_LIB" >&2
  exit 1
fi

source "$AUDIT_LIB"

AUDIT_LOG="${AUDIT_LOG:-$HOOK_DIR/audit.log}"
AUDIT_LOCK="${AUDIT_LOCK:-$AUDIT_LOG.lock}"

mkdir -p "$(dirname "$AUDIT_LOG")"

trap cleanup EXIT

exec 9>"$AUDIT_LOCK"
LOCK_FD_OPENED=1
flock -x 9

rotate_audit_log "$AUDIT_LOG"
append_audit_line "$AUDIT_LOG" \
  "log-permission-request.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, Input: $INPUT"

# { behavior: "allow|deny", message: "reason given to LLM for denying", interrupt: true|false }
#!/usr/bin/env bash
set -euo pipefail

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Required command not found: $1" >&2
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
require_cmd dotnet

INPUT="$(cat)"
SESSION_ID=$(jq -r '.sessionId // .session_id // empty' <<< "$INPUT")
TIMESTAMP=$(jq -r '.timestamp // empty' <<< "$INPUT")

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
HOOK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/audit.sh"

AUDIT_LOG="${AUDIT_LOG:-$HOOK_DIR/audit.log}"
AUDIT_LOCK="${AUDIT_LOCK:-$AUDIT_LOG.lock}"

mkdir -p "$(dirname "$AUDIT_LOG")"

trap cleanup EXIT

exec 9>"$AUDIT_LOCK"
LOCK_FD_OPENED=1
flock -x 9

rotate_audit_log "$AUDIT_LOG"
append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, REPO_ROOT: $REPO_ROOT, Input: $INPUT"

if ! cd "$REPO_ROOT/src"; then
  append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, failed to cd to $REPO_ROOT/src"
  exit 1
fi

if ! build_output=$(dotnet build 2>&1); then
  append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, dotnet build failed: $build_output"
  exit 1
fi

if ! test_output=$(dotnet test --no-build 2>&1); then
  append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, dotnet test failed: $test_output"
  exit 1
fi

append_audit_line "$AUDIT_LOG" "[$TIMESTAMP] Session: $SESSION_ID, Command: dotnet build && dotnet test --no-build"
echo '{"continue":true}'
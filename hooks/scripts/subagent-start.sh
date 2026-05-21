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
TRANSCRIPT_PATH=$(jq -r '.transcriptPath // .transcript_path // empty' <<< "$INPUT")
AGENT_NAME=$(jq -r '.agentName // .agent_name // .agent_type // empty' <<< "$INPUT")
AGENT_ID=$(jq -r '.agentId // .agent_id // empty' <<< "$INPUT")
AGENT_DISPLAY_NAME=$(jq -r '.agentDisplayName // .agent_display_name // empty' <<< "$INPUT")
AGENT_DESCRIPTION=$(jq -r '.agentDescription // .agent_description // empty' <<< "$INPUT")

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

AUDIT_LIB="$SCRIPT_DIR/audit.sh"
STARTUP_CONTEXT_LIB="$SCRIPT_DIR/startup-context.sh"

if [[ ! -f "$AUDIT_LIB" ]]; then
  echo "Missing audit library: $AUDIT_LIB" >&2
  exit 1
fi

if [[ ! -f "$STARTUP_CONTEXT_LIB" ]]; then
  echo "Missing startup context library: $STARTUP_CONTEXT_LIB" >&2
  exit 1
fi

source "$AUDIT_LIB"
source "$STARTUP_CONTEXT_LIB"

AUDIT_LOG="${AUDIT_LOG:-$HOOK_DIR/audit.log}"
AUDIT_LOCK="${AUDIT_LOCK:-$AUDIT_LOG.lock}"

mkdir -p "$(dirname "$AUDIT_LOG")"

trap cleanup EXIT

exec 9>"$AUDIT_LOCK"
LOCK_FD_OPENED=1
flock -x 9

rotate_audit_log "$AUDIT_LOG"
append_audit_line "$AUDIT_LOG" \
  "subagent-start.sh" \
  "[$TIMESTAMP] Session: $SESSION_ID, \
    Transcript: $TRANSCRIPT_PATH, \
    Agent: $AGENT_NAME, \
    Agent ID: $AGENT_ID, \
    Display Name: $AGENT_DISPLAY_NAME, \
    Description: $AGENT_DESCRIPTION"

CONTEXT="$(read_startup_additional_context "$HOOK_DIR/references/agent-start-context.json")"
emit_startup_context_payload "$INPUT" "SubagentStart" "$CONTEXT"

# Optional — cannot block creation. Copilot CLI and VS Code use this when
# SubagentStart fires; SessionStart remains the fallback for runtimes that omit it.
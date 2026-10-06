#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

workdir="$(setup_test_workdir)"
cleanup() {
  rm -rf -- "$workdir"
}
trap cleanup EXIT

payload="$(jq -cn --arg content "$(printf 'x%.0s' {1..33000})" \
  '{hook_event_name:"PreToolUse",tool_name:"write_file",tool_input:{content:$content}}')"
output="$(with_disposable_hook_home env TOOL_GUARD_LOG_DIR="$workdir/guard.log" GUARD_MODE=block \
  python3 "$REPO_ROOT/.codex/hooks/tool-guard.py" <<<"$payload")"
assert_equals "deny" "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$output")" \
  "Expected Codex to deny an oversized write_file call."
reason="$(jq -r '.hookSpecificOutput.permissionDecisionReason' <<<"$output")"
[[ "$reason" == *'structured_bytes'* && "$reason" == *'write_file.content'* && "$reason" == *'33000 bytes'* ]] || {
  echo "Expected Codex denial to name the exact safe limit cause." >&2
  exit 1
}
[[ "$reason" != *'TOOL_GUARD_ALLOWLIST'* ]] || {
  echo "Expected Codex limit denial to omit misleading allowlist advice." >&2
  exit 1
}
assert_file_contains "$workdir/guard.log" '"rule_id":"structured_bytes"' \
  "Expected the Codex guard log to record the same safe rule."

operation='git push'
operation+=' --force origin main'
payload="$(jq -cn --arg command "$operation" \
  '{hook_event_name:"PreToolUse",tool_name:"Bash",tool_input:{command:$command}}')"
output="$(with_disposable_hook_home env TOOL_GUARD_LOG_DIR="$workdir/guard.log" GUARD_MODE=warn \
  python3 "$REPO_ROOT/.codex/hooks/tool-guard.py" <<<"$payload")"
[[ "$(jq -r '.systemMessage' <<<"$output")" == *'force_push_protected_branch'* ]] || {
  echo "Expected Codex warning to name the specific dangerous rule." >&2
  exit 1
}

with_disposable_hook_home python3 "$REPO_ROOT/scripts/test-security-banners.py"

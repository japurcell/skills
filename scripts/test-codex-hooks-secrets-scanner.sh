#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

python3 - "$REPO_ROOT/.codex/global-hooks.json" <<'PY'
import json
import pathlib
import sys

config = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
for event in ("PreToolUse", "Stop"):
    handlers = [handler for group in config["hooks"][event] for handler in group["hooks"]]
    assert len(handlers) == 1
    assert handlers[0]["command"] == "python3 ~/.codex/hooks/scan-secrets.py"
    assert handlers[0]["commandWindows"] == 'py -3 "%USERPROFILE%\\.codex\\hooks\\scan-secrets.py"'
PY

workdir="$(setup_test_workdir)"
trap 'rm -rf "$workdir"' EXIT
git -C "$workdir" init -q
printf '%s\n' 'sk_live_1234567890abcdefghij' > "$workdir/credentials.txt"

scan() {
  local event="$1" mode="$2"
  (
    cd "$workdir"
    SCAN_MODE="$mode" SECRETS_LOG_DIR="$workdir/logs" \
      python3 -I -S -B "$REPO_ROOT/.codex/hooks/scan-secrets.py" \
      <<JSON
{"hook_event_name":"$event","session_id":"m4-test","cwd":"$workdir","tool_name":"Bash","tool_input":{"command":"git status --short"}}
JSON
  )
}

pretool="$(scan PreToolUse block)"
jq -e '.hookSpecificOutput == {"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":.hookSpecificOutput.permissionDecisionReason} and (.hookSpecificOutput.permissionDecisionReason | contains("potential secrets detected"))' >/dev/null <<<"$pretool"
stop="$(scan Stop block)"
jq -e '.decision == "block" and (.reason | contains("potential secrets detected"))' >/dev/null <<<"$stop"
warn="$(scan PreToolUse warn)"
jq -e '.systemMessage | contains("Potential secrets detected")' >/dev/null <<<"$warn"
[[ "$pretool$stop$warn" != *"sk_live_1234567890abcdefghij"* ]]

rm "$workdir/credentials.txt"
clean="$(scan PreToolUse block)"
jq -e '. == {}' >/dev/null <<<"$clean"

printf 'PASS: Codex scan-secrets public envelopes\n'

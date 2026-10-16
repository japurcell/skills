#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

python3 - "$REPO_ROOT/.codex/global-hooks.json" <<'PY'
import json
import pathlib
import sys

config = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
for event, filename, timeout, status in (
    ("PreToolUse", "tool-guard.py", 10, "Checking dangerous tool actions"),
    ("Stop", "scan-status.py", 2, "Reading last secret-scan status"),
):
    matches = [
        (group, handler)
        for group in config["hooks"][event]
        for handler in group["hooks"]
        if handler.get("command") == f"python3 ~/.codex/hooks/{filename}"
    ]
    assert len(matches) == 1, f"Expected one {filename} registration on {event}"
    group, handler = matches[0]
    assert handler["type"] == "command"
    assert handler["commandWindows"] == f'py -3 "%USERPROFILE%\\.codex\\hooks\\{filename}"'
    assert handler["timeout"] == timeout
    assert handler["statusMessage"] == status
    if event == "PreToolUse":
        assert group["matcher"] == "Bash|apply_patch|Edit|Write"
    else:
        assert group.get("matcher", "*") == "*"
PY

workdir="$(setup_test_workdir)"
logdir="$(setup_test_workdir)"
trap 'rm -rf "$workdir" "$logdir"' EXIT
git -C "$workdir" init -q
printf '%s\n' 'sk_live_1234567890abcdefghij' > "$workdir/credentials.txt"

scan() {
  local event="$1" mode="$2"
  (
    cd "$workdir"
    SCAN_MODE="$mode" SECRETS_LOG_DIR="$logdir" \
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
jq -e '.systemMessage | contains("scan-secrets warning")' >/dev/null <<<"$warn"
[[ "$pretool$stop$warn" != *"sk_live_1234567890abcdefghij"* ]]

rm "$workdir/credentials.txt"
clean="$(scan PreToolUse block)"
jq -e '. == {}' >/dev/null <<<"$clean"
clean_stop="$(scan Stop block)"
jq -e '.systemMessage == "scan-secrets: pass; 0 modified files"' >/dev/null <<<"$clean_stop"

printf 'PASS: Codex scan-secrets public envelopes\n'
python3 "$REPO_ROOT/scripts/test-scan-secrets-capture.py" codex

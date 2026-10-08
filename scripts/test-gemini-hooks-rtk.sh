#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

RTK_PROVIDER="gemini"
RTK_PROVIDER_LABEL="Gemini"
RTK_SESSION_FIELD="session_id"
RTK_WRAPPER="$REPO_ROOT/.gemini/hooks/scripts/rtk-hook-gemini.py"
source "$REPO_ROOT/scripts/rtk-test-support.sh"


test_rtk_argument_vector_is_gemini() {
  local workdir
  local audit_log
  local arguments

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  audit_log="$workdir/audit.log"
  arguments="$workdir/rtk.arguments"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
printf "%s\\n" "$*" > "$RTK_ARGUMENTS_FILE"
printf "%s\\n" "{}"'

  run_rtk_hook \
    "$audit_log" \
    '{"session_id":"rtk-arguments","tool_name":"run_shell_command"}' \
    "PATH=$workdir/bin:$PATH" \
    "RTK_ARGUMENTS_FILE=$arguments" >/dev/null

  assert_equals "hook gemini" "$(<"$arguments")" \
    "Expected the Gemini wrapper to invoke exactly 'rtk hook gemini'."
}

test_gemini_rtk_rewrite_preserves_decisions() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
printf "%s\\n" "$RTK_RESPONSE"'

  output="$(
    RTK_RESPONSE='{"permissionDecision":"allow"}' run_rtk_hook \
      "$audit_log" \
      '{"session_id":"rtk-allow","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"
  assert_equals '{"permissionDecision":"allow"}' "$(jq -c . <<<"$output")" \
    "Expected Gemini to preserve allow decisions from RTK."

  output="$(
    RTK_RESPONSE='{"permissionDecision":"deny"}' run_rtk_hook \
      "$audit_log" \
      '{"session_id":"rtk-deny","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"
  assert_equals '{"permissionDecision":"deny"}' "$(jq -c . <<<"$output")" \
    "Expected Gemini to preserve deny decisions from RTK."

  output="$(
    RTK_RESPONSE='{"permissionDecision":"ask_user"}' run_rtk_hook \
      "$audit_log" \
      '{"session_id":"rtk-ask-user","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"
  assert_equals '{"permissionDecision":"ask_user"}' "$(jq -c . <<<"$output")" \
    "Expected Gemini to preserve ask_user decisions from RTK."
}

test_gemini_settings_register_rtk_rewrite_hook() {
  assert_equals 'python "$HOME/.gemini/hooks/scripts/rtk-hook-gemini.py"' \
    "$(jq -r '.hooks.BeforeTool[] | select(.matcher == "run_shell_command") | .hooks[0].command // empty' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected .gemini/global-settings.json to register rtk-hook-gemini.py for run_shell_command rewrites."
  assert_equals '5000' \
    "$(jq -r '.hooks.BeforeTool[] | select(.matcher == "run_shell_command") | .hooks[0].timeout // empty' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected the Gemini RTK registration to retain its five-second outer timeout."
  assert_equals '["*","run_shell_command"]' \
    "$(jq -c '.hooks.BeforeTool | map(.matcher)' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected the Gemini RTK registration to remain after the general BeforeTool hooks."
  python3 - "$REPO_ROOT/.gemini/global-settings.json" <<'PY'
import json
import sys
from pathlib import Path

settings = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
commands = [hook["command"] for group in settings["hooks"]["BeforeTool"] for hook in group["hooks"]]
required = [
    'python "$HOME/.gemini/hooks/scripts/send-event.py"',
    'python "$HOME/.gemini/hooks/scripts/tool-guard.py"',
    'python "$HOME/.gemini/hooks/scripts/scan-secrets.py"',
    'python "$HOME/.gemini/hooks/scripts/rtk-hook-gemini.py"',
]
positions = [commands.index(command) for command in required]
assert positions == sorted(positions), "Expected Markdown, observability, security, and RTK handlers in order."
PY
}

main() {
  test_valid_rewrite_is_forwarded_and_stdin_is_preserved
  test_open_pipe_completion_and_exact_input_bytes
  test_invalid_json_degrades_to_noop_json
  test_failed_rtk_rewrite_degrades_to_noop_json
  test_timeout_rtk_rewrite_degrades_to_noop_json
  test_empty_rtk_rewrite_is_treated_as_noop_without_audit_errors
  test_invalid_or_non_object_rtk_output_degrades_to_noop_json
  test_missing_rtk_degrades_to_noop_json
  test_rtk_argument_vector_is_gemini
  test_gemini_rtk_rewrite_preserves_decisions
  test_gemini_settings_register_rtk_rewrite_hook
}

main "$@"

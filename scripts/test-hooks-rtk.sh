#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_rtk_hook() {
  local audit_log="$1"
  local payload="$2"
  shift 2

  env AUDIT_LOG="$audit_log" "$@" python3 "$REPO_ROOT/.copilot/hooks/scripts/rtk-hook-copilot.py" <<<"$payload"
}

test_valid_rewrite_is_forwarded_and_stdin_is_preserved() {
  local workdir
  local audit_log
  local rtk_stdin
  local output
  local payload
  local expected_output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  rtk_stdin="$workdir/rtk.stdin"
  payload='{"sessionId":"rtk-session","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo forwarded","args":["one","two"]}}'
  expected_output='{"hookSpecificOutput":{"tool_input":{"command":"echo forwarded","args":["one","two"]}}}'

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
set -euo pipefail
cat > "$RTK_STDIN_FILE"
printf "%s\n" '"'"'{"hookSpecificOutput":{"tool_input":{"command":"echo forwarded","args":["one","two"]}}}'"'"''

  output="$(
    run_rtk_hook \
      "$audit_log" \
      "$payload" \
      "PATH=$workdir/bin:$PATH" \
      "RTK_STDIN_FILE=$rtk_stdin"
  )"

  assert_equals "$(jq -c . <<<"$payload")" "$(jq -c . < "$rtk_stdin")" \
    "Expected the wrapper to forward the original payload to rtk over stdin."
  assert_equals "$(jq -c . <<<"$expected_output")" "$(jq -c . <<<"$output")" \
    "Expected the wrapper to forward valid rtk JSON unchanged."
}

test_invalid_json_degrades_to_noop_json() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
echo unexpected >&2
exit 0'

  output="$(
    run_rtk_hook \
      "$audit_log" \
      'not-json' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected invalid-input RTK hook to degrade to a no-op JSON response."
  assert_equals "false" "$(if [[ -e "$workdir/rtk.stdin" ]]; then echo true; else echo false; fi)" \
    "Expected invalid JSON to skip invoking rtk."
  assert_file_contains "$audit_log" "invalid hook input JSON" \
    "Expected invalid JSON to be logged as a fallback."
}

test_failed_rtk_rewrite_degrades_to_noop_json() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
exit 23'

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-fail","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo ok"}}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected RTK rewrite failures to leave the original Copilot tool input unchanged."
  assert_file_contains "$audit_log" "rtk exited 23" \
    "Expected non-zero RTK exits to be logged as a fallback."
}

test_timeout_rtk_rewrite_degrades_to_noop_json() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
sleep 2
printf "%s\n" '"'"'{"hookSpecificOutput":{"tool_input":{"command":"echo late"}}}'"'"''

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-timeout","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo slow"}}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected RTK timeouts to leave the original Copilot tool input unchanged."
  assert_file_contains "$audit_log" "timed out after 1.0s" \
    "Expected RTK timeouts to be logged as a fallback."
}

test_rtk_rewrite_config_points_to_python_wrapper() {
  assert_equals 'python3 $HOME/.copilot/hooks/scripts/rtk-hook-copilot.py' \
    "$(jq -r '.hooks.PreToolUse[0].command // empty' "$REPO_ROOT/.copilot/hooks/rtk-rewrite.json")" \
    "Expected Copilot RTK rewrite config to point at the Python wrapper."
}

main() {
  test_valid_rewrite_is_forwarded_and_stdin_is_preserved
  test_invalid_json_degrades_to_noop_json
  test_failed_rtk_rewrite_degrades_to_noop_json
  test_timeout_rtk_rewrite_degrades_to_noop_json
  test_rtk_rewrite_config_points_to_python_wrapper
}

main "$@"

#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_rtk_hook() {
  local audit_log="$1"
  local payload="$2"
  shift 2

  env AUDIT_LOG="$audit_log" "$@" python3 "$REPO_ROOT/.gemini/hooks/scripts/rtk-hook-gemini.py" <<<"$payload"
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
  payload='{"session_id":"rtk-session","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo forwarded","args":["one","two"]}}'
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
      '{"session_id":"rtk-fail","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo ok"}}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected RTK rewrite failures to leave the original Gemini tool input unchanged."
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
      '{"session_id":"rtk-timeout","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo slow"}}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected RTK timeouts to leave the original Gemini tool input unchanged."
  assert_file_contains "$audit_log" "timed out after 1.0s" \
    "Expected RTK timeouts to be logged as a fallback."
}

test_empty_rtk_rewrite_is_treated_as_noop_without_audit_errors() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
exit 0'

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"session_id":"rtk-empty","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo empty"}}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected empty rtk stdout to return a standard no-op response."
  if [[ -f "$audit_log" ]] && grep -Fq "RTK rewrite fallback" "$audit_log"; then
    echo "Expected no RTK rewrite fallback errors in the audit log for clean empty output." >&2
    echo "--- Audit Log ---" >&2
    cat "$audit_log" >&2
    exit 1
  fi
}

test_invalid_or_non_object_rtk_output_degrades_to_noop_json() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
printf "%s\\n" invalid-json'

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"session_id":"rtk-invalid-output","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected malformed RTK output to degrade to a no-op JSON response."
  assert_file_contains "$audit_log" "rtk returned invalid JSON" \
    "Expected malformed RTK output to be logged as a fallback."

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
printf "%s\\n" "[]"'

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"session_id":"rtk-array-output","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected non-object RTK output to degrade to a no-op JSON response."
  assert_file_contains "$audit_log" "rtk returned non-object JSON" \
    "Expected non-object RTK output to be logged as a fallback."
}

test_missing_rtk_degrades_to_noop_json() {
  local workdir
  local audit_log
  local output
  local python_dir

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  mkdir -p "$workdir/empty-path"
  python_dir="$(dirname "$(command -v python3)")"

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"session_id":"rtk-missing","tool_name":"run_shell_command"}' \
      "PATH=$workdir/empty-path:$python_dir"
  )"

  assert_equals "{}" "$output" \
    "Expected a missing RTK executable to degrade to a no-op JSON response."
  assert_file_contains "$audit_log" "rtk command not found" \
    "Expected a missing RTK executable to be logged as a fallback."
}

test_rtk_argument_vector_is_gemini() {
  local workdir
  local audit_log
  local arguments

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
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
  trap 'rm -rf "'"$workdir"'"' RETURN
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
  assert_equals '["*","run_shell_command"]' \
    "$(jq -c '.hooks.BeforeTool | map(.matcher)' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected the Gemini RTK registration to remain after the general BeforeTool hooks."
  assert_equals 'python "$HOME/.gemini/hooks/scripts/send-event.py"' \
    "$(jq -r '.hooks.BeforeTool[0].hooks[0].command' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected observability to remain before Gemini RTK rewriting."
  assert_equals 'tool-guard' \
    "$(jq -r '.hooks.BeforeTool[0].hooks[1].name' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected Tool Guardian to remain before Gemini RTK rewriting."
  assert_equals 'scan-secrets' \
    "$(jq -r '.hooks.BeforeTool[0].hooks[2].name' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected secret scanning to remain before Gemini RTK rewriting."
}

main() {
  test_valid_rewrite_is_forwarded_and_stdin_is_preserved
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

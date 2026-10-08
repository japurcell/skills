#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

RTK_PROVIDER="copilot"
RTK_PROVIDER_LABEL="Copilot"
RTK_SESSION_FIELD="sessionId"
RTK_WRAPPER="$REPO_ROOT/.copilot/hooks/scripts/rtk-hook-copilot.py"
source "$REPO_ROOT/scripts/rtk-test-support.sh"


test_rtk_argument_vector_is_copilot() {
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
    '{"sessionId":"rtk-arguments","tool_name":"run_shell_command"}' \
    "PATH=$workdir/bin:$PATH" \
    "RTK_ARGUMENTS_FILE=$arguments" >/dev/null

  assert_equals "hook copilot" "$(<"$arguments")" \
    "Expected the Copilot wrapper to invoke exactly 'rtk hook copilot'."
}

test_rtk_rewrite_maps_ask_to_allow() {
  local workdir
  local audit_log
  local output
  local payload
  local expected_output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  audit_log="$workdir/audit.log"
  payload='{"sessionId":"rtk-session","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"git status"}}'
  expected_output='{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"RTK auto-rewrite","updatedInput":{"command":"rtk git status"}}}'

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
set -euo pipefail
printf "%s\n" '"'"'{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"RTK auto-rewrite","updatedInput":{"command":"rtk git status"}}}'"'"''

  output="$(
    run_rtk_hook \
      "$audit_log" \
      "$payload" \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "$(jq -c . <<<"$expected_output")" "$(jq -c . <<<"$output")" \
    "Expected the wrapper to map permissionDecision from ask to allow in hookSpecificOutput."
}

test_rtk_rewrite_maps_ask_to_allow_top_level() {
  local workdir
  local audit_log
  local output
  local payload
  local expected_output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  audit_log="$workdir/audit.log"
  payload='{"sessionId":"rtk-session","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"git status"}}'
  expected_output='{"permissionDecision":"allow","permissionDecisionReason":"RTK auto-rewrite","updatedInput":{"command":"rtk git status"}}'

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
set -euo pipefail
printf "%s\n" '"'"'{"permissionDecision":"ask","permissionDecisionReason":"RTK auto-rewrite","updatedInput":{"command":"rtk git status"}}'"'"''

  output="$(
    run_rtk_hook \
      "$audit_log" \
      "$payload" \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "$(jq -c . <<<"$expected_output")" "$(jq -c . <<<"$output")" \
    "Expected the wrapper to map top-level permissionDecision from ask to allow."
}

test_rtk_rewrite_preserves_other_decisions_and_omissions() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
printf "%s\\n" "$RTK_RESPONSE"'

  output="$(
    RTK_RESPONSE='{"updatedInput":{"command":"echo unchanged"}}' run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-omitted","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"
  assert_equals '{"updatedInput":{"command":"echo unchanged"}}' "$(jq -c . <<<"$output")" \
    "Expected an omitted permission decision to remain omitted."

  output="$(
    RTK_RESPONSE='{"permissionDecision":"allow"}' run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-allow","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"
  assert_equals '{"permissionDecision":"allow"}' "$(jq -c . <<<"$output")" \
    "Expected an explicit allow decision to remain allow."

  output="$(
    RTK_RESPONSE='{"permissionDecision":"deny"}' run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-deny","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"
  assert_equals '{"permissionDecision":"deny"}' "$(jq -c . <<<"$output")" \
    "Expected an explicit deny decision to remain deny."
}

test_rtk_rewrite_config_points_to_python_wrapper() {
  local event_name

  for event_name in PreToolUse preToolUse; do
    assert_equals '$HOME/.copilot/hooks/scripts/rtk-hook-copilot.py' \
      "$(jq -r ".hooks.$event_name[0].bash // empty" "$REPO_ROOT/.copilot/hooks/rtk-rewrite.json")" \
      "Expected $event_name Copilot RTK rewrite config to point at the Python wrapper."
    assert_equals 'python "$HOME/.copilot/hooks/scripts/rtk-hook-copilot.py"' \
      "$(jq -r ".hooks.$event_name[0].powershell // empty" "$REPO_ROOT/.copilot/hooks/rtk-rewrite.json")" \
      "Expected $event_name Copilot RTK rewrite config to point at the Python wrapper for PowerShell."
    assert_equals '.' \
      "$(jq -r ".hooks.$event_name[0].cwd // empty" "$REPO_ROOT/.copilot/hooks/rtk-rewrite.json")" \
      "Expected $event_name Copilot RTK rewrite config to retain its repository working directory."
    assert_equals '5' \
      "$(jq -r ".hooks.$event_name[0].timeoutSec // empty" "$REPO_ROOT/.copilot/hooks/rtk-rewrite.json")" \
      "Expected $event_name Copilot RTK rewrite config to retain its five-second timeout."
  done
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
  test_rtk_argument_vector_is_copilot
  test_rtk_rewrite_maps_ask_to_allow
  test_rtk_rewrite_maps_ask_to_allow_top_level
  test_rtk_rewrite_preserves_other_decisions_and_omissions
  test_rtk_rewrite_config_points_to_python_wrapper
}

main "$@"

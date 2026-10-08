#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/security-test-support.sh"

SECURITY_PROVIDER=copilot
SECURITY_PROVIDER_LABEL=Copilot
SECURITY_GUARD_RUNNER=run_tool_guard
SECURITY_GUARD_SCRIPT="$REPO_ROOT/.copilot/hooks/scripts/tool-guard.py"
SECURITY_SHELL_TOOL=bash
SECURITY_GUARD_TOOL_KEY=toolName
SECURITY_GUARD_INPUT_KEY=toolArgs
SECURITY_GUARD_SESSION_KEY=sessionId
SECURITY_GUARD_DECISION_FILTER='.permissionDecision'
SECURITY_GUARD_BENIGN_PAYLOAD='{"sessionId":"cli-session","toolName":"bash","toolArgs":{"file_path":"test.py","content":"def clean():\n    unlink()\n\nos.environ"}}'

run_tool_guard() {
  local log_dir="$1"
  local mode="$2"
  local payload="$3"

  TOOL_GUARD_LOG_DIR="$log_dir/guard.log" \
  GUARD_MODE="$mode" \
  python3 "$REPO_ROOT/.copilot/hooks/scripts/tool-guard.py" <<<"$payload"
}

test_warn_mode_returns_json_for_cli_payload() {
  local workdir
  local log_dir
  local output
  local risky_delete
  local expected_warning

  workdir="$(setup_test_workdir)"
  trap 'python3 -c "import shutil, sys; shutil.rmtree(sys.argv[1], ignore_errors=True)" "$workdir"' RETURN
  log_dir="$workdir/logs"
  risky_delete="rm"
  risky_delete+=" -rf"
  risky_delete+=" ."
  expected_warning="Tool Guardian warning bash. destructive_file_ops/critical [recursive_remove_current]: recursive forced removal targets the current directory. Action: rm -rf .. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."

  output="$(
    run_tool_guard \
      "$log_dir" \
      warn \
      "{\"sessionId\":\"cli-session\",\"toolName\":\"bash\",\"toolArgs\":\"${risky_delete}\"}"
  )"

  assert_equals "allow" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected warn mode to allow the tool after logging threats."
  assert_equals "allow" "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$output")" \
    "Expected warn mode to include a VS Code-compatible allow decision."
  assert_equals "$expected_warning" \
    "$(jq -r '.systemMessage' <<<"$output")" \
    "Expected warn mode to include terminal warning text."
  assert_file_contains "$log_dir/guard.log" '"event":"threats_detected"' \
    "Expected warn mode to log detected threats."
}

test_block_mode_denies_vscode_payload() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  log_dir="$workdir/logs"

  output="$(
    run_tool_guard \
      "$log_dir" \
      block \
      '{"hook_event_name":"PreToolUse","session_id":"vscode-session","tool_name":"Bash","tool_input":{"command":"git push --force origin main"}}'
  )"

  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected block mode to deny detected destructive operations."
  assert_equals "deny" "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$output")" \
    "Expected block mode to include a VS Code-compatible deny decision."
  assert_file_contains "$log_dir/guard.log" '"tool":"Bash"' \
    "Expected guard log to record the VS Code tool name."
}

test_block_mode_parses_cli_tool_args_objects() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  log_dir="$workdir/logs"

  output="$(
    run_tool_guard \
      "$log_dir" \
      block \
      '{"sessionId":"cli-object","toolName":"bash","toolArgs":{"command":"DROP TABLE users;"}}'
  )"

  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected block mode to inspect object-valued toolArgs."
  assert_file_contains "$log_dir/guard.log" '"category":"database_destruction"' \
    "Expected guard log to capture threat details from object-valued toolArgs."
}

test_nested_structured_tool_args_scan_decoded_string_values() {
  local workdir
  local log_dir
  local query
  local payload
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  log_dir="$workdir/logs"

  query="DELETE"; query+=" FROM"; query+=" users"
  payload="$(jq -cn --arg query "$query" '{toolName:"database_query",toolArgs:{request:{query:$query},options:{timeout:5}}}')"
  output="$(run_tool_guard "$log_dir" block "$payload")"
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected Copilot to scan decoded query strings nested in object-valued tool arguments."

  query="SELECT id"; query+=" FROM users"; query+=" WHERE id = 1"
  payload="$(jq -cn --arg query "$query" '{toolName:"database_query",toolArgs:{request:{query:$query},options:{timeout:5}}}')"
  output="$(run_tool_guard "$log_dir" block "$payload")"
  assert_equals "allow" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected safe nested structured Copilot arguments to remain allowed."
}

test_skip_mode_returns_explicit_allow_json() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  log_dir="$workdir/logs"

  output="$(
    TOOL_GUARD_LOG_DIR="$log_dir/guard.log" \
    GUARD_MODE="block" \
    SKIP_TOOL_GUARD="true" \
    python3 "$REPO_ROOT/.copilot/hooks/scripts/tool-guard.py" \
      <<<'{"sessionId":"skip-session","toolName":"bash","toolArgs":"echo ok"}'
  )"

  assert_equals "allow" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected skip mode to return an explicit allow permissionDecision."
  assert_equals "allow" "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$output")" \
    "Expected skip mode to keep VS Code-compatible allow output."
}

test_tool_guard_denies_invalid_payload() {
  local log_dir
  local output

  log_dir="$(setup_test_workdir)/logs"

  output="$(
    run_tool_guard \
      "$log_dir" \
      block \
      "not-even-json"
  )"

  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected Tool Guardian to deny malformed inputs (fail-closed)."

  output="$(
    run_tool_guard \
      "$log_dir" \
      block \
      "[]"
  )"

  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected Tool Guardian to deny non-object inputs."
}

test_tool_guard_denies_unexpected_input_exception() {
  local workdir
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  mkdir -p "$workdir/helpers"
  cp "$REPO_ROOT/.copilot/hooks/scripts/tool-guard.py" "$workdir/tool-guard.py"
  cp "$REPO_ROOT/.copilot/hooks/scripts/helpers/tool_guard_policy.py" "$workdir/helpers/tool_guard_policy.py"
  printf '%s\n' \
    'import json' \
    'import sys' \
    'def emit_json(payload):' \
    '    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")' \
    'def read_json_input():' \
    '    raise RuntimeError("forced input failure")' \
    'def sanitize_log_field(value):' \
    '    return str(value)' \
    >"$workdir/helpers/common.py"
  printf '%s\n' \
    'def audit_log_event(*_args, **_kwargs):' \
    '    return True' \
    >"$workdir/helpers/audit.py"

  output="$(python3 "$workdir/tool-guard.py" <<<'{}' 2>"$workdir/stderr")"

  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected Tool Guardian to deny unexpected input failures."
  assert_equals "Tool Guardian skipped: unexpected exception." \
    "$(jq -r '.permissionDecisionReason' <<<"$output")" \
    "Expected the fail-closed Copilot envelope for unexpected input failures."
  assert_file_contains "$workdir/stderr" 'RuntimeError' \
    "Expected the unexpected input failure to be diagnosed on stderr."
}

main() {
  test_structured_allowlist_is_tool_scoped_and_exact
  test_equivalent_and_json_encoded_threats_are_denied
  test_parser_limits_and_complete_command_forms_fail_closed
  test_home_variable_removals_and_git_global_options_are_denied
  test_block_response_and_audit_omit_sensitive_evidence
  test_warn_mode_returns_json_for_cli_payload
  test_block_mode_denies_vscode_payload
  test_block_mode_parses_cli_tool_args_objects
  test_nested_structured_tool_args_scan_decoded_string_values
  test_skip_mode_returns_explicit_allow_json
  test_tool_guard_denies_invalid_payload
  test_tool_guard_denies_unexpected_input_exception
  test_tool_guard_rm_env_and_rm_git
}

security_run_suite main "$@"

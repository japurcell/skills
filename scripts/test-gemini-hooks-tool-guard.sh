#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/security-test-support.sh"

SECURITY_PROVIDER=gemini
SECURITY_PROVIDER_LABEL=Gemini
SECURITY_GUARD_RUNNER=run_gemini_tool_guard
SECURITY_GUARD_SCRIPT="$REPO_ROOT/.gemini/hooks/scripts/tool-guard.py"
SECURITY_SHELL_TOOL=run_shell_command
SECURITY_GUARD_TOOL_KEY=tool_name
SECURITY_GUARD_INPUT_KEY=tool_input
SECURITY_GUARD_SESSION_KEY=session_id
SECURITY_GUARD_DECISION_FILTER='.decision'
SECURITY_GUARD_BENIGN_PAYLOAD='{"session_id":"cli-session","tool_name":"write_file","tool_input":{"file_path":"test.py","content":"def clean():\n    unlink()\n\nos.environ"}}'

run_gemini_tool_guard() {
  local log_dir="$1"
  local mode="$2"
  local payload="$3"

  TOOL_GUARD_LOG_DIR="$log_dir" \
  GUARD_MODE="$mode" \
  python3 "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.py" <<<"$payload"
}

test_gemini_log_is_owner_only_locked_and_no_follow() {
  local workdir
  local log_dir
  local process_id
  local output
  local outside_log
  local original_outside

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  log_dir="$workdir/logs"
  mkdir -p "$log_dir"
  printf 'existing\n' >"$log_dir/guard.log"
  chmod 666 "$log_dir/guard.log"
  output="$(run_gemini_tool_guard "$log_dir" block '{"tool_name":"run_shell_command","tool_input":"echo safe"}')"
  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected a safe invocation to create the hardened Gemini log."
  assert_equals "600" "$(python3 -c 'import os, sys; print(oct(os.stat(sys.argv[1]).st_mode & 0o777)[2:])' "$log_dir/guard.log")" \
    "Expected the Gemini Tool Guardian log to be owner-only."
  assert_equals "600" "$(python3 -c 'import os, sys; print(oct(os.stat(sys.argv[1]).st_mode & 0o777)[2:])' "$log_dir/guard.log.lock")" \
    "Expected the Gemini Tool Guardian lock file to be owner-only."

  : >"$log_dir/guard.log"
  for process_id in $(seq 1 12); do
    TOOL_GUARD_LOG_DIR="$log_dir" GUARD_MODE=block \
      python3 "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.py" \
      <<<'{"tool_name":"run_shell_command","tool_input":"echo safe"}' \
      >"$workdir/concurrent-$process_id.json" &
  done
  wait
  assert_equals "12" "$(wc -l <"$log_dir/guard.log" | tr -d ' ')" \
    "Expected every concurrent Gemini invocation to append one complete record."
  if ! jq -e -s 'length == 12 and all(.[]; .event == "guard_passed")' \
    "$log_dir/guard.log" >/dev/null; then
    echo "Expected concurrent Gemini audit writes to remain valid, complete JSON records." >&2
    exit 1
  fi

  rm -f "$log_dir/guard.log"
  outside_log="$workdir/outside.log"
  original_outside="outside-sentinel"
  printf '%s\n' "$original_outside" >"$outside_log"
  ln -s "$outside_log" "$log_dir/guard.log"

  output="$(run_gemini_tool_guard "$log_dir" block '{"tool_name":"run_shell_command","tool_input":"echo safe"}' 2>"$workdir/symlink-stderr")"
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected a linked Gemini log destination to fail closed."
  assert_equals "$original_outside" "$(cat "$outside_log")" \
    "Expected no-follow logging to leave the linked target unchanged."
}

test_warn_mode_returns_json_for_gemini_payload() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  log_dir="$workdir/logs"

  output="$(
    run_gemini_tool_guard \
      "$log_dir" \
      warn \
      '{"session_id":"cli-session","tool_name":"run_shell_command","tool_input":"rm -rf ."}'
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected warn mode to allow the tool after logging threats."
  assert_file_contains "$log_dir/guard.log" '"event":"threats_detected"' \
    "Expected warn mode to log detected threats."

  local expected_msg
  expected_msg="Tool Guardian warning run_shell_command. destructive_file_ops/critical [recursive_remove_current]: recursive forced removal targets the current directory. Action: rm -rf .. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."
  assert_equals "$expected_msg" "$(jq -r '.systemMessage' <<<"$output")" \
    "Expected warn mode to include correct warning systemMessage."
}

test_block_mode_denies_gemini_payload() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  log_dir="$workdir/logs"

  output="$(
    run_gemini_tool_guard \
      "$log_dir" \
      block \
      '{"hook_event_name":"BeforeTool","session_id":"vscode-session","tool_name":"run_shell_command","tool_input":{"command":"git push --force origin main"}}'
  )"

  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected block mode to deny detected destructive operations."
  assert_file_contains "$log_dir/guard.log" '"tool":"run_shell_command"' \
    "Expected guard log to record the Gemini tool name."

  local expected_msg
  expected_msg="Tool Guardian blocked run_shell_command. destructive_git_ops/critical [force_push_protected_branch]: forced push targets a protected branch. Action: git push --force origin main; {\"command\":\"git push --force origin main\"}. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."
  assert_equals "$expected_msg" "$(jq -r '.reason' <<<"$output")" \
    "Expected block mode to include correct block reason."
  assert_equals "null" "$(jq -r '.systemMessage' <<<"$output")" \
    "Expected Gemini denial reason to avoid duplicate native display."
}

test_block_mode_parses_gemini_tool_input_objects() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  log_dir="$workdir/logs"

  output="$(
    run_gemini_tool_guard \
      "$log_dir" \
      block \
      '{"session_id":"cli-object","tool_name":"run_shell_command","tool_input":{"command":"DROP TABLE users;"}}'
  )"

  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected block mode to inspect object-valued tool_input."
  assert_file_contains "$log_dir/guard.log" '"category":"database_destruction"' \
    "Expected guard log to capture threat details from object-valued tool_input."

  local expected_msg
  expected_msg="Tool Guardian blocked run_shell_command. database_destruction/critical [drop_table]: SQL drops a table. Action: DROP TABLE; {\"command\":\"DROP TABLE users;\"}. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."
  assert_equals "$expected_msg" "$(jq -r '.reason' <<<"$output")" \
    "Expected block mode to include correct reason for object-valued input."
  assert_equals "null" "$(jq -r '.systemMessage' <<<"$output")" \
    "Expected Gemini denial reason to avoid duplicate native display."
}

test_nested_structured_tool_input_scans_decoded_string_values() {
  local workdir
  local log_dir
  local query
  local payload
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  log_dir="$workdir/logs"

  query="DELETE"; query+=" FROM"; query+=" users"
  payload="$(jq -cn --arg query "$query" '{tool_name:"database_query",tool_input:{request:{query:$query},options:{timeout:5}}}')"
  output="$(run_gemini_tool_guard "$log_dir" block "$payload")"
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected Gemini to scan decoded query strings nested in object-valued tool input."

  query="SELECT id"; query+=" FROM users"; query+=" WHERE id = 1"
  payload="$(jq -cn --arg query "$query" '{tool_name:"database_query",tool_input:{request:{query:$query},options:{timeout:5}}}')"
  output="$(run_gemini_tool_guard "$log_dir" block "$payload")"
  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected safe nested structured Gemini input to remain allowed."
}

test_skip_mode_returns_explicit_allow_json() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  log_dir="$workdir/logs"

  output="$(
    TOOL_GUARD_LOG_DIR="$log_dir" \
    GUARD_MODE="block" \
    SKIP_TOOL_GUARD="true" \
    python3 "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.py" \
      <<<'{"session_id":"skip-session","tool_name":"run_shell_command","tool_input":"echo ok"}'
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected skip mode to return an explicit allow decision."
}

test_gemini_settings_register_tool_guard() {
  python3 - "$REPO_ROOT/.gemini/global-settings.json" <<'PYTEST'
import json
from pathlib import Path
import sys

settings = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
commands = [
    hook["command"]
    for group in settings["hooks"]["BeforeTool"] if group.get("matcher") == "*"
    for hook in group["hooks"]
]
observability = 'python "$HOME/.gemini/hooks/scripts/send-event.py"'
guard = 'python "$HOME/.gemini/hooks/scripts/tool-guard.py"'
assert commands.count(observability) == 1, "Expected one Gemini observability handler."
assert commands.count(guard) == 1, "Expected one Gemini Tool Guardian handler."
assert commands.index(observability) < commands.index(guard), "Expected Tool Guardian after observability."
PYTEST
}

test_tool_guard_denies_invalid_payload() {
  local log_dir
  local output

  log_dir="$(setup_test_workdir)/logs"

  output="$(
    run_gemini_tool_guard \
      "$log_dir" \
      block \
      "not-even-json"
  )"

  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected Gemini Tool Guardian to deny malformed inputs (fail-closed)."

  output="$(
    run_gemini_tool_guard \
      "$log_dir" \
      block \
      "[]"
  )"

  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected Gemini Tool Guardian to deny non-object inputs."
}

test_tool_guard_denies_unexpected_input_exception() {
  local workdir
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  mkdir -p "$workdir/helpers"
  cp "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.py" "$workdir/tool-guard.py"
  cp "$REPO_ROOT/.gemini/hooks/scripts/helpers/tool_guard_policy.py" "$workdir/helpers/tool_guard_policy.py"
  printf '%s\n' \
    'import json' \
    'import sys' \
    'def emit_json(payload):' \
    '    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")' \
    'def read_json_input():' \
    '    raise RuntimeError("forced input failure")' \
    >"$workdir/helpers/common.py"

  output="$(python3 "$workdir/tool-guard.py" <<<'{}' 2>"$workdir/stderr")"

  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected Gemini Tool Guardian to deny unexpected input failures."
  assert_equals "Tool Guardian skipped: unexpected exception." \
    "$(jq -r '.reason' <<<"$output")" \
    "Expected the fail-closed Gemini envelope for unexpected input failures."
  assert_file_contains "$workdir/stderr" 'RuntimeError' \
    "Expected the unexpected input failure to be diagnosed on stderr."
}

main() {
  test_structured_allowlist_is_tool_scoped_and_exact
  test_equivalent_and_json_encoded_threats_are_denied
  test_parser_limits_and_complete_command_forms_fail_closed
  test_home_variable_removals_and_git_global_options_are_denied
  test_block_response_and_audit_omit_sensitive_evidence
  test_gemini_log_is_owner_only_locked_and_no_follow
  test_warn_mode_returns_json_for_gemini_payload
  test_block_mode_denies_gemini_payload
  test_block_mode_parses_gemini_tool_input_objects
  test_nested_structured_tool_input_scans_decoded_string_values
  test_skip_mode_returns_explicit_allow_json
  test_gemini_settings_register_tool_guard
  test_tool_guard_denies_invalid_payload
  test_tool_guard_denies_unexpected_input_exception
  test_tool_guard_rm_env_and_rm_git
}

security_run_suite main "$@"

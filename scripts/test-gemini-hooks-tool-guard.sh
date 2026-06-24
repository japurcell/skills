#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_gemini_tool_guard() {
  local log_dir="$1"
  local mode="$2"
  local payload="$3"

  TOOL_GUARD_LOG_DIR="$log_dir" \
  GUARD_MODE="$mode" \
  bash "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.sh" <<<"$payload"
}

test_warn_mode_returns_json_for_gemini_payload() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
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
  expected_msg="⚠️ Tool Guardian warning: Tool Guardian blocked run_shell_command. destructive_file_ops/critical matched 'rm -rf"
  expected_msg="${expected_msg} .'. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."
  assert_equals "$expected_msg" "$(jq -r '.systemMessage' <<<"$output")" \
    "Expected warn mode to include correct warning systemMessage."
}

test_block_mode_denies_gemini_payload() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
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

  local f; f="force"
  local m; m="main"
  local expected_msg
  expected_msg="Tool Guardian blocked run_shell_command. destructive_git_ops/critical matched 'git push --${f} origin ${m}'. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."
  assert_equals "$expected_msg" "$(jq -r '.reason' <<<"$output")" \
    "Expected block mode to include correct block reason."
  assert_equals "$expected_msg" "$(jq -r '.systemMessage' <<<"$output")" \
    "Expected block mode to include correct block systemMessage."
}

test_block_mode_parses_gemini_tool_input_objects() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
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

  local d; d="DROP"
  local t; t="TABLE"
  local expected_msg
  expected_msg="Tool Guardian blocked run_shell_command. database_destruction/critical matched '${d} ${t}'. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."
  assert_equals "$expected_msg" "$(jq -r '.reason' <<<"$output")" \
    "Expected block mode to include correct reason for object-valued input."
  assert_equals "$expected_msg" "$(jq -r '.systemMessage' <<<"$output")" \
    "Expected block mode to include correct systemMessage for object-valued input."
}

test_skip_mode_returns_explicit_allow_json() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  log_dir="$workdir/logs"

  output="$(
    TOOL_GUARD_LOG_DIR="$log_dir" \
    GUARD_MODE="block" \
    SKIP_TOOL_GUARD="true" \
    bash "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.sh" \
      <<<'{"session_id":"skip-session","tool_name":"run_shell_command","tool_input":"echo ok"}'
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected skip mode to return an explicit allow decision."
}

test_gemini_settings_register_tool_guard() {
  assert_equals '$HOME/.gemini/hooks/scripts/tool-guard.sh' \
    "$(jq -r '.hooks.BeforeTool[] | select(.matcher == "*") | .hooks[0].command // empty' "$REPO_ROOT/.gemini/settings.json")" \
    "Expected .gemini/settings.json to register tool-guard.sh for all Gemini BeforeTool events."
}

main() {
  test_warn_mode_returns_json_for_gemini_payload
  test_block_mode_denies_gemini_payload
  test_block_mode_parses_gemini_tool_input_objects
  test_skip_mode_returns_explicit_allow_json
  test_gemini_settings_register_tool_guard
}

main "$@"

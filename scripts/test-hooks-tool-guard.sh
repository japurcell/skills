#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_tool_guard() {
  local log_dir="$1"
  local mode="$2"
  local payload="$3"

  TOOL_GUARD_LOG_DIR="$log_dir/guard.log" \
  GUARD_MODE="$mode" \
  bash "$REPO_ROOT/.copilot/hooks/scripts/tool-guard.sh" <<<"$payload"
}

test_common_allowlist_helpers_trim_and_match() {
  local output

  output="$(
    bash -c '
      set -euo pipefail
      repo_root="$1"
      risky_delete="rm -rf ""."
      risky_db="DROP"" TABLE"

      source "$repo_root/.copilot/hooks/scripts/common.sh"
      parse_allowlist_csv " $risky_delete ,  $risky_db  ,   " ALLOWLIST

      allowlist_contains "bash $risky_delete" "${ALLOWLIST[@]}" || exit 10
      allowlist_contains "bash ${risky_db} users;" "${ALLOWLIST[@]}" || exit 11
      if allowlist_contains "bash echo safe" "${ALLOWLIST[@]}"; then
        exit 12
      fi

      printf "ok"
    ' _ "$REPO_ROOT" 2>/dev/null || true
  )"

  assert_equals "ok" "$output" \
    "Expected shared allowlist helpers to parse, trim, and match entries."
}

test_warn_mode_returns_json_for_cli_payload() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  log_dir="$workdir/logs"

  output="$(
    run_tool_guard \
      "$log_dir" \
      warn \
      '{"sessionId":"cli-session","toolName":"bash","toolArgs":"rm -rf ."}'
  )"

  assert_equals "allow" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected warn mode to allow the tool after logging threats."
  assert_equals "allow" "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$output")" \
    "Expected warn mode to include a VS Code-compatible allow decision."
  assert_file_contains "$log_dir/guard.log" '"event":"threats_detected"' \
    "Expected warn mode to log detected threats."
}

test_block_mode_denies_vscode_payload() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
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
  trap 'rm -rf "'"$workdir"'"' RETURN
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

test_skip_mode_returns_explicit_allow_json() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  log_dir="$workdir/logs"

  output="$(
    TOOL_GUARD_LOG_DIR="$log_dir/guard.log" \
    GUARD_MODE="block" \
    SKIP_TOOL_GUARD="true" \
    bash "$REPO_ROOT/.copilot/hooks/scripts/tool-guard.sh" \
      <<<'{"sessionId":"skip-session","toolName":"bash","toolArgs":"echo ok"}'
  )"

  assert_equals "allow" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected skip mode to return an explicit allow permissionDecision."
  assert_equals "allow" "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$output")" \
    "Expected skip mode to keep VS Code-compatible allow output."
}

main() {
  test_common_allowlist_helpers_trim_and_match
  test_warn_mode_returns_json_for_cli_payload
  test_block_mode_denies_vscode_payload
  test_block_mode_parses_cli_tool_args_objects
  test_skip_mode_returns_explicit_allow_json
}

main "$@"

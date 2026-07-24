#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_gemini_passive_hook() {
  local hook_name="$1"
  local audit_log="$2"
  local payload="$3"
  local mode="${4:-}"
  local shadow_log="${5:-}"

  local env_cmd=("AUDIT_LOG=$audit_log")
  if [[ -n "$mode" ]]; then
    env_cmd+=("GEMINI_PASSIVE_LOG_MODE=$mode")
  fi
  if [[ -n "$shadow_log" ]]; then
    env_cmd+=("GEMINI_PASSIVE_SHADOW_LOG=$shadow_log")
  fi

  env "${env_cmd[@]}" bash "$REPO_ROOT/.gemini/hooks/scripts/$hook_name" <<<"$payload"
}

assert_json_object_output() {
  local output="$1"
  local message="$2"

  if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$output"; then
    echo "$message" >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
}

test_gemini_audit_init_returns_nonzero_without_exiting_shell() {
  local output
  local bash_path

  bash_path="$(command -v bash)"

  output="$(
    env PATH=/nonexistent "$bash_path" -c '
      set -euo pipefail
      source "$1"
      if audit_init; then
        printf "unexpected-success"
      else
        printf "returned-%s" "$?"
      fi
    ' _ "$REPO_ROOT/.gemini/hooks/scripts/audit.sh" 2>/dev/null
  )"

  assert_equals "returned-1" "$output" \
    "Expected Gemini audit_init to return nonzero instead of exiting the caller shell."
}

test_hook_scripts_use_passive_audit_helper() {
  local scripts_dir="$REPO_ROOT/.gemini/hooks/scripts"
  local script

  for script in \
    "$scripts_dir/log-after-agent.sh" \
    "$scripts_dir/log-before-agent.sh" \
    "$scripts_dir/log-notification.sh" \
    "$scripts_dir/log-post-tooluse.sh" \
    "$scripts_dir/log-pre-tooluse.sh" \
    "$scripts_dir/log-session-end.sh" \
    "$scripts_dir/log-session-start.sh"
  do
    assert_file_contains "$script" 'audit.sh' \
      "Expected $script to source audit.sh."
    assert_file_contains "$script" 'audit_init' \
      "Expected $script to initialize audit logging with audit_init."
    assert_file_contains "$script" 'audit_log_passive_event' \
      "Expected $script to log through audit_log_passive_event."
  done
}

test_default_mode_keeps_primary_passive_log_path() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(
    run_gemini_passive_hook \
      "log-before-agent.sh" \
      "$audit_log" \
      '{"session_id":"default-mode","timestamp":"2026-06-24T00:00:00Z","prompt":"hello"}'
  )"

  assert_equals "{}" "$output" \
    "Expected passive log hook to keep machine-readable JSON output."
  assert_file_contains "$audit_log" "Session: default-mode" \
    "Expected default passive mode to keep writing to the primary audit log."
}

test_shadow_mode_is_additive() {
  local workdir
  local audit_log
  local shadow_log

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  shadow_log="$workdir/passive-shadow.log"

  run_gemini_passive_hook \
    "log-before-agent.sh" \
    "$audit_log" \
    '{"session_id":"shadow-mode","timestamp":"2026-06-24T00:00:01Z","prompt":"hello"}' \
    "shadow" \
    "$shadow_log" \
    >/dev/null

  assert_file_contains "$audit_log" "Session: shadow-mode" \
    "Expected shadow mode to remain additive and keep primary audit logging."
  assert_file_contains "$shadow_log" "Session: shadow-mode" \
    "Expected shadow mode to write a passive shadow log copy."
}

test_shadow_mode_creates_nested_shadow_log_directory() {
  local workdir
  local audit_log
  local shadow_log

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  shadow_log="$workdir/nested/shadow/passive-shadow.log"

  run_gemini_passive_hook \
    "log-before-agent.sh" \
    "$audit_log" \
    '{"session_id":"shadow-nested-mode","timestamp":"2026-06-24T00:00:02Z","prompt":"hello"}' \
    "shadow" \
    "$shadow_log" \
    >/dev/null

  assert_file_contains "$audit_log" "Session: shadow-nested-mode" \
    "Expected nested shadow mode to keep primary audit logging."
  assert_file_contains "$shadow_log" "Session: shadow-nested-mode" \
    "Expected shadow mode to create nested shadow-log directory and write log."
}

test_shadow_mode_uses_shared_lock_for_primary_and_shadow_logs() {
  local workdir
  local audit_log
  local shadow_log
  local shadow_lock

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  shadow_log="$workdir/passive-shadow.log"
  shadow_lock="$workdir/passive-shadow.lock"

  GEMINI_PASSIVE_LOG_MODE=shadow \
    GEMINI_PASSIVE_SHADOW_LOG="$shadow_log" \
    GEMINI_PASSIVE_SHADOW_LOCK="$shadow_lock" \
    AUDIT_LOG="$audit_log" \
    bash "$REPO_ROOT/.gemini/hooks/scripts/log-before-agent.sh" \
    <<<'{"session_id":"shared-lock","timestamp":"2026-06-24T00:00:03Z","prompt":"hello"}' \
    >/dev/null

  [[ ! -e "$shadow_lock" ]] || fail \
    "Expected passive shadow logging to share the primary audit lock instead of creating a dedicated shadow lock file."
}

test_invalid_json_degrades_to_noop_json() {
  local workdir
  local audit_log
  local output
  local hook_name

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  for hook_name in \
    log-session-start.sh \
    log-before-agent.sh \
    log-after-agent.sh \
    log-notification.sh \
    log-session-end.sh
  do
    output="$(run_gemini_passive_hook "$hook_name" "$audit_log" 'not-json')"
    assert_equals "{}" "$output" \
      "Expected $hook_name to degrade invalid input to a no-op JSON response."
  done

  for hook_name in log-pre-tooluse.sh log-post-tooluse.sh; do
    output="$(run_gemini_passive_hook "$hook_name" "$audit_log" 'not-json')"
    assert_json_object_output "$output" \
      "Expected $hook_name to keep invalid-input output JSON-safe."
    assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
      "Expected $hook_name to explicitly allow when invalid input is ignored."
  done
}

test_notification_hook_logs_valid_payload() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(
    run_gemini_passive_hook \
      "log-notification.sh" \
      "$audit_log" \
      '{"session_id":"notification-session","timestamp":"2026-06-24T00:00:04Z","notification_type":"ToolPermission","message":"permission needed","details":{"tool_name":"run_shell_command"}}'
  )"

  assert_equals "{}" "$output" \
    "Expected notification hook to keep machine-readable JSON output."
  assert_file_contains "$audit_log" "session_id: notification-session" \
    "Expected notification hook to log the session ID from valid input."
  assert_file_contains "$audit_log" "notification_type: ToolPermission" \
    "Expected notification hook to log the notification type from valid input."
  assert_file_contains "$audit_log" "message: permission needed" \
    "Expected notification hook to log the message from valid input."
  assert_file_contains "$audit_log" 'details: {"tool_name":"run_shell_command"}' \
    "Expected notification hook to log details from valid input."
}

test_gemini_settings_keep_required_safety_hooks() {
  assert_equals '$HOME/.gemini/hooks/scripts/tool-guard.sh' \
    "$(jq -r '.hooks.BeforeTool[] | select(.matcher == "*") | .hooks[] | select(.name == "tool-guard") | .command // empty' "$REPO_ROOT/.gemini/settings.json")" \
    "Expected .gemini/settings.json to keep tool-guard wired."
  assert_equals '$HOME/.gemini/hooks/scripts/scan-secrets.sh' \
    "$(jq -r '.hooks.SessionEnd[] | .hooks[] | select(.name == "scan-secrets") | .command // empty' "$REPO_ROOT/.gemini/settings.json")" \
    "Expected .gemini/settings.json to keep scan-secrets wired."
}

main() {
  test_gemini_audit_init_returns_nonzero_without_exiting_shell
  test_hook_scripts_use_passive_audit_helper
  test_default_mode_keeps_primary_passive_log_path
  test_shadow_mode_is_additive
  test_shadow_mode_creates_nested_shadow_log_directory
  test_shadow_mode_uses_shared_lock_for_primary_and_shadow_logs
  test_invalid_json_degrades_to_noop_json
  test_notification_hook_logs_valid_payload
  test_gemini_settings_keep_required_safety_hooks
}

main "$@"

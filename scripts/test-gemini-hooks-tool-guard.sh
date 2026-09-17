#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_gemini_tool_guard() {
  local log_dir="$1"
  local mode="$2"
  local payload="$3"

  TOOL_GUARD_LOG_DIR="$log_dir" \
  GUARD_MODE="$mode" \
  python3 "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.py" <<<"$payload"
}

test_structured_allowlist_is_tool_scoped_and_exact() {
  local workdir
  local log_dir
  local risky_input
  local allowlist
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  log_dir="$workdir/logs"
  risky_input="git push"
  risky_input+=" --force"
  risky_input+=" origin main"
  allowlist="$(jq -cn --arg tool run_shell_command --arg input "$risky_input" '[{tool:$tool,input:$input}]')"

  output="$(
    TOOL_GUARD_LOG_DIR="$log_dir" TOOL_GUARD_ALLOWLIST="$allowlist" GUARD_MODE=block \
      python3 "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.py" \
      <<<"$(jq -cn --arg input "$risky_input" '{tool_name:"run_shell_command",tool_input:$input}')"
  )"
  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected an exact tool-scoped Gemini allowlist entry to allow its declared invocation."

  output="$(
    TOOL_GUARD_LOG_DIR="$log_dir" TOOL_GUARD_ALLOWLIST="$allowlist" GUARD_MODE=block \
      python3 "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.py" \
      <<<"$(jq -cn --arg input "$risky_input && echo unsafe" '{tool_name:"run_shell_command",tool_input:$input}')"
  )"
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected surrounding content to invalidate a Gemini allowlist input."

  output="$(
    TOOL_GUARD_LOG_DIR="$log_dir" TOOL_GUARD_ALLOWLIST="$allowlist" GUARD_MODE=block \
      python3 "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.py" \
      <<<"$(jq -cn --arg input "$risky_input" '{tool_name:"write_file",tool_input:$input}')"
  )"
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected a Gemini allowlist entry to remain scoped to its declared tool."
}

test_equivalent_and_json_encoded_threats_are_denied() {
  local workdir
  local log_dir
  local reordered_remove
  local trailing_force
  local unfiltered_delete
  local encoded_payload
  local risky_input
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  log_dir="$workdir/logs"
  reordered_remove="rm"
  reordered_remove+=" -fr"
  reordered_remove+=" /"
  trailing_force="git push"
  trailing_force+=" origin main"
  trailing_force+=" --force"
  unfiltered_delete="DELETE"
  unfiltered_delete+=" FROM"
  unfiltered_delete+=" users"

  for risky_input in "$reordered_remove" "$trailing_force" "$unfiltered_delete"; do
    output="$(run_gemini_tool_guard "$log_dir" block "$(jq -cn --arg input "$risky_input" '{tool_name:"run_shell_command",tool_input:$input}')")"
    assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
      "Expected equivalent destructive syntax to remain blocked by Gemini."
  done

  encoded_payload="$(python3 - "$trailing_force" <<'PY'
import sys

encoded = "".join(f"\\u{ord(character):04x}" for character in sys.argv[1])
print('{"tool_name":"run_shell_command","tool_input":"' + encoded + '"}')
PY
  )"
  output="$(run_gemini_tool_guard "$log_dir" block "$encoded_payload")"
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected JSON-escaped destructive syntax to be decoded and blocked by Gemini."
}

test_block_response_and_log_redact_sensitive_values() {
  local workdir
  local log_dir
  local url_password
  local query_token
  local bearer_token
  local api_key
  local risky_input
  local payload
  local output
  local sensitive_value

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  log_dir="$workdir/logs"
  url_password="fake-url-password"
  query_token="fake-query-token"
  bearer_token="fake-bearer-token"
  api_key="fake-api-key"
  risky_input="rm Authorization: Bearer ${bearer_token} API_KEY=${api_key} .env && git push"
  risky_input+=" https://tester:${url_password}@example.invalid/repo?access_token=${query_token}"
  risky_input+=" origin main"
  risky_input+=" --force"
  payload="$(jq -cn --arg input "$risky_input" '{tool_name:"run_shell_command",tool_input:$input}')"

  output="$(run_gemini_tool_guard "$log_dir" block "$payload")"
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected Gemini to deny the sensitive destructive invocation."
  assert_file_contains "$log_dir/guard.log" '[REDACTED]' \
    "Expected redaction markers in the Gemini Tool Guardian log."
  if ! jq -e 'select(.event == "threats_detected") | all(.threats[]; (keys | sort) == ["category","excerpt","severity"])' \
    "$log_dir/guard.log" >/dev/null; then
    echo "Expected Gemini log threats to contain only category, severity, and redacted excerpt fields." >&2
    exit 1
  fi

  for sensitive_value in "$url_password" "$query_token" "$bearer_token" "$api_key"; do
    if [[ "$output" == *"$sensitive_value"* ]]; then
      echo "Expected Gemini block output to redact sensitive values." >&2
      exit 1
    fi
    if grep -Fq "$sensitive_value" "$log_dir/guard.log"; then
      echo "Expected Gemini Tool Guardian log output to redact sensitive values." >&2
      exit 1
    fi
  done
}

test_gemini_log_is_owner_only_locked_and_no_follow() {
  local workdir
  local log_dir
  local process_id
  local output
  local outside_log
  local original_outside

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  log_dir="$workdir/logs"
  mkdir -p "$log_dir"
  printf 'existing\n' >"$log_dir/guard.log"
  chmod 666 "$log_dir/guard.log"
  output="$(run_gemini_tool_guard "$log_dir" block '{"tool_name":"run_shell_command","tool_input":"echo safe"}')"
  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected a safe invocation to create the hardened Gemini log."
  assert_equals "600" "$(stat -c '%a' "$log_dir/guard.log")" \
    "Expected the Gemini Tool Guardian log to be owner-only."
  assert_equals "600" "$(stat -c '%a' "$log_dir/guard.log.lock")" \
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
  expected_msg="⚠️ Tool Guardian warning: Tool Guardian blocked run_shell_command. destructive_file_ops/critical near 'rm -rf"
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
  expected_msg="Tool Guardian blocked run_shell_command. destructive_git_ops/critical near 'git push --${f} origin ${m}'. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."
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
  expected_msg="Tool Guardian blocked run_shell_command. database_destruction/critical near '${d} ${t}'. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."
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
    python3 "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.py" \
      <<<'{"session_id":"skip-session","tool_name":"run_shell_command","tool_input":"echo ok"}'
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected skip mode to return an explicit allow decision."
}

test_gemini_settings_register_tool_guard() {
  assert_equals 'python "$HOME/.gemini/hooks/scripts/send-event.py"' \
    "$(jq -r '.hooks.BeforeTool[] | select(.matcher == "*") | .hooks[0].command // empty' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected .gemini/global-settings.json to register send-event.py before Gemini BeforeTool events."
  assert_equals 'python "$HOME/.gemini/hooks/scripts/tool-guard.py"' \
    "$(jq -r '.hooks.BeforeTool[] | select(.matcher == "*") | .hooks[1].command // empty' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected .gemini/global-settings.json to register tool-guard.py after observability for all Gemini BeforeTool events."
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
  trap 'rm -rf "'"$workdir"'"' RETURN
  mkdir -p "$workdir/helpers"
  cp "$REPO_ROOT/.gemini/hooks/scripts/tool-guard.py" "$workdir/tool-guard.py"
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
  assert_file_contains "$workdir/stderr" 'forced input failure' \
    "Expected the unexpected input failure to be diagnosed on stderr."
}

test_tool_guard_rm_env_and_rm_git() {
  local workdir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  local trap_cmd; trap_cmd="rm"
  trap_cmd+=" -rf"
  trap_cmd+=" \"$workdir\""
  trap "$trap_cmd" RETURN
  log_dir="$workdir/logs"

  local test_env; test_env="rm"
  test_env+=" .env"
  output="$(
    run_gemini_tool_guard \
      "$log_dir" \
      block \
      "{\"session_id\":\"cli-session\",\"tool_name\":\"run_shell_command\",\"tool_input\":\"${test_env}\"}"
  )"
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected delete env to be blocked."

  local test_git; test_git="rm"
  test_git+=" -rf"
  test_git+=" .git"
  output="$(
    run_gemini_tool_guard \
      "$log_dir" \
      block \
      "{\"session_id\":\"cli-session\",\"tool_name\":\"run_shell_command\",\"tool_input\":\"${test_git}\"}"
  )"
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected delete git to be blocked."

  local benign_payload
  benign_payload='{"session_id":"cli-session","tool_name":"write_file","tool_input":{"file_path":"test.py","content":"def clean():\n    unlink()\n\nos.environ"}}'
  output="$(
    run_gemini_tool_guard \
      "$log_dir" \
      block \
      "$benign_payload"
  )"
  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected benign multiline clean function and environment lookups to be allowed."
}

main() {
  test_structured_allowlist_is_tool_scoped_and_exact
  test_equivalent_and_json_encoded_threats_are_denied
  test_block_response_and_log_redact_sensitive_values
  test_gemini_log_is_owner_only_locked_and_no_follow
  test_warn_mode_returns_json_for_gemini_payload
  test_block_mode_denies_gemini_payload
  test_block_mode_parses_gemini_tool_input_objects
  test_skip_mode_returns_explicit_allow_json
  test_gemini_settings_register_tool_guard
  test_tool_guard_denies_invalid_payload
  test_tool_guard_denies_unexpected_input_exception
  test_tool_guard_rm_env_and_rm_git
}

main "$@"

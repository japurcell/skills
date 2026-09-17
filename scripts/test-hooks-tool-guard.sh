#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_tool_guard() {
  local log_dir="$1"
  local mode="$2"
  local payload="$3"

  TOOL_GUARD_LOG_DIR="$log_dir/guard.log" \
  GUARD_MODE="$mode" \
  python3 "$REPO_ROOT/.copilot/hooks/scripts/tool-guard.py" <<<"$payload"
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
  allowlist="$(jq -cn --arg tool bash --arg input "$risky_input" '[{tool:$tool,input:$input}]')"

  output="$(
    TOOL_GUARD_LOG_DIR="$log_dir/guard.log" TOOL_GUARD_ALLOWLIST="$allowlist" GUARD_MODE=block \
      python3 "$REPO_ROOT/.copilot/hooks/scripts/tool-guard.py" \
      <<<"$(jq -cn --arg input "$risky_input" '{toolName:"bash",toolArgs:$input}')"
  )"
  assert_equals "allow" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected an exact tool-scoped allowlist entry to allow only its declared invocation."

  output="$(
    TOOL_GUARD_LOG_DIR="$log_dir/guard.log" TOOL_GUARD_ALLOWLIST="$allowlist" GUARD_MODE=block \
      python3 "$REPO_ROOT/.copilot/hooks/scripts/tool-guard.py" \
      <<<"$(jq -cn --arg input "echo safe && $risky_input" '{toolName:"bash",toolArgs:$input}')"
  )"
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected surrounding content to invalidate an otherwise matching allowlist input."

  output="$(
    TOOL_GUARD_LOG_DIR="$log_dir/guard.log" TOOL_GUARD_ALLOWLIST="$allowlist" GUARD_MODE=block \
      python3 "$REPO_ROOT/.copilot/hooks/scripts/tool-guard.py" \
      <<<"$(jq -cn --arg input "$risky_input" '{toolName:"write_file",toolArgs:$input}')"
  )"
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected the same input under a different tool to remain blocked."

  output="$(
    TOOL_GUARD_LOG_DIR="$log_dir/guard.log" TOOL_GUARD_ALLOWLIST="$risky_input" GUARD_MODE=block \
      python3 "$REPO_ROOT/.copilot/hooks/scripts/tool-guard.py" \
      <<<"$(jq -cn --arg input "$risky_input" '{toolName:"bash",toolArgs:$input}')"
  )"
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected legacy unstructured allowlist text to fail closed."
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
    output="$(run_tool_guard "$log_dir" block "$(jq -cn --arg input "$risky_input" '{toolName:"bash",toolArgs:$input}')")"
    assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
      "Expected equivalent destructive syntax to remain blocked."
  done

  encoded_payload="$(python3 - "$trailing_force" <<'PY'
import sys

encoded = "".join(f"\\u{ord(character):04x}" for character in sys.argv[1])
print('{"toolName":"bash","toolArgs":"' + encoded + '"}')
PY
  )"
  output="$(run_tool_guard "$log_dir" block "$encoded_payload")"
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected JSON-escaped destructive syntax to be decoded and blocked."
}

test_block_response_and_audit_redact_sensitive_values() {
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
  payload="$(jq -cn --arg input "$risky_input" '{toolName:"bash",toolArgs:$input}')"

  output="$(run_tool_guard "$log_dir" block "$payload")"
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected the sensitive destructive invocation to be denied."
  assert_file_contains "$log_dir/guard.log" '[REDACTED]' \
    "Expected redaction markers in the Tool Guardian audit record."
  if grep -Fq '"match":' "$log_dir/guard.log" || grep -Fq '"suggestion":' "$log_dir/guard.log"; then
    echo "Expected audit threats to contain only category, severity, and redacted excerpt fields." >&2
    exit 1
  fi

  for sensitive_value in "$url_password" "$query_token" "$bearer_token" "$api_key"; do
    if [[ "$output" == *"$sensitive_value"* ]]; then
      echo "Expected block output to redact sensitive values." >&2
      exit 1
    fi
    if grep -Fq "$sensitive_value" "$log_dir/guard.log"; then
      echo "Expected Tool Guardian audit output to redact sensitive values." >&2
      exit 1
    fi
  done
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
  expected_warning="⚠️ Tool Guardian warning: Tool Guardian blocked bash. destructive_file_ops/critical near '${risky_delete}'. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."

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
  trap 'rm -rf "'"$workdir"'"' RETURN
  mkdir -p "$workdir/helpers"
  cp "$REPO_ROOT/.copilot/hooks/scripts/tool-guard.py" "$workdir/tool-guard.py"
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
    run_tool_guard \
      "$log_dir" \
      block \
      "{\"sessionId\":\"cli-session\",\"toolName\":\"bash\",\"toolArgs\":\"${test_env}\"}"
  )"
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected delete env to be blocked."

  local test_git; test_git="rm"
  test_git+=" -rf"
  test_git+=" .git"
  output="$(
    run_tool_guard \
      "$log_dir" \
      block \
      "{\"sessionId\":\"cli-session\",\"toolName\":\"bash\",\"toolArgs\":\"${test_git}\"}"
  )"
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected delete git to be blocked."

  local benign_payload
  benign_payload='{"sessionId":"cli-session","toolName":"bash","toolArgs":{"file_path":"test.py","content":"def clean():\n    unlink()\n\nos.environ"}}'
  output="$(
    run_tool_guard \
      "$log_dir" \
      block \
      "$benign_payload"
  )"
  assert_equals "allow" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected benign multiline clean function and environment lookups to be allowed."
}

main() {
  test_structured_allowlist_is_tool_scoped_and_exact
  test_equivalent_and_json_encoded_threats_are_denied
  test_block_response_and_audit_redact_sensitive_values
  test_warn_mode_returns_json_for_cli_payload
  test_block_mode_denies_vscode_payload
  test_block_mode_parses_cli_tool_args_objects
  test_skip_mode_returns_explicit_allow_json
  test_tool_guard_denies_invalid_payload
  test_tool_guard_denies_unexpected_input_exception
  test_tool_guard_rm_env_and_rm_git
}

main "$@"

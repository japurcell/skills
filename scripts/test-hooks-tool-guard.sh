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

test_common_allowlist_helpers_trim_and_match() {
  local output

  output="$(
    python3 - "$REPO_ROOT" <<'PY'
import sys
import importlib.util
from pathlib import Path

repo_root = Path(sys.argv[1])
tool_guard_path = repo_root / ".copilot/hooks/scripts/tool-guard.py"
sys.path.insert(0, str(tool_guard_path.parent))
spec = importlib.util.spec_from_file_location("copilot_tool_guard", tool_guard_path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

risky_delete = "rm" + " -rf" + " ."
risky_db = "DROP" + " TABLE"
allowlist = module.parse_allowlist_csv(f" {risky_delete} ,  {risky_db}  ,   ")

if not module.allowlist_contains(f"bash {risky_delete}", allowlist):
    raise SystemExit(10)
if not module.allowlist_contains(f"bash {risky_db} users;", allowlist):
    raise SystemExit(11)
if module.allowlist_contains("bash echo safe", allowlist):
    raise SystemExit(12)

print("ok")
PY
  )"

  assert_equals "ok" "$output" \
    "Expected shared allowlist helpers to parse, trim, and match entries."
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
  expected_warning="⚠️ Tool Guardian warning: Tool Guardian blocked bash. destructive_file_ops/critical matched '${risky_delete}'. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."

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

main() {
  test_common_allowlist_helpers_trim_and_match
  test_warn_mode_returns_json_for_cli_payload
  test_block_mode_denies_vscode_payload
  test_block_mode_parses_cli_tool_args_objects
  test_skip_mode_returns_explicit_allow_json
}

main "$@"

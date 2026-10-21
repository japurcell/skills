#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/security-test-support.sh"
source "$(dirname "${BASH_SOURCE[0]}")/scanner-test-support.sh"

SECURITY_SCANNER_LOG_SUFFIX=""
SECURITY_SCANNER_COMMAND=(python3 -I -S -B "$REPO_ROOT/.gemini/hooks/scripts/scan-secrets.py")

SECURITY_SCANNER_PROVIDER=gemini

security_scanner_payload() {
  local repo_dir="$1" session="$2" copilot_timestamp="$3" gemini_timestamp="$4"
  local copilot_reason="$5" gemini_event="$6" reason=exit
  if [[ "$gemini_event" == BeforeTool ]]; then reason=tool; fi
  jq -cn --arg session "$session" --arg timestamp "$gemini_timestamp" --arg event "$gemini_event" \
    --arg cwd "$repo_dir" --arg reason "$reason" \
    '{session_id:$session,timestamp:$timestamp,hook_event_name:$event,cwd:$cwd,reason:$reason}'
}

security_assert_scanner_denial() {
  assert_equals deny "$(jq -r '.decision' <<<"$1")" "Expected Gemini scanner denial."
}

security_scanner_denial_reason() {
  jq -r '.reason' <<<"$1"
}

run_gemini_scan_hook() {
  security_run_scan "$@"
}

test_invalid_json_degrades_to_noop_json() {
  local workdir
  local repo_dir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  output="$(
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      'not-json'
  )"

  assert_json_output "$output" "Expected invalid-input Gemini secrets scan to emit JSON."
  jq -e '.systemMessage | contains("scan-secrets warning") and contains("incomplete")' >/dev/null <<<"$output"
}

test_gemini_settings_register_status_and_session_end_handlers() {
  python3 - "$REPO_ROOT/.gemini/global-settings.json" <<'PY'
import json
import pathlib
import sys

hooks = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))["hooks"]
for event in ("AfterAgent", "SessionEnd"):
    handlers = [handler for group in hooks[event] for handler in group["hooks"]]
    command = 'python "$HOME/.gemini/hooks/scripts/send-event.py"'
    matches = [(index, handler) for index, handler in enumerate(handlers)
               if handler.get("command") == command]
    assert len(matches) == 1, f"Expected one observability registration on {event}"
    observer_index, observer = matches[0]
    assert observer["type"] == "command"
    assert observer["env"]["OBSERVABILITY_CAPTURE_EVENT"] == "true"
    assert observer["env"]["OBSERVABILITY_SOURCE_EVENT_NAME"] == event
    if event == "AfterAgent":
        status = [(index, handler) for index, handler in enumerate(handlers)
                  if handler.get("command") == 'python "$HOME/.gemini/hooks/scripts/scan-status.py"']
        assert len(status) == 1, "Expected one historical scan-status registration on AfterAgent"
        status_index, handler = status[0]
        assert handler["type"] == "command"
        # Keep the existing logical name so disabled-hook intent survives upgrades.
        assert handler["name"] == "scan-secrets"
        assert handler["timeout"] == 2000
        assert observer_index < status_index, "Expected observability before scan status"
PY
}

test_gemini_settings_register_before_tool_handlers() {
  python3 - "$REPO_ROOT/.gemini/global-settings.json" <<'PY'
import json
import pathlib
import sys

config = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
handlers = [(group, handler) for group in config["hooks"]["BeforeTool"] for handler in group["hooks"]]
positions = []
for script in ("send-event.py", "rtk-hook-gemini.py"):
    command = f'python "$HOME/.gemini/hooks/scripts/{script}"'
    matches = [(index, group, handler) for index, (group, handler) in enumerate(handlers)
               if handler.get("command") == command]
    assert len(matches) == 1, f"Expected one {script} registration on BeforeTool"
    index, group, handler = matches[0]
    positions.append(index)
    assert handler["type"] == "command"
    if script == "rtk-hook-gemini.py":
        assert group["matcher"] == "run_shell_command"
        assert handler["timeout"] == 5000
    else:
        assert group["matcher"] == "*"
        assert handler["env"]["OBSERVABILITY_CAPTURE_EVENT"] == "true"
        assert handler["env"]["OBSERVABILITY_SOURCE_EVENT_NAME"] == "BeforeTool"
assert positions[0] < positions[1], "Expected observability before RTK"
PY
}

main() {
  python3 "$REPO_ROOT/scripts/test-scan-secrets-capture.py" gemini
  test_stalled_git_is_bounded_by_timeout
  test_stalled_git_denies_in_block_mode
  test_failed_initial_git_probe_with_repo_marker_respects_fail_closed_mode
  test_missing_git_block_mode_uses_provider_denial_envelope
  test_audit_init_failure_block_mode_uses_provider_denial_envelope
  test_unexpected_exception_block_mode_denies_with_json_and_exit_zero
  test_unexpected_exception_warn_mode_warns_with_json_and_exit_zero
  test_warn_mode_reports_findings_without_failing
  test_high_match_input_has_bounded_denial_and_log
  test_env_variants_are_logged_but_not_flagged_by_path_alone
  test_warn_mode_flags_sensitive_credential_paths_without_token_match
  test_binary_credential_path_still_scans_ascii_tokens
  test_unusual_filename_and_double_plus_added_line_are_scanned
  test_committed_literal_pathspec_filename_is_scanned
  test_staged_scope_excludes_unrelated_untracked_files
  test_staged_zero_prefix_filename_is_scanned
  test_diff_scope_scans_cached_secret_when_worktree_matches_head
  test_generic_secrets_filename_stays_clean
  test_diff_mode_ignores_unchanged_secrets_in_touched_files
  test_diff_mode_ignores_secret_like_diff_headers
  test_allowlist_suppresses_credential_path_finding
  test_invalid_json_degrades_to_noop_json
  test_invalid_json_block_mode_denies_with_json_and_exit_zero
  test_gemini_settings_register_status_and_session_end_handlers
  test_gemini_settings_register_before_tool_handlers
}

security_run_suite main "$@"

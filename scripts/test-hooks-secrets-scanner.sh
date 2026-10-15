#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/security-test-support.sh"
source "$(dirname "${BASH_SOURCE[0]}")/scanner-test-support.sh"

SECURITY_SCANNER_LOG_SUFFIX="/scan.log"
SECURITY_SCANNER_COMMAND=(python3 "$REPO_ROOT/.copilot/hooks/scripts/scan-secrets.py")

SECURITY_SCANNER_PROVIDER=copilot

security_scanner_payload() {
  local repo_dir="$1" session="$2" copilot_timestamp="$3" gemini_timestamp="$4"
  local copilot_reason="$5" gemini_event="$6"
  jq -cn --arg session "$session" --arg timestamp "$copilot_timestamp" --arg reason "$copilot_reason" \
    '{sessionId:$session,timestamp:$timestamp,reason:$reason}'
}

security_assert_scanner_denial() {
  local output="$1"
  assert_equals deny "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected Copilot top-level scanner denial."
  assert_equals deny "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$output")" \
    "Expected Copilot nested scanner denial."
}

security_scanner_denial_reason() {
  jq -r '.permissionDecisionReason' <<<"$1"
}

run_scan_hook() {
  security_run_scan "$@"
}

create_selectively_failing_git() {
  local fake_bin="$1"

  mkdir -p "$fake_bin"
  cat > "$fake_bin/git" <<'EOF'
#!/usr/bin/env bash

if [[ "${1-}" == "${FAIL_GIT_COMMAND-}" ]]; then
  exit 9
fi
exec "$REAL_GIT" "$@"
EOF
  chmod 755 "$fake_bin/git"
}

test_git_failures_after_repo_detection_respect_fail_closed_mode() {
  local workdir
  local repo_dir
  local log_dir
  local fake_bin
  local real_git
  local output
  local scope
  local status
  local command_name

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  fake_bin="$workdir/bin"
  real_git="$(command -v git)"
  mkdir -p "$repo_dir"
  init_git_repo "$repo_dir"
  printf 'baseline\n' > "$repo_dir/notes.txt"
  git -C "$repo_dir" add notes.txt
  git -C "$repo_dir" commit -qm "baseline"
  printf 'changed\n' >> "$repo_dir/notes.txt"
  git -C "$repo_dir" add notes.txt
  create_selectively_failing_git "$fake_bin"

  for command_name in diff ls-files cat-file; do
    scope=staged
    if [[ "$command_name" == "ls-files" ]]; then
      scope=diff
    fi
    if output="$(
      run_scan_hook \
        "$repo_dir" \
        "$log_dir/$command_name-block" \
        block \
        "$scope" \
        '{"sessionId":"git-failure","timestamp":"2026-06-23T23:38:45Z","reason":"tool"}' \
        "PATH=$fake_bin:$PATH" \
        "REAL_GIT=$real_git" \
        "FAIL_GIT_COMMAND=$command_name"
    )"; then
      status=0
    else
      status=$?
    fi
    assert_equals "0" "$status" \
      "Expected $command_name failure in block mode to return exit code 0."
    assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
      "Expected $command_name failure after repository detection to deny."

    output="$(
      run_scan_hook \
        "$repo_dir" \
        "$log_dir/$command_name-warn" \
        warn \
        "$scope" \
        '{"sessionId":"git-failure","timestamp":"2026-06-23T23:38:46Z","reason":"complete"}' \
        "PATH=$fake_bin:$PATH" \
        "REAL_GIT=$real_git" \
        "FAIL_GIT_COMMAND=$command_name"
    )"
    assert_incomplete_warning "$output"
  done
}

test_unsafe_and_oversized_candidates_respect_fail_closed_mode() {
  local workdir
  local repo_dir
  local log_dir
  local outside
  local output
  local status
  local candidate_case

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  outside="$workdir/outside.txt"
  mkdir -p "$repo_dir"
  init_git_repo "$repo_dir"
  printf 'outside\n' > "$outside"

  for candidate_case in symlink oversized; do
    if [[ "$candidate_case" == "symlink" ]]; then
      ln -s "$outside" "$repo_dir/candidate.txt"
    else
      head -c 8388609 /dev/zero > "$repo_dir/candidate.txt"
    fi

    if output="$(
      run_scan_hook \
        "$repo_dir" \
        "$log_dir/$candidate_case-block" \
        block \
        diff \
        '{"sessionId":"candidate-limit","timestamp":"2026-06-23T23:38:50Z","reason":"tool"}'
    )"; then
      status=0
    else
      status=$?
    fi
    assert_equals "0" "$status" \
      "Expected $candidate_case candidate rejection to return exit code 0."
    assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
      "Expected $candidate_case candidate rejection to fail closed."

    output="$(
      run_scan_hook \
        "$repo_dir" \
        "$log_dir/$candidate_case-warn" \
        warn \
        diff \
        '{"sessionId":"candidate-limit","timestamp":"2026-06-23T23:38:51Z","reason":"complete"}'
    )"
    assert_incomplete_warning "$output"
    unlink "$repo_dir/candidate.txt"
  done
}

test_scan_log_lock_timeout_respects_fail_closed_mode() {
  local workdir
  local repo_dir
  local log_dir
  local lock_path
  local ready_path
  local locker_pid
  local output
  local status

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  lock_path="$log_dir/scan.log.lock"
  ready_path="$workdir/lock-ready"
  mkdir -p "$repo_dir" "$log_dir"
  init_git_repo "$repo_dir"

  python3 - "$lock_path" "$ready_path" <<'PY' &
import fcntl
import os
from pathlib import Path
import sys
import time

descriptor = os.open(sys.argv[1], os.O_CREAT | os.O_RDWR, 0o600)
fcntl.flock(descriptor, fcntl.LOCK_EX)
Path(sys.argv[2]).write_text("ready", encoding="utf-8")
time.sleep(30)  # Test cleanup releases the lock after both bounded hook calls.
PY
  locker_pid=$!
  trap 'kill "'"$locker_pid"'" 2>/dev/null || true; wait "'"$locker_pid"'" 2>/dev/null || true; rm -rf "'"$workdir"'"' RETURN
  while [[ ! -f "$ready_path" ]]; do
    sleep 0.01
  done

  if output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      '{"sessionId":"locked-log","timestamp":"2026-06-23T23:38:55Z","reason":"tool"}'
  )"; then
    status=0
  else
    status=$?
  fi
  assert_equals "0" "$status" \
    "Expected a blocked scan-log lock to return exit code 0."
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected a scan-log lock timeout to fail closed in block mode."

  output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      '{"sessionId":"locked-log","timestamp":"2026-06-23T23:38:56Z","reason":"complete"}'
  )"
  assert_incomplete_warning "$output"

  kill "$locker_pid" 2>/dev/null || true
  wait "$locker_pid" 2>/dev/null || true
}

test_block_mode_denies_when_findings_exist() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local status

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'safe=true\n' > "$repo_dir/.env"
  git -C "$repo_dir" add .env
  git -C "$repo_dir" commit -qm "baseline"

  printf 'aws=%s\n' "AK""IA1234567890ABCDEF" > "$repo_dir/.env"

  if output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      '{"sessionId":"block-session","timestamp":"2026-06-23T23:41:00Z","reason":"complete"}'
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected block mode findings to return exit code 0 so Copilot can read deny JSON."
  assert_json_output "$output" "Expected block mode findings to emit structured deny JSON."
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected block mode findings to emit top-level permissionDecision deny."
  assert_equals "deny" "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$output")" \
    "Expected block mode findings to emit hookSpecificOutput permissionDecision deny."
  if [[ "$(jq -r '.permissionDecisionReason' <<<"$output")" != *"scan-secrets blocked: session-end scan; potential secrets detected."* ]]; then
    echo "Expected block mode denial reason to name the safe action and finding." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
  assert_file_contains "$log_dir/scan.log" '"status":"findings"' \
    "Expected block mode to log findings before denying."
}

test_hooks_json_registers_session_end_scanner() {
  assert_equals '$HOME/.copilot/hooks/scripts/bell.py' \
    "$(jq -r '.hooks.sessionEnd[] | select(.bash == "$HOME/.copilot/hooks/scripts/bell.py") | .bash' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to register the session-end bell Python hook."
  assert_equals '$HOME/.copilot/hooks/scripts/scan-secrets.py' \
    "$(jq -r '.hooks.sessionEnd[] | select(.bash == "$HOME/.copilot/hooks/scripts/scan-secrets.py") | .bash' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to register the secrets scanner on sessionEnd."
  assert_equals warn \
    "$(jq -r '.hooks.sessionEnd[] | select(.bash == "$HOME/.copilot/hooks/scripts/scan-secrets.py") | .env.SCAN_MODE' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to default secrets scanning to warn mode."
  assert_equals diff \
    "$(jq -r '.hooks.sessionEnd[] | select(.bash == "$HOME/.copilot/hooks/scripts/scan-secrets.py") | .env.SCAN_SCOPE' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to scan working tree diffs by default."
}

test_hooks_json_registers_pre_tool_scanner() {
  assert_equals '$HOME/.copilot/hooks/scripts/scan-secrets.py' \
    "$(jq -r '.hooks.preToolUse[] | select(.bash == "$HOME/.copilot/hooks/scripts/scan-secrets.py") | .bash' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to register the secrets scanner on preToolUse."
  assert_equals block \
    "$(jq -r '.hooks.preToolUse[] | select(.bash == "$HOME/.copilot/hooks/scripts/scan-secrets.py") | .env.SCAN_MODE' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to default secrets scanning to block mode under preToolUse."
}

main() {
  python3 "$REPO_ROOT/scripts/test-scan-secrets-capture.py" copilot
  test_stalled_git_is_bounded_by_timeout
  test_stalled_git_denies_in_block_mode
  test_failed_initial_git_probe_with_repo_marker_respects_fail_closed_mode
  test_missing_git_block_mode_uses_provider_denial_envelope
  test_audit_init_failure_block_mode_uses_provider_denial_envelope
  test_git_failures_after_repo_detection_respect_fail_closed_mode
  test_unsafe_and_oversized_candidates_respect_fail_closed_mode
  test_scan_log_lock_timeout_respects_fail_closed_mode
  test_unexpected_exception_block_mode_denies_with_json_and_exit_zero
  test_unexpected_exception_warn_mode_warns_with_json_and_exit_zero
  test_invalid_json_block_mode_denies_with_json_and_exit_zero
  test_warn_mode_reports_findings_without_failing
  test_block_mode_denies_when_findings_exist
  test_high_match_input_has_bounded_denial_and_log
  test_diff_mode_ignores_unchanged_secrets_in_touched_files
  test_warn_mode_flags_sensitive_credential_paths_without_token_match
  test_binary_credential_path_still_scans_ascii_tokens
  test_unusual_filename_and_double_plus_added_line_are_scanned
  test_committed_literal_pathspec_filename_is_scanned
  test_staged_scope_excludes_unrelated_untracked_files
  test_staged_zero_prefix_filename_is_scanned
  test_diff_scope_scans_cached_secret_when_worktree_matches_head
  test_env_variants_are_logged_but_not_flagged_by_path_alone
  test_generic_secrets_filename_stays_clean
  test_allowlist_suppresses_credential_path_finding
  test_diff_mode_ignores_secret_like_diff_headers
  test_hooks_json_registers_session_end_scanner
  test_hooks_json_registers_pre_tool_scanner
}

security_run_suite main "$@"

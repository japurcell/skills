#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_scan_hook() {
  local repo_dir="$1"
  local log_dir="$2"
  local mode="$3"
  local scope="$4"
  local payload="$5"
  shift 5

  local env_cmd=(
    "SECRETS_LOG_DIR=$log_dir/scan.log"
    "SCAN_MODE=$mode"
    "SCAN_SCOPE=$scope"
  )

  while [[ $# -gt 0 ]]; do
    env_cmd+=("$1")
    shift
  done

  (
    cd "$repo_dir"
    env "${env_cmd[@]}" \
      python3 "$REPO_ROOT/.copilot/hooks/scripts/scan-secrets.py" <<<"$payload"
  )
}

init_git_repo() {
  local repo_dir="$1"

  git -C "$repo_dir" init -q
  git -C "$repo_dir" config user.email "copilot@example.com"
  git -C "$repo_dir" config user.name "Copilot Test"
  git -C "$repo_dir" config commit.gpgsign false
}

assert_json_output() {
  local output="$1"
  local message="$2"

  if ! jq -e 'type == "object"' >/dev/null 2>&1 <<<"$output"; then
    echo "$message" >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
}

create_stalling_git() {
  local fake_bin="$1"

  mkdir -p "$fake_bin"
  cat > "$fake_bin/git" <<'EOF'
#!/usr/bin/env bash

case "$1 ${2-}" in
  "rev-parse --show-toplevel")
    exit 1
    ;;
  "rev-parse --is-inside-work-tree")
    sleep 10
    exit 0
    ;;
esac

exit 1
EOF
  cat > "$fake_bin/git.cmd" <<'EOF'
@echo off
if "%1 %2"=="rev-parse --is-inside-work-tree" (
  timeout /t 10 /nobreak >nul
  exit /b 0
)
exit /b 1
EOF
  chmod 755 "$fake_bin/git"
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

test_stalled_git_is_bounded_by_timeout() {
  local workdir
  local repo_dir
  local log_dir
  local fake_bin
  local output
  local elapsed_ms
  local start_ns
  local end_ns

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  fake_bin="$workdir/bin"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  create_stalling_git "$fake_bin"

  start_ns="$(date +%s%N)"
  output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      '{"sessionId":"stalled-git","timestamp":"2026-06-23T23:49:59Z","reason":"complete"}' \
      "PATH=$fake_bin:$PATH"
  )"
  end_ns="$(date +%s%N)"
  elapsed_ms=$(((end_ns - start_ns) / 1000000))

  assert_json_output "$output" "Expected scanner to emit JSON after stalled git returns."
  assert_equals "{}" "$output" \
    "Expected scanner to noop after stalled git times out."
  if (( elapsed_ms >= 8000 )); then
    echo "Expected scanner to stop stalled git within 8000ms. Elapsed: ${elapsed_ms}ms" >&2
    exit 1
  fi
}

test_stalled_git_denies_in_block_mode() {
  local workdir
  local repo_dir
  local log_dir
  local fake_bin
  local output
  local status

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  fake_bin="$workdir/bin"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  create_stalling_git "$fake_bin"

  if output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      '{"sessionId":"stalled-git-block","timestamp":"2026-06-23T23:49:59Z","reason":"tool"}' \
      "PATH=$fake_bin:$PATH"
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected stalled-git block mode to return exit code 0."
  assert_json_output "$output" "Expected stalled-git block mode to emit JSON."
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected stalled-git block mode to deny."
  assert_equals "deny" "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$output")" \
    "Expected stalled-git block mode to keep hookSpecificOutput deny payload."
}

test_missing_git_block_mode_uses_copilot_denial_envelope() {
  local workdir
  local repo_dir
  local log_dir
  local fake_bin
  local output
  local status

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  fake_bin="$workdir/bin"
  mkdir -p "$repo_dir" "$fake_bin"
  ln -s "$(command -v python3)" "$fake_bin/python3"

  if output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      '{"sessionId":"missing-git","timestamp":"2026-06-23T23:38:00Z","reason":"tool"}' \
      "PATH=$fake_bin"
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected missing-Git block mode to return exit code 0."
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected missing-Git block mode to deny through the Copilot envelope."
  assert_equals "scan-secrets.py: required command not found: git" \
    "$(jq -r '.permissionDecisionReason' <<<"$output")" \
    "Expected missing-Git denial reason to remain stable."
}

test_audit_init_failure_block_mode_uses_copilot_denial_envelope() {
  local workdir
  local repo_dir
  local log_dir
  local occupied_parent
  local output
  local status

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  occupied_parent="$workdir/not-a-directory"
  mkdir -p "$repo_dir"
  printf 'occupied\n' > "$occupied_parent"

  if output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      '{"sessionId":"audit-init","timestamp":"2026-06-23T23:38:30Z","reason":"tool"}' \
      "AUDIT_LOG=$occupied_parent/audit.log"
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected audit-init block mode to return exit code 0."
  assert_equals "deny" "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$output")" \
    "Expected audit-init block mode to deny through the Copilot envelope."
  assert_equals "scan-secrets.py: failed to initialize audit logging." \
    "$(jq -r '.permissionDecisionReason' <<<"$output")" \
    "Expected audit-init denial reason to remain stable."
}

test_git_failures_after_repo_detection_respect_fail_closed_mode() {
  local workdir
  local repo_dir
  local log_dir
  local fake_bin
  local real_git
  local output
  local status
  local command_name

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
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

  for command_name in diff ls-files show; do
    if output="$(
      run_scan_hook \
        "$repo_dir" \
        "$log_dir/$command_name-block" \
        block \
        staged \
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
        staged \
        '{"sessionId":"git-failure","timestamp":"2026-06-23T23:38:46Z","reason":"complete"}' \
        "PATH=$fake_bin:$PATH" \
        "REAL_GIT=$real_git" \
        "FAIL_GIT_COMMAND=$command_name"
    )"
    assert_equals "{}" "$output" \
      "Expected $command_name failure in warn mode to degrade to JSON no-op."
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
  trap 'rm -rf "'"$workdir"'"' RETURN
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
      head -c 1048577 /dev/zero > "$repo_dir/candidate.txt"
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
    assert_equals "{}" "$output" \
      "Expected $candidate_case candidate rejection in warn mode to no-op."
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
  trap 'rm -rf "'"$workdir"'"' RETURN
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
time.sleep(5)
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
  assert_equals "{}" "$output" \
    "Expected a scan-log lock timeout to no-op in warn mode."

  kill "$locker_pid" 2>/dev/null || true
  wait "$locker_pid" 2>/dev/null || true
}

test_unexpected_exception_block_mode_denies_with_json_and_exit_zero() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local errfile
  local status

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  errfile="$workdir/block.err"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'safe=true\n' > "$repo_dir/app.env"

  if output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      '{"sessionId":"unexpected-block","timestamp":"2026-06-23T23:39:00Z","reason":"complete"}' \
      'AUDIT_LOG_MAX_BYTES=not-a-number' \
      2>"$errfile"
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected block-mode exception handling to return exit code 0."
  assert_json_output "$output" "Expected block-mode exception handling to emit JSON."
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected block-mode exception handling to deny."
  assert_equals "deny" "$(jq -r '.hookSpecificOutput.permissionDecision' <<<"$output")" \
    "Expected block-mode exception handling to keep hookSpecificOutput deny payload."
  assert_file_contains "$errfile" 'scan-secrets.py: unexpected scanner error.' \
    "Expected sanitized scanner error on stderr."
  if grep -Fq 'Traceback' "$errfile"; then
    echo "Did not expect traceback in sanitized scanner error output." >&2
    cat "$errfile" >&2
    exit 1
  fi
}

test_unexpected_exception_warn_mode_noops_with_json_and_exit_zero() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local errfile
  local status

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  errfile="$workdir/warn.err"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'safe=true\n' > "$repo_dir/app.env"

  if output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      '{"sessionId":"unexpected-warn","timestamp":"2026-06-23T23:39:30Z","reason":"complete"}' \
      'AUDIT_LOG_MAX_BYTES=not-a-number' \
      2>"$errfile"
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected warn-mode exception handling to return exit code 0."
  assert_equals "{}" "$output" \
    "Expected warn-mode exception handling to degrade to noop JSON output."
  assert_file_contains "$errfile" 'scan-secrets.py: unexpected scanner error.' \
    "Expected sanitized warn-mode scanner error on stderr."
  if grep -Fq 'Traceback' "$errfile"; then
    echo "Did not expect traceback in warn-mode sanitized scanner output." >&2
    cat "$errfile" >&2
    exit 1
  fi
}

test_invalid_json_block_mode_denies_with_json_and_exit_zero() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local status

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  if output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      'not-json'
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected invalid block-mode input to return exit code 0."
  assert_json_output "$output" "Expected invalid block-mode input to emit JSON."
  assert_equals "deny" "$(jq -r '.permissionDecision' <<<"$output")" \
    "Expected invalid block-mode input to deny."
}

test_warn_mode_reports_findings_without_failing() {
  local workdir
  local repo_dir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'safe=true\n' > "$repo_dir/app.env"
  git -C "$repo_dir" add app.env
  git -C "$repo_dir" commit -qm "baseline"

  printf 'token=ghp_123456789012345678901234567890123456\n' > "$repo_dir/app.env"

  output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      '{"sessionId":"warn-session","timestamp":"2026-06-23T23:40:00Z","reason":"complete"}'
  )"

  assert_file_contains "$log_dir/scan.log" '"status":"findings"' \
    "Expected warn mode to log findings."
  assert_file_contains "$log_dir/scan.log" '"path":"app.env"' \
    "Expected warn mode log to record detected file path."
  assert_file_contains "$log_dir/scan.log" '"pattern":"github_classic_pat"' \
    "Expected warn mode log to record detected pattern."
  assert_file_contains "$log_dir/scan.log" '"redactedMatch":"ghp_...3456"' \
    "Expected warn mode log to redact stored match values."
  if [[ "$output" != *"Potential secrets detected in modified files"* ]]; then
    echo "Expected warn mode to print findings summary via systemMessage." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
}

test_block_mode_denies_when_findings_exist() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local status

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'safe=true\n' > "$repo_dir/.env"
  git -C "$repo_dir" add .env
  git -C "$repo_dir" commit -qm "baseline"

  printf 'aws=AKIA1234567890ABCDEF\n' > "$repo_dir/.env"

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
  if [[ "$(jq -r '.permissionDecisionReason' <<<"$output")" != *"scan.log"* ]]; then
    echo "Expected block mode denial reason to reference scan log path." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
  assert_file_contains "$log_dir/scan.log" '"status":"findings"' \
    "Expected block mode to log findings before denying."
}

test_diff_mode_ignores_unchanged_secrets_in_touched_files() {
  local workdir
  local repo_dir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  cat > "$repo_dir/app.env" <<'EOF'
token=ghp_123456789012345678901234567890123456
safe=true
EOF
  git -C "$repo_dir" add app.env
  git -C "$repo_dir" commit -qm "baseline"

  cat > "$repo_dir/app.env" <<'EOF'
token=ghp_123456789012345678901234567890123456
safe=false
EOF

  output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      '{"sessionId":"unchanged-secret","timestamp":"2026-06-23T23:42:00Z","reason":"complete"}'
  )"

  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected diff mode to ignore unchanged secrets in touched files."
  if [[ "$output" != "{}" ]]; then
    echo "Expected diff mode to stay clean when only non-secret lines changed." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
}

test_diff_mode_ignores_secret_like_diff_headers() {
  local workdir
  local repo_dir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir/docs"

  init_git_repo "$repo_dir"
  printf 'safe content\n' > "$repo_dir/docs/sk_live_1234567890ABCDEF.txt"
  git -C "$repo_dir" add docs/sk_live_1234567890ABCDEF.txt
  git -C "$repo_dir" commit -qm "baseline"

  printf 'safe content updated\n' > "$repo_dir/docs/sk_live_1234567890ABCDEF.txt"

  output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      '{"sessionId":"header-ignore","timestamp":"2026-06-23T23:42:30Z","reason":"complete"}'
  )"

  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected diff mode to ignore secret-like unified-diff header paths."
  if [[ "$output" != "{}" ]]; then
    echo "Expected diff mode to stay clean when only the diff header path looks secret-like." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
}

test_warn_mode_flags_sensitive_credential_paths_without_token_match() {
  local workdir
  local repo_dir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'These are deployment notes only.\n' > "$repo_dir/credentials.md"

  output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      '{"sessionId":"credential-path","timestamp":"2026-06-23T23:43:00Z","reason":"complete"}'
  )"

  assert_file_contains "$log_dir/scan.log" '"pattern":"credential_path"' \
    "Expected sensitive credential-like paths to produce a finding even without token-shaped content."
  assert_file_contains "$log_dir/scan.log" '"path":"credentials.md"' \
    "Expected credential-path finding to record the file path."
  if [[ "$output" != *"Potential secrets detected"* ]]; then
    echo "Expected credential-path warning in hook output." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
}

test_binary_credential_path_still_scans_ascii_tokens() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local fake_token

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir/.ssh"

  init_git_repo "$repo_dir"
  fake_token="gh""p_$(printf '0%.0s' {1..36})"
  printf 'binary\0token=%s\n' "$fake_token" > "$repo_dir/.ssh/id_test"

  output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      '{"sessionId":"binary-credential","timestamp":"2026-06-23T23:43:30Z","reason":"complete"}'
  )"

  assert_json_output "$output" "Expected binary credential scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"pattern":"credential_path"' \
    "Expected binary credential paths to be flagged before text classification."
  assert_file_contains "$log_dir/scan.log" '"pattern":"github_classic_pat"' \
    "Expected bounded ASCII token scanning to inspect NUL-bearing files."
  if grep -Fq "$fake_token" "$log_dir/scan.log"; then
    echo "Did not expect the fake token to appear unredacted in the scan log." >&2
    exit 1
  fi
}

test_unusual_filename_and_double_plus_added_line_are_scanned() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local fake_token
  local unusual_name

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'baseline\n' > "$repo_dir/notes.txt"
  git -C "$repo_dir" add notes.txt
  git -C "$repo_dir" commit -qm "baseline"

  fake_token="gh""p_$(printf '0%.0s' {1..36})"
  unusual_name=$'odd\nname.env'
  printf 'token=%s\n' "$fake_token" > "$repo_dir/$unusual_name"
  printf '++token=%s\n' "$fake_token" >> "$repo_dir/notes.txt"

  output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      '{"sessionId":"unusual-path","timestamp":"2026-06-23T23:43:45Z","reason":"complete"}'
  )"

  assert_json_output "$output" "Expected unusual-path scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"path":"odd\nname.env"' \
    "Expected NUL-delimited Git paths to preserve embedded newlines."
  assert_file_contains "$log_dir/scan.log" '"path":"notes.txt","line":2' \
    "Expected added content beginning with two plus signs to be scanned inside a hunk."
}

test_env_variants_are_logged_but_not_flagged_by_path_alone() {
  local workdir
  local repo_dir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'APP_MODE=development\n' > "$repo_dir/.env.local"

  output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      '{"sessionId":"env-variant","timestamp":"2026-06-23T23:44:00Z","reason":"complete"}'
  )"

  assert_file_contains "$log_dir/scan.log" '"envFiles":[".env.local"]' \
    "Expected .env variants to be logged when scanned."
  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected .env variants without secrets to remain clean."
  if [[ "$output" != "{}" ]]; then
    echo "Expected .env variant without secrets to stay clean." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
}

test_generic_secrets_filename_stays_clean() {
  local workdir
  local repo_dir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'notes only\n' > "$repo_dir/scan-secrets.sh"

  output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      '{"sessionId":"generic-secrets-name","timestamp":"2026-06-23T23:45:00Z","reason":"complete"}'
  )"

  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected generic filenames containing 'secrets' to stay clean."
  if grep -Fq '"pattern":"credential_path"' "$log_dir/scan.log"; then
    echo "Did not expect generic 'secrets' filename to trigger credential_path." >&2
    cat "$log_dir/scan.log" >&2
    exit 1
  fi
  if [[ "$output" != "{}" ]]; then
    echo "Expected generic 'secrets' filename to stay clean." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
}

test_allowlist_suppresses_credential_path_finding() {
  local workdir
  local repo_dir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'notes only\n' > "$repo_dir/credentials.md"

  output="$(
    run_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      '{"sessionId":"credential-allowlist","timestamp":"2026-06-23T23:46:00Z","reason":"complete"}' \
      'SECRETS_ALLOWLIST=[{"tool":"scan_secrets","input":"credentials.md:1:credential_path:[SENSITIVE PATH]"}]'
  )"

  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected allowlisted credential_path finding to stay clean."
  if grep -Fq '"pattern":"credential_path"' "$log_dir/scan.log"; then
    echo "Did not expect allowlisted credential_path finding to remain in log." >&2
    cat "$log_dir/scan.log" >&2
    exit 1
  fi
  if [[ "$output" != "{}" ]]; then
    echo "Expected allowlisted credential_path finding to be suppressed." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
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
  test_stalled_git_is_bounded_by_timeout
  test_stalled_git_denies_in_block_mode
  test_missing_git_block_mode_uses_copilot_denial_envelope
  test_audit_init_failure_block_mode_uses_copilot_denial_envelope
  test_git_failures_after_repo_detection_respect_fail_closed_mode
  test_unsafe_and_oversized_candidates_respect_fail_closed_mode
  test_scan_log_lock_timeout_respects_fail_closed_mode
  test_unexpected_exception_block_mode_denies_with_json_and_exit_zero
  test_unexpected_exception_warn_mode_noops_with_json_and_exit_zero
  test_invalid_json_block_mode_denies_with_json_and_exit_zero
  test_warn_mode_reports_findings_without_failing
  test_block_mode_denies_when_findings_exist
  test_diff_mode_ignores_unchanged_secrets_in_touched_files
  test_warn_mode_flags_sensitive_credential_paths_without_token_match
  test_binary_credential_path_still_scans_ascii_tokens
  test_unusual_filename_and_double_plus_added_line_are_scanned
  test_env_variants_are_logged_but_not_flagged_by_path_alone
  test_generic_secrets_filename_stays_clean
  test_allowlist_suppresses_credential_path_finding
  test_diff_mode_ignores_secret_like_diff_headers
  test_hooks_json_registers_session_end_scanner
  test_hooks_json_registers_pre_tool_scanner
}

main "$@"

#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_gemini_scan_hook() {
  local repo_dir="$1"
  local log_dir="$2"
  local mode="$3"
  local scope="$4"
  local payload="$5"
  shift 5

  local env_cmd=(
    "SECRETS_LOG_DIR=$log_dir"
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
      python3 -I -S -B "$REPO_ROOT/.gemini/hooks/scripts/scan-secrets.py" <<<"$payload"
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "{\"session_id\":\"stalled-git\",\"timestamp\":\"2026-06-23T23:49:59Z\",\"hook_event_name\":\"SessionEnd\",\"cwd\":\"$repo_dir\",\"reason\":\"exit\"}" \
      "PATH=$fake_bin:$PATH"
  )"
  end_ns="$(date +%s%N)"
  elapsed_ms=$(((end_ns - start_ns) / 1000000))

  assert_json_output "$output" "Expected Gemini scanner to emit JSON after stalled git returns."
  assert_equals "{}" "$output" \
    "Expected Gemini scanner to noop after stalled git times out."
  if (( elapsed_ms >= 8000 )); then
    echo "Expected Gemini scanner to stop stalled git within 8000ms. Elapsed: ${elapsed_ms}ms" >&2
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      "{\"session_id\":\"stalled-git-block\",\"timestamp\":\"2026-06-23T23:49:59Z\",\"hook_event_name\":\"BeforeTool\",\"cwd\":\"$repo_dir\",\"reason\":\"tool\"}" \
      "PATH=$fake_bin:$PATH"
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected Gemini stalled-git block mode to return exit code 0."
  assert_json_output "$output" "Expected Gemini stalled-git block mode to emit JSON."
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected Gemini stalled-git block mode to deny."
}

test_missing_git_block_mode_uses_gemini_denial_envelope() {
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      "{\"session_id\":\"missing-git\",\"timestamp\":\"2026-06-23T23:48:00Z\",\"hook_event_name\":\"BeforeTool\",\"cwd\":\"$repo_dir\",\"reason\":\"tool\"}" \
      "PATH=$fake_bin"
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected Gemini missing-Git block mode to return exit code 0."
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected Gemini missing-Git block mode to deny."
  assert_equals "scan-secrets.py: required command not found: git" \
    "$(jq -r '.reason' <<<"$output")" \
    "Expected Gemini missing-Git denial reason to remain stable."
}

test_audit_init_failure_block_mode_uses_gemini_denial_envelope() {
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      "{\"session_id\":\"audit-init\",\"timestamp\":\"2026-06-23T23:48:30Z\",\"hook_event_name\":\"BeforeTool\",\"cwd\":\"$repo_dir\",\"reason\":\"tool\"}" \
      "AUDIT_LOG=$occupied_parent/audit.log"
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected Gemini audit-init block mode to return exit code 0."
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected Gemini audit-init block mode to deny."
  assert_equals "scan-secrets.py: failed to initialize audit logging." \
    "$(jq -r '.reason' <<<"$output")" \
    "Expected Gemini audit-init denial reason to remain stable."
}

test_warn_mode_reports_findings_with_json_output() {
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "{\"session_id\":\"warn-session\",\"timestamp\":\"2026-06-23T23:50:00Z\",\"hook_event_name\":\"SessionEnd\",\"cwd\":\"$repo_dir\",\"reason\":\"exit\"}"
  )"

  assert_json_output "$output" "Expected Gemini secrets scanner to emit JSON only."
  assert_file_contains "$log_dir/scan.log" '"status":"findings"' \
    "Expected warn mode to log findings."
  assert_file_contains "$log_dir/scan.log" '"pattern":"github_classic_pat"' \
    "Expected warn mode log to record detected pattern."
  assert_file_contains "$log_dir/scan.log" '"redactedMatch":"ghp_...3456"' \
    "Expected warn mode log to redact stored match values."
  assert_equals "Potential secrets detected in modified files. See $log_dir/scan.log." "$(jq -r '.systemMessage' <<<"$output")" \
    "Expected findings to surface via Gemini systemMessage."
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      "{\"session_id\":\"unexpected-block\",\"timestamp\":\"2026-06-23T23:49:00Z\",\"hook_event_name\":\"BeforeTool\",\"cwd\":\"$repo_dir\",\"reason\":\"tool\"}" \
      'AUDIT_LOG_MAX_BYTES=not-a-number' \
      2>"$errfile"
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected Gemini block-mode exception handling to return exit code 0."
  assert_json_output "$output" "Expected Gemini block-mode exception handling to emit JSON."
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected Gemini block-mode exception handling to deny."
  assert_file_contains "$errfile" 'scan-secrets.py: unexpected scanner error.' \
    "Expected sanitized Gemini block-mode scanner error on stderr."
  if grep -Fq 'Traceback' "$errfile"; then
    echo "Did not expect traceback in Gemini block-mode sanitized scanner output." >&2
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "{\"session_id\":\"unexpected-warn\",\"timestamp\":\"2026-06-23T23:49:30Z\",\"hook_event_name\":\"BeforeTool\",\"cwd\":\"$repo_dir\",\"reason\":\"tool\"}" \
      'AUDIT_LOG_MAX_BYTES=not-a-number' \
      2>"$errfile"
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected Gemini warn-mode exception handling to return exit code 0."
  assert_equals "{}" "$output" \
    "Expected Gemini warn-mode exception handling to degrade to noop JSON output."
  assert_file_contains "$errfile" 'scan-secrets.py: unexpected scanner error.' \
    "Expected sanitized Gemini warn-mode scanner error on stderr."
  if grep -Fq 'Traceback' "$errfile"; then
    echo "Did not expect traceback in Gemini warn-mode sanitized scanner output." >&2
    cat "$errfile" >&2
    exit 1
  fi
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "{\"session_id\":\"env-variant\",\"timestamp\":\"2026-06-23T23:51:00Z\",\"hook_event_name\":\"SessionEnd\",\"cwd\":\"$repo_dir\",\"reason\":\"exit\"}"
  )"

  assert_json_output "$output" "Expected clean Gemini secrets scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"envFiles":[".env.local"]' \
    "Expected .env variants to be logged when scanned."
  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected .env variants without secrets to remain clean."
  assert_equals "null" "$(jq -r '.systemMessage // empty // "null"' <<<"$output")" \
    "Did not expect clean scan to emit a Gemini systemMessage."
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "{\"session_id\":\"credential-path\",\"timestamp\":\"2026-06-23T23:52:00Z\",\"hook_event_name\":\"SessionEnd\",\"cwd\":\"$repo_dir\",\"reason\":\"exit\"}"
  )"

  assert_json_output "$output" "Expected credential-path scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"pattern":"credential_path"' \
    "Expected sensitive credential-like paths to produce a finding even without token-shaped content."
  assert_file_contains "$log_dir/scan.log" '"path":"credentials.md"' \
    "Expected credential-path finding to record the file path."
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "{\"session_id\":\"binary-credential\",\"timestamp\":\"2026-06-23T23:52:30Z\",\"hook_event_name\":\"SessionEnd\",\"cwd\":\"$repo_dir\",\"reason\":\"exit\"}"
  )"

  assert_json_output "$output" "Expected Gemini binary credential scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"pattern":"credential_path"' \
    "Expected Gemini binary credential paths to be flagged before text classification."
  assert_file_contains "$log_dir/scan.log" '"pattern":"github_classic_pat"' \
    "Expected Gemini bounded ASCII token scanning to inspect NUL-bearing files."
  if grep -Fq "$fake_token" "$log_dir/scan.log"; then
    echo "Did not expect the fake token to appear unredacted in the Gemini scan log." >&2
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "{\"session_id\":\"unusual-path\",\"timestamp\":\"2026-06-23T23:52:45Z\",\"hook_event_name\":\"SessionEnd\",\"cwd\":\"$repo_dir\",\"reason\":\"exit\"}"
  )"

  assert_json_output "$output" "Expected Gemini unusual-path scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"path":"odd\nname.env"' \
    "Expected Gemini NUL-delimited Git paths to preserve embedded newlines."
  assert_file_contains "$log_dir/scan.log" '"path":"notes.txt","line":2' \
    "Expected Gemini added content beginning with two plus signs to be scanned inside a hunk."
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "{\"session_id\":\"generic-secrets-name\",\"timestamp\":\"2026-06-23T23:53:00Z\",\"hook_event_name\":\"SessionEnd\",\"cwd\":\"$repo_dir\",\"reason\":\"exit\"}"
  )"

  assert_json_output "$output" "Expected generic filename scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected generic filenames containing 'secrets' to stay clean."
  if grep -Fq '"pattern":"credential_path"' "$log_dir/scan.log"; then
    echo "Did not expect generic 'secrets' filename to trigger credential_path." >&2
    cat "$log_dir/scan.log" >&2
    exit 1
  fi
}

test_diff_mode_ignores_unmodified_secret_lines() {
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
  cat > "$repo_dir/notes.txt" <<'EOF'
token=ghp_1234567890abcdef1234567890abcdef1234
context=baseline
EOF
  git -C "$repo_dir" add notes.txt
  git -C "$repo_dir" commit -qm "baseline"

  printf '%s\n' 'context=updated' >> "$repo_dir/notes.txt"

  output="$(
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "{\"session_id\":\"unchanged-secret\",\"timestamp\":\"2026-06-23T23:54:30Z\",\"hook_event_name\":\"SessionEnd\",\"cwd\":\"$repo_dir\",\"reason\":\"exit\"}"
  )"

  assert_equals "{}" "$output" \
    "Expected unchanged secret-bearing lines to stay out of Gemini diff findings."
  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected unchanged secret-bearing lines to keep diff scans clean."
}

test_diff_mode_ignores_unified_diff_headers() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local secret_name

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  secret_name="ghp_$(printf 'a%.0s' {1..36}).txt"
  printf '%s\n' 'safe content only' > "$repo_dir/$secret_name"
  git -C "$repo_dir" add "$secret_name"
  git -C "$repo_dir" commit -qm "baseline"

  printf '%s\n' 'safe content updated' >> "$repo_dir/$secret_name"

  output="$(
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "{\"session_id\":\"header-ignore\",\"timestamp\":\"2026-06-23T23:54:40Z\",\"hook_event_name\":\"SessionEnd\",\"cwd\":\"$repo_dir\",\"reason\":\"exit\"}"
  )"

  assert_equals "{}" "$output" \
    "Expected unified-diff header lines to stay out of Gemini diff findings."
  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected diff header lines to remain ignored during Gemini secret scans."
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
    run_gemini_scan_hook \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "{\"session_id\":\"credential-allowlist\",\"timestamp\":\"2026-06-23T23:54:00Z\",\"hook_event_name\":\"SessionEnd\",\"cwd\":\"$repo_dir\",\"reason\":\"exit\"}" \
      'SECRETS_ALLOWLIST=[{"tool":"scan_secrets","input":"credentials.md:1:credential_path:[SENSITIVE PATH]"}]'
  )"

  assert_json_output "$output" "Expected allowlisted scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected allowlisted credential_path finding to stay clean."
  if grep -Fq '"pattern":"credential_path"' "$log_dir/scan.log"; then
    echo "Did not expect allowlisted credential_path finding to remain in log." >&2
    cat "$log_dir/scan.log" >&2
    exit 1
  fi
}

test_invalid_json_degrades_to_noop_json() {
  local workdir
  local repo_dir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
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
  assert_equals "{}" "$output" \
    "Expected invalid-input Gemini secrets scan to degrade to a no-op JSON response."
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
    run_gemini_scan_hook \
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
    "Expected invalid Gemini block-mode input to return exit code 0."
  assert_json_output "$output" "Expected invalid Gemini block-mode input to emit JSON."
  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected invalid Gemini block-mode input to deny."
}

test_gemini_settings_register_session_end_scanner() {
  assert_equals 'python "$HOME/.gemini/hooks/scripts/scan-secrets.py"' \
    "$(jq -r '.hooks.SessionEnd[0].hooks[] | select(.name == "scan-secrets") | .command // empty' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected .gemini/global-settings.json to register scan-secrets.py for Gemini SessionEnd."
}

test_gemini_settings_register_before_tool_scanner() {
  assert_equals 'python "$HOME/.gemini/hooks/scripts/scan-secrets.py"' \
    "$(jq -r '.hooks.BeforeTool[0].hooks[] | select(.name == "scan-secrets") | .command // empty' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected .gemini/global-settings.json to register scan-secrets.py for Gemini BeforeTool."
  assert_equals 'block' \
    "$(jq -r '.hooks.BeforeTool[0].hooks[] | select(.name == "scan-secrets") | .env.SCAN_MODE // empty' "$REPO_ROOT/.gemini/global-settings.json")" \
    "Expected .gemini/global-settings.json scan-secrets before tools to default to block."
}

main() {
  test_stalled_git_is_bounded_by_timeout
  test_stalled_git_denies_in_block_mode
  test_missing_git_block_mode_uses_gemini_denial_envelope
  test_audit_init_failure_block_mode_uses_gemini_denial_envelope
  test_unexpected_exception_block_mode_denies_with_json_and_exit_zero
  test_unexpected_exception_warn_mode_noops_with_json_and_exit_zero
  test_warn_mode_reports_findings_with_json_output
  test_env_variants_are_logged_but_not_flagged_by_path_alone
  test_warn_mode_flags_sensitive_credential_paths_without_token_match
  test_binary_credential_path_still_scans_ascii_tokens
  test_unusual_filename_and_double_plus_added_line_are_scanned
  test_generic_secrets_filename_stays_clean
  test_diff_mode_ignores_unmodified_secret_lines
  test_diff_mode_ignores_unified_diff_headers
  test_allowlist_suppresses_credential_path_finding
  test_invalid_json_degrades_to_noop_json
  test_invalid_json_block_mode_denies_with_json_and_exit_zero
  test_gemini_settings_register_session_end_scanner
  test_gemini_settings_register_before_tool_scanner
}

main "$@"

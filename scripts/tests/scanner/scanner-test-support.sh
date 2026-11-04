#!/usr/bin/env bash
# Scanner scenarios shared by provider suites; fixture and invocation primitives
# come from security-test-support.sh, and native envelope adapters stay local.

# Only the build fingerprint is read from actual output. Callers supply every
# expected semantic attribution field so a wrong outcome cannot pass by parity.
security_scanner_report_suffix() {
  local log_path="$1" security_outcome="$2" audit_outcome="$3" enforcement="$4"
  local route="$5" cause="$6" build
  build="$(jq -er '.build' "$log_path")"
  printf 'security_outcome=%s; audit_outcome=%s; enforcement=%s; build=%s; profile=pending_snapshots_v1; route=%s; cause=%s.' \
    "$security_outcome" "$audit_outcome" "$enforcement" "$build" "$route" "$cause"
}

# Each provider suite registers these scenarios and supplies its native payload,
# denial, and reason adapters. Provider fixture differences stay explicit here.
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
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  fake_bin="$workdir/bin"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  create_stalling_git "$fake_bin"

  start_ns="$(date +%s%N)"
  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "stalled-git" "2026-06-23T23:49:59Z" "2026-06-23T23:49:59Z" "complete" "SessionEnd")" \
      "PATH=$fake_bin:$PATH"
  )"
  end_ns="$(date +%s%N)"
  elapsed_ms=$(((end_ns - start_ns) / 1000000))

  assert_json_output "$output" "Expected scanner to emit JSON after stalled git returns."
  assert_incomplete_warning "$output"
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
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  fake_bin="$workdir/bin"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  create_stalling_git "$fake_bin"

  if output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      "$(security_scanner_payload "$repo_dir" "stalled-git-block" "2026-06-23T23:49:59Z" "2026-06-23T23:49:59Z" "tool" "BeforeTool")" \
      "PATH=$fake_bin:$PATH"
  )"; then
    status=0
  else
    status=$?
  fi

  security_assert_scanner_denial "$output"

  assert_equals "0" "$status" \
    "Expected stalled-git block mode to return exit code 0."
  assert_json_output "$output" "Expected stalled-git block mode to emit JSON."
}

test_failed_initial_git_probe_with_repo_marker_respects_fail_closed_mode() {
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
  printf '%s\n' '[broken' > "$repo_dir/.git/config"

  if output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir/block" \
      block \
      diff \
      "$(security_scanner_payload "$repo_dir" "initial-probe" "2026-06-23T23:37:30Z" "2026-06-23T23:49:30Z" "tool" "BeforeTool")"
  )"; then
    status=0
  else
    status=$?
  fi
  security_assert_scanner_denial "$output"

  assert_equals "0" "$status" \
    "Expected a failed initial Git probe with a repository marker to return exit code 0."

  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir/warn" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "initial-probe" "2026-06-23T23:37:31Z" "2026-06-23T23:49:31Z" "complete" "SessionEnd")"
  )"
  assert_incomplete_warning "$output"
}

test_missing_git_block_mode_uses_provider_denial_envelope() {
  local workdir
  local repo_dir
  local log_dir
  local fake_bin
  local output
  local status

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  fake_bin="$workdir/bin"
  mkdir -p "$repo_dir" "$fake_bin"
  ln -s "$(python3 -c 'import sys; print(sys.executable)')" "$fake_bin/python3"

  if output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      "$(security_scanner_payload "$repo_dir" "missing-git" "2026-06-23T23:38:00Z" "2026-06-23T23:48:00Z" "tool" "BeforeTool")" \
      "PATH=$fake_bin"
  )"; then
    status=0
  else
    status=$?
  fi

  security_assert_scanner_denial "$output"

  assert_equals "0" "$status" \
    "Expected missing-Git block mode to return exit code 0."
  assert_equals "scan-secrets blocked: scan; scan incomplete; potential secrets could not be checked. git_unavailable/initialization: Git is unavailable. Check Git availability in the hook environment. $(security_scanner_report_suffix "$log_dir/scan.log" incomplete written deny pending_scan git_unavailable)" \
    "$(security_scanner_denial_reason "$output")" \
    "Expected missing-Git denial reason to remain stable."
}

test_audit_init_failure_block_mode_uses_provider_denial_envelope() {
  local workdir
  local repo_dir
  local log_dir
  local occupied_parent
  local output
  local status

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  occupied_parent="$workdir/not-a-directory"
  mkdir -p "$repo_dir"
  printf 'occupied\n' > "$occupied_parent"

  if output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      "$(security_scanner_payload "$repo_dir" "audit-init" "2026-06-23T23:38:30Z" "2026-06-23T23:48:30Z" "tool" "BeforeTool")" \
      "AUDIT_LOG=$occupied_parent/audit.log"
  )"; then
    status=0
  else
    status=$?
  fi

  security_assert_scanner_denial "$output"

  assert_equals "0" "$status" \
    "Expected audit-init block mode to return exit code 0."
  assert_equals "scan-secrets blocked: scan; scan incomplete; potential secrets could not be checked. audit_unavailable/initialization: audit storage is unavailable. Check hook audit storage. $(security_scanner_report_suffix "$log_dir/scan.log" incomplete written deny pending_scan audit_unavailable)" \
    "$(security_scanner_denial_reason "$output")" \
    "Expected audit-init denial reason to remain stable."
}

test_warn_mode_reports_findings_without_failing() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local fake_token

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'safe=true\n' > "$repo_dir/app.env"
  git -C "$repo_dir" add app.env
  git -C "$repo_dir" commit -qm "baseline"

  fake_token="gh""p_123456789012345678901234567890123456"
  printf 'token=%s\n' "$fake_token" > "$repo_dir/app.env"

  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "warn-session" "2026-06-23T23:40:00Z" "2026-06-23T23:50:00Z" "complete" "SessionEnd")"
  )"

  assert_json_output "$output" "Expected scanner to emit JSON only."

  assert_file_contains "$log_dir/scan.log" '"status":"findings"' \
    "Expected warn mode to log findings."
  assert_file_contains "$log_dir/scan.log" '"path":"app.env"' \
    "Expected warn mode log to record detected file path."
  assert_file_contains "$log_dir/scan.log" '"pattern":"github_classic_pat"' \
    "Expected warn mode log to record detected pattern."
  assert_file_contains "$log_dir/scan.log" '"redactedMatch":"ghp_...3456"' \
    "Expected warn mode log to redact stored match values."
  if [[ "$output" != *"scan-secrets warning:"* || "$output" != *"potential secrets detected"* ]]; then
    echo "Expected warn mode to print findings summary via systemMessage." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
  if [[ "$SECURITY_SCANNER_PROVIDER" == gemini ]]; then
    assert_equals "scan-secrets warning: session-end scan; potential secrets detected. $(security_scanner_report_suffix "$log_dir/scan.log" findings written allow pending_scan findings)" "$(jq -r '.systemMessage' <<<"$output")" \
      "Expected findings to surface via Gemini systemMessage."
  fi
}

test_high_match_input_has_bounded_denial_and_log() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local fake_token
  local elapsed_ms
  local start_ns
  local end_ns
  local log_bytes

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir" "$log_dir"

  fake_token="gh""p_$(printf '0%.0s' {1..36})"
  security_prepare_burst_scan "$repo_dir" "$fake_token" "$log_dir"

  start_ns="$(date +%s%N)"
  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      block \
      staged \
      "$(security_scanner_payload "$repo_dir" "high-match" "2026-06-23T23:41:30Z" "2026-06-23T23:50:30Z" "complete" "SessionEnd")" \
      'AUDIT_LOG_MAX_BYTES=65536'
  )"
  end_ns="$(date +%s%N)"
  elapsed_ms=$(((end_ns - start_ns) / 1000000))

  security_assert_scanner_denial "$output"

  assert_json_output "$output" "Expected high-match input to emit structured JSON."
  if ((elapsed_ms >= 8000)); then
    echo "Expected high-match scan to finish within 8000ms. Elapsed: ${elapsed_ms}ms" >&2
    exit 1
  fi
  if [[ ! -f "$log_dir/scan.log.1" ]]; then
    echo "Expected incoming bounded record to rotate the nearly full scan log." >&2
    exit 1
  fi
  log_bytes="$(wc -c < "$log_dir/scan.log")"
  if ((log_bytes > 65536)); then
    echo "Expected active scan log to stay within 65536 bytes. Actual: $log_bytes" >&2
    exit 1
  fi
  if ! jq -e '.findings | length <= 100' "$log_dir/scan.log" >/dev/null; then
    echo "Expected retained high-match finding details to be capped." >&2
    exit 1
  fi
  if ! jq -e '.omittedFindings > 0 and .findingsTruncated == true' "$log_dir/scan.log" >/dev/null; then
    echo "Expected bounded log to count omitted high-match findings." >&2
    exit 1
  fi
  if grep -Fq "$fake_token" "$log_dir/scan.log"; then
    echo "Did not expect high-match log to expose the fake token." >&2
    exit 1
  fi
}

test_unexpected_exception_block_mode_denies_with_json_and_exit_zero() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local errfile
  local status

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  errfile="$workdir/block.err"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'safe=true\n' > "$repo_dir/app.env"

  if output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      block \
      diff \
      "$(security_scanner_payload "$repo_dir" "unexpected-block" "2026-06-23T23:39:00Z" "2026-06-23T23:49:00Z" "complete" "BeforeTool")" \
      'AUDIT_LOG_MAX_BYTES=not-a-number' \
      2>"$errfile"
  )"; then
    status=0
  else
    status=$?
  fi

  security_assert_scanner_denial "$output"

  assert_equals "0" "$status" \
    "Expected block-mode exception handling to return exit code 0."
  assert_json_output "$output" "Expected block-mode exception handling to emit JSON."
  assert_file_contains "$errfile" 'scan incomplete' \
    "Expected sanitized scanner error on stderr."
  if grep -Fq 'Traceback' "$errfile"; then
    echo "Did not expect traceback in sanitized scanner error output." >&2
    cat "$errfile" >&2
    exit 1
  fi
}

test_unexpected_exception_warn_mode_warns_with_json_and_exit_zero() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local errfile
  local status

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  errfile="$workdir/warn.err"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'safe=true\n' > "$repo_dir/app.env"

  if output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "unexpected-warn" "2026-06-23T23:39:30Z" "2026-06-23T23:49:30Z" "complete" "BeforeTool")" \
      'AUDIT_LOG_MAX_BYTES=not-a-number' \
      2>"$errfile"
  )"; then
    status=0
  else
    status=$?
  fi

  assert_equals "0" "$status" \
    "Expected warn-mode exception handling to return exit code 0."
  assert_incomplete_warning "$output"
  assert_file_contains "$errfile" 'scan incomplete' \
    "Expected sanitized warn-mode scanner error on stderr."
  if grep -Fq 'Traceback' "$errfile"; then
    echo "Did not expect traceback in warn-mode sanitized scanner output." >&2
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
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'APP_MODE=development\n' > "$repo_dir/.env.local"

  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "env-variant" "2026-06-23T23:44:00Z" "2026-06-23T23:51:00Z" "complete" "SessionEnd")"
  )"

  assert_json_output "$output" "Expected scanner to emit JSON only."

  assert_file_contains "$log_dir/scan.log" '"envFiles":[".env.local"]' \
    "Expected .env variants to be logged when scanned."
  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected .env variants without secrets to remain clean."
  assert_equals "null" "$(jq -r '.systemMessage // empty // "null"' <<<"$output")" \
    "Did not expect clean scan to emit a systemMessage."
  if [[ "$output" != "{}" ]]; then
    echo "Expected .env variant without secrets to stay clean." >&2
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
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'These are deployment notes only.\n' > "$repo_dir/credentials.md"

  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "credential-path" "2026-06-23T23:43:00Z" "2026-06-23T23:52:00Z" "complete" "SessionEnd")"
  )"

  assert_json_output "$output" "Expected scanner to emit JSON only."

  assert_file_contains "$log_dir/scan.log" '"pattern":"credential_path"' \
    "Expected sensitive credential-like paths to produce a finding even without token-shaped content."
  assert_file_contains "$log_dir/scan.log" '"path":"credentials.md"' \
    "Expected credential-path finding to record the file path."
  if [[ "$output" != *"potential secrets detected"* ]]; then
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
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir/.ssh"

  init_git_repo "$repo_dir"
  fake_token="gh""p_$(printf '0%.0s' {1..36})"
  printf 'binary\0token=%s\n' "$fake_token" > "$repo_dir/.ssh/id_test"

  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "binary-credential" "2026-06-23T23:43:30Z" "2026-06-23T23:52:30Z" "complete" "SessionEnd")"
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

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  fake_token="gh""p_$(printf '0%.0s' {1..36})"
  security_prepare_unusual_scan "$repo_dir" "$fake_token"
  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "unusual-path" "2026-06-23T23:43:45Z" "2026-06-23T23:52:45Z" "complete" "SessionEnd")"
  )"

  assert_json_output "$output" "Expected unusual-path scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"path":"odd name.env","line":1' \
    "Expected the newline-bearing Git path to be scanned and safely displayed."
  assert_file_contains "$log_dir/scan.log" '"path":"notes.txt","line":2' \
    "Expected added content beginning with two plus signs to be scanned inside a hunk."
}

test_committed_literal_pathspec_filename_is_scanned() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local fake_token

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  fake_token="gh""p_$(printf '0%.0s' {1..36})"
  security_prepare_literal_pathspec_scan "$repo_dir" "$fake_token"
  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "literal-pathspec" "2026-06-23T23:43:50Z" "2026-06-23T23:52:50Z" "complete" "SessionEnd")"
  )"

  assert_json_output "$output" "Expected literal-pathspec scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"path":":(literal)notes.txt"' \
    "Expected Git pathspec syntax in a committed filename to stay literal."
  assert_file_contains "$log_dir/scan.log" '"pattern":"github_classic_pat"' \
    "Expected the literal pathspec-shaped file's added token to be scanned."
}

test_staged_scope_excludes_unrelated_untracked_files() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local fake_token

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  fake_token="gh""p_$(printf '0%.0s' {1..36})"
  security_prepare_staged_scope_scan "$repo_dir" "$fake_token"
  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      staged \
      "$(security_scanner_payload "$repo_dir" "staged-only" "2026-06-23T23:43:55Z" "2026-06-23T23:52:55Z" "complete" "SessionEnd")"
  )"

  assert_equals "{}" "$output" \
    "Expected staged scope to ignore an unrelated untracked secret-bearing file."
  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected the safe staged change to remain clean."
  if grep -Fq 'untracked.txt' "$log_dir/scan.log"; then
    echo "Did not expect staged scope to scan an unrelated untracked file." >&2
    cat "$log_dir/scan.log" >&2
    exit 1
  fi
}

test_staged_zero_prefix_filename_is_scanned() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local fake_token

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  fake_token="gh""p_$(printf '0%.0s' {1..36})"
  security_prepare_zero_prefix_scan "$repo_dir" "$fake_token"
  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      staged \
      "$(security_scanner_payload "$repo_dir" "zero-prefix" "2026-06-23T23:43:58Z" "2026-06-23T23:52:58Z" "complete" "SessionEnd")"
  )"

  assert_json_output "$output" "Expected staged zero-prefix scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"path":"0:notes.env"' \
    "Expected a staged filename beginning with 0: to use an unambiguous index lookup."
  assert_file_contains "$log_dir/scan.log" '"pattern":"github_classic_pat"' \
    "Expected the staged zero-prefix file's fake token to be scanned."
}

test_diff_scope_scans_cached_secret_when_worktree_matches_head() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local fake_token

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  fake_token="gh""p_$(printf '0%.0s' {1..36})"
  security_prepare_cached_scan "$repo_dir" "$fake_token"
  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "cached-only" "2026-06-23T23:43:59Z" "2026-06-23T23:52:59Z" "complete" "SessionEnd")"
  )"

  assert_json_output "$output" "Expected cached-only diff scan to emit JSON."
  assert_file_contains "$log_dir/scan.log" '"path":"notes.env"' \
    "Expected default diff scope to scan the HEAD-to-index source independently."
  assert_file_contains "$log_dir/scan.log" '"pattern":"github_classic_pat"' \
    "Expected a fake secret staged only in the index to be detected."
}

test_generic_secrets_filename_stays_clean() {
  local workdir
  local repo_dir
  local log_dir
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'notes only\n' > "$repo_dir/scan-secrets.sh"

  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "generic-secrets-name" "2026-06-23T23:45:00Z" "2026-06-23T23:53:00Z" "complete" "SessionEnd")"
  )"

  assert_json_output "$output" "Expected scanner to emit JSON only."

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

test_diff_mode_ignores_unchanged_secrets_in_touched_files() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local fake_token

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  if [[ "$SECURITY_SCANNER_PROVIDER" == copilot ]]; then
    fake_token="gh""p_123456789012345678901234567890123456"
    printf 'token=%s\nsafe=true\n' "$fake_token" > "$repo_dir/app.env"
    git -C "$repo_dir" add app.env
    git -C "$repo_dir" commit -qm "baseline"
    printf 'token=%s\nsafe=false\n' "$fake_token" > "$repo_dir/app.env"
  else
    fake_token="gh""p_1234567890abcdef1234567890abcdef1234"
    printf 'token=%s\ncontext=baseline\n' "$fake_token" > "$repo_dir/notes.txt"
    git -C "$repo_dir" add notes.txt
    git -C "$repo_dir" commit -qm "baseline"
    printf '%s\n' 'context=updated' >> "$repo_dir/notes.txt"
  fi

  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "unchanged-secret" "2026-06-23T23:42:00Z" "2026-06-23T23:54:30Z" "complete" "SessionEnd")"
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
  local secret_name

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir/docs"

  init_git_repo "$repo_dir"
  if [[ "$SECURITY_SCANNER_PROVIDER" == copilot ]]; then
    secret_name="sk""_live_1234567890ABCDEF.txt"
    printf 'safe content\n' > "$repo_dir/docs/$secret_name"
    git -C "$repo_dir" add "docs/$secret_name"
    git -C "$repo_dir" commit -qm "baseline"
    printf 'safe content updated\n' > "$repo_dir/docs/$secret_name"
  else
    secret_name="ghp_$(printf 'a%.0s' {1..36}).txt"
    printf '%s\n' 'safe content only' > "$repo_dir/$secret_name"
    git -C "$repo_dir" add "$secret_name"
    git -C "$repo_dir" commit -qm "baseline"

    printf '%s\n' 'safe content updated' >> "$repo_dir/$secret_name"
  fi

  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      warn \
      diff \
      "$(security_scanner_payload "$repo_dir" "header-ignore" "2026-06-23T23:42:30Z" "2026-06-23T23:54:40Z" "complete" "SessionEnd")"
  )"

  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected diff mode to ignore secret-like unified-diff header paths."
  if [[ "$output" != "{}" ]]; then
    echo "Expected diff mode to stay clean when only the diff header path looks secret-like." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
}

test_allowlist_suppresses_credential_path_finding() {
  local workdir
  local repo_dir
  local log_dir
  local output
  local mode

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  repo_dir="$workdir/repo"
  log_dir="$workdir/logs"
  mkdir -p "$repo_dir"

  init_git_repo "$repo_dir"
  printf 'notes only\n' > "$repo_dir/credentials.md"

  # Keep the original block-mode Copilot and warn-mode Gemini controls.
  mode=block
  if [[ "$SECURITY_SCANNER_PROVIDER" == gemini ]]; then mode=warn; fi
  output="$(
    security_run_scan \
      "$repo_dir" \
      "$log_dir" \
      "$mode" \
      diff \
      "$(security_scanner_payload "$repo_dir" "credential-allowlist" "2026-06-23T23:46:00Z" "2026-06-23T23:54:00Z" "complete" "SessionEnd")" \
      'SECRETS_ALLOWLIST=[{"tool":"scan_secrets","input":"credentials.md:1:credential_path:[SENSITIVE PATH]"}]'
  )"

  assert_json_output "$output" "Expected scanner to emit JSON only."

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

test_invalid_json_block_mode_denies_with_json_and_exit_zero() {
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

  if output="$(
    security_run_scan \
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

  security_assert_scanner_denial "$output"

  assert_equals "0" "$status" \
    "Expected invalid block-mode input to return exit code 0."
  assert_json_output "$output" "Expected invalid block-mode input to emit JSON."
}

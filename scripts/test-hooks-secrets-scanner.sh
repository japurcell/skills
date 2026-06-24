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
      bash "$REPO_ROOT/.copilot/hooks/scripts/scan-secrets.sh" <<<"$payload"
  )
}

init_git_repo() {
  local repo_dir="$1"

  git -C "$repo_dir" init -q
  git -C "$repo_dir" config user.email "copilot@example.com"
  git -C "$repo_dir" config user.name "Copilot Test"
  git -C "$repo_dir" config commit.gpgsign false
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
  if [[ "$output" != *"Potential secrets detected in modified files:"* ]]; then
    echo "Expected warn mode to print findings summary." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
}

test_block_mode_fails_when_findings_exist() {
  local workdir
  local repo_dir
  local log_dir

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

  if run_scan_hook \
    "$repo_dir" \
    "$log_dir" \
    block \
    diff \
    '{"sessionId":"block-session","timestamp":"2026-06-23T23:41:00Z","reason":"complete"}' \
    >"$workdir/block.out"
  then
    echo "Expected block mode to fail when secrets are detected." >&2
    exit 1
  fi

  assert_file_contains "$log_dir/scan.log" '"status":"findings"' \
    "Expected block mode to log findings before failing."
  assert_file_contains "$workdir/block.out" 'aws_access_key' \
    "Expected block mode output to include detected pattern name."
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
  if [[ "$output" != "Secrets scan clean." ]]; then
    echo "Expected diff mode to stay clean when only non-secret lines changed." >&2
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
  if [[ "$output" != *"credential_path"* ]]; then
    echo "Expected credential-path warning in hook output." >&2
    echo "Actual output: $output" >&2
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
  if [[ "$output" != "Secrets scan clean." ]]; then
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
  if [[ "$output" != "Secrets scan clean." ]]; then
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
      'SECRETS_ALLOWLIST=credentials.md:1:credential_path:[SENSITIVE PATH]'
  )"

  assert_file_contains "$log_dir/scan.log" '"status":"clean"' \
    "Expected allowlisted credential_path finding to stay clean."
  if grep -Fq '"pattern":"credential_path"' "$log_dir/scan.log"; then
    echo "Did not expect allowlisted credential_path finding to remain in log." >&2
    cat "$log_dir/scan.log" >&2
    exit 1
  fi
  if [[ "$output" != "Secrets scan clean." ]]; then
    echo "Expected allowlisted credential_path finding to be suppressed." >&2
    echo "Actual output: $output" >&2
    exit 1
  fi
}

test_hooks_json_registers_session_end_scanner() {
  assert_equals '$HOME/.copilot/hooks/scripts/scan-secrets.sh' \
    "$(jq -r '.hooks.sessionEnd[] | select(.bash == "$HOME/.copilot/hooks/scripts/scan-secrets.sh") | .bash' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to register the secrets scanner on sessionEnd."
  assert_equals warn \
    "$(jq -r '.hooks.sessionEnd[] | select(.bash == "$HOME/.copilot/hooks/scripts/scan-secrets.sh") | .env.SCAN_MODE' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to default secrets scanning to warn mode."
  assert_equals diff \
    "$(jq -r '.hooks.sessionEnd[] | select(.bash == "$HOME/.copilot/hooks/scripts/scan-secrets.sh") | .env.SCAN_SCOPE' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to scan working tree diffs by default."
}

main() {
  test_warn_mode_reports_findings_without_failing
  test_block_mode_fails_when_findings_exist
  test_diff_mode_ignores_unchanged_secrets_in_touched_files
  test_warn_mode_flags_sensitive_credential_paths_without_token_match
  test_env_variants_are_logged_but_not_flagged_by_path_alone
  test_generic_secrets_filename_stays_clean
  test_allowlist_suppresses_credential_path_finding
  test_hooks_json_registers_session_end_scanner
}

main "$@"

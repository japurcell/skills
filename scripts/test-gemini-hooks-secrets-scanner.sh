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
      bash "$REPO_ROOT/.gemini/hooks/scripts/scan-secrets.sh" <<<"$payload"
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
      'SECRETS_ALLOWLIST=credentials.md:1:credential_path:[SENSITIVE PATH]'
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

test_gemini_settings_register_session_end_scanner() {
  assert_equals '$HOME/.gemini/hooks/scripts/scan-secrets.sh' \
    "$(jq -r '.hooks.SessionEnd[0].hooks[] | select(.name == "scan-secrets") | .command // empty' "$REPO_ROOT/.gemini/settings.json")" \
    "Expected .gemini/settings.json to register scan-secrets.sh for Gemini SessionEnd."
}

main() {
  test_warn_mode_reports_findings_with_json_output
  test_env_variants_are_logged_but_not_flagged_by_path_alone
  test_warn_mode_flags_sensitive_credential_paths_without_token_match
  test_generic_secrets_filename_stays_clean
  test_allowlist_suppresses_credential_path_finding
  test_gemini_settings_register_session_end_scanner
}

main "$@"

#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

install_into_temp_home() {
  local home="$1"

  mkdir -p "$home"
  TMPDIR="$REPO_ROOT/.tmp" HOME="$home" "$REPO_ROOT/scripts/install.sh" >/dev/null
}

run_installed_auto_ingest_hook() {
  local home="$1"
  local payload="$2"
  shift 2

  env HOME="$home" AUDIT_LOG="$home/audit.log" "$@" python3 "$home/.gemini/hooks/scripts/auto-ingest.py" <<<"$payload"
}

write_manifest() {
  local path="$1"
  local content="$2"

  mkdir -p "$(dirname "$path")"
  python3 - "$path" "$content" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
content = sys.argv[2]
path.write_text(content, encoding="utf-8")
PY
}

write_text_file() {
  local path="$1"
  local content="$2"

  mkdir -p "$(dirname "$path")"
  python3 - "$path" "$content" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
content = sys.argv[2]
path.write_text(content, encoding="utf-8")
PY
}

sha256_file() {
  python3 -c 'import hashlib, pathlib, sys
path = pathlib.Path(sys.argv[1])
print(hashlib.sha256(path.read_bytes()).hexdigest(), end="")' "$1"
}

mtime_file() {
  python3 -c 'import pathlib, sys
path = pathlib.Path(sys.argv[1])
print(int(path.stat().st_mtime))' "$1"
}

test_session_start_startup_registers_auto_ingest_hook() {
  assert_equals '$HOME/.gemini/hooks/scripts/auto-ingest.py' \
    "$(jq -r '.hooks.SessionStart[] | select(.matcher == "startup") | .hooks[0].command // empty' "$REPO_ROOT/.gemini/settings.json")" \
    "Expected Gemini startup-only auto-ingest hook registration."
}

test_new_source_injects_scaffold_context_and_updates_manifest() {
  local workdir
  local home
  local repo_dir
  local source_dir
  local summary_dir
  local manifest_path
  local summary_file
  local output
  local context

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  repo_dir="$workdir/repo"
  source_dir="$repo_dir/.agents/sources"
  summary_dir="$repo_dir/.agents/memory/sources"
  manifest_path="$summary_dir/source-ingest-manifest.json"
  summary_file="$summary_dir/alpha-hooks-md.summary.md"

  mkdir -p "$source_dir" "$summary_dir"
  printf '# alpha\n' > "$source_dir/alpha-hooks.md"
  write_text_file "$repo_dir/.agents/skills/ingest-source/SKILL.md" $'---\nname: ingest-source\ndescription: wrong scope\n---\n\n# repo-local-ingest-source-marker\n'
  install_into_temp_home "$home"
  write_text_file "$home/.agents/skills/ingest-source/SKILL.md" $'---\nname: ingest-source\ndescription: wrong scope\n---\n\n# global-ingest-source-marker\n'

  output="$(
    run_installed_auto_ingest_hook \
      "$home" \
      '{"session_id":"ingest-new","timestamp":"2026-06-24T10:00:00Z","hook_event_name":"SessionStart","source":"startup","cwd":"'"$repo_dir"'"}' \
      AGENTS_SOURCE_SCAN_DIR="$source_dir" \
      AGENTS_SOURCE_SUMMARY_DIR="$summary_dir"
  )"

  context="$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"

  assert_file_contains <(printf '%s' "$context") \
    "new file" \
    "Expected new sources to be reported as stale."
  assert_file_contains <(printf '%s' "$context") \
    'Sources requiring `ingest-source`' \
    "Expected new sources to request ingest-source."
  assert_file_contains <(printf '%s' "$context") \
    '# /ingest-source' \
    "Expected new-source context to inject the built-in ingest-source guidance."
  assert_file_contains <(printf '%s' "$context") \
    'Update the summary executive summary and key findings with only verified facts.' \
    "Expected hard-coded ingest-source guidance to include the summary update workflow."
  if grep -Fq '# repo-local-ingest-source-marker' <<<"$context"; then
    echo "Expected auto-ingest to ignore repo-local ingest-source skill files." >&2
    exit 1
  fi
  if grep -Fq '# global-ingest-source-marker' <<<"$context"; then
    echo "Expected auto-ingest to ignore globally installed ingest-source skill copies." >&2
    exit 1
  fi
  assert_file_contains <(printf '%s' "$context") \
    "alpha-hooks-md.summary.md" \
    "Expected new sources to use filename-encoded summary names."
  assert_file_contains "$summary_file" \
    "## Executive Summary" \
    "Expected new sources to scaffold a summary template."
  assert_equals "needs_summary" \
    "$(jq -r '.entries[] | select(.source_path=="alpha-hooks.md") | .state' "$manifest_path")" \
    "Expected new sources to persist in the manifest as needing a summary."
}

test_missing_cwd_falls_back_to_process_working_directory() {
  local workdir
  local home
  local repo_dir
  local source_dir
  local summary_dir
  local manifest_path
  local output
  local context

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  repo_dir="$workdir/repo"
  source_dir="$repo_dir/.agents/sources"
  summary_dir="$repo_dir/.agents/memory/sources"
  manifest_path="$summary_dir/source-ingest-manifest.json"

  mkdir -p "$source_dir" "$summary_dir"
  printf '# fallback\n' > "$source_dir/fallback.md"

  install_into_temp_home "$home"

  output="$(
    cd "$repo_dir" && \
      run_installed_auto_ingest_hook \
        "$home" \
        '{"session_id":"ingest-fallback","timestamp":"2026-06-24T10:00:00Z","hook_event_name":"SessionStart","source":"startup"}'
  )"

  context="$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"

  assert_file_contains <(printf '%s' "$context") \
    "fallback.md" \
    "Expected the hook to resolve repo paths from the process working directory when cwd is missing."
  assert_equals "needs_summary" \
    "$(jq -r '.entries[] | select(.source_path=="fallback.md") | .state' "$manifest_path")" \
    "Expected missing cwd payloads to still update the manifest."
}

test_modified_source_keeps_existing_summary_and_marks_stale() {
  local workdir
  local home
  local repo_dir
  local source_dir
  local summary_dir
  local manifest_path
  local summary_file
  local summary_hash
  local before_mtime
  local after_mtime
  local output
  local context

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  repo_dir="$workdir/repo"
  source_dir="$repo_dir/.agents/sources"
  summary_dir="$repo_dir/.agents/memory/sources"
  manifest_path="$summary_dir/source-ingest-manifest.json"

  mkdir -p "$source_dir" "$summary_dir"
  printf 'original\n' > "$source_dir/beta-hooks.md"
  summary_file="$summary_dir/beta-hooks-md.summary.md"
  printf 'summary\n' > "$summary_file"
  summary_hash="$(sha256_file "$summary_file")"
  before_mtime="$(mtime_file "$summary_file")"

  write_manifest "$manifest_path" '{"version":1,"entries":[{"source_path":"beta-hooks.md","summary_path":"beta-hooks-md.summary.md","content_hash":"old-hash","summary_hash":"'"$summary_hash"'","size":9,"state":"active","reason":""}]}'
  printf 'modified content\n' > "$source_dir/beta-hooks.md"

  install_into_temp_home "$home"

  output="$(
    run_installed_auto_ingest_hook \
      "$home" \
      '{"session_id":"ingest-modified","timestamp":"2026-06-24T10:00:01Z","hook_event_name":"SessionStart","source":"startup","cwd":"'"$repo_dir"'"}' \
      AGENTS_SOURCE_SCAN_DIR="$source_dir" \
      AGENTS_SOURCE_SUMMARY_DIR="$summary_dir"
  )"

  context="$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"
  after_mtime="$(mtime_file "$summary_file")"

  assert_file_contains <(printf '%s' "$context") \
    "content modified" \
    "Expected modified sources to be marked stale."
  assert_equals "$before_mtime" "$after_mtime" \
    "Expected the hook to leave the existing summary file untouched."
  assert_equals "stale" \
    "$(jq -r '.entries[] | select(.source_path=="beta-hooks.md") | .state' "$manifest_path")" \
    "Expected modified sources to remain stale in the manifest."
}

test_renamed_source_preserves_orphan_context_and_scaffolds_new_summary() {
  local workdir
  local home
  local repo_dir
  local source_dir
  local summary_dir
  local manifest_path
  local old_summary_file
  local output
  local context
  local content_hash

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  repo_dir="$workdir/repo"
  source_dir="$repo_dir/.agents/sources"
  summary_dir="$repo_dir/.agents/memory/sources"
  manifest_path="$summary_dir/source-ingest-manifest.json"
  old_summary_file="$summary_dir/gamma-old-md.summary.md"

  mkdir -p "$source_dir" "$summary_dir"
  printf 'shared content\n' > "$source_dir/gamma-renamed.md"
  printf 'old summary\n' > "$old_summary_file"
  content_hash="$(python3 - <<'PY'
import hashlib
print(hashlib.sha256(b"shared content\n").hexdigest(), end="")
PY
)"
  write_manifest "$manifest_path" '{"version":1,"entries":[{"source_path":"gamma-old.md","summary_path":"gamma-old-md.summary.md","content_hash":"'"$content_hash"'","summary_hash":"'"$(sha256_file "$old_summary_file")"'","size":15,"state":"active","reason":""}]}'
  mv "$source_dir/gamma-renamed.md" "$source_dir/gamma-new.md"

  install_into_temp_home "$home"

  output="$(
    run_installed_auto_ingest_hook \
      "$home" \
      '{"session_id":"ingest-renamed","timestamp":"2026-06-24T10:00:02Z","hook_event_name":"SessionStart","source":"startup","cwd":"'"$repo_dir"'"}' \
      AGENTS_SOURCE_SCAN_DIR="$source_dir" \
      AGENTS_SOURCE_SUMMARY_DIR="$summary_dir"
  )"

  context="$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"

  assert_file_contains <(printf '%s' "$context") \
    "renamed/moved" \
    "Expected renamed sources to report a rename stale reason."
  assert_file_contains <(printf '%s' "$context") \
    "gamma-new-md.summary.md" \
    "Expected renamed sources to scaffold a new summary for the new path."
  assert_file_contains <(printf '%s' "$context") \
    "gamma-old-md.summary.md" \
    "Expected renamed sources to preserve the orphaned old summary path."
  assert_equals "orphan" \
    "$(jq -r '.entries[] | select(.source_path=="gamma-old.md") | .state' "$manifest_path")" \
    "Expected renamed source origins to remain as orphans in the manifest."
  assert_equals "needs_summary" \
    "$(jq -r '.entries[] | select(.source_path=="gamma-new.md") | .state' "$manifest_path")" \
    "Expected renamed source destinations to require a new summary."
}

test_deleted_source_keeps_orphan_only_context() {
  local workdir
  local home
  local repo_dir
  local source_dir
  local summary_dir
  local manifest_path
  local summary_file
  local output
  local context

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  repo_dir="$workdir/repo"
  source_dir="$repo_dir/.agents/sources"
  summary_dir="$repo_dir/.agents/memory/sources"
  manifest_path="$summary_dir/source-ingest-manifest.json"
  summary_file="$summary_dir/delta-hooks-md.summary.md"

  mkdir -p "$source_dir" "$summary_dir"
  printf 'orphan summary\n' > "$summary_file"
  write_manifest "$manifest_path" '{"version":1,"entries":[{"source_path":"delta-hooks.md","summary_path":"delta-hooks-md.summary.md","content_hash":"delta","summary_hash":"'"$(sha256_file "$summary_file")"'","size":5,"state":"active","reason":""}]}'

  install_into_temp_home "$home"

  output="$(
    run_installed_auto_ingest_hook \
      "$home" \
      '{"session_id":"ingest-deleted","timestamp":"2026-06-24T10:00:03Z","hook_event_name":"SessionStart","source":"startup","cwd":"'"$repo_dir"'"}' \
      AGENTS_SOURCE_SCAN_DIR="$source_dir" \
      AGENTS_SOURCE_SUMMARY_DIR="$summary_dir"
  )"

  context="$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"

  assert_file_contains <(printf '%s' "$context") \
    "deleted" \
    "Expected deleted sources to report cleanup-only context."
  assert_file_contains <(printf '%s' "$context") \
    "delta-hooks-md.summary.md" \
    "Expected deleted sources to preserve their orphan summary path."
  if grep -Fq 'Activate or load the `ingest-source` skill' <<<"$context"; then
    echo "Did not expect deleted sources to tell the agent to invoke ingest-source." >&2
    exit 1
  fi
  assert_equals "orphan" \
    "$(jq -r '.entries[] | select(.source_path=="delta-hooks.md") | .state' "$manifest_path")" \
    "Expected deleted sources to remain orphaned in the manifest."
}

test_manifest_summary_path_is_sanitized_to_basename() {
  local workdir
  local home
  local repo_dir
  local source_dir
  local summary_dir
  local manifest_path
  local external_summary
  local local_summary
  local expected_hash

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  repo_dir="$workdir/repo"
  source_dir="$repo_dir/.agents/sources"
  summary_dir="$repo_dir/.agents/memory/sources"
  manifest_path="$summary_dir/source-ingest-manifest.json"
  external_summary="$repo_dir/escape.summary.md"
  local_summary="$summary_dir/escape.summary.md"

  mkdir -p "$source_dir" "$summary_dir"
  printf 'outside summary\n' > "$external_summary"
  printf 'inside summary\n' > "$local_summary"
  expected_hash="$(sha256_file "$local_summary")"
  write_manifest "$manifest_path" '{"version":1,"entries":[{"source_path":"deleted.md","summary_path":"../../escape.summary.md","content_hash":"deleted-hash","summary_hash":"old-hash","size":1,"state":"active","reason":""}]}'

  install_into_temp_home "$home"

  run_installed_auto_ingest_hook \
    "$home" \
    '{"session_id":"sanitize-summary-path","timestamp":"2026-06-24T10:00:04Z","hook_event_name":"SessionStart","source":"startup","cwd":"'"$repo_dir"'"}' \
    AGENTS_SOURCE_SCAN_DIR="$source_dir" \
    AGENTS_SOURCE_SUMMARY_DIR="$summary_dir" >/dev/null

  assert_equals "$expected_hash" \
    "$(jq -r '.entries[] | select(.source_path=="deleted.md") | .summary_hash' "$manifest_path")" \
    "Expected manifest summary path sanitization to hash the local basename only."
}

test_gemini_auto_ingest_robust_audit_logging() {
  local workdir
  local home
  local repo_dir
  local source_dir
  local summary_dir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  repo_dir="$workdir/repo"
  source_dir="$repo_dir/.agents/sources"
  summary_dir="$repo_dir/.agents/memory/sources"
  audit_log="$home/audit.log"

  mkdir -p "$source_dir" "$summary_dir"
  install_into_temp_home "$home"

  # Case 1: no sources found
  output="$(
    run_installed_auto_ingest_hook \
      "$home" \
      '{"session_id":"ingest-logging-empty","timestamp":"2026-06-24T10:00:00Z","hook_event_name":"SessionStart","source":"startup","cwd":"'"$repo_dir"'"}' \
      AGENTS_SOURCE_SCAN_DIR="$source_dir" \
      AGENTS_SOURCE_SUMMARY_DIR="$summary_dir"
  )"
  assert_file_contains "$audit_log" "Message: auto-ingest scan complete: no context injected (no sources found)" \
    "Expected Gemini audit log to record no context injected when no sources found."

  # Case 2: context injected
  printf '# hello\n' > "$source_dir/hello.md"
  output="$(
    run_installed_auto_ingest_hook \
      "$home" \
      '{"session_id":"ingest-logging-injected","timestamp":"2026-06-24T10:00:01Z","hook_event_name":"SessionStart","source":"startup","cwd":"'"$repo_dir"'"}' \
      AGENTS_SOURCE_SCAN_DIR="$source_dir" \
      AGENTS_SOURCE_SUMMARY_DIR="$summary_dir"
  )"
  assert_file_contains "$audit_log" "Message: auto-ingest scan complete: context injected. Findings: 1" \
    "Expected Gemini audit log to record context injected."
  assert_file_contains "$audit_log" "Finding: state=needs_summary, reason=new file, path=hello.md" \
    "Expected Gemini audit log to log the individual finding details."

  # Case 3: all summaries up to date
  # Write summary for hello.md
  printf '# Summary for hello\n\nVerified summary.\n' > "$summary_dir/hello-md.summary.md"
  # Run once to sync manifest
  output="$(
    run_installed_auto_ingest_hook \
      "$home" \
      '{"session_id":"ingest-logging-sync","timestamp":"2026-06-24T10:00:02Z","hook_event_name":"SessionStart","source":"startup","cwd":"'"$repo_dir"'"}' \
      AGENTS_SOURCE_SCAN_DIR="$source_dir" \
      AGENTS_SOURCE_SUMMARY_DIR="$summary_dir"
  )"
  # Run again to get "all summaries up to date"
  output="$(
    run_installed_auto_ingest_hook \
      "$home" \
      '{"session_id":"ingest-logging-uptodate","timestamp":"2026-06-24T10:00:03Z","hook_event_name":"SessionStart","source":"startup","cwd":"'"$repo_dir"'"}' \
      AGENTS_SOURCE_SCAN_DIR="$source_dir" \
      AGENTS_SOURCE_SUMMARY_DIR="$summary_dir"
  )"
  assert_file_contains "$audit_log" "Message: auto-ingest scan complete: no context injected (all summaries up to date)" \
    "Expected Gemini audit log to record no context injected when all summaries are up to date."

  # Case 4: hard stop logging
  # Run with invalid payload that is not a json object
  output="$(
    env HOME="$home" AUDIT_LOG="$audit_log" python3 "$home/.gemini/hooks/scripts/auto-ingest.py" <<<"invalid-payload" || true
  )"
  assert_file_contains "$audit_log" "Error: Hook hard stop: Invalid hook input: expected a JSON object" \
    "Expected Gemini audit log to capture hard stop error when invalid JSON is supplied."
}

main() {
  test_session_start_startup_registers_auto_ingest_hook
  test_new_source_injects_scaffold_context_and_updates_manifest
  test_missing_cwd_falls_back_to_process_working_directory
  test_modified_source_keeps_existing_summary_and_marks_stale
  test_renamed_source_preserves_orphan_context_and_scaffolds_new_summary
  test_deleted_source_keeps_orphan_only_context
  test_manifest_summary_path_is_sanitized_to_basename
  test_gemini_auto_ingest_robust_audit_logging
}

main "$@"

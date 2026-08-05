#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

make_text_file() {
  local path="$1"
  local content="$2"

  CONTENT="$content" python3 -c 'import os, sys
from pathlib import Path
path = Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(os.environ["CONTENT"], encoding="utf-8")' "$path"
}

summary_name_for_source() {
  python3 -c 'from pathlib import Path
import sys
relpath = Path(sys.argv[1])
encoded = "__".join(part.replace(".", "-") for part in relpath.parts)
print(f"{encoded}.summary.md")' "$1"
}

sha256_file() {
  python3 -c 'import hashlib, pathlib, sys
path = pathlib.Path(sys.argv[1])
print(hashlib.sha256(path.read_bytes()).hexdigest(), end="")' "$1"
}

run_auto_ingest_hook() {
  local audit_log="$1"
  local payload="$2"
  local root="$3"

  run_copilot_hook \
    "auto-ingest-source.py" \
    "$audit_log" \
    "$payload" \
    "" \
    "COPILOT_AUTO_INGEST_REPO_ROOT=$root" \
    "COPILOT_AUTO_INGEST_SUMMARY_DIR=$root/.agents/memory/sources"
}

test_session_start_auto_ingest_materializes_manifest_and_surfaces_all_stale_reasons() {
  local workdir
  local audit_log
  local output
  local state_dir
  local manifest_path
  local modified_before_hash
  local renamed_old_before_hash
  local deleted_before_hash
  local modified_summary
  local renamed_old_summary
  local deleted_summary
  local new_summary
  local renamed_new_summary

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  state_dir="$workdir/.agents/memory/sources"
  manifest_path="$state_dir/source-ingest-manifest.json"

  mkdir -p "$workdir/.agents/sources"
  make_text_file "$workdir/.agents/sources/unchanged.md" $'unchanged source v1\n'
  make_text_file "$workdir/.agents/sources/modified.md" $'modified source v1\n'
  make_text_file "$workdir/.agents/sources/rename-old.md" $'rename source v1\n'
  make_text_file "$workdir/.agents/sources/deleted.md" $'deleted source v1\n'

  output="$(
    run_auto_ingest_hook \
      "$audit_log" \
      '{"sessionId":"auto-ingest-session","timestamp":"2026-05-21T09:00:00Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "$workdir"
  )"

  assert_equals "true" "$(jq -r 'has("additionalContext")' <<<"$output")" \
    "Expected Copilot CLI auto-ingest payloads to return additionalContext."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") 'Sources requiring `ingest-source`' \
    "Expected initial auto-ingest run to request ingest-source for scaffolded summaries."
  assert_file_contains "$manifest_path" '"state": "needs_summary"' \
    "Expected auto-ingest run to write needs_summary manifest entries for new sources."

  modified_summary="$state_dir/$(summary_name_for_source "modified.md")"
  renamed_old_summary="$state_dir/$(summary_name_for_source "rename-old.md")"
  deleted_summary="$state_dir/$(summary_name_for_source "deleted.md")"
  modified_before_hash="$(sha256_file "$modified_summary")"
  renamed_old_before_hash="$(sha256_file "$renamed_old_summary")"
  deleted_before_hash="$(sha256_file "$deleted_summary")"

  make_text_file "$workdir/.agents/sources/modified.md" $'modified source v2\n'
  rm -f "$workdir/.agents/sources/rename-old.md"
  make_text_file "$workdir/.agents/sources/rename-new.md" $'rename source v1\n'
  rm -f "$workdir/.agents/sources/deleted.md"
  make_text_file "$workdir/.agents/sources/new.md" $'new source v1\n'

  output="$(
    run_auto_ingest_hook \
      "$audit_log" \
      '{"sessionId":"auto-ingest-session","timestamp":"2026-05-21T09:00:01Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "$workdir"
  )"

  assert_file_contains <(jq -r '.additionalContext' <<<"$output") 'Sources requiring `ingest-source`' \
    "Expected auto-ingest output to mention new files."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") "content modified" \
    "Expected auto-ingest output to mention modified files."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") "renamed/moved" \
    "Expected auto-ingest output to mention renamed files."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") "Orphan summaries requiring cleanup" \
    "Expected auto-ingest output to mention deleted files."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") 'Do not invoke `ingest-source` for deleted sources' \
    "Expected deleted-source context to be cleanup-only."

  assert_equals "$modified_before_hash" "$(sha256_file "$modified_summary")" \
    "Expected the modified summary to remain untouched."
  assert_equals "$renamed_old_before_hash" "$(sha256_file "$renamed_old_summary")" \
    "Expected the orphaned rename summary to remain untouched."
  assert_equals "$deleted_before_hash" "$(sha256_file "$deleted_summary")" \
    "Expected the orphaned deleted summary to remain untouched."

  renamed_new_summary="$state_dir/$(summary_name_for_source "rename-new.md")"
  new_summary="$state_dir/$(summary_name_for_source "new.md")"

  assert_file_contains "$new_summary" "## Executive Summary" \
    "Expected the new source to receive a scaffolded summary."
  assert_file_contains "$renamed_new_summary" "## Key Findings" \
    "Expected the renamed source to receive a new scaffolded summary."

  assert_file_contains "$manifest_path" '"rename-old.md"' \
    "Expected the manifest to preserve the orphaned rename source."
  assert_file_contains "$manifest_path" '"deleted.md"' \
    "Expected the manifest to preserve the orphaned deleted source."
  assert_file_contains "$manifest_path" '"rename-new.md"' \
    "Expected the manifest to add the renamed destination source."
  assert_file_contains "$manifest_path" '"new.md"' \
    "Expected the manifest to add the new source."
}

test_session_start_auto_ingest_outputs_vscode_schema_for_new_sources() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mkdir -p "$workdir/.agents/sources"
  make_text_file "$workdir/.agents/sources/sample.md" $'sample source v1\n'

  output="$(
    run_auto_ingest_hook \
      "$audit_log" \
      '{"hookEventName":"SessionStart","session_id":"vscode-session","timestamp":"2026-05-21T09:00:02Z","source":"vscode","initial_prompt":"hello"}' \
      "$workdir"
  )"

  assert_equals "true" "$(jq -r 'has("hookSpecificOutput")' <<<"$output")" \
    "Expected VS Code session-start payloads to return hookSpecificOutput."
  assert_equals "SessionStart" "$(jq -r '.hookSpecificOutput.hookEventName' <<<"$output")" \
    "Expected VS Code output to preserve the SessionStart event name."
  assert_file_contains <(jq -r '.hookSpecificOutput.additionalContext' <<<"$output") 'Sources requiring `ingest-source`' \
    "Expected VS Code auto-ingest context to mention the new source."
}

test_manifest_summary_path_is_sanitized_to_basename() {
  local workdir
  local audit_log
  local state_dir
  local manifest_path
  local external_summary
  local local_summary
  local expected_hash

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  state_dir="$workdir/.agents/memory/sources"
  manifest_path="$state_dir/source-ingest-manifest.json"
  external_summary="$workdir/escape.summary.md"
  local_summary="$state_dir/escape.summary.md"

  mkdir -p "$workdir/.agents/sources" "$state_dir"
  make_text_file "$external_summary" $'outside summary\n'
  make_text_file "$local_summary" $'inside summary\n'
  expected_hash="$(sha256_file "$local_summary")"
  python3 - "$manifest_path" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
payload = {
    "version": 1,
    "entries": [
        {
            "source_path": "deleted.md",
            "summary_path": "../../escape.summary.md",
            "content_hash": "deleted-hash",
            "summary_hash": "old-hash",
            "size": 1,
            "state": "active",
            "reason": "",
        }
    ],
}
path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

  run_auto_ingest_hook \
    "$audit_log" \
    '{"sessionId":"sanitize-summary-path","timestamp":"2026-05-21T09:00:03Z","source":"copilot-cli","initialPrompt":"hello"}' \
    "$workdir" >/dev/null

  assert_equals "$expected_hash" \
    "$(jq -r '.entries[] | select(.source_path=="deleted.md") | .summary_hash' "$manifest_path")" \
    "Expected manifest summary path sanitization to hash the local basename only."
}

test_hooks_json_registers_auto_ingest_between_send_event_and_required_skills() {
  assert_equals '$HOME/.copilot/hooks/scripts/send-event.py' \
    "$(jq -r '.hooks.sessionStart[0].bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected send-event.py to remain first for sessionStart."

  assert_equals '$HOME/.copilot/hooks/scripts/auto-ingest-source.py' \
    "$(jq -r '.hooks.sessionStart[1].bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected auto-ingest-source.py to run immediately after send-event.py."

  assert_equals '$HOME/.copilot/hooks/scripts/load-required-skills.py' \
    "$(jq -r '.hooks.sessionStart[2].bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected load-required-skills.py to remain after auto-ingest-source.py."
}

main() {
  test_session_start_auto_ingest_materializes_manifest_and_surfaces_all_stale_reasons
  test_session_start_auto_ingest_outputs_vscode_schema_for_new_sources
  test_manifest_summary_path_is_sanitized_to_basename
  test_hooks_json_registers_auto_ingest_between_send_event_and_required_skills
}

main "$@"

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
  local home="${4:-}"

  local extra_env=(
    "AUDIT_LOG=$audit_log"
    "COPILOT_AUTO_INGEST_REPO_ROOT=$root"
    "COPILOT_AUTO_INGEST_SUMMARY_DIR=$root/.agents/memory/sources"
  )
  if [[ -n "$home" ]]; then
    extra_env+=("HOME=$home")
  fi

  run_copilot_hook \
    "auto-ingest-source.py" \
    "$audit_log" \
    "$payload" \
    "" \
    "${extra_env[@]}"
}

run_repo_local_auto_ingest_hook() {
  local audit_log="$1"
  local payload="$2"
  local root="$3"
  local home="${4:-}"

  local extra_env=(
    "AUDIT_LOG=$audit_log"
    "COPILOT_AUTO_INGEST_REPO_ROOT=$root"
    "COPILOT_AUTO_INGEST_SUMMARY_DIR=$root/.agents/memory/sources"
  )
  if [[ -n "$home" ]]; then
    extra_env+=("HOME=$home")
  fi

  env "${extra_env[@]}" python3 "$REPO_ROOT/.github/hooks/scripts/auto-ingest-source.py" <<<"$payload"
}

run_user_prompt_transformed_auto_ingest_hook() {
  local audit_log="$1"
  local payload="$2"
  local root="$3"
  local home="${4:-}"

  local extra_env=(
    "AUDIT_LOG=$audit_log" \
    "COPILOT_AUTO_INGEST_REPO_ROOT=$root" \
    "COPILOT_AUTO_INGEST_SUMMARY_DIR=$root/.agents/memory/sources" \
    "COPILOT_AUTO_INGEST_HELPER_PATH=$REPO_ROOT/.github/hooks/scripts/helpers/auto_ingest.py"
  )
  if [[ -n "$home" ]]; then
    extra_env+=("HOME=$home")
  fi

  env "${extra_env[@]}" python3 "$REPO_ROOT/.github/hooks/scripts/inject-auto-ingest-context.py" <<<"$payload"
}

run_agent_stop_auto_ingest_hook() {
  local audit_log="$1"
  local payload="$2"
  local root="$3"
  local home="${4:-}"

  local extra_env=(
    "AUDIT_LOG=$audit_log" \
    "COPILOT_AUTO_INGEST_REPO_ROOT=$root" \
    "COPILOT_AUTO_INGEST_SUMMARY_DIR=$root/.agents/memory/sources" \
    "COPILOT_AUTO_INGEST_HELPER_PATH=$REPO_ROOT/.github/hooks/scripts/helpers/auto_ingest.py"
  )
  if [[ -n "$home" ]]; then
    extra_env+=("HOME=$home")
  fi

  env "${extra_env[@]}" python3 "$REPO_ROOT/.github/hooks/scripts/inject-auto-ingest-context.py" <<<"$payload"
}

test_session_start_auto_ingest_materializes_manifest_and_surfaces_all_stale_reasons() {
  local workdir
  local audit_log
  local output
  local home_dir
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
  home_dir="$workdir/home"
  state_dir="$workdir/.agents/memory/sources"
  manifest_path="$state_dir/source-ingest-manifest.json"

  mkdir -p "$workdir/.agents/sources"
  make_text_file "$workdir/.agents/sources/unchanged.md" $'unchanged source v1\n'
  make_text_file "$workdir/.agents/sources/modified.md" $'modified source v1\n'
  make_text_file "$workdir/.agents/sources/rename-old.md" $'rename source v1\n'
  make_text_file "$workdir/.agents/sources/deleted.md" $'deleted source v1\n'
  make_text_file "$workdir/.agents/skills/ingest-source/SKILL.md" $'---\nname: ingest-source\ndescription: repo local scope\n---\n\n# repo-skill-marker\n'
  make_text_file "$workdir/skills/ingest-source/SKILL.md" $'---\nname: ingest-source\ndescription: wrong scope\n---\n\n# legacy-skill-marker\n'
  make_text_file "$home_dir/.agents/skills/ingest-source/SKILL.md" $'---\nname: ingest-source\ndescription: wrong scope\n---\n\n# global-ingest-source-marker\n'

  output="$(
    run_repo_local_auto_ingest_hook \
      "$audit_log" \
      '{"sessionId":"auto-ingest-session","timestamp":"2026-05-21T09:00:00Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "$workdir" \
      "$home_dir"
  )"

  assert_equals "true" "$(jq -r 'has("additionalContext")' <<<"$output")" \
    "Expected Copilot CLI auto-ingest payloads to return additionalContext."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") 'Pending ingest blocks normal work.' \
    "Expected initial auto-ingest run to block normal work while summaries are pending."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") 'Activate or load the `ingest-source` skill, then run `/ingest-source`.' \
    "Expected initial auto-ingest run to point at the real ingest-source skill."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") '## Pending entries' \
    "Expected initial auto-ingest run to list pending entries."
  if jq -r '.additionalContext' <<<"$output" | grep -Fq '# legacy-skill-marker'; then
    echo "Expected auto-ingest to ignore legacy skills/ ingest-source copies." >&2
    exit 1
  fi
  if jq -r '.additionalContext' <<<"$output" | grep -Fq '# global-ingest-source-marker'; then
    echo "Expected auto-ingest to ignore globally installed ingest-source skill copies." >&2
    exit 1
  fi
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
    run_repo_local_auto_ingest_hook \
      "$audit_log" \
      '{"sessionId":"auto-ingest-session","timestamp":"2026-05-21T09:00:01Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "$workdir" \
      "$home_dir"
  )"

  assert_file_contains <(jq -r '.additionalContext' <<<"$output") 'Pending ingest blocks normal work.' \
    "Expected auto-ingest output to mention pending ingest blocks."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") "content modified" \
    "Expected auto-ingest output to mention modified files."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") "renamed/moved" \
    "Expected auto-ingest output to mention renamed files."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") "Orphan summaries requiring cleanup" \
    "Expected auto-ingest output to mention deleted files."
  assert_file_contains <(jq -r '.additionalContext' <<<"$output") 'Pending ingest blocks normal work.' \
    "Expected auto-ingest output to block normal work for pending entries."

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

test_user_prompt_transformed_injects_auto_ingest_context_and_materializes_manifest() {
  local workdir
  local audit_log
  local output
  local transformed
  local manifest_path
  local summary_path
  local home_dir

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  home_dir="$workdir/home"
  manifest_path="$workdir/.agents/memory/sources/source-ingest-manifest.json"
  summary_path="$workdir/.agents/memory/sources/$(summary_name_for_source "prompt-source.md")"

  mkdir -p "$workdir/.agents/sources"
  make_text_file "$workdir/.agents/sources/prompt-source.md" $'prompt source v1\n'
  make_text_file "$workdir/.agents/skills/ingest-source/SKILL.md" $'---\nname: ingest-source\ndescription: repo local scope\n---\n\n# repo-skill-marker\n'

  output="$(
    run_user_prompt_transformed_auto_ingest_hook \
      "$audit_log" \
      '{"sessionId":"prompt-auto-ingest","timestamp":"2026-05-21T09:00:00Z","cwd":"'"$workdir"'","prompt":"What is your training cut off date?","transformedPrompt":"What is your training cut off date?"}' \
      "$workdir" \
      "$home_dir"
  )"

  transformed="$(jq -r '.modifiedTransformedPrompt' <<<"$output")"

  assert_file_contains <(printf '%s' "$transformed") 'Pending ingest blocks normal work.' \
    "Expected userPromptTransformed auto-ingest to prepend pending-ingest context."
  assert_file_contains <(printf '%s' "$transformed") 'Pending ingest blocks normal work.' \
    "Expected userPromptTransformed auto-ingest to block normal work."
  assert_file_contains <(printf '%s' "$transformed") 'What is your training cut off date?' \
    "Expected userPromptTransformed auto-ingest to preserve the original model-facing prompt."
  assert_file_contains "$summary_path" '## Executive Summary' \
    "Expected userPromptTransformed auto-ingest to scaffold the missing summary."
  assert_file_contains "$manifest_path" '"state": "needs_summary"' \
    "Expected userPromptTransformed auto-ingest to persist stale manifest entries."
}

test_user_prompt_transformed_uses_recovery_checklist_when_skill_missing() {
  local workdir
  local audit_log
  local output
  local transformed

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mkdir -p "$workdir/.agents/sources"
  make_text_file "$workdir/.agents/sources/missing-skill.md" $'missing skill source v1\n'
  make_text_file "$workdir/skills/ingest-source/SKILL.md" $'---\nname: ingest-source\ndescription: wrong scope\n---\n\n# legacy-skill-marker\n'
  make_text_file "$workdir/home/.agents/skills/ingest-source/SKILL.md" $'---\nname: ingest-source\ndescription: wrong scope\n---\n\n# installed-ingest-source-marker\n'

  output="$(
    env \
      "AUDIT_LOG=$audit_log" \
      "COPILOT_AUTO_INGEST_REPO_ROOT=$workdir" \
      "COPILOT_AUTO_INGEST_SUMMARY_DIR=$workdir/.agents/memory/sources" \
      "COPILOT_AUTO_INGEST_HELPER_PATH=$REPO_ROOT/.github/hooks/scripts/helpers/auto_ingest.py" \
      HOME="$workdir/home" \
      python3 "$REPO_ROOT/.github/hooks/scripts/inject-auto-ingest-context.py" \
      <<< '{"sessionId":"prompt-auto-ingest-missing-skill","timestamp":"2026-05-21T09:00:00Z","cwd":"'"$workdir"'","prompt":"hello","transformedPrompt":"hello"}'
  )"

  transformed="$(jq -r '.modifiedTransformedPrompt' <<<"$output")"

  assert_file_contains <(printf '%s' "$transformed") 'Recovery checklist' \
    "Expected missing ingest-source skill to surface a recovery checklist."
  assert_file_contains <(printf '%s' "$transformed") 'Restore `.agents/skills/ingest-source/SKILL.md`' \
    "Expected missing ingest-source skill to tell the user how to restore it."
  assert_file_contains <(printf '%s' "$transformed") 'Pending ingest blocks normal work.' \
    "Expected missing ingest-source skill to keep the turn blocked."
}

test_agent_stop_blocks_pending_ingest() {
  local workdir
  local audit_log
  local output
  local home_dir

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  home_dir="$workdir/home"

  mkdir -p "$workdir/.agents/sources"
  make_text_file "$workdir/.agents/sources/pending.md" $'pending source v1\n'
  make_text_file "$workdir/.agents/skills/ingest-source/SKILL.md" $'---\nname: ingest-source\ndescription: repo local scope\n---\n\n# repo-skill-marker\n'

  output="$(
    run_agent_stop_auto_ingest_hook \
      "$audit_log" \
      '{"sessionId":"block-pending-ingest","timestamp":"2026-05-21T09:00:02Z","hookEventName":"agentStop","source":"copilot-cli","transcriptPath":"'"$workdir"'/transcript.jsonl","stopReason":"end_turn"}' \
      "$workdir" \
      "$home_dir"
  )"

  assert_equals "block" "$(jq -r '.decision' <<<"$output")" \
    "Expected Copilot agentStop pending ingest gate to block normal work."
  assert_file_contains <(jq -r '.reason' <<<"$output") 'Pending ingest blocks normal work.' \
    "Expected Copilot agentStop block reason to call out pending ingest."
  assert_file_contains <(jq -r '.reason' <<<"$output") 'pending.md' \
    "Expected Copilot agentStop block reason to list the pending source."
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
    run_repo_local_auto_ingest_hook \
      "$audit_log" \
      '{"hookEventName":"SessionStart","session_id":"vscode-session","timestamp":"2026-05-21T09:00:02Z","source":"vscode","initial_prompt":"hello"}' \
      "$workdir"
  )"

  assert_equals "true" "$(jq -r 'has("hookSpecificOutput")' <<<"$output")" \
    "Expected VS Code session-start payloads to return hookSpecificOutput."
  assert_equals "SessionStart" "$(jq -r '.hookSpecificOutput.hookEventName' <<<"$output")" \
    "Expected VS Code output to preserve the SessionStart event name."
  assert_file_contains <(jq -r '.hookSpecificOutput.additionalContext' <<<"$output") 'Pending ingest blocks normal work.' \
    "Expected VS Code auto-ingest context to mention the pending ingest block."
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

  run_repo_local_auto_ingest_hook \
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

  assert_equals '$HOME/.copilot/hooks/scripts/load-required-skills.py' \
    "$(jq -r '.hooks.sessionStart[1].bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected load-required-skills.py to remain after send-event.py."

  assert_equals '.github/hooks/scripts/auto-ingest-source.py' \
    "$(jq -r '.hooks.sessionStart[0].bash // empty' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local hooks.json to register auto-ingest-source.py."

  assert_equals 1 \
    "$(jq -r '.hooks.sessionStart | length' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local hooks.json to contain only the auto-ingest startup hook."

  assert_equals '.github/hooks/scripts/inject-auto-ingest-context.py' \
    "$(jq -r '.hooks.agentStop[0].bash // empty' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local agentStop to end with the pending-ingest backstop."

  assert_equals '.github/hooks/scripts/inject-auto-ingest-context.py' \
    "$(jq -r '.hooks.subagentStop[0].bash // empty' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local subagentStop to end with the pending-ingest backstop."
}

test_ingest_source_skill_is_checked_in() {
  assert_file_contains "$REPO_ROOT/.agents/skills/ingest-source/SKILL.md" \
    'Process every blocking source in the manifest in one run.' \
    "Expected the ingest-source skill to describe batch ingestion."
  assert_file_contains "$REPO_ROOT/.agents/skills/ingest-source/SKILL.md" \
    'Do not silently replace an existing summary.' \
    "Expected the ingest-source skill to preserve summary guardrails."
}

test_auto_ingest_robust_audit_logging() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  # Case 1: no sources found (empty .agents/sources)
  mkdir -p "$workdir/.agents/sources"
  output="$(
    run_repo_local_auto_ingest_hook \
      "$audit_log" \
      '{"sessionId":"logging-session","timestamp":"2026-05-21T09:00:00Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "$workdir"
  )"
  assert_file_contains "$audit_log" "Findings: 0, no context injected (no sources found)" \
    "Expected audit log to record that no context was injected because no sources were found."

  # Case 2: new sources added -> context injected -> logs findings
  make_text_file "$workdir/.agents/sources/test1.md" $'test1\n'
  output="$(
    run_repo_local_auto_ingest_hook \
      "$audit_log" \
      '{"sessionId":"logging-session","timestamp":"2026-05-21T09:00:01Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "$workdir"
  )"
  assert_file_contains "$audit_log" "Findings: 1, context injected" \
    "Expected audit log to record context injected for new source."
  assert_file_contains "$audit_log" "Finding: state=needs_summary, reason=new file, path=test1.md" \
    "Expected audit log to log individual finding with state and reason."

  # Case 3: all summaries up to date -> no context injected
  # To make summaries up to date, let's create a non-scaffold summary for test1.md.
  # Let's see, what is the summary filename? It should be test1-md.summary.md.
  # Let's write some content without "status: scaffold".
  mkdir -p "$workdir/.agents/memory/sources"
  make_text_file "$workdir/.agents/memory/sources/test1-md.summary.md" $'# Summary for test1\n\nVerified summary content.\n'
  # And let's run the hook again so the manifest updates with active state and the actual summary hash.
  output="$(
    run_repo_local_auto_ingest_hook \
      "$audit_log" \
      '{"sessionId":"logging-session","timestamp":"2026-05-21T09:00:02Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "$workdir"
  )"
  # Now let's run it one more time to test the "all summaries up to date" case.
  output="$(
    run_repo_local_auto_ingest_hook \
      "$audit_log" \
      '{"sessionId":"logging-session","timestamp":"2026-05-21T09:00:03Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "$workdir"
  )"
  assert_file_contains "$audit_log" "Findings: 0, no context injected (all summaries up to date)" \
    "Expected audit log to record that all summaries were up to date."

  # Case 4: failure logging (invalid payload)
  output="$(
    run_repo_local_auto_ingest_hook \
      "$audit_log" \
      'not-a-json' \
      "$workdir" || true
  )"
  assert_file_contains "$audit_log" "Error: Invalid hook input: expected a JSON object" \
    "Expected audit log to capture invalid payload failure."
}

main() {
  test_session_start_auto_ingest_materializes_manifest_and_surfaces_all_stale_reasons
  test_user_prompt_transformed_injects_auto_ingest_context_and_materializes_manifest
  test_user_prompt_transformed_uses_recovery_checklist_when_skill_missing
  test_agent_stop_blocks_pending_ingest
  test_session_start_auto_ingest_outputs_vscode_schema_for_new_sources
  test_manifest_summary_path_is_sanitized_to_basename
  test_hooks_json_registers_auto_ingest_between_send_event_and_required_skills
  test_ingest_source_skill_is_checked_in
  test_auto_ingest_robust_audit_logging
}

main "$@"

#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

assert_caveman_context_shape() {
  local context="$1"

  assert_file_contains <(printf '%s' "$context") "Required skill context loaded." \
    "Expected required skill context marker in additionalContext."
  assert_file_contains <(printf '%s' "$context") "Respond terse like smart caveman." \
    "Expected required context to include caveman content."

  if [[ "$context" == *"# Universal Guidelines"* || "$context" == *"# CLI Compression"* || "$context" == *"# Context Engineering"* ]]; then
    echo "Expected startup hooks to load only caveman skill context." >&2
    printf '%s\n' "$context" >&2
    exit 1
  fi
}

hook_final_json() {
  python3 -c 'import json, sys
preserved = []
for line in sys.stdin.read().splitlines():
    stripped = line.strip()
    if stripped:
        try:
            payload = json.loads(stripped)
            if isinstance(payload, dict) and payload.get("type") == "progress":
                continue
        except json.JSONDecodeError:
            pass
    preserved.append(line)
print("\n".join(preserved).strip(), end="")' <<<"$1"
}

assert_progress_message() {
  local output="$1"
  local expected="$2"

  HOOK_OUTPUT="$output" python3 -c 'import json, os, sys
expected = sys.argv[1]
for line in os.environ["HOOK_OUTPUT"].splitlines():
    try:
        payload = json.loads(line.strip())
    except json.JSONDecodeError:
        continue
    if isinstance(payload, dict) and payload.get("type") == "progress" and payload.get("message") == expected:
        raise SystemExit(0)
print(f"Expected progress message: {expected}", file=sys.stderr)
raise SystemExit(1)' "$expected"
}

assert_no_progress_messages() {
  local output="$1"

  HOOK_OUTPUT="$output" python3 -c 'import json, os, sys
for line in os.environ["HOOK_OUTPUT"].splitlines():
    try:
        payload = json.loads(line.strip())
    except json.JSONDecodeError:
        continue
    if isinstance(payload, dict) and payload.get("type") == "progress":
        print("Unexpected progress message: " + str(payload.get("message")), file=sys.stderr)
        raise SystemExit(1)'
}

run_session_start_hook() {
  local audit_log="$1"
  local payload="$2"

  run_copilot_hook "load-required-skills.py" "$audit_log" "$payload" "" "AGENTS_REQUIRED_SKILL_FILES=caveman/SKILL.md"
}

run_subagent_start_hook() {
  local audit_log="$1"
  local payload="$2"

  run_copilot_hook "load-required-skills.py" "$audit_log" "$payload" "" "AGENTS_REQUIRED_SKILL_FILES=caveman/SKILL.md"
}

test_session_start_outputs_cli_schema_with_caveman_only_context() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(run_session_start_hook "$audit_log" '{"sessionId":"cli-session","timestamp":"2026-05-21T09:00:00Z","source":"copilot-cli","initialPrompt":"hello"}')"
  output="$(hook_final_json "$output")"

  assert_equals "true" "$(jq -r 'has("additionalContext")' <<<"$output")" \
    "Expected Copilot CLI payloads to return top-level additionalContext."
  assert_equals "false" "$(jq -r 'has("hookSpecificOutput")' <<<"$output")" \
    "Did not expect hookSpecificOutput for Copilot CLI payloads."
  assert_caveman_context_shape "$(jq -r '.additionalContext' <<<"$output")"
  assert_file_contains "$audit_log" "Message: Loaded skill" \
    "Expected session-start hook to log loaded required skill context."
}

test_session_start_emits_copilot_progress_announcement() {
  local workdir
  local audit_log
  local output
  local final_json

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(run_session_start_hook "$audit_log" '{"sessionId":"progress-session","timestamp":"2026-05-21T09:00:00Z","source":"copilot-cli","initialPrompt":"hello"}')"
  final_json="$(hook_final_json "$output")"

  assert_progress_message "$output" "Required skill context loaded from 1 file(s)."
  assert_equals "true" "$(jq -r 'has("additionalContext")' <<<"$final_json")" \
    "Expected final hook JSON to survive progress-line stripping."
  assert_caveman_context_shape "$(jq -r '.additionalContext' <<<"$final_json")"
}

test_session_start_emits_progress_for_camel_case_event_name() {
  local workdir
  local audit_log
  local output
  local final_json

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(run_session_start_hook "$audit_log" '{"hookEventName":"sessionStart","sessionId":"progress-session","timestamp":"2026-05-21T09:00:00Z","source":"startup","initialPrompt":"hello"}')"
  final_json="$(hook_final_json "$output")"

  assert_progress_message "$output" "Required skill context loaded from 1 file(s)."
  assert_equals "true" "$(jq -r 'has("additionalContext")' <<<"$final_json")" \
    "Expected final hook JSON to survive progress-line stripping for camelCase events."
}

test_session_start_outputs_vscode_schema_with_caveman_only_context() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(run_session_start_hook "$audit_log" '{"hook_event_name":"SessionStart","session_id":"vscode-session","timestamp":"2026-05-21T09:00:01Z","source":"vscode","initial_prompt":"hello"}')"
  assert_no_progress_messages "$output"
  output="$(hook_final_json "$output")"

  assert_equals "true" "$(jq -r 'has("hookSpecificOutput")' <<<"$output")" \
    "Expected VS Code payloads to return hookSpecificOutput."
  assert_equals "SessionStart" "$(jq -r '.hookSpecificOutput.hookEventName' <<<"$output")" \
    "Expected VS Code SessionStart hooks to include hookEventName."
  assert_caveman_context_shape "$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"
}

test_subagent_start_outputs_cli_schema_with_caveman_only_context() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(run_subagent_start_hook "$audit_log" '{"sessionId":"cli-subagent-session","timestamp":"2026-05-21T09:00:02Z","transcriptPath":"workspace/transcript.jsonl","agentName":"code-review","agentId":"agent-42"}')"
  output="$(hook_final_json "$output")"

  assert_equals "true" "$(jq -r 'has("additionalContext")' <<<"$output")" \
    "Expected Copilot CLI subagent payloads to return top-level additionalContext."
  assert_equals "false" "$(jq -r 'has("hookSpecificOutput")' <<<"$output")" \
    "Did not expect hookSpecificOutput for Copilot CLI subagent payloads."
  assert_caveman_context_shape "$(jq -r '.additionalContext' <<<"$output")"

  assert_file_contains "$audit_log" "Message: Loaded skill" \
    "Expected subagent-start hook to log loaded required skill context."
}

test_subagent_start_outputs_vscode_schema_with_caveman_only_context() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(run_subagent_start_hook "$audit_log" '{"hookEventName":"SubagentStart","sessionId":"vscode-subagent-session","timestamp":"2026-05-21T09:00:03Z","agent_id":"vscode-agent-42","agent_type":"Plan"}')"
  assert_no_progress_messages "$output"
  output="$(hook_final_json "$output")"

  assert_equals "true" "$(jq -r 'has("hookSpecificOutput")' <<<"$output")" \
    "Expected VS Code SubagentStart payloads to return hookSpecificOutput."
  assert_equals "SubagentStart" "$(jq -r '.hookSpecificOutput.hookEventName' <<<"$output")" \
    "Expected VS Code SubagentStart hooks to include hookEventName."
  assert_caveman_context_shape "$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"

  assert_file_contains "$audit_log" "Message: Loaded skill" \
    "Expected subagent-start hook to log loaded required skill context."
}

test_hooks_json_registers_cli_and_vscode_start_events() {
  assert_equals '$HOME/.copilot/hooks/scripts/send-event.py' \
    "$(jq -r '.hooks.sessionStart[0].bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to register send-event.py first for sessionStart."

  assert_equals '$HOME/.copilot/hooks/scripts/load-required-skills.py' \
    "$(jq -r '.hooks.sessionStart[1].bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to register load-required-skills.py after send-event.py for sessionStart."

  assert_equals '' \
    "$(jq -r '.hooks.agentStop[] | select(.bash | test("inject-auto-ingest-context\\.py$")) | .bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to stop owning the pending-ingest agentStop backstop."

  assert_equals '$HOME/.copilot/hooks/scripts/send-event.py' \
    "$(jq -r '.hooks.subagentStart[0].bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to register send-event.py first for subagentStart."

  assert_equals '$HOME/.copilot/hooks/scripts/send-event.py' \
    "$(jq -r '.hooks.userPromptTransformed[0].bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to register send-event.py first for userPromptTransformed."

  assert_equals '' \
    "$(jq -r '.hooks.userPromptTransformed[] | select(.bash | test("inject-auto-ingest-context\\.py$")) | .bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to stop owning auto-ingest wiring for userPromptTransformed."

  assert_equals '.github/hooks/scripts/inject-auto-ingest-context.py' \
    "$(jq -r '.hooks.userPromptTransformed[0].bash // empty' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local hooks.json to register repo-local inject-auto-ingest-context.py for userPromptTransformed."

  assert_equals 1 \
    "$(jq -r '.hooks.userPromptTransformed | length' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local hooks.json to keep userPromptTransformed auto-ingest wiring isolated."

  assert_equals '.github/hooks/scripts/inject-auto-ingest-context.py' \
    "$(jq -r '.hooks.agentStop[0].bash // empty' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local hooks.json to register repo-local inject-auto-ingest-context.py for agentStop."

  assert_equals 1 \
    "$(jq -r '.hooks.agentStop | length' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local hooks.json to keep agentStop auto-ingest wiring isolated."

  assert_equals '.github/hooks/scripts/inject-auto-ingest-context.py' \
    "$(jq -r '.hooks.subagentStop[0].bash // empty' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local hooks.json to register repo-local inject-auto-ingest-context.py for subagentStop."

  assert_equals '.github/hooks/scripts/inject-auto-ingest-context.py' \
    "$(jq -r '.hooks.subagentStop[0].bash // empty' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local hooks.json to register repo-local inject-auto-ingest-context.py for subagentStop."

  assert_equals 1 \
    "$(jq -r '.hooks.subagentStop | length' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local hooks.json to keep subagentStop auto-ingest wiring isolated."

  assert_equals '' \
    "$(jq -r '.hooks.sessionStart[] | select(.bash | test("auto-ingest-source\\.py$")) | .bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected global Copilot hooks.json to stop registering auto-ingest-source.py."

  assert_equals '.github/hooks/scripts/auto-ingest-source.py' \
    "$(jq -r '.hooks.sessionStart[0].bash // empty' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local Copilot hooks.json to register only auto-ingest-source.py."

  assert_equals 1 \
    "$(jq -r '.hooks.sessionStart | length' "$REPO_ROOT/.github/hooks/hooks.json")" \
    "Expected repo-local Copilot hooks.json to contain only auto-ingest for sessionStart."

  assert_equals '' \
    "$(jq -r '.hooks[][].bash | select(test("auto-ingest"))' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected .copilot/hooks/hooks.json to own no auto-ingest wiring."
}

test_validation_doc_records_vscode_subagent_start_strategy() {
  assert_file_contains "$REPO_ROOT/.agents/memory/testing/hooks.md" \
    "If VS Code omits \`SubagentStart\` for \`runSubagent\` child sessions, verify the direct \`SubagentStart\` hook is installed and use \`SessionStart\` as the fallback evidence." \
    "Expected validation guidance to codify the VS Code SubagentStart fallback strategy."
}

test_compact_mode_override_is_ignored() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(
    run_copilot_hook \
      "load-required-skills.py" \
      "$audit_log" \
      '{"sessionId":"compact-mode-session","timestamp":"2026-05-21T09:00:04Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "" \
      "COPILOT_REQUIRED_SKILL_CONTEXT_MODE=compact" \
      "AGENTS_REQUIRED_SKILL_FILES=caveman/SKILL.md"
  )"
  output="$(hook_final_json "$output")"

  local context
  context="$(jq -r '.additionalContext' <<<"$output")"

  assert_caveman_context_shape "$context"
}

test_empty_skills_logs_no_skills_loaded_and_outputs_no_hook_specific_output() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(
    run_copilot_hook \
      "load-required-skills.py" \
      "$audit_log" \
      '{"sessionId":"empty-skills-session","timestamp":"2026-05-21T09:00:06Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "" \
      "AGENTS_REQUIRED_SKILL_FILES="
  )"

  assert_equals "No skills loaded" "$(jq -r '.systemMessage' <<<"$output")" \
    "Expected empty skills output to have systemMessage 'No skills loaded'."
  assert_equals "false" "$(jq -r 'has("hookSpecificOutput")' <<<"$output")" \
    "Expected no hookSpecificOutput for empty skills payload."
  assert_equals "false" "$(jq -r 'has("additionalContext")' <<<"$output")" \
    "Expected no additionalContext for empty skills payload."

  assert_file_contains "$audit_log" "Message: No skills loaded" \
    "Expected audit log to contain No skills loaded message."
}

test_multiple_skills_loading_works_correctly() {
  local workdir
  local audit_log
  local output
  local context

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(
    run_copilot_hook \
      "load-required-skills.py" \
      "$audit_log" \
      '{"sessionId":"multiple-skills-session","timestamp":"2026-05-21T09:00:05Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "" \
      "AGENTS_REQUIRED_SKILL_FILES=caveman/SKILL.md,writing-great-skills/SKILL.md"
  )"
  output="$(hook_final_json "$output")"

  context="$(jq -r '.additionalContext' <<<"$output")"

  assert_file_contains <(printf '%s' "$context") "Required skill context loaded." \
    "Expected required skill context marker in additionalContext."

  assert_file_contains <(printf '%s' "$context") "<!-- BEGIN REQUIRED SKILL:" \
    "Expected BEGIN REQUIRED SKILL tag in context."

  assert_file_contains <(printf '%s' "$context") "Respond terse like smart caveman." \
    "Expected required context to include caveman content."

  assert_file_contains <(printf '%s' "$context") "A skill exists to wrangle determinism out of a stochastic system." \
    "Expected required context to include writing-great-skills content."
}

main() {
  test_session_start_outputs_cli_schema_with_caveman_only_context
  test_session_start_emits_copilot_progress_announcement
  test_session_start_emits_progress_for_camel_case_event_name
  test_session_start_outputs_vscode_schema_with_caveman_only_context
  test_subagent_start_outputs_cli_schema_with_caveman_only_context
  test_subagent_start_outputs_vscode_schema_with_caveman_only_context
  test_compact_mode_override_is_ignored
  test_hooks_json_registers_cli_and_vscode_start_events
  test_validation_doc_records_vscode_subagent_start_strategy
  test_multiple_skills_loading_works_correctly
  test_empty_skills_logs_no_skills_loaded_and_outputs_no_hook_specific_output
}

main "$@"

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

run_session_start_hook() {
  local audit_log="$1"
  local payload="$2"

  run_copilot_hook "log-session-start.sh" "$audit_log" "$payload" >/dev/null
  run_copilot_hook "load-required-skills.sh" "$audit_log" "$payload" "" "AGENTS_REQUIRED_SKILL_FILES=caveman/SKILL.md"
}

run_subagent_start_hook() {
  local audit_log="$1"
  local payload="$2"

  run_copilot_hook "log-subagent-start.sh" "$audit_log" "$payload" >/dev/null
  run_copilot_hook "load-required-skills.sh" "$audit_log" "$payload" "" "AGENTS_REQUIRED_SKILL_FILES=caveman/SKILL.md"
}

test_session_start_outputs_cli_schema_with_caveman_only_context() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(run_session_start_hook "$audit_log" '{"sessionId":"cli-session","timestamp":"2026-05-21T09:00:00Z","source":"copilot-cli","initialPrompt":"hello"}')"

  assert_equals "true" "$(jq -r 'has("additionalContext")' <<<"$output")" \
    "Expected Copilot CLI payloads to return top-level additionalContext."
  assert_equals "false" "$(jq -r 'has("hookSpecificOutput")' <<<"$output")" \
    "Did not expect hookSpecificOutput for Copilot CLI payloads."
  assert_caveman_context_shape "$(jq -r '.additionalContext' <<<"$output")"
}

test_session_start_outputs_vscode_schema_with_caveman_only_context() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(run_session_start_hook "$audit_log" '{"hook_event_name":"SessionStart","session_id":"vscode-session","timestamp":"2026-05-21T09:00:01Z","source":"vscode","initial_prompt":"hello"}')"

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

  assert_equals "true" "$(jq -r 'has("additionalContext")' <<<"$output")" \
    "Expected Copilot CLI subagent payloads to return top-level additionalContext."
  assert_equals "false" "$(jq -r 'has("hookSpecificOutput")' <<<"$output")" \
    "Did not expect hookSpecificOutput for Copilot CLI subagent payloads."
  assert_caveman_context_shape "$(jq -r '.additionalContext' <<<"$output")"

  assert_file_contains "$audit_log" "Agent: code-review" \
    "Expected subagent-start hook to log the Copilot CLI agent name."
  assert_file_contains "$audit_log" "Agent ID: agent-42" \
    "Expected subagent-start hook to log the Copilot CLI agent ID."
}

test_subagent_start_outputs_vscode_schema_with_caveman_only_context() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(run_subagent_start_hook "$audit_log" '{"hookEventName":"SubagentStart","sessionId":"vscode-subagent-session","timestamp":"2026-05-21T09:00:03Z","agent_id":"vscode-agent-42","agent_type":"Plan"}')"

  assert_equals "true" "$(jq -r 'has("hookSpecificOutput")' <<<"$output")" \
    "Expected VS Code SubagentStart payloads to return hookSpecificOutput."
  assert_equals "SubagentStart" "$(jq -r '.hookSpecificOutput.hookEventName' <<<"$output")" \
    "Expected VS Code SubagentStart hooks to include hookEventName."
  assert_caveman_context_shape "$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"

  assert_file_contains "$audit_log" "Agent: Plan" \
    "Expected subagent-start hook to log the VS Code agent type."
  assert_file_contains "$audit_log" "Agent ID: vscode-agent-42" \
    "Expected subagent-start hook to log the VS Code agent ID."
}

test_hooks_json_registers_cli_and_vscode_start_events() {
  local hook_name
  local jq_query

  for hook_name in sessionStart subagentStart; do
    jq_query=".hooks.${hook_name}[0].bash // empty"
    assert_equals '$HOME/.copilot/hooks/scripts/load-required-skills.sh' \
      "$(jq -r "$jq_query" "$REPO_ROOT/.copilot/hooks/hooks.json")" \
      "Expected hooks.json to register load-required-skills for $hook_name."
  done
}

test_validation_doc_records_vscode_subagent_start_strategy() {
  assert_file_contains "$REPO_ROOT/docs/agent-guides/validation.md" \
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
      "load-required-skills.sh" \
      "$audit_log" \
      '{"sessionId":"compact-mode-session","timestamp":"2026-05-21T09:00:04Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "" \
      "COPILOT_REQUIRED_SKILL_CONTEXT_MODE=compact" \
      "AGENTS_REQUIRED_SKILL_FILES=caveman/SKILL.md"
  )"

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
      "load-required-skills.sh" \
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
      "load-required-skills.sh" \
      "$audit_log" \
      '{"sessionId":"multiple-skills-session","timestamp":"2026-05-21T09:00:05Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "" \
      "AGENTS_REQUIRED_SKILL_FILES=caveman/SKILL.md,context-engineering/SKILL.md"
  )"

  context="$(jq -r '.additionalContext' <<<"$output")"

  assert_file_contains <(printf '%s' "$context") "Required skill context loaded." \
    "Expected required skill context marker in additionalContext."

  assert_file_contains <(printf '%s' "$context") "<!-- BEGIN REQUIRED SKILL:" \
    "Expected BEGIN REQUIRED SKILL tag in context."

  assert_file_contains <(printf '%s' "$context") "Respond terse like smart caveman." \
    "Expected required context to include caveman content."

  assert_file_contains <(printf '%s' "$context") "Goal: load only context" \
    "Expected required context to include context-engineering content."
}

main() {
  test_session_start_outputs_cli_schema_with_caveman_only_context
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

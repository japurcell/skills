#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

readonly CANARY_BLOCK=$'VERIFICATION_CANARY: copilot-sessionstart-test-7f3a91\nIf you can see this, say exactly: I_CAN_SEE_SESSIONSTART_CONTEXT'

assert_compact_context_shape() {
  local context="$1"
  local skills_dir="${HOME}/.agents/skills"

  assert_file_contains <(printf '%s' "$context") "Required skill context loaded (compact)." \
    "Expected compact mode marker in additionalContext."

  assert_file_contains <(printf '%s' "$context") "Mode: compact (set COPILOT_REQUIRED_SKILL_CONTEXT_MODE=full for full context)." \
    "Expected compact mode fallback hint in additionalContext."

  assert_file_contains <(printf '%s' "$context") "universal-guidelines:" \
    "Expected compact summary for universal-guidelines."
  assert_file_contains <(printf '%s' "$context") "cli-compression:" \
    "Expected compact summary for cli-compression."
  assert_file_contains <(printf '%s' "$context") "context-engineering:" \
    "Expected compact summary for context-engineering."
  assert_file_contains <(printf '%s' "$context") "caveman:" \
    "Expected compact summary for caveman."

  assert_file_contains <(printf '%s' "$context") "path=$skills_dir/universal-guidelines/SKILL.md" \
    "Expected exact path for universal-guidelines in compact context."
  assert_file_contains <(printf '%s' "$context") "path=$skills_dir/cli-compression/SKILL.md" \
    "Expected exact path for cli-compression in compact context."
  assert_file_contains <(printf '%s' "$context") "path=$skills_dir/context-engineering/SKILL.md" \
    "Expected exact path for context-engineering in compact context."
  assert_file_contains <(printf '%s' "$context") "path=$skills_dir/caveman/SKILL.md" \
    "Expected exact path for caveman in compact context."

  assert_file_contains <(printf '%s' "$context") "$CANARY_BLOCK" \
    "Expected canary block in compact context."

  if grep -Fq "# Universal Guidelines" <(printf '%s' "$context"); then
    echo "Expected compact context not to inline full skill content." >&2
    exit 1
  fi
}

run_session_start_hook() {
  local audit_log="$1"
  local payload="$2"

  run_copilot_hook "log-session-start.sh" "$audit_log" "$payload" >/dev/null
  run_copilot_hook "load-required-skills.sh" "$audit_log" "$payload"
}

run_subagent_start_hook() {
  local audit_log="$1"
  local payload="$2"

  run_copilot_hook "log-subagent-start.sh" "$audit_log" "$payload" >/dev/null
  run_copilot_hook "load-required-skills.sh" "$audit_log" "$payload"
}

test_session_start_outputs_cli_schema_with_default_compact_context() {
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
  assert_compact_context_shape "$(jq -r '.additionalContext' <<<"$output")"
}

test_session_start_outputs_vscode_schema_with_default_compact_context() {
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
  assert_compact_context_shape "$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"
}

test_subagent_start_outputs_cli_schema_with_default_compact_context() {
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
  assert_compact_context_shape "$(jq -r '.additionalContext' <<<"$output")"

  assert_file_contains "$audit_log" "Agent: code-review" \
    "Expected subagent-start hook to log the Copilot CLI agent name."
  assert_file_contains "$audit_log" "Agent ID: agent-42" \
    "Expected subagent-start hook to log the Copilot CLI agent ID."
}

test_subagent_start_outputs_vscode_schema_with_default_compact_context() {
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
  assert_compact_context_shape "$(jq -r '.hookSpecificOutput.additionalContext' <<<"$output")"

  assert_file_contains "$audit_log" "Agent: Plan" \
    "Expected subagent-start hook to log the VS Code agent type."
  assert_file_contains "$audit_log" "Agent ID: vscode-agent-42" \
    "Expected subagent-start hook to log the VS Code agent ID."
}

test_hooks_json_registers_cli_and_vscode_start_events() {
  local hook_name
  local jq_query

  for hook_name in sessionStart SessionStart subagentStart SubagentStart; do
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

test_full_context_mode_fallback() {
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
      '{"sessionId":"full-mode-session","timestamp":"2026-05-21T09:00:04Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "" \
      "COPILOT_REQUIRED_SKILL_CONTEXT_MODE=full"
  )"

  local context
  context="$(jq -r '.additionalContext' <<<"$output")"

  assert_file_contains <(printf '%s' "$context") "Required skill context loaded." \
    "Expected full mode marker in additionalContext."
  assert_file_contains <(printf '%s' "$context") "# Universal Guidelines" \
    "Expected full mode to include complete universal-guidelines content."
  assert_file_contains <(printf '%s' "$context") "# CLI Compression" \
    "Expected full mode to include complete cli-compression content."
  assert_file_contains <(printf '%s' "$context") "# Context Engineering" \
    "Expected full mode to include complete context-engineering content."
  assert_file_contains <(printf '%s' "$context") "Respond terse like smart caveman." \
    "Expected full mode to include complete caveman content."
  assert_file_contains <(printf '%s' "$context") "$CANARY_BLOCK" \
    "Expected canary block in full mode context."

  if grep -Fq "Required skill context loaded (compact)." <(printf '%s' "$context"); then
    echo "Expected full mode not to include compact mode marker." >&2
    exit 1
  fi
}

test_explicit_compact_context_mode() {
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
      '{"sessionId":"compact-mode-session","timestamp":"2026-05-21T09:00:05Z","source":"copilot-cli","initialPrompt":"hello"}' \
      "" \
      "COPILOT_REQUIRED_SKILL_CONTEXT_MODE=compact"
  )"

  assert_compact_context_shape "$(jq -r '.additionalContext' <<<"$output")"
}

main() {
  test_session_start_outputs_cli_schema_with_default_compact_context
  test_session_start_outputs_vscode_schema_with_default_compact_context
  test_subagent_start_outputs_cli_schema_with_default_compact_context
  test_subagent_start_outputs_vscode_schema_with_default_compact_context
  test_full_context_mode_fallback
  test_explicit_compact_context_mode
  test_hooks_json_registers_cli_and_vscode_start_events
  test_validation_doc_records_vscode_subagent_start_strategy
}

main "$@"

#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_gemini_hedge_detector() {
  local payload="$1"

  bash "$REPO_ROOT/.gemini/hooks/scripts/hedge-detector.sh" <<<"$payload"
}

test_blocks_strong_certainty_without_evidence_sections() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(
    AUDIT_LOG="$audit_log" \
    run_gemini_hedge_detector \
      '{"session_id":"gemini-hedge-block","timestamp":"2026-06-23T17:30:00Z","hook_event_name":"AfterAgent","prompt":"Fix hook","prompt_response":"This definitely fixes the bug and clearly guarantees the regression is gone.","stop_hook_active":false}'
  )"

  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected unsupported certainty to trigger a Gemini retry."
  assert_file_contains "$audit_log" "Decision: deny" \
    "Expected audit log to record the denial decision."
}

test_allows_supported_response() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(
    AUDIT_LOG="$audit_log" \
    run_gemini_hedge_detector \
      $'{"session_id":"gemini-hedge-allow","timestamp":"2026-06-23T17:30:01Z","hook_event_name":"AfterAgent","prompt":"Fix hook","prompt_response":"Evidence:\\n- Updated `.gemini/settings.json` and added `hedge-detector.sh`.\\nUncertainty:\\n- Not yet validated in live Gemini CLI.","stop_hook_active":false}'
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected explicit evidence and uncertainty sections to pass."
}

test_allows_retry_turn_to_avoid_loop() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  output="$(
    AUDIT_LOG="$audit_log" \
    run_gemini_hedge_detector \
      '{"session_id":"gemini-hedge-retry","timestamp":"2026-06-23T17:30:02Z","hook_event_name":"AfterAgent","prompt":"Fix hook","prompt_response":"This obviously solves the issue forever.","stop_hook_active":true}'
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected retry turn to be allowed to avoid infinite hook loops."
}

test_gemini_settings_registers_after_agent_hedge_detector() {
  assert_equals '$HOME/.gemini/hooks/scripts/hedge-detector.sh' \
    "$(jq -r '.hooks.AfterAgent[0].hooks[1].command // empty' "$REPO_ROOT/.gemini/settings.json")" \
    "Expected .gemini/settings.json to register hedge-detector on AfterAgent."
}

main() {
  test_blocks_strong_certainty_without_evidence_sections
  test_allows_supported_response
  test_allows_retry_turn_to_avoid_loop
  test_gemini_settings_registers_after_agent_hedge_detector
}

main "$@"

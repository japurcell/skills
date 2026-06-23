#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_hedge_detector() {
  local audit_log="$1"
  local payload="$2"
  local copilot_home="$3"

  run_copilot_hook "hedge-detector.sh" "$audit_log" "$payload" "$copilot_home"
}

write_transcript() {
  local path="$1"
  local content="$2"
  local turn_id="${3:-0}"

  jq -nc \
    --arg turn_id "$turn_id" \
    --arg content "$content" \
    '{type:"assistant.message",data:{turnId:$turn_id,content:$content}}' >"$path"
}

test_blocks_strong_certainty_without_evidence_sections() {
  local workdir
  local audit_log
  local copilot_home
  local transcript_path
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  copilot_home="$workdir/copilot-home"
  transcript_path="$workdir/transcript.jsonl"

  write_transcript \
    "$transcript_path" \
    "This definitely fixes the bug and clearly guarantees the regression is gone."

  output="$(
    run_hedge_detector \
      "$audit_log" \
      "{\"sessionId\":\"hedge-block\",\"timestamp\":\"2026-06-23T17:00:00Z\",\"transcriptPath\":\"$transcript_path\",\"stopReason\":\"end_turn\"}" \
      "$copilot_home"
  )"

  assert_equals "block" "$(jq -r '.decision' <<<"$output")" \
    "Expected unsupported certainty to trigger a blocking retry."
  assert_file_contains "$audit_log" "Decision: block" \
    "Expected audit log to record the blocking decision."
}

test_allows_revised_response_with_evidence_and_uncertainty_sections() {
  local workdir
  local audit_log
  local copilot_home
  local transcript_path
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  copilot_home="$workdir/copilot-home"
  transcript_path="$workdir/transcript.jsonl"

  write_transcript \
    "$transcript_path" \
    $'Evidence:\n- Updated `.copilot/hooks/hooks.json` and added `hedge-detector.sh`.\nUncertainty:\n- Not yet validated in VS Code.'

  output="$(
    run_hedge_detector \
      "$audit_log" \
      "{\"sessionId\":\"hedge-allow\",\"timestamp\":\"2026-06-23T17:00:01Z\",\"transcriptPath\":\"$transcript_path\",\"stopReason\":\"end_turn\"}" \
      "$copilot_home"
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected explicit evidence and uncertainty sections to pass."
}

test_allows_repeated_identical_reply_after_single_block() {
  local workdir
  local audit_log
  local copilot_home
  local transcript_path
  local first_output
  local second_output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  copilot_home="$workdir/copilot-home"
  transcript_path="$workdir/transcript.jsonl"

  write_transcript \
    "$transcript_path" \
    "This obviously solves the issue forever."

  first_output="$(
    run_hedge_detector \
      "$audit_log" \
      "{\"sessionId\":\"hedge-loop\",\"timestamp\":\"2026-06-23T17:00:02Z\",\"transcriptPath\":\"$transcript_path\",\"stopReason\":\"end_turn\"}" \
      "$copilot_home"
  )"
  second_output="$(
    run_hedge_detector \
      "$audit_log" \
      "{\"sessionId\":\"hedge-loop\",\"timestamp\":\"2026-06-23T17:00:03Z\",\"transcriptPath\":\"$transcript_path\",\"stopReason\":\"end_turn\"}" \
      "$copilot_home"
  )"

  assert_equals "block" "$(jq -r '.decision' <<<"$first_output")" \
    "Expected first unsupported reply to be blocked."
  assert_equals "allow" "$(jq -r '.decision' <<<"$second_output")" \
    "Expected identical reply to be allowed on retry to avoid infinite loops."
}

test_hooks_json_registers_agent_stop_hedge_detector() {
  assert_equals '$HOME/.copilot/hooks/scripts/hedge-detector.sh' \
    "$(jq -r '.hooks.agentStop[1].bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to register hedge-detector on agentStop."
}

main() {
  test_blocks_strong_certainty_without_evidence_sections
  test_allows_revised_response_with_evidence_and_uncertainty_sections
  test_allows_repeated_identical_reply_after_single_block
  test_hooks_json_registers_agent_stop_hedge_detector
}

main "$@"

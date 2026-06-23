#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_pride_check() {
  local audit_log="$1"
  local payload="$2"
  local copilot_home="$3"

  run_copilot_hook "pride-check.sh" "$audit_log" "$payload" "$copilot_home"
}

append_json_line() {
  local path="$1"
  local json="$2"
  printf '%s\n' "$json" >>"$path"
}

write_tool_event() {
  local path="$1"
  local tool_name="$2"
  local turn_id="${3:-0}"

  append_json_line "$path" "$(
    jq -nc \
      --arg tool_name "$tool_name" \
      --arg turn_id "$turn_id" \
      '{type:"tool.execution_start",data:{toolName:$tool_name,turnId:$turn_id}}'
  )"
}

write_assistant_message() {
  local path="$1"
  local content="$2"
  local turn_id="${3:-0}"

  append_json_line "$path" "$(
    jq -nc \
      --arg turn_id "$turn_id" \
      --arg content "$content" \
      '{type:"assistant.message",data:{turnId:$turn_id,content:$content}}'
  )"
}

test_blocks_later_read_only_turn_when_earlier_edit_left_session_dirty() {
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
  : >"$transcript_path"

  write_tool_event "$transcript_path" "apply_patch" "0"
  write_assistant_message "$transcript_path" "Implemented token refresh and added tests." "0"
  write_tool_event "$transcript_path" "view" "1"
  write_assistant_message "$transcript_path" "Explained the earlier auth fix." "1"

  output="$(
  run_pride_check \
    "$audit_log" \
    "{\"sessionId\":\"pride-session-dirty\",\"timestamp\":\"2026-06-23T19:30:00Z\",\"transcriptPath\":\"$transcript_path\",\"stopReason\":\"end_turn\"}" \
    "$copilot_home"
  )"

  assert_equals "block" "$(jq -r '.decision' <<<"$output")" \
  "Expected later read-only turn to stay blocked while earlier edit still lacks Pride Check."
}

test_allows_read_only_turn_after_pride_check_clears_session_dirty_state() {
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
  : >"$transcript_path"

  write_tool_event "$transcript_path" "apply_patch" "0"
  write_assistant_message "$transcript_path" "Implemented token refresh and added tests." "0"
  write_assistant_message "$transcript_path" $'Pride Check:\n- Senior respect: src/auth_session.py now follows existing session helpers and keeps refresh logic local.\n- Self-explaining: should_refresh_token makes expiry intent obvious without extra comments.\n- Edge cases: tests/test_auth_session.py covers missing token, missing expiry, and refresh-window boundary cases.\n- Simplicity: one helper plus straight-line guards is enough; no speculative abstraction was added.\n- Codebase better: added boundary regression tests alongside the fix so future auth changes stay safer.' "1"
  write_tool_event "$transcript_path" "view" "2"
  write_assistant_message "$transcript_path" "Summarized the earlier auth fix." "2"

  output="$(
  run_pride_check \
    "$audit_log" \
    "{\"sessionId\":\"pride-session-cleared\",\"timestamp\":\"2026-06-23T19:30:01Z\",\"transcriptPath\":\"$transcript_path\",\"stopReason\":\"end_turn\"}" \
    "$copilot_home"
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
  "Expected later read-only turn to pass once a valid Pride Check cleared the session."
}

test_blocks_changed_turn_without_pride_check() {
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
  : >"$transcript_path"

  write_tool_event "$transcript_path" "apply_patch"
  write_assistant_message "$transcript_path" "Implemented token refresh and added tests."

  output="$(
    run_pride_check \
      "$audit_log" \
      "{\"sessionId\":\"pride-block\",\"timestamp\":\"2026-06-23T19:30:00Z\",\"transcriptPath\":\"$transcript_path\",\"stopReason\":\"end_turn\"}" \
      "$copilot_home"
  )"

  assert_equals "block" "$(jq -r '.decision' <<<"$output")" \
    "Expected changed turn without Pride Check section to be blocked."
  assert_file_contains "$audit_log" "Decision: block" \
    "Expected audit log to record the Pride Check block."
  assert_file_contains "$audit_log" "Turn: 0" \
    "Expected audit log to record the blocked turn id."
}

test_allows_changed_turn_with_full_pride_check_template() {
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
  : >"$transcript_path"

  write_tool_event "$transcript_path" "apply_patch"
  write_assistant_message "$transcript_path" $'Pride Check:\n- Senior respect: src/auth_session.py now follows existing session helpers and keeps refresh logic local.\n- Self-explaining: should_refresh_token makes expiry intent obvious without extra comments.\n- Edge cases: tests/test_auth_session.py covers missing token, missing expiry, and refresh-window boundary cases.\n- Simplicity: one helper plus straight-line guards is enough; no speculative abstraction was added.\n- Codebase better: added boundary regression tests alongside the fix so future auth changes stay safer.'

  output="$(
    run_pride_check \
      "$audit_log" \
      "{\"sessionId\":\"pride-allow\",\"timestamp\":\"2026-06-23T19:30:01Z\",\"transcriptPath\":\"$transcript_path\",\"stopReason\":\"end_turn\"}" \
      "$copilot_home"
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected full Pride Check section to pass."
}

test_allows_read_only_turn_without_pride_check() {
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
  : >"$transcript_path"

  write_tool_event "$transcript_path" "view"
  write_assistant_message "$transcript_path" "Found the root cause in src/auth_session.py."

  output="$(
    run_pride_check \
      "$audit_log" \
      "{\"sessionId\":\"pride-readonly\",\"timestamp\":\"2026-06-23T19:30:02Z\",\"transcriptPath\":\"$transcript_path\",\"stopReason\":\"end_turn\"}" \
      "$copilot_home"
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected read-only turn to bypass Pride Check."
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
  : >"$transcript_path"

  write_tool_event "$transcript_path" "apply_patch"
  write_assistant_message "$transcript_path" "Refactored the builder and updated tests."

  first_output="$(
    run_pride_check \
      "$audit_log" \
      "{\"sessionId\":\"pride-loop\",\"timestamp\":\"2026-06-23T19:30:03Z\",\"transcriptPath\":\"$transcript_path\",\"stopReason\":\"end_turn\"}" \
      "$copilot_home"
  )"
  second_output="$(
    run_pride_check \
      "$audit_log" \
      "{\"sessionId\":\"pride-loop\",\"timestamp\":\"2026-06-23T19:30:04Z\",\"transcriptPath\":\"$transcript_path\",\"stopReason\":\"end_turn\"}" \
      "$copilot_home"
  )"

  assert_equals "block" "$(jq -r '.decision' <<<"$first_output")" \
    "Expected first changed reply without Pride Check to be blocked."
  assert_equals "allow" "$(jq -r '.decision' <<<"$second_output")" \
    "Expected repeat reply to be allowed so the hook cannot loop forever."
}

test_hooks_json_registers_agent_stop_pride_check() {
  assert_equals '$HOME/.copilot/hooks/scripts/pride-check.sh' \
    "$(jq -r '.hooks.agentStop[2].bash // empty' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected hooks.json to register pride-check on agentStop."
}

main() {
  test_blocks_changed_turn_without_pride_check
  test_allows_changed_turn_with_full_pride_check_template
  test_allows_read_only_turn_without_pride_check
  test_blocks_later_read_only_turn_when_earlier_edit_left_session_dirty
  test_allows_read_only_turn_after_pride_check_clears_session_dirty_state
  test_allows_repeated_identical_reply_after_single_block
  test_hooks_json_registers_agent_stop_pride_check
}

main "$@"

#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_gemini_pride_check() {
  local audit_log="$1"
  local payload="$2"

  AUDIT_LOG="$audit_log" \
    bash "$REPO_ROOT/.gemini/hooks/scripts/pride-check.sh" <<<"$payload"
}

write_transcript() {
  local path="$1"
  local tool_name="$2"
  local final_response="$3"

  jq -nc \
    --arg tool_name "$tool_name" \
    --arg final_response "$final_response" '
      {
        sessionId: "session-1",
        projectHash: "project-1",
        startTime: "2026-06-23T19:00:00Z",
        lastUpdated: "2026-06-23T19:00:00Z",
        messages: [
          {
            id: "u1",
            timestamp: "2026-06-23T19:00:00Z",
            type: "user",
            content: [{text: "Fix hook"}]
          },
          {
            id: "g1",
            timestamp: "2026-06-23T19:00:01Z",
            type: "gemini",
            content: [{text: "Working through files."}],
            toolCalls: (
              if $tool_name == "" then
                []
              else
                [{
                  id: "tool-1",
                  name: $tool_name,
                  args: {file_path: "src/auth_session.py"},
                  status: "success",
                  timestamp: "2026-06-23T19:00:01Z"
                }]
              end
            )
          },
          {
            id: "g2",
            timestamp: "2026-06-23T19:00:02Z",
            type: "gemini",
            content: [{text: $final_response}]
          }
        ]
      }
    ' >"$path"
}

write_session_dirty_transcript() {
  local path="$1"
  local cleared_response="$2"
  local final_response="$3"

  jq -nc \
    --arg cleared_response "$cleared_response" \
    --arg final_response "$final_response" '
      {
        sessionId: "session-1",
        projectHash: "project-1",
        startTime: "2026-06-23T19:00:00Z",
        lastUpdated: "2026-06-23T19:00:00Z",
        messages: [
          {
            id: "u1",
            timestamp: "2026-06-23T19:00:00Z",
            type: "user",
            content: [{text: "Fix hook"}]
          },
          {
            id: "g1",
            timestamp: "2026-06-23T19:00:01Z",
            type: "gemini",
            content: [{text: "Implemented token refresh and added tests."}],
            toolCalls: [{
              id: "tool-1",
              name: "replace",
              args: {file_path: "src/auth_session.py"},
              status: "success",
              timestamp: "2026-06-23T19:00:01Z"
            }]
          }
        ] + (
          if $cleared_response == "" then
            []
          else
            [{
              id: "g2",
              timestamp: "2026-06-23T19:00:02Z",
              type: "gemini",
              content: [{text: $cleared_response}]
            }]
          end
        ) + [
          {
            id: "g3",
            timestamp: "2026-06-23T19:00:03Z",
            type: "gemini",
            content: [{text: $final_response}],
            toolCalls: []
          }
        ]
      }
    ' >"$path"
}

test_blocks_changed_turn_without_pride_check() {
  local workdir
  local audit_log
  local transcript_path
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  transcript_path="$workdir/session.json"

  write_transcript "$transcript_path" "replace" "Implemented token refresh and added tests."

  output="$(
    run_gemini_pride_check \
      "$audit_log" \
      "{\"session_id\":\"gemini-pride-block\",\"timestamp\":\"2026-06-23T19:30:00Z\",\"hook_event_name\":\"AfterAgent\",\"prompt\":\"Fix hook\",\"prompt_response\":\"Implemented token refresh and added tests.\",\"transcript_path\":\"$transcript_path\",\"stop_hook_active\":false}"
  )"

  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected changed turn without Pride Check section to trigger a Gemini retry."
  assert_file_contains "$audit_log" "Decision: deny" \
    "Expected audit log to record the Pride Check denial."
}

test_allows_changed_turn_with_full_pride_check_template() {
  local workdir
  local audit_log
  local transcript_path
  local response
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  transcript_path="$workdir/session.json"
  response=$'Pride Check:\n- Senior respect: src/auth_session.py now keeps refresh logic local and follows existing helpers.\n- Self-explaining: should_refresh_token makes expiry intent obvious without extra comments.\n- Edge cases: tests/test_auth_session.py covers missing token, missing expiry, and refresh-window boundaries.\n- Simplicity: one helper plus straight-line guards solves this without speculative abstraction.\n- Codebase better: added regression coverage alongside the fix so future auth changes stay safer.'

  write_transcript "$transcript_path" "write_file" "$response"

  output="$(
    run_gemini_pride_check \
      "$audit_log" \
      "$(jq -nc \
        --arg transcript_path "$transcript_path" \
        --arg response "$response" \
        '{
          session_id: "gemini-pride-allow",
          timestamp: "2026-06-23T19:30:01Z",
          hook_event_name: "AfterAgent",
          prompt: "Fix hook",
          prompt_response: $response,
          transcript_path: $transcript_path,
          stop_hook_active: false
        }'
      )"
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected full Pride Check section to pass."
}

test_allows_read_only_turn_without_pride_check() {
  local workdir
  local audit_log
  local transcript_path
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  transcript_path="$workdir/session.json"

  write_transcript "$transcript_path" "read_file" "Found root cause in src/auth_session.py."

  output="$(
    run_gemini_pride_check \
      "$audit_log" \
      "{\"session_id\":\"gemini-pride-readonly\",\"timestamp\":\"2026-06-23T19:30:02Z\",\"hook_event_name\":\"AfterAgent\",\"prompt\":\"Fix hook\",\"prompt_response\":\"Found root cause in src/auth_session.py.\",\"transcript_path\":\"$transcript_path\",\"stop_hook_active\":false}"
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected read-only turn to bypass Pride Check."
}

test_blocks_later_read_only_turn_when_earlier_edit_left_session_dirty() {
  local workdir
  local audit_log
  local transcript_path
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  transcript_path="$workdir/session.json"

  write_session_dirty_transcript "$transcript_path" "" "Explained the earlier auth fix."

  output="$(
    run_gemini_pride_check \
      "$audit_log" \
      "{\"session_id\":\"gemini-pride-session-dirty\",\"timestamp\":\"2026-06-23T19:30:02Z\",\"hook_event_name\":\"AfterAgent\",\"prompt\":\"Fix hook\",\"prompt_response\":\"Explained the earlier auth fix.\",\"transcript_path\":\"$transcript_path\",\"stop_hook_active\":false}"
  )"

  assert_equals "deny" "$(jq -r '.decision' <<<"$output")" \
    "Expected later read-only Gemini turn to stay blocked while earlier edit still lacks Pride Check."
}

test_allows_read_only_turn_after_pride_check_clears_session_dirty_state() {
  local workdir
  local audit_log
  local transcript_path
  local cleared_response
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  transcript_path="$workdir/session.json"
  cleared_response=$'Pride Check:\n- Senior respect: src/auth_session.py now keeps refresh logic local and follows existing helpers.\n- Self-explaining: should_refresh_token makes expiry intent obvious without extra comments.\n- Edge cases: tests/test_auth_session.py covers missing token, missing expiry, and refresh-window boundaries.\n- Simplicity: one helper plus straight-line guards solves this without speculative abstraction.\n- Codebase better: added regression coverage alongside the fix so future auth changes stay safer.'

  write_session_dirty_transcript "$transcript_path" "$cleared_response" "Summarized the earlier auth fix."

  output="$(
    run_gemini_pride_check \
      "$audit_log" \
      "{\"session_id\":\"gemini-pride-session-cleared\",\"timestamp\":\"2026-06-23T19:30:03Z\",\"hook_event_name\":\"AfterAgent\",\"prompt\":\"Fix hook\",\"prompt_response\":\"Summarized the earlier auth fix.\",\"transcript_path\":\"$transcript_path\",\"stop_hook_active\":false}"
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected later read-only Gemini turn to pass once a valid Pride Check cleared the session."
}

test_allows_retry_turn_to_avoid_loop() {
  local workdir
  local audit_log
  local transcript_path
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  transcript_path="$workdir/session.json"

  write_transcript "$transcript_path" "replace" "Refactored the builder and updated tests."

  output="$(
    run_gemini_pride_check \
      "$audit_log" \
      "{\"session_id\":\"gemini-pride-retry\",\"timestamp\":\"2026-06-23T19:30:03Z\",\"hook_event_name\":\"AfterAgent\",\"prompt\":\"Fix hook\",\"prompt_response\":\"Refactored the builder and updated tests.\",\"transcript_path\":\"$transcript_path\",\"stop_hook_active\":true}"
  )"

  assert_equals "allow" "$(jq -r '.decision' <<<"$output")" \
    "Expected retry turn to be allowed to avoid infinite hook loops."
}

test_gemini_settings_registers_after_agent_pride_check() {
  assert_equals '$HOME/.gemini/hooks/scripts/pride-check.sh' \
    "$(jq -r '.hooks.AfterAgent[0].hooks[2].command // empty' "$REPO_ROOT/.gemini/settings.json")" \
    "Expected .gemini/settings.json to register pride-check on AfterAgent."
}

main() {
  test_blocks_changed_turn_without_pride_check
  test_allows_changed_turn_with_full_pride_check_template
  test_allows_read_only_turn_without_pride_check
  test_blocks_later_read_only_turn_when_earlier_edit_left_session_dirty
  test_allows_read_only_turn_after_pride_check_clears_session_dirty_state
  test_allows_retry_turn_to_avoid_loop
  test_gemini_settings_registers_after_agent_pride_check
}

main "$@"

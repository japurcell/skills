#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

install_into_temp_home() {
  local home="$1"

  mkdir -p "$home"
  TMPDIR="$REPO_ROOT/.tmp" HOME="$home" "$REPO_ROOT/scripts/install.sh" >/dev/null
}

run_installed_gemini_hook() {
  local home="$1"
  local hook_name="$2"
  local payload="$3"
  shift 3

  env HOME="$home" AUDIT_LOG="$home/audit.log" "$@" python3 "$home/.gemini/hooks/scripts/$hook_name" <<<"$payload"
}

assert_hook_registered_with_observability_emitter() {
  local hook_name="$1"
  local source_event_name="$2"

  assert_equals '$HOME/.gemini/hooks/scripts/send-event.py' \
    "$(jq -r ".hooks.${hook_name}[0].hooks[0].command // empty" "$REPO_ROOT/.gemini/settings.json")" \
    "Expected $hook_name to start with send-event.py."
  assert_equals true \
    "$(jq -r ".hooks.${hook_name}[0].hooks[0].env.OBSERVABILITY_CAPTURE_EVENT == \"true\"" "$REPO_ROOT/.gemini/settings.json")" \
    "Expected $hook_name to capture observability input."
  assert_equals "$source_event_name" \
    "$(jq -r ".hooks.${hook_name}[0].hooks[0].env.OBSERVABILITY_SOURCE_EVENT_NAME" "$REPO_ROOT/.gemini/settings.json")" \
    "Expected $hook_name to preserve its source event name."
}

test_settings_json_registers_observability_emitters() {
  local hook_name
  local source_event_name

  for hook_name in SessionStart AfterAgent BeforeTool Notification SessionEnd; do
    source_event_name="$hook_name"
    assert_hook_registered_with_observability_emitter "$hook_name" "$source_event_name"
  done
}

test_structured_observability_records_session_rollup_and_mutation() {
  local workdir
  local home
  local obs_log
  local payload
  local long_tail
  local token_tail
  local token_value
  local output
  local records

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  obs_log="$home/.gemini/hooks/logs/observability.ndjson"
  long_tail="$(python3 - <<'PY'
print("x" * 2000, end="")
PY
)"
  token_tail="$(printf '%s%s%s%s' '1234567890AB' 'CDEF12345678' '90ABCDEF' '3456')"
  token_value="$(printf 'ghp_%s' "$token_tail")"
  payload="$(jq -nc --arg tail "$long_tail" --arg token "$token_value" '{
    session_id: "obs-session",
    timestamp: "2026-06-24T10:00:00Z",
    hook_event_name: "SessionEnd",
    reason: "done",
    message: ($token + " " + $tail)
  }')"

  output="$(
    env HOME="$home" GEMINI_OBSERVABILITY_CAPTURE_EVENT=true GEMINI_OBSERVABILITY_SOURCE_EVENT_NAME=SessionEnd \
      python3 "$home/.gemini/hooks/scripts/send-event.py" <<<"$payload"
  )"

  assert_equals '{}' "$(jq -c . <<<"$output")" \
    "Expected send-event to stay output-neutral."

  run_installed_gemini_hook \
    "$home" \
    "skill-context-injector.py" \
    '{"session_id":"mutate-session","timestamp":"2026-06-24T10:00:01Z","hook_event_name":"SessionStart","cwd":"/repo"}' \
    "AGENTS_REQUIRED_SKILL_FILES=caveman/SKILL.md" \
    >/dev/null

  assert_file_contains "$obs_log" '"record_type":"event_capture"' \
    "Expected event_capture records in the observability log."
  assert_file_contains "$obs_log" '"record_type":"hook_execution"' \
    "Expected hook_execution records in the observability log."
  assert_file_contains "$obs_log" '"record_type":"rollup"' \
    "Expected rollup records in the observability log."

  records="$(jq -s '.' "$obs_log")"

  assert_equals "SessionEnd" \
    "$(jq -r '.[] | select(.record_type=="event_capture") | .source_event_name' <<<"$records" | head -n 1)" \
    "Expected the emitted event capture to preserve the original source event name."
  assert_equals "session_end" \
    "$(jq -r '.[] | select(.record_type=="rollup") | .event_name' <<<"$records" | head -n 1)" \
    "Expected the session rollup to use the canonical session_end event name."
  assert_equals "obs-session" \
    "$(jq -r '.[] | select(.record_type=="rollup") | .session_id' <<<"$records" | head -n 1)" \
    "Expected the rollup to keep the session identifier."
  assert_file_contains <(jq -r '.[] | select(.record_type=="hook_execution" and .event_name=="session_start") | .effective_payload.hookSpecificOutput.additionalContext' <<<"$records") \
    "Respond terse like smart caveman." \
    "Expected the startup hook execution record to keep the generated context."
  assert_equals "ghp_...3456" \
    "$(jq -r '.[] | select(.record_type=="hook_execution" and .event_name=="session_end") | .raw_payload.message' <<<"$records" | head -n 1 | cut -d' ' -f1)" \
    "Expected sensitive token values to be redacted in structured payloads."
  if [[ "$(jq -r '.[] | select(.record_type=="hook_execution" and .event_name=="session_end") | .raw_payload.message | length' <<<"$records" | head -n 1)" -gt 1024 ]]; then
    echo "Expected structured payload strings to be size-capped." >&2
    exit 1
  fi
}

test_observability_lock_wait_and_disable_are_fail_open() {
  local workdir
  local home
  local obs_log
  local locker_pid
  local before_count
  local after_count
  local start_ns
  local end_ns
  local elapsed_ms
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  obs_log="$home/.gemini/hooks/logs/observability.ndjson"
  mkdir -p "$(dirname "$obs_log")"

  before_count="$(if [[ -f "$obs_log" ]]; then jq -s 'length' "$obs_log"; else echo 0; fi)"

  python3 - "$obs_log.lock" <<'PY' &
import fcntl
import sys
import time

lock_path = sys.argv[1]
with open(lock_path, "a+", encoding="utf-8") as handle:
    fcntl.flock(handle, fcntl.LOCK_EX)
    time.sleep(2)
PY
  locker_pid=$!

  start_ns="$(date +%s%N)"
  output="$(
    env HOME="$home" GEMINI_OBSERVABILITY_CAPTURE_EVENT=true GEMINI_OBSERVABILITY_SOURCE_EVENT_NAME=SessionEnd GEMINI_OBSERVABILITY_LOCK_WAIT_MS=10 \
      python3 "$home/.gemini/hooks/scripts/send-event.py" <<<'{"session_id":"lock-wait","timestamp":"2026-06-24T10:00:02Z","hook_event_name":"SessionEnd"}'
  )"
  end_ns="$(date +%s%N)"
  elapsed_ms="$(( (end_ns - start_ns) / 1000000 ))"

  wait "$locker_pid"

  assert_equals '{}' "$(jq -c . <<<"$output")" \
    "Expected lock contention to keep send-event output neutral."
  if [[ "$elapsed_ms" -gt 1500 ]]; then
    echo "Expected observability writes to fail open after a short lock wait." >&2
    echo "Elapsed ms: $elapsed_ms" >&2
    exit 1
  fi

  after_count="$(if [[ -f "$obs_log" ]]; then jq -s 'length' "$obs_log"; else echo 0; fi)"
  assert_equals "$before_count" "$after_count" \
    "Expected a locked observability write to drop instead of blocking control flow."

  output="$(
    env HOME="$home" GEMINI_OBSERVABILITY_DISABLE=true GEMINI_OBSERVABILITY_CAPTURE_EVENT=true GEMINI_OBSERVABILITY_SOURCE_EVENT_NAME=SessionEnd \
      python3 "$home/.gemini/hooks/scripts/send-event.py" <<<'{"session_id":"kill-switch","timestamp":"2026-06-24T10:00:03Z","hook_event_name":"SessionEnd"}'
  )"

  assert_equals '{}' "$(jq -c . <<<"$output")" \
    "Expected the observability kill-switch to leave hook output unchanged."

  after_count="$(if [[ -f "$obs_log" ]]; then jq -s 'length' "$obs_log"; else echo 0; fi)"
  assert_equals "$before_count" "$after_count" \
    "Expected the observability kill-switch to suppress structured records."
}

main() {
  test_settings_json_registers_observability_emitters
  test_structured_observability_records_session_rollup_and_mutation
  test_observability_lock_wait_and_disable_are_fail_open
}

main "$@"

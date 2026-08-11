#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

install_into_temp_home() {
  local home="$1"

  mkdir -p "$home"
  HOME="$home" "$REPO_ROOT/scripts/install.sh" >/dev/null
}

run_installed_copilot_hook() {
  local home="$1"
  local hook_name="$2"
  local payload="$3"
  shift 3

  env HOME="$home" AUDIT_LOG="$home/audit.log" "$@" python3 "$home/.copilot/hooks/scripts/$hook_name" <<<"$payload"
}

assert_hook_registered_with_observability_emitter() {
  local event_name="$1"
  local source_event_name="$2"

  assert_equals '$HOME/.copilot/hooks/scripts/send-event.py' \
    "$(jq -r ".hooks.${event_name}[0].bash" "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected $event_name to start with send-event.py."
  assert_equals true \
    "$(jq -r ".hooks.${event_name}[0].env.OBSERVABILITY_CAPTURE_EVENT == \"true\"" "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected $event_name to capture observability input."
  assert_equals "$source_event_name" \
    "$(jq -r ".hooks.${event_name}[0].env.OBSERVABILITY_SOURCE_EVENT_NAME" "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected $event_name to preserve its source event name."
}

test_hooks_json_registers_observability_emitters() {
  local event_name
  local source_event_name

  for event_name in sessionStart subagentStart preToolUse agentStop errorOccurred notification postToolUseFailure subagentStop sessionEnd; do
    source_event_name="$event_name"
    assert_hook_registered_with_observability_emitter "$event_name" "$source_event_name"
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
  trap 'rm -rf "$workdir"' RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  obs_log="$home/.copilot/hooks/logs/observability.ndjson"
  long_tail="$(python3 - <<'PY'
print("x" * 2000, end="")
PY
)"
  token_tail="$(printf '%s%s%s%s' '1234567890AB' 'CDEF12345678' '90ABCDEF' '3456')"
  token_value="$(printf 'ghp_%s' "$token_tail")"
  payload="$(jq -nc --arg tail "$long_tail" --arg token "$token_value" '{
    sessionId: "obs-session",
    timestamp: "2026-06-23T23:50:00Z",
    reason: "done",
    message: ($token + " " + $tail)
  }')"

  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionEnd \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload"
  )"

  assert_equals '{}' "$(jq -c . <<<"$output")" \
    "Expected send-event to stay output-neutral."

  run_installed_copilot_hook \
    "$home" \
    "load-required-skills.py" \
    '{"sessionId":"mutate-session","timestamp":"2026-06-23T23:50:01Z","source":"copilot-cli","initialPrompt":"hello"}' \
    "AGENTS_REQUIRED_SKILL_FILES=caveman/SKILL.md" >/dev/null

  assert_file_contains "$obs_log" '"record_type":"event_capture"' \
    "Expected event_capture records in the observability log."
  assert_file_contains "$obs_log" '"record_type":"hook_execution"' \
    "Expected hook_execution records in the observability log."
  assert_file_contains "$obs_log" '"record_type":"rollup"' \
    "Expected rollup records in the observability log."

  records="$(jq -s '.' "$obs_log")"

  assert_equals "sessionEnd" \
    "$(jq -r '.[] | select(.record_type=="event_capture") | .source_event_name' <<<"$records" | head -n 1)" \
    "Expected the emitted event capture to preserve the original source event name."
  assert_equals "session_end" \
    "$(jq -r '.[] | select(.record_type=="rollup") | .event_name' <<<"$records" | head -n 1)" \
    "Expected the session rollup to use the canonical session_end event name."
  assert_equals "obs-session" \
    "$(jq -r '.[] | select(.record_type=="rollup") | .session_id' <<<"$records" | head -n 1)" \
    "Expected the rollup to keep the session identifier."
  assert_file_contains <(jq -r '.[] | select(.record_type=="hook_execution" and .event_name=="session_start") | .effective_payload.additionalContext' <<<"$records") \
    "Required skill context loaded." \
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
  obs_log="$home/.copilot/hooks/logs/observability.ndjson"
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
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionEnd COPILOT_OBSERVABILITY_LOCK_WAIT_MS=10 \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<'{"sessionId":"lock-wait","timestamp":"2026-06-23T23:51:00Z"}'
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
    env HOME="$home" COPILOT_OBSERVABILITY_DISABLE=true OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionEnd \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<'{"sessionId":"kill-switch","timestamp":"2026-06-23T23:52:00Z"}'
  )"

  assert_equals '{}' "$(jq -c . <<<"$output")" \
    "Expected the observability kill-switch to leave hook output unchanged."

  after_count="$(if [[ -f "$obs_log" ]]; then jq -s 'length' "$obs_log"; else echo 0; fi)"
  assert_equals "$before_count" "$after_count" \
    "Expected the observability kill-switch to suppress structured records."
}


test_observability_log_rotation() {
  local workdir
  local home
  local obs_log
  local payload
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  
  if [[ "$0" == *"gemini"* ]]; then
    obs_log="$home/.gemini/hooks/logs/observability.ndjson"
    prefix="GEMINI"
    event_name="SessionEnd"
    runner_path="$home/.gemini/hooks/scripts/send-event.py"
    payload="$(jq -nc '{ session_id: "rot-session", timestamp: "2026-06-24T10:00:00Z", hook_event_name: "SessionEnd", reason: "test-rotate", payload_stuff: ("a" * 150) }')"
  else
    obs_log="$home/.copilot/hooks/logs/observability.ndjson"
    prefix="COPILOT"
    event_name="sessionEnd"
    runner_path="$home/.copilot/hooks/scripts/send-event.py"
    payload="$(jq -nc '{ sessionId: "rot-session", timestamp: "2026-06-23T23:50:00Z", reason: "test-rotate", payload_stuff: ("a" * 150) }')"
  fi

  for i in {1..5}; do
    output="$(
      env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=$event_name \
        OBSERVABILITY_LOG_MAX_BYTES=300 \
        OBSERVABILITY_LOG_BACKUP_COUNT=2 \
        python3 "$runner_path" <<<"$payload"
    )"
    assert_equals '{}' "$(jq -c . <<<"$output")" \
      "Expected send-event to stay output-neutral."
  done

  # Assertions
  if [[ ! -f "$obs_log" ]]; then
    echo "Expected active log file to exist: $obs_log" >&2
    exit 1
  fi
  jq '.' "$obs_log" >/dev/null || { echo "Active log contains invalid JSON" >&2; exit 1; }

  if [[ ! -f "$obs_log.1" ]]; then
    echo "Expected log backup .1 to exist" >&2
    exit 1
  fi
  jq '.' "$obs_log.1" >/dev/null || { echo "Log backup .1 contains invalid JSON" >&2; exit 1; }

  if [[ ! -f "$obs_log.2" ]]; then
    echo "Expected log backup .2 to exist" >&2
    exit 1
  fi
  jq '.' "$obs_log.2" >/dev/null || { echo "Log backup .2 contains invalid JSON" >&2; exit 1; }

  if [[ -f "$obs_log.3" ]]; then
    echo "Expected log backup .3 to NOT exist" >&2
    exit 1
  fi
}

test_observability_log_rotation_pruning_and_precedence() {
  local workdir
  local home
  local obs_log
  local payload
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  
  if [[ "$0" == *"gemini"* ]]; then
    obs_log="$home/.gemini/hooks/logs/observability.ndjson"
    prefix="GEMINI"
    event_name="SessionEnd"
    runner_path="$home/.gemini/hooks/scripts/send-event.py"
    payload="$(jq -nc '{ session_id: "prune-session", timestamp: "2026-06-24T10:00:00Z", hook_event_name: "SessionEnd", payload_stuff: ("a" * 600) }')"
  else
    obs_log="$home/.copilot/hooks/logs/observability.ndjson"
    prefix="COPILOT"
    event_name="sessionEnd"
    runner_path="$home/.copilot/hooks/scripts/send-event.py"
    payload="$(jq -nc '{ sessionId: "prune-session", timestamp: "2026-06-23T23:50:00Z", payload_stuff: ("a" * 600) }')"
  fi

  # First run: force 3 backups using precedence variable
  for i in {1..5}; do
    output="$(
      env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=$event_name \
        OBSERVABILITY_LOG_MAX_BYTES=999999999 \
        OBSERVABILITY_LOG_BACKUP_COUNT=999 \
        ${prefix}_OBSERVABILITY_LOG_MAX_BYTES=300 \
        ${prefix}_OBSERVABILITY_LOG_BACKUP_COUNT=3 \
        python3 "$runner_path" <<<"$payload"
    )"
  done

  if [[ ! -f "$obs_log.3" ]]; then
    echo "Expected log backup .3 to exist, precedence failed" >&2
    exit 1
  fi
  if [[ -f "$obs_log.4" ]]; then
    echo "Expected log backup .4 to NOT exist, precedence failed" >&2
    exit 1
  fi

  # Second run: lower backup count to 1, causing pruning of .2 and .3
  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=$event_name \
      ${prefix}_OBSERVABILITY_LOG_MAX_BYTES=300 \
      ${prefix}_OBSERVABILITY_LOG_BACKUP_COUNT=1 \
      python3 "$runner_path" <<<"$payload"
  )"
  
  if [[ ! -f "$obs_log.1" ]]; then
    echo "Expected log backup .1 to exist after pruning" >&2
    exit 1
  fi
  if [[ -f "$obs_log.2" ]]; then
    echo "Expected log backup .2 to NOT exist after pruning" >&2
    exit 1
  fi
  if [[ -f "$obs_log.3" ]]; then
    echo "Expected log backup .3 to NOT exist after pruning" >&2
    exit 1
  fi

  # Third run: lower backup count to 0, which should delete active log (which gets recreated immediately) and .1
  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=$event_name \
      ${prefix}_OBSERVABILITY_LOG_MAX_BYTES=300 \
      ${prefix}_OBSERVABILITY_LOG_BACKUP_COUNT=0 \
      python3 "$runner_path" <<<"$payload"
  )"

  if [[ ! -f "$obs_log" ]]; then
    echo "Expected active log to be recreated on next write after 0 backup count pruning" >&2
    exit 1
  fi
  if [[ -f "$obs_log.1" ]]; then
    echo "Expected log backup .1 to be pruned on 0 backup count" >&2
    exit 1
  fi
}
test_observability_log_rotation_unconditional_prune() {
  local workdir
  local home
  local obs_log
  local payload
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  
  if [[ "$0" == *"gemini"* ]]; then
    obs_log="$home/.gemini/hooks/logs/observability.ndjson"
    prefix="GEMINI"
    event_name="SessionEnd"
    runner_path="$home/.gemini/hooks/scripts/send-event.py"
    payload="$(jq -nc '{ session_id: "prune-session", timestamp: "2026-06-24T10:00:00Z", hook_event_name: "SessionEnd", payload_stuff: ("a" * 150) }')"
  else
    obs_log="$home/.copilot/hooks/logs/observability.ndjson"
    prefix="COPILOT"
    event_name="sessionEnd"
    runner_path="$home/.copilot/hooks/scripts/send-event.py"
    payload="$(jq -nc '{ sessionId: "prune-session", timestamp: "2026-06-23T23:50:00Z", payload_stuff: ("a" * 150) }')"
  fi

  # Create fake backups manually to simulate a historically busy log
  mkdir -p "$(dirname "$obs_log")"
  echo "{}" > "$obs_log.1"
  echo "{}" > "$obs_log.2"
  echo "{}" > "$obs_log.3"

  # Run the hook with a HUGE max_bytes so active log does not trigger rotation,
  # but with a backup limit of 1.
  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=$event_name \
      ${prefix}_OBSERVABILITY_LOG_MAX_BYTES=999999999 \
      ${prefix}_OBSERVABILITY_LOG_BACKUP_COUNT=1 \
      python3 "$runner_path" <<<"$payload"
  )"

  # Assert that .2 and .3 were pruned unconditionally, while .1 survived
  if [[ ! -f "$obs_log.1" ]]; then
    echo "Expected log backup .1 to survive unconditional prune" >&2
    exit 1
  fi
  if [[ -f "$obs_log.2" ]]; then
    echo "Expected log backup .2 to NOT exist after unconditional prune" >&2
    exit 1
  fi
  if [[ -f "$obs_log.3" ]]; then
    echo "Expected log backup .3 to NOT exist after unconditional prune" >&2
    exit 1
  fi
}
test_observability_log_rotation_sub_512() {
  local workdir
  local home
  local obs_log
  local payload
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  
  if [[ "$0" == *"gemini"* ]]; then
    obs_log="$home/.gemini/hooks/logs/observability.ndjson"
    prefix="GEMINI"
    event_name="SessionEnd"
    runner_path="$home/.gemini/hooks/scripts/send-event.py"
    payload="$(jq -nc '{ session_id: "sub-512-session", timestamp: "2026-06-24T10:00:00Z", hook_event_name: "SessionEnd", reason: "test-rotate", payload_stuff: ("a" * 50) }')"
  else
    obs_log="$home/.copilot/hooks/logs/observability.ndjson"
    prefix="COPILOT"
    event_name="sessionEnd"
    runner_path="$home/.copilot/hooks/scripts/send-event.py"
    payload="$(jq -nc '{ sessionId: "sub-512-session", timestamp: "2026-06-23T23:50:00Z", reason: "test-rotate", payload_stuff: ("a" * 50) }')"
  fi

  # First payload creates active log. Size will be ~150 bytes.
  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=$event_name \
      ${prefix}_OBSERVABILITY_LOG_MAX_BYTES=10 \
      ${prefix}_OBSERVABILITY_LOG_BACKUP_COUNT=2 \
      python3 "$runner_path" <<<"$payload"
  )"

  # Since max_bytes is 10, the next write will see st_size > 10 and rotate the first payload into .1
  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=$event_name \
      ${prefix}_OBSERVABILITY_LOG_MAX_BYTES=10 \
      ${prefix}_OBSERVABILITY_LOG_BACKUP_COUNT=2 \
      python3 "$runner_path" <<<"$payload"
  )"

  if [[ ! -f "$obs_log.1" ]]; then
    echo "Expected log backup .1 to exist, sub-512 max_bytes was silently clamped/ignored!" >&2
    exit 1
  fi
}

test_observability_log_rotation_generic_fallback() {
  local workdir
  local home
  local obs_log
  local payload
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  
  if [[ "$0" == *"gemini"* ]]; then
    obs_log="$home/.gemini/hooks/logs/observability.ndjson"
    event_name="SessionEnd"
    runner_path="$home/.gemini/hooks/scripts/send-event.py"
    payload="$(jq -nc '{ session_id: "generic-session", timestamp: "2026-06-24T10:00:00Z", hook_event_name: "SessionEnd", reason: "test-rotate", payload_stuff: ("a" * 50) }')"
  else
    obs_log="$home/.copilot/hooks/logs/observability.ndjson"
    event_name="sessionEnd"
    runner_path="$home/.copilot/hooks/scripts/send-event.py"
    payload="$(jq -nc '{ sessionId: "generic-session", timestamp: "2026-06-23T23:50:00Z", reason: "test-rotate", payload_stuff: ("a" * 50) }')"
  fi

  # Write twice using ONLY generic observability variables to trigger rotation.
  # First payload creates active log. Size will be ~150 bytes.
  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=$event_name \
      OBSERVABILITY_LOG_MAX_BYTES=10 \
      OBSERVABILITY_LOG_BACKUP_COUNT=2 \
      python3 "$runner_path" <<<"$payload"
  )"

  # Second write rotates .ndjson to .ndjson.1
  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=$event_name \
      OBSERVABILITY_LOG_MAX_BYTES=10 \
      OBSERVABILITY_LOG_BACKUP_COUNT=2 \
      python3 "$runner_path" <<<"$payload"
  )"

  if [[ ! -f "$obs_log.1" ]]; then
    echo "Expected log backup .1 to exist, generic OBSERVABILITY_LOG_MAX_BYTES fallback was ignored!" >&2
    exit 1
  fi
}

main() {
  test_hooks_json_registers_observability_emitters
  test_structured_observability_records_session_rollup_and_mutation
  test_observability_lock_wait_and_disable_are_fail_open
  test_observability_log_rotation
  test_observability_log_rotation_pruning_and_precedence
  test_observability_log_rotation_unconditional_prune
  test_observability_log_rotation_sub_512
  test_observability_log_rotation_generic_fallback
}

main "$@"

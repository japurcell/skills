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

test_sqlite_observability_persistence() {
  local workdir
  local home
  local db_path
  local payload
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  db_path="$home/.copilot/hooks/logs/observability_v1.db"

  if [[ -f "$db_path" ]]; then
    echo "Expected database file to not exist initially." >&2
    exit 1
  fi

  # Test permissive permissions (644) gets corrected to 600
  mkdir -p "$(dirname "$db_path")"
  touch "$db_path"
  chmod 644 "$db_path"

  payload="$(jq -nc '{
    sessionId: "sqlite-session-1",
    timestamp: "2026-06-23T23:50:00Z",
    reason: "test",
    cwd: "/home/adam/dev/personal/skills"
  }')"

  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionEnd \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload"
  )"

  local perms
  if stat --help 2>&1 | grep -q -- "-c"; then
    perms="$(stat -c "%a" "$db_path")"
  else
    perms="$(stat -f "%Lp" "$db_path")"
  fi
  if [[ "$perms" != "600" ]]; then
    echo "Expected database file permissions to be corrected to 600, got: $perms" >&2
    exit 1
  fi

  rm -f "$db_path"

  # Test schema version mismatch (PRAGMA user_version = 42) triggers automatic recovery (rebuilt as v1)
  mkdir -p "$(dirname "$db_path")"
  sqlite3 "$db_path" "PRAGMA user_version = 42;"

  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionEnd \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload"
  )"

  local uv
  uv="$(sqlite3 "$db_path" "PRAGMA user_version;")"
  if [[ "$uv" != "1" ]]; then
    echo "Expected database to recover and have PRAGMA user_version = 1, got: $uv" >&2
    exit 1
  fi

  rm -f "$db_path"

  # Test structural write corruption (database overwritten with garbage) triggers automatic recovery
  mkdir -p "$(dirname "$db_path")"
  echo "NOT A DATABASE AT ALL" > "$db_path"

  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionEnd \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload"
  )"

  local uv_corrupt
  uv_corrupt="$(sqlite3 "$db_path" "PRAGMA user_version;")"
  if [[ "$uv_corrupt" != "1" ]]; then
    echo "Expected database to recover from structural corruption and have PRAGMA user_version = 1, got: $uv_corrupt" >&2
    exit 1
  fi

  rm -f "$db_path"

  # Proceed with normal SQLite persistence checks
  payload="$(jq -nc '{
    sessionId: "sqlite-session-1",
    timestamp: "2026-06-23T23:50:00Z",
    reason: "test",
    cwd: "/home/adam/dev/personal/skills"
  }')"

  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionStart \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload"
  )"

  if [[ ! -f "$db_path" ]]; then
    echo "Expected database file to be created: $db_path" >&2
    exit 1
  fi

  local perms
  if stat --help 2>&1 | grep -q -- "-c"; then
    perms="$(stat -c "%a" "$db_path")"
  else
    perms="$(stat -f "%Lp" "$db_path")"
  fi
  if [[ "$perms" != "600" ]]; then
    echo "Expected database file permissions to be 600, got: $perms" >&2
    exit 1
  fi

  local uv
  uv="$(sqlite3 "$db_path" "PRAGMA user_version;")"
  if [[ "$uv" != "1" ]]; then
    echo "Expected PRAGMA user_version to be 1, got: $uv" >&2
    exit 1
  fi

  local sess_count
  sess_count="$(sqlite3 "$db_path" "SELECT COUNT(*) FROM sessions WHERE session_id = 'sqlite-session-1';")"
  if [[ "$sess_count" != "1" ]]; then
    echo "Expected 1 session row for 'sqlite-session-1', got: $sess_count" >&2
    exit 1
  fi

  local ws_root
  ws_root="$(sqlite3 "$db_path" "SELECT workspace_root FROM sessions WHERE session_id = 'sqlite-session-1';")"
  if [[ -z "$ws_root" ]]; then
    echo "Expected workspace_root to be recorded, got empty string." >&2
    exit 1
  fi

  local span_count
  span_count="$(sqlite3 "$db_path" "SELECT COUNT(*) FROM spans WHERE session_id = 'sqlite-session-1';")"
  if [[ "$span_count" != "1" ]]; then
    echo "Expected 1 span row for 'sqlite-session-1', got: $span_count" >&2
    exit 1
  fi

  local seq_no
  seq_no="$(sqlite3 "$db_path" "SELECT sequence_no FROM spans WHERE session_id = 'sqlite-session-1';")"
  if [[ "$seq_no" != "1" ]]; then
    echo "Expected sequence_no = 1, got: $seq_no" >&2
    exit 1
  fi

  local ev_name
  ev_name="$(sqlite3 "$db_path" "SELECT event_name FROM spans WHERE session_id = 'sqlite-session-1';")"
  if [[ "$ev_name" != "session_start" ]]; then
    echo "Expected event_name = session_start, got: $ev_name" >&2
    exit 1
  fi

  payload="$(jq -nc '{
    sessionId: "sqlite-session-1",
    timestamp: "2026-06-23T23:50:01Z",
    toolName: "test-tool"
  }')"

  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=preToolUse \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload"
  )"

  seq_no="$(sqlite3 "$db_path" "SELECT sequence_no FROM spans WHERE session_id = 'sqlite-session-1' AND event_name = 'before_tool';")"
  if [[ "$seq_no" != "2" ]]; then
    echo "Expected second span to have sequence_no = 2, got: $seq_no" >&2
    exit 1
  fi

  local status
  status="$(sqlite3 "$db_path" "SELECT status FROM sessions WHERE session_id = 'sqlite-session-1';")"
  if [[ "$status" != "running" ]]; then
    echo "Expected session status to be running, got: $status" >&2
    exit 1
  fi
}

test_sqlite_span_sequencing_and_child_linkage() {
  local workdir
  local home
  local db_path
  local payload
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  db_path="$home/.copilot/hooks/logs/observability_v1.db"

  # 1. Verify Parent-side subagentStart writes registry file and backfills parent session
  payload="$(jq -nc '{
    sessionId: "child-session-123",
    timestamp: "2026-06-23T23:50:00Z"
  }')"

  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=subagentStart COPILOT_SESSION_ID="parent-session-abc" \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload"
  )"

  local reg_file="$home/.copilot/hooks/logs/registries/subagents/child-session-123.json"
  if [[ ! -f "$reg_file" ]]; then
    echo "Expected subagent registry file to be created: $reg_file" >&2
    exit 1
  fi

  local reg_parent
  reg_parent="$(jq -r '.parent_session_id' "$reg_file")"
  if [[ "$reg_parent" != "parent-session-abc" ]]; then
    echo "Expected parent_session_id parent-session-abc in registry file, got: $reg_parent" >&2
    exit 1
  fi

  # 2. Verify child session has parent_session_id correctly linked in DB
  local parent_id
  parent_id="$(sqlite3 "$db_path" "SELECT parent_session_id FROM sessions WHERE session_id = 'child-session-123';")"
  if [[ "$parent_id" != "parent-session-abc" ]]; then
    echo "Expected parent_session_id link 'parent-session-abc' in database, got: '$parent_id'" >&2
    exit 1
  fi

  # 3. Verify late-arrival spans allowed in finalizing sessions
  # Move child session to 'finalizing'
  sqlite3 "$db_path" "UPDATE sessions SET status = 'finalizing' WHERE session_id = 'child-session-123';"

  # Send a late-arrival event
  payload="$(jq -nc '{
    sessionId: "child-session-123",
    timestamp: "2026-06-23T23:51:00Z"
  }')"

  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=preToolUse \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload"
  )"

  local late_arrival
  late_arrival="$(sqlite3 "$db_path" "SELECT late_arrival FROM spans WHERE session_id = 'child-session-123' AND event_name = 'before_tool';")"
  if [[ "$late_arrival" != "1" ]]; then
    echo "Expected late_arrival = 1 for finalized session span, got: '$late_arrival'" >&2
    exit 1
  fi

  # 4. Verify rejection of spans for terminal states ('success', 'failed', 'failed-finalization')
  for t_status in success failed failed-finalization; do
    sqlite3 "$db_path" "UPDATE sessions SET status = '$t_status' WHERE session_id = 'child-session-123';"
    
    # Try sending event
    payload="$(jq -nc '{
      sessionId: "child-session-123",
      timestamp: "2026-06-23T23:52:00Z"
    }')"

    output="$(
      env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=preToolUse \
        python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload"
    )"

    local span_count
    span_count="$(sqlite3 "$db_path" "SELECT COUNT(*) FROM spans WHERE session_id = 'child-session-123' AND timestamp_ms = 1782258720000;")"
    if [[ "$span_count" != "0" ]]; then
      echo "Expected span to be rejected and NOT saved when session is '$t_status', but it was saved!" >&2
      exit 1
    fi
  done

  # 5. Verify retry-based backfill when registry is delayed
  # Trigger child event first (creates session and span, parent-link is NULL because registry doesn't exist)
  payload="$(jq -nc '{
    sessionId: "child-delayed-999",
    timestamp: "2026-06-23T23:55:00Z"
  }')"

  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionStart \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload"
  )"

  local linked_parent
  linked_parent="$(sqlite3 "$db_path" "SELECT parent_session_id FROM sessions WHERE session_id = 'child-delayed-999';")"
  if [[ -n "$linked_parent" ]]; then
    echo "Expected parent_session_id to be NULL initially, got: '$linked_parent'" >&2
    exit 1
  fi

  # Create registry file now
  local delayed_reg_file="$home/.copilot/hooks/logs/registries/subagents/child-delayed-999.json"
  mkdir -p "$(dirname "$delayed_reg_file")"
  echo '{"parent_session_id":"parent-delayed-xyz"}' > "$delayed_reg_file"

  # Trigger subsequent child event (should backfill parent_session_id)
  payload="$(jq -nc '{
    sessionId: "child-delayed-999",
    timestamp: "2026-06-23T23:55:01Z"
  }')"

  output="$(
    env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=preToolUse \
      python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload"
  )"

  linked_parent="$(sqlite3 "$db_path" "SELECT parent_session_id FROM sessions WHERE session_id = 'child-delayed-999';")"
  if [[ "$linked_parent" != "parent-delayed-xyz" ]]; then
    echo "Expected delayed parent_session_id backfill to 'parent-delayed-xyz', got: '$linked_parent'" >&2
    exit 1
  fi

  # 6. Verify concurrent parallel registration does not create duplicate sequence_no
  # Trigger 10 parallel background span registers for a new session and verify all 10 have unique sequence numbers 1 to 10
  local parallel_sess="parallel-session-xyz"
  
  # Run 10 parallel processes
  for i in {1..10}; do
    (
      payload="$(jq -nc --arg idx "$i" '{
        sessionId: "parallel-session-xyz",
        timestamp: "2026-06-23T23:58:00Z",
        reason: ("proc-" + $idx)
      }')"
      env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=preToolUse \
        python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload" >/dev/null
    ) &
  done
  wait

  local unique_seq_count
  unique_seq_count="$(sqlite3 "$db_path" "SELECT COUNT(DISTINCT sequence_no) FROM spans WHERE session_id = 'parallel-session-xyz';")"
  if [[ "$unique_seq_count" != "10" ]]; then
    echo "Concurrency failure: expected 10 unique sequence numbers, got: $unique_seq_count" >&2
    # Show sequence numbers
    sqlite3 "$db_path" "SELECT sequence_no, metadata FROM spans WHERE session_id = 'parallel-session-xyz' ORDER BY sequence_no;"
    exit 1
  fi
}

test_sqlite_finalization_and_transcripts() {
  local workdir
  local home
  local db_path
  local payload
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  db_path="$home/.copilot/hooks/logs/observability_v1.db"

  # --- TEST 1: Saving, merging active chunks to .jsonl, sequence numbers and ISO 8601 timestamps ---
  payload="$(jq -nc '{
    sessionId: "final-session-1",
    timestamp: "2026-06-23T23:45:00.123Z"
  }')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionStart \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload" >/dev/null

  payload="$(jq -nc '{
    sessionId: "final-session-1",
    timestamp: "2026-06-23T23:45:01.456Z"
  }')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=preToolUse \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload" >/dev/null

  payload="$(jq -nc '{
    sessionId: "final-session-1",
    timestamp: "2026-06-23T23:45:02.789Z"
  }')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionEnd \
    env OBSERVABILITY_SAMPLING_FORCE=1 \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload" >/dev/null

  local saved_jsonl="$home/.copilot/hooks/logs/transcripts/saved/final-session-1.jsonl"
  if [[ ! -f "$saved_jsonl" ]]; then
    echo "Expected saved transcript .jsonl to exist: $saved_jsonl" >&2
    exit 1
  fi

  local merged_content
  merged_content="$(cat "$saved_jsonl")"
  if [[ ! "$merged_content" =~ "final-session-1" ]]; then
    echo "Expected final-session-1 in merged lines, got: $merged_content" >&2
    exit 1
  fi
  if [[ ! "$merged_content" =~ 2026-06-23T23:45:01\.456Z ]]; then
    echo "Expected millisecond timestamp '2026-06-23T23:45:01.456Z' in merged transcript, got: $merged_content" >&2
    exit 1
  fi

  # --- TEST 2: Payload content capping at 512KB with payload_capped = true recorded in SQLite ---
  payload="$(jq -nc '{
    sessionId: "final-session-2",
    timestamp: "2026-06-23T23:46:00.000Z"
  }')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionStart \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload" >/dev/null

  payload="$(python3 -c 'import json; print(json.dumps({"sessionId": "final-session-2", "timestamp": "2026-06-23T23:46:01.000Z", "content": "A" * 530000}))')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=preToolUse \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload" >/dev/null

  local capped_meta
  capped_meta="$(sqlite3 "$db_path" "SELECT metadata FROM spans WHERE session_id = 'final-session-2' AND event_name = 'before_tool';")"
  if [[ ! "$capped_meta" =~ "\"payload_capped\": true" ]]; then
    echo "Expected metadata to record payload_capped = true, got: $capped_meta" >&2
    exit 1
  fi

  # --- TEST 3: Stale and dead-PID span abandonment checking and setting has_errors = 1 ---
  payload="$(jq -nc '{
    sessionId: "final-session-3",
    timestamp: "2026-06-23T23:47:00.000Z"
  }')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionStart \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload" >/dev/null

  payload="$(jq -nc '{
    sessionId: "final-session-3",
    timestamp: "2026-06-23T23:47:01.000Z"
  }')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=preToolUse \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload" >/dev/null

  sqlite3 "$db_path" "UPDATE spans SET status = 'running', pid = 999999, updated_at_ms = 1000000000 WHERE session_id = 'final-session-3' AND event_name = 'before_tool';"

  payload="$(jq -nc '{
    sessionId: "final-session-3",
    timestamp: "2026-06-23T23:47:02.000Z"
  }')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionEnd \
    env OBSERVABILITY_SAMPLING_FORCE=1 \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload" >/dev/null

  local final_span_status
  final_span_status="$(sqlite3 "$db_path" "SELECT status FROM spans WHERE session_id = 'final-session-3' AND event_name = 'before_tool';")"
  if [[ "$final_span_status" != "abandoned" ]]; then
    echo "Expected dead-PID span status to be abandoned, got: $final_span_status" >&2
    exit 1
  fi

  local sess_errs
  sess_errs="$(sqlite3 "$db_path" "SELECT has_errors FROM sessions WHERE session_id = 'final-session-3';")"
  if [[ "$sess_errs" != "1" ]]; then
    echo "Expected dead-PID session to record has_errors = 1, got: $sess_errs" >&2
    exit 1
  fi
}

main() {
  (
    export OBSERVABILITY_FORCE_NDJSON=1
    test_hooks_json_registers_observability_emitters
    test_structured_observability_records_session_rollup_and_mutation
    test_observability_lock_wait_and_disable_are_fail_open
    test_observability_log_rotation
    test_observability_log_rotation_pruning_and_precedence
    test_observability_log_rotation_unconditional_prune
    test_observability_log_rotation_sub_512
    test_observability_log_rotation_generic_fallback
  )
  test_sqlite_observability_persistence
  test_sqlite_span_sequencing_and_child_linkage
  test_sqlite_finalization_and_transcripts
}

main "$@"

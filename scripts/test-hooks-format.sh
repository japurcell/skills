#!/usr/bin/env bash

set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

assert_equals() {
  local expected="$1"
  local actual="$2"
  local message="$3"

  if [[ "$actual" != "$expected" ]]; then
    echo "$message" >&2
    echo "Expected: $expected" >&2
    echo "Actual:   $actual" >&2
    exit 1
  fi
}

assert_file_contains() {
  local file="$1"
  local needle="$2"
  local message="$3"

  if ! grep -Fq "$needle" "$file"; then
    echo "$message" >&2
    echo "Missing: $needle" >&2
    echo "File: $file" >&2
    exit 1
  fi
}

run_hook() {
  local audit_log="$1"
  local max_bytes="$2"
  local payload="$3"

  AUDIT_LOG="$audit_log" \
    AUDIT_LOG_MAX_BYTES="$max_bytes" \
    bash "$REPO_ROOT/hooks/scripts/format.sh" <<<"$payload" >/dev/null
}

test_rolls_over_audit_log() {
  local workdir
  local audit_log

  workdir="$(mktemp -d)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  run_hook \
    "$audit_log" \
    1 \
    '{"sessionId":"one","timestamp":"2026-05-12T19:00:00Z","toolName":"create","toolArgs":{"path":"/tmp/one.txt","file_text":"alpha"}}'

  run_hook \
    "$audit_log" \
    1 \
    '{"sessionId":"two","timestamp":"2026-05-12T19:00:01Z","toolName":"create","toolArgs":{"path":"/tmp/two.txt","file_text":"beta"}}'

  assert_equals "yes" "$([[ -f "$audit_log.1" ]] && echo yes || echo no)" \
    "Expected audit.log to roll over into audit.log.1 when it grows past the configured size."

  assert_equals "yes" "$([[ -f "$audit_log" ]] && echo yes || echo no)" \
    "Expected the current audit.log to remain writable after rollover."

  assert_file_contains "$audit_log.1" "Session: one, Tool: create" \
    "Expected the first write to move into audit.log.1."

  assert_file_contains "$audit_log" "Session: two, Tool: create" \
    "Expected the second write to stay in the active audit log."
}

test_waits_for_log_lock() {
  local workdir
  local audit_log
  local lock_file
  local start_ns
  local end_ns
  local elapsed_ms
  local locker_pid

  workdir="$(mktemp -d)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  lock_file="$audit_log.lock"

  (
    exec 9>"$lock_file"
    flock -x 9
    sleep 1
  ) &
  locker_pid="$!"

  start_ns="$(date +%s%N)"
  run_hook \
    "$audit_log" \
    1024 \
    '{"sessionId":"lock","timestamp":"2026-05-12T19:00:02Z","toolName":"create","toolArgs":{"path":"/tmp/lock.txt","file_text":"gamma"}}'
  end_ns="$(date +%s%N)"
  wait "$locker_pid"

  elapsed_ms=$(( (end_ns - start_ns) / 1000000 ))

  if (( elapsed_ms < 900 )); then
    echo "Expected the hook to wait for the audit lock, but it completed in ${elapsed_ms}ms." >&2
    exit 1
  fi

  assert_file_contains "$audit_log" "Session: lock, Tool: create" \
    "Expected the hook to write after acquiring the log lock."
}

main() {
  test_rolls_over_audit_log
  test_waits_for_log_lock
}

main "$@"

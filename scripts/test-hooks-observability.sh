#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"
clear_observability_test_overrides

OBS_TEST_PROVIDER="copilot"
OBS_TEST_PROVIDER_LABEL="Copilot"
OBS_TEST_PROVIDER_PREFIX="COPILOT"
OBS_TEST_HOOKS_RELATIVE=".copilot/hooks"
OBS_TEST_SESSION_FIELD="sessionId"
OBS_TEST_CAPTURE_ENV="OBSERVABILITY_CAPTURE_EVENT"
OBS_TEST_SOURCE_EVENT_ENV="OBSERVABILITY_SOURCE_EVENT_NAME"
OBS_TEST_AUDIT_PASSIVE_MODE_ENV="AUDIT_PASSIVE_LOG_MODE"
OBS_TEST_AUDIT_PASSIVE_SHADOW_ENV="AUDIT_PASSIVE_LOG_SHADOW_LOG"
OBS_TEST_SESSION_ID_ENV="COPILOT_SESSION_ID"
OBS_TEST_SESSION_START_EVENT="sessionStart"
OBS_TEST_SESSION_END_EVENT="sessionEnd"
OBS_TEST_PRE_TOOL_EVENT="preToolUse"
OBS_TEST_POST_TOOL_EVENT="postToolUse"
OBS_TEST_SUBAGENT_START_EVENT="subagentStart"
OBS_TEST_PYTHON="$REPO_ROOT/scripts/observability-test-python.sh"
export OBS_TEST_PROVIDER OBS_TEST_PROVIDER_LABEL OBS_TEST_PROVIDER_PREFIX
export OBS_TEST_HOOKS_RELATIVE OBS_TEST_SESSION_FIELD OBS_TEST_PYTHON
export OBS_TEST_CAPTURE_ENV OBS_TEST_SOURCE_EVENT_ENV
export OBS_TEST_AUDIT_PASSIVE_MODE_ENV OBS_TEST_AUDIT_PASSIVE_SHADOW_ENV
export OBS_TEST_SESSION_ID_ENV OBS_TEST_SESSION_START_EVENT OBS_TEST_SESSION_END_EVENT
export OBS_TEST_PRE_TOOL_EVENT OBS_TEST_POST_TOOL_EVENT OBS_TEST_SUBAGENT_START_EVENT
source "$REPO_ROOT/scripts/observability-test-support.sh"

run_installed_copilot_hook() {
  local home="$1"
  local hook_name="$2"
  local payload="$3"
  shift 3

  env HOME="$home" AUDIT_LOG="$home/audit.log" "$@" python3 "$home/.copilot/hooks/scripts/$hook_name" <<<"$payload"
}

test_send_event_does_not_wait_for_stdin_close() {
  local workdir
  local home

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  home="$workdir/home"
  install_into_temp_home "$home"

  HOME="$home" python3 - "$home" <<'PY'
import os
import ctypes
import importlib.util
import json
import subprocess
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch

home = sys.argv[1]
env = os.environ.copy()
env.update(
    {
        "HOME": home,
        "OBSERVABILITY_CAPTURE_EVENT": "true",
        "OBSERVABILITY_SOURCE_EVENT_NAME": "postToolUse",
    }
)
process = subprocess.Popen(
    [sys.executable, f"{home}/.copilot/hooks/scripts/send-event.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env=env,
)
assert process.stdin is not None
process.stdin.write(
    json.dumps(
        {
            "sessionId": "open-stdin",
            "timestamp": "2026-09-03T17:00:00Z",
        },
        indent=2,
    )
    + "\n"
)
process.stdin.flush()

deadline = time.monotonic() + 1.0
while process.poll() is None and time.monotonic() < deadline:
    time.sleep(0.01)

if process.poll() is None:
    process.stdin.close()
    process.terminate()
    process.wait(timeout=1)
    raise SystemExit("Expected send-event.py to exit without waiting for stdin to close.")

stdout, stderr = process.communicate()
if process.returncode != 0:
    raise SystemExit(f"send-event.py failed: {stderr.strip()}")
if stdout.strip() != "{}":
    raise SystemExit(f"Expected neutral JSON output, got: {stdout!r}")

process = subprocess.Popen(
    [sys.executable, f"{home}/.copilot/hooks/scripts/send-event.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env=env,
)
assert process.stdin is not None
process.stdin.write('{"sessionId":"trailing-junk"}\nJUNK')
process.stdin.flush()

deadline = time.monotonic() + 1.0
while process.poll() is None and time.monotonic() < deadline:
    time.sleep(0.01)

if process.poll() is None:
    process.stdin.close()
    process.terminate()
    process.wait(timeout=1)
    raise SystemExit("Expected trailing hook input to fail without waiting for stdin to close.")

stdout, stderr = process.communicate()
if process.returncode == 0:
    raise SystemExit(f"Expected trailing hook input to fail, got: {stdout!r}")
if "Invalid hook input: expected a JSON object" not in stderr:
    raise SystemExit(f"Expected malformed-input error, got: {stderr!r}")

common_path = f"{home}/.copilot/hooks/scripts/helpers/common.py"
spec = importlib.util.spec_from_file_location("copilot_common", common_path)
assert spec is not None and spec.loader is not None
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)


class FakeKernel32:
    def __init__(self):
        self.calls = 0

    def PeekNamedPipe(self, _handle, _buffer, _size, _read, available, _remaining):
        available._obj.value = 4 if self.calls == 0 else 0
        self.calls += 1
        return 1


kernel32 = FakeKernel32()
msvcrt = SimpleNamespace(get_osfhandle=lambda _fd: 123)
with (
    patch.object(common.os, "name", "nt"),
    patch.object(common.os, "read", return_value=b"JUNK"),
    patch.dict(sys.modules, {"msvcrt": msvcrt}),
    patch.object(ctypes, "WinDLL", return_value=kernel32, create=True),
):
    if common._read_available_stdin_bytes(0) != b"JUNK":
        raise SystemExit("Expected Windows PeekNamedPipe drain to return available bytes.")
PY
}

assert_hook_registered_with_observability_emitter() {
  local event_name="$1"
  local source_event_name="$2"

  assert_equals '$HOME/.copilot/hooks/scripts/send-event.py' \
    "$(jq -r --arg event "$event_name" '.hooks[$event][] | select(.env.OBSERVABILITY_CAPTURE_EVENT == "true") | .bash' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected $event_name to register send-event.py."
  assert_equals true \
    "$(jq -r --arg event "$event_name" '[.hooks[$event][] | select(.env.OBSERVABILITY_CAPTURE_EVENT == "true")] | length == 1' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected $event_name to capture observability input."
  assert_equals "$source_event_name" \
    "$(jq -r --arg event "$event_name" '.hooks[$event][] | select(.env.OBSERVABILITY_CAPTURE_EVENT == "true") | .env.OBSERVABILITY_SOURCE_EVENT_NAME' "$REPO_ROOT/.copilot/hooks/hooks.json")" \
    "Expected $event_name to preserve its source event name."
}

test_hooks_json_registers_observability_emitters() {
  local event_name
  local source_event_name

  for event_name in sessionStart subagentStart preToolUse agentStop errorOccurred notification postToolUseFailure subagentStop sessionEnd permissionRequest postToolUse preCompact userPromptSubmitted userPromptTransformed; do
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
  trap cleanup_test_workdir RETURN
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

test_sqlite_adversarial_hardening() {
  local workdir
  local home
  local db_path
  local payload
  local output

  workdir="$(setup_test_workdir)"
  trap cleanup_test_workdir RETURN
  home="$workdir/home"
  install_into_temp_home "$home"
  db_path="$home/.copilot/hooks/logs/observability_v1.db"

  # 1. Trigger sessionStart to create database and WAL/SHM files
  payload="$(jq -nc '{
    sessionId: "adversarial-session-1",
    timestamp: "2026-06-23T23:50:00Z"
  }')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionStart \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload" >/dev/null

  # Verify WAL/SHM permissions are restricted to 600 if they exist
  local suffix
  for suffix in -wal -shm; do
    if [[ -f "$db_path$suffix" ]]; then
      local perms
      if stat --help 2>&1 | grep -q -- "-c"; then
        perms="$(stat -c "%a" "$db_path$suffix")"
      else
        perms="$(stat -f "%Lp" "$db_path$suffix")"
      fi
      assert_equals "600" "$perms" "Expected WAL/SHM side file $suffix permissions to be 600, got: $perms"
    fi
  done

  # 2. Trigger subagentStart to create registry file
  payload="$(jq -nc '{
    sessionId: "child-session-perms-test",
    timestamp: "2026-06-23T23:50:00Z"
  }')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=subagentStart COPILOT_SESSION_ID="parent-session-abc" \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload" >/dev/null

  local perms_reg
  local reg_file="$home/.copilot/hooks/logs/registries/subagents/child-session-perms-test.json"
  if stat --help 2>&1 | grep -q -- "-c"; then
    perms_reg="$(stat -c "%a" "$reg_file")"
  else
    perms_reg="$(stat -f "%Lp" "$reg_file")"
  fi
  assert_equals "600" "$perms_reg" "Expected registry file permissions to be 600, got: $perms_reg"

  local perms_dir
  local reg_dir="$home/.copilot/hooks/logs/registries/subagents"
  if stat --help 2>&1 | grep -q -- "-c"; then
    perms_dir="$(stat -c "%a" "$reg_dir")"
  else
    perms_dir="$(stat -f "%Lp" "$reg_dir")"
  fi
  assert_equals "700" "$perms_dir" "Expected registry dir permissions to be 700, got: $perms_dir"

  # 3. Cyclical payload capability unit test
  python3 - "$home" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/.copilot/hooks/scripts")
from helpers.observability import _cap_payload_content

raw = {}
raw["self"] = raw

effective = {}
effective["self"] = effective

r_raw, r_eff, capped = _cap_payload_content(raw, effective)
assert capped is True, "Expected capped to be True for cyclic payload"
assert r_raw == {"self": "<circular reference>"}, f"Expected circular reference string, got {r_raw}"
assert r_eff == {"self": "<circular reference>"}, f"Expected circular reference string, got {r_eff}"
print("CYCLIC_TEST_OK")
PY

  # 4. Late-arriving span chunk appends to saved transcript
  payload_start="$(jq -nc '{sessionId: "late-append-session", timestamp: "2026-06-23T23:50:00Z"}')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionStart \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload_start" >/dev/null

  payload_end="$(jq -nc '{sessionId: "late-append-session", timestamp: "2026-06-23T23:50:01Z"}')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=sessionEnd env OBSERVABILITY_SAMPLING_FORCE=1 \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload_end" >/dev/null

  local saved_jsonl="$home/.copilot/hooks/logs/transcripts/saved/late-append-session.jsonl"
  if [[ ! -f "$saved_jsonl" ]]; then
    echo "Expected saved jsonl to exist" >&2
    exit 1
  fi
  
  local lines_before
  lines_before="$(wc -l < "$saved_jsonl" | xargs)"

  # Manually set session status back to 'finalizing' to simulate concurrent late span processing
  sqlite3 "$db_path" "UPDATE sessions SET status = 'finalizing' WHERE session_id = 'late-append-session';"

  payload_late="$(jq -nc '{sessionId: "late-append-session", timestamp: "2026-06-23T23:50:02Z", toolName: "late-tool"}')"
  env HOME="$home" OBSERVABILITY_CAPTURE_EVENT=true OBSERVABILITY_SOURCE_EVENT_NAME=preToolUse \
    python3 "$home/.copilot/hooks/scripts/send-event.py" <<<"$payload_late" >/dev/null

  local lines_after
  lines_after="$(wc -l < "$saved_jsonl" | xargs)"
  
  if [[ "$lines_after" -le "$lines_before" ]]; then
    echo "Expected late arriving span to be appended to saved transcript, lines: $lines_before -> $lines_after" >&2
    exit 1
  fi
  
  if ! grep -q "late-tool" "$saved_jsonl"; then
    echo "Expected late tool info to be in the saved transcript" >&2
    exit 1
  fi

  # 5. Fallback fcntl gracefully on Windows/non-POSIX using python mock
  HOME="$home" python3 - "$home" <<'PY'
import sys
sys.modules["fcntl"] = None

from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/.copilot/hooks/scripts")
from helpers import observability

lock_path = Path(sys.argv[1]) / "test_fallback.lock"
lock_fd = observability._acquire_lock(lock_path, 0.1)
assert lock_fd == -1, f"Expected lock_fd to be -1, got {lock_fd}"

record = observability._build_record("test_type", {"sessionId": "fallback-test"})
success = observability._write_record(record)
assert success is True, "Expected _write_record to succeed in fallback mode"
print("MOCK_FCNTL_OK")
PY
}

main() {
  (
    export OBSERVABILITY_FORCE_NDJSON=1
    test_hooks_json_registers_observability_emitters
    test_temp_install_uses_fixture_codex_home
    test_send_event_does_not_wait_for_stdin_close
    test_structured_observability_records_session_rollup_and_mutation
    test_observability_lock_wait_and_disable_are_fail_open
    test_audit_log_secure_file_permissions
    test_observability_log_rotation
    test_observability_log_rotation_pruning_and_precedence
    test_observability_log_rotation_unconditional_prune
    test_observability_log_rotation_max_bytes_zero_disables_active_rotation
    test_observability_log_rotation_sub_512
    test_observability_log_rotation_generic_fallback
    test_observability_log_rotation_fail_open
  )
  test_sqlite_observability_persistence
  test_sqlite_span_sequencing_and_child_linkage
  test_sqlite_finalization_and_transcripts
  test_sqlite_finalization_maintenance_resume
  test_sqlite_adversarial_hardening
  test_sqlite_additional_observability_scenarios
}

OBS_TEST_SUITE_HOME="$(setup_test_workdir)"

cleanup_observability_suite_home() {
  local workdir="${OBS_TEST_SUITE_HOME:-}"
  cleanup_test_workdir
}

trap cleanup_observability_suite_home EXIT
with_hook_test_environment "$OBS_TEST_SUITE_HOME" -- main "$@"

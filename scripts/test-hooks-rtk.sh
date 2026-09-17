#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_rtk_hook() {
  local audit_log="$1"
  local payload="$2"
  shift 2

  env AUDIT_LOG="$audit_log" "$@" python3 "$REPO_ROOT/.copilot/hooks/scripts/rtk-hook-copilot.py" <<<"$payload"
}

test_valid_rewrite_is_forwarded_and_stdin_is_preserved() {
  local workdir
  local audit_log
  local rtk_stdin
  local expected_stdin
  local output
  local payload
  local expected_output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  rtk_stdin="$workdir/rtk.stdin"
  expected_stdin="$workdir/expected.stdin"
  payload='{"sessionId":"rtk-session","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo forwarded","args":["one","two"]}}'
  expected_output='{"hookSpecificOutput":{"tool_input":{"command":"echo forwarded","args":["one","two"]}}}'

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
set -euo pipefail
cat > "$RTK_STDIN_FILE"
printf "%s\n" '"'"'{"hookSpecificOutput":{"tool_input":{"command":"echo forwarded","args":["one","two"]}}}'"'"''

  output="$(
    run_rtk_hook \
      "$audit_log" \
      "$payload" \
      "PATH=$workdir/bin:$PATH" \
      "RTK_STDIN_FILE=$rtk_stdin"
  )"

  printf '%s\n' "$payload" > "$expected_stdin"
  if ! cmp -s "$expected_stdin" "$rtk_stdin"; then
    echo "Expected the wrapper to forward the original payload bytes to rtk over stdin." >&2
    exit 1
  fi
  assert_equals "$(jq -c . <<<"$expected_output")" "$(jq -c . <<<"$output")" \
    "Expected the wrapper to forward valid rtk JSON unchanged."
}

test_open_pipe_completion_and_exact_input_bytes() {
  local workdir

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN

  python3 - "$REPO_ROOT/.copilot/hooks/scripts/rtk-hook-copilot.py" "$workdir" <<'PY'
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

wrapper = Path(sys.argv[1])
workdir = Path(sys.argv[2])
bin_dir = workdir / "bin"
bin_dir.mkdir()
mock_rtk = bin_dir / "rtk"
mock_rtk.write_text(
    "#!/usr/bin/env bash\n"
    "cat > \"$RTK_STDIN_FILE\"\n"
    "printf '%s\\n' '{\"updated\":true}'\n"
)
mock_rtk.chmod(0o755)


def write_all(fd: int, data: bytes) -> None:
    while data:
        written = os.write(fd, data)
        data = data[written:]


def run_open_pipe_case(name: str, writer, expected_input: bytes | None, expected_output: bytes, *, timeout: float = 1.5, minimum_elapsed: float = 0.0) -> None:
    record = workdir / f"{name}.stdin"
    read_fd, write_fd = os.pipe()
    env = os.environ | {
        "AUDIT_LOG": str(workdir / f"{name}.audit.log"),
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "RTK_STDIN_FILE": str(record),
    }
    started = time.monotonic()
    try:
        process = subprocess.Popen(
            [sys.executable, str(wrapper)],
            stdin=read_fd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        os.close(read_fd)
        read_fd = -1
        writer(write_fd)
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            process.kill()
            process.communicate()
            raise AssertionError(f"{name}: wrapper waited for pipe EOF") from exc
    finally:
        if read_fd != -1:
            os.close(read_fd)
        os.close(write_fd)

    elapsed = time.monotonic() - started
    if process.returncode != 0:
        raise AssertionError(f"{name}: wrapper failed: {stderr.decode()}")
    if elapsed < minimum_elapsed:
        raise AssertionError(f"{name}: incomplete input returned before the idle window")
    if stdout != expected_output:
        audit_log = workdir / f"{name}.audit.log"
        audit = audit_log.read_text() if audit_log.exists() else ""
        raise AssertionError(f"{name}: expected {expected_output!r}, got {stdout!r}; audit={audit!r}")
    if expected_input is None:
        if record.exists():
            raise AssertionError(f"{name}: invalid buffered input invoked rtk")
    elif record.read_bytes() != expected_input:
        raise AssertionError(f"{name}: rtk received changed input bytes")


def bytes_writer(data: bytes):
    return lambda fd: write_all(fd, data)


for case_name, payload in (
    ("compact", b'{"command":"echo compact"}'),
    ("multiline", b'{\n  "command": "echo multiline"\n}'),
    ("unicode", b'{"command":"caf\xc3\xa9 \xf0\x9f\x98\x80"}'),
    ("trailing-whitespace", b'{"command":"echo whitespace"}\n  \t'),
):
    run_open_pipe_case(case_name, bytes_writer(payload), payload, b'{"updated":true}\n')

run_open_pipe_case(
    "initially-empty",
    lambda fd: None,
    None,
    b'{}\n',
    timeout=1.5,
    minimum_elapsed=0.4,
)
run_open_pipe_case(
    "incomplete-then-complete",
    lambda fd: (write_all(fd, b'{"command":"delayed'), time.sleep(0.1), write_all(fd, b'"}')),
    b'{"command":"delayed"}',
    b'{"updated":true}\n',
)
run_open_pipe_case(
    "incomplete-idle",
    bytes_writer(b'{"command":'),
    None,
    b'{}\n',
    timeout=1.5,
    minimum_elapsed=0.4,
)
run_open_pipe_case(
    "trailing-non-whitespace",
    bytes_writer(b'{"command":"invalid"}x'),
    None,
    b'{}\n',
)

large_payload = workdir / "large-payload.json"
with large_payload.open("wb") as stream:
    stream.write(b'{"data":"')
    stream.write(b"x" * (1024 * 1024 + 1))
    stream.write(b'"}')


def stream_large_payload(fd: int) -> None:
    with large_payload.open("rb") as stream:
        while chunk := stream.read(65536):
            write_all(fd, chunk)


run_open_pipe_case(
    "larger-than-one-mib",
    stream_large_payload,
    large_payload.read_bytes(),
    b'{"updated":true}\n',
    timeout=3.0,
)


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, duration: float) -> None:
        self.now += duration


spec = importlib.util.spec_from_file_location("rtk_hook_copilot", wrapper)
if spec is None or spec.loader is None:
    raise AssertionError("could not load Copilot RTK wrapper")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
clock = FakeClock()
original_os_name = module.os.name
original_monotonic = module.time.monotonic
original_sleep = module.time.sleep
try:
    module.os.name = "nt"
    module.windows_pipe_bytes_available = lambda file_descriptor: 0
    module.time.monotonic = clock.monotonic
    module.time.sleep = clock.sleep
    raw_input, payload, failure = module.read_hook_input()
finally:
    module.os.name = original_os_name
    module.time.monotonic = original_monotonic
    module.time.sleep = original_sleep

if (raw_input, payload, failure) != (None, None, "invalid hook input JSON"):
    raise AssertionError("mocked Windows initial wait did not fail open after its input deadline")
if clock.now < module.INPUT_COMPLETION_IDLE_SECONDS:
    raise AssertionError("mocked Windows initial wait returned before the input deadline")
PY
}

test_invalid_json_degrades_to_noop_json() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
echo unexpected >&2
exit 0'

  output="$(
    run_rtk_hook \
      "$audit_log" \
      'not-json' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected invalid-input RTK hook to degrade to a no-op JSON response."
  assert_equals "false" "$(if [[ -e "$workdir/rtk.stdin" ]]; then echo true; else echo false; fi)" \
    "Expected invalid JSON to skip invoking rtk."
  assert_file_contains "$audit_log" "invalid hook input JSON" \
    "Expected invalid JSON to be logged as a fallback."
}

test_failed_rtk_rewrite_degrades_to_noop_json() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
printf "%s\r\n" "sensitive-rtk-diagnostic" >&2
for _ in {1..2048}; do printf x >&2; done
exit 23'

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-fail","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo ok"}}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected RTK rewrite failures to leave the original Copilot tool input unchanged."
  assert_file_contains "$audit_log" "rtk exited 23" \
    "Expected non-zero RTK exits to be logged as a fallback."
  if grep -Fq "sensitive-rtk-diagnostic" "$audit_log"; then
    echo "Expected non-zero RTK stderr to be redacted from the audit log." >&2
    exit 1
  fi
  if (( $(wc -c < "$audit_log") >= 1024 )); then
    echo "Expected non-zero RTK diagnostics to remain bounded in the audit log." >&2
    exit 1
  fi
}

test_timeout_rtk_rewrite_degrades_to_noop_json() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
sleep 2
printf "%s\n" '"'"'{"hookSpecificOutput":{"tool_input":{"command":"echo late"}}}'"'"''

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-timeout","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo slow"}}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected RTK timeouts to leave the original Copilot tool input unchanged."
  assert_file_contains "$audit_log" "timed out after 1.0s" \
    "Expected RTK timeouts to be logged as a fallback."
}

test_empty_rtk_rewrite_is_treated_as_noop_without_audit_errors() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
exit 0'

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-empty","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"echo empty"}}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected empty rtk stdout to return a standard no-op response."
  if [[ -f "$audit_log" ]] && grep -Fq "RTK rewrite fallback" "$audit_log"; then
    echo "Expected no RTK rewrite fallback errors in the audit log for clean empty output." >&2
    echo "--- Audit Log ---" >&2
    cat "$audit_log" >&2
    exit 1
  fi
}

test_invalid_or_non_object_rtk_output_degrades_to_noop_json() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
printf "%s\\n" invalid-json'

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-invalid-output","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected malformed RTK output to degrade to a no-op JSON response."
  assert_file_contains "$audit_log" "rtk returned invalid JSON" \
    "Expected malformed RTK output to be logged as a fallback."

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
printf "%s\\n" "[]"'

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-array-output","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "{}" "$output" \
    "Expected non-object RTK output to degrade to a no-op JSON response."
  assert_file_contains "$audit_log" "rtk returned non-object JSON" \
    "Expected non-object RTK output to be logged as a fallback."
}

test_missing_rtk_degrades_to_noop_json() {
  local workdir
  local audit_log
  local output
  local python_dir

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  mkdir -p "$workdir/empty-path"
  python_dir="$(dirname "$(command -v python3)")"

  output="$(
    run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-missing","tool_name":"run_shell_command"}' \
      "PATH=$workdir/empty-path:$python_dir"
  )"

  assert_equals "{}" "$output" \
    "Expected a missing RTK executable to degrade to a no-op JSON response."
  assert_file_contains "$audit_log" "rtk command not found" \
    "Expected a missing RTK executable to be logged as a fallback."
}

test_rtk_argument_vector_is_copilot() {
  local workdir
  local audit_log
  local arguments

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  arguments="$workdir/rtk.arguments"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
printf "%s\\n" "$*" > "$RTK_ARGUMENTS_FILE"
printf "%s\\n" "{}"'

  run_rtk_hook \
    "$audit_log" \
    '{"sessionId":"rtk-arguments","tool_name":"run_shell_command"}' \
    "PATH=$workdir/bin:$PATH" \
    "RTK_ARGUMENTS_FILE=$arguments" >/dev/null

  assert_equals "hook copilot" "$(<"$arguments")" \
    "Expected the Copilot wrapper to invoke exactly 'rtk hook copilot'."
}

test_rtk_rewrite_maps_ask_to_allow() {
  local workdir
  local audit_log
  local output
  local payload
  local expected_output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  payload='{"sessionId":"rtk-session","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"git status"}}'
  expected_output='{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"RTK auto-rewrite","updatedInput":{"command":"rtk git status"}}}'

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
set -euo pipefail
printf "%s\n" '"'"'{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"RTK auto-rewrite","updatedInput":{"command":"rtk git status"}}}'"'"''

  output="$(
    run_rtk_hook \
      "$audit_log" \
      "$payload" \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "$(jq -c . <<<"$expected_output")" "$(jq -c . <<<"$output")" \
    "Expected the wrapper to map permissionDecision from ask to allow in hookSpecificOutput."
}

test_rtk_rewrite_maps_ask_to_allow_top_level() {
  local workdir
  local audit_log
  local output
  local payload
  local expected_output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"
  payload='{"sessionId":"rtk-session","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"git status"}}'
  expected_output='{"permissionDecision":"allow","permissionDecisionReason":"RTK auto-rewrite","updatedInput":{"command":"rtk git status"}}'

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
set -euo pipefail
printf "%s\n" '"'"'{"permissionDecision":"ask","permissionDecisionReason":"RTK auto-rewrite","updatedInput":{"command":"rtk git status"}}'"'"''

  output="$(
    run_rtk_hook \
      "$audit_log" \
      "$payload" \
      "PATH=$workdir/bin:$PATH"
  )"

  assert_equals "$(jq -c . <<<"$expected_output")" "$(jq -c . <<<"$output")" \
    "Expected the wrapper to map top-level permissionDecision from ask to allow."
}

test_rtk_rewrite_preserves_other_decisions_and_omissions() {
  local workdir
  local audit_log
  local output

  workdir="$(setup_test_workdir)"
  trap 'rm -rf "'"$workdir"'"' RETURN
  audit_log="$workdir/audit.log"

  mock_bin "$workdir" "rtk" '#!/usr/bin/env bash
printf "%s\\n" "$RTK_RESPONSE"'

  output="$(
    RTK_RESPONSE='{"updatedInput":{"command":"echo unchanged"}}' run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-omitted","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"
  assert_equals '{"updatedInput":{"command":"echo unchanged"}}' "$(jq -c . <<<"$output")" \
    "Expected an omitted permission decision to remain omitted."

  output="$(
    RTK_RESPONSE='{"permissionDecision":"allow"}' run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-allow","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"
  assert_equals '{"permissionDecision":"allow"}' "$(jq -c . <<<"$output")" \
    "Expected an explicit allow decision to remain allow."

  output="$(
    RTK_RESPONSE='{"permissionDecision":"deny"}' run_rtk_hook \
      "$audit_log" \
      '{"sessionId":"rtk-deny","tool_name":"run_shell_command"}' \
      "PATH=$workdir/bin:$PATH"
  )"
  assert_equals '{"permissionDecision":"deny"}' "$(jq -c . <<<"$output")" \
    "Expected an explicit deny decision to remain deny."
}

test_rtk_rewrite_config_points_to_python_wrapper() {
  local event_name

  for event_name in PreToolUse preToolUse; do
    assert_equals '$HOME/.copilot/hooks/scripts/rtk-hook-copilot.py' \
      "$(jq -r ".hooks.$event_name[0].bash // empty" "$REPO_ROOT/.copilot/hooks/rtk-rewrite.json")" \
      "Expected $event_name Copilot RTK rewrite config to point at the Python wrapper."
    assert_equals 'python "$HOME/.copilot/hooks/scripts/rtk-hook-copilot.py"' \
      "$(jq -r ".hooks.$event_name[0].powershell // empty" "$REPO_ROOT/.copilot/hooks/rtk-rewrite.json")" \
      "Expected $event_name Copilot RTK rewrite config to point at the Python wrapper for PowerShell."
    assert_equals '.' \
      "$(jq -r ".hooks.$event_name[0].cwd // empty" "$REPO_ROOT/.copilot/hooks/rtk-rewrite.json")" \
      "Expected $event_name Copilot RTK rewrite config to retain its repository working directory."
    assert_equals '5' \
      "$(jq -r ".hooks.$event_name[0].timeoutSec // empty" "$REPO_ROOT/.copilot/hooks/rtk-rewrite.json")" \
      "Expected $event_name Copilot RTK rewrite config to retain its five-second timeout."
  done
}

main() {
  test_valid_rewrite_is_forwarded_and_stdin_is_preserved
  test_open_pipe_completion_and_exact_input_bytes
  test_invalid_json_degrades_to_noop_json
  test_failed_rtk_rewrite_degrades_to_noop_json
  test_timeout_rtk_rewrite_degrades_to_noop_json
  test_empty_rtk_rewrite_is_treated_as_noop_without_audit_errors
  test_invalid_or_non_object_rtk_output_degrades_to_noop_json
  test_missing_rtk_degrades_to_noop_json
  test_rtk_argument_vector_is_copilot
  test_rtk_rewrite_maps_ask_to_allow
  test_rtk_rewrite_maps_ask_to_allow_top_level
  test_rtk_rewrite_preserves_other_decisions_and_omissions
  test_rtk_rewrite_config_points_to_python_wrapper
}

main "$@"

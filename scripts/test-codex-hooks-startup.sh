#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$REPO_ROOT/.codex/hooks/load-required-skills.py"
workdir=""

cleanup() {
  if [[ -n "$workdir" ]]; then
    rm -rf -- "$workdir"
  fi
}

reset_workdir() {
  cleanup
  workdir="$(mktemp -d)"
}

trap cleanup EXIT

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

assert_equals() {
  local expected="$1"
  local actual="$2"
  local description="$3"

  [[ "$actual" == "$expected" ]] || fail "$description: expected '$expected', got '$actual'"
}

test_startup_loads_required_skill_context() {
  reset_workdir
  mkdir -p "$workdir/home/.agents/skills/caveman"
  printf '%s\n' '---' 'name: caveman' '---' 'Use few words.' > "$workdir/home/.agents/skills/caveman/SKILL.md"

  local stdout_file="$workdir/stdout.json"
  local stderr_file="$workdir/stderr.txt"
  local status=0
  HOME="$workdir/home" python3 "$HOOK" >"$stdout_file" 2>"$stderr_file" <<'JSON' || status=$?
{"hook_event_name":"SessionStart","source":"startup","session_id":"test-session"}
JSON

  assert_equals '0' "$status" 'startup hook exit status'

  python3 - "$stdout_file" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_bytes().decode("utf-8"))
assert payload["systemMessage"] == "Required skill context loaded from 1 file(s)."
assert payload["hookSpecificOutput"] == {
    "hookEventName": "SessionStart",
    "additionalContext": (
        "Required skill context loaded.\n\n"
        "BEGIN REQUIRED SKILL: caveman/SKILL.md\n"
        "Use few words.\n"
        "END REQUIRED SKILL: caveman/SKILL.md"
    ),
}
PY
}

test_global_hook_template() {
  python3 - "$REPO_ROOT/.codex/global-hooks.json" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
groups = payload["hooks"]["SessionStart"]
assert len(groups) == 1
group = groups[0]
assert group["matcher"] == "startup|resume|clear|compact"
assert group["hooks"] == [{
    "type": "command",
    "command": "python3 ~/.codex/hooks/load-required-skills.py",
    "commandWindows": 'py -3 "%USERPROFILE%\\.codex\\hooks\\load-required-skills.py"',
    "timeout": 5,
    "statusMessage": "Loading required skill context",
    "additionalContextLimit": 8000,
}]
assert "SubagentStart" not in payload["hooks"]
PY
}

assert_failure_response() {
  local home_dir="$1"
  local input="$2"
  local expected_reason="$3"
  local stdout_file="$workdir/failure-stdout.json"
  local stderr_file="$workdir/failure-stderr.txt"
  local status=0

  HOME="$home_dir" python3 "$HOOK" >"$stdout_file" 2>"$stderr_file" <<<"$input" || status=$?
  assert_equals '0' "$status" 'failure hook exit status'

  python3 - "$stdout_file" "$expected_reason" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_bytes().decode("utf-8"))
assert payload["continue"] is False
assert sys.argv[2] in payload["stopReason"]
assert payload["systemMessage"] == "Required skill context was NOT loaded."
PY
}

test_rejects_invalid_events_and_missing_skills() {
  reset_workdir
  mkdir -p "$workdir/home/.agents/skills/caveman"
  printf '%s\n' 'Valid body.' > "$workdir/home/.agents/skills/caveman/SKILL.md"

  assert_failure_response \
    "$workdir/home" \
    '{"hook_event_name":"SubagentStart","source":"startup"}' \
    'Unsupported hook event'

  rm "$workdir/home/.agents/skills/caveman/SKILL.md"
  assert_failure_response \
    "$workdir/home" \
    '{"hook_event_name":"SessionStart","source":"startup"}' \
    'Required skill file not found'
}

test_input_sources_and_audit_boundaries() {
  reset_workdir
  mkdir -p "$workdir/home/.agents/skills/caveman"
  printf '%s\n' '---' 'name: caveman' '---' 'Unicode: ✓' > "$workdir/home/.agents/skills/caveman/SKILL.md"

  for source in resume clear compact; do
    local output="$workdir/$source.json"
    HOME="$workdir/home" python3 "$HOOK" >"$output" <<JSON
{"hook_event_name":"SessionStart","source":"$source"}
JSON
    python3 - "$output" <<'PY'
import json
import pathlib
payload = json.loads(pathlib.Path(__import__("sys").argv[1]).read_bytes().decode("utf-8"))
assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
assert "✓" in payload["hookSpecificOutput"]["additionalContext"]
PY
  done

  assert_failure_response "$workdir/home" '{not json' 'Invalid hook input'
  assert_failure_response "$workdir/home" '{"hook_event_name":"SessionStart","source":"startup"} trailing' 'trailing data'
  assert_failure_response "$workdir/home" '{"hook_event_name":"SessionStart","source":"other"}' 'Unsupported SessionStart source'

  local audit="$workdir/home/.codex/hooks/logs/audit.log"
  python3 - "$audit" <<'PY'
import pathlib
import stat
import sys

audit = pathlib.Path(sys.argv[1])
assert stat.S_IMODE(audit.stat().st_mode) == 0o600
assert stat.S_IMODE(audit.parent.stat().st_mode) == 0o700
PY
  ! grep -F 'Unicode: ✓' "$audit" || fail 'audit log must not contain skill contents'
}

test_skill_path_and_content_boundaries() {
  reset_workdir
  mkdir -p "$workdir/home/.agents/skills/caveman" "$workdir/outside"
  printf 'safe body\n' > "$workdir/home/.agents/skills/caveman/SKILL.md"
  printf 'outside body\n' > "$workdir/outside/SKILL.md"
  ln -s "$workdir/outside/SKILL.md" "$workdir/home/.agents/skills/caveman/escaped.md"

  local configured="$workdir/configured-hook.py"
  cp "$HOOK" "$configured"
  python3 - "$configured" "$workdir/outside/SKILL.md" <<'PY'
import pathlib
import sys
path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
path.write_text(text.replace('required_skill_files = ["caveman/SKILL.md"]', f'required_skill_files = [{sys.argv[2]!r}]'), encoding="utf-8")
PY
  local original_hook="$HOOK"
  HOOK="$configured"
  assert_failure_response "$workdir/home" '{"hook_event_name":"SessionStart","source":"startup"}' 'safe relative path'

  cp "$original_hook" "$configured"
  python3 - "$configured" <<'PY'
import pathlib
import sys
path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
path.write_text(text.replace('required_skill_files = ["caveman/SKILL.md"]', 'required_skill_files = ["caveman/escaped.md"]'), encoding="utf-8")
PY
  assert_failure_response "$workdir/home" '{"hook_event_name":"SessionStart","source":"startup"}' 'escapes the skills directory'

  cp "$original_hook" "$configured"
  python3 - "$configured" <<'PY'
import pathlib
import sys
path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
path.write_text(text.replace('required_skill_files = ["caveman/SKILL.md"]', 'required_skill_files = ["../outside/SKILL.md"]'), encoding="utf-8")
PY
  assert_failure_response "$workdir/home" '{"hook_event_name":"SessionStart","source":"startup"}' 'safe relative path'
  HOOK="$original_hook"
}

test_open_stdin_and_audit_failure_are_fail_open() {
  reset_workdir
  mkdir -p "$workdir/home/.agents/skills/caveman" "$workdir/home/.codex/hooks/logs/audit.log"
  printf 'open pipe body\n' > "$workdir/home/.agents/skills/caveman/SKILL.md"

  python3 - "$HOOK" "$workdir/home" <<'PY'
import json
import os
import select
import subprocess
import sys

environment = dict(os.environ, HOME=sys.argv[2])
process = subprocess.Popen(
    [sys.executable, sys.argv[1]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment
)
assert process.stdin is not None and process.stdout is not None
process.stdin.write(b'{"hook_event_name":"SessionStart","source":"startup"}')
process.stdin.flush()
assert select.select([process.stdout], [], [], 2)[0], "hook waited for stdin EOF"
payload = json.loads(process.stdout.readline().decode("utf-8"))
assert payload["systemMessage"] == "Required skill context loaded from 1 file(s)."
process.stdin.close()
assert process.wait(timeout=2) == 0
assert b"audit unavailable" in process.stderr.read()
PY
}

test_unreadable_invalid_utf8_size_and_multiple_skills() {
  reset_workdir
  mkdir -p "$workdir/home/.agents/skills/caveman"
  local skill="$workdir/home/.agents/skills/caveman/SKILL.md"
  printf 'body\n' > "$skill"
  chmod 000 "$skill"
  assert_failure_response "$workdir/home" '{"hook_event_name":"SessionStart","source":"startup"}' 'not readable'
  chmod 644 "$skill"
  printf '\377' > "$skill"
  assert_failure_response "$workdir/home" '{"hook_event_name":"SessionStart","source":"startup"}' 'not valid UTF-8'
  python3 - "$skill" <<'PY'
import pathlib
import sys
pathlib.Path(sys.argv[1]).write_text("x" * 20_001, encoding="utf-8")
PY
  assert_failure_response "$workdir/home" '{"hook_event_name":"SessionStart","source":"startup"}' 'exceeds the maximum size'

  printf 'first\n' > "$skill"
  mkdir -p "$workdir/home/.agents/skills/other"
  printf 'second\n' > "$workdir/home/.agents/skills/other/SKILL.md"
  local configured="$workdir/multi-hook.py"
  cp "$HOOK" "$configured"
  python3 - "$configured" <<'PY'
import pathlib
import sys
path = pathlib.Path(sys.argv[1])
path.write_text(path.read_text(encoding="utf-8").replace('required_skill_files = ["caveman/SKILL.md"]', 'required_skill_files = ["caveman/SKILL.md", "other/SKILL.md"]'), encoding="utf-8")
PY
  HOME="$workdir/home" python3 "$configured" > "$workdir/multi.json" <<'JSON'
{"hook_event_name":"SessionStart","source":"startup"}
JSON
  python3 - "$workdir/multi.json" <<'PY'
import json
import pathlib
import sys
payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["systemMessage"] == "Required skill context loaded from 2 file(s)."
assert "first" in payload["hookSpecificOutput"]["additionalContext"]
assert "second" in payload["hookSpecificOutput"]["additionalContext"]
PY
}

test_large_frontmatter_does_not_consume_context_budget() {
  reset_workdir
  mkdir -p "$workdir/home/.agents/skills/caveman"
  local skill="$workdir/home/.agents/skills/caveman/SKILL.md"
  python3 - "$skill" <<'PY'
import pathlib
import sys

pathlib.Path(sys.argv[1]).write_text(
    "---\nmetadata: " + ("x" * 25_000) + "\n---\nsmall body\n",
    encoding="utf-8",
)
PY

  HOME="$workdir/home" python3 "$HOOK" > "$workdir/large-frontmatter.json" <<'JSON'
{"hook_event_name":"SessionStart","source":"startup"}
JSON
  python3 - "$workdir/large-frontmatter.json" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
context = payload["hookSpecificOutput"]["additionalContext"]
assert "small body" in context
assert "metadata:" not in context
PY

  python3 - "$skill" <<'PY'
import pathlib
import sys

pathlib.Path(sys.argv[1]).write_text("x" * 1_000_001, encoding="utf-8")
PY
  assert_failure_response \
    "$workdir/home" \
    '{"hook_event_name":"SessionStart","source":"startup"}' \
    'Required skill file exceeds the maximum size'
}

test_rejects_input_that_crosses_the_byte_limit_on_the_final_read() {
  reset_workdir
  mkdir -p "$workdir/home/.agents/skills/caveman"
  printf 'body\n' > "$workdir/home/.agents/skills/caveman/SKILL.md"

  python3 - "$HOOK" "$workdir/home" <<'PY'
import json
import os
import subprocess
import sys

payload = {
    "hook_event_name": "SessionStart",
    "source": "startup",
    "padding": "x" * 1_000_000,
}
process = subprocess.run(
    [sys.executable, sys.argv[1]],
    input=json.dumps(payload).encode("utf-8"),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=dict(os.environ, HOME=sys.argv[2]),
    check=False,
)
assert process.returncode == 0
response = json.loads(process.stdout.decode("utf-8"))
assert response["continue"] is False, response
assert "maximum size" in response["stopReason"], response
PY
}

test_audit_does_not_follow_a_symlinked_directory() {
  reset_workdir
  mkdir -p "$workdir/home/.agents/skills/caveman" "$workdir/home/.codex/hooks" "$workdir/outside"
  printf 'body\n' > "$workdir/home/.agents/skills/caveman/SKILL.md"
  chmod 755 "$workdir/outside"
  ln -s "$workdir/outside" "$workdir/home/.codex/hooks/logs"

  HOME="$workdir/home" python3 "$HOOK" > "$workdir/symlink-audit.json" 2> "$workdir/symlink-audit.stderr" <<'JSON'
{"hook_event_name":"SessionStart","source":"startup"}
JSON

  python3 - "$workdir/symlink-audit.json" "$workdir/symlink-audit.stderr" "$workdir/outside" <<'PY'
import json
import pathlib
import stat
import sys

response = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert response["systemMessage"] == "Required skill context loaded from 1 file(s)."
assert "audit unavailable" in pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")
outside = pathlib.Path(sys.argv[3])
assert stat.S_IMODE(outside.stat().st_mode) == 0o755
assert not (outside / "audit.log").exists()
PY

  rm "$workdir/home/.codex/hooks/logs"
  mkdir "$workdir/home/.codex/hooks/logs"
  printf 'external audit\n' > "$workdir/outside-audit.log"
  chmod 600 "$workdir/outside-audit.log"
  ln -s "$workdir/outside-audit.log" "$workdir/home/.codex/hooks/logs/audit.log"
  HOME="$workdir/home" python3 "$HOOK" > "$workdir/symlink-file-audit.json" 2> "$workdir/symlink-file-audit.stderr" <<'JSON'
{"hook_event_name":"SessionStart","source":"startup"}
JSON
  python3 - "$workdir/symlink-file-audit.json" "$workdir/symlink-file-audit.stderr" "$workdir/outside-audit.log" <<'PY'
import json
import pathlib
import stat
import sys

response = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert response["systemMessage"] == "Required skill context loaded from 1 file(s)."
assert "audit unavailable" in pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")
outside = pathlib.Path(sys.argv[3])
assert outside.read_text(encoding="utf-8") == "external audit\n"
assert stat.S_IMODE(outside.stat().st_mode) == 0o600
PY

  rm "$workdir/home/.codex/hooks/logs/audit.log"
  ln -s "$workdir/missing-audit-target.log" "$workdir/home/.codex/hooks/logs/audit.log"
  HOME="$workdir/home" python3 "$HOOK" > "$workdir/dangling-audit.json" 2> "$workdir/dangling-audit.stderr" <<'JSON'
{"hook_event_name":"SessionStart","source":"startup"}
JSON
  python3 - "$workdir/dangling-audit.json" "$workdir/dangling-audit.stderr" "$workdir/missing-audit-target.log" <<'PY'
import json
import pathlib
import sys

response = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert response["systemMessage"] == "Required skill context loaded from 1 file(s)."
assert "audit unavailable" in pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")
assert not pathlib.Path(sys.argv[3]).exists()
PY
}

test_lone_surrogates_always_return_valid_utf8_json() {
  reset_workdir
  mkdir -p "$workdir/home/.agents/skills/caveman"
  printf 'body\n' > "$workdir/home/.agents/skills/caveman/SKILL.md"

  python3 - "$HOOK" "$workdir/home" <<'PY'
import json
import os
import subprocess
import sys

payloads = [
    {"hook_event_name": "SessionStart", "source": "startup", "session_id": "\ud800"},
    {"hook_event_name": "SessionStart", "source": "\ud800"},
    {"hook_event_name": "\ud800", "source": "startup"},
]
for payload in payloads:
    process = subprocess.run(
        [sys.executable, sys.argv[1]],
        input=json.dumps(payload).encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=dict(os.environ, HOME=sys.argv[2]),
        check=False,
    )
    assert process.returncode == 0, process.stderr.decode("utf-8", errors="replace")
    response = json.loads(process.stdout.decode("utf-8"))
    assert response["systemMessage"] in {
        "Required skill context loaded from 1 file(s).",
        "Required skill context was NOT loaded.",
    }
PY
}

test_open_stdin_rejects_irrecoverable_json_but_waits_for_valid_completion() {
  reset_workdir
  mkdir -p "$workdir/home/.agents/skills/caveman"
  printf 'body\n' > "$workdir/home/.agents/skills/caveman/SKILL.md"

  python3 - "$HOOK" "$workdir/home" <<'PY'
import json
import os
import select
import subprocess
import sys

environment = dict(os.environ, HOME=sys.argv[2])
for incomplete_prefix in (b"", b'{"x":"\xe2'):
    incomplete = subprocess.Popen(
        [sys.executable, sys.argv[1]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment
    )
    assert incomplete.stdin is not None and incomplete.stdout is not None
    if incomplete_prefix:
        incomplete.stdin.write(incomplete_prefix)
        incomplete.stdin.flush()
    assert select.select([incomplete.stdout], [], [], 2)[0], (
        f"hook waited indefinitely for incomplete input: {incomplete_prefix!r}"
    )
    incomplete_response = json.loads(incomplete.stdout.readline().decode("utf-8"))
    assert incomplete_response["continue"] is False
    incomplete.stdin.close()
    assert incomplete.wait(timeout=2) == 0

for invalid_prefix in (
    b"{not json",
    b'{"x": invalid}',
    b'{"x" 1}',
    b'{"x": 1 nope',
    b'{"x": -x',
    b'{"hook_event_name":"SessionStart","source":1e}',
    b'{"x":"\\uZZZZ"}',
):
    invalid = subprocess.Popen(
        [sys.executable, sys.argv[1]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment
    )
    assert invalid.stdin is not None and invalid.stdout is not None
    invalid.stdin.write(invalid_prefix)
    invalid.stdin.flush()
    assert select.select([invalid.stdout], [], [], 2)[0], (
        f"hook waited for EOF after irrecoverably invalid JSON: {invalid_prefix!r}"
    )
    invalid_response = json.loads(invalid.stdout.readline().decode("utf-8"))
    assert invalid_response["continue"] is False
    invalid.stdin.close()
    assert invalid.wait(timeout=2) == 0

valid = subprocess.Popen(
    [sys.executable, sys.argv[1]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment
)
assert valid.stdin is not None and valid.stdout is not None
valid.stdin.write(b'{\n  "hook_event_name":')
valid.stdin.flush()
assert not select.select([valid.stdout], [], [], 0.1)[0], "hook rejected an incomplete valid JSON prefix"
valid.stdin.write(b' "SessionStart",\n  "source": "startup"\n}')
valid.stdin.flush()
assert select.select([valid.stdout], [], [], 2)[0], "hook did not accept completed multiline JSON"
valid_response = json.loads(valid.stdout.readline().decode("utf-8"))
assert valid_response["systemMessage"] == "Required skill context loaded from 1 file(s)."
valid.stdin.close()
assert valid.wait(timeout=2) == 0

number = subprocess.Popen(
    [sys.executable, sys.argv[1]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment
)
assert number.stdin is not None and number.stdout is not None
number.stdin.write(b'{"hook_event_name":"SessionStart","source":"startup","padding":1e')
number.stdin.flush()
assert not select.select([number.stdout], [], [], 0.1)[0], "hook rejected an incomplete valid JSON number"
number.stdin.write(b'2}')
number.stdin.flush()
assert select.select([number.stdout], [], [], 2)[0], "hook did not accept a completed JSON number"
number_response = json.loads(number.stdout.readline().decode("utf-8"))
assert number_response["systemMessage"] == "Required skill context loaded from 1 file(s)."
number.stdin.close()
assert number.wait(timeout=2) == 0
PY
}

test_startup_loads_required_skill_context
test_global_hook_template
test_rejects_invalid_events_and_missing_skills
test_input_sources_and_audit_boundaries
test_skill_path_and_content_boundaries
test_open_stdin_and_audit_failure_are_fail_open
test_unreadable_invalid_utf8_size_and_multiple_skills
test_large_frontmatter_does_not_consume_context_budget
test_rejects_input_that_crosses_the_byte_limit_on_the_final_read
test_audit_does_not_follow_a_symlinked_directory
test_lone_surrogates_always_return_valid_utf8_json
test_open_stdin_rejects_irrecoverable_json_but_waits_for_valid_completion
printf 'PASS: Codex SessionStart required-skill hook\n'

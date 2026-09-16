#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

run_okf_hook() {
  local payload="$1"

  python3 "$REPO_ROOT/.github/hooks/scripts/lint-okf.py" <<<"$payload"
}

test_clean_post_tool_use_returns_empty_object() {
  local output

  output="$(
    run_okf_hook '{"sessionId":"session-123","timestamp":1789050461000,"cwd":"'"$REPO_ROOT"'","toolName":"edit","toolArgs":{"path":".agents/instructions/repo.md"},"toolResult":{"resultType":"success","textResultForLlm":"Updated file"}}'
  )"

  assert_equals "{}" "$output" "Expected a clean Copilot postToolUse result to be a JSON no-op."
}

test_adapter_contract() {
  python3 - "$REPO_ROOT" <<'PY'
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

source = Path(sys.argv[1])


def make_repo() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    tempdir = tempfile.TemporaryDirectory()
    root = Path(tempdir.name) / "repo"
    shutil.copytree(source / "scripts" / "fixtures" / "okf-valid-repo", root)
    shutil.copytree(source / "scripts", root / "scripts")
    shutil.copytree(source / ".github", root / ".github")
    return tempdir, root


@contextmanager
def repo():
    tempdir, root = make_repo()
    try:
        yield root
    finally:
        tempdir.cleanup()


def run(root: Path, payload: object | None = None, raw: str | None = None, extra_env: dict[str, str] | None = None) -> dict:
    environment = os.environ.copy()
    if extra_env:
        environment.update(extra_env)
    completed = subprocess.run(
        [sys.executable, str(root / ".github/hooks/scripts/lint-okf.py")],
        input=raw if raw is not None else json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        env=environment,
    )
    assert completed.returncode == 0, completed
    assert completed.stderr == "", completed.stderr
    assert len(completed.stdout.encode("utf-8")) < 8192, len(completed.stdout.encode("utf-8"))
    return json.loads(completed.stdout)


def run_registered_stop_hook(root: Path, payload: dict[str, object]) -> dict:
    registrations = json.loads((root / ".github/hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]["agentStop"]
    responses = []
    for registration in registrations:
        command = registration["bash"]
        completed = subprocess.run(
            [sys.executable, str(root / command)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        assert completed.returncode == 0, completed
        assert completed.stderr == "", completed.stderr
        responses.append(json.loads(completed.stdout))
    return responses[-1]


def run_with_open_stdin(program: Path, payload: dict[str, object] | None = None, raw: bytes | None = None) -> dict:
    process = subprocess.Popen(
        [sys.executable, str(program)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert process.stdin is not None
        process.stdin.write(raw if raw is not None else json.dumps(payload).encode("utf-8"))
        process.stdin.flush()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired as exc:
            raise AssertionError(f"{program.name} waited for stdin EOF") from exc
        assert process.returncode == 0, process.returncode
        assert process.stdout is not None
        assert process.stderr is not None
        assert process.stderr.read() == b""
        return json.loads(process.stdout.read().decode("utf-8"))
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        if process.stdin is not None:
            process.stdin.close()


def run_stop_hook_bytes(root: Path, payload: dict[str, object], extra_env: dict[str, str] | None = None) -> bytes:
    environment = os.environ.copy()
    if extra_env:
        environment.update(extra_env)
    completed = subprocess.run(
        [sys.executable, str(root / ".github/hooks/scripts/validate-stop.py")],
        input=json.dumps(payload).encode("utf-8"),
        capture_output=True,
        check=False,
        env=environment,
    )
    assert completed.returncode == 0, completed
    assert completed.stderr == b"", completed.stderr
    return completed.stdout


def write_stop_validator(root: Path, name: str, reason: str) -> None:
    (root / ".github/hooks/scripts" / name).write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import sys\n"
        f"response = {{'decision': 'block', 'reason': {reason!r}}}\n"
        "sys.stdout.buffer.write(json.dumps(response, ensure_ascii=False, separators=(',', ':')).encode('utf-8') + b'\\n')\n",
        encoding="utf-8",
    )


def invalidate(root: Path) -> list[dict]:
    path = root / ".agents/instructions/repo.md"
    path.write_text(path.read_text(encoding="utf-8").replace("type: Agent Instruction", "type: Agent Memory"), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(root / "scripts/lint-okf.py"), "--format", "json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 1, completed
    diagnostics = json.loads(completed.stdout)["diagnostics"]
    assert diagnostics and diagnostics[0]["id"] == "OKF101", diagnostics
    return diagnostics


def write_linter(root: Path, program: str) -> None:
    (root / "scripts/lint-okf.py").write_text(program, encoding="utf-8")


def copilot_post_tool_use(root: Path) -> dict:
    return {
        "sessionId": "session-123",
        "timestamp": 1789050461000,
        "cwd": str(root),
        "toolName": "edit",
        "toolArgs": {"path": ".agents/instructions/repo.md"},
        "toolResult": {"resultType": "success", "textResultForLlm": "Updated file"},
    }


def copilot_agent_stop(root: Path) -> dict:
    return {
        "sessionId": "session-123",
        "timestamp": 1789050461000,
        "cwd": str(root),
        "transcriptPath": str(root / ".copilot/session-transcript.jsonl"),
        "stopReason": "end_turn",
        "stop_hook_active": False,
    }


def copilot_subagent_stop(root: Path) -> dict:
    return {
        "sessionId": "session-123",
        "timestamp": 1789050461000,
        "cwd": str(root),
        "transcriptPath": str(root / ".copilot/subagent-transcript.jsonl"),
        "agentId": "agent-456",
        "agentType": "custom",
        "agentName": "reviewer",
        "agentDisplayName": "Reviewer",
        "response": "Review complete.",
        "stopReason": "end_turn",
    }


def vscode_post_tool_use(root: Path) -> dict:
    return {
        "hook_event_name": "PostToolUse",
        "session_id": "session-123",
        "timestamp": "2026-09-10T12:00:00Z",
        "cwd": str(root),
        "tool_name": "Edit",
        "tool_input": {"file_path": ".agents/instructions/repo.md"},
        "tool_result": {"result_type": "success", "text_result_for_llm": "Updated file"},
    }


def vscode_agent_stop(root: Path) -> dict:
    return {
        "hook_event_name": "Stop",
        "session_id": "session-123",
        "timestamp": "2026-09-10T12:00:00Z",
        "cwd": str(root),
        "transcript_path": str(root / ".copilot/session-transcript.jsonl"),
        "stop_reason": "end_turn",
        "stop_hook_active": False,
    }


def vscode_subagent_stop(root: Path) -> dict:
    return {
        "hook_event_name": "SubagentStop",
        "session_id": "session-123",
        "timestamp": "2026-09-10T12:00:00Z",
        "cwd": str(root),
        "transcript_path": str(root / ".copilot/subagent-transcript.jsonl"),
        "agent_id": "agent-456",
        "agent_type": "custom",
        "agent_name": "reviewer",
        "agent_display_name": "Reviewer",
        "last_assistant_message": "Review complete.",
        "stop_reason": "end_turn",
    }


with repo() as root:
    nested = root / "nested/worktree"
    nested.mkdir(parents=True)
    assert run(root, copilot_post_tool_use(nested)) == {}
    windows_payload = copilot_post_tool_use(nested)
    windows_payload["cwd"] = str(nested).replace("/", "\\")
    assert run(root, windows_payload) == {}


with repo() as root:
    outside = root.parent / "decoy"
    (outside / "scripts").mkdir(parents=True)
    marker = outside / "executed"
    write_linter(
        outside,
        "#!/usr/bin/env python3\n"
        "import json\n"
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('executed', encoding='utf-8')\n"
        "print(json.dumps({\"schema_version\": 1, \"diagnostics\": []}))\n",
    )
    response = run(root, copilot_post_tool_use(outside))
    assert not marker.exists(), marker
    assert set(response) == {"additionalContext"}, response
    assert "OKF900" in response["additionalContext"], response
    response = run(root, copilot_subagent_stop(outside))
    assert not marker.exists(), marker
    assert response["decision"] == "block" and "OKF900" in response["reason"], response


with repo() as root:
    assert run(root, copilot_post_tool_use(root)) == {}
    assert run(root, vscode_post_tool_use(root)) == {}
    assert run(root, copilot_agent_stop(root)) == {"decision": "allow"}
    assert run(root, copilot_subagent_stop(root)) == {"decision": "allow"}
    assert run(root, vscode_agent_stop(root)) == {"decision": "allow"}
    assert run(root, vscode_subagent_stop(root)) == {"decision": "allow"}


with repo() as root:
    payload = copilot_agent_stop(root)
    assert run_with_open_stdin(root / ".github/hooks/scripts/lint-okf.py", payload)["decision"] == "allow"
    assert run_with_open_stdin(root / ".github/hooks/scripts/validate-stop.py", payload) == {"decision": "allow"}


with repo() as root:
    for raw in (b"{", b"{not json"):
        adapter_response = run_with_open_stdin(root / ".github/hooks/scripts/lint-okf.py", raw=raw)
        assert adapter_response["decision"] == "block" and "OKF900" in adapter_response["reason"], adapter_response
        coordinator_response = run_with_open_stdin(root / ".github/hooks/scripts/validate-stop.py", raw=raw)
        assert coordinator_response["decision"] == "block", coordinator_response


with repo() as root:
    raw = json.dumps(copilot_agent_stop(root), indent=2).encode("utf-8")
    assert run_with_open_stdin(root / ".github/hooks/scripts/lint-okf.py", raw=raw)["decision"] == "allow"
    assert run_with_open_stdin(root / ".github/hooks/scripts/validate-stop.py", raw=raw) == {"decision": "allow"}


with repo() as root:
    raw = json.dumps(copilot_agent_stop(root)).encode("utf-8") + b" trailing"
    adapter_response = run_with_open_stdin(root / ".github/hooks/scripts/lint-okf.py", raw=raw)
    assert adapter_response["decision"] == "block" and "OKF900" in adapter_response["reason"], adapter_response
    assert run_with_open_stdin(root / ".github/hooks/scripts/validate-stop.py", raw=raw)["decision"] == "block"

with repo() as root:
    diagnostics = invalidate(root)
    expected = diagnostics[0]
    rendered = f'{expected["path"]}:{expected["line"]}:{expected["column"]}: {expected["id"]} {expected["message"]}'
    post = run(root, copilot_post_tool_use(root))
    assert set(post) == {"additionalContext"}, post
    assert rendered in post["additionalContext"], post
    assert "0 additional diagnostics omitted." in post["additionalContext"], post
    assert "./scripts/lint-okf.py" in post["additionalContext"], post
    windows_post = run(
        root,
        copilot_post_tool_use(root),
        extra_env={"OKF_LINT_TEST_PLATFORM": "windows"},
    )
    assert "python scripts/lint-okf.py" in windows_post["additionalContext"], windows_post
    assert "./scripts/lint-okf.py" not in windows_post["additionalContext"], windows_post
    for payload in (
        copilot_agent_stop(root),
        copilot_subagent_stop(root),
        vscode_agent_stop(root),
        vscode_subagent_stop(root),
    ):
        response = run(root, payload)
        assert response["decision"] == "block" and rendered in response["reason"], response
        assert "0 additional diagnostics omitted." in response["reason"], response

with repo() as root:
    diagnostics = [
        {"id": "OKF101", "path": f".agents/memory/{index:02d}.md", "line": 1, "column": 1, "message": "x" * 20}
        for index in range(25, 0, -1)
    ]
    write_linter(
        root,
        "#!/usr/bin/env python3\nimport json\nprint(json.dumps({\"schema_version\": 1, \"diagnostics\": " + repr(diagnostics) + "}))\nraise SystemExit(1)\n",
    )
    response = run(root, copilot_agent_stop(root))
    reason = response["reason"]
    assert response["decision"] == "block", response
    assert reason.count("OKF101") == 20, reason
    assert ".agents/memory/01.md" in reason and ".agents/memory/20.md" in reason, reason
    assert ".agents/memory/21.md" not in reason, reason
    assert "5 additional diagnostics omitted." in reason, reason
    assert len(reason.encode("utf-8")) < 8192, len(reason.encode("utf-8"))
    assert len(json.dumps(response, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) < 8192

with repo() as root:
    diagnostics = [
        {"id": "OKF101", "path": f".agents/memory/{index:02d}.md", "line": 1, "column": 1, "message": f"detail-{index:02d}-" + "x" * 500}
        for index in range(25)
    ]
    write_linter(
        root,
        "#!/usr/bin/env python3\nimport json\nprint(json.dumps({\"schema_version\": 1, \"diagnostics\": " + repr(diagnostics) + "}))\nraise SystemExit(1)\n",
    )
    response = run(root, copilot_agent_stop(root))
    reason = response["reason"]
    shown = [item for item in diagnostics if item["message"] in reason]
    assert response["decision"] == "block" and shown, response
    assert shown == diagnostics[:len(shown)], shown
    assert f"{len(diagnostics) - len(shown)} additional diagnostics omitted." in reason, reason
    assert "Rerun: ./scripts/lint-okf.py" in reason, response

for invalid_id in ("NOTOKF", "OKF12", "OKF1234", "okf123"):
    with repo() as root:
        diagnostics = [{"id": invalid_id, "path": ".agents/memory/a.md", "line": 1, "column": 1, "message": "bad identifier"}]
        write_linter(
            root,
            "#!/usr/bin/env python3\nimport json\nprint(json.dumps({\"schema_version\": 1, \"diagnostics\": " + repr(diagnostics) + "}))\nraise SystemExit(1)\n",
        )
        response = run(root, copilot_post_tool_use(root))
        assert set(response) == {"additionalContext"} and "OKF900" in response["additionalContext"], response

for program in (
    "#!/usr/bin/env python3\nprint('{not json')\nraise SystemExit(1)\n",
    "#!/usr/bin/env python3\nimport json\nprint(json.dumps({\"schema_version\": 2, \"diagnostics\": []}))\n",
    "#!/usr/bin/env python3\nimport json\nprint(json.dumps({\"schema_version\": 1, \"diagnostics\": [{\"id\": \"OKF101\"}]}))\nraise SystemExit(1)\n",
    "#!/usr/bin/env python3\nimport json\nprint(json.dumps({\"schema_version\": 1, \"diagnostics\": []}))\nraise SystemExit(1)\n",
    "#!/usr/bin/env python3\nimport json\nprint(json.dumps({\"schema_version\": 1, \"diagnostics\": []}))\nraise SystemExit(2)\n",
    "#!/usr/bin/env python3\nimport time\ntime.sleep(9)\n",
):
    with repo() as root:
        write_linter(root, program)
        response = run(root, copilot_post_tool_use(root))
        assert set(response) == {"additionalContext"}, response
        assert "OKF900" in response["additionalContext"], response
        assert "0 additional diagnostics omitted." in response["additionalContext"], response

with repo() as root:
    missing = root / "scripts/lint-okf.py"
    missing.unlink()
    response = run(root, copilot_agent_stop(root))
    assert response["decision"] == "block" and "OKF900" in response["reason"], response
    malformed = run(root, raw="{")
    assert malformed["decision"] == "block" and "OKF900" in malformed["reason"], malformed

with repo() as root:
    shutil.rmtree(root / "scripts/vendor/yaml")
    response = run(root, copilot_post_tool_use(root))
    assert set(response) == {"additionalContext"} and "OKF900" in response["additionalContext"], response

with repo() as root:
    (root / ".agents/skills/ingest-source").mkdir(parents=True)
    (root / ".agents/skills/ingest-source/SKILL.md").write_text("---\nname: ingest-source\ndescription: test\n---\n", encoding="utf-8")
    (root / ".agents/sources/new.md").write_text("new source\n", encoding="utf-8")
    invalidate(root)
    payload = copilot_agent_stop(root)
    response = run_registered_stop_hook(root, payload)
    assert response["decision"] == "block", response
    reason = response["reason"]
    assert "Pending ingest blocks normal work." in reason, response
    assert "OKF validation failed:" in reason and "OKF101" in reason, response
    assert reason.index("Pending ingest blocks normal work.") < reason.index("OKF validation failed:"), reason


with repo() as root:
    write_stop_validator(root, "inject-auto-ingest-context.py", "Pending ingest blocks normal work. 雪")
    write_stop_validator(root, "lint-okf.py", "OKF validation failed: 雪")
    response = json.loads(run_stop_hook_bytes(root, copilot_agent_stop(root), {"PYTHONIOENCODING": "cp1252"}).decode("utf-8"))
    assert response["decision"] == "block", response
    assert "雪" in response["reason"], response


with repo() as root:
    ingest_reason = "Pending ingest blocks normal work. " + "i" * 5000
    okf_reason = "OKF validation failed: " + "o" * 5000
    write_stop_validator(root, "inject-auto-ingest-context.py", ingest_reason)
    write_stop_validator(root, "lint-okf.py", okf_reason)
    response = json.loads(run_stop_hook_bytes(root, copilot_agent_stop(root)).decode("utf-8"))
    serialized = json.dumps(response, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    assert len(serialized) < 8192, len(serialized)
    reason = response["reason"]
    assert "Pending ingest blocks normal work." in reason, reason
    assert "OKF validation failed:" in reason, reason
    assert reason.index("Pending ingest blocks normal work.") < reason.index("OKF validation failed:"), reason
    assert "truncated" in reason.lower(), reason
PY
}

main() {
  test_clean_post_tool_use_returns_empty_object
  test_adapter_contract
  echo "PASSED: Copilot OKF lint hook contract"
}

main "$@"

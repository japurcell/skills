#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

python3 - "$REPO_ROOT" <<'PY'
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

source = Path(sys.argv[1])
registration = json.loads((source / ".codex/hooks.json").read_text())["hooks"]["Stop"][0]["hooks"][0]
assert registration["command"] == 'python3 "$(git rev-parse --show-toplevel)/.codex/hooks/repository-okf.py"', registration
assert "git','rev-parse','--show-toplevel" in registration["commandWindows"], registration
assert "repository-okf.py" not in (source / ".codex/global-hooks.json").read_text()
assert "repository-okf.py" not in (source / "scripts/install.sh").read_text()
assert "repository-okf.py" not in (source / "scripts/install.ps1").read_text()

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary) / "repo"
    shutil.copytree(source / "scripts/fixtures/okf-valid-repo", root)
    shutil.copytree(source / "scripts", root / "scripts")
    adapter = root / ".codex/hooks/repository-okf.py"
    adapter.parent.mkdir(parents=True)
    shutil.copy2(source / ".codex/hooks/repository-okf.py", adapter)
    shutil.copytree(source / ".codex/hooks/helpers", adapter.parent / "helpers")
    audit = root / "audit.log"
    env = {**os.environ, "AUDIT_LOG": str(audit)}

    def run(payload, *, environment=env):
        completed = subprocess.run(
            [sys.executable, str(adapter)], input=json.dumps(payload), text=True,
            capture_output=True, env=environment, timeout=11,
        )
        assert completed.returncode == 0, completed
        assert len(completed.stdout.encode()) < 8192, completed.stdout
        return json.loads(completed.stdout)

    payload = {"hook_event_name": "Stop", "session_id": "test-session", "cwd": str(root)}
    assert run(payload) == {}
    first_audit = audit.read_text().splitlines()
    assert len(first_audit) == 1, first_audit
    assert json.loads(first_audit[0])["outcome"] == "pass"
    assert run(payload) == {}
    assert len(audit.read_text().splitlines()) == 1, "repeated stop duplicated audit"

    file = root / ".agents/instructions/repo.md"
    file.write_text(file.read_text().replace("type: Agent Instruction", "type: Agent Memory"))
    first = run(payload)
    assert first["decision"] == "block" and "OKF101" in first["reason"], first
    retry = run({**payload, "stop_hook_active": True})
    assert set(retry) == {"systemMessage"} and "OKF101" in retry["systemMessage"], retry
    records = [json.loads(line) for line in audit.read_text().splitlines()]
    assert len(records) == 3 and records[-1]["outcome"] == "fail" and records[-1]["attempt"] == "retry", records
    assert all(len(line.encode()) <= 4096 for line in audit.read_text().splitlines())
    assert all("message" not in line and "type must" not in line for line in audit.read_text().splitlines())

    nested = root / "nested/worktree"
    nested.mkdir(parents=True)
    assert run({**payload, "cwd": str(nested).replace("/nested/", "/nested/../nested/")})["decision"] == "block"
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    registered = subprocess.run(registration["command"], shell=True, cwd=nested,
        input=json.dumps({**payload, "cwd": str(nested)}), text=True, capture_output=True, env=env)
    assert registered.returncode == 0 and json.loads(registered.stdout)["decision"] == "block", registered
    outside = root.parent / "outside"
    outside.mkdir()
    assert "OKF900" in run({**payload, "cwd": str(outside)})["systemMessage"]
    assert "python scripts/lint-okf.py" in run(payload, environment={**env, "OKF_LINT_TEST_PLATFORM": "windows"})["reason"]

    (root / "scripts/lint-okf.py").unlink()
    incomplete = run(payload)
    assert "OKF900" in incomplete["systemMessage"], incomplete
    assert json.loads(audit.read_text().splitlines()[-1])["outcome"] == "incomplete"

    for index in range(100):
        (root / ".agents/memory" / (f"audit-{index:03d}-" + "x" * 80 + ".md")).write_text("# invalid\n")
    run(payload)
    last = audit.read_text().splitlines()[-1]
    assert len(last.encode()) <= 4096, len(last.encode())
    assert json.loads(last)["omitted_paths"] > 0, last

    shutil.copy2(source / "scripts/lint-okf.py", root / "scripts/lint-okf.py")
    assert run(payload, environment={**env, "AUDIT_LOG": str(root)})["decision"] == "block"
    linked = root / "audit-link"
    linked.symlink_to(root.parent, target_is_directory=True)
    assert run(payload, environment={**env, "AUDIT_LOG": str(linked / "outside.log")})["decision"] == "block"
    assert not (root.parent / "outside.log").exists()

    values = [{"id": "OKF101", "path": f".agents/memory/{index:02d}.md", "line": 1,
        "column": 1, "message": "x" * 20} for index in range(25)]
    (root / "scripts/lint-okf.py").write_text(
        "import json\nprint(json.dumps({'schema_version': 1, 'diagnostics': " + repr(values) + "}))\nraise SystemExit(1)\n")
    bounded = run(payload)
    assert bounded["reason"].count("OKF101") == 20, bounded
    assert "5 additional diagnostics omitted." in bounded["reason"], bounded

print("PASSED: Codex repository OKF Stop envelope and audit")
PY

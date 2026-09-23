#!/usr/bin/env python3
"""Exercise generated scanners through their JSON hook entry points."""

from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent.parent
HOOKS = {
    "copilot": ROOT / ".copilot/hooks/scripts/scan-secrets.py",
    "gemini": ROOT / ".gemini/hooks/scripts/scan-secrets.py",
    "codex": ROOT / ".codex/hooks/scan-secrets.py",
}


def payload(provider: str, repo: Path, mode: str) -> dict[str, object]:
    if provider == "copilot":
        return {"sessionId": "capture-test", "reason": "complete"}
    if provider == "gemini":
        return {"session_id": "capture-test", "hook_event_name":
                "BeforeTool" if mode == "block" else "SessionEnd", "cwd": str(repo)}
    return {"session_id": "capture-test", "hook_event_name":
            "PreToolUse" if mode == "block" else "Stop", "cwd": str(repo)}


def run_case(
    provider: str, mode: str, fake_git: str, maximum: float = 3.0,
    capture_failure: bool = False,
) -> tuple[dict, str]:
    with tempfile.TemporaryDirectory(prefix="scan-capture-test-") as directory:
        root = Path(directory)
        repo = root / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        fake_bin = root / "bin"
        fake_bin.mkdir()
        git_path = fake_bin / "git"
        git_path.write_text(fake_git, encoding="utf-8")
        git_path.chmod(0o755)
        real_git = shutil.which("git")
        assert real_git is not None
        subprocess.run([real_git, "-C", str(repo), "init", "-q"], check=True)
        output_path = root / "response.json"
        error_path = root / "stderr.txt"
        env = os.environ.copy()
        env.update({"PATH": f"{fake_bin}{os.pathsep}{env['PATH']}", "SCAN_MODE": mode,
                    "SECRETS_LOG_DIR": str(root / "logs"), "TMPDIR": str(root),
                    "REAL_GIT": real_git})
        started = time.monotonic()
        command = [sys.executable, "-I", "-S", "-B", str(HOOKS[provider])]
        if capture_failure:
            wrapper = (
                "import runpy, tempfile\n"
                "def fail(*args, **kwargs):\n"
                "    raise OSError('private capture failure detail')\n"
                "tempfile.TemporaryFile = fail\n"
                f"runpy.run_path({str(HOOKS[provider])!r}, run_name='__main__')\n"
            )
            command = [sys.executable, "-I", "-S", "-B", "-c", wrapper]
        with output_path.open("wb") as output, error_path.open("wb") as errors:
            process = subprocess.Popen(
                command,
                cwd=repo, env=env, stdin=subprocess.PIPE, stdout=output,
                stderr=errors, start_new_session=True,
            )
            try:
                process.communicate(json.dumps(payload(provider, repo, mode)).encode(),
                                    timeout=maximum)
            except subprocess.TimeoutExpired as exc:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=1)
                raise AssertionError(f"{provider} {mode} exceeded {maximum}s") from exc
        elapsed = time.monotonic() - started
        assert process.returncode == 0, (provider, mode, process.returncode)
        response = json.loads(output_path.read_text(encoding="utf-8"))
        if capture_failure:
            assert "private capture failure detail" not in output_path.read_text(encoding="utf-8")
            assert "private capture failure detail" not in error_path.read_text(encoding="utf-8")
        assert elapsed < maximum, (provider, mode, elapsed)
        assert not list(root.glob("tmp*")), "Git capture file leaked"
        log_file = root / "logs" / "scan.log"
        return response, log_file.read_text(encoding="utf-8") if log_file.exists() else ""


def assert_incomplete(provider: str, mode: str, result: tuple[dict, str]) -> None:
    response, log = result
    rendered = json.dumps(response).lower()
    assert "incomplete" in rendered, (provider, mode, response)
    assert "clean" not in rendered, (provider, mode, response)
    assert '"status":"clean"' not in log, (provider, mode, log)
    assert '"status":"incomplete"' in log, (provider, mode, log)
    if mode == "block":
        if provider == "codex":
            assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
        elif provider == "gemini":
            assert response["decision"] == "deny"
        else:
            assert response["permissionDecision"] == "deny"


def main() -> None:
    provider = sys.argv[1]
    descendant_git = """#!/usr/bin/env python3
import os, sys, time
if sys.argv[1:3] == ['rev-parse', '--is-inside-work-tree']:
    if os.fork() == 0:
        time.sleep(10)
        os._exit(0)
    sys.stdout.write('true\\n')
    sys.stdout.flush()
    os._exit(0)
sys.exit(9)
"""
    partial_git = """#!/usr/bin/env python3
import sys, time
sys.stdout.write('true\\n')
sys.stdout.flush()
time.sleep(10)
"""
    oversized_git = """#!/usr/bin/env python3
import os, time
os.write(1, b'x' * (8388608 + 1))
time.sleep(10)
"""
    failed_git = "#!/usr/bin/env python3\nimport sys\nsys.stdout.write('true\\n')\nsys.exit(9)\n"
    malformed_git = """#!/usr/bin/env python3
import os, sys
args = sys.argv[1:]
if args[:2] == ['rev-parse', '--is-inside-work-tree']:
    print('true')
elif args[:2] == ['rev-parse', '--show-toplevel']:
    print(os.getcwd())
elif args[:3] == ['rev-parse', '--verify', 'HEAD']:
    sys.exit(9)
elif args[0] == 'diff':
    sys.stdout.write('partial-path')
else:
    sys.exit(9)
"""
    real_git = "#!/usr/bin/env python3\nimport os\nos.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *__import__('sys').argv[1:]])\n"
    for mode in ("block", "warn"):
        for fake_git, maximum in ((descendant_git, 3.0), (partial_git, 7.0),
                                  (oversized_git, 3.0), (failed_git, 3.0),
                                  (malformed_git, 3.0)):
            assert_incomplete(provider, mode, run_case(provider, mode, fake_git, maximum))
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, capture_failure=True,
        ))
        response, log = run_case(provider, mode, real_git)
        assert response == {}, (provider, mode, response)
        assert '"status":"clean"' in log, (provider, mode, log)
    print(f"PASS: {provider} scanner capture failures and no-HEAD success")


if __name__ == "__main__":
    main()

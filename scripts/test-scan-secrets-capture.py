#!/usr/bin/env python3
"""Exercise generated scanners through their JSON hook entry points."""

from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import time

from scanner_test_support import HOOKS, install_fake_git


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
    capture_failure: bool = False, committed: bool = False,
    unexpected_failure: bool = False, unexpected_input: bool = False, files: dict[str, bytes] | None = None,
    input_text: str | None = None, missing_git: bool = False,
    storage_fault: str = "", hostile_payload: bool = False, descriptor_fault: str = "",
    launch_fault: str = "",
) -> tuple[dict, str]:
    with tempfile.TemporaryDirectory(prefix="scan-capture-test-") as directory:
        root = Path(directory)
        repo = root / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        real_git = shutil.which("git")
        assert real_git is not None
        subprocess.run([real_git, "-C", str(repo), "init", "-q"], check=True)
        if committed:
            (repo / "README.md").write_text("safe fixture\n", encoding="utf-8")
            subprocess.run([real_git, "-C", str(repo), "add", "README.md"], check=True)
            subprocess.run([
                real_git, "-C", str(repo), "-c", "user.name=Scanner Test",
                "-c", "user.email=scanner@example.invalid", "-c", "commit.gpgsign=false",
                "commit", "-qm", "fixture",
            ], check=True)
        for name, content in (files or {}).items():
            (repo / name).write_bytes(content)
        output_path = root / "response.json"
        error_path = root / "stderr.txt"
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("AUDIT_", "OBSERVABILITY_", "COPILOT_OBSERVABILITY_",
                                      "GEMINI_OBSERVABILITY_"))}
        install_fake_git(root, env, fake_git, real_git=real_git)
        env.update({"SCAN_MODE": mode,
                    "SECRETS_LOG_DIR": str(root / "logs"), "TMPDIR": str(root),
                    "AUDIT_LOG": str(root / "audit.log"),
                    "OBSERVABILITY_LOG_PATH": str(root / "observability.jsonl"),
                    "OBSERVABILITY_TESTING": "1", "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CONFIG_GLOBAL": os.devnull})
        lock_handle = None
        if missing_git:
            env["PATH"] = str(root / "empty-bin")
        if storage_fault == "audit":
            (root / "barrier").write_text("safe")
            env["AUDIT_LOG"] = str(root / "barrier" / "audit.log")
        elif storage_fault == "unavailable":
            env["SECRETS_LOG_DIR"] = str(root / "absent" / "logs")
            # The directory exists but the current user cannot create log files.
            (root / "absent").mkdir()
            (root / "absent").chmod(0o500)
        elif storage_fault == "unsafe":
            (root / "logs").mkdir()
            (root / "logs" / "scan.log").mkdir()
        elif storage_fault == "configuration":
            env["AUDIT_LOG_MAX_BYTES"] = "/private/hostile-path token=FAKE_DIAGNOSTIC_TOKEN"
        elif storage_fault == "lock":
            import fcntl
            (root / "logs").mkdir()
            lock_handle = (root / "logs" / "scan.log.lock").open("wb")
            fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        started = time.monotonic()
        command = [sys.executable, "-I", "-S", "-B", str(HOOKS[provider])]
        if capture_failure or unexpected_failure or unexpected_input:
            error_type = "RuntimeError" if unexpected_failure or unexpected_input else "OSError"
            failure_target = "os.read" if unexpected_input else "tempfile.TemporaryFile"
            wrapper = (
                "import os, runpy, tempfile\n"
                "def fail(*args, **kwargs):\n"
                f"    raise {error_type}('/private/hostile-path token=FAKE_DIAGNOSTIC_TOKEN')\n"
                f"{failure_target} = fail\n"
                f"runpy.run_path({str(HOOKS[provider])!r}, run_name='__main__')\n"
            )
            command = [sys.executable, "-I", "-S", "-B", "-c", wrapper]
        if descriptor_fault:
            wrapper = (
                "import os, runpy\n"
                "from pathlib import Path\n"
                "original_open, original_read = os.open, os.read\n"
                "candidate = Path('race.txt')\n"
                "descriptors = set()\n"
                "changed = False\n"
                f"fault = {descriptor_fault!r}\n"
                "def open_candidate(path, flags, *args, **kwargs):\n"
                "    global changed\n"
                "    selected = os.fspath(path) == 'race.txt'\n"
                "    if selected and fault == 'fifo' and not changed:\n"
                "        candidate.unlink()\n"
                "        os.mkfifo(candidate)\n"
                "        changed = True\n"
                "    descriptor = original_open(path, flags, *args, **kwargs)\n"
                "    if selected:\n"
                "        descriptors.add(descriptor)\n"
                "    return descriptor\n"
                "def read_candidate(descriptor, size):\n"
                "    global changed\n"
                "    if descriptor in descriptors and not changed:\n"
                "        changed = True\n"
                "        if fault == 'growth':\n"
                "            with candidate.open('ab') as handle:\n"
                "                handle.write(b'x' * 8388609)\n"
                "        elif fault == 'replacement':\n"
                "            candidate.rename('original.txt')\n"
                "            candidate.write_bytes(b'safe replacement\\n')\n"
                "    chunk = original_read(descriptor, size)\n"
                "    if descriptor in descriptors and not chunk and fault == 'replay':\n"
                "        candidate.write_bytes(b'safe rewritten after acquisition\\n')\n"
                "    return chunk\n"
                "os.open, os.read = open_candidate, read_candidate\n"
                "os.supports_dir_fd.add(open_candidate)\n"
                f"runpy.run_path({str(HOOKS[provider])!r}, run_name='__main__')\n"
            )
            command = [sys.executable, "-I", "-S", "-B", "-c", wrapper]
        if launch_fault:
            wrapper = (
                "import errno, runpy, subprocess\n"
                f"fault = {launch_fault!r}\n"
                "original_popen = subprocess.Popen\n"
                "failures = 0\n"
                "def launch(args, *positional, **keyword):\n"
                "    global failures\n"
                "    if list(args[1:]) == ['rev-parse', '--verify', 'HEAD']:\n"
                "        failures += 1\n"
                "        if fault == 'native_once' and failures == 1:\n"
                "            import resource\n"
                "            before = resource.getrlimit(resource.RLIMIT_NPROC)\n"
                "            resource.setrlimit(resource.RLIMIT_NPROC, (0, before[1]))\n"
                "            try:\n"
                "                child = original_popen(args, *positional, **keyword)\n"
                "                child.wait(timeout=1)\n"
                "                raise RuntimeError('native process limit did not prevent launch')\n"
                "            finally:\n"
                "                current = resource.getrlimit(resource.RLIMIT_NPROC)\n"
                "                resource.setrlimit(resource.RLIMIT_NPROC, (before[0], current[1]))\n"
                "        if fault == 'eagain_deadline':\n"
                "            import time\n"
                "            time.sleep(5.05)\n"
                "            raise BlockingIOError(errno.EAGAIN, 'temporary launch failure')\n"
                "        if (fault == 'eagain_always' or (fault == 'eagain_once' and failures == 1)\n"
                "                or (fault == 'eagain_twice' and failures <= 2)):\n"
                "            raise BlockingIOError(errno.EAGAIN, '/private/hostile-path token=FAKE_DIAGNOSTIC_TOKEN')\n"
                "        if fault == 'permission':\n"
                "            raise PermissionError(errno.EACCES, '/private/hostile-path token=FAKE_DIAGNOSTIC_TOKEN')\n"
                "    return original_popen(args, *positional, **keyword)\n"
                "subprocess.Popen = launch\n"
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
                request = payload(provider, repo, mode)
                if hostile_payload:
                    request.update({"sessionId": "FAKE_DIAGNOSTIC_TOKEN", "session_id": "FAKE_DIAGNOSTIC_TOKEN",
                                    "timestamp": "/private/hostile-path token=FAKE_DIAGNOSTIC_TOKEN"})
                process.communicate((json.dumps(request) if input_text is None else input_text).encode(),
                                    timeout=maximum)
            except subprocess.TimeoutExpired as exc:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=1)
                raise AssertionError(f"{provider} {mode} exceeded {maximum}s") from exc
        if lock_handle is not None:
            lock_handle.close()
        if storage_fault == "unavailable":
            (root / "absent").chmod(0o700)
        elapsed = time.monotonic() - started
        assert process.returncode == 0, (provider, mode, process.returncode)
        response = json.loads(output_path.read_text(encoding="utf-8"))
        if capture_failure or unexpected_failure or unexpected_input:
            assert "/private/hostile-path token=FAKE_DIAGNOSTIC_TOKEN" not in output_path.read_text(encoding="utf-8")
            assert "/private/hostile-path token=FAKE_DIAGNOSTIC_TOKEN" not in error_path.read_text(encoding="utf-8")
        assert elapsed < maximum, (provider, mode, elapsed)
        assert not list(root.glob("tmp*")), "Git capture file leaked"
        log_file = root / "logs" / "scan.log"
        log = log_file.read_text(encoding="utf-8") if log_file.is_file() else ""
        for marker in ("/private/hostile-path", "FAKE_DIAGNOSTIC_TOKEN"):
            assert marker not in output_path.read_text() + error_path.read_text() + log
        if "incomplete" in json.dumps(response):
            assert str(repo) not in output_path.read_text() + error_path.read_text() + log
        return response, log


def assert_incomplete(provider: str, mode: str, result: tuple[dict, str],
                      cause: str, operation: str, logging: bool = True,
                      **details: int | float | str) -> None:
    response, log = result
    rendered = json.dumps(response).lower()
    assert "incomplete" in rendered, (provider, mode, response)
    assert cause in rendered, (provider, mode, cause, response)
    assert operation in rendered, (provider, mode, operation, response)
    assert "check" in rendered or "retry" in rendered, response
    if logging:
        record = json.loads(log.splitlines()[-1])
        assert record["diagnostic"] == {"cause": cause, "operation": operation, **details}, record
        assert record["note"].lower() in rendered, (response, record)
        assert record["action"] in rendered, (response, record)
        assert '"status":"clean"' not in log, (provider, mode, log)
        assert '"status":"incomplete"' in log, (provider, mode, log)
    else:
        assert not log, (provider, mode, log)
    if mode == "block":
        if provider == "codex":
            if "hookSpecificOutput" in response:
                assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
            else:
                assert response["decision"] == "block"
        elif provider == "gemini":
            assert response["decision"] == "deny"
        else:
            assert response["permissionDecision"] == "deny"


def main() -> None:
    provider = sys.argv[1]
    descendant_git = """import os, sys, time
if sys.argv[1:3] == ['rev-parse', '--is-inside-work-tree']:
    if os.fork() == 0:
        time.sleep(10)
        os._exit(0)
    sys.stdout.write('true\\n')
    sys.stdout.flush()
    os._exit(0)
sys.exit(9)
"""
    partial_git = """import sys, time
sys.stdout.write('true\\n')
sys.stdout.flush()
time.sleep(10)
"""
    oversized_git = """import os, time
os.write(1, b'x' * (8388608 + 1))
time.sleep(10)
"""
    failed_git = """import sys
sys.stderr.write('/private/hostile-path token=FAKE_DIAGNOSTIC_TOKEN')
sys.stdout.write('true\\n')
sys.exit(9)
"""
    malformed_git = """import os, sys
args = sys.argv[1:]
if args[:2] == ['rev-parse', '--is-inside-work-tree']:
    print('true')
elif args[:2] == ['rev-parse', '--show-toplevel']:
    print(os.getcwd())
elif args[0] == 'diff':
    sys.stdout.write('partial-path')
else:
    os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])
"""
    real_git = "import os\nos.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *__import__('sys').argv[1:]])\n"
    recovery_faults = ["eagain_once", "eagain_twice"]
    if sys.platform == "darwin":
        recovery_faults.append("native_once")
    for mode in ("block", "warn"):
        for fault in recovery_faults:
            response, log = run_case(provider, mode, real_git, launch_fault=fault,
                                     files={"fake.txt": ("gh" + "p_" + "A" * 36).encode()})
            assert "potential secrets detected" in json.dumps(response), (fault, response)
            assert json.loads(log.splitlines()[-1])["status"] == "findings", (fault, log)
            response, log = run_case(provider, mode, real_git, launch_fault=fault)
            expected = {"systemMessage": "scan-secrets: pass; 0 modified files"} if provider == "codex" and mode == "warn" else {}
            assert response == expected, (fault, response)
            assert json.loads(log.splitlines()[-1])["status"] == "clean", (fault, log)
        for fault, number, attempts in (("permission", errno.EACCES, 1),
                                        ("eagain_always", errno.EAGAIN, 3)):
            assert_incomplete(provider, mode, run_case(
                provider, mode, real_git, launch_fault=fault,
            ), "git_capture_failed", "git_head", capture_step="spawn", os_errno=number, attempts=attempts)
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, launch_fault="eagain_deadline", maximum=7.0,
        ), "git_timeout", "git_head", seconds=5)
    failed_head_git = """import os, sys
if sys.argv[1:] == ['rev-parse', '--verify', 'HEAD']:
    sys.exit(128)
os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *sys.argv[1:]])
"""
    failed_diff_git = """import os, sys
args = sys.argv[1:]
if args[0] == 'diff':
    flags = args[:args.index('--')]
    if '--name-only' in flags:
        if '--cached' not in flags:
            sys.stdout.buffer.write(b'--name-only\\0')
    else:
        sys.exit(9)
else:
    os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])
"""
    unsafe_candidate_git = """import os, sys
if sys.argv[1:] == ['ls-files', '-z', '--others', '--exclude-standard']:
    sys.stdout.buffer.write(b'../private/hostile-path token=FAKE_DIAGNOSTIC_TOKEN\\0')
else:
    os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *sys.argv[1:]])
"""
    missing_candidate_git = unsafe_candidate_git.replace(
        '../private/hostile-path token=FAKE_DIAGNOSTIC_TOKEN', 'missing-file.txt')
    slow_git = """import os, sys, time
time.sleep(3)
os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *sys.argv[1:]])
"""
    # Race at the public generated entrypoint: opening a swapped FIFO must
    # never wait for a writer, and growth must stop at the first extra byte.
    for mode in ("block", "warn"):
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, files={"race.txt": b"safe\n"}, descriptor_fault="fifo",
        ), "candidate_unsafe", "candidate_read")
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, files={"race.txt": b"safe\n"}, descriptor_fault="growth",
        ), "total_bytes_limit", "candidate_read", measured=8388609, limit=8388608)
        token = ("gh" + "p_" + "FAKE" * 9).encode()
        # Classification reads the complete protected snapshot before matching,
        # including split UTF-8 and late binary markers beyond the first chunk.
        response, log = run_case(provider, mode, real_git, files={
            "split.txt": b"x" * 65535 + "é".encode() + b" " + token,
            "late.bin": token + b" " + b"x" * 65536 + b"\0",
            "invalid.bin": b"x" * 65536 + b"\xff " + token,
        })
        record = json.loads(log.splitlines()[-1])
        assert record["status"] == "findings", record
        assert [finding["path"] for finding in record["findings"]] == [
            "invalid.bin", "late.bin", "split.txt"], record
        for fault in ("replacement", "replay"):
            response, log = run_case(provider, mode, real_git,
                                     files={"race.txt": token + b"\n"}, descriptor_fault=fault)
            assert "potential secrets detected" in json.dumps(response), (fault, response)
            record = json.loads(log.splitlines()[-1])
            assert record["status"] == "findings", (fault, record)
            assert record["findings"][0]["path"] == "race.txt", record
            assert token.decode() not in json.dumps(response) + log
    for mode in ("block", "warn"):
        for fake_git, maximum, cause, numbers in (
            (descendant_git, 3.0, "git_descendant_running", {}),
            (partial_git, 7.0, "git_timeout", {"seconds": 5}),
            (oversized_git, 3.0, "git_output_limit", {"measured": 8388609, "limit": 8388608}),
            (failed_git, 3.0, "git_failed", {"exit_status": 9}),
            (malformed_git, 3.0, "git_output_invalid", {}),
        ):
            operation = "git_candidates" if fake_git == malformed_git else "git_repository"
            assert_incomplete(provider, mode, run_case(provider, mode, fake_git, maximum),
                              cause, operation, **numbers)
        assert_incomplete(provider, mode, run_case(
            provider, mode, failed_diff_git, committed=True, files={"--name-only": b"safe\n"},
        ), "git_failed", "git_diff", exit_status=9)
        assert_incomplete(provider, mode, run_case(
            provider, mode, unsafe_candidate_git,
        ), "candidate_unsafe", "candidate_read")
        assert_incomplete(provider, mode, run_case(
            provider, mode, missing_candidate_git,
        ), "candidate_read_failed", "candidate_read")
        assert_incomplete(provider, mode, run_case(
            provider, mode, slow_git, maximum=11.0,
        ), "scan_timeout", "git_head", seconds=8)
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, capture_failure=True,
        ), "git_capture_failed", "git_repository", capture_step="temporary_file")
        assert_incomplete(provider, mode, run_case(
            provider, mode, failed_head_git, committed=True,
        ), "git_head_invalid", "git_head")
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, unexpected_failure=True,
        ), "internal_error", "git_repository")
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, unexpected_input=True,
        ), "internal_error", "input")
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, missing_git=True,
        ), "git_unavailable", "initialization")
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, storage_fault="audit",
        ), "audit_unavailable", "initialization")
        for invalid_input in ('[]', '{"private_token":"FAKE_DIAGNOSTIC_TOKEN",'):
            assert_incomplete(provider, mode, run_case(
                provider, mode, real_git, input_text=invalid_input,
            ), "input_invalid", "input")
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, files={"large.bin": b"x" * 8388609}, hostile_payload=True,
        ), "total_bytes_limit", "candidate_read", measured=8388609, limit=8388608)
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, files={f"file-{i}.txt": b"safe\n" for i in range(257)},
        ), "snapshot_count_limit", "git_candidates", measured=257, limit=256)
        assert_incomplete(provider, mode, run_case(
            provider, mode, real_git, maximum=7.0,
            files={f"file-{i}.bin": b"x" * 1048576 for i in range(9)},
        ), "total_bytes_limit", "candidate_read", measured=9437184, limit=8388608)
        for fault, cause, numbers in (("unsafe", "log_unsafe", {}),
                                      ("unavailable", "log_unavailable", {}),
                                      ("configuration", "log_configuration_invalid", {}),
                                      ("lock", "log_lock_timeout", {"seconds": 1})):
            assert_incomplete(provider, mode, run_case(
                provider, mode, real_git, storage_fault=fault,
            ), cause, "scan_log", logging=False, **numbers)
        assert_incomplete(provider, mode, run_case(
            provider, mode, failed_git, storage_fault="unsafe",
        ), "git_failed", "git_repository", logging=False, exit_status=9)
        response, log = run_case(provider, mode, real_git,
                                 files={"fake.txt": ("gh" + "p_" + "A" * 36).encode()})
        assert "potential secrets detected" in json.dumps(response), response
        assert '"status":"findings"' in log, log
        assert ("gh" + "p_" + "A" * 36) not in json.dumps(response) + log
        response, log = run_case(provider, mode, real_git)
        expected = {"systemMessage": "scan-secrets: pass; 0 modified files"} if provider == "codex" and mode == "warn" else {}
        assert response == expected, (provider, mode, response)
        assert '"status":"clean"' in log, (provider, mode, log)
    print(f"PASS: {provider} scanner capture failures and no-HEAD success")


if __name__ == "__main__":
    main()

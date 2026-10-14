#!/usr/bin/env python3
"""Exercise bounded stdin transport through generated public security hooks."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from tool_guard_corpus import decision as guardian_decision, script_path


def decision(provider: str, response: dict) -> str:
    if response.get("continue") is False or response.get("decision") == "block":
        return "deny"
    if response == {}:
        return "allow"
    return guardian_decision(provider, response)


ROOT = Path(__file__).resolve().parent.parent
PROVIDERS = ("copilot", "gemini", "codex")


class HookInputBoundsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = tempfile.TemporaryDirectory(prefix="hook-input-bounds-")
        self.addCleanup(self.fixture.cleanup)
        self.directory = Path(self.fixture.name)
        self.env = os.environ.copy()
        for name in ("SKIP_TOOL_GUARD", "TOOL_GUARD_ALLOWLIST", "SKIP_SECRETS_SCAN", "SECRETS_ALLOWLIST"):
            self.env.pop(name, None)
        subprocess.run(["git", "init", "-q", str(self.directory)], check=True)
        self.env.update(HOME=str(self.directory), OBSERVABILITY_TESTING="1",
                        OBSERVABILITY_LOG_PATH=str(self.directory / "observability.sqlite"),
                        TOOL_GUARD_LOG_DIR=str(self.directory / "guard"),
                        SECRETS_LOG_DIR=str(self.directory / "scanner"),
                        GUARD_MODE="block", SCAN_MODE="block")

    def start(self, provider: str, hook: str = "tool-guard") -> subprocess.Popen:
        path = script_path(ROOT, provider).with_name(hook + ".py")
        environment = {**self.env, "TOOL_GUARD_LOG_DIR": str(self.directory / (provider + "-guard")),
                       "SECRETS_LOG_DIR": str(self.directory / (provider + "-scanner"))}
        process = subprocess.Popen([sys.executable, "-B", str(path)], cwd=self.directory,
                                   env=environment, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        def cleanup() -> None:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=2)
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream is not None:
                    try:
                        stream.close()
                    except BrokenPipeError:
                        pass
        self.addCleanup(cleanup)
        return process

    def response(self, process: subprocess.Popen, timeout: float = 1.5) -> dict:
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.fail("hook waited beyond the transport watchdog with stdin retained")
        self.assertEqual(process.returncode, 0, process.stderr.read().decode())
        return json.loads(process.stdout.read())

    def test_missing_and_incomplete_retained_stdin_deny(self) -> None:
        for provider in PROVIDERS:
            for hook in ("tool-guard", "scan-secrets"):
                for prefix in (b"", b'{"tool_name":', b'{"x":"\xe2'):
                    with self.subTest(provider=provider, hook=hook, prefix=prefix):
                        process = self.start(provider, hook)
                        if prefix:
                            process.stdin.write(prefix)
                            process.stdin.flush()
                        self.assert_input_denial(provider, process)

    def test_trickle_has_a_nonextendable_total_deadline(self) -> None:
        for provider in PROVIDERS:
            for hook in ("tool-guard", "scan-secrets"):
                with self.subTest(provider=provider, hook=hook):
                    process = self.start(provider, hook)
                    started = time.monotonic()
                    process.stdin.write(b"{")
                    process.stdin.flush()
                    while process.poll() is None and time.monotonic() - started < 2.8:
                        try:
                            process.stdin.write(b" ")
                            process.stdin.flush()
                        except BrokenPipeError:
                            break
                        time.sleep(0.1)
                    self.assert_input_denial(provider, process, 0.2)
                    self.assertLess(time.monotonic() - started, 2.8)

    def test_raw_byte_depth_and_trailing_limits_deny(self) -> None:
        cases = (b'{"padding":"' + b"x" * (2 * 1024 * 1024),
                 b'{"padding":' + b"[" * 64,
                 b'{} trailing', b'{} {}', b'{"x":]}', b'{not json', b'{"x":1e}', b'{"x":"\\uZZZZ"}', b'{"x":"\xff"}')
        for provider in PROVIDERS:
            for hook in ("tool-guard", "scan-secrets"):
                for raw in cases:
                    with self.subTest(provider=provider, hook=hook, size=len(raw), prefix=raw[:20]):
                        process = self.start(provider, hook)
                        try:
                            process.stdin.write(raw)
                            process.stdin.flush()
                        except BrokenPipeError:
                            pass
                        self.assert_input_denial(provider, process)

    def payload(self, provider: str, tool: str, value: object) -> dict:
        if provider == "copilot":
            return {"hook_event_name": "preToolUse", "toolName": tool, "toolArgs": value}
        return {"hook_event_name": "PreToolUse" if provider == "codex" else "BeforeTool",
                "tool_name": tool, "tool_input": value}

    def test_complete_open_stdin_and_split_utf8_stay_usable(self) -> None:
        for provider in PROVIDERS:
            tool = {"copilot": "bash", "gemini": "run_shell_command", "codex": "Bash"}[provider]
            raw = json.dumps(self.payload(provider, tool, {"command": "echo '界 {} []'"}),
                             ensure_ascii=False).encode()
            split = raw.index("界".encode()) + 1
            for hook in ("tool-guard", "scan-secrets"):
                with self.subTest(provider=provider, hook=hook):
                    process = self.start(provider, hook)
                    process.stdin.write(raw[:split])
                    process.stdin.flush()
                    time.sleep(0.1)
                    self.assertIsNone(process.poll(), "valid UTF-8 prefix was rejected")
                    process.stdin.write(raw[split:] + b" \t\r\n")
                    process.stdin.flush()
                    self.assertEqual(decision(provider, self.response(process)), "allow")

    def test_maximum_escaped_native_input_keeps_metadata_headroom(self) -> None:
        for provider in PROVIDERS:
            if provider in ("copilot", "codex"):
                prefix = "*** Begin Patch\n*** Add File: example.txt\n+"
                suffix = "\n*** End Patch"
                size = 262144 - (7 if provider == "codex" else 0)
                patch = prefix + "\x01" * (size - len(prefix + suffix)) + suffix
                value = {"command": patch} if provider == "codex" else patch
                tool = "apply_patch"
            else:
                value = {"file_path": "example.txt", "content": "\x01" * (65536 - 27)}
                tool = "write_file"
            payload = self.payload(provider, tool, value)
            payload["session_id"] = "m" * (500 * 1024)
            raw = json.dumps(payload, separators=(",", ":")).encode()
            self.assertLess(len(raw), 2 * 1024 * 1024)
            with self.subTest(provider=provider, raw_bytes=len(raw)):
                process = self.start(provider)
                process.stdin.write(raw)
                process.stdin.flush()
                self.assertEqual(decision(provider, self.response(process)), "allow")

    def test_raw_ceiling_includes_buffered_trailing_whitespace(self) -> None:
        # A regular stdin fixture makes every trailing byte available at completion.
        # Producers writing after the reader observes an empty pipe are outside that boundary.
        for length, expected in ((2097152, "allow"), (2097153, "deny")):
            source = self.directory / ".git" / "input.json"
            source.write_bytes(b"{}" + b" " * (length - 2))
            for provider in PROVIDERS:
                for hook in ("tool-guard", "scan-secrets"):
                    path = script_path(ROOT, provider).with_name(hook + ".py")
                    with self.subTest(provider=provider, hook=hook, length=length), source.open("rb") as stream:
                        result = subprocess.run([sys.executable, "-B", str(path)], stdin=stream,
                                                capture_output=True, env={**self.env,
                                                    "TOOL_GUARD_LOG_DIR": str(self.directory / (provider + "-guard")),
                                                    "SECRETS_LOG_DIR": str(self.directory / (provider + "-scanner"))},
                                                cwd=self.directory, timeout=1.5)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(decision(provider, json.loads(result.stdout)), expected)

    def test_finite_invalid_input_does_not_pay_idle_timeout(self) -> None:
        for provider in PROVIDERS:
            process = self.start(provider)
            started = time.monotonic()
            process.stdin.write(b'{"incomplete":')
            process.stdin.close()
            self.assert_input_denial(provider, process, 0.45)
            self.assertLess(time.monotonic() - started, 0.45)

    def assert_input_denial(self, provider: str, process: subprocess.Popen, timeout: float = 1.5) -> None:
        response = self.response(process, timeout)
        self.assertEqual(decision(provider, response), "deny")
        safe_output = json.dumps(response)
        if str(process.args[-1]).endswith("scan-secrets.py"):
            self.assertIn("scan incomplete", safe_output)
            self.assertIn("input_invalid/input", safe_output)
        else:
            self.assertIn("invalid hook input JSON", safe_output)

    def test_depth_boundary_and_fragmented_json_number(self) -> None:
        for provider in PROVIDERS:
            value = 1
            for _ in range(63):
                value = [value]
            raw = json.dumps({"padding": value}).encode()
            process = self.start(provider, "scan-secrets")
            process.stdin.write(raw)
            process.stdin.flush()
            self.assertEqual(decision(provider, self.response(process)), "allow")
            tool = {"copilot": "bash", "gemini": "run_shell_command", "codex": "Bash"}[provider]
            raw = json.dumps(self.payload(provider, tool, {"command": "echo safe"})).encode()
            process = self.start(provider)
            process.stdin.write(raw[:-1] + b', "padding":1e')
            process.stdin.flush()
            time.sleep(0.1)
            self.assertIsNone(process.poll())
            process.stdin.write(b"2}")
            process.stdin.flush()
            self.assertEqual(decision(provider, self.response(process)), "allow")

    def test_concurrent_trailing_whitespace_cannot_extend_drain(self) -> None:
        import threading

        for provider in PROVIDERS:
            process = self.start(provider)
            stopped = threading.Event()
            def produce() -> None:
                try:
                    process.stdin.write(b"{}")
                    process.stdin.flush()
                    while not stopped.is_set():
                        process.stdin.write(b" " * 65536)
                        process.stdin.flush()
                except BrokenPipeError:
                    pass
            writer = threading.Thread(target=produce, daemon=True)
            writer.start()
            try:
                response = self.response(process, 2.8)
                # An empty readiness snapshot may finish before a concurrent write.
                # Either native outcome is safe; continued buffered input must be bounded.
                self.assertIn(decision(provider, response), ("allow", "deny"))
            finally:
                stopped.set()
                writer.join(timeout=1)
                self.assertFalse(writer.is_alive(), "producer remained blocked after hook exit")

if __name__ == "__main__":
    unittest.main()

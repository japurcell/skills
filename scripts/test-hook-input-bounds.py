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
from unittest import mock

from tool_guard_corpus import decision as guardian_decision, script_path
from hook_test_support import fresh_common, raw_tool_envelope


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
        return raw_tool_envelope(provider, tool, value)

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
                size = 1048576
                patch = prefix + "\x01" * (size - len(prefix + suffix)) + suffix
                value = {"command": patch} if provider == "codex" else patch
                tool = "apply_patch"
            else:
                value = {"file_path": "example.txt", "content": "\x01" * 1048576}
                tool = "write_file"
            payload = self.payload(provider, tool, value)
            payload["session_id"] = "m" * 16000
            raw = json.dumps(payload, separators=(",", ":")).encode()
            self.assertLess(len(raw), 6889472)
            with self.subTest(provider=provider, raw_bytes=len(raw)):
                process = self.start(provider)
                process.stdin.write(raw)
                process.stdin.flush()
                self.assertEqual(decision(provider, self.response(process)), "allow")
            # More transport headroom never grants unbounded envelope metadata.
            payload["session_id"] = "m" * (500 * 1024)
            process = self.start(provider)
            process.stdin.write(json.dumps(payload, separators=(",", ":")).encode())
            process.stdin.flush()
            response = self.response(process)
            self.assertEqual(decision(provider, response), "deny")
            self.assertIn("envelope_metadata_bytes", json.dumps(response))

    def test_raw_ceiling_includes_buffered_trailing_whitespace(self) -> None:
        # A regular stdin fixture makes every trailing byte available at completion.
        # Producers writing after the reader observes an empty pipe are outside that boundary.
        for hook, ceiling in (("tool-guard", 6889472), ("scan-secrets", 2097152)):
            for length, expected in ((ceiling, "allow"), (ceiling + 1, "deny")):
                source = self.directory / ".git" / "input.json"
                source.write_bytes(b"{}" + b" " * (length - 2))
                for provider in PROVIDERS:
                    path = script_path(ROOT, provider).with_name(hook + ".py")
                    with self.subTest(provider=provider, hook=hook, length=length), source.open("rb") as stream:
                        result = subprocess.run([sys.executable, "-B", str(path)], stdin=stream,
                                                capture_output=True, env={**self.env,
                                                    "TOOL_GUARD_LOG_DIR": str(self.directory / (provider + "-guard")),
                                                    "SECRETS_LOG_DIR": str(self.directory / (provider + "-scanner"))},
                                                cwd=self.directory, timeout=1.5)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(decision(provider, json.loads(result.stdout)), expected)
                        if hook == "tool-guard" and expected == "deny":
                            self.assertIn("6889473 bytes exceeds limit 6889472 bytes", result.stdout.decode())

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

    def test_structural_escape_splits_preserve_complete_native_decisions(self) -> None:
        # Put structure-looking data before the operation. A premature boundary
        # must never hide the later executable control from either public hook.
        for provider in PROVIDERS:
            tool = {"copilot": "bash", "gemini": "run_shell_command", "codex": "Bash"}[provider]
            for content in ('backslash\\ordinary {} []', 'backslash\\"quote {} []',
                            'double\\\\end []', '界' + 'ordinary' * 10000):
                payload = {"padding": content, **self.payload(provider, tool, {"command": "echo safe"})}
                raw = json.dumps(payload, ensure_ascii=False).encode()
                self.assertEqual(json.loads(raw), payload)
                marker = raw.index(b"\\") if b"\\" in raw else raw.index("界".encode())
                for split in (marker + 1, marker + 2):
                    for hook in ("tool-guard", "scan-secrets"):
                        with self.subTest(provider=provider, hook=hook, content=content[:25], split=split):
                            process = self.start(provider, hook)
                            process.stdin.write(raw[:split])
                            process.stdin.flush()
                            time.sleep(0.08)
                            self.assertIsNone(process.poll(), "valid object prefix was rejected or completed")
                            process.stdin.write(raw[split:])
                            process.stdin.flush()
                            response = self.response(process)
                            exceeds_guard_metadata = hook == "tool-guard" and len(content.encode()) > 32768
                            self.assertEqual(decision(provider, response), "deny" if exceeds_guard_metadata else "allow")
                            if exceeds_guard_metadata:
                                self.assertIn("envelope_metadata_bytes", json.dumps(response))

            # A valid string containing a literal escaped quote cannot hide the
            # dangerous field that follows it in the same object.
            payload = {"padding": '\\"{}', **self.payload(provider, tool,
                       {"command": "git push" + " --force origin main"})}
            raw = json.dumps(payload).encode()
            split = raw.index(b"\\") + 1
            process = self.start(provider)
            process.stdin.write(raw[:split])
            process.stdin.flush()
            time.sleep(0.08)
            self.assertIsNone(process.poll())
            process.stdin.write(raw[split:])
            process.stdin.flush()
            response = self.response(process)
            self.assertEqual(decision(provider, response), "deny")
            self.assertIn("force_push_protected_branch", json.dumps(response))


class JsonCollectionParityTests(unittest.TestCase):
    def test_json_authority_and_explicit_depth_policy_across_chunk_widths(self) -> None:
        common = fresh_common(ROOT, "parity_common")
        strings = ("", "ordinary" * 10000, "界é", "{}[]", 'quote"end',
                   "\\", "\\a", '\\"', "\\\\", "\\\\a", '\\\\"', "\\u1234", "\n\t")
        inputs = [json.dumps({"value": text, "after": [{"x": 1}]}, ensure_ascii=ascii_only).encode()
                  for text in strings for ascii_only in (True, False)]
        inputs += [b" \t\r\n" + raw + b" \t\r\n" for raw in inputs]
        for depth in (63, 64, 65):
            inputs.append(b'{"value":' + b"[" * (depth - 1) + b"0" + b"]" * (depth - 1) + b"}")
        valid = list(inputs)
        inputs += [raw[:-1] for raw in valid]
        inputs += [raw + suffix for raw in valid[:26] for suffix in (b"x", b"{}", b"\x0b")]
        inputs += [b"[]", b'"{}"', b'x{}', b'{"x":]}', b'{"x":1e}',
                   b'{"x":"\\uZZZZ"}', b'{"x":"\xff"}', b'{"x":"unescaped\n"}']

        def max_depth(value):
            if isinstance(value, dict):
                return 1 + max((max_depth(child) for child in value.values()), default=0)
            if isinstance(value, list):
                return 1 + max((max_depth(child) for child in value), default=0)
            return 0

        for raw in inputs:
            try:
                expected = json.loads(raw)
                accepted = isinstance(expected, dict) and max_depth(expected) <= 64
            except (ValueError, UnicodeError):
                accepted = False
            for width in (1, 2, 3, 7, 64, 65536):
                chunks = [raw[offset:offset + width] for offset in range(0, len(raw), width)] + [b""]
                with self.subTest(size=len(raw), prefix=raw[:30], width=width), mock.patch.object(
                    common, "_read_stdin_chunk", side_effect=chunks
                ):
                    if accepted:
                        self.assertEqual(common.read_json_input(), expected)
                    else:
                        with self.assertRaises(ValueError):
                            common.read_json_input()

@unittest.skipIf(os.name == "nt", "POSIX flags; Windows uses PeekNamedPipe")
class StdinChunkTests(unittest.TestCase):
    """The approved descriptor adapter seam complements public pipe tests."""

    def setUp(self) -> None:
        self.common = fresh_common(ROOT, "bounded_common")
        self.reader, self.writer = os.pipe()
        self.addCleanup(os.close, self.reader)
        self.addCleanup(os.close, self.writer)

    def test_immediate_data_restores_original_flags_without_waiting(self) -> None:
        for blocking in (True, False):
            with self.subTest(blocking=blocking):
                os.set_blocking(self.reader, blocking)
                os.write(self.writer, b"chunk")
                with mock.patch.object(self.common, "_stdin_is_ready", side_effect=AssertionError("unnecessary wait")):
                    self.assertEqual(self.common._read_stdin_chunk(self.reader, 5, 0.5), b"chunk")
                self.assertEqual(os.get_blocking(self.reader), blocking)

    def test_eagain_timeout_is_distinct_from_eof_and_restores_flags(self) -> None:
        for blocking in (True, False):
            with self.subTest(blocking=blocking):
                os.set_blocking(self.reader, blocking)
                with mock.patch.object(self.common, "_stdin_is_ready", return_value=False) as ready:
                    self.assertIsNone(self.common._read_stdin_chunk(self.reader, 5, 0.125))
                ready.assert_called_once_with(self.reader, 0.125)
                self.assertEqual(os.get_blocking(self.reader), blocking)
        reader, writer = os.pipe()
        os.close(writer)
        try:
            self.assertEqual(self.common._read_stdin_chunk(reader, 5, 0), b"")
            self.assertTrue(os.get_blocking(reader))
        finally:
            os.close(reader)

    def test_eagain_wait_then_read_restores_flags(self) -> None:
        def ready(fd, timeout):
            self.assertFalse(os.get_blocking(fd), "fallback read must remain nonblocking")
            self.assertEqual(timeout, 0.25)
            os.write(self.writer, b"ready")
            return True
        with mock.patch.object(self.common, "_stdin_is_ready", side_effect=ready) as wait:
            self.assertEqual(self.common._read_stdin_chunk(self.reader, 5, 0.25), b"ready")
        wait.assert_called_once()
        self.assertTrue(os.get_blocking(self.reader))

    def test_read_and_readiness_errors_restore_both_original_flags(self) -> None:
        for blocking in (True, False):
            for failure in ("read", "readiness", "read_after_ready"):
                with self.subTest(blocking=blocking, failure=failure):
                    os.set_blocking(self.reader, blocking)
                    reads = ([OSError("read failed")] if failure == "read" else
                             [BlockingIOError(), OSError("ready read failed")])
                    wait = OSError("readiness failed") if failure == "readiness" else None
                    with mock.patch.object(self.common.os, "read", side_effect=reads), mock.patch.object(
                        self.common, "_stdin_is_ready", return_value=True, side_effect=wait
                    ), self.assertRaises(OSError):
                        self.common._read_stdin_chunk(self.reader, 5, 0.125)
                    self.assertEqual(os.get_blocking(self.reader), blocking)

    def test_expired_trailing_drain_never_attempts_another_read(self) -> None:
        with mock.patch.object(self.common, "_read_stdin_chunk", side_effect=AssertionError("deadline expired")):
            with self.assertRaisesRegex(ValueError, "input deadline exceeded"):
                self.common._read_available_stdin_bytes(self.reader, deadline=time.monotonic() - 1)


class WindowsReadinessContractTests(unittest.TestCase):
    def test_windows_adapter_keeps_readiness_authority_without_posix_flags(self) -> None:
        common = fresh_common(ROOT, "windows_common")
        for ready in (False, True):
            with self.subTest(ready=ready), mock.patch.object(common.os, "name", "nt"), mock.patch.object(
                common, "_stdin_is_ready", return_value=ready
            ) as wait, mock.patch.object(common.os, "read", return_value=b"") as read, mock.patch.object(
                common.os, "get_blocking", side_effect=AssertionError("POSIX flag API used")
            ):
                self.assertEqual(common._read_stdin_chunk(42, 17, 0.125), b"" if ready else None)
                wait.assert_called_once_with(42, 0.125)
                if ready:
                    read.assert_called_once_with(42, 17)
                else:
                    read.assert_not_called()


if __name__ == "__main__":
    unittest.main()

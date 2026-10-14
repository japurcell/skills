#!/usr/bin/env python3
"""Streaming scanner capacity and semantics through generated JSON entrypoints."""
from __future__ import annotations
import importlib.util
import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("merge_fixture", Path(__file__).with_name("test-scan-secrets-merge.py"))
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)

class StreamingScannerTests(unittest.TestCase):
    def setUp(self):
        fixture.MergeScannerTests.setUp(self)
        self.env["HOME"] = str(self.root)
    git = fixture.MergeScannerTests.git
    scan = fixture.MergeScannerTests.scan
    assert_outcome = fixture.MergeScannerTests.assert_outcome

    def findings(self, provider, expected, scope="diff"):
        response, record = self.scan(provider, "block", scope)
        self.assertEqual(record["status"], "findings", record)
        self.assertTrue(response)
        self.assertEqual([(row["pattern"], row["line"], row["redactedMatch"])
                          for row in record["findings"]], expected)
        return record

    def test_exact_aggregate_capacity_and_first_overflow_worktree_and_index(self):
        path = self.repo / "capacity.txt"
        path.write_bytes(b"q" * 8388608)
        for provider in fixture.PROVIDERS:
            self.assert_outcome(provider, "block", "diff", "clean")
        with path.open("ab") as output:
            output.write(b"q")
        for provider in fixture.PROVIDERS:
            self.assert_outcome(provider, "block", "diff", "incomplete", cause="total_bytes_limit")
            _, record = self.scan(provider)
            self.assertEqual(record["diagnostic"]["measured"], 8388609)
            self.assertEqual(record["diagnostic"]["limit"], 8388608)
        with path.open("r+b") as output:
            output.truncate(8388608)
        self.git("add", "--all")
        # Exact-cap index bodies cannot fit batch framing. Raw OID capture must
        # remain valid and framing must never consume logical candidate bytes.
        for provider in fixture.PROVIDERS:
            self.assert_outcome(provider, "block", "staged", "clean")
        with path.open("ab") as output:
            output.write(b"q")
        self.git("add", "--all")
        for provider in fixture.PROVIDERS:
            self.assert_outcome(provider, "block", "staged", "incomplete", cause="total_bytes_limit")

    def test_nonoverlap_restart_and_byte_first_diff_unicode(self):
        path = self.repo / "semantic.txt"
        path.write_text("baseline\n")
        self.git("add", "--all")
        self.git("commit", "-qm", "baseline")
        path.write_text("AKIA" * 6 + " ghp_ghp_" + "A" * 36
                        + "\u2028github_pat_" + "B" * 20 + "\n")
        for provider in fixture.PROVIDERS:
            self.findings(provider, [("github_classic_pat", 1, "ghp_...AAAA"),
                                     ("github_fine_grained_pat", 1, "gith...BBBB"),
                                     ("aws_access_key", 1, "AKIA...AKIA")])
        self.git("add", "--all")
        path.write_text("safe replacement\n")
        for provider in fixture.PROVIDERS:
            self.findings(provider, [("github_classic_pat", 1, "ghp_...AAAA"),
                                     ("aws_access_key", 1, "AKIA...AKIA"),
                                     ("github_fine_grained_pat", 2, "gith...BBBB")], scope="staged")

    def test_every_token_split_at_acquisition_boundary_and_eof(self):
        tokens = [("github_classic_pat", "ghp_" + "A" * 36, "ghp_...AAAA"),
                  ("github_fine_grained_pat", "github_pat_" + "B" * 20, "gith...BBBB"),
                  ("aws_access_key", "AKIA" + "C" * 16, "AKIA...CCCC"),
                  ("stripe_live_key", "sk_live_" + "D" * 16, "sk_l...DDDD"),
                  ("slack_token", "xoxb-" + "E" * 10, "xoxb...EEEE")]
        path = self.repo / "splits.txt"
        for name, token, redaction in tokens:
            raw = bytearray()
            for split in range(len(token) + 1):
                distance = (65536 - split - len(raw)) % 65536
                raw.extend(b"q" * distance + token.encode() + b"/\n")
            raw.extend(token.encode())
            path.write_bytes(raw)
            expected = [(name, line, redaction) for line in range(1, len(token) + 3)]
            for provider in fixture.PROVIDERS:
                with self.subTest(provider=provider, pattern=name):
                    self.findings(provider, expected)

    def test_greedy_extension_exact_allowlist_and_pattern_order(self):
        short = "github_pat_" + "B" * 20
        (self.repo / "greedy.txt").write_text(short + "\nAKIA" + "C" * 16 + " "
                                             + short + "Z" * 9000, encoding="utf-8")
        self.env["SECRETS_ALLOWLIST"] = json.dumps([
            {"tool": "scan_secrets", "input": "greedy.txt:1:github_fine_grained_pat:" + short},
            {"tool": "scan_secrets", "input": "greedy.txt:2:github_fine_grained_pat:" + short}])
        for provider in fixture.PROVIDERS:
            self.findings(provider, [("github_fine_grained_pat", 2, "gith...ZZZZ"),
                                     ("aws_access_key", 2, "AKIA...CCCC")])

    def test_text_separator_utf8_crlf_and_invalid_replacement(self):
        token = fixture.FAKE_TOKEN.encode()
        (self.repo / "separators.txt").write_bytes(b"q" * 65535 + b"\r\n" + token)
        for provider in fixture.PROVIDERS:
            self.findings(provider, [("github_classic_pat", 2, "ghp_...FAKE")])
        raw = b"q" * 65535 + "é".encode() + b"\r\n" + token
        separators = ["\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"]
        for separator in separators:
            raw += separator.encode() + token
        raw += b"\xff\r\n" + token
        (self.repo / "separators.txt").write_bytes(raw)
        for provider in fixture.PROVIDERS:
            self.findings(provider, [("github_classic_pat", line, "ghp_...FAKE")
                                     for line in range(2, 12)])

    def test_late_binary_markers_force_full_snapshot_projection(self):
        path = self.repo / "binary.bin"
        path.write_bytes(fixture.FAKE_TOKEN.encode() + b"\n" + b"q" * 131072)
        self.git("add", "--all")
        self.git("commit", "-qm", "unchanged token")
        for marker in (b"\0", b"\xff"):
            path.write_bytes(fixture.FAKE_TOKEN.encode() + b"\n" + b"q" * 131072
                             + marker + b"\n" + fixture.FAKE_TOKEN.encode())
            for provider in fixture.PROVIDERS:
                self.findings(provider, [("github_classic_pat", 1, "ghp_...FAKE"),
                                         ("github_classic_pat", 3, "ghp_...FAKE")])

    def test_report_caps_and_token_after_many_short_lines(self):
        token = fixture.FAKE_TOKEN
        (self.repo / "dense.txt").write_text("x\n" * 100000 + (token + "\n") * 1001)
        for provider in fixture.PROVIDERS:
            record = self.findings(provider, [("github_classic_pat", line, "ghp_...FAKE")
                                              for line in range(100001, 100101)])
            self.assertEqual(record["omittedFindings"], 900)
            self.assertTrue(record["findingsTruncated"])

    def test_credential_path_precedes_tokens_and_report_is_shared_across_candidates(self):
        token = fixture.FAKE_TOKEN
        sensitive = self.repo / ".aws/credentials"
        sensitive.parent.mkdir()
        sensitive.write_text(token + "\n")
        (self.repo / "z.txt").write_text((token + "\n") * 1001)
        for provider in fixture.PROVIDERS:
            record = self.findings(provider, [
                ("credential_path", 1, "[SENSITIVE PATH]"),
                ("github_classic_pat", 1, "ghp_...FAKE"),
                *[("github_classic_pat", line, "ghp_...FAKE") for line in range(1, 99)]])
            self.assertEqual(record["omittedFindings"], 900)
            self.assertEqual([row["path"] for row in record["findings"][:2]],
                             [".aws/credentials", ".aws/credentials"])

    def test_benign_long_single_line_and_empty_newline_dense_allow(self):
        path = self.repo / "benign.txt"
        for raw in (b"q" * 2030848, b"\n" * 8388608):
            path.write_bytes(raw)
            for provider in fixture.PROVIDERS:
                self.assert_outcome(provider, "block", "diff", "clean")

    def test_malformed_diff_tail_is_validated_after_finding_cap(self):
        (self.repo / "changed.txt").write_text("baseline\n")
        self.git("add", "--all")
        self.git("commit", "-qm", "baseline")
        (self.repo / "changed.txt").write_text("changed\n")
        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        wrapper = fake_bin / "git"
        wrapper.write_text(f"#!{sys.executable}\n"
            "import os, sys\n"
            "args = sys.argv[1:]\n"
            "if args[0] == 'diff' and '--name-only' not in args:\n"
            "    token = ('gh' + 'p_' + 'FAKE' * 9).encode()\n"
            "    sys.stdout.buffer.write(b'diff --git a/p b/p\\n@@ -1 +1 @@\\n+'"
            " + (token + b' ') * 1001 + b'\\nunexpected tail\\n')\n"
            "else:\n"
            "    os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])\n")
        wrapper.chmod(0o755)
        self.env.update(PATH=str(fake_bin) + os.pathsep + self.env["PATH"], REAL_GIT=str(self.git_path))
        for provider in fixture.PROVIDERS:
            self.assert_outcome(provider, "block", "diff", "incomplete", cause="git_output_invalid")

    def test_input_time_and_git_work_share_nonextendable_deadline(self):
        (self.repo / "pending.txt").write_text("safe\n")
        fake_bin = self.root / "slow-bin"
        fake_bin.mkdir()
        wrapper = fake_bin / "git"
        wrapper.write_text(f"#!{sys.executable}\n"
            "import os, sys, time\nfrom pathlib import Path\n"
            "count = Path(os.environ['COUNT_FILE'])\n"
            "n = int(count.read_text()) if count.exists() else 0\n"
            "count.write_text(str(n + 1))\n"
            "if n < 4: time.sleep(1.9)\n"
            "os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *sys.argv[1:]])\n")
        wrapper.chmod(0o755)
        for provider in fixture.PROVIDERS:
            log = self.root / ("deadline-" + provider)
            log.mkdir()
            env = {**self.env, "HOME": str(self.root), "OBSERVABILITY_TESTING": "1",
                   "SCAN_MODE": "block", "SCAN_SCOPE": "diff",
                   "PATH": str(fake_bin) + os.pathsep + self.env["PATH"],
                   "REAL_GIT": str(self.git_path), "COUNT_FILE": str(log / "count"),
                   "SECRETS_LOG_DIR": str(log), "AUDIT_LOG": str(log / "audit.log"),
                   "OBSERVABILITY_LOG_PATH": str(log / "obs.jsonl")}
            if provider == "copilot":
                payload = {"hook_event_name": "preToolUse", "toolName": "bash",
                           "toolArgs": {"command": "git status"}}
            else:
                payload = {"hook_event_name": "BeforeTool" if provider == "gemini" else "PreToolUse",
                           "tool_name": "run_shell_command" if provider == "gemini" else "exec_command",
                           "tool_input": {"command": "git status"}, "cwd": str(self.repo)}
            process = subprocess.Popen([sys.executable, "-I", "-S", "-B", str(fixture.HOOKS[provider])],
                cwd=self.repo, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                process.stdin.write(b"{")
                process.stdin.flush()
                for _ in range(7):
                    time.sleep(0.2)
                    process.stdin.write(b" ")
                    process.stdin.flush()
                output, error = process.communicate(json.dumps(payload).encode()[1:], timeout=12)
                self.assertEqual(process.returncode, 0, error)
                self.assertTrue(json.loads(output))
                record = json.loads((log / "scan.log").read_text().splitlines()[-1])
                self.assertEqual(record["status"], "incomplete", record)
                self.assertEqual(record["diagnostic"]["cause"], "scan_timeout", record)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate()

    def test_reported_size_short_nonempty_dense_lines_allow(self):
        (self.repo / "dense.txt").write_bytes(b"x\n" * 1015424)
        for provider in fixture.PROVIDERS:
            with self.subTest(provider=provider):
                self.assert_outcome(provider, "block", "diff", "clean")

    def test_single_2030848_byte_safe_candidate_allows(self):
        (self.repo / "large.txt").write_bytes(b"safe text\n" * 203084 + b"safe tex")
        self.assertEqual((self.repo / "large.txt").stat().st_size, 2030848)
        for provider in fixture.PROVIDERS:
            with self.subTest(provider=provider, state="untracked"):
                self.assert_outcome(provider, "block", "diff", "clean")
        self.git("add", "--all")
        self.git("commit", "-qm", "large baseline")
        with (self.repo / "large.txt").open("ab") as handle:
            handle.write(b"benign edit!\n")
        for provider in fixture.PROVIDERS:
            with self.subTest(provider=provider, state="tracked"):
                self.assert_outcome(provider, "block", "diff", "clean")

if __name__ == "__main__":
    unittest.main()

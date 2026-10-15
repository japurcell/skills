#!/usr/bin/env python3
"""Streaming scanner capacity and semantics through generated JSON entrypoints."""
from __future__ import annotations
import json
import subprocess
import sys
import time
import unittest

import scanner_test_support as fixture
from scanner_test_support import ScannerFixtureMixin, scanner_tool_payload

class StreamingScannerTests(ScannerFixtureMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.env["HOME"] = str(self.root)

    def findings(self, provider, expected, scope="diff", status="findings"):
        response, record = self.scan(provider, "block", scope)
        self.assertEqual(record["status"], status, record)
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
                                              for line in range(100001, 100101)], status="incomplete")
            self.assertEqual(record["omittedFindings"], 900)
            self.assertTrue(record["findingsTruncated"])

    def test_result_coverage_distinguishes_retention_from_inspection_stop(self):
        path = self.repo / "coverage.txt"
        path.write_text((fixture.FAKE_TOKEN + "\n") * 101)
        for provider in fixture.PROVIDERS:
            _, record = self.scan(provider)
            self.assertEqual(record["scanResult"]["outcome"], "complete_findings")
            self.assertTrue(record["scanResult"]["coverage_complete"])
            self.assertEqual(record["scanResult"]["counts"]["processed_findings"], 101)
        path.write_text((fixture.FAKE_TOKEN + "\n") * 1001)
        for provider in fixture.PROVIDERS:
            _, record = self.scan(provider)
            self.assertEqual(record["status"], "incomplete")
            self.assertEqual(record["scanResult"]["outcome"], "incomplete")
            self.assertFalse(record["scanResult"]["coverage_complete"])
            self.assertEqual(record["diagnostic"]["cause"], "findings_limit")
            self.assertEqual(len(record["findings"]), 100)
            self.assertEqual(record["security_outcome"], "findings")

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
                *[("github_classic_pat", line, "ghp_...FAKE") for line in range(1, 99)]], status="incomplete")
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
        self.install_fake_git(
            "import os, sys\n"
            "args = sys.argv[1:]\n"
            "if args[0] == 'diff' and '--name-only' not in args:\n"
            "    token = ('gh' + 'p_' + 'FAKE' * 9).encode()\n"
            "    sys.stdout.buffer.write(b'diff --git a/p b/p\\n@@ -1 +1 @@\\n+'"
            " + (token + b' ') * 1001 + b'\\nunexpected tail\\n')\n"
            "else:\n"
            "    os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])\n")
        for provider in fixture.PROVIDERS:
            self.assert_outcome(provider, "block", "diff", "incomplete", cause="git_output_invalid")

    def test_diff_matches_captured_worktree_even_when_path_changes_before_git_diff(self):
        path = self.repo / "captured.txt"
        path.write_text("baseline\n")
        self.git("add", "--all")
        self.git("commit", "-qm", "baseline")
        self.install_fake_git(
            "import os, sys\nfrom pathlib import Path\n"
            "args = sys.argv[1:]\n"
            "if args[0] == 'diff' and '--name-only' not in args:\n"
            "    Path('captured.txt').write_text('baseline\\n')\n"
            "os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])\n",
            directory="mutable-diff-bin")
        for provider in fixture.PROVIDERS:
            path.write_text(fixture.FAKE_TOKEN + "\n")
            self.assert_outcome(provider, "block", "diff", "findings", "captured.txt")
            self.assertEqual(path.read_text(), "baseline\n")

    def test_worktree_diff_baseline_is_pinned_before_candidate_capture(self):
        from unittest import mock
        path = self.repo / "captured.txt"
        path.write_text("baseline\n")
        self.git("add", "--all")
        self.git("commit", "-qm", "baseline")
        base = self.git("rev-parse", "HEAD").stdout.strip()
        path.write_text(fixture.FAKE_TOKEN + "\n")
        secret_oid = self.git("hash-object", "-w", "captured.txt").stdout.strip()
        for provider in fixture.PROVIDERS:
            self.git("reset", "-q", base, "--", "captured.txt")
            wrapper = self.root / (provider + "-baseline.py")
            wrapper.write_text(
                "import os, runpy, subprocess\n"
                "original_open, original_read = os.open, os.read\n"
                "selected = set()\nchanged = False\n"
                "def opening(path, flags, *args, **kwargs):\n"
                "    fd = original_open(path, flags, *args, **kwargs)\n"
                "    if os.fspath(path) == 'captured.txt': selected.add(fd)\n"
                "    return fd\n"
                "def reading(fd, size):\n"
                "    global changed\n"
                "    chunk = original_read(fd, size)\n"
                "    if fd in selected and not chunk and not changed:\n"
                "        changed = True\n"
                "        subprocess.run(" + repr([str(self.git_path), "update-index", "--cacheinfo", "100644," + secret_oid + ",captured.txt"]) + ", check=True)\n"
                "    return chunk\n"
                "os.open, os.read = opening, reading\n"
                "os.supports_dir_fd.add(opening)\n"
                "runpy.run_path(" + repr(str(fixture.HOOKS[provider])) + ", run_name='__main__')\n")
            with mock.patch.dict(fixture.HOOKS, {provider: wrapper}):
                self.assert_outcome(provider, "block", "diff", "findings", "captured.txt")

    def test_staged_diff_baseline_is_pinned_before_candidate_capture(self):
        path = self.repo / "captured.txt"
        path.write_text("baseline\n")
        self.git("add", "--all")
        self.git("commit", "-qm", "baseline")
        base = self.git("rev-parse", "HEAD").stdout.strip()
        path.write_text(fixture.FAKE_TOKEN + "\n")
        self.git("add", "--all")
        tree = self.git("write-tree").stdout.strip()
        secret_commit = self.git("commit-tree", tree, "-p", base, "-m", "fixture").stdout.strip()
        self.install_fake_git(
            "import os, subprocess, sys\n"
            "args = sys.argv[1:]\n"
            "if args[:2] == ['cat-file', '--batch-check']:\n"
            "    result = subprocess.run([os.environ['REAL_GIT'], *args], input=sys.stdin.buffer.read(), capture_output=True)\n"
            "    subprocess.run([os.environ['REAL_GIT'], 'update-ref', 'HEAD', " + repr(secret_commit) + "], check=True)\n"
            "    sys.stdout.buffer.write(result.stdout)\n"
            "    sys.exit(result.returncode)\n"
            "os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])\n",
            directory="head-move-bin")
        for provider in fixture.PROVIDERS:
            self.git("update-ref", "HEAD", base)
            self.assert_outcome(provider, "block", "diff", "findings", "captured.txt")

    def assert_declared_crlf_conversion(self, attributes=False):
        path = self.repo / "converted.txt"
        self.git("config", "core.autocrlf", "false" if attributes else "true")
        if attributes:
            (self.repo / ".gitattributes").write_text("converted.txt text eol=crlf\n")
        path.write_bytes(("retained=" + fixture.FAKE_TOKEN + "\nold safe\n").encode())
        self.git("add", "--all")
        self.git("commit", "-qm", "baseline")
        path.write_bytes(("retained=" + fixture.FAKE_TOKEN + "\r\nnew safe\r\n").encode())
        for provider in fixture.PROVIDERS:
            self.assert_outcome(provider, "block", "diff", "clean")
        path.write_bytes(("retained=" + fixture.FAKE_TOKEN + "\r\nnew=" + fixture.FAKE_TOKEN + "\r\n").encode())
        for provider in fixture.PROVIDERS:
            self.findings(provider, [("github_classic_pat", 2, "ghp_...FAKE")])

    def test_declared_crlf_conversion_preserves_diff_suppression_and_new_findings(self):
        self.assert_declared_crlf_conversion()

    def test_path_declared_crlf_conversion_preserves_suppression_and_new_findings(self):
        self.assert_declared_crlf_conversion(attributes=True)

    def test_auto_conversion_keeps_crlf_indexed_baseline_literal(self):
        path = self.repo / "converted.txt"
        self.git("config", "core.autocrlf", "false")
        baseline = ("retained=" + fixture.FAKE_TOKEN + "\r\nold safe\r\n").encode()
        path.write_bytes(baseline)
        self.git("add", "--all")
        self.git("commit", "-qm", "literal CRLF baseline")
        self.assertEqual(subprocess.check_output([str(self.git_path), "-C", str(self.repo), "cat-file", "blob", "HEAD:converted.txt"], env=self.env), baseline)
        self.git("config", "core.autocrlf", "true")
        path.write_bytes(("retained=" + fixture.FAKE_TOKEN + "\r\nnew safe\r\n").encode())
        for provider in fixture.PROVIDERS:
            self.assert_outcome(provider, "block", "diff", "clean")
        path.write_bytes(("retained=" + fixture.FAKE_TOKEN + "\r\nnew=" + fixture.FAKE_TOKEN + "\r\n").encode())
        for provider in fixture.PROVIDERS:
            self.findings(provider, [("github_classic_pat", 2, "ghp_...FAKE")])
        path.write_bytes(("retained=" + fixture.FAKE_TOKEN + "\nnew safe\n").encode())
        for provider in fixture.PROVIDERS:
            self.findings(provider, [("github_classic_pat", 1, "ghp_...FAKE")])

    def test_unsupported_conversion_retains_known_findings_as_incomplete(self):
        path = self.repo / "converted.txt"
        path.write_text("baseline\n")
        self.git("add", "--all")
        self.git("commit", "-qm", "baseline")
        path.write_text("changed safe\n")
        (self.repo / "a-secret.txt").write_text(fixture.FAKE_TOKEN + "\n")
        for declaration in ("filter=fixture", "working-tree-encoding=UTF-8", "ident"):
            (self.repo / ".gitattributes").write_text("converted.txt " + declaration + "\n")
            for provider in fixture.PROVIDERS:
                with self.subTest(provider=provider, declaration=declaration):
                    response, record = self.scan(provider)
                    self.assertEqual(record["status"], "incomplete")
                    self.assertEqual(record["diagnostic"]["cause"], "conversion_unsupported")
                    self.assertEqual(record["security_outcome"], "findings")
                    self.assertFalse(record["scanResult"]["coverage_complete"])
                    self.assertEqual(record["findings"][0]["path"], "a-secret.txt")
                    self.assertIn("scan incomplete", json.dumps(response))

    def test_private_diff_names_do_not_execute_global_clean_filter(self):
        import shlex
        path = self.repo / "converted.txt"
        path.write_text("baseline\n")
        self.git("add", "--all")
        self.git("commit", "-qm", "baseline")
        attributes = self.root / "global-attributes"
        attributes.write_text("* filter=fixture\n")
        (self.repo / ".gitattributes").write_text("converted.txt -filter\n")
        marker_path = self.root / "filter-executed"
        command = shlex.join([sys.executable, "-c",
            "import sys;from pathlib import Path;Path(" + repr(str(marker_path)) + ").touch();sys.stdout.buffer.write(sys.stdin.buffer.read())"])
        self.git("config", "core.attributesFile", str(attributes))
        self.git("config", "filter.fixture.clean", command)
        path.write_text("changed safe\n")
        for provider in fixture.PROVIDERS:
            marker_path.unlink(missing_ok=True)
            self.assert_outcome(provider, "block", "diff", "clean")
            self.assertFalse(marker_path.exists(), "private comparison names executed an unrelated clean filter")
        path.write_text(fixture.FAKE_TOKEN + "\n")
        for provider in fixture.PROVIDERS:
            marker_path.unlink(missing_ok=True)
            self.findings(provider, [("github_classic_pat", 1, "ghp_...FAKE")])
            self.assertFalse(marker_path.exists(), "secret comparison executed an unrelated clean filter")

    def test_input_time_and_git_work_share_nonextendable_deadline(self):
        (self.repo / "pending.txt").write_text("safe\n")
        self.install_fake_git(
            "import os, sys, time\nfrom pathlib import Path\n"
            "count = Path(os.environ['COUNT_FILE'])\n"
            "n = int(count.read_text()) if count.exists() else 0\n"
            "count.write_text(str(n + 1))\n"
            "if n < 4: time.sleep(1.9)\n"
            "os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *sys.argv[1:]])\n",
            directory="slow-bin")
        for provider in fixture.PROVIDERS:
            log = self.root / ("deadline-" + provider)
            log.mkdir()
            env = {**self.env, "HOME": str(self.root), "OBSERVABILITY_TESTING": "1",
                   "SCAN_MODE": "block", "SCAN_SCOPE": "diff",
                   "COUNT_FILE": str(log / "count"),
                   "SECRETS_LOG_DIR": str(log), "AUDIT_LOG": str(log / "audit.log"),
                   "OBSERVABILITY_LOG_PATH": str(log / "obs.jsonl")}
            payload = scanner_tool_payload(provider, self.repo)
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

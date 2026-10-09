#!/usr/bin/env python3
"""Exercise unresolved Git merges through generated scanner JSON entrypoints."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
HOOKS = {
    "copilot": ROOT / ".copilot/hooks/scripts/scan-secrets.py",
    "gemini": ROOT / ".gemini/hooks/scripts/scan-secrets.py",
    "codex": ROOT / ".codex/hooks/scan-secrets.py",
}
PROVIDERS = tuple(HOOKS)
FAKE_TOKEN = "gh" + "p_" + "FAKE" * 9


class MergeScannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="scan-merge-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git_path = shutil.which("git")
        self.assertIsNotNone(self.git_path, "Git is required")
        self.env = {
            key: value for key, value in os.environ.items()
            if not key.startswith("GIT_")
            and key not in {"SKIP_SECRETS_SCAN", "SECRETS_ALLOWLIST"}
        }
        self.env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [str(self.git_path), "-C", str(self.repo),
             "-c", "user.name=Scanner Merge Test",
             "-c", "user.email=scanner-merge@example.invalid",
             "-c", "commit.gpgsign=false", "-c", "core.hooksPath=" + str(self.root / "no-hooks"),
             *args],
            env=self.env, text=True, capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, expected, f"Git fixture failed: {args!r}: {result.stderr}")
        return result

    def write_files(self, files: dict[str, str | None]) -> None:
        for name, content in files.items():
            path = self.repo / name
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

    def merge(self, base: dict[str, str], ours: dict[str, str | None],
              theirs: dict[str, str | None]) -> None:
        self.write_files(base)
        self.git("add", "--all")
        self.git("commit", "-qm", "base")
        self.git("branch", "other")
        self.write_files(ours)
        self.git("add", "--all")
        self.git("commit", "-qm", "ours")
        self.git("checkout", "-q", "other")
        self.write_files(theirs)
        self.git("add", "--all")
        self.git("commit", "-qm", "theirs")
        self.git("checkout", "-q", "main")
        self.git("merge", "--no-edit", "other", expected=1)
        self.assertTrue((self.repo / ".git/MERGE_HEAD").exists(), "fixture must have an active merge")
        self.assertTrue(self.git("ls-files", "--unmerged").stdout, "fixture must have unresolved paths")

    def scan(self, provider: str, mode: str = "block", scope: str = "diff",
             *, stop: bool = False) -> tuple[dict, dict]:
        log_dir = self.root / f"logs-{provider}-{mode}-{scope}"
        log_dir.mkdir(exist_ok=True)
        env = {**self.env, "SCAN_MODE": mode, "SCAN_SCOPE": scope,
               "SECRETS_LOG_DIR": str(log_dir), "AUDIT_LOG": str(log_dir / "audit.log"),
               "OBSERVABILITY_LOG_PATH": str(log_dir / "observability.jsonl"),
               "OBSERVABILITY_TESTING": "1", "TMPDIR": str(self.root)}
        if provider == "copilot":
            payload = {"sessionId": "merge-test", "hook_event_name": "preToolUse",
                       "toolName": "bash", "toolArgs": {"command": "git status"}}
        else:
            payload = {"session_id": "merge-test", "cwd": str(self.repo),
                       "hook_event_name": "BeforeTool" if provider == "gemini" else "PreToolUse",
                       "tool_name": "run_shell_command" if provider == "gemini" else "exec_command",
                       "tool_input": {"command": "git status"}}
        if stop:
            payload["hook_event_name"] = {
                "copilot": "agentStop", "gemini": "SessionEnd", "codex": "Stop",
            }[provider]
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(HOOKS[provider])],
            cwd=self.repo, env=env, input=json.dumps(payload), text=True, capture_output=True, timeout=12,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        log_text = (log_dir / "scan.log").read_text(encoding="utf-8")
        all_output = (result.stdout + result.stderr).encode("utf-8") + b"".join(
            path.read_bytes() for path in log_dir.rglob("*") if path.is_file()
        )
        self.assertNotIn(FAKE_TOKEN.encode("ascii"), all_output,
                         "fake credential leaked through hook output or logs")
        rows = [json.loads(line) for line in log_text.splitlines()]
        self.assertTrue(rows, "scanner must record an outcome")
        return response, rows[-1]

    def assert_outcome(self, provider: str, mode: str, scope: str, status: str,
                       finding_path: str | None = None, cause: str | None = None) -> None:
        response, record = self.scan(provider, mode, scope)
        self.assertEqual(record["status"], status)
        if status == "clean":
            expected = {}
        else:
            detail = ("potential secrets detected." if status == "findings" else
                      "scan incomplete; potential secrets could not be checked.")
            if status == "incomplete":
                diagnostic = record["diagnostic"]
                self.assertEqual(record["action"], "tool scan")
                if cause is not None:
                    self.assertEqual(diagnostic["cause"], cause)
                self.assertIn(diagnostic["cause"], record["note"])
                self.assertIn(diagnostic["operation"], record["note"])
                self.assertNotIn(str(self.repo), json.dumps(response) + json.dumps(record))
                detail += " " + record["note"]
            reason = f"scan-secrets blocked: tool scan; {detail}"
            if mode == "warn":
                expected = {"systemMessage": f"scan-secrets warning: tool scan; {detail}"}
            elif provider == "copilot":
                expected = {"continue": True, "permissionDecision": "deny",
                            "permissionDecisionReason": reason,
                            "hookSpecificOutput": {"permissionDecision": "deny",
                                                   "permissionDecisionReason": reason}}
            elif provider == "gemini":
                expected = {"decision": "deny", "reason": reason}
            else:
                expected = {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                   "permissionDecision": "deny",
                                                   "permissionDecisionReason": reason}}
        self.assertEqual(response, expected)
        if finding_path is not None:
            self.assertTrue(any(finding["pattern"] == "github_classic_pat"
                                and finding["path"] == finding_path
                                for finding in record["findings"]), record)

    def assert_all_scans(self, status: str, finding_path: str | None = None, cause: str | None = None) -> None:
        for provider in PROVIDERS:
            for mode in ("block", "warn"):
                for scope in ("diff", "staged"):
                    with self.subTest(provider=provider, mode=mode, scope=scope):
                        self.assert_outcome(provider, mode, scope, status, finding_path, cause)

    def large_resolved_merge(self) -> None:
        self.write_files({f"file-{index:03}.txt": "baseline\n" for index in range(250)})
        self.git("add", "--all")
        self.git("commit", "-qm", "base")
        self.git("checkout", "-qb", "other")
        self.write_files({f"file-{index:03}.txt": f"safe merged content {index}\n" * 128
                          for index in range(250)})
        self.git("add", "--all")
        self.git("commit", "-qm", "incoming changes")
        self.git("checkout", "-q", "main")
        self.write_files({"README.md": "independent local change\n"})
        self.git("add", "--all")
        self.git("commit", "-qm", "local change")
        self.git("merge", "--no-commit", "other")
        self.assertTrue((self.repo / ".git/MERGE_HEAD").exists())
        self.assertEqual(self.git("ls-files", "--unmerged").stdout, "")

    def test_large_resolved_merge_allows_session_end(self) -> None:
        self.large_resolved_merge()
        for provider in PROVIDERS:
            with self.subTest(provider=provider):
                response, record = self.scan(provider, stop=True)
                expected = ({"systemMessage": "scan-secrets: pass; 250 modified files"}
                            if provider == "codex" else {})
                self.assertEqual(response, expected)
                self.assertEqual(record["status"], "clean")

    def test_large_resolved_merge_detects_secret_in_final_path(self) -> None:
        self.large_resolved_merge()
        self.write_files({"file-249.txt": f"fake_token={FAKE_TOKEN}\n"})
        self.git("add", "--all")
        for provider in PROVIDERS:
            with self.subTest(provider=provider):
                response, record = self.scan(provider, stop=True)
                self.assertEqual(record["status"], "findings")
                self.assertIn("potential secrets detected.", json.dumps(response))
                self.assertTrue(any(finding["pattern"] == "github_classic_pat"
                                    and finding["path"] == "file-249.txt"
                                    for finding in record["findings"]))

    def stage_pair(self, contents: dict[str, str]) -> None:
        self.write_files({name: "baseline\n" for name in contents})
        self.git("add", "--all")
        self.git("commit", "-qm", "base")
        self.write_files(contents)
        self.git("add", "--all")

    def test_pre_238_git_allows_clean_index_and_detects_staged_secret(self) -> None:
        fake_bin = self.root / "old-git-bin"
        fake_bin.mkdir()
        wrapper = fake_bin / "git"
        wrapper.write_text(
            f"#!{sys.executable}\n"
            "import os, sys\n"
            "args = sys.argv[1:]\n"
            "if args == ['cat-file', '--batch-check', '-z']:\n"
            "    sys.stderr.write('error: unknown switch z\\n')\n"
            "    sys.exit(129)\n"
            "os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        self.env.update(PATH=str(fake_bin) + os.pathsep + self.env["PATH"],
                        REAL_GIT=str(self.git_path))
        path = "line\nbreak\tname.txt"
        self.stage_pair({path: "safe changed content\n", ":0:notes.txt": "safe\n"})
        self.assert_all_scans("clean")
        self.write_files({path: f"fake_token={FAKE_TOKEN}\n"})
        self.git("add", "--all")
        self.assert_all_scans("findings", path)

    def test_batch_paths_preserve_newlines_tabs_and_colons(self) -> None:
        # Constructing the index references must never treat path delimiters as
        # separate requests. The leading colon is an ordinary filename byte.
        path = "line\nbreak\tname.txt"
        self.stage_pair({path: f"fake_token={FAKE_TOKEN}\n", ":0:notes.txt": "safe\n"})
        self.assert_all_scans("findings", path)

    def test_batch_long_paths_fit_bounded_git_command_lines(self) -> None:
        contents = {f"entry-{index:03}-" + "x" * 190 + ".txt": "safe changed content\n"
                    for index in range(256)}
        self.stage_pair(contents)
        fake_bin = self.root / "argv-bin"
        fake_bin.mkdir()
        wrapper = fake_bin / "git"
        wrapper.write_text(
            f"#!{sys.executable}\n"
            "import os, sys\n"
            "args = sys.argv[1:]\n"
            "if args[:5] == ['--literal-pathspecs', 'ls-files', '--stage', '-z', '--']:\n"
            "    if sum(len(os.fsencode(path)) * 2 + 3 for path in args[5:]) > 8192:\n"
            "        sys.stderr.write('command line exceeds fixture limit\\n')\n"
            "        sys.exit(129)\n"
            "os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        self.env.update(PATH=str(fake_bin) + os.pathsep + self.env["PATH"],
                        REAL_GIT=str(self.git_path))
        self.assert_all_scans("clean")
        last_path = sorted(contents)[-1]
        self.write_files({last_path: f"fake_token={FAKE_TOKEN}\n"})
        self.git("add", "--all")
        self.assert_all_scans("findings", last_path)

    def directory_file_batch_merge(self, secret_source: str | None = None) -> None:
        # These 16 names put the unresolved parent at the end of the first
        # argument batch, while its staged child belongs to the next batch.
        filler = {f"a-{index:02}-" + "x" * 248: "baseline\n" for index in range(16)}
        self.write_files({"zconflict": "base\n", **filler})
        self.git("add", "--all")
        self.git("commit", "-qm", "base")
        self.git("branch", "other")
        parent = f"fake_token={FAKE_TOKEN}\n" if secret_source == "parent" else "ours\n"
        self.write_files({"zconflict": parent})
        self.git("add", "--all")
        self.git("commit", "-qm", "ours")
        self.git("checkout", "-q", "other")
        self.write_files({"zconflict": None})
        child = f"fake_token={FAKE_TOKEN}\n" if secret_source == "child" else "theirs\n"
        self.write_files({"zconflict/child": child,
                          **{name: "safe changed\n" for name in filler}})
        self.git("add", "--all")
        self.git("commit", "-qm", "theirs")
        self.git("checkout", "-q", "main")
        self.git("merge", "-s", "resolve", "--no-commit", "other", expected=1)
        self.assertTrue((self.repo / ".git/MERGE_HEAD").exists())
        self.assertTrue(self.git("ls-files", "--unmerged").stdout)
        self.assertTrue((self.repo / "zconflict").is_dir())

    def test_directory_file_batch_allows_staged_and_keeps_diff_incomplete(self) -> None:
        self.directory_file_batch_merge()
        for provider in PROVIDERS:
            for mode in ("block", "warn"):
                with self.subTest(provider=provider, mode=mode, scope="staged"):
                    self.assert_outcome(provider, mode, "staged", "clean")
                with self.subTest(provider=provider, mode=mode, scope="diff"):
                    self.assert_outcome(provider, mode, "diff", "incomplete")

    def test_directory_file_batch_detects_parent_snapshot_secret(self) -> None:
        self.directory_file_batch_merge("parent")
        for provider in PROVIDERS:
            for mode in ("block", "warn"):
                with self.subTest(provider=provider, mode=mode):
                    self.assert_outcome(provider, mode, "staged", "findings", "zconflict")

    def test_directory_file_batch_detects_child_snapshot_secret(self) -> None:
        self.directory_file_batch_merge("child")
        for provider in PROVIDERS:
            for mode in ("block", "warn"):
                with self.subTest(provider=provider, mode=mode):
                    self.assert_outcome(provider, mode, "staged", "findings", "zconflict/child")

    def test_directory_file_batch_validates_unselected_descendant_records(self) -> None:
        self.directory_file_batch_merge()
        fake_bin = self.root / "prefix-bin"
        fake_bin.mkdir()
        wrapper = fake_bin / "git"
        wrapper.write_text(
            f"#!{sys.executable}\n"
            "import os, subprocess, sys\n"
            "args = sys.argv[1:]\n"
            "if (args[:5] != ['--literal-pathspecs', 'ls-files', '--stage', '-z', '--']\n"
            "        or 'zconflict' not in args[5:]):\n"
            "    os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])\n"
            "result = subprocess.run([os.environ['REAL_GIT'], *args],\n"
            "                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)\n"
            "output = result.stdout\n"
            "header = output.split(b'\\t', 1)[0]\n"
            "path = b'zconflict/unchanged'\n"
            "fault = os.environ['PREFIX_FAULT']\n"
            "if fault == 'malformed-object':\n"
            "    header = b'100644 not-an-object 0'\n"
            "elif fault == 'invalid-stage':\n"
            "    header = header.rsplit(b' ', 1)[0] + b' 4'\n"
            "elif fault == 'escaping-descendant':\n"
            "    path = b'zconflict/../private-outside'\n"
            "elif fault == 'dot-component':\n"
            "    path = b'zconflict/./private-outside'\n"
            "elif fault == 'empty-component':\n"
            "    path = b'zconflict//private-outside'\n"
            "elif fault == 'sibling-prefix':\n"
            "    path = b'zconflict-sibling/private-outside'\n"
            "sys.stdout.buffer.write(output + header + b'\\t' + path + b'\\0')\n"
            "sys.exit(result.returncode)\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        self.env.update(PATH=str(fake_bin) + os.pathsep + self.env["PATH"],
                        REAL_GIT=str(self.git_path))
        for fault in ("valid-descendant", "malformed-object", "invalid-stage",
                      "escaping-descendant", "dot-component", "empty-component", "sibling-prefix"):
            self.env["PREFIX_FAULT"] = fault
            for provider in PROVIDERS:
                for mode in ("block", "warn"):
                    with self.subTest(fault=fault, provider=provider, mode=mode):
                        self.assert_outcome(provider, mode, "staged",
                                            "clean" if fault == "valid-descendant" else "incomplete")
        all_logs = b"".join(path.read_bytes() for path in self.root.glob("logs-*/*") if path.is_file())
        self.assertNotIn(b"not-an-object", all_logs)
        self.assertNotIn(b"private-outside", all_logs)

    def test_batch_keeps_staged_secret_when_worktree_matches_head(self) -> None:
        self.stage_pair({"hidden.txt": f"fake_token={FAKE_TOKEN}\n", "safe.txt": "safe\n"})
        self.write_files({"hidden.txt": "baseline\n"})
        self.assert_all_scans("findings", "hidden.txt")

    def test_batch_diff_ignores_unchanged_secrets(self) -> None:
        self.write_files({name: f"fake_token={FAKE_TOKEN}\nbaseline\n"
                          for name in ("first.txt", "second.txt")})
        self.git("add", "--all")
        self.git("commit", "-qm", "historical fixture")
        self.write_files({name: f"fake_token={FAKE_TOKEN}\nsafe change\n"
                          for name in ("first.txt", "second.txt")})
        self.git("add", "--all")
        for provider in PROVIDERS:
            for mode in ("block", "warn"):
                with self.subTest(provider=provider, mode=mode):
                    self.assert_outcome(provider, mode, "diff", "clean")
                    self.assert_outcome(provider, mode, "staged", "findings", "first.txt")

    def test_batch_at_total_byte_limit_allows_framing_overhead(self) -> None:
        self.stage_pair({f"file-{index}.txt": "safe\n" + "x" * (1048576 - 5)
                         for index in range(8)})
        self.assert_all_scans("clean")

    def test_batch_binary_and_empty_blobs_keep_content_boundaries(self) -> None:
        self.stage_pair({"empty.txt": "", "binary.bin": f"\0fake_token={FAKE_TOKEN}\0"})
        self.assert_all_scans("findings", "binary.bin")

    def test_batch_corrupt_git_responses_remain_incomplete(self) -> None:
        self.stage_pair({"first.txt": "first changed\n", "second.txt": "second changed\n"})
        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        wrapper = fake_bin / "git"
        wrapper.write_text(
            f"#!{sys.executable}\n"
            "import os, subprocess, sys\n"
            "args = sys.argv[1:]\n"
            "if args not in (['cat-file', '--batch-check'], ['cat-file', '--batch']):\n"
            "    os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])\n"
            "result = subprocess.run([os.environ['REAL_GIT'], *args], input=sys.stdin.buffer.read(),\n"
            "                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)\n"
            "output = result.stdout\n"
            "fault = os.environ['BATCH_FAULT']\n"
            "metadata = '--batch-check' in args\n"
            "if fault == 'missing-object' and metadata:\n"
            "    output = b'private missing object\\n'\n"
            "elif fault == 'wrong-type' and metadata:\n"
            "    output = output.replace(b' blob ', b' tree ', 1)\n"
            "elif fault == 'invalid-size' and metadata:\n"
            "    output = output.split(b'\\n', 1)[0].rsplit(b' ', 1)[0] + b' -1\\n'\n"
            "elif fault == 'oversized-integer' and metadata:\n"
            "    first, rest = output.split(b'\\n', 1)\n"
            "    output = first.rsplit(b' ', 1)[0] + b' ' + b'9' * 5000 + b'\\n' + rest\n"
            "elif fault == 'extra-metadata' and metadata:\n"
            "    output += output.split(b'\\n', 1)[0] + b'\\n'\n"
            "elif fault == 'wrong-metadata-object' and metadata:\n"
            "    output = (b'0' if output[:1] != b'0' else b'1') + output[1:]\n"
            "elif fault == 'oversized-blob' and metadata:\n"
            "    first, rest = output.split(b'\\n', 1)\n"
            "    output = first.rsplit(b' ', 1)[0] + b' 1048577\\n' + rest\n"
            "elif fault == 'truncated' and not metadata:\n"
            "    output = output[:-1]\n"
            "elif fault == 'extra-content' and not metadata:\n"
            "    output += b'private unexpected content'\n"
            "elif fault == 'wrong-object' and not metadata:\n"
            "    output = (b'0' if output[:1] != b'0' else b'1') + output[1:]\n"
            "elif fault == 'bad-separator' and not metadata:\n"
            "    output = output[:-1] + b'x'\n"
            "elif fault == 'nonzero' and not metadata:\n"
            "    sys.exit(9)\n"
            "sys.stdout.buffer.write(output)\n"
            "sys.exit(result.returncode)\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        self.env.update(PATH=str(fake_bin) + os.pathsep + self.env["PATH"], REAL_GIT=str(self.git_path))
        for fault in ("missing-object", "wrong-type", "invalid-size", "oversized-integer", "extra-metadata",
                      "wrong-metadata-object",
                      "oversized-blob", "truncated", "extra-content", "wrong-object",
                      "bad-separator", "nonzero"):
            self.env["BATCH_FAULT"] = fault
            for provider in PROVIDERS:
                for mode in ("block", "warn"):
                    with self.subTest(fault=fault, provider=provider, mode=mode):
                        self.assert_outcome(provider, mode, "diff", "incomplete",
                                            cause="git_failed" if fault == "nonzero" else
                                            "file_bytes_limit" if fault == "oversized-blob" else
                                            "git_output_invalid")
        all_logs = b"".join(path.read_bytes() for path in self.root.glob("logs-*/*") if path.is_file())
        self.assertNotIn(b"private missing object", all_logs)
        self.assertNotIn(b"private unexpected content", all_logs)

    def test_batch_corrupt_index_resolution_remains_incomplete(self) -> None:
        self.stage_pair({"first.txt": "first changed\n", "second.txt": "second changed\n"})
        fake_bin = self.root / "index-bin"
        fake_bin.mkdir()
        wrapper = fake_bin / "git"
        wrapper.write_text(
            f"#!{sys.executable}\n"
            "import os, subprocess, sys\n"
            "args = sys.argv[1:]\n"
            "if args[:5] != ['--literal-pathspecs', 'ls-files', '--stage', '-z', '--']:\n"
            "    os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])\n"
            "result = subprocess.run([os.environ['REAL_GIT'], *args],\n"
            "                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)\n"
            "output = result.stdout\n"
            "records = output[:-1].split(b'\\0')\n"
            "fault = os.environ['INDEX_FAULT']\n"
            "if fault == 'truncated':\n"
            "    output = output[:-1]\n"
            "elif fault == 'missing':\n"
            "    output = records[0] + b'\\0'\n"
            "elif fault == 'duplicate':\n"
            "    output += records[0] + b'\\0'\n"
            "elif fault == 'empty-record':\n"
            "    output += b'\\0'\n"
            "elif fault == 'invalid-object':\n"
            "    fields = records[0].split(b' ', 2)\n"
            "    records[0] = fields[0] + b' not-an-object ' + fields[2]\n"
            "    output = b'\\0'.join(records) + b'\\0'\n"
            "elif fault == 'invalid-stage':\n"
            "    output = output.replace(b' 0\\t', b' 4\\t', 1)\n"
            "elif fault == 'unexpected-stage':\n"
            "    output = output.replace(b' 0\\t', b' 2\\t', 1)\n"
            "elif fault == 'unexpected-path':\n"
            "    header, _ = records[0].split(b'\\t', 1)\n"
            "    records[0] = header + b'\\tprivate unrequested path'\n"
            "    output = b'\\0'.join(records) + b'\\0'\n"
            "elif fault == 'nonzero':\n"
            "    sys.exit(9)\n"
            "sys.stdout.buffer.write(output)\n"
            "sys.exit(result.returncode)\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        self.env.update(PATH=str(fake_bin) + os.pathsep + self.env["PATH"],
                        REAL_GIT=str(self.git_path))
        for fault in ("truncated", "missing", "duplicate", "empty-record", "invalid-object",
                      "invalid-stage", "unexpected-stage", "unexpected-path", "nonzero"):
            self.env["INDEX_FAULT"] = fault
            for provider in PROVIDERS:
                for mode in ("block", "warn"):
                    with self.subTest(fault=fault, provider=provider, mode=mode):
                        self.assert_outcome(provider, mode, "diff", "incomplete",
                                            cause="git_failed" if fault == "nonzero" else
                                            "file_bytes_limit" if fault == "oversized-blob" else
                                            "git_output_invalid")
        all_logs = b"".join(path.read_bytes() for path in self.root.glob("logs-*/*") if path.is_file())
        self.assertNotIn(b"private unrequested path", all_logs)

    def test_clean_content_and_modify_delete_merge_allows_tool(self) -> None:
        self.merge(
            {"conflict.txt": "base\n", "removed.txt": "base\n"},
            {"conflict.txt": "ours\n", "removed.txt": "ours\n"},
            {"conflict.txt": "theirs\n", "removed.txt": None},
        )
        self.assert_all_scans("clean")

    def assert_secret_stage(self, stage: int) -> None:
        contents = ["base\n", "ours\n", "theirs\n"]
        contents[stage - 1] = f"fake_token={FAKE_TOKEN}\n"
        self.merge({"conflict.txt": contents[0]}, {"conflict.txt": contents[1]},
                   {"conflict.txt": contents[2]})
        # A user can replace the conflict markers before staging a resolution.
        # The unresolved index still retains each side's original snapshot.
        self.write_files({"conflict.txt": "safe replacement awaiting git add\n"})
        self.assert_all_scans("findings", "conflict.txt")

    def test_secret_in_merge_base_is_detected_after_worktree_replacement(self) -> None:
        self.assert_secret_stage(1)

    def test_secret_in_ours_is_detected_after_worktree_replacement(self) -> None:
        self.assert_secret_stage(2)

    def test_secret_in_theirs_is_detected_after_worktree_replacement(self) -> None:
        self.assert_secret_stage(3)

    def test_worktree_only_conflict_secret_is_detected_in_diff_scope(self) -> None:
        self.merge({"conflict.txt": "base\n"}, {"conflict.txt": "ours\n"},
                   {"conflict.txt": "theirs\n"})
        self.write_files({"conflict.txt": f"fake_token={FAKE_TOKEN}\n"})
        for provider in PROVIDERS:
            for mode in ("block", "warn"):
                with self.subTest(provider=provider, mode=mode, scope="diff"):
                    self.assert_outcome(provider, mode, "diff", "findings", "conflict.txt")
                with self.subTest(provider=provider, mode=mode, scope="staged"):
                    self.assert_outcome(provider, mode, "staged", "clean")

    def test_clean_add_add_conflict_allows_tool_without_a_base_stage(self) -> None:
        self.merge({"README.md": "safe fixture\n"}, {"added.txt": "ours\n"},
                   {"added.txt": "theirs\n"})
        self.assert_all_scans("clean")

    def test_add_add_conflict_retains_secret_after_worktree_replacement(self) -> None:
        self.merge({"README.md": "safe fixture\n"}, {"added.txt": "ours\n"},
                   {"added.txt": f"fake_token={FAKE_TOKEN}\n"})
        self.write_files({"added.txt": "safe replacement awaiting git add\n"})
        self.assert_all_scans("findings", "added.txt")

    def assert_deleted_conflict(self, *, deleted_by_ours: bool, secret: bool) -> None:
        modified = f"fake_token={FAKE_TOKEN}\n" if secret else "safe modified version\n"
        ours = None if deleted_by_ours else modified
        theirs = modified if deleted_by_ours else None
        self.merge({"removed.txt": "base\n"}, {"removed.txt": ours}, {"removed.txt": theirs})
        # Deletion is a normal resolution step before `git add` records it.
        (self.repo / "removed.txt").unlink()
        self.assert_all_scans("findings" if secret else "clean", "removed.txt" if secret else None)

    def test_missing_clean_conflict_deleted_by_ours_allows_tool(self) -> None:
        self.assert_deleted_conflict(deleted_by_ours=True, secret=False)

    def test_missing_clean_conflict_deleted_by_theirs_allows_tool(self) -> None:
        self.assert_deleted_conflict(deleted_by_ours=False, secret=False)

    def test_missing_conflict_deleted_by_ours_retains_index_secret(self) -> None:
        self.assert_deleted_conflict(deleted_by_ours=True, secret=True)

    def test_missing_conflict_deleted_by_theirs_retains_index_secret(self) -> None:
        self.assert_deleted_conflict(deleted_by_ours=False, secret=True)

    def assert_worktree_read_failure(self) -> None:
        for provider in PROVIDERS:
            for mode in ("block", "warn"):
                with self.subTest(provider=provider, mode=mode, scope="diff"):
                    self.assert_outcome(provider, mode, "diff", "incomplete", cause="candidate_unsafe")
                with self.subTest(provider=provider, mode=mode, scope="staged"):
                    self.assert_outcome(provider, mode, "staged", "clean")

    def test_symlink_conflict_worktree_stays_incomplete_and_is_not_followed(self) -> None:
        self.merge({"conflict.txt": "base\n"}, {"conflict.txt": "ours\n"},
                   {"conflict.txt": "theirs\n"})
        outside = self.root / "outside.txt"
        outside.write_text(f"fake_token={FAKE_TOKEN}\n", encoding="utf-8")
        conflict = self.repo / "conflict.txt"
        conflict.unlink()
        conflict.symlink_to(outside)
        self.assert_worktree_read_failure()

    def test_directory_conflict_worktree_stays_incomplete(self) -> None:
        self.merge({"conflict.txt": "base\n"}, {"conflict.txt": "ours\n"},
                   {"conflict.txt": "theirs\n"})
        conflict = self.repo / "conflict.txt"
        conflict.unlink()
        conflict.mkdir()
        self.assert_worktree_read_failure()

    def assert_conflict_stage_size(self, size: int, status: str) -> None:
        self.merge({"conflict.txt": "base\n"}, {"conflict.txt": "x" * (size - 1) + "\n"},
                   {"conflict.txt": "theirs\n"})
        self.write_files({"conflict.txt": "safe replacement awaiting git add\n"})
        self.assert_all_scans(status, cause="file_bytes_limit" if status == "incomplete" else None)

    def test_conflict_stage_at_file_byte_limit_remains_scannable(self) -> None:
        self.assert_conflict_stage_size(1048576, "clean")

    def test_oversized_conflict_stage_stays_incomplete(self) -> None:
        self.assert_conflict_stage_size(1048577, "incomplete")

    def assert_snapshot_budget(self, count: int, status: str) -> None:
        # Each snapshot is below the file bound. Three conflicts have 8.1 MB
        # across their nine index snapshots; four conflicts exceed the 8 MiB
        # aggregate bound even after the working copies are made small.
        base = {f"conflict-{index}.txt": "b" * 899999 + "\n" for index in range(count)}
        ours = {name: "o" * 899999 + "\n" for name in base}
        theirs = {name: "t" * 899999 + "\n" for name in base}
        self.merge(base, ours, theirs)
        self.write_files({name: "safe replacement awaiting git add\n" for name in base})
        self.assert_all_scans(status, cause="total_bytes_limit" if status == "incomplete" else None)

    def test_conflict_snapshots_below_total_byte_limit_remain_scannable(self) -> None:
        self.assert_snapshot_budget(3, "clean")

    def test_conflict_snapshots_exceeding_total_byte_limit_stay_incomplete(self) -> None:
        self.assert_snapshot_budget(4, "incomplete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Other arguments pass to unittest, including -v, -k PATTERN, and test names.",
    )
    parser.add_argument("--provider", choices=tuple(HOOKS), help="run one provider only")
    options, remaining = parser.parse_known_args()
    if options.provider:
        PROVIDERS = (options.provider,)
    unittest.main(argv=[sys.argv[0], *remaining])

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

    def scan(self, provider: str, mode: str = "block", scope: str = "diff") -> tuple[dict, dict]:
        log_dir = self.root / f"logs-{provider}-{mode}-{scope}"
        log_dir.mkdir(exist_ok=True)
        env = {**self.env, "SCAN_MODE": mode, "SCAN_SCOPE": scope,
               "SECRETS_LOG_DIR": str(log_dir), "AUDIT_LOG": str(log_dir / "audit.log"),
               "OBSERVABILITY_LOG_PATH": str(log_dir / "observability.jsonl"), "TMPDIR": str(self.root)}
        if provider == "copilot":
            payload = {"sessionId": "merge-test", "hook_event_name": "preToolUse",
                       "toolName": "bash", "toolArgs": {"command": "git status"}}
        else:
            payload = {"session_id": "merge-test", "cwd": str(self.repo),
                       "hook_event_name": "BeforeTool" if provider == "gemini" else "PreToolUse",
                       "tool_name": "run_shell_command" if provider == "gemini" else "exec_command",
                       "tool_input": {"command": "git status"}}
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
                       finding_path: str | None = None) -> None:
        response, record = self.scan(provider, mode, scope)
        self.assertEqual(record["status"], status)
        if status == "clean":
            expected = {}
        else:
            detail = ("potential secrets detected." if status == "findings" else
                      "scan incomplete; potential secrets could not be checked.")
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

    def assert_all_scans(self, status: str, finding_path: str | None = None) -> None:
        for provider in PROVIDERS:
            for mode in ("block", "warn"):
                for scope in ("diff", "staged"):
                    with self.subTest(provider=provider, mode=mode, scope=scope):
                        self.assert_outcome(provider, mode, scope, status, finding_path)

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
                    self.assert_outcome(provider, mode, "diff", "incomplete")
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
        self.assert_all_scans(status)

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
        self.assert_all_scans(status)

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

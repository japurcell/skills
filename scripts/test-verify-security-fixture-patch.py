#!/usr/bin/env python3
"""Acceptance at the fixture-preflight CLI and generated-provider seams."""
from __future__ import annotations
import difflib
import json
import hashlib
import stat
import zipfile
import os
import shutil
import signal
import shlex
import time
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts/verify-security-fixture-patch.py"
TOKEN = "gh" + "p_" + "FAKE" * 9

class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fixture-preflight-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(HOME=str(self.base / "home"), GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_CONFIG_NOSYSTEM="1", GIT_OPTIONAL_LOCKS="0")
        self.git("init", "-q", "-b", "main")
        self.target = self.repo / "fixture.py"
        self.target.write_text("value = 'safe'\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "baseline")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.repo), *args], env=self.env,
                                capture_output=True, check=True, timeout=10)
        return result.stdout

    def patch(self, after, before=None, path="fixture.py"):
        before = self.target.read_text() if before is None else before
        patch = self.base / "candidate.patch"
        patch.write_text("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                                     fromfile="a/" + path, tofile="b/" + path)))
        return patch

    def run_cli(self, patch, *extra, active=ROOT, timeout=60):
        return subprocess.run([sys.executable, str(CLI), "--patch", str(patch),
                               "--path", "fixture.py", "--active-hook-root", str(active),
                               "--json", "--no-input", *extra], cwd=self.repo, env=self.env,
                              capture_output=True, timeout=timeout)

    def fingerprint(self):
        return (self.target.read_bytes(), self.target.stat().st_mode,
                (self.repo / ".git/index").read_bytes(), self.git("status", "--porcelain=v1", "-z"))

    def test_moved_literal_is_rejected_without_mutation(self):
        # The end-user hazard: a retained credential is moved into an added line.
        original = "left = '" + TOKEN + "'\nright = 'safe'\n"
        self.target.write_text(original)
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "fake baseline")
        candidate = "left = 'safe'\nright = '" + TOKEN + "'\n"
        patch = self.patch(candidate)
        before = self.fingerprint()
        result = self.run_cli(patch, "--check")
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["reason"], "findings")
        self.assertEqual(self.fingerprint(), before)
        self.assertNotIn(TOKEN.encode(), result.stdout + result.stderr)

    def test_complete_changed_content_catches_retained_credential(self):
        baseline = "value = '" + TOKEN + "'\nother = 'old'\n"
        self.target.write_text(baseline)
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "fake baseline")
        patch = self.patch(baseline.replace("old", "new"))
        before = self.fingerprint()
        result = self.run_cli(patch, "--check")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_repaired_representation_preserves_runtime_and_dirty_state(self):
        self.target.chmod(0o755)
        self.target.write_text("value = 'staged'\n")
        self.git("add", "fixture.py")
        self.target.write_text("value = 'worktree'\n")
        (self.repo / "untracked.txt").write_text("retained untracked data\n")
        sentinel = self.base / "hook-executed"
        hook = self.repo / ".git/hooks/pre-commit"
        hook.write_text("#!/bin/sh\nprintf bad > " + str(sentinel) + "\n")
        hook.chmod(0o755)
        self.git("config", "filter.hostile.clean", "touch " + str(sentinel))
        after = "value = 'gh' + 'p_' + 'FAKE' * 9\nprint(value, end='')\n"
        patch = self.patch(after)
        before = self.fingerprint()
        checked = self.run_cli(patch, "--check")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertEqual(self.fingerprint(), before)
        self.assertEqual(json.loads(checked.stdout)["controls_detected"], 6)
        # Execute only the reviewed representation in a separate disposable
        # fixture, never the live repository target or arbitrary tool input.
        candidate = self.base / "verified-candidate.py"
        candidate.write_text(after)
        runtime = subprocess.run([sys.executable, "-I", "-S", "-B", str(candidate)], capture_output=True, check=True)
        self.assertEqual(runtime.stdout, TOKEN.encode())
        self.assertEqual(self.fingerprint(), before)
        self.assertEqual((self.repo / "untracked.txt").read_text(), "retained untracked data\n")
        self.assertFalse(sentinel.exists())
        report = json.loads(checked.stdout)
        self.assertEqual(set(report["builds"]), {"active", "candidate"})
        self.assertEqual(report["result"], "verified")

    def test_display_truncation_is_findings_but_inspection_stop_is_incomplete(self):
        before = self.fingerprint()
        for count, code in ((101, 1), (1001, 2)):
            with self.subTest(count=count):
                patch = self.patch(("value = '" + TOKEN + "'\n") * count)
                result = self.run_cli(patch, "--check")
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                report = json.loads(result.stdout)
                self.assertTrue(report["findings_present"])
                self.assertEqual(self.fingerprint(), before)
                self.assertNotIn(TOKEN.encode(), result.stdout + result.stderr)

    def historical_active(self, label, revision, helpers=()):
        fixture = ROOT / "scripts/fixtures/hook-resilience"
        manifest = json.loads((fixture / (label + ".json")).read_text())
        self.assertEqual(manifest["source_revision"], revision)
        names = {folder + "/" + name for folder in
                 (".codex/hooks", ".copilot/hooks/scripts", ".gemini/hooks/scripts")
                 for name in ("scan-secrets.py", "helpers/common.py", "helpers/audit.py", *helpers)}
        self.assertEqual(set(manifest["files"]), names)
        archive_path = fixture / (label + ".zip")
        self.assertLess(archive_path.stat().st_size, 1024 * 1024)
        active = self.base / label
        with zipfile.ZipFile(archive_path) as archive:
            self.assertEqual(set(archive.namelist()), names)
            self.assertEqual(len(archive.infolist()), len(names))
            for name in sorted(names):
                info = archive.getinfo(name)
                self.assertEqual(stat.S_IFMT(info.external_attr >> 16), stat.S_IFREG)
                self.assertLessEqual(info.file_size, 1024 * 1024)
                data = archive.read(name)
                self.assertEqual(len(data), manifest["files"][name]["bytes"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), manifest["files"][name]["sha256"])
                target = active / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        return active

    def legacy_active(self):
        return self.historical_active("legacy-active-scanners", "6c3c2d8c8033525792fb1c5effd04e3e32cd7682")

    def test_historical_seven_helper_active_and_current_candidate(self):
        helpers = tuple("helpers/" + name + ".py" for name in ("scan_types", "scan_reporting",
            "scan_allowlist", "scan_stream", "scan_git", "scan_audit", "scan_engine"))
        active = self.historical_active("seven-helper-active-scanners",
            "50c12113563b2c1f519514bdb2bcd73b32339334", helpers)
        before = self.fingerprint()
        result = self.run_cli(self.patch("value = 'gh' + 'p_' + 'FAKE' * 9\n"), "--check", active=active)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["controls_detected"], 6)
        for provider in ("codex", "copilot", "gemini"):
            old, new = (report["builds"][label][provider] for label in ("active", "candidate"))
            self.assertEqual(old["coverage_schema"], 1)
            self.assertEqual(new["coverage_schema"], 1)
            self.assertNotEqual(old["bundle"], new["bundle"])
        self.assertEqual(self.fingerprint(), before)

    def test_reviewed_legacy_active_and_new_candidate_remain_independent(self):
        before = self.fingerprint()
        active = self.legacy_active()
        repaired = "value = 'gh' + 'p_' + 'FAKE' * 9\n"
        result = self.run_cli(self.patch(repaired), "--check", active=active)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["controls_detected"], 6)
        for provider in ("codex", "copilot", "gemini"):
            old, new = (report["builds"][label][provider] for label in ("active", "candidate"))
            self.assertNotEqual(old["bundle"], new["bundle"])
            self.assertEqual(old["coverage_schema"], 0)
            self.assertEqual(new["coverage_schema"], 1)
        self.assertEqual(self.fingerprint(), before)
        # Historical bundles cannot prove complete inspection from truncation.
        patch = self.patch(("value = '" + TOKEN + "'\n") * 101)
        result = self.run_cli(patch, "--check", active=active)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "incomplete_scan")
        self.assertTrue(json.loads(result.stdout)["findings_present"])
        self.assertEqual(self.fingerprint(), before)

    def active_copy(self, fault):
        active = self.base / ("active-" + fault)
        for directory in (".codex/hooks", ".copilot/hooks/scripts", ".gemini/hooks/scripts"):
            origin = ROOT / directory
            target = active / directory
            target.mkdir(parents=True)
            names = ("scan-secrets.py", "helpers/common.py", "helpers/audit.py", *(
                "helpers/" + name + ".py" for name in ("scan_types", "scan_reporting",
                "scan_allowlist", "scan_stream", "scan_git", "scan_native_file", "scan_native_process", "scan_audit", "scan_engine")))
            for name in names:
                (target / name).parent.mkdir(exist_ok=True)
                shutil.copy2(origin / name, target / name)
        scanner = active / ".codex/hooks/scan-secrets.py"
        source = scanner.read_text()
        if fault == "malformed":
            source = source.replace('if __name__ == "__main__":', 'print("not-json")\nif __name__ == "__main__":')
        elif fault == "audit":
            source = source.replace('raise SystemExit(main())', 'code = main()\n        resolve_scan_log().unlink()\n        raise SystemExit(code)')
        elif fault == "timeout":
            source = source.replace('if __name__ == "__main__":', 'time.sleep(60)\nif __name__ == "__main__":')
        elif fault == "build":
            source = source.replace('REPORT_BUILD = "', 'REPORT_BUILD = "bad')
        elif fault == "clean-findings":
            source = source.replace("raise SystemExit(main())", "code = main()\n        log = resolve_scan_log()\n        record = json.loads(log.read_text())\n        record.update(findings=[{'pattern': 'github_classic_pat'}], findingsTruncated=True, omittedFindings=1)\n        log.write_text(json.dumps(record) + '\\n')\n        raise SystemExit(code)")
        elif fault == "findings-allow":
            source = source.replace('if __name__ == "__main__":', 'emit_block_denial = lambda reason: emit_json({})\nif __name__ == "__main__":')
        elif fault == "findings-unsafe-audit":
            source = source.replace("raise SystemExit(main())", "code = main()\n        resolve_scan_log().chmod(0o644)\n        raise SystemExit(code)")
        scanner.write_text(source)
        return active

    def test_modern_coverage_metadata_must_be_present_and_consistent(self):
        before = self.fingerprint()
        for fault, change in (
            ("missing", "record.pop('scanResult')"),
            ("coverage", "record['scanResult']['coverage_complete'] = False"),
            ("schema", "record['scanResult']['schema_version'] = True"),
            ("build", "record['scanResult']['build'] = '0' * 16"),
            ("policy", "record['scanResult']['policy_version'] = 'unknown'"),
            ("scope", "record['scanResult']['scope'] = 'staged'"),
            ("identity", "record['scanResult']['scope_identity'] = 'bad'"),
            ("outcome", "record['scanResult']['outcome'] = 'complete_clean'"),
            ("counts", "record['scanResult']['counts']['processed_findings'] = 0"),
            ("audit", "record['scanResult']['audit_outcome'] = 'unavailable'"),
        ):
            with self.subTest(fault=fault):
                active = self.active_copy("coverage-" + fault)
                scanner = active / ".codex/hooks/scan-secrets.py"
                source = scanner.read_text().replace("raise SystemExit(main())",
                    "code = main()\n        log = resolve_scan_log()\n        record = json.loads(log.read_text())\n        " + change +
                    "\n        log.write_text(json.dumps(record) + '\\n')\n        raise SystemExit(code)")
                scanner.write_text(source)
                patch = self.patch("value = '" + TOKEN + "'\n")
                result = self.run_cli(patch, "--check", active=active)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                report = json.loads(result.stdout)
                self.assertIn(report["reason"], ("invalid_scan_result_schema", "inconsistent_scanner_result"))
                self.assertTrue(report["findings_present"])
                self.assertEqual(self.fingerprint(), before)
                self.assertNotIn(TOKEN.encode(), result.stdout + result.stderr)

    def test_active_scanner_faults_fail_closed(self):
        patch = self.patch("value = 'repaired'\n")
        before = self.fingerprint()
        for fault in ("malformed", "audit", "timeout", "build"):
            with self.subTest(fault=fault):
                started = time.monotonic()
                result = self.run_cli(patch, "--check", active=self.active_copy(fault), timeout=20)
                self.assertIn(result.returncode, (2, 3), result.stdout + result.stderr)
                self.assertLess(time.monotonic() - started, 16)
                self.assertEqual(self.fingerprint(), before)
                self.assertNotIn(TOKEN.encode(), result.stdout + result.stderr)

    def test_unsafe_targets_and_patch_forms_never_write(self):
        patch = self.patch("value = 'repaired'\n")
        before = self.fingerprint()
        cases = (("--path", "../outside"), ("--path", "/absolute"),
                 ("--path", "C:/outside"), ("--path", "fixture.py"))
        for extra in cases:
            with self.subTest(extra=extra):
                result = self.run_cli(patch, "--check", *extra)
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertEqual(self.fingerprint(), before)
        original = self.target.read_bytes()
        self.target.unlink()
        outside = self.base / "outside"
        outside.write_bytes(original)
        self.target.symlink_to(outside)
        result = self.run_cli(patch, "--check")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(outside.read_bytes(), original)
        self.target.unlink()
        self.target.write_bytes(original)
        for content in (b"GIT binary patch\n", b"rename from fixture.py\nrename to other.py\n"):
            patch.write_bytes(content)
            result = self.run_cli(patch, "--check")
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertEqual(self.target.read_bytes(), original)
        self.target.write_bytes(b"binary\0data")
        result = self.run_cli(self.patch("value = 'safe'\n", before="binary"), "--check")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(self.target.read_bytes(), b"binary\0data")

    def test_help_version_invalid_arguments_and_explicit_check(self):
        for args in ([], ["--help"], ["help"], ["help", "check"], ["--version"]):
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, str(CLI), *args], cwd=self.base,
                                        env=self.env, capture_output=True, timeout=2)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout)
        patch = self.patch("value = 'repaired'\n")
        for extra in ((), ("--che",), ("--unknown=" + TOKEN,), ("--check", "--check=invalid")):
            with self.subTest(extra=extra):
                before = self.fingerprint()
                result = self.run_cli(patch, *extra)
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)["reason"], "invalid_arguments")
                self.assertEqual(result.stderr, b"")
                self.assertNotIn(TOKEN.encode(), result.stdout)
                self.assertEqual(self.fingerprint(), before)

    def test_active_scan_detects_live_drift_without_overwriting_it(self):
        active = self.active_copy("drift")
        scanner = active / ".codex/hooks/scan-secrets.py"
        scanner.write_text(scanner.read_text().replace('if __name__ == "__main__":',
            "Path(" + repr(str(self.target)) + ").write_text('concurrent user edit')\nif __name__ == \"__main__\":"))
        index = (self.repo / ".git/index").read_bytes()
        result = self.run_cli(self.patch("value = 'repaired'\n"), "--check", active=active)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "state_drift")
        self.assertEqual(self.target.read_text(), "concurrent user edit")
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)

    def test_dirty_staged_and_untracked_credentials_are_inspected(self):
        patch = self.patch("value = 'repaired'\n")
        for location in ("untracked", "staged"):
            with self.subTest(location=location):
                control = self.repo / "dirty-control.txt"
                control.write_text(TOKEN)
                if location == "staged":
                    self.git("add", "dirty-control.txt")
                    control.write_text("safe worktree bytes")
                before = self.fingerprint()
                result = self.run_cli(patch, "--check")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(self.fingerprint(), before)
                if location == "staged":
                    self.assertEqual(control.read_text(), "safe worktree bytes")
                control.unlink()

    def test_unresolved_index_is_rejected_without_writes(self):
        self.git("branch", "other")
        for branch, value in (("main", "one"), ("other", "two")):
            self.git("checkout", "-q", branch)
            self.target.write_text("value = '" + value + "'\n")
            self.git("add", "fixture.py")
            self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                     "-c", "commit.gpgsign=false", "commit", "-qm", branch)
        merged = subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=Fixture",
            "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "merge", "main"],
            env=self.env, capture_output=True, timeout=5)
        self.assertEqual(merged.returncode, 1)
        before = self.fingerprint()
        result = self.run_cli(self.patch("value = 'resolved'\n"), "--check")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "unsupported_index")
        self.assertEqual(self.fingerprint(), before)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX special-file case")
    def test_special_file_and_linked_parent_are_rejected(self):
        patch = self.patch("value = 'repaired'\n")
        original = self.target.read_bytes()
        index = (self.repo / ".git/index").read_bytes()
        self.target.unlink()
        os.mkfifo(self.target)
        result = self.run_cli(patch, "--check", timeout=3)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)
        self.target.unlink()
        self.target.write_bytes(original)
        outside = self.base / "outside-directory"
        outside.mkdir()
        (outside / "nested.py").write_bytes(original)
        (self.repo / "linked").symlink_to(outside, target_is_directory=True)
        patch = self.patch("value = 'repaired'\n", path="linked/nested.py")
        result = self.run_cli(patch, "--check", "--path", "linked/nested.py")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual((outside / "nested.py").read_bytes(), original)

    def test_active_bundle_identity_is_independent(self):
        active = self.active_copy("reviewed")
        scanner = active / ".codex/hooks/scan-secrets.py"
        scanner.write_text(scanner.read_text() + "\n# separately reviewed active build\n")
        result = self.run_cli(self.patch("value = 'repaired'\n"), "--check", active=active)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        builds = json.loads(result.stdout)["builds"]
        self.assertNotEqual(builds["active"]["codex"]["bundle"], builds["candidate"]["codex"]["bundle"])

    def test_open_stdin_is_bounded_and_help_does_not_read_it(self):
        before = self.fingerprint()
        for args, expected in ((["--help"], 0), (["--patch", "-", "--path", "fixture.py",
                "--active-hook-root", str(ROOT), "--check", "--json"], 2)):
            with self.subTest(args=args), subprocess.Popen([sys.executable, str(CLI), *args],
                    cwd=self.repo, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                process.wait(timeout=4)
                stdout = process.stdout.read()
                stderr = process.stderr.read()
                self.assertEqual(process.returncode, expected, stdout + stderr)
                self.assertNotIn(b"Traceback", stderr)
                if expected:
                    self.assertEqual(json.loads(stdout)["reason"], "stdin_timeout")
        patch = self.patch("value = 'repaired'\n")
        result = subprocess.run([sys.executable, str(CLI), "--patch", "-", "--path", "fixture.py",
                "--active-hook-root", str(ROOT), "--check", "--json", "--quiet", "--no-color"],
                cwd=self.repo, env={**self.env, "SKIP_SECRETS_SCAN": "true", "SCAN_MODE": "warn",
                    "SECRETS_ALLOWLIST": ".*", "NO_COLOR": "1", "TERM": "dumb"},
                input=patch.read_bytes(), capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["controls_detected"], 6)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(self.fingerprint(), before)

    @unittest.skipIf(os.name == "nt", "POSIX process-group cancellation")
    def test_cancellation_cleans_child_and_preserves_live_state(self):
        active = self.active_copy("cancel")
        marker = self.base / "child-pid"
        scanner = active / ".codex/hooks/scan-secrets.py"
        injection = ("import subprocess\n"
            "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
            "Path(" + repr(str(marker)) + ").write_text(str(child.pid))\n"
            "time.sleep(60)\n")
        scanner.write_text(scanner.read_text().replace('if __name__ == "__main__":', injection + 'if __name__ == "__main__":'))
        patch = self.patch("value = 'repaired'\n")
        before = self.fingerprint()
        with subprocess.Popen([sys.executable, str(CLI), "--patch", str(patch), "--path", "fixture.py",
                "--active-hook-root", str(active), "--check", "--json"], cwd=self.repo, env=self.env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            deadline = time.monotonic() + 6
            while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
                time.sleep(0.02)
            self.assertTrue(marker.exists())
            child = int(marker.read_text())
            process.send_signal(signal.SIGINT)
            stdout, stderr = process.communicate(timeout=4)
            self.assertEqual(process.returncode, 130, stdout + stderr)
            self.assertEqual(json.loads(stdout)["reason"], "interrupted")
            self.assertNotIn(b"Traceback", stderr)
        # A dead process may remain briefly as an orphan zombie; it must never run.
        result = subprocess.run(["ps", "-o", "stat=", "-p", str(child)], capture_output=True, timeout=2)
        self.assertTrue(not result.stdout.strip() or result.stdout.lstrip().startswith(b"Z"), result.stdout)
        self.assertEqual(self.fingerprint(), before)

    def test_failed_committed_head_capture_is_not_treated_as_unborn(self):
        patch = self.patch("value = 'repaired'\n")
        before = self.fingerprint()
        wrapper = self.base / "head-fault.py"
        wrapper.write_text("import subprocess,runpy,sys\n"
            "real = subprocess.Popen\n"
            "def failed(command,*args,**kwargs):\n"
            " if command[-3:] == ['rev-parse','--verify','HEAD']:\n"
            "  command = [sys.executable, '-I', '-S', '-B', '-c', 'raise SystemExit(128)']\n"
            " return real(command,*args,**kwargs)\n"
            "subprocess.Popen = failed\n"
            "sys.argv = [" + repr(str(CLI)) + "] + sys.argv[1:]\n"
            "runpy.run_path(" + repr(str(CLI)) + ", run_name='__main__')\n")
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(wrapper), "--patch", str(patch),
            "--path", "fixture.py", "--active-hook-root", str(ROOT), "--check", "--json"],
            cwd=self.repo, env=self.env, capture_output=True, timeout=25)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_broken_output_pipes_are_bounded_without_tracebacks(self):
        patch = self.patch("value = 'repaired'\n")
        arguments = (["--help"], ["--patch", str(patch), "--path", "fixture.py",
            "--active-hook-root", str(ROOT), "--check", "--json"])
        before = self.fingerprint()
        for args in arguments:
            with self.subTest(args=args), subprocess.Popen([sys.executable, str(CLI), *args],
                    cwd=self.repo, env=self.env, stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                process.stdout.close()
                process.wait(timeout=15)
                stderr = process.stderr.read()
                self.assertNotIn(b"Traceback", stderr)
                self.assertNotIn(b"Exception ignored", stderr)
                self.assertNotEqual(process.returncode, 0)
        self.assertEqual(self.fingerprint(), before)

    def test_source_filter_commands_are_never_executed(self):
        self.target.write_text("value = 'dirt'\n")
        patch = self.patch("value = 'repaired'\n")
        marker = self.base / "filter-executed"
        driver = self.base / "filter.py"
        driver.write_text("import sys\nfrom pathlib import Path\nPath(" + repr(str(marker)) +
                          ").write_text('unexpected execution')\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n")
        (self.repo / ".gitattributes").write_text("fixture.py filter=fixture-preflight\n")
        self.git("config", "filter.fixture-preflight.clean", shlex.join([sys.executable, str(driver)]))
        original = self.target.read_bytes()
        index = (self.repo / ".git/index").read_bytes()
        result = self.run_cli(patch, "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(marker.exists(), "verification executed source Git filter configuration")
        self.assertEqual(self.target.read_bytes(), original)
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)
        result = self.run_cli(self.patch("value = '" + TOKEN + "'\n"), "--check")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "findings")
        self.assertFalse(marker.exists(), "credential inspection executed a source Git filter")
        self.assertEqual(self.target.read_bytes(), original)
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)

    def test_inconsistent_scanner_results_are_incomplete(self):
        original = self.fingerprint()
        for fault in ("clean-findings", "findings-allow", "findings-unsafe-audit"):
            with self.subTest(fault=fault):
                after = "value = 'repaired'\n" if fault == "clean-findings" else "value = '" + TOKEN + "'\n"
                result = self.run_cli(self.patch(after), "--check", active=self.active_copy(fault))
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(self.fingerprint(), original)
                self.assertNotIn(TOKEN.encode(), result.stdout + result.stderr)

    def test_tracked_attributes_preserve_raw_head_and_index(self):
        raw = b"value = 'safe'\r\n"
        self.target.write_bytes(raw)
        (self.repo / ".gitattributes").write_text("fixture.py text\n")
        self.git("add", ".gitattributes")
        oid = subprocess.run(["git", "-C", str(self.repo), "hash-object", "-w", "--stdin"],
                             env=self.env, input=raw, capture_output=True, check=True).stdout.strip().decode()
        self.git("update-index", "--cacheinfo", "100644", oid, "fixture.py")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "raw attributed baseline")
        marker = self.base / "captured-head-bytes"
        active = self.active_copy("raw-head")
        scanner = active / ".codex/hooks/scan-secrets.py"
        injection = ("import subprocess\n"
            "captured = subprocess.run(['git', 'show', 'HEAD:fixture.py'], capture_output=True)\n"
            "if captured.returncode == 0:\n Path(" + repr(str(marker)) + ").write_bytes(captured.stdout)\n")
        scanner.write_text(scanner.read_text().replace('if __name__ == "__main__":', injection + 'if __name__ == "__main__":'))
        before = self.fingerprint()
        patch = self.patch(raw.replace(b"safe", b"repaired").decode(), before=raw.decode())
        result = self.run_cli(patch, "--check", active=active)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(marker.read_bytes(), raw)
        self.assertEqual(self.fingerprint(), before)

    @unittest.skipIf(os.name == "nt", "POSIX canonical Git-session cancellation")
    def test_cancellation_cleans_real_scanner_capture_git_session(self):
        before = self.fingerprint()
        patch = self.patch("value = 'repaired'\n")
        for responsive in (True, False):
            with self.subTest(responsive=responsive):
                label = "responsive-capture" if responsive else "unresponsive-capture"
                active = self.active_copy(label)
                marker = self.base / (label + "-git.json")
                binaries = self.base / (label + "-bin")
                binaries.mkdir()
                fake_git = binaries / "git"
                fake_git.write_text("#!" + sys.executable + "\nimport json,os,time\nfrom pathlib import Path\n"
                    "Path(" + repr(str(marker)) + ").write_text(json.dumps({'pid':os.getpid(), 'parent':os.getppid(), 'group':os.getpgrp(), 'session':os.getsid(0)}))\n"
                    "time.sleep(60)\n")
                fake_git.chmod(0o755)
                scanner = active / ".codex/hooks/scan-secrets.py"
                injection = "os.environ['PATH'] = " + repr(str(binaries)) + " + os.pathsep + os.environ['PATH']\n"
                if not responsive:
                    injection += "signal.signal(signal.SIGINT, signal.SIG_IGN)\n"
                scanner.write_text(scanner.read_text().replace('if __name__ == "__main__":', injection + 'if __name__ == "__main__":'))
                child = None
                try:
                    with subprocess.Popen([sys.executable, str(CLI), "--patch", str(patch), "--path", "fixture.py",
                            "--active-hook-root", str(active), "--check", "--json"], cwd=self.repo, env=self.env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                        deadline = time.monotonic() + 6
                        while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
                            time.sleep(0.02)
                        self.assertTrue(marker.exists(), "the real scanner did not enter protected Git capture")
                        details = json.loads(marker.read_text())
                        child = details["pid"]
                        self.assertEqual(details["group"], child)
                        self.assertEqual(details["session"], child)
                        self.assertNotEqual(details["parent"], child)
                        self.assertNotEqual(os.getpgid(details["parent"]), child)
                        started = time.monotonic()
                        process.send_signal(signal.SIGINT)
                        stdout, stderr = process.communicate(timeout=5)
                        self.assertEqual(process.returncode, 130, stdout + stderr)
                        self.assertLess(time.monotonic() - started, 3)
                        self.assertEqual(json.loads(stdout)["reason"], "interrupted")
                        self.assertNotIn(b"Traceback", stderr)
                    result = subprocess.run(["ps", "-o", "stat=", "-p", str(child)], capture_output=True, timeout=2)
                    self.assertTrue(not result.stdout.strip() or result.stdout.lstrip().startswith(b"Z"),
                                    "canonical capture Git survived preflight cancellation: " + repr(result.stdout))
                    self.assertEqual(self.fingerprint(), before)
                finally:
                    # Assertion occurs before this cleanup, so fixture cleanup
                    # cannot turn a surviving canonical Git child into a pass.
                    if child is not None:
                        try:
                            os.kill(child, signal.SIGKILL)
                        except ProcessLookupError:
                            pass

    def observation_wrapper(self, delay, *, first=0, after=None, seen=None, settle=0, until=None, trigger=None, descendants=(), timings=None, trigger_delay=False, next_observation=None):
        """Delay the real metadata process at the OS process boundary."""
        wrapper = self.base / "observer-wrapper.py"
        observers = self.base / "observer-pids"
        git_started = self.base / "observer-git-started"
        child = ("import os,sys,time\ntime.sleep(" + repr(delay) + ")\n"
                 "os.execv('/bin/ps', ['/bin/ps', *sys.argv[1:]])\n")
        pause_delay = "time.sleep(" + repr(delay) + ")\n"
        pause_settle = "time.sleep(" + repr(settle) + ")\n"
        if seen is not None:
            if trigger_delay:
                self.assertIsNotNone(trigger)
                pause_delay = "time.sleep(" + repr(delay) + " if delayed else 0)\n"
                pause_settle = "time.sleep(" + repr(settle) + " if delayed else 0)\n"
            child = ("import os,sys,time,subprocess\nfrom pathlib import Path\n"
                "delayed = " + ("Path(" + repr(str(trigger)) + ").exists()" if trigger_delay else "True") + "\n"
                + pause_delay +
                "raw = subprocess.check_output(['/bin/ps', *sys.argv[1:]])\n"
                "for marker_name, seen_name in " + repr([(str(after), str(seen)), *[(str(a), str(s)) for a, s in descendants]]) + ":\n"
                " marker = Path(marker_name)\n"
                " if marker.exists() and any(row.split()[:1] == [marker.read_bytes()] for row in raw.splitlines()):\n"
                "  Path(seen_name).touch()\n"
                + pause_settle + "os.write(1, raw)\n")
        timing_source = ""
        if timings is not None:
            # Fixed numeric events only. Each write is short and the diagnostic
            # file is capped; telemetry never alters waits or cleanup policy.
            timing_source = ("import os,json,time\n"
                "timing_fd=os.open(" + repr(str(timings)) + ",os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)\n"
                "def timing(stage,pid=None,at=None):\n"
                " if os.fstat(timing_fd).st_size<16000:\n"
                "  os.write(timing_fd,(json.dumps({'pid':os.getpid() if pid is None else pid,'stage':stage,'at':time.monotonic() if at is None else at})+'\\n').encode())\n")
            child = child.replace(pause_delay,
                "timing('delay_started')\n" + pause_delay + "timing('delay_finished')\n", 1)
            child = child.replace("raw = subprocess.check_output(", "timing('snapshot_started')\nraw = subprocess.check_output(")
            child = child.replace("for marker_name, seen_name in ", "timing('snapshot_finished')\nfor marker_name, seen_name in ")
            child = child.replace(pause_settle,
                "timing('return_delay_started')\n" + pause_settle + "timing('return_delay_finished')\n", 1)
            child = child.replace("os.write(1, raw)", "timing('delivery_started')\nos.write(1, raw)\ntiming('delivery_finished')")
            child = timing_source + "timing('child_entered')\n" + child
        wrapper.write_text(timing_source + "import subprocess,runpy,sys\nfrom pathlib import Path\n"
            "real = subprocess.Popen\nobservations = 0\n"
            "def launched(command,*args,**kwargs):\n"
            " global observations\n"
            " if command[0] == '/bin/ps':\n"
            "  observations += 1\n"
            "  if observations <= " + repr(first) + " or (" + repr(str(after)) +
            " != 'None' and Path(" + repr(str(after)) + ").exists() and (" + repr(str(trigger)) +
            " == 'None' or " + repr(trigger_delay) + " or Path(" + repr(str(trigger)) + ").exists()) and (" + repr(str(until)) +
            " == 'None' or not Path(" + repr(str(until)) + ").exists())):\n"
            "   command = [sys.executable, '-I', '-S', '-B', '-c', " + repr(child) + ", *command[1:]]\n"
            + ("  launch_started=time.monotonic()\n" if timings is not None else "") +
            ("  seen_before_launch = Path(" + repr(str(seen)) + ").exists()\n"
               if next_observation is not None else "") +
            "  process = real(command,*args,**kwargs)\n"
            + ("  if seen_before_launch: Path(" + repr(str(next_observation)) + ").touch()\n"
               if next_observation is not None else "") +
            ("  timing('parent_launch_started',process.pid,launch_started)\n"
               "  timing('parent_launch_completed',process.pid)\n"
               "  real_poll=process.poll;real_wait=process.wait;acknowledged=[False]\n"
               "  def received(code):\n"
               "   if code is not None and not acknowledged[0]:\n"
               "    acknowledged[0]=True;timing('parent_exit_received',process.pid)\n"
               "   return code\n"
               "  process.poll=lambda:received(real_poll())\n"
               "  process.wait=lambda *args,**kwargs:received(real_wait(*args,**kwargs))\n" if timings is not None else "") +
            "  with Path(" + repr(str(observers)) + ").open('a') as stream: stream.write(str(process.pid)+'\\n')\n"
            "  return process\n"
            " if Path(command[0]).name == 'git': Path(" + repr(str(git_started)) + ").touch()\n"
            " return real(command,*args,**kwargs)\n"
            "subprocess.Popen = launched\n"
            "sys.argv = [" + repr(str(CLI)) + "] + sys.argv[1:]\n"
            "runpy.run_path(" + repr(str(CLI)) + ", run_name='__main__')\n")
        return wrapper, observers, git_started

    def report_observer_timings(self, path):
        if path is None or not path.exists():
            return
        # Keep failure output bounded to the last four observers. All fields
        # are fixture-owned enums and numbers; no process command is recorded.
        events = {}
        with path.open('rb') as stream:
            for raw in stream.read(16384).splitlines():
                try:
                    row = json.loads(raw)
                    events.setdefault(row['pid'], []).append(row)
                except (ValueError, KeyError):
                    continue
        for pid, rows in list(events.items())[-4:]:
            rows.sort(key=lambda row: row['at'])
            origin = rows[0]['at']
            print(json.dumps({'fixture_observer': 'stage-timing', 'observer_pid': pid,
                'stages': [{'stage': row['stage'], 'seconds_from_launch': round(row['at'] - origin, 6)}
                           for row in rows]}), flush=True)

    def assert_stopped(self, pids):
        for pid in pids:
            result = subprocess.run(['/bin/ps', '-o', 'stat=', '-p', str(pid)],
                                    capture_output=True, timeout=2)
            self.assertTrue(not result.stdout.strip() or result.stdout.lstrip().startswith(b'Z'),
                            'verifier-owned process survived: ' + str(pid) + ' ' + repr(result.stdout))

    @unittest.skipIf(os.name == "nt", "POSIX real metadata observation")
    def test_real_metadata_observation_allows_ordinary_host_latency_and_bounds_stalls(self):
        before = self.fingerprint()
        patch = self.patch("value = 'repaired'\n")
        for delay, expected in ((0.3, 0), (0.65, 0), (60, 2)):
            with self.subTest(delay=delay):
                wrapper, observers, git_started = self.observation_wrapper(delay, first=2)
                observers.unlink(missing_ok=True)
                git_started.unlink(missing_ok=True)
                started = time.monotonic()
                result = subprocess.run([sys.executable, '-I', '-S', '-B', str(wrapper),
                    '--patch', str(patch), '--path', 'fixture.py', '--active-hook-root', str(ROOT),
                    '--check', '--json', '--no-input'], cwd=self.repo, env=self.env,
                    capture_output=True, timeout=20)
                elapsed = time.monotonic() - started
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                report = json.loads(result.stdout)
                if expected == 0:
                    self.assertEqual(report['result'], 'verified')
                    self.assertEqual(report['controls_detected'], 6)
                    self.assertGreaterEqual(elapsed, 0.6)
                else:
                    self.assertEqual(report['reason'], 'process_observation_timeout')
                    self.assertEqual(report['unit'], 'seconds')
                    self.assertLess(report['limit'], 2)
                    self.assertLess(elapsed, 2)
                    self.assertFalse(git_started.exists())
                self.assertNotIn(TOKEN.encode(), result.stdout + result.stderr)
                self.assertNotIn(b'Traceback', result.stderr)
                self.assertEqual(self.fingerprint(), before)
                pids = [int(pid) for pid in observers.read_text().splitlines()]
                self.assert_stopped(pids)
                print(json.dumps({'fixture_observer': 'ordinary' if not expected else 'stalled',
                    'delay_seconds': delay, 'elapsed_seconds': round(elapsed, 6),
                    'observed_processes_stopped': len(pids)}), flush=True)

    @unittest.skipIf(os.name == "nt", "POSIX metadata observer shutdown")
    def test_denied_stopped_metadata_observer_shutdown_reports_incomplete(self):
        wrapper, observers, git_started = self.observation_wrapper(60, first=1)
        source = wrapper.read_text().replace('real = subprocess.Popen\nobservations = 0\n',
            'real = subprocess.Popen\nobservations = 0\nimport os,signal\nobserver_pid=None\nreal_killpg=os.killpg\n'
            'def guarded_killpg(pid,signum):\n'
            ' if pid==observer_pid and signum==signal.SIGKILL:\n'
            '  real_killpg(pid,signal.SIGSTOP)\n'
            '  raise PermissionError("injected observer signal denial")\n'
            ' return real_killpg(pid,signum)\n'
            'os.killpg=guarded_killpg\n')
        source = source.replace(' global observations\n', ' global observations,observer_pid\n')
        source = source.replace('  process = real(command,*args,**kwargs)\n',
            '  process = real(command,*args,**kwargs)\n'
            '  if observations==1: observer_pid=process.pid\n')
        wrapper.write_text(source)
        before = self.fingerprint()
        observer = None
        identity = None
        try:
            with subprocess.Popen([sys.executable, '-I', '-S', '-B', str(wrapper),
                    '--patch', str(self.patch("value = 'repaired'\n")), '--path', 'fixture.py',
                    '--active-hook-root', str(ROOT), '--check', '--json', '--no-input'],
                    cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                deadline = time.monotonic() + 3
                while not observers.exists() and time.monotonic() < deadline and process.poll() is None:
                    time.sleep(0.01)
                self.assertTrue(observers.exists(), 'metadata observer did not start')
                observer = int(observers.read_text().splitlines()[0])
                identity = subprocess.check_output(['/bin/ps', '-o', 'lstart=', '-p', str(observer)])
                started = time.monotonic()
                process.send_signal(signal.SIGINT)
                stdout, stderr = process.communicate(timeout=4)
                elapsed = time.monotonic() - started
            state = subprocess.run(['/bin/ps', '-o', 'stat=', '-p', str(observer)],
                capture_output=True, timeout=2).stdout.strip()
            print(json.dumps({'fixture_observer': 'denied-stopped-metadata-observer',
                'returncode': process.returncode, 'reason': json.loads(stdout)['reason'],
                'cleanup_seconds': round(elapsed, 6), 'observer_state_before_emergency_cleanup': state.decode()}), flush=True)
            self.assertTrue(state.startswith(b'T'), 'injected observer denial did not leave a stopped observer')
            self.assertEqual(process.returncode, 2, stdout + stderr)
            report = json.loads(stdout)
            self.assertEqual(report['result'], 'rejected')
            self.assertEqual(report['reason'], 'process_cleanup_incomplete')
            self.assertEqual(report['phase'], 'cleanup')
            self.assertFalse(git_started.exists())
            self.assertLess(elapsed, 2)
            self.assertNotIn(b'Traceback', stderr)
            self.assertNotIn(TOKEN.encode(), stdout + stderr)
            self.assertEqual(self.fingerprint(), before)
        finally:
            # Observe the survivor before emergency cleanup. The fresh start
            # identity and unique fixture marker authorize only this child.
            if observer is not None and identity and observers.exists():
                current = subprocess.run(['/bin/ps', '-o', 'lstart=', '-p', str(observer)],
                    capture_output=True, timeout=2).stdout
                if current == identity and observers.read_text().splitlines() == [str(observer)]:
                    try:
                        os.killpg(observer, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    deadline = time.monotonic() + 1
                    while time.monotonic() < deadline:
                        state = subprocess.run(['/bin/ps', '-o', 'stat=', '-p', str(observer)],
                            capture_output=True, timeout=2).stdout.strip()
                        if not state or state.startswith(b'Z'):
                            break
                        time.sleep(0.01)
                    self.assert_stopped([observer])

    @unittest.skipIf(os.name == "nt", "POSIX Linux proc disappearance protocol")
    def test_linux_proc_read_disappearance_preserves_observed_child_cancellation(self):
        self.assert_linux_proc_read_cleanup('esrch')

    @unittest.skipIf(os.name == "nt", "POSIX Linux proc failure protocol")
    def test_linux_proc_read_failures_remain_incomplete_with_safe_categories(self):
        for mode in ('denied', 'io_error', 'empty'):
            with self.subTest(mode=mode):
                self.assert_linux_proc_read_cleanup(mode)

    def assert_linux_proc_read_cleanup(self, mode):
        active = self.active_copy('linux-proc-read-' + mode)
        marker = self.base / ('proc-child-pid-' + mode)
        sampled = self.base / ('proc-child-sampled-' + mode)
        reaped = self.base / ('proc-child-reaped-' + mode)
        injected = self.base / ('proc-read-injected-' + mode)
        parent_marker = self.base / ('proc-parent-pid-' + mode)
        child_code = ('import time\nfrom pathlib import Path\n'
            'while not Path(' + repr(str(sampled)) + ').exists(): time.sleep(0.005)\n')
        scanner = active / '.codex/hooks/scan-secrets.py'
        injection = ('import subprocess\nsignal.signal(signal.SIGINT,signal.SIG_IGN)\n'
            'Path(' + repr(str(parent_marker)) + ').write_text(str(os.getpid()))\n'
            'child=subprocess.Popen([sys.executable,"-c",' + repr(child_code) + '])\n'
            'Path(' + repr(str(marker)) + ').write_text(str(child.pid))\n'
            'child.wait()\nPath(' + repr(str(reaped)) + ').touch()\ntime.sleep(60)\n')
        scanner.write_text(scanner.read_text().replace('if __name__ == "__main__":', injection + 'if __name__ == "__main__":'))
        wrapper, observers, _ = self.observation_wrapper(0, after=marker, seen=sampled, until=sampled)
        # The CLI launches its unchanged Linux helper/protocol. On other POSIX
        # hosts, numeric /proc fixtures come from real targeted ps records.
        # ESRCH is injected at read only after the real observed child was reaped.
        fault = ("import builtins,io,errno,os,sys,time,subprocess\nfrom pathlib import Path\n"
            "host=sys.platform;sys.platform='linux'\nreal_open=builtins.open;real_sysconf=os.sysconf\n"
            "class Gone(io.BytesIO):\n"
            " def read(self,*args):\n"
            "  Path(" + repr(str(injected)) + ").touch()\n"
            "  if " + repr(mode) + "=='empty': return b''\n"
            "  raise OSError(" + {'esrch': 'errno.ESRCH', 'denied': 'errno.EACCES', 'io_error': 'errno.EIO', 'empty': '0'}[mode] + ", 'injected proc read result')\n"
            "def opened(name,*args,**kwargs):\n"
            " if isinstance(name,str) and name.startswith('/proc/') and name.endswith('/stat') and name.split('/')[2].isdigit():\n"
            "  pid=int(name.split('/')[2])\n"
            "  raw=subprocess.run(['/bin/ps','-o','pid=,ppid=,pgid=,lstart=,stat=','-p',str(pid)],capture_output=True,check=False).stdout\n"
            "  if not raw.strip():\n"
            "   if Path(" + repr(str(reaped)) + ").exists() and pid==int(Path(" + repr(str(marker)) + ").read_text()): return Gone()\n"
            "   raise FileNotFoundError(errno.ENOENT,'absent fixture process')\n"
            "  if host.startswith('linux'): return real_open(name,*args,**kwargs)\n"
            "  row=raw.split();seconds=int(time.mktime(time.strptime(b' '.join(row[3:8]).decode(),'%a %b %d %H:%M:%S %Y')))\n"
            "  fields=[row[8][:1],row[1],row[2],*([b'0']*16),str((seconds-1700000000)*100).encode()]\n"
            "  return io.BytesIO(str(pid).encode()+b' (fixture) '+b' '.join(fields)+b'\\n')\n"
            " if host!='linux' and name=='/proc/stat': return io.BytesIO(b'btime 1700000000\\n')\n"
            " return real_open(name,*args,**kwargs)\n"
            "builtins.open=opened\n"
            "os.sysconf=lambda name:100 if name=='SC_CLK_TCK' and not host.startswith('linux') else real_sysconf(name)\n")
        source = wrapper.read_text().replace(" if command[0] == '/bin/ps':\n",
            " if any('fixture_process_helper' in str(part) for part in command): command=[*command[:-1]," + repr(fault) + "+command[-1]]\n"
            " if command[0] == '/bin/ps':\n")
        wrapper.write_text(source)
        before = self.fingerprint()
        with subprocess.Popen([sys.executable, '-I', '-S', '-B', str(wrapper),
                '--patch', str(self.patch("value = 'repaired'\n")), '--path', 'fixture.py',
                '--active-hook-root', str(active), '--check', '--json', '--no-input'],
                cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            deadline = time.monotonic() + 6
            while not reaped.exists() and time.monotonic() < deadline and process.poll() is None:
                time.sleep(0.01)
            self.assertTrue(reaped.exists(), 'observed scanner child was not reaped: ' + repr(process.communicate(timeout=1) if process.poll() is not None else process.returncode))
            started = time.monotonic()
            process.send_signal(signal.SIGINT)
            stdout, stderr = process.communicate(timeout=4)
            elapsed = time.monotonic() - started
        self.assertTrue(injected.exists(), 'Linux descriptor read result was not exercised')
        self.assert_stopped([int(parent_marker.read_text()), int(marker.read_text()), *map(int, observers.read_text().splitlines())])
        self.assertEqual(self.fingerprint(), before)
        print(json.dumps({'fixture_observer': 'linux-proc-read-' + mode, 'returncode': process.returncode,
            'reason': json.loads(stdout)['reason'], 'native_cause': json.loads(stdout).get('native_cause'),
            'cleanup_seconds': round(elapsed, 6)}), flush=True)
        self.assertEqual(process.returncode, 130 if mode == 'esrch' else 2, stdout + stderr)
        report = json.loads(stdout)
        self.assertEqual(report['reason'], 'interrupted' if mode == 'esrch' else 'process_observation_native_unavailable')
        if mode != 'esrch':
            self.assertEqual(report.get('native_cause'), {'denied': 'denied', 'io_error': 'read_error', 'empty': 'invalid_record'}[mode])
        self.assertLess(elapsed, 2)
        self.assertNotIn(b'Traceback', stderr)
        self.assertNotIn(TOKEN.encode(), stdout + stderr)

    @unittest.skipIf(os.name == "nt", "POSIX observed descendant cancellation")
    def test_delayed_metadata_cleanup_stops_resistant_separate_session(self):
        self.assert_resistant_session_cleanup(0.3)

    @unittest.skipIf(os.name == "nt", "POSIX observed descendant cancellation")
    def test_slower_metadata_cleanup_preserves_cancellation_deadline(self):
        self.assert_resistant_session_cleanup(0.65)

    @unittest.skipIf(os.name == "nt", "POSIX observed descendant cancellation")
    def test_cancellation_during_metadata_return_shares_cleanup_deadline(self):
        self.assert_resistant_session_cleanup(0.3, settle=0.55)

    @unittest.skipIf(os.name == "nt", "POSIX observed descendant cancellation")
    def test_cleanup_observation_uses_remaining_shared_shutdown_budget(self):
        # The next ordinary observer launch acknowledges that the earlier
        # snapshot containing the child was consumed before cancellation.
        # Only the required fresh cleanup graph carries the 1.0-second delay.
        self.assert_resistant_session_cleanup(0.3, settle=0.7, delayed_cleanup=True)

    def assert_resistant_session_cleanup(self, delay, *, settle=0, delayed_cleanup=False):
        active = self.active_copy("slow-observer-cancel")
        marker = self.base / 'slow-observer-child'
        observed = self.base / 'child-observed-before-setsid'
        ready = self.base / 'child-session-ready'
        scanner = active / '.codex/hooks/scan-secrets.py'
        child_code = ('import os,signal,time\nfrom pathlib import Path\n'
                      'signal.signal(signal.SIGINT,signal.SIG_IGN)\n'
                      'signal.signal(signal.SIGTERM,signal.SIG_IGN)\n'
                      'while not Path(' + repr(str(observed)) + ').exists(): time.sleep(0.01)\n'
                      'os.setsid()\nPath(' + repr(str(ready)) + ').touch()\ntime.sleep(60)')
        injection = ("import subprocess\n"
            "signal.signal(signal.SIGINT, signal.SIG_IGN)\n"
            "child = subprocess.Popen([sys.executable, '-c', " + repr(child_code) + "])\n"
            "Path(" + repr(str(marker)) + ").write_text(str(child.pid))\n"
            "time.sleep(60)\n")
        scanner.write_text(scanner.read_text().replace('if __name__ == "__main__":', injection + 'if __name__ == "__main__":'))
        timings = self.base / 'delayed-return-observer-timings.jsonl' if settle else None
        trigger = self.base / 'delay-cleanup-observer' if delayed_cleanup else None
        next_observation = self.base / 'child-snapshot-consumed' if delayed_cleanup else None
        wrapper, observers, _ = self.observation_wrapper(delay, after=marker, seen=observed,
            settle=settle, timings=timings, trigger=trigger, trigger_delay=delayed_cleanup,
            next_observation=next_observation)
        before = self.fingerprint()
        patch = self.patch("value = 'repaired'\n")
        child = None
        try:
            with subprocess.Popen([sys.executable, '-I', '-S', '-B', str(wrapper),
                    '--patch', str(patch), '--path', 'fixture.py', '--active-hook-root', str(active),
                    '--check', '--json', '--no-input'], cwd=self.repo, env=self.env,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                deadline = time.monotonic() + 6
                while (not ready.exists() or next_observation is not None and not next_observation.exists()) and time.monotonic() < deadline and process.poll() is None:
                    time.sleep(0.02)
                if marker.exists():
                    child = int(marker.read_text())
                self.assertTrue(ready.exists(), 'real scanner child did not change session after metadata observation')
                if next_observation is not None:
                    self.assertTrue(next_observation.exists(), 'normal observer did not acknowledge the known child')
                    trigger.touch()
                started = time.monotonic()
                process.send_signal(signal.SIGINT)
                stdout, stderr = process.communicate(timeout=4)
                elapsed = time.monotonic() - started
                self.report_observer_timings(timings)
                self.assertEqual(process.returncode, 130, stdout + stderr)
                self.assertEqual(json.loads(stdout)['reason'], 'interrupted')
                self.assertLess(elapsed, 2)
                self.assertNotIn(b'Traceback', stderr)
                self.assertNotIn(TOKEN.encode(), stdout + stderr)
            pids = [int(pid) for pid in observers.read_text().splitlines()]
            self.assert_stopped([child, *pids])
            self.assertEqual(self.fingerprint(), before)
            print(json.dumps({'fixture_observer': 'resistant-child-cancellation',
                'delay_seconds': delay, 'return_delay_seconds': settle, 'cleanup_seconds': round(elapsed, 6),
                'observed_processes_stopped': len(pids) + 1}), flush=True)
        finally:
            # Cleanup follows leak assertions, so it cannot turn a leak into a pass.
            if child is not None:
                try:
                    os.kill(child, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    @unittest.skipIf(os.name == "nt", "POSIX observed descendant cancellation")
    def test_cancellation_discovers_child_spawned_after_inflight_snapshot(self):
        active = self.active_copy("spawn-after-snapshot")
        marker = self.base / 'parent-pid'
        observed = self.base / 'parent-observed'
        ready = self.base / 'new-child-pid'
        child_code = ('import signal,time\n'
            'signal.signal(signal.SIGINT,signal.SIG_IGN)\n'
            'signal.signal(signal.SIGTERM,signal.SIG_IGN)\ntime.sleep(60)\n')
        injection = ('import subprocess\nsignal.signal(signal.SIGINT,signal.SIG_IGN)\n'
            'Path(' + repr(str(marker)) + ').write_text(str(os.getpid()))\n'
            'while not Path(' + repr(str(observed)) + ').exists(): time.sleep(0.005)\n'
            'child=subprocess.Popen([sys.executable,"-c",' + repr(child_code) + '],start_new_session=True)\n'
            'Path(' + repr(str(ready)) + ').write_text(str(child.pid))\ntime.sleep(60)\n')
        scanner = active / '.codex/hooks/scan-secrets.py'
        scanner.write_text(scanner.read_text().replace('if __name__ == "__main__":', injection + 'if __name__ == "__main__":'))
        wrapper, observers, _ = self.observation_wrapper(0.3, after=marker,
            seen=observed, settle=0.55, until=observed)
        before = self.fingerprint()
        child = None
        identity = None
        try:
            with subprocess.Popen([sys.executable, '-I', '-S', '-B', str(wrapper),
                    '--patch', str(self.patch("value = 'repaired'\n")), '--path', 'fixture.py',
                    '--active-hook-root', str(active), '--check', '--json', '--no-input'],
                    cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                deadline = time.monotonic() + 6
                while not ready.exists() and time.monotonic() < deadline and process.poll() is None:
                    time.sleep(0.01)
                self.assertTrue(ready.exists(), 'scanner did not spawn child after metadata capture')
                child = int(ready.read_text())
                identity = subprocess.check_output(['/bin/ps', '-o', 'lstart=', '-p', str(child)])
                started = time.monotonic()
                process.send_signal(signal.SIGINT)
                stdout, stderr = process.communicate(timeout=4)
                elapsed = time.monotonic() - started
                self.assertEqual(process.returncode, 130, stdout + stderr)
                self.assertEqual(json.loads(stdout)['reason'], 'interrupted')
                self.assertLess(elapsed, 2)
                self.assertNotIn(b'Traceback', stderr)
                self.assertNotIn(TOKEN.encode(), stdout + stderr)
            pids = [int(pid) for pid in observers.read_text().splitlines()]
            self.assert_stopped([child, *pids])
            self.assertEqual(self.fingerprint(), before)
            print(json.dumps({'fixture_observer': 'child-spawned-after-snapshot',
                'cleanup_seconds': round(elapsed, 6),
                'observed_processes_stopped': len(pids) + 1}), flush=True)
        finally:
            # Check the leak first; emergency fixture cleanup verifies identity.
            if child is not None and identity:
                current = subprocess.run(['/bin/ps', '-o', 'lstart=', '-p', str(child)],
                    capture_output=True, timeout=2).stdout
                if current == identity:
                    try:
                        os.kill(child, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    @unittest.skipIf(os.name == "nt", "POSIX observed descendant cancellation")
    def test_cancellation_retains_separate_ancestor_until_descendants_discovered(self):
        active = self.active_copy("grandchild-after-snapshot")
        marker = self.base / 'separate-ancestor-pid'
        sampled = self.base / 'ancestor-sampled-after-cancel'
        trigger = self.base / 'cancel-trigger'
        ready = self.base / 'new-grandchild-pid'
        child_code = ('import signal,time\nsignal.signal(signal.SIGINT,signal.SIG_IGN)\n'
            'signal.signal(signal.SIGTERM,signal.SIG_IGN)\ntime.sleep(60)\n')
        ancestor_code = ('import subprocess,sys,signal,time\nfrom pathlib import Path\n'
            'signal.signal(signal.SIGINT,signal.SIG_IGN)\nsignal.signal(signal.SIGTERM,signal.SIG_IGN)\n'
            'while not Path(' + repr(str(sampled)) + ').exists(): time.sleep(0.005)\n'
            'child=subprocess.Popen([sys.executable,"-c",' + repr(child_code) + '],start_new_session=True)\n'
            'Path(' + repr(str(ready)) + ').write_text(str(child.pid))\ntime.sleep(60)\n')
        injection = ('import subprocess\nsignal.signal(signal.SIGINT,signal.SIG_IGN)\n'
            'child=subprocess.Popen([sys.executable,"-c",' + repr(ancestor_code) + '],start_new_session=True)\n'
            'Path(' + repr(str(marker)) + ').write_text(str(child.pid))\ntime.sleep(60)\n')
        scanner = active / '.codex/hooks/scan-secrets.py'
        scanner.write_text(scanner.read_text().replace('if __name__ == "__main__":', injection + 'if __name__ == "__main__":'))
        wrapper, observers, _ = self.observation_wrapper(0, after=marker,
            seen=sampled, settle=0.55, until=sampled, trigger=trigger)
        before = self.fingerprint()
        identities = {}
        try:
            with subprocess.Popen([sys.executable, '-I', '-S', '-B', str(wrapper),
                    '--patch', str(self.patch("value = 'repaired'\n")), '--path', 'fixture.py',
                    '--active-hook-root', str(active), '--check', '--json', '--no-input'],
                    cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                deadline = time.monotonic() + 6
                while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
                    time.sleep(0.01)
                self.assertTrue(marker.exists(), 'separate-session ancestor did not start')
                ancestor = int(marker.read_text())
                identities[ancestor] = subprocess.check_output(['/bin/ps', '-o', 'lstart=', '-p', str(ancestor)])
                time.sleep(0.2)
                trigger.touch()
                started = time.monotonic()
                process.send_signal(signal.SIGINT)
                stdout, stderr = process.communicate(timeout=4)
                elapsed = time.monotonic() - started
                self.assertEqual(process.returncode, 130, stdout + stderr)
                self.assertEqual(json.loads(stdout)['reason'], 'interrupted')
                self.assertLess(elapsed, 2)
                self.assertNotIn(b'Traceback', stderr)
                self.assertNotIn(TOKEN.encode(), stdout + stderr)
            children = [ancestor]
            if ready.exists():
                child = int(ready.read_text())
                identities[child] = subprocess.run(['/bin/ps', '-o', 'lstart=', '-p', str(child)],
                    capture_output=True, timeout=2).stdout
                children.append(child)
            pids = [int(pid) for pid in observers.read_text().splitlines()]
            self.assert_stopped([*children, *pids])
            self.assertEqual(self.fingerprint(), before)
            print(json.dumps({'fixture_observer': 'grandchild-after-fresh-snapshot',
                'cleanup_seconds': round(elapsed, 6), 'spawn_prevented': not ready.exists(),
                'observed_processes_stopped': len(children) + len(pids)}), flush=True)
        finally:
            for pid, identity in identities.items():
                current = subprocess.run(['/bin/ps', '-o', 'lstart=', '-p', str(pid)],
                    capture_output=True, timeout=2).stdout
                if identity and current == identity:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    @unittest.skipIf(os.name == "nt", "POSIX observed descendant cancellation")
    def test_cancellation_discovers_descendants_created_during_successive_scans(self):
        active = self.active_copy("successive-descendants")
        root_marker = self.base / 'cascade-root'
        root_seen = self.base / 'cascade-root-seen'
        markers = [self.base / ('cascade-pid-' + str(n)) for n in range(3)]
        seen = [self.base / ('cascade-seen-' + str(n)) for n in range(2)]
        code = 'import signal,time\nsignal.signal(signal.SIGINT,signal.SIG_IGN)\nsignal.signal(signal.SIGTERM,signal.SIG_IGN)\ntime.sleep(60)\n'
        for number in (1, 0):
            code = ('import subprocess,sys,signal,time\nfrom pathlib import Path\n'
                'signal.signal(signal.SIGINT,signal.SIG_IGN)\nsignal.signal(signal.SIGTERM,signal.SIG_IGN)\n'
                'while not Path(' + repr(str(seen[number])) + ').exists(): time.sleep(0.005)\n'
                'child=subprocess.Popen([sys.executable,"-c",' + repr(code) + '],start_new_session=True)\n'
                'Path(' + repr(str(markers[number + 1])) + ').write_text(str(child.pid))\ntime.sleep(60)\n')
        injection = ('import subprocess\nsignal.signal(signal.SIGINT,signal.SIG_IGN)\n'
            'Path(' + repr(str(root_marker)) + ').write_text(str(os.getpid()))\n'
            'while not Path(' + repr(str(root_seen)) + ').exists(): time.sleep(0.005)\n'
            'child=subprocess.Popen([sys.executable,"-c",' + repr(code) + '],start_new_session=True)\n'
            'Path(' + repr(str(markers[0])) + ').write_text(str(child.pid))\ntime.sleep(60)\n')
        scanner = active / '.codex/hooks/scan-secrets.py'
        scanner.write_text(scanner.read_text().replace('if __name__ == "__main__":', injection + 'if __name__ == "__main__":'))
        wrapper, observers, _ = self.observation_wrapper(0, after=root_marker,
            seen=root_seen, settle=0.2, until=seen[1], descendants=tuple(zip(markers, seen)))
        before = self.fingerprint()
        identities = {}
        try:
            with subprocess.Popen([sys.executable, '-I', '-S', '-B', str(wrapper),
                    '--patch', str(self.patch("value = 'repaired'\n")), '--path', 'fixture.py',
                    '--active-hook-root', str(active), '--check', '--json', '--no-input'],
                    cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                deadline = time.monotonic() + 6
                while not markers[0].exists() and time.monotonic() < deadline and process.poll() is None:
                    time.sleep(0.005)
                self.assertTrue(markers[0].exists(), 'first separate ancestor did not start')
                started = time.monotonic()
                process.send_signal(signal.SIGINT)
                stdout, stderr = process.communicate(timeout=4)
                elapsed = time.monotonic() - started
                self.assertIn(process.returncode, (130, 2), stdout + stderr)
                report = json.loads(stdout)
                if process.returncode == 130:
                    self.assertEqual(report['reason'], 'interrupted')
                else:
                    self.assertEqual(report['result'], 'rejected')
                    self.assertIn(report['phase'], ('cleanup', 'cancellation'))
                self.assertLess(elapsed, 2)
                self.assertNotIn(b'Traceback', stderr)
                self.assertNotIn(TOKEN.encode(), stdout + stderr)
            children = []
            for marker in markers:
                if marker.exists():
                    pid = int(marker.read_text())
                    identities[pid] = subprocess.run(['/bin/ps', '-o', 'lstart=', '-p', str(pid)],
                        capture_output=True, timeout=2).stdout
                    children.append(pid)
            self.assertTrue(markers[1].exists(), 'second generation was not created during discovery')
            self.assertTrue(markers[2].exists(), 'third generation was not created during the next discovery scan')
            pids = [int(pid) for pid in observers.read_text().splitlines()]
            self.assert_stopped([*children, *pids])
            self.assertEqual(self.fingerprint(), before)
            print(json.dumps({'fixture_observer': 'successive-descendant-discovery',
                'cleanup_seconds': round(elapsed, 6), 'generations': len(children),
                'result': report['reason']}), flush=True)
        finally:
            for pid, identity in identities.items():
                current = subprocess.run(['/bin/ps', '-o', 'lstart=', '-p', str(pid)],
                    capture_output=True, timeout=2).stdout
                if identity and current == identity:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def native_wrapper(self, mode, *, active=False):
        wrapper = self.base / 'native-wrapper.py'
        marker = self.base / 'native-git-started'
        pids = self.base / 'native-pids'
        fault = ("import json,os,time\nreal_dumps=json.dumps\n"
            "def encoded(value,*args,**kwargs):\n"
            " if isinstance(value,dict) and any(key.isdigit() and int(key)!=os.getppid() for key in value):\n"
            "  if " + repr(mode) + " == 'stall': time.sleep(60)\n"
            "  if " + repr(mode) + " == 'denied': value={'error':'native_query_denied'}\n"
            "  if " + repr(mode) + " == 'absent': value={key:None for key in value}\n"
            "  if " + repr(mode) + " == 'mismatch':\n"
            "   for row in value.values():\n"
            "    if isinstance(row,list): row[3]+=60\n"
            " return real_dumps(value,*args,**kwargs)\n"
            "json.dumps=encoded\n")
        response = {'absent': '{}', 'denied': '{"error":"native_query_denied"}', 'invalid': '[]'}.get(mode, '{}')
        fake = ('import time;time.sleep(60)' if mode == 'stall'
                else 'import json,sys;print(json.dumps({str(pid):None for pid in json.loads(sys.stdin.readline())}),flush=True);import time;time.sleep(60)' if mode == 'absent'
                else 'import time;print(' + repr(response) + ',flush=True);time.sleep(60)')
        wrapper.write_text("import subprocess,runpy,sys\nfrom pathlib import Path\n"
            "real=subprocess.Popen\n"
            "def launched(command,*args,**kwargs):\n"
            " if any('fixture_process_helper' in str(part) for part in command):\n"
            "  if " + repr(active) + ": command=[*command[:-1]," + repr(fault) + "+command[-1]]\n"
            "  else: command=[sys.executable,'-I','-S','-B','-c'," + repr(fake) + "]\n"
            " elif Path(command[0]).name=='git':\n"
            "  Path(" + repr(str(marker)) + ").touch()\n"
            "  if " + repr(active) + ": command=[sys.executable,'-I','-S','-B','-c','import signal,time;signal.signal(signal.SIGINT,signal.SIG_IGN);time.sleep(60)']\n"
            " process=real(command,*args,**kwargs)\n"
            " with Path(" + repr(str(pids)) + ").open('a') as stream: stream.write(str(process.pid)+'\\n')\n"
            " return process\n"
            "subprocess.Popen=launched\n"
            "sys.argv=[" + repr(str(CLI)) + "]+sys.argv[1:]\n"
            "runpy.run_path(" + repr(str(CLI)) + ",run_name='__main__')\n")
        return wrapper, marker, pids

    @unittest.skipIf(os.name == "nt", "POSIX native identity query")
    def test_native_query_failure_and_stall_stop_before_git(self):
        before = self.fingerprint()
        for mode in ('denied', 'invalid', 'absent', 'stall'):
            with self.subTest(mode=mode):
                wrapper, marker, pids = self.native_wrapper(mode)
                marker.unlink(missing_ok=True)
                pids.unlink(missing_ok=True)
                started = time.monotonic()
                result = subprocess.run([sys.executable, '-I', '-S', '-B', str(wrapper),
                    '--patch', str(self.patch("value = 'repaired'\n")), '--path', 'fixture.py',
                    '--active-hook-root', str(ROOT), '--check', '--json', '--no-input'],
                    cwd=self.repo, env=self.env, capture_output=True, timeout=4)
                self.assertLess(time.monotonic() - started, 2)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertTrue(json.loads(result.stdout)['reason'].startswith('process_observation_'))
                self.assertFalse(marker.exists())
                self.assertNotIn(b'Traceback', result.stderr)
                self.assertNotIn(TOKEN.encode(), result.stdout + result.stderr)
                self.assert_stopped([int(pid) for pid in pids.read_text().splitlines()])
                self.assertEqual(self.fingerprint(), before)

    @unittest.skipIf(os.name == "nt", "POSIX native identity query")
    def test_native_cleanup_query_failure_stall_and_identity_mismatch_are_incomplete(self):
        before = self.fingerprint()
        for mode in ('denied', 'stall', 'mismatch', 'absent'):
            with self.subTest(mode=mode):
                wrapper, marker, pids = self.native_wrapper(mode, active=True)
                marker.unlink(missing_ok=True)
                pids.unlink(missing_ok=True)
                with subprocess.Popen([sys.executable, '-I', '-S', '-B', str(wrapper),
                        '--patch', str(self.patch("value = 'repaired'\n")), '--path', 'fixture.py',
                        '--active-hook-root', str(ROOT), '--check', '--json', '--no-input'],
                        cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                    deadline = time.monotonic() + 3
                    while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
                        time.sleep(0.01)
                    self.assertTrue(marker.exists(), 'bounded child did not start after healthy native preflight')
                    time.sleep(0.2)
                    started = time.monotonic()
                    process.send_signal(signal.SIGINT)
                    stdout, stderr = process.communicate(timeout=4)
                    self.assertLess(time.monotonic() - started, 2)
                    self.assertEqual(process.returncode, 2, stdout + stderr)
                    expected = ('process_observation_identity_mismatch' if mode == 'mismatch'
                        else 'process_observation_timeout' if mode == 'stall'
                        else 'process_observation_native_unavailable')
                    self.assertEqual(json.loads(stdout)['reason'], expected)
                    self.assertNotIn(b'Traceback', stderr)
                    self.assertNotIn(TOKEN.encode(), stdout + stderr)
                self.assert_stopped([int(pid) for pid in pids.read_text().splitlines()])
                self.assertEqual(self.fingerprint(), before)

    @unittest.skipIf(os.name == "nt", "POSIX native helper shutdown")
    def test_denied_stopped_native_helper_shutdown_reports_incomplete(self):
        wrapper, marker, pids = self.native_wrapper('healthy', active=True)
        helper_marker = self.base / 'denied-helper-pid'
        source = wrapper.read_text().replace('real=subprocess.Popen\n',
            'real=subprocess.Popen\nimport os,signal\nhelper_pid=None\nreal_killpg=os.killpg\n'
            'def guarded_killpg(pid,signum):\n'
            ' if pid==helper_pid and signum==signal.SIGKILL:\n'
            '  real_killpg(pid,signal.SIGSTOP)\n'
            '  raise PermissionError("injected helper signal denial")\n'
            ' return real_killpg(pid,signum)\n'
            'os.killpg=guarded_killpg\n')
        source = source.replace('def launched(command,*args,**kwargs):\n',
            'def launched(command,*args,**kwargs):\n global helper_pid\n')
        source = source.replace(' process=real(command,*args,**kwargs)\n',
            ' process=real(command,*args,**kwargs)\n'
            ' if any("fixture_process_helper" in str(part) for part in command):\n'
            '  helper_pid=process.pid\n'
            '  Path(' + repr(str(helper_marker)) + ').write_text(str(process.pid))\n')
        wrapper.write_text(source)
        before = self.fingerprint()
        helper = None
        identity = None
        try:
            with subprocess.Popen([sys.executable, '-I', '-S', '-B', str(wrapper),
                    '--patch', str(self.patch("value = 'repaired'\n")), '--path', 'fixture.py',
                    '--active-hook-root', str(ROOT), '--check', '--json', '--no-input'],
                    cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                deadline = time.monotonic() + 3
                while (not marker.exists() or not helper_marker.exists()) and time.monotonic() < deadline and process.poll() is None:
                    time.sleep(0.01)
                self.assertTrue(marker.exists() and helper_marker.exists(), 'native helper and bounded child did not start')
                helper = int(helper_marker.read_text())
                identity = subprocess.check_output(['/bin/ps', '-o', 'lstart=', '-p', str(helper)])
                time.sleep(0.2)
                started = time.monotonic()
                process.send_signal(signal.SIGINT)
                stdout, stderr = process.communicate(timeout=4)
                elapsed = time.monotonic() - started
            state = subprocess.run(['/bin/ps', '-o', 'stat=', '-p', str(helper)],
                capture_output=True, timeout=2).stdout.strip()
            print(json.dumps({'fixture_observer': 'denied-stopped-native-helper',
                'returncode': process.returncode, 'reason': json.loads(stdout)['reason'],
                'cleanup_seconds': round(elapsed, 6), 'helper_state_before_emergency_cleanup': state.decode()}), flush=True)
            self.assertTrue(state.startswith(b'T'), 'injected helper denial did not leave a stopped helper')
            self.assertEqual(process.returncode, 2, stdout + stderr)
            report = json.loads(stdout)
            self.assertEqual(report['result'], 'rejected')
            self.assertEqual(report['reason'], 'process_cleanup_incomplete')
            self.assertEqual(report['phase'], 'cleanup')
            self.assertLess(elapsed, 2)
            self.assertNotIn(b'Traceback', stderr)
            self.assertNotIn(TOKEN.encode(), stdout + stderr)
            self.assert_stopped([int(pid) for pid in pids.read_text().splitlines() if int(pid) != helper])
            self.assertEqual(self.fingerprint(), before)
        finally:
            # The fault and incomplete result are observed before emergency
            # cleanup; only the same freshly verified helper identity is killed.
            if helper is not None and identity:
                current = subprocess.run(['/bin/ps', '-o', 'lstart=', '-p', str(helper)],
                    capture_output=True, timeout=2).stdout
                if current == identity:
                    try:
                        os.killpg(helper, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    deadline = time.monotonic() + 1
                    while time.monotonic() < deadline:
                        state = subprocess.run(['/bin/ps', '-o', 'stat=', '-p', str(helper)],
                            capture_output=True, timeout=2).stdout.strip()
                        if not state or state.startswith(b'Z'):
                            break
                        time.sleep(0.01)
                    self.assert_stopped([helper])

    def test_linux_native_process_protocol_validates_targeted_proc_records(self):
        fields = ['T', '100', '4321', *(['0'] * 16), '123456']
        valid = b'4321 (name with ) spaces) ' + ' '.join(fields).encode() + b'\n'
        for mode in ('valid', 'absent', 'open_esrch', 'read_esrch', 'denied', 'read_denied', 'read_error', 'empty', 'short', 'wrong_pid', 'unknown_state', 'invalid_group'):
            with self.subTest(mode=mode):
                raw = (b'4322' + valid[4:] if mode == 'wrong_pid' else
                    valid.replace(b') T ', b') Q ') if mode == 'unknown_state' else
                    b'4321 (short) T 100' if mode == 'short' else
                    b'' if mode == 'empty' else
                    valid.replace(b') T 100 4321 ', b') T 100 -1 ') if mode == 'invalid_group' else valid)
                code = ("import runpy,sys,os,time,io,builtins,errno\n"
                    "scope=runpy.run_path(" + repr(str(CLI)) + ",run_name='fixture_process_helper')\n"
                    "os.environ['TZ']='UTC';time.tzset();sys.platform='linux'\n"
                    "real_open=builtins.open;real_sysconf=os.sysconf\n"
                    "class FailedRead(io.BytesIO):\n"
                    " def read(self,*args): raise OSError({'read_esrch':errno.ESRCH,'read_denied':errno.EACCES,'read_error':errno.EIO}[" + repr(mode) + "],'injected proc read failure')\n"
                    "def opened(name,*args,**kwargs):\n"
                    " if name=='/proc/stat': return io.BytesIO(b'btime 1700000000\\n')\n"
                    " if name=='/proc/4321/stat':\n"
                    "  if " + repr(mode) + " == 'absent': raise FileNotFoundError\n"
                    "  if " + repr(mode) + " == 'open_esrch': raise ProcessLookupError(errno.ESRCH,'injected proc open absence')\n"
                    "  if " + repr(mode) + " == 'denied': raise PermissionError(errno.EACCES,'injected proc denial')\n"
                    "  if " + repr(mode) + " in ('read_esrch','read_denied','read_error'): return FailedRead()\n"
                    "  return io.BytesIO(" + repr(raw) + ")\n"
                    " return real_open(name,*args,**kwargs)\n"
                    "builtins.open=opened\n"
                    "os.sysconf=lambda name:100 if name=='SC_CLK_TCK' else real_sysconf(name)\n"
                    "scope['process_query_helper']()\n")
                result = subprocess.run([sys.executable, '-I', '-S', '-B', '-c', code],
                    input=b'[4321]\n', capture_output=True, timeout=2)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                if mode == 'valid':
                    self.assertEqual(report, {'4321': [4321, 100, 4321, 1700001234, 123456, 'stopped', 0]})
                elif mode in ('absent', 'open_esrch', 'read_esrch'):
                    self.assertEqual(report, {'4321': None})
                else:
                    cause = 'denied' if mode in ('denied', 'read_denied') else 'read_error' if mode == 'read_error' else 'invalid_record'
                    self.assertEqual(report, {'error': 'native_query_unavailable', 'cause': cause})

    def test_darwin_native_process_protocol_rejects_partial_or_denied_records(self):
        for mode in ('valid', 'absent', 'denied', 'partial', 'wrong_pid', 'unknown_state'):
            with self.subTest(mode=mode):
                code = ("import runpy,sys,os,time,ctypes,errno\n"
                    "scope=runpy.run_path(" + repr(str(CLI)) + ",run_name='fixture_process_helper')\n"
                    "os.environ['TZ']='UTC';time.tzset();sys.platform='darwin'\n"
                    "class Query:\n"
                    " def __call__(self,pid,flavor,arg,buffer,size):\n"
                    "  assert flavor==3 and size==136\n"
                    "  if " + repr(mode) + " in ('absent','denied'):\n"
                    "   ctypes.set_errno(errno.ESRCH if " + repr(mode) + "=='absent' else errno.EPERM);return 0\n"
                    "  info=buffer._obj;info.pid=pid;info.ppid=100;info.pgid=pid;info.status=4\n"
                    "  info.seconds=1700001234;info.microseconds=123456\n"
                    "  if " + repr(mode) + "=='wrong_pid': info.pid+=1\n"
                    "  if " + repr(mode) + "=='unknown_state': info.status=99\n"
                    "  return 135 if " + repr(mode) + "=='partial' else size\n"
                    "class Library: proc_pidinfo=Query()\n"
                    "ctypes.CDLL=lambda *args,**kwargs:Library()\n"
                    "scope['process_query_helper']()\n")
                result = subprocess.run([sys.executable, '-I', '-S', '-B', '-c', code],
                    input=b'[4321]\n', capture_output=True, timeout=2)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                if mode == 'valid':
                    self.assertEqual(report, {'4321': [4321, 100, 4321, 1700001234, 123456, 'stopped', 0]})
                elif mode == 'absent':
                    self.assertEqual(report, {'4321': None})
                else:
                    self.assertEqual(report, {'error': 'native_query_unavailable', 'cause': 'denied' if mode == 'denied' else 'read_error' if mode == 'partial' else 'invalid_record'})

    def test_unavailable_process_observation_stops_before_git_or_scanners(self):
        before = self.fingerprint()
        marker = self.base / "unexpected-git-start"
        wrapper = self.base / "observer-failure.py"
        wrapper.write_text("import subprocess,runpy,sys\nfrom pathlib import Path\n"
            "real = subprocess.Popen\n"
            "def launched(command,*args,**kwargs):\n"
            " if command[0] == '/bin/ps':\n"
            "  command = [sys.executable, '-I', '-S', '-B', '-c', 'raise SystemExit(1)']\n"
            " elif Path(command[0]).name == 'git':\n"
            "  Path(" + repr(str(marker)) + ").touch()\n"
            " return real(command,*args,**kwargs)\n"
            "subprocess.Popen = launched\n"
            "sys.argv = [" + repr(str(CLI)) + "] + sys.argv[1:]\n"
            "runpy.run_path(" + repr(str(CLI)) + ", run_name='__main__')\n")
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(wrapper),
            "--patch", str(self.patch("value = 'repaired'\n")), "--path", "fixture.py",
            "--active-hook-root", str(ROOT), "--check", "--json"],
            cwd=self.repo, env=self.env, capture_output=True, timeout=3)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "process_observation_unavailable")
        self.assertFalse(marker.exists())
        self.assertEqual(self.fingerprint(), before)

    def test_resource_failures_report_safe_measurements(self):
        before = self.fingerprint()
        patch = self.patch("value = 'repaired'\n")
        oversized = self.base / "oversized.patch"
        oversized.write_bytes(TOKEN.encode() + b"x" * (1048577 - len(TOKEN)))
        cases = [
            (self.run_cli(oversized, "--check"), 3, 1048576, 1048577, "bytes"),
            (self.run_cli(patch, "--check", *[item for number in range(64)
                for item in ("--path", "target" + str(number) + ".py")]), 3, 64, 65, "paths"),
        ]
        wrapper = self.base / "stderr-limit.py"
        wrapper.write_text("import subprocess,runpy,sys\nfrom pathlib import Path\n"
            "real = subprocess.Popen\n"
            "def launched(command,*args,**kwargs):\n"
            " if Path(command[0]).name == 'git':\n"
            "  command = [sys.executable, '-I', '-S', '-B', '-c', \"import sys; token='gh'+'p_'+'FAKE'*9; sys.stderr.buffer.write(token.encode()+b'x'*(1048577-len(token)))\"]\n"
            " return real(command,*args,**kwargs)\n"
            "subprocess.Popen = launched\n"
            "sys.argv = [" + repr(str(CLI)) + "] + sys.argv[1:]\n"
            "runpy.run_path(" + repr(str(CLI)) + ", run_name='__main__')\n")
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(wrapper), "--patch", str(patch),
            "--path", "fixture.py", "--active-hook-root", str(ROOT), "--check", "--json"],
            cwd=self.repo, env=self.env, capture_output=True, timeout=4)
        cases.append((result, 2, 1048576, 1048577, "bytes"))
        for result, code, limit, measured, unit in cases:
            with self.subTest(limit=limit, unit=unit):
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report.get("limit"), limit, report)
                self.assertEqual(report.get("measured"), measured, report)
                self.assertEqual(report.get("unit"), unit, report)
                self.assertTrue(report.get("action"))
                self.assertNotIn(TOKEN.encode(), result.stdout + result.stderr)
                self.assertEqual(self.fingerprint(), before)

    def test_missing_git_has_actionable_repair(self):
        before = self.fingerprint()
        patch = self.patch("value = 'repaired'\n")
        wrapper = self.base / "missing-git.py"
        wrapper.write_text("import shutil,runpy,sys\n"
            "real = shutil.which\n"
            "shutil.which = lambda name,*args,**kwargs: None if name == 'git' else real(name,*args,**kwargs)\n"
            "sys.argv = [" + repr(str(CLI)) + "] + sys.argv[1:]\n"
            "runpy.run_path(" + repr(str(CLI)) + ", run_name='__main__')\n")
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(wrapper), "--patch", str(patch),
            "--path", "fixture.py", "--active-hook-root", str(ROOT), "--check", "--json"],
            cwd=self.repo, env=self.env, capture_output=True, timeout=3)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["reason"], "git_unavailable")
        self.assertIn("Git", report["action"])
        self.assertIn("install", report["action"].lower())
        self.assertEqual(self.fingerprint(), before)

if __name__ == "__main__":
    unittest.main()

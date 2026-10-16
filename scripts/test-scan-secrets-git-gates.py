#!/usr/bin/env python3
"""Staged gate proof through isolated CLI processes and real Git commits."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts/scan-secrets.py"
GIT = shutil.which("git")


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="git-gate-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SCAN_", "PYTHON"))}
        self.env.update(HOME=str(self.base / "home"), USERPROFILE=str(self.base / "home"),
                        XDG_DATA_HOME=str(self.base / "data"), XDG_CONFIG_HOME=str(self.base / "config"),
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.git("init", "--quiet")

    def git(self, *args, data=None, env=None, check=True):
        return subprocess.run([GIT, "-c", "commit.gpgsign=false", "-c", "user.name=Fixture",
            "-c", "user.email=fixture@example.invalid", *args], cwd=self.repo, env=env or self.env,
            input=data, capture_output=True, check=check, timeout=15)

    def cli(self, *args, env=None, entry=CLI):
        return subprocess.run([sys.executable, "-I", "-S", "-B", str(entry), *args], cwd=self.repo,
            env=env or self.env, input=b"unused stdin", capture_output=True, timeout=45)

    def gate(self, code, *args, env=None):
        process = self.cli("gate", "pre-commit", "--repo", str(self.repo), "--json", *args, env=env)
        self.assertEqual(process.returncode, code, process.stdout + process.stderr)
        self.assertNotIn(b"Traceback", process.stderr)
        return json.loads(process.stdout)

    @staticmethod
    def credential():
        return ("gh" + "p_" + "A" * 36).encode()

    def test_full_selected_index_ignores_worktree_bytes(self):
        path = self.repo / "selected.txt"
        path.write_bytes(self.credential())
        self.git("add", ".")
        path.write_text("clean worktree\n")
        value = self.gate(1)
        self.assertEqual(value["schema"], "scan_secrets_gate_v1")
        self.assertEqual(value["action"], "pre-commit")
        self.assertEqual(value["scope"], "index")
        self.assertEqual(value["policy_version"], "selected_index_v1")
        self.assertEqual(value["budget_profile"], "checkpoint")
        self.assertEqual(value["audit_outcome"], "written")
        path.write_text("clean staged\n")
        self.git("add", ".")
        path.write_bytes(self.credential())
        self.assertTrue(self.gate(0)["coverage_complete"])

    def install_dispatcher(self, *, mutation=None, extra_args=()):
        # Temporary test composition only. T7 owns production hook installation.
        import hashlib
        sys.path.insert(0, str(ROOT))
        from hooks.runtime import scan_cli, scan_budget
        build = hashlib.sha256()
        for name, raw in (("scan-secrets.py", CLI.read_bytes()), ("scan_cli.py", (ROOT / "hooks/runtime/scan_cli.py").read_bytes()),
                          ("scan_status.py", (ROOT / "hooks/runtime/scan_status.py").read_bytes()),
                          *((name + ".py", (ROOT / "hooks/runtime" / (name + ".py")).read_bytes()) for name in scan_cli.MODULES)):
            build.update(name.encode() + b"\0" + raw)
        identity = hashlib.sha256(b"\0".join(str(path).encode() for path in
            (self.repo, self.repo / ".git", self.repo / ".git"))).hexdigest()
        budget_identity = scan_budget.load_budget(None)[1]
        hook = self.repo / ".git/hooks/pre-commit"
        hook.write_text("#!" + sys.executable + " -I\n" +
            "import hashlib,json,os,subprocess,sys\nfrom pathlib import Path\n" +
            "sys.path.insert(0," + repr(str(ROOT)) + ")\nfrom hooks.runtime.scan_gate import validate_result\n" +
            "index=Path(os.environ.get('GIT_INDEX_FILE', '.git/index'))\n" +
            "index_identity=hashlib.sha256(b'selected-index-v1\\0'+(index.read_bytes() if index.exists() else b'absent')).hexdigest()\n" +
            "p=subprocess.run(" + repr([sys.executable, "-I", "-S", "-B", str(CLI), "gate", "pre-commit", "--json", "--repo", str(self.repo), *extra_args]) + ",capture_output=True)\n" +
            "raw=p.stdout\nmutation=" + repr(mutation) + "\n" +
            "if mutation=='missing': raw=b''\nelif mutation=='malformed': raw=b'{}'\n" +
            "elif mutation:\n v=json.loads(raw)\n v[mutation]='0'*64 if mutation in {'build','repository_identity','index_identity','budget_identity'} else 'mismatched'\n raw=json.dumps(v).encode()\n" +
            "try:\n validate_result(raw,p.returncode,action='pre-commit',build=" + repr(build.hexdigest()) +
            ",repository_identity=" + repr(identity) + ",index_identity=index_identity,budget_identity=" + repr(budget_identity) + ")\n" +
            "except Exception: sys.exit(2)\nsys.exit(p.returncode)\n")
        hook.chmod(0o755)

    def seed(self, raw=b"base\n"):
        (self.repo / "selected.txt").write_bytes(raw)
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "base")

    def head(self):
        return self.git("rev-parse", "--verify", "HEAD").stdout

    def test_actual_commit_blocks_staged_secret_and_allows_clean_index(self):
        self.seed()
        self.install_dispatcher()
        before = self.head()
        path = self.repo / "selected.txt"
        path.write_bytes(self.credential())
        self.git("add", ".")
        path.write_text("clean worktree\n")
        self.assertNotEqual(self.git("commit", "--quiet", "-m", "blocked", check=False).returncode, 0)
        self.assertEqual(self.head(), before)
        path.write_text("safe staged\n")
        self.git("add", ".")
        path.write_bytes(self.credential())
        self.git("commit", "--quiet", "-m", "clean")
        self.assertNotEqual(self.head(), before)
        self.assertEqual(self.git("show", "HEAD:selected.txt").stdout, b"safe staged\n")

    def test_unchanged_index_paths_are_full_gate_scope(self):
        self.seed(self.credential())
        self.assertGreater(self.gate(1)["counts"]["processed_findings"], 0)
        # Explicit checkpoint index semantics still enumerate pending versions.
        self.assertEqual(self.cli("check", "--scope", "index", "--json").returncode, 0)

    def test_alternate_index_and_real_partial_commit_select_the_actual_tree(self):
        self.seed()
        alternate = self.base / "alternate-index"
        env = {**self.env, "GIT_INDEX_FILE": str(alternate)}
        self.git("read-tree", "HEAD", env=env)
        path = self.repo / "selected.txt"
        path.write_bytes(self.credential())
        self.git("add", ".", env=env)
        path.write_text("safe working copy\n")
        self.assertGreater(self.gate(1, env=env)["counts"]["processed_findings"], 0)
        self.assertEqual(self.cli("check", "--scope", "index", "--json", env=env).returncode, 0)
        self.install_dispatcher()
        before = self.head()
        self.assertNotEqual(self.git("commit", "--quiet", "-m", "alternate", env=env, check=False).returncode, 0)
        self.assertEqual(self.head(), before)
        # --only supplies a temporary next-index, not the ordinary index.
        path.write_bytes(self.credential())
        self.assertNotEqual(self.git("commit", "--only", "selected.txt", "-m", "partial blocked", check=False).returncode, 0)
        self.assertEqual(self.head(), before)
        path.write_text("safe partial\n")
        self.git("commit", "--only", "selected.txt", "-m", "partial allowed")
        self.assertEqual(self.git("show", "HEAD:selected.txt").stdout, b"safe partial\n")
        # The normal index may contain an unsafe unrelated staged path.
        (self.repo / "other.txt").write_bytes(self.credential())
        self.git("add", "other.txt")
        path.write_text("safe next partial\n")
        self.git("commit", "--only", "selected.txt", "-m", "partial ignores unrelated staged")
        self.assertEqual(self.git("ls-tree", "--name-only", "HEAD").stdout, b"selected.txt\n")

    def test_empty_unborn_and_split_index_are_honest(self):
        empty = self.gate(0)
        self.assertEqual(empty["counts"]["candidates"], 0)
        self.seed()
        self.git("update-index", "--split-index")
        (self.repo / "selected.txt").write_bytes(self.credential())
        self.git("add", ".")
        self.assertGreater(self.gate(1)["counts"]["processed_findings"], 0)

    def test_unresolved_index_never_reports_clean(self):
        self.seed()
        oid = self.git("hash-object", "-w", "--stdin", data=b"safe\n").stdout.strip()
        self.git("update-index", "--index-info", data=b"0 " + b"0" * 40 + b"\tselected.txt\n" +
                 b"100644 " + oid + b" 1\tselected.txt\n100644 " + oid + b" 2\tselected.txt\n")
        self.assertEqual(self.gate(2)["reason"], "index_unresolved")

    def test_skip_warn_environment_and_unrelated_git_redirects_do_not_authorize(self):
        (self.repo / "selected.txt").write_bytes(self.credential())
        self.git("add", ".")
        env = {**self.env, "SCAN_MODE": "warn", "GUARD_MODE": "warn", "SKIP_SECRETS_SCAN": "1",
               "SCAN_SECRETS_SKIP": "1", "SECRETS_ALLOWLIST": ".*", "GIT_DIR": str(self.base / "absent"),
               "GIT_OBJECT_DIRECTORY": str(self.base / "absent"), "GIT_CONFIG_COUNT": "1",
               "GIT_CONFIG_KEY_0": "core.fsmonitor", "GIT_CONFIG_VALUE_0": "evil"}
        self.assertGreater(self.gate(1, env=env)["counts"]["processed_findings"], 0)

    def test_selected_index_rejects_missing_linked_or_special_inputs(self):
        for selected in (str(self.base / "absent"), ""):
            self.gate(2, env={**self.env, "GIT_INDEX_FILE": selected})
        if os.name != "nt":
            link = self.base / "linked"
            link.symlink_to(self.repo / ".git")
            self.gate(2, env={**self.env, "GIT_INDEX_FILE": str(link / "index")})
            fifo = self.base / "fifo"
            os.mkfifo(fifo)
            self.gate(2, env={**self.env, "GIT_INDEX_FILE": str(fifo)})

    def test_substituted_loose_blob_bytes_are_not_coverage_evidence(self):
        import zlib
        raw = b"clean original\n"
        path = self.repo / "selected.txt"
        path.write_bytes(raw)
        self.git("add", ".")
        oid = self.git("rev-parse", ":selected.txt").stdout.decode().strip()
        substituted = b"clean impostor\n"
        object_file = self.repo / ".git/objects" / oid[:2] / oid[2:]
        object_file.chmod(0o600)
        object_file.write_bytes(zlib.compress(b"blob " + str(len(substituted)).encode() + b"\0" + substituted))
        value = self.gate(2)
        self.assertEqual(value["reason"], "git_output_invalid")
        self.assertFalse(value["coverage_complete"])

    def test_missing_empty_malformed_or_mismatched_results_block_actual_commit(self):
        self.seed()
        for mutation in ("missing", "malformed", "action", "schema", "build", "policy_version", "scope",
                         "repository_identity", "index_identity", "budget_identity", "exit_code",
                         "coverage_complete", "audit_outcome", "outcome", "counts", "security_outcome",
                         "scope_identity", "accounting_units", "budget_profile"):
            with self.subTest(mutation=mutation):
                self.install_dispatcher(mutation=mutation)
                before = self.head()
                (self.repo / "selected.txt").write_text("safe changed " + str(mutation))
                self.git("add", ".")
                self.assertNotEqual(self.git("commit", "--quiet", "-m", "invalid result", check=False).returncode, 0)
                self.assertEqual(self.head(), before)

    def test_audit_and_display_outcomes_are_independent(self):
        self.seed()
        path = self.repo / "selected.txt"
        path.write_bytes(self.credential())
        self.git("add", ".")
        # A failed informational display must retain the findings exit.
        status = self.base / "data/scan-secrets/status"
        status.parent.mkdir(parents=True, mode=0o700)
        status.write_text("blocked display directory")
        value = self.gate(1)
        self.assertEqual(value["status_outcome"], "failed")
        self.assertEqual(value["audit_outcome"], "written")
        records = [json.loads(row) for row in (status.parent / "audit.jsonl").read_text().splitlines()]
        self.assertEqual(records[-1]["action"], "pre-commit")
        self.assertEqual(records[-1]["profile"], "selected_index_v1")
        self.assertEqual(records[-1]["route"], "git_gate")
        self.assertEqual(records[-1]["scope"], "index")
        # Required audit failure stays incomplete, retaining known findings.
        audit = status.parent / "audit.jsonl"
        audit.unlink()
        audit.mkdir()
        value = self.gate(2)
        self.assertEqual(value["audit_outcome"], "failed")
        self.assertEqual(value["security_outcome"], "findings")
        self.assertGreater(value["counts"]["processed_findings"], 0)
        path.write_text("safe\n")
        self.git("add", ".")
        self.assertEqual(self.gate(2)["reason"], "audit_unavailable")
        self.install_dispatcher()
        before = self.head()
        self.assertNotEqual(self.git("commit", "--quiet", "-m", "audit unavailable", check=False).returncode, 0)
        self.assertEqual(self.head(), before)

    def test_late_corrupt_object_preserves_known_findings(self):
        import zlib
        (self.repo / "a.txt").write_bytes(self.credential())
        (self.repo / "z.txt").write_bytes(b"original\n")
        self.git("add", ".")
        oid = self.git("rev-parse", ":z.txt").stdout.decode().strip()
        object_file = self.repo / ".git/objects" / oid[:2] / oid[2:]
        object_file.chmod(0o600)
        object_file.write_bytes(zlib.compress(b"blob 9\0impostor\n"))
        value = self.gate(2)
        self.assertEqual(value["reason"], "git_output_invalid")
        self.assertEqual(value["security_outcome"], "findings")
        self.assertGreater(value["counts"]["processed_findings"], 0)
        self.assertTrue(value["findings"])

    def budget(self, **overrides):
        path = self.base / "budget.json"
        path.write_text(json.dumps(dict(schema_version=1,
            checkpoint=dict(max_objects=4096, max_candidate_bytes=67108864, max_seconds=30,
                            max_capture_bytes=134217728, max_temp_bytes=268435456),
            publication=dict(max_objects=20000, max_candidate_bytes=268435456, max_seconds=120,
                             max_capture_bytes=536870912, max_temp_bytes=805306368))))
        value = json.loads(path.read_text())
        value["checkpoint"].update(overrides)
        path.write_text(json.dumps(value))
        return str(path)

    def test_checkpoint_capacity_is_finite_and_reports_actual_units(self):
        for name in ("a.txt", "b.txt"):
            (self.repo / name).write_text("safe\n")
        self.git("add", ".")
        value = self.gate(2, "--budget-file", self.budget(max_objects=1))
        self.assertEqual(value["reason"], "snapshot_count_limit")
        self.assertEqual(value["diagnostic"]["unit"], "snapshots")
        self.assertEqual(value["limits"]["max_objects"], 1)
        self.assertEqual(value["accounting_units"]["max_seconds"], "seconds")
        (self.repo / "a.txt").write_bytes(b"\0" * 1048577)
        self.git("add", ".")
        self.assertEqual(self.gate(2, "--budget-file", self.budget(max_candidate_bytes=1048576))["reason"], "total_bytes_limit")
        for key, reason in (("max_capture_bytes", "capture_bytes_limit"), ("max_temp_bytes", "temporary_bytes_limit")):
            self.assertEqual(self.gate(2, "--budget-file", self.budget(**{key:1048576}))["reason"], reason)

    def test_gate_arguments_help_open_stdin_and_closed_output_are_bounded(self):
        for args in (("gate",), ("gate", "--help"), ("help", "gate"), ("gate", "pre-commit", "--help")):
            with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(CLI), *args], cwd=self.base,
                    env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                process.wait(timeout=3)
                stdout, stderr = process.communicate()
                self.assertEqual(process.returncode, 0, stderr)
                self.assertTrue(stdout)
        for args in (("gate", "pre-commit", "--force"), ("gate", "pre-commit", "--rep", "."),
                     ("gate", "pre-push"), ("gate", "pre-commit", "--scope", "worktree")):
            self.assertEqual(self.cli(*args, "--json").returncode, 3)
        with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(CLI), "gate", "pre-commit", "--json"],
                cwd=self.repo, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            process.wait(timeout=3)
            stdout, stderr = process.communicate()
            self.assertEqual(process.returncode, 0, stdout + stderr)
        with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(CLI), "gate", "pre-commit", "--json"],
                cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            process.stdout.close()
            process.wait(timeout=3)
            stderr = process.stderr.read()
            self.assertNotEqual(process.returncode, 0)
            self.assertNotIn(b"Traceback", stderr)

    def test_cancellation_terminates_gate_git_capture(self):
        if os.name == "nt":
            self.skipTest("POSIX signal fixture; native Windows proof remains separate")
        import signal
        import time
        binary = self.base / "bin"
        binary.mkdir()
        marker = self.base / "started"
        wrapper = binary / "git"
        wrapper.write_text("#!" + sys.executable + "\nimport os,time\nfrom pathlib import Path\nPath(" + repr(str(marker)) + ").write_text(str(os.getpid()))\ntime.sleep(60)\n")
        wrapper.chmod(0o755)
        with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(CLI), "gate", "pre-commit", "--json"],
                cwd=self.repo, env={**self.env, "PATH": str(binary) + os.pathsep + self.env["PATH"]},
                stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            deadline = time.monotonic() + 3
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(marker.exists())
            child = int(marker.read_text())
            try:
                process.send_signal(signal.SIGINT)
                stdout, stderr = process.communicate(timeout=3)
                self.assertEqual(process.returncode, 130, stdout + stderr)
                self.assertEqual(json.loads(stdout)["reason"], "cancelled")
                observed = subprocess.run(["ps", "-o", "stat=", "-p", str(child)], capture_output=True, timeout=2)
                self.assertEqual(observed.stderr, b"")
                self.assertTrue(not observed.stdout.strip() or observed.stdout.lstrip().startswith(b"Z"), observed.stdout)
            finally:
                try:
                    os.kill(child, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_missing_gate_dependency_fails_closed(self):
        sys.path.insert(0, str(ROOT))
        from hooks.runtime.scan_cli import MODULES
        source = self.base / "source"
        (source / "scripts").mkdir(parents=True)
        (source / "hooks/runtime").mkdir(parents=True)
        shutil.copy2(CLI, source / "scripts/scan-secrets.py")
        for name in (*MODULES, "scan_cli", "scan_status"):
            if name != "scan_gate":
                shutil.copy2(ROOT / "hooks/runtime" / (name + ".py"), source / "hooks/runtime" / (name + ".py"))
        process = self.cli("gate", "pre-commit", "--json", entry=source / "scripts/scan-secrets.py")
        self.assertEqual(process.returncode, 2)
        self.assertEqual(json.loads(process.stdout)["reason"], "runtime_unavailable")

    def test_gate_failure_schema_survives_multiple_common_prefix_flags(self):
        process = self.cli("--json", "--no-input", "--quiet", "gate", "pre-commit", "--repo", str(self.base))
        self.assertEqual(process.returncode, 3)
        value = json.loads(process.stdout)
        self.assertEqual(value["schema"], "scan_secrets_gate_v1")
        self.assertEqual(value["exit_code"], 3)
        self.assertEqual(value["reason"], "not_repository")

    def test_neutral_installed_bundle_executes_gate_without_source_checkout(self):
        destination = self.base / "installed"
        process = subprocess.run([sys.executable, "-I", "-S", "-B", str(ROOT / "scripts/install-scan-secrets.py"),
            "install", "--source-dir", str(ROOT), "--destination", str(destination), "--json"],
            cwd=self.base, env=self.env, capture_output=True, timeout=30)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        manifest = json.loads((destination / "installation.json").read_text())
        self.assertEqual(len(manifest["files"]), 14)
        (self.repo / "selected.txt").write_bytes(self.credential())
        self.git("add", ".")
        process = self.cli("gate", "pre-commit", "--json", entry=destination / "scripts/scan-secrets.py")
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        value = json.loads(process.stdout)
        self.assertEqual(value["schema"], "scan_secrets_gate_v1")
        self.assertEqual(value["audit_outcome"], "written")
        self.assertEqual(value["policy_version"], "selected_index_v1")

    @unittest.skipUnless(sys.platform == "darwin", "macOS fixed system aliases")
    def test_selected_index_accepts_verified_macos_system_alias(self):
        self.seed()
        physical = self.repo / ".git/index"
        for alias in (Path("/tmp"), Path("/var")):
            target = alias.resolve(strict=True)
            if physical.is_relative_to(target):
                selected = alias / physical.relative_to(target)
                self.assertEqual(self.gate(0, env={**self.env, "GIT_INDEX_FILE": str(selected)})["counts"]["candidates"], 1)
                return
        self.fail("fixture did not use a macOS system alias target")

    def test_gate_never_runs_optional_helpers_or_mutates_repository(self):
        import hashlib
        self.seed()
        marker = self.base / "helper-ran"
        helper = self.base / "optional-helper"
        helper.write_text("#!/bin/sh\nprintf unsafe > '" + str(marker) + "'\ncat\n")
        helper.chmod(0o755)
        (self.repo / ".gitattributes").write_text("*.txt filter=fixture diff=fixture\n")
        self.git("add", ".gitattributes")
        self.git("config", "filter.fixture.clean", str(helper))
        self.git("config", "filter.fixture.required", "true")
        self.git("config", "diff.fixture.textconv", str(helper))
        self.git("config", "core.fsmonitor", str(helper))
        def fingerprint():
            return {str(p.relative_to(self.repo)): (p.stat().st_mode, hashlib.sha256(p.read_bytes()).hexdigest())
                    for p in self.repo.rglob("*") if p.is_file()}
        before = fingerprint()
        self.gate(0)
        self.assertFalse(marker.exists())
        self.assertEqual(fingerprint(), before)

    def test_gate_repository_named_status_keeps_gate_error_schema(self):
        (self.base / "status").mkdir()
        process = subprocess.run([sys.executable, "-I", "-S", "-B", str(CLI), "gate", "pre-commit", "--repo", "status", "--json"],
            cwd=self.base, env=self.env, input=b"unused stdin", capture_output=True, timeout=5)
        self.assertEqual(process.returncode, 3)
        value = json.loads(process.stdout)
        self.assertEqual(value["schema"], "scan_secrets_gate_v1")
        self.assertEqual(value["reason"], "not_repository")

    def test_gate_default_capacity_reaches_late_staged_secret_beyond_legacy_limits(self):
        for number in range(300):
            (self.repo / f"candidate-{number:04}.bin").write_bytes(b"\0" * 32768)
        (self.repo / "candidate-0299.bin").write_bytes(b"\0" * 32768 + self.credential())
        self.git("add", ".")
        value = self.gate(1)
        self.assertEqual(value["counts"]["inspected_snapshots"], 300)
        self.assertGreater(value["counts"]["candidate_bytes"], 8388608)
        self.assertTrue(value["coverage_complete"])
        self.assertEqual(value["limits"]["max_objects"], 4096)

    def test_help_or_invalid_gate_invocation_cannot_authorize_commit(self):
        self.seed()
        for extra in (("--help",), ("--force",)):
            self.install_dispatcher(extra_args=extra)
            (self.repo / "selected.txt").write_text("safe changed " + extra[0])
            self.git("add", ".")
            before = self.head()
            self.assertNotEqual(self.git("commit", "--quiet", "-m", "no gate result", check=False).returncode, 0)
            self.assertEqual(self.head(), before)


if __name__ == "__main__":
    unittest.main()

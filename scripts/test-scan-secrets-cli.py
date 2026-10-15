#!/usr/bin/env python3
"""Exercise the standalone checkpoint through its public process interface."""
from pathlib import Path
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts/scan-secrets.py"
GIT = shutil.which("git")


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="checkpoint-cli-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SCAN_SECRETS_", "PYTHON"))}
        self.env.update(HOME=str(self.base / "home"), USERPROFILE=str(self.base / "home"),
                        XDG_DATA_HOME=str(self.base / "data"), XDG_CONFIG_HOME=str(self.base / "config"),
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.git("init", "--quiet")

    def git(self, *args, data=None):
        return subprocess.run([GIT, "-c", "commit.gpgsign=false", "-c", "user.name=Fixture",
            "-c", "user.email=fixture@example.invalid", *args], cwd=self.repo, env=self.env,
            input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout

    def cli(self, *args, env=None, entry=CLI, cwd=None):
        return subprocess.run([sys.executable, str(entry), *args], cwd=cwd or self.repo,
            env=env or self.env, input=b"unconsumed stdin", stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=45)

    def result(self, process, code):
        self.assertEqual(process.returncode, code, (process.stdout, process.stderr))
        value = json.loads(process.stdout)
        self.assertEqual(value["schema"], "scan_secrets_check_v1")
        self.assertNotIn(b"Traceback", process.stderr)
        return value

    def test_clean_check_has_explicit_complete_result(self):
        result = self.result(self.cli("check", "--json"), 0)
        self.assertEqual(result["outcome"], "complete_clean")
        self.assertTrue(result["coverage_complete"])
        self.assertEqual(result["scope"], "worktree")
        self.assertEqual(result["audit_outcome"], "written")

    def test_explicit_budget_file_controls_limits_and_rejects_ambiguous_json(self):
        checkpoint = dict(max_objects=1, max_candidate_bytes=1048576, max_seconds=10,
                          max_capture_bytes=1048576, max_temp_bytes=1048576)
        publication = dict(max_objects=20000, max_candidate_bytes=268435456, max_seconds=120,
                           max_capture_bytes=536870912, max_temp_bytes=805306368)
        config = dict(schema_version=1, checkpoint=checkpoint, publication=publication)
        path = self.base / "budget.json"
        path.write_text(json.dumps(config))
        value = self.result(self.cli("check", "--json", "--budget-file", str(path)), 0)
        self.assertEqual(value["limits"], checkpoint)
        self.assertEqual(len(value["budget_identity"]), 64)
        (self.repo / "a.txt").write_text("clean\n")
        (self.repo / "b.txt").write_text("clean\n")
        value = self.result(self.cli("check", "--json", "--budget-file", str(path)), 2)
        self.assertEqual(value["reason"], "snapshot_count_limit")
        self.assertEqual(value["diagnostic"]["limit"], 1)
        for raw in ('{}', '{"schema_version":1,"schema_version":1}',
                    json.dumps({**config, "extra": 1}), json.dumps({**config, "schema_version": True}),
                    *[json.dumps({**config, "checkpoint": {**checkpoint, "max_objects": value}})
                      for value in (True, "1", 0, 16385, 1.5)],
                    *[json.dumps({**config, "checkpoint": {**checkpoint, "max_seconds": value}})
                      for value in (float("nan"), float("inf"), 121)]):
            with self.subTest(raw=raw):
                path.write_text(raw)
                self.assertEqual(self.result(self.cli("check", "--json", "--budget-file", str(path)), 3)["reason"], "budget_invalid")

    @staticmethod
    def credential():
        return ("gh" + "p_" + "A" * 36).encode()

    def commit(self):
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "fixture")

    def test_hostile_environment_cannot_skip_or_redirect_the_check(self):
        (self.repo / "pending.bin").write_bytes(b"\0" + self.credential())
        env = {**self.env, "SCAN_SECRETS_MODE": "off", "SCAN_SECRETS_SCOPE": "staged",
               "SCAN_SECRETS_SKIP": "1", "GIT_DIR": str(self.base / "absent"),
               "SCAN_MODE": "warn", "SKIP_SECRETS_SCAN": "true", "SECRETS_ALLOWLIST": ".*",
               "GIT_INDEX_FILE": str(self.base / "absent"), "GIT_OBJECT_DIRECTORY": str(self.base / "absent"),
               "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.fsmonitor", "GIT_CONFIG_VALUE_0": "evil"}
        value = self.result(self.cli("check", "--json", env=env), 1)
        self.assertEqual(value["outcome"], "complete_findings")
        self.assertNotIn(self.credential(), self.cli("check", "--json", env=env).stdout)

    def test_local_conversion_and_fsmonitor_helpers_never_execute(self):
        (self.repo / "pending.txt").write_text("clean\n")
        self.commit()
        marker = self.base / "executed"
        helper = self.base / "helper.sh"
        helper.write_text(f"#!/bin/sh\nprintf executed > '{marker}'\ncat\n")
        helper.chmod(0o755)
        self.git("config", "filter.fixture.clean", str(helper))
        self.git("config", "filter.fixture.required", "true")
        self.git("config", "core.fsmonitor", str(helper))
        (self.repo / ".gitattributes").write_text("*.txt filter=fixture\n")
        (self.repo / "pending.txt").write_bytes(b"clean\n" + self.credential() + b"\n")
        before = (self.repo / ".git/index").read_bytes()
        value = self.result(self.cli("check", "--json"), 2)
        self.assertFalse(marker.exists(), "optional Git helper ran")
        self.assertEqual(value["reason"], "conversion_unsupported")
        self.assertEqual((self.repo / ".git/index").read_bytes(), before)
        self.assertIn(self.credential(), (self.repo / "pending.txt").read_bytes())

    def test_help_version_arguments_and_open_stdin_have_no_scan_side_effects(self):
        for args in ((), ("--help",), ("-h",), ("help",), ("help", "check"), ("check", "-h"), ("check", "--help"), ("--version",)):
            with self.subTest(args=args):
                process = subprocess.Popen([sys.executable, str(CLI), *args], cwd=self.base, env=self.env,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.wait(timeout=3)
                stdout, stderr = process.communicate()
                self.assertEqual(process.returncode, 0, stderr)
                self.assertTrue(stdout)
                self.assertEqual(stderr, b"")
                self.assertFalse((self.base / "data").exists())
        for args in (("check", "--sc", "index"), ("unknown",), ("check", "--scope", "outgoing"),
                     ("check", "--force"), ("--unknown=https://name:private@example.invalid",)):
            process = self.cli(*args, "--json")
            value = self.result(process, 3)
            self.assertEqual(value["reason"], "invalid_arguments")
            self.assertNotIn(b"private", process.stdout + process.stderr)
        value = self.result(self.cli("check", "--json", cwd=self.base), 3)
        self.assertEqual(value["reason"], "not_repository")
        self.assertEqual(self.result(self.cli("check", "--json", "--repo", str(self.base / "missing")), 3)["reason"], "not_repository")
        process = self.cli("--json", "check", "--no-input", "--quiet", "--no-color")
        self.result(process, 0)
        self.assertEqual(process.stderr, b"")
        self.assertEqual(self.cli("check", "--quiet").stdout, b"")

    def test_direct_entry_ignores_python_and_optional_git_helper_environment(self):
        marker = self.base / "python-startup-ran"
        decoy = self.base / "decoy"
        decoy.mkdir()
        (decoy / "sitecustomize.py").write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n")
        (decoy / "scan_engine.py").write_text("raise RuntimeError('untrusted helper')\n")
        env = {**self.env, "PYTHONPATH": str(decoy), "PYTHONSTARTUP": str(decoy / "sitecustomize.py"),
               "GIT_EXEC_PATH": str(decoy), "GIT_ASKPASS": str(decoy / "helper"),
               "GIT_EXTERNAL_DIFF": str(decoy / "helper"), "GIT_PAGER": str(decoy / "helper")}
        process = subprocess.run([str(CLI), "check", "--json"], cwd=self.repo, env=env,
            stdin=subprocess.PIPE, capture_output=True, timeout=8)
        self.result(process, 0)
        self.assertFalse(marker.exists())

    def test_check_does_not_wait_for_open_stdin(self):
        with subprocess.Popen([str(CLI), "check", "--json", "--no-input"], cwd=self.repo, env=self.env,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            process.wait(timeout=3)
            stdout, stderr = process.communicate()
            self.result(subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr), 0)

    def test_unavailable_git_and_malformed_repository_configuration_are_incomplete(self):
        env = {**self.env, "PATH": str(self.base / "absent-bin")}
        self.assertEqual(self.result(self.cli("check", "--json", env=env), 2)["reason"], "git_unavailable")
        (self.repo / ".git/config").write_text("[malformed\n")
        self.assertEqual(self.result(self.cli("check", "--json"), 2)["reason"], "git_failed")

    def test_worktree_and_index_scopes_use_the_selected_bytes(self):
        path = self.repo / "selected.txt"
        path.write_text("base\n")
        self.commit()
        path.write_text("base\nstaged clean\n")
        self.git("add", "selected.txt")
        path.write_bytes(b"base\nstaged clean\n" + self.credential() + b"\n")
        self.assertEqual(self.result(self.cli("check", "--scope", "index", "--json"), 0)["counts"]["inspected_snapshots"], 1)
        self.assertGreater(self.result(self.cli("check", "--json"), 1)["counts"]["processed_findings"], 0)
        # A historical credential on an unchanged line is ignored by worktree
        # diff semantics, while selected staged versions are scanned in full.
        self.git("add", "selected.txt")
        self.git("commit", "--quiet", "-m", "historical fixture")
        path.write_bytes(path.read_bytes() + b"new clean line\n")
        self.git("add", "selected.txt")
        self.result(self.cli("check", "--json"), 0)
        self.result(self.cli("check", "--scope", "index", "--json"), 1)

    def test_raw_index_and_worktree_are_preserved_with_supported_text_conversion(self):
        path = self.repo / "selected.txt"
        path.write_bytes(b"historical " + self.credential() + b"\nbase\n")
        (self.repo / ".gitattributes").write_text("selected.txt text eol=crlf\n")
        self.commit()
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n") + b"new clean\r\n")
        before = {name: (self.repo / name).read_bytes() for name in ("selected.txt", ".git/index", ".git/HEAD", ".git/config")}
        self.result(self.cli("check", "--json"), 0)
        path.write_bytes(path.read_bytes() + self.credential() + b"\r\n")
        self.result(self.cli("check", "--json"), 1)
        self.assertEqual({name: (self.repo / name).read_bytes() for name in before if name != "selected.txt"},
                         {name: raw for name, raw in before.items() if name != "selected.txt"})
        self.assertTrue(path.read_bytes().startswith(before["selected.txt"]))

    def test_linked_worktree_uses_its_captured_text_conversion_settings(self):
        (self.repo / "selected.txt").write_bytes(self.credential() + b"\nbase\n")
        self.commit()
        linked = self.base / "linked"
        self.git("worktree", "add", "--quiet", "-b", "fixture-linked", str(linked))
        self.git("config", "extensions.worktreeConfig", "true")
        self.git("-C", str(linked), "config", "--worktree", "core.autocrlf", "true")
        path = linked / "selected.txt"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n") + b"new clean\r\n")
        self.result(self.cli("check", "--json", "--repo", str(linked)), 0)
        path.write_bytes(path.read_bytes() + self.credential() + b"\r\n")
        self.result(self.cli("check", "--json", "--repo", str(linked)), 1)

    def test_object_replacements_cannot_hide_selected_index_content(self):
        path = self.repo / "selected.bin"
        path.write_bytes(b"\0" + self.credential())
        self.git("add", "selected.bin")
        oid = self.git("rev-parse", ":selected.bin").strip().decode()
        replacement = self.git("hash-object", "-w", "--stdin", data=b"clean\n").strip().decode()
        self.git("replace", oid, replacement)
        self.result(self.cli("check", "--scope", "index", "--json"), 1)

    def test_missing_promisor_object_is_incomplete_without_fetch(self):
        path = self.repo / "selected.bin"
        path.write_bytes(b"\0" + self.credential())
        self.git("add", "selected.bin")
        oid = self.git("rev-parse", ":selected.bin").strip().decode()
        (self.repo / ".git/objects" / oid[:2] / oid[2:]).unlink()
        marker = self.base / "fetch-ran"
        helper = self.base / "remote-helper.sh"
        helper.write_text(f"#!/bin/sh\nprintf ran > '{marker}'\nexit 1\n")
        helper.chmod(0o755)
        self.git("config", "extensions.partialClone", "origin")
        self.git("config", "remote.origin.promisor", "true")
        self.git("config", "remote.origin.url", "ext::" + str(helper))
        self.git("config", "protocol.ext.allow", "always")
        value = self.result(self.cli("check", "--scope", "index", "--json"), 2)
        self.assertIn(value["reason"], {"git_output_invalid", "git_failed"})
        self.assertFalse(marker.exists())

    def test_captured_index_is_used_after_the_live_index_changes(self):
        (self.repo / "selected.bin").write_bytes(b"\0" + self.credential())
        self.git("add", "selected.bin")
        index = self.repo / ".git/index"
        captured = index.read_bytes()
        self.git("read-tree", "--empty")
        alternate = self.base / "other-index"
        alternate.write_bytes(index.read_bytes())
        index.write_bytes(captured)
        wrapper = self.base / "index-change.py"
        wrapper.write_text("import subprocess,runpy,sys\nfrom pathlib import Path\nreal=subprocess.Popen\n"
            "def launched(command,*args,**kwargs):\n"
            " if command[1:3] == ['diff','--cached']:\n"
            "  Path(" + repr(str(index)) + ").write_bytes(Path(" + repr(str(alternate)) + ").read_bytes())\n"
            " return real(command,*args,**kwargs)\nsubprocess.Popen=launched\n"
            "sys.argv=[" + repr(str(CLI)) + "]+sys.argv[1:]\nrunpy.run_path(" + repr(str(CLI)) + ",run_name='__main__')\n")
        process = subprocess.run([sys.executable, "-I", "-S", "-B", str(wrapper), "check", "--scope", "index", "--json"],
            cwd=self.repo, env=self.env, capture_output=True, timeout=10)
        self.result(process, 1)
        self.assertEqual(index.read_bytes(), alternate.read_bytes())

    def test_known_findings_survive_a_later_unsafe_candidate(self):
        (self.repo / "a.bin").write_bytes(b"\0" + self.credential())
        os.symlink(self.base / "elsewhere", self.repo / "z.bin")
        value = self.result(self.cli("check", "--json"), 2)
        self.assertEqual(value["reason"], "candidate_unsafe")
        self.assertGreater(value["counts"]["processed_findings"], 0)
        self.assertTrue(value["findings"])
        self.assertFalse(value["coverage_complete"])

    def test_known_findings_survive_later_private_repository_cleanup_failure(self):
        (self.repo / "pending.bin").write_bytes(b"\0" + self.credential())
        wrapper = self.base / "cleanup-failure.py"
        wrapper.write_text("import tempfile,runpy,sys\nfrom pathlib import Path\nreal=tempfile.TemporaryDirectory.cleanup\n"
            "def cleanup(self):\n real(self)\n if Path(self.name).name.startswith('scan-checkpoint-'): raise OSError('unsafe raw failure detail')\n"
            "tempfile.TemporaryDirectory.cleanup=cleanup\nsys.argv=[" + repr(str(CLI)) + "]+sys.argv[1:]\n"
            "runpy.run_path(" + repr(str(CLI)) + ",run_name='__main__')\n")
        process = subprocess.run([sys.executable, "-I", "-S", "-B", str(wrapper), "check", "--json"],
            cwd=self.repo, env=self.env, capture_output=True, timeout=5)
        value = self.result(process, 2)
        self.assertEqual(value["reason"], "cleanup_failed")
        self.assertTrue(value["findings"])
        self.assertGreater(value["counts"]["processed_findings"], 0)
        self.assertNotIn(b"unsafe raw failure detail", process.stdout + process.stderr)

    def test_index_refuses_conflicts_while_worktree_inspects_versions(self):
        clean = self.git("hash-object", "-w", "--stdin", data=b"base\n").strip()
        secret = self.git("hash-object", "-w", "--stdin", data=self.credential() + b"\n").strip()
        rows = b"100644 " + clean + b" 1\tconflict.txt\n100644 " + secret + b" 2\tconflict.txt\n100644 " + clean + b" 3\tconflict.txt\n"
        self.git("update-index", "--index-info", data=rows)
        (self.repo / "conflict.txt").write_text("resolved-looking clean\n")
        value = self.result(self.cli("check", "--scope", "index", "--json"), 2)
        self.assertEqual(value["reason"], "index_unresolved")
        self.result(self.cli("check", "--json"), 1)

    def test_missing_detector_keeps_help_but_fails_check(self):
        copy = self.base / "bundle"
        (copy / "scripts").mkdir(parents=True)
        shutil.copy2(CLI, copy / "scripts/scan-secrets.py")
        shutil.copytree(ROOT / "hooks/runtime", copy / "hooks/runtime")
        (copy / "hooks/runtime/scan_stream.py").unlink()
        entry = copy / "scripts/scan-secrets.py"
        self.assertEqual(self.cli("--help", entry=entry, cwd=self.base).returncode, 0)
        self.assertEqual(self.cli("--version", entry=entry, cwd=self.base).returncode, 0)
        self.assertEqual(self.result(self.cli("check", "--json", entry=entry), 2)["reason"], "runtime_unavailable")

    def test_required_audit_failure_never_returns_complete_clean(self):
        data = self.base / "data"
        data.mkdir()
        (data / "scan-secrets").write_text("not a directory")
        value = self.result(self.cli("check", "--json"), 2)
        self.assertEqual(value["reason"], "audit_unavailable")
        self.assertEqual(value["audit_outcome"], "failed")
        self.assertTrue(value["coverage_complete"], "content coverage stays independent of required audit")

    def test_audit_link_and_worktree_data_roots_are_rejected(self):
        outside = self.base / "outside"
        outside.mkdir()
        (self.base / "data").mkdir()
        os.symlink(outside, self.base / "data/scan-secrets")
        self.assertEqual(self.result(self.cli("check", "--json"), 2)["reason"], "audit_unavailable")
        self.assertEqual(list(outside.iterdir()), [])
        env = {**self.env, "XDG_DATA_HOME": str(self.repo / "private-data")}
        self.assertEqual(self.result(self.cli("check", "--json", env=env), 2)["reason"], "audit_unavailable")
        self.assertFalse((self.repo / "private-data").exists())

    def test_hardlinked_audit_cannot_mutate_tracked_source(self):
        source = self.repo / "source.txt"
        source.write_text("original source\n")
        source.chmod(0o644)
        self.commit()
        index = (self.repo / ".git/index").read_bytes()
        app_data = self.base / "data/scan-secrets"
        app_data.mkdir(parents=True)
        os.link(source, app_data / "audit.jsonl")
        value = self.result(self.cli("check", "--json"), 2)
        self.assertEqual(value["reason"], "audit_unavailable")
        self.assertEqual(source.read_text(), "original source\n")
        self.assertEqual(source.stat().st_mode & 0o777, 0o644)
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)

    def test_hardlinked_audit_lock_cannot_change_tracked_source_mode(self):
        source = self.repo / "source.txt"
        source.write_text("original source\n")
        source.chmod(0o644)
        self.commit()
        app_data = self.base / "data/scan-secrets"
        app_data.mkdir(parents=True)
        os.link(source, app_data / "audit.jsonl.lock")
        self.result(self.cli("check", "--json"), 2)
        self.assertEqual(source.read_text(), "original source\n")
        self.assertEqual(source.stat().st_mode & 0o777, 0o644)

    @unittest.skipIf(os.name == "nt", "POSIX executable fixture; native Windows remains separate")
    def test_fractional_deadline_reports_the_effective_configured_limit(self):
        binary = self.base / "bin"
        binary.mkdir()
        wrapper = binary / "git"
        wrapper.write_text("#!" + sys.executable + "\nimport os,sys,time\n"
            "if sys.argv[1:2]==['ls-files']: time.sleep(10)\n"
            "os.execv(" + repr(GIT) + ",[" + repr(GIT) + "]+sys.argv[1:])\n")
        wrapper.chmod(0o755)
        budget = self.base / "deadline.json"
        budget.write_text(json.dumps(dict(schema_version=1,
            checkpoint=dict(max_objects=4096, max_candidate_bytes=67108864, max_seconds=1.25,
                            max_capture_bytes=134217728, max_temp_bytes=268435456),
            publication=dict(max_objects=20000, max_candidate_bytes=268435456, max_seconds=120,
                             max_capture_bytes=536870912, max_temp_bytes=805306368))))
        env = {**self.env, "PATH": str(binary) + os.pathsep + self.env["PATH"]}
        value = self.result(self.cli("check", "--json", "--budget-file", str(budget), env=env), 2)
        self.assertEqual(value["reason"], "scan_timeout")
        self.assertEqual(value["diagnostic"]["seconds"], 1.25)
        self.assertEqual(value["diagnostic"]["unit"], "seconds")

    def test_larger_default_envelope_detects_late_credential_and_stays_finite(self):
        for number in range(300):
            (self.repo / f"candidate-{number:04}.bin").write_bytes(b"\0" * 32768)
        clean = self.result(self.cli("check", "--json"), 0)
        self.assertEqual(clean["counts"]["inspected_snapshots"], 300)
        self.assertGreater(clean["counts"]["candidate_bytes"], 8388608)
        path = self.repo / "candidate-0299.bin"
        path.write_bytes(path.read_bytes() + self.credential())
        value = self.result(self.cli("check", "--json"), 1)
        self.assertGreater(value["counts"]["processed_findings"], 0)
        self.assertEqual(value["limits"]["max_objects"], 4096)
        # An explicit smaller profile is a finite failure, never truncated clean.
        budget = self.base / "small.json"
        budget.write_text(json.dumps(dict(schema_version=1,
            checkpoint=dict(max_objects=4096, max_candidate_bytes=1048576, max_seconds=30,
                            max_capture_bytes=134217728, max_temp_bytes=268435456),
            publication=dict(max_objects=20000, max_candidate_bytes=268435456, max_seconds=120,
                             max_capture_bytes=536870912, max_temp_bytes=805306368))))
        value = self.result(self.cli("check", "--json", "--budget-file", str(budget)), 2)
        self.assertEqual(value["reason"], "total_bytes_limit")
        self.assertEqual(value["diagnostic"]["limit"], 1048576)

    def test_display_retention_is_distinct_from_processed_finding_cap(self):
        path = self.repo / "many.txt"
        path.write_bytes((self.credential() + b"\n") * 101)
        value = self.result(self.cli("check", "--json"), 1)
        self.assertEqual(len(value["findings"]), 100)
        self.assertEqual(value["counts"]["processed_findings"], 101)
        self.assertTrue(value["coverage_complete"])
        path.write_bytes((self.credential() + b"\n") * 1001)
        value = self.result(self.cli("check", "--json"), 2)
        self.assertEqual(value["reason"], "findings_limit")
        self.assertEqual(value["counts"]["processed_findings"], 1000)

    def test_capture_and_temporary_budgets_are_independent_finite_bounds(self):
        checkpoint = dict(max_objects=4096, max_candidate_bytes=67108864, max_seconds=30,
                          max_capture_bytes=134217728, max_temp_bytes=268435456)
        publication = dict(max_objects=20000, max_candidate_bytes=268435456, max_seconds=120,
                           max_capture_bytes=536870912, max_temp_bytes=805306368)
        budget = self.base / "resources.json"
        (self.repo / "large.bin").write_bytes(b"\0" * 2097152)
        budget.write_text(json.dumps(dict(schema_version=1,
            checkpoint={**checkpoint, "max_temp_bytes": 1048576}, publication=publication)))
        value = self.result(self.cli("check", "--json", "--budget-file", str(budget)), 2)
        self.assertEqual(value["reason"], "temporary_bytes_limit")
        self.assertGreater(value["diagnostic"]["measured"], 1048576)
        (self.repo / "large.bin").unlink()
        for number in range(10):
            (self.repo / f"object-{number}.bin").write_bytes(b"\0" * 131072)
        self.git("add", "--all")
        budget.write_text(json.dumps(dict(schema_version=1,
            checkpoint={**checkpoint, "max_capture_bytes": 1048576}, publication=publication)))
        value = self.result(self.cli("check", "--scope", "index", "--json", "--budget-file", str(budget)), 2)
        self.assertEqual(value["reason"], "capture_bytes_limit")
        self.assertEqual(value["diagnostic"]["limit"], 1048576)

    def test_closed_output_pipe_exits_without_tracebacks(self):
        for args in ((), ("help", "check"), ("--help",), ("check", "--json")):
            with self.subTest(args=args):
                with subprocess.Popen([sys.executable, str(CLI), *args], cwd=self.repo, env=self.env,
                        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                    process.stdout.close()
                    process.wait(timeout=5)
                    stderr = process.stderr.read()
                self.assertNotEqual(process.returncode, 0)
                self.assertNotIn(b"Traceback", stderr)
                self.assertNotIn(b"Exception ignored", stderr)

    @unittest.skipIf(os.name == "nt", "requires native POSIX sessions; Windows proof remains separate")
    def test_cancellation_cleans_the_canonical_separate_git_session(self):
        marker = self.base / "git-pid.json"
        binary = self.base / "bin"
        binary.mkdir()
        wrapper = binary / "git"
        wrapper.write_text("#!" + sys.executable + "\nimport json,os,time\nfrom pathlib import Path\n"
            "Path(" + repr(str(marker)) + ").write_text(json.dumps({'pid':os.getpid(),'parent':os.getppid(),'group':os.getpgrp(),'session':os.getsid(0)}))\ntime.sleep(60)\n")
        wrapper.chmod(0o755)
        env = {**self.env, "PATH": str(binary) + os.pathsep + self.env["PATH"]}
        child = None
        try:
            with subprocess.Popen([sys.executable, str(CLI), "check", "--json"], cwd=self.repo, env=env,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                deadline = time.monotonic() + 3
                while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
                    time.sleep(0.02)
                self.assertTrue(marker.exists(), "canonical capture did not start Git")
                details = json.loads(marker.read_text())
                child = details["pid"]
                self.assertEqual(details["group"], child)
                self.assertEqual(details["session"], child)
                self.assertNotEqual(os.getpgid(details["parent"]), child)
                process.send_signal(signal.SIGINT)
                stdout, stderr = process.communicate(timeout=3)
                self.assertEqual(process.returncode, 130, stdout + stderr)
                self.assertEqual(json.loads(stdout)["reason"], "cancelled")
                self.assertNotIn(b"Traceback", stderr)
            observed = subprocess.run(["ps", "-o", "stat=", "-p", str(child)], capture_output=True, timeout=2)
            self.assertTrue(not observed.stdout.strip() or observed.stdout.lstrip().startswith(b"Z"), observed.stdout)
        finally:
            if child is not None:
                try:
                    os.kill(child, signal.SIGKILL)
                except ProcessLookupError:
                    pass


if __name__ == "__main__":
    unittest.main()

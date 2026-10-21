#!/usr/bin/env python3
"""Historical status contract through isolated standalone CLI processes."""
from pathlib import Path
import json
import os
import shutil
import signal
import time
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts/scan-secrets.py"
GIT = shutil.which("git")


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="scan-status-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("GIT_", "PYTHON", "SCAN_SECRETS_"))}
        self.env.update(HOME=str(self.base / "home"), USERPROFILE=str(self.base / "home"),
            XDG_DATA_HOME=str(self.base / "data"), LOCALAPPDATA=str(self.base / "data"),
            GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.git("init", "--quiet")

    def git(self, *args):
        return subprocess.run([GIT, "-c", "commit.gpgsign=false", "-c", "user.name=Fixture",
            "-c", "user.email=fixture@example.invalid", *args], cwd=self.repo, env=self.env,
            capture_output=True, check=True, timeout=10).stdout

    def cli(self, *args, cwd=None, env=None, entry=CLI):
        return subprocess.run([sys.executable, "-I", "-S", "-B", str(entry), *args],
            cwd=cwd or self.repo, env=env or self.env, input=b"hostile unconsumed stdin",
            capture_output=True, timeout=8)

    def status(self, *, cwd=None, env=None, entry=CLI, code=0):
        process = self.cli("status", "--json", cwd=cwd, env=env, entry=entry)
        self.assertEqual(process.returncode, code, (process.stdout, process.stderr))
        self.assertEqual(process.stderr, b"")
        value = json.loads(process.stdout)
        self.assertEqual(value["schema"], "scan_secrets_status_v1")
        self.assertTrue(value["historical"])
        self.assertFalse(value["authorizes_publication"])
        return value

    @staticmethod
    def credential():
        return ("gh" + "p_" + "A" * 36).encode()

    def test_explicit_checks_save_clean_findings_and_incomplete_history(self):
        for content, exit_code, outcome in ((b"clean\n", 0, "complete_clean"),
                (self.credential() + b"\n", 1, "complete_findings")):
            with self.subTest(outcome=outcome):
                (self.repo / "pending.txt").write_bytes(content)
                checked = self.cli("check", "--json")
                self.assertEqual(checked.returncode, exit_code, checked.stdout + checked.stderr)
                check = json.loads(checked.stdout)
                self.assertEqual(check["status_outcome"], "written")
                value = self.status()
                self.assertEqual(value["outcome"], "last_scan")
                last = value["last_scan"]
                self.assertEqual(last["outcome"], outcome)
                self.assertEqual(last["scope"], "worktree")
                self.assertEqual(last["scope_identity"], check["scope_identity"])
                self.assertEqual(last["build"], check["build"])
                self.assertTrue(last["coverage_complete"])
                self.assertRegex(last["completed_at"], r"^\d{4}-\d\d-\d\dT.*Z$")
                self.assertNotIn(self.credential(), value.__repr__().encode())
                self.assertNotIn("findings", last)
        os.symlink(self.base / "absent", self.repo / "unsafe.bin")
        checked = self.cli("check", "--json")
        self.assertEqual(checked.returncode, 2, checked.stdout + checked.stderr)
        last = self.status()["last_scan"]
        self.assertEqual(last["outcome"], "incomplete")
        self.assertFalse(last["coverage_complete"])
        self.assertEqual(last["reason"], "candidate_unsafe")
        self.assertEqual(last["security_outcome"], "findings")
        self.assertGreater(last["counts"]["processed_findings"], 0)

    def test_separate_git_directories_preserve_meaningful_trailing_spaces(self):
        first, second = self.base / "first", self.base / "second"
        first.mkdir()
        second.mkdir()
        admin = self.base / "admin"
        for worktree, gitdir in ((first, admin), (second, Path(str(admin) + " "))):
            subprocess.run([GIT, "init", "--quiet", "--separate-git-dir", str(gitdir), str(worktree)],
                env=self.env, check=True, capture_output=True, timeout=5)
        (first / "pending.txt").write_bytes(self.credential())
        self.assertEqual(self.cli("check", "--json", cwd=first).returncode, 1)
        self.assertEqual(self.status(cwd=second)["outcome"], "not_scanned")
        self.assertEqual(self.cli("check", "--json", cwd=second).returncode, 0)
        left, right = self.status(cwd=first), self.status(cwd=second)
        self.assertNotEqual(left["worktree_identity"], right["worktree_identity"])
        self.assertEqual(left["last_scan"]["outcome"], "complete_findings")
        self.assertEqual(right["last_scan"]["outcome"], "complete_clean")

    def test_history_is_unchanged_after_content_edit_and_linked_worktree_is_distinct(self):
        (self.repo / "tracked.txt").write_text("clean\n")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "fixture")
        checked = self.cli("check", "--scope", "index", "--json")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        before = self.status()
        (self.repo / "tracked.txt").write_bytes(self.credential())
        self.assertEqual(self.status(), before)
        nested = self.repo / "nested"
        nested.mkdir()
        self.assertEqual(self.status(cwd=nested), before)
        linked = self.base / "linked"
        self.git("worktree", "add", "--quiet", "-b", "fixture-linked", str(linked))
        self.assertEqual(self.status(cwd=linked)["outcome"], "not_scanned")
        self.assertEqual(self.cli("check", "--json", cwd=linked).returncode, 0)
        other = self.status(cwd=linked)
        self.assertNotEqual(other["worktree_identity"], before["worktree_identity"])
        self.assertEqual(other["last_scan"]["scope"], "worktree")
        self.assertEqual(self.status(), before)

    def seed(self):
        process = self.cli("check", "--json")
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        reports = list((self.base / "data/scan-secrets/status").glob("*.json"))
        self.assertEqual(len(reports), 1)
        self.assertLessEqual(reports[0].stat().st_size, 65536)
        return reports[0]

    def bundle(self):
        root = self.base / "bundle"
        (root / "scripts").mkdir(parents=True)
        shutil.copy2(CLI, root / "scripts/scan-secrets.py")
        shutil.copytree(ROOT / "hooks/runtime", root / "hooks/runtime")
        return root / "scripts/scan-secrets.py"

    def wrapper(self, setup, *, entry=CLI):
        path = self.base / ("wrapper-" + str(len(list(self.base.glob("wrapper-*")))) + ".py")
        path.write_text("import os,sys,runpy,time\nfrom pathlib import Path\n" + setup + "\n"
            "sys.argv=[" + repr(str(entry)) + "]+sys.argv[1:]\nrunpy.run_path(" + repr(str(entry)) + ",run_name='__main__')\n")
        return path

    def test_strict_records_reject_corruption_oversize_unknown_fields_and_raw_values(self):
        report = self.seed()
        original = report.read_bytes()
        value = json.loads(original)
        cases = [b"{", b"x" * 65537, original.replace(b'"schema":', b'"schema":1,"schema":', 1)]
        for change in ({"extra": self.credential().decode()}, {"schema": "future"},
                {"worktree_identity": "0" * 64}, {"completed_at": "not a time"},
                {"reason": "https://fake-user:fake-password@example.invalid"}, {"coverage_complete": 1},
                {"counts": {**value["counts"], "candidate_bytes": True}},
                {"security_outcome": "findings"}, {"status_outcome": "permission_to_publish"}):
            cases.append(json.dumps({**value, **change}).encode())
        for raw in cases:
            with self.subTest(raw=raw[:80]):
                report.write_bytes(raw)
                response = self.status(code=2)
                self.assertEqual(response["outcome"], "unavailable")
                self.assertIsNone(response["last_scan"])
                self.assertNotIn(self.credential().decode(), json.dumps(response))
                self.assertNotIn("fake-password", json.dumps(response))
                self.assertEqual(report.read_bytes(), raw, "read-only status must not repair corruption")
        # An explicit check can replace corrupt display bytes.
        self.assertEqual(self.cli("check", "--json").returncode, 0)
        self.assertEqual(self.status()["last_scan"]["outcome"], "complete_clean")

    def test_symlinks_hardlinks_and_unsafe_storage_never_modify_source(self):
        report = self.seed()
        source = self.repo / "tracked.txt"
        source.write_text("original clean source\n")
        source.chmod(0o600)
        original = report.read_bytes()
        for kind in ("symlink", "hardlink"):
            with self.subTest(kind=kind):
                report.unlink()
                if kind == "symlink":
                    os.symlink(source, report)
                else:
                    os.link(source, report)
                self.assertEqual(self.status(code=2)["outcome"], "unavailable")
                process = self.cli("check", "--json")
                self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                value = json.loads(process.stdout)
                self.assertEqual(value["security_outcome"], "clean")
                self.assertEqual(value["status_outcome"], "failed")
                self.assertEqual(source.read_text(), "original clean source\n")
                if os.name == "posix":
                    self.assertEqual(source.stat().st_mode & 0o777, 0o600)
        report.unlink()
        report.write_bytes(original)
        report.chmod(0o600)
        lock = report.with_name(report.name + ".lock")
        lock.unlink()
        os.link(source, lock)
        result = self.cli("check", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status_outcome"], "failed")
        self.assertEqual(source.read_text(), "original clean source\n")
        self.assertEqual(source.stat().st_mode & 0o777, 0o600)

    def test_posix_private_permissions_and_unreadable_report(self):
        if os.name != "posix":
            self.fail("POSIX mode evidence requires a POSIX host; use native Windows ACL evidence separately")
        report = self.seed()
        for path in (report, report.with_name(report.name + ".lock")):
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        for path in (report.parent, report.parent.parent):
            self.assertEqual(path.stat().st_mode & 0o777, 0o700)
        for path, mode in ((report, 0), (report, 0o644), (report.parent, 0o755)):
            with self.subTest(path=path, mode=mode):
                original_mode = path.stat().st_mode & 0o777
                path.chmod(mode)
                try:
                    self.assertEqual(self.status(code=2)["outcome"], "unavailable")
                    self.assertEqual(path.stat().st_mode & 0o777, mode)
                finally:
                    path.chmod(original_mode)

    def test_redirected_roots_and_worktree_locations_are_rejected_without_writes(self):
        target = self.base / "outside"
        target.mkdir()
        link = self.base / "redirect"
        os.symlink(target, link)
        for data in (link, link / "nested", self.repo / "private-data"):
            with self.subTest(data=data):
                env = {**self.env, "XDG_DATA_HOME": str(data), "LOCALAPPDATA": str(data)}
                self.assertEqual(self.status(env=env, code=2)["outcome"], "unavailable")
                checked = self.cli("check", "--json", env=env)
                self.assertEqual(checked.returncode, 2, checked.stdout + checked.stderr)
                value = json.loads(checked.stdout)
                self.assertEqual(value["status_outcome"], "failed")
                self.assertEqual(value["security_outcome"], "clean")
        self.assertEqual(list(target.iterdir()), [])
        self.assertFalse((self.repo / "private-data").exists())

    def test_status_never_runs_git_network_detector_or_writes_or_enumerates_content(self):
        report = self.seed()
        expected = self.status()
        entry = self.bundle()
        for module in (entry.parent.parent / "hooks/runtime").glob("*.py"):
            if module.name not in {"scan_cli.py", "scan_status.py", "scan_native_file.py"}:
                module.unlink()
        sentinel = r"""
def guard(event,args):
 if event in {'subprocess.Popen','os.system','socket.__new__','socket.connect','os.mkdir','os.rename','os.remove','os.chmod'}:
  os.write(2,b'FORBIDDEN SIDE EFFECT '+event.encode()+b'\n');raise RuntimeError('forbidden')
 if event in {'os.listdir','os.scandir'} and str(args[0]).startswith((os.getcwd(),os.environ['XDG_DATA_HOME'])):
  os.write(2,b'FORBIDDEN ENUMERATION\n');raise RuntimeError('forbidden')
 if event=='open':
  path,mode,flags=args
  if flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND) or str(path).endswith(('/index','/config','/tracked.txt')):
   os.write(2,b'FORBIDDEN OPEN\n');raise RuntimeError('forbidden')
sys.addaudithook(guard)
"""
        wrapper = self.wrapper(sentinel, entry=entry)
        before = {path: (path.stat().st_mtime_ns, path.read_bytes()) for path in report.parent.parent.rglob("*") if path.is_file()}
        env = {**self.env, "GIT_DIR": str(self.base / "poison"), "GIT_WORK_TREE": str(self.base / "poison"),
               "HTTP_PROXY": "http://fake-user:fake-password@example.invalid", "SCAN_SECRETS_SKIP": "true"}
        self.assertEqual(self.status(entry=wrapper, env=env), expected)
        after = {path: (path.stat().st_mtime_ns, path.read_bytes()) for path in report.parent.parent.rglob("*") if path.is_file()}
        self.assertEqual(after, before)
        with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(wrapper), "status", "--json"],
                cwd=self.repo, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            process.wait(timeout=3)
            self.assertEqual(process.returncode, 0, process.stderr.read())
            self.assertEqual(json.loads(process.stdout.read()), expected)

    def test_missing_status_helper_preserves_check_security_and_help(self):
        entry = self.bundle()
        (entry.parent.parent / "hooks/runtime/scan_status.py").unlink()
        (self.repo / "pending.txt").write_bytes(self.credential())
        check = self.cli("check", "--json", entry=entry)
        self.assertEqual(check.returncode, 1, check.stdout + check.stderr)
        value = json.loads(check.stdout)
        self.assertEqual(value["security_outcome"], "findings")
        self.assertEqual(value["status_outcome"], "failed")
        self.assertEqual(value["audit_outcome"], "written")
        self.assertEqual(self.cli("help", "status", entry=entry).returncode, 0)
        self.assertEqual(self.status(entry=entry, code=2)["reason"], "status_runtime_unavailable")
        human = self.cli("status", entry=entry)
        self.assertEqual((human.returncode, human.stdout), (2, b""))
        self.assertIn(b"last scan unavailable", human.stderr)
        self.assertIn(b"time and scope unavailable", human.stderr)

    def test_missing_filesystem_helper_is_a_safe_runtime_failure(self):
        entry = self.bundle()
        (entry.parent.parent / "hooks/runtime/scan_native_file.py").unlink()
        self.assertEqual(self.status(entry=entry, code=2)["reason"], "status_runtime_unavailable")
        checked = self.cli("check", "--json", entry=entry)
        self.assertEqual(checked.returncode, 2, checked.stdout + checked.stderr)
        value = json.loads(checked.stdout)
        self.assertEqual(value["security_outcome"], "incomplete")
        self.assertEqual(value["status_outcome"], "failed")
        self.assertNotIn(b"Traceback", checked.stderr)
        self.assertEqual(self.cli("help", "status", entry=entry).returncode, 0)

    def test_display_write_failure_retains_findings_and_previous_record(self):
        self.seed()
        before = self.status()
        (self.repo / "pending.txt").write_bytes(self.credential())
        wrapper = self.wrapper(r"""
real_replace=os.replace
def replace(source,target,*args,**kwargs):
 if str(target).endswith('.json'):raise OSError('fake-password raw storage exception')
 return real_replace(source,target,*args,**kwargs)
os.replace=replace
""")
        process = self.cli("check", "--json", entry=wrapper)
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        value = json.loads(process.stdout)
        self.assertEqual(value["security_outcome"], "findings")
        self.assertEqual(value["outcome"], "complete_findings")
        self.assertEqual(value["status_outcome"], "failed")
        self.assertEqual(value["audit_outcome"], "written")
        self.assertNotIn(b"fake-password", process.stdout + process.stderr)
        self.assertEqual(self.status(), before)
        self.assertEqual(list((self.base / "data/scan-secrets/status").glob("*.tmp")), [])

    def test_missing_detector_records_incomplete_and_audit_failure_stays_independent(self):
        entry = self.bundle()
        (entry.parent.parent / "hooks/runtime/scan_stream.py").unlink()
        process = self.cli("check", "--json", entry=entry)
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        last = self.status()["last_scan"]
        self.assertEqual(last["outcome"], "incomplete")
        self.assertEqual(last["reason"], "runtime_unavailable")
        self.assertEqual(last["security_outcome"], "incomplete")
        audit = self.base / "data/scan-secrets/audit.jsonl"
        audit.mkdir()
        process = self.cli("check", "--json")
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        last = self.status()["last_scan"]
        self.assertEqual(last["audit_outcome"], "failed")
        self.assertEqual(last["security_outcome"], "clean")
        self.assertEqual(last["outcome"], "incomplete")
        self.assertTrue(last["coverage_complete"])

    def test_help_common_flags_errors_and_text_describe_history(self):
        for args in ((), ("--help",), ("help",), ("help", "status"), ("status", "--help")):
            with self.subTest(args=args):
                process = self.cli(*args, cwd=self.base)
                self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                self.assertEqual(process.stderr, b"")
                self.assertIn(b"status", process.stdout)
        for args in (("status", "--js"), ("status", "--scope", "index"), ("status", "unknown")):
            with self.subTest(args=args):
                process = self.cli(*args, "--json")
                self.assertEqual(process.returncode, 3, process.stdout + process.stderr)
                self.assertEqual(json.loads(process.stdout)["schema"], "scan_secrets_status_v1")
                self.assertEqual(process.stderr, b"")
        quiet = self.cli("status", "--quiet", "--no-input", "--no-color")
        self.assertEqual((quiet.returncode, quiet.stdout, quiet.stderr), (0, b"", b""))
        for args in (("--json", "--quiet", "--no-input", "--no-color", "status"),
                     ("status", "--json", "--quiet", "--no-input", "--no-color")):
            process = self.cli(*args)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertEqual(json.loads(process.stdout)["outcome"], "not_scanned")
        self.seed()
        last = self.status()["last_scan"]
        process = self.cli("status", "--no-color", env={**self.env, "NO_COLOR": "1", "TERM": "dumb"})
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn(b"last scan", process.stdout)
        self.assertIn(last["completed_at"].encode(), process.stdout)
        self.assertIn(b"scope worktree", process.stdout)
        self.assertIn(b"current content has not been checked by status", process.stdout)
        self.assertNotIn(b"\x1b", process.stdout + process.stderr)
        report = next((self.base / "data/scan-secrets/status").glob("*.json"))
        report.write_bytes(b"broken")
        process = self.cli("status", "--quiet")
        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, b"")
        self.assertIn(b"last scan unavailable", process.stderr)

    def test_missing_parser_retains_versioned_status_unavailable(self):
        entry = self.bundle()
        (entry.parent.parent / "hooks/runtime/scan_cli.py").unlink()
        self.assertEqual(self.status(entry=entry, code=2)["reason"], "runtime_unavailable")
        human = self.cli("status", entry=entry)
        self.assertEqual((human.returncode, human.stdout), (2, b""))
        self.assertIn(b"last scan unavailable", human.stderr)
        self.assertIn(b"time and scope unavailable", human.stderr)

    def test_status_closed_pipe_exits_without_traceback(self):
        for args in (("status", "--json"), ("status",), ("help", "status")):
            with self.subTest(args=args):
                with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(CLI), *args],
                        cwd=self.repo, env=self.env, stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                    process.stdout.close()
                    process.wait(timeout=3)
                    stderr = process.stderr.read()
                self.assertNotEqual(process.returncode, 0)
                self.assertNotIn(b"Traceback", stderr)
                self.assertNotIn(b"Exception ignored", stderr)

    def test_fifo_and_oversized_git_metadata_are_bounded_errors(self):
        report = self.seed()
        report.unlink()
        os.mkfifo(report, 0o600)
        self.assertEqual(self.status(code=2)["outcome"], "unavailable")
        head = self.repo / ".git/HEAD"
        original = head.read_bytes()
        for raw in (b"x" * 4097, b""):
            head.write_bytes(raw)
            self.assertEqual(self.status(code=2)["reason"], "repository_metadata_invalid")
        head.write_bytes(original)

    def test_lock_timeout_does_not_block_status_or_erase_scan_result(self):
        if os.name != "posix":
            self.fail("This lock-contention proof requires POSIX; native Windows locking is separate")
        import fcntl
        report = self.seed()
        previous = self.status()
        with report.with_name(report.name + ".lock").open("rb") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            self.assertEqual(self.status(), previous)
            started = time.monotonic()
            checked = self.cli("check", "--json")
            self.assertLess(time.monotonic() - started, 4)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        value = json.loads(checked.stdout)
        self.assertEqual(value["status_outcome"], "failed")
        self.assertEqual(value["status_reason"], "status_timeout")
        self.assertEqual(value["security_outcome"], "clean")
        self.assertEqual(self.status(), previous)

    def wait_marker(self, marker, process):
        deadline = time.monotonic() + 4
        while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(marker.exists(), "writer did not reach the actual OS boundary")

    def test_concurrent_writers_keep_the_last_completed_scan_when_older_writer_delays(self):
        if os.name != "posix":
            self.fail("POSIX flock ordering fixture; Windows requires its native equivalent")
        marker, resume = self.base / "ready", self.base / "resume"
        wrapper = self.wrapper("import fcntl\nreal_flock=fcntl.flock\nreal_open=os.open\nreport_locks=set()\n"
            "def open_file(path,*args,**kwargs):\n fd=real_open(path,*args,**kwargs)\n"
            " if str(path).endswith('.json.lock'):report_locks.add(fd)\n return fd\nos.open=open_file\n"
            "def flock(fd,operation):\n"
            " if operation==fcntl.LOCK_EX|fcntl.LOCK_NB and fd in report_locks:\n"
            "  Path(" + repr(str(marker)) + ").touch()\n  until=time.monotonic()+6\n"
            "  while not Path(" + repr(str(resume)) + ").exists() and time.monotonic()<until:time.sleep(.01)\n"
            " return real_flock(fd,operation)\nfcntl.flock=flock\n")
        (self.repo / "pending.txt").write_bytes(self.credential())
        with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(wrapper), "check", "--json"],
                cwd=self.repo, env=self.env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            try:
                self.wait_marker(marker, process)
                self.assertEqual(self.status()["outcome"], "not_scanned", "status must not wait for or start a scan")
                newer = self.cli("check", "--scope", "index", "--json")
                self.assertEqual(newer.returncode, 0, newer.stdout + newer.stderr)
                last = self.status()
                self.assertEqual(last["last_scan"]["scope"], "index")
            finally:
                resume.touch()
            stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 1, stdout + stderr)
        old = json.loads(stdout)
        self.assertEqual(old["status_outcome"], "superseded")
        self.assertEqual(old["security_outcome"], "findings")
        self.assertEqual(self.status(), last)

    def test_interrupted_atomic_write_leaves_the_previous_historical_record(self):
        self.seed()
        previous = self.status()
        marker = self.base / "replace-ready"
        wrapper = self.wrapper("real_replace=os.replace\n"
            "def replace(source,target,*args,**kwargs):\n"
            " if str(target).endswith('.json'):\n  Path(" + repr(str(marker)) + ").touch()\n  time.sleep(6)\n"
            " return real_replace(source,target,*args,**kwargs)\nos.replace=replace\n")
        (self.repo / "pending.txt").write_bytes(self.credential())
        with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(wrapper), "check", "--json"],
                cwd=self.repo, env=self.env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            try:
                self.wait_marker(marker, process)
                self.assertEqual(self.status(), previous, "reader does not wait on a writer lock")
            finally:
                process.kill()
                process.communicate(timeout=3)
        self.assertEqual(self.status(), previous)
        # The next explicit scan can proceed after the killed writer's OS lock releases.
        self.assertEqual(self.cli("check", "--json").returncode, 1)
        self.assertEqual(self.status()["last_scan"]["outcome"], "complete_findings")

    def test_check_executes_the_status_source_captured_for_its_build(self):
        entry = self.bundle()
        marker = self.base / "changed-helper-executed"
        replacement = "from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\nraise RuntimeError('changed status helper')\n"
        wrapper = self.wrapper("real_read=Path.read_bytes\nchanged=False\n"
            "def read_bytes(path):\n global changed\n raw=real_read(path)\n"
            " if path.name=='scan_status.py' and not changed:\n  changed=True\n  path.write_text(" + repr(replacement) + ")\n"
            " return raw\nPath.read_bytes=read_bytes\n", entry=entry)
        process = self.cli("check", "--json", entry=wrapper)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        value = json.loads(process.stdout)
        self.assertEqual(value["status_outcome"], "written")
        self.assertFalse(marker.exists(), "check executed a replacement outside its captured build")
        self.assertEqual(self.status()["last_scan"]["build"], value["build"])

    def test_result_stays_bound_to_the_repository_metadata_captured_by_check(self):
        first, second = self.base / "first", self.base / "second"
        first.mkdir()
        second.mkdir()
        admin_a, admin_b = self.base / "admin-a", self.base / "admin-b"
        for root, admin in ((first, admin_a), (second, admin_b)):
            subprocess.run([GIT, "init", "--quiet", "--separate-git-dir", str(admin), str(root)],
                env=self.env, check=True, capture_output=True, timeout=5)
        (first / "pending.txt").write_bytes(self.credential())
        wrapper = self.wrapper("real_open=os.open\nchanged=False\n"
            "def open_file(path,*args,**kwargs):\n global changed\n"
            " if str(path).endswith('audit.jsonl') and not changed:\n  changed=True\n  Path(" + repr(str(first / ".git")) + ").write_text(" + repr("gitdir: " + str(admin_b) + "\n") + ")\n"
            " return real_open(path,*args,**kwargs)\nos.open=open_file\n")
        process = self.cli("check", "--json", cwd=first, entry=wrapper)
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["status_outcome"], "written")
        self.assertEqual(self.status(cwd=second)["outcome"], "not_scanned", "metadata drift misattributed another worktree's scan")
        (first / ".git").write_text("gitdir: " + str(admin_a) + "\n")
        self.assertEqual(self.status(cwd=first)["last_scan"]["outcome"], "complete_findings")

    def test_data_directory_substitution_cannot_redirect_a_report_write(self):
        app = self.base / "data/scan-secrets"
        moved = self.base / "moved-app"
        outside = self.base / "outside"
        outside.mkdir(mode=0o700)
        wrapper = self.wrapper("real_open=os.open\nreal_lstat=Path.lstat\naudit_seen=False\nchanged=False\n"
            "def open_file(path,*args,**kwargs):\n global audit_seen\n fd=real_open(path,*args,**kwargs)\n"
            " if str(path).endswith('audit.jsonl'):audit_seen=True\n return fd\nos.open=open_file\n"
            "def lstat(path,*args,**kwargs):\n global changed\n info=real_lstat(path,*args,**kwargs)\n"
            " if str(path)==" + repr(str(app)) + " and audit_seen and not changed:\n  changed=True\n"
            "  os.rename(" + repr(str(app)) + "," + repr(str(moved)) + ")\n"
            "  os.symlink(" + repr(str(outside)) + "," + repr(str(app)) + ")\n"
            " return info\nPath.lstat=lstat\n")
        process = self.cli("check", "--json", entry=wrapper)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        value = json.loads(process.stdout)
        self.assertEqual(value["security_outcome"], "clean")
        self.assertEqual(value["status_outcome"], "failed")
        self.assertTrue(app.is_symlink(), "fixture did not replace the actual checked data directory")
        self.assertEqual(list(outside.iterdir()), [])

    def test_old_record_remains_historical_without_refresh_after_new_content(self):
        report = self.seed()
        value = json.loads(report.read_bytes())
        value.update(completed_at="2000-01-01T00:00:00.000000Z", completed_ns=946684800000000000,
                     completion_order_ns=1, scanner_version="0.9.0")
        report.write_text(json.dumps(value))
        before = report.read_bytes(), report.stat().st_mtime_ns
        (self.repo / "pending.txt").write_bytes(self.credential())
        last = self.status()["last_scan"]
        self.assertEqual(last["completed_at"], "2000-01-01T00:00:00.000000Z")
        self.assertEqual(last["scanner_version"], "0.9.0")
        self.assertEqual(last["outcome"], "complete_clean")
        self.assertEqual((report.read_bytes(), report.stat().st_mtime_ns), before)

    def test_reparse_metadata_is_rejected_at_the_filesystem_boundary(self):
        self.seed()
        wrapper = self.wrapper("real_stat=os.stat\n"
            "class Reparse:\n def __init__(self,info):self.info=info;self.st_file_attributes=0x400\n"
            " def __getattr__(self,name):return getattr(self.info,name)\n"
            "def stat_file(path,*args,**kwargs):\n info=real_stat(path,*args,**kwargs)\n"
            " return Reparse(info) if str(path).endswith('.json') else info\nos.stat=stat_file\n")
        self.assertEqual(self.status(entry=wrapper, code=2)["reason"], "status_unsafe")

    def test_explicit_repo_path_aliases_keep_the_same_canonical_identity(self):
        self.seed()
        expected = self.status()
        process = self.cli("status", "--repo", str(self.repo), "--json", cwd=self.base)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout), expected)
        alias = self.base / "repo-alias"
        os.symlink(self.repo, alias)
        process = self.cli("status", "--repo", str(alias), "--json", cwd=self.base)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout), expected)
        alternate_case = self.repo.with_name("REPO")
        if alternate_case.exists() and alternate_case.samefile(self.repo):
            process = self.cli("status", "--repo", str(alternate_case), "--json", cwd=self.base)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertEqual(json.loads(process.stdout), expected)

    def test_case_alias_cannot_place_audit_or_status_inside_the_worktree(self):
        alternate_case = self.repo.with_name("REPO")
        if not alternate_case.exists() or not alternate_case.samefile(self.repo):
            alternate_case = self.repo
        data = alternate_case / "private-data"
        env = {**self.env, "XDG_DATA_HOME": str(data), "LOCALAPPDATA": str(data)}
        self.assertEqual(self.status(env=env, code=2)["outcome"], "unavailable")
        process = self.cli("check", "--json", env=env)
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        value = json.loads(process.stdout)
        self.assertEqual(value["audit_outcome"], "failed")
        self.assertEqual(value["status_outcome"], "failed")
        self.assertEqual(value["security_outcome"], "clean")
        self.assertFalse((self.repo / "private-data").exists())

    def test_crlf_git_metadata_preserves_trailing_directory_spaces(self):
        root, admin = self.base / "separate", self.base / "admin "
        subprocess.run([GIT, "init", "--quiet", "--separate-git-dir", str(admin), str(root)],
            env=self.env, check=True, capture_output=True, timeout=5)
        marker = root / ".git"
        marker.write_bytes(marker.read_bytes()[:-1] + b"\r\n")
        resolved = subprocess.run([GIT, "-C", str(root), "rev-parse", "--absolute-git-dir"],
            env=self.env, check=True, capture_output=True, timeout=5)
        self.assertEqual(resolved.stdout, os.fsencode(admin) + b"\n")
        process = self.cli("check", "--json", cwd=root)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["status_outcome"], "written")
        self.assertEqual(self.status(cwd=root)["last_scan"]["outcome"], "complete_clean")
        prefix = marker.read_bytes().rstrip(b"\r\n")
        for terminator in (b"\n", b"\r", b"\r\n", b"\n\n", b"\r\r", b"\n\r"):
            with self.subTest(terminator=terminator):
                marker.write_bytes(prefix + terminator)
                accepted = subprocess.run([GIT, "-C", str(root), "rev-parse", "--absolute-git-dir"],
                    env=self.env, check=True, capture_output=True, timeout=5)
                self.assertEqual(accepted.stdout, os.fsencode(admin) + b"\n")
                self.assertEqual(self.status(cwd=root)["last_scan"]["outcome"], "complete_clean")

    def test_audit_prevalidation_does_not_canonicalize_a_substituted_user_ancestor(self):
        data = self.base / "data"
        data.mkdir(mode=0o700)
        moved = self.base / "moved-data"
        outside = self.base / "other-repository"
        outside.mkdir()
        subprocess.run([GIT, "init", "--quiet", str(outside)], env=self.env,
            check=True, capture_output=True, timeout=5)
        source = outside / "scan-secrets/audit.jsonl"
        source.parent.mkdir()
        source.write_bytes(b"original tracked source\n")
        source.chmod(0o644)
        subprocess.run([GIT, "-C", str(outside), "add", "--all"], env=self.env,
            check=True, capture_output=True, timeout=5)
        wrapper = self.wrapper("real_lstat=Path.lstat\nchanged=False\n"
            "def lstat(path,*args,**kwargs):\n global changed\n info=real_lstat(path,*args,**kwargs)\n"
            " if str(path)==" + repr(str(data)) + " and not changed:\n  changed=True\n"
            "  os.rename(" + repr(str(data)) + "," + repr(str(moved)) + ")\n"
            "  os.symlink(" + repr(str(outside)) + "," + repr(str(data)) + ")\n"
            " return info\nPath.lstat=lstat\n")
        process = self.cli("check", "--json", entry=wrapper)
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["audit_outcome"], "failed")
        self.assertTrue(data.is_symlink(), "fixture did not replace the validated user ancestor")
        self.assertEqual(source.read_bytes(), b"original tracked source\n")
        self.assertEqual(source.stat().st_mode & 0o777, 0o644)

    def test_missing_report_and_outside_repository_are_valid_without_writes(self):
        value = self.status()
        self.assertEqual(value["outcome"], "not_scanned")
        self.assertEqual(value["reason"], "report_missing")
        self.assertIsNone(value["last_scan"])
        self.assertEqual(self.status(cwd=self.base)["reason"], "not_repository")
        self.assertFalse((self.base / "data").exists())


if __name__ == "__main__":
    unittest.main()

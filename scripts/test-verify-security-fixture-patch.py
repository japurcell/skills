#!/usr/bin/env python3
"""Acceptance at the fixture-preflight CLI and generated-provider seams."""
from __future__ import annotations
import ast
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
import textwrap
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

    def run_cli(self, patch, *extra, active=ROOT, timeout=60, diagnose=False):
        launcher = self.scanner_diagnostics() if diagnose else CLI
        result = subprocess.run([sys.executable, str(launcher), "--patch", str(patch),
                                "--path", "fixture.py", "--active-hook-root", str(active),
                                "--json", "--no-input", *extra], cwd=self.repo, env=self.env,
                               capture_output=True, timeout=timeout)
        if diagnose:
            # Only the diagnostic launcher's fixed-vocabulary records leave the
            # private fixture; never echo scanner output or arbitrary stderr.
            for line in result.stderr.splitlines():
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if isinstance(record, dict) and (record.get("fixture_work") == "audit_boundary_v1"
                        or result.returncode and record.get("fixture_scanner") == "audit_boundary_v1"):
                    print(json.dumps(record, sort_keys=True), flush=True)
        return result

    def scanner_git_diagnostics(self):
        """Keep bounded numeric evidence at each real scanner Git boundary."""
        launcher = self.base / "scanner-git-diagnostics.py"
        launcher.write_text(textwrap.dedent("""
            import json, os, runpy, stat, subprocess, sys, time
            from pathlib import Path
            script, trace = sys.argv[1:]
            real = subprocess.Popen
            sequence = 0
            operations = {'rev-parse', 'diff', 'ls-files', 'ls-tree', 'cat-file',
                          'check-attr', 'show', 'init', 'hash-object', 'update-index', 'status'}
            def append(record):
                encoded = (json.dumps(record, sort_keys=True) + '\\n').encode('ascii')
                if len(encoded) > 1024:
                    encoded = b'{"trace_error":"record_limit"}\\n'
                try:
                    fd = os.open(trace, os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, 'O_NOFOLLOW', 0), 0o600)
                    with os.fdopen(fd, 'ab') as stream:
                        info = os.fstat(stream.fileno())
                        if stat.S_ISREG(info.st_mode) and info.st_size + len(encoded) <= 1048576:
                            stream.write(encoded)
                except OSError:
                    pass  # The outer observer reports an unavailable trace.
            class GitObserved(real):
                def __init__(self, command, *args, **kwargs):
                    global sequence
                    self.observe = Path(command[0]).name == 'git'
                    self.recorded = False
                    self.started = time.monotonic()
                    self.output = kwargs.get('stdout')
                    self.errors = kwargs.get('stderr')
                    self.operation = next((arg for arg in command[1:] if arg in operations), 'other_git')
                    if self.observe:
                        sequence += 1
                    self.sequence = sequence
                    super().__init__(command, *args, **kwargs)
                    self.launch_seconds = time.monotonic() - self.started
                    self.group = None
                    if self.observe:
                        try:
                            self.group = os.getpgid(self.pid)
                        except OSError:
                            pass
                def poll(self):
                    code = super().poll()
                    self.record()
                    return code
                def wait(self, *args, **kwargs):
                    code = super().wait(*args, **kwargs)
                    self.record()
                    return code
                def record(self):
                    if not self.observe or self.returncode is None or self.recorded:
                        return
                    self.recorded = True
                    if self.sequence > 256:
                        if self.sequence == 257:
                            append({'trace_error': 'event_limit'})
                        return
                    record = {'operation': self.operation, 'sequence': self.sequence,
                              'pid': self.pid, 'exit_status': self.returncode,
                              'launch_seconds': round(self.launch_seconds, 6),
                              'elapsed_seconds': round(time.monotonic() - self.started, 6)}
                    if self.group is not None:
                        record['group'] = self.group
                    for name, stream in (('stdout_bytes', self.output), ('stderr_bytes', self.errors)):
                        try:
                            record[name] = os.fstat(stream.fileno()).st_size
                        except (AttributeError, OSError, ValueError):
                            pass
                    append(record)
            subprocess.Popen = GitObserved
            sys.argv = [script]
            runpy.run_path(script, run_name='__main__')
        """))
        return launcher

    def scanner_diagnostics(self):
        """Observe real scanner completion using bounded, allowlisted audit fields."""
        types = ast.parse((ROOT / ".codex/hooks/helpers/scan_types.py").read_text())
        constants = {node.targets[0].id: ast.literal_eval(node.value) for node in types.body
                     if isinstance(node, ast.Assign) and len(node.targets) == 1
                     and isinstance(node.targets[0], ast.Name)
                     and node.targets[0].id in {"INCOMPLETE_CAUSES", "INCOMPLETE_OPERATIONS"}}
        launcher = self.base / "scanner-diagnostics.py"
        inner_launcher = self.scanner_git_diagnostics()
        source = "INNER_LAUNCHER = " + repr(str(inner_launcher)) + "\n"
        source += "KNOWN_CAUSES = " + repr(set(constants["INCOMPLETE_CAUSES"]) | {"clean", "findings", "not_repository"}) + "\n"
        source += "KNOWN_OPERATIONS = " + repr(constants["INCOMPLETE_OPERATIONS"]) + "\n"
        source += textwrap.dedent("""
            import ast, atexit, json, math, subprocess, sys, time, runpy
            from pathlib import Path
            real = subprocess.Popen
            work = {'git': 0, 'scanner': 0, 'observer': 0}
            atexit.register(lambda: print(json.dumps({'fixture_work': 'audit_boundary_v1',
                **work}, sort_keys=True), file=sys.stderr, flush=True))
            def label(value, choices):
                return value if isinstance(value, str) and value in choices else 'unrecognized'
            def number(value):
                return (type(value) is int or type(value) is float and math.isfinite(value)) and -2147483648 <= value <= 9223372036854775807
            class Diagnosed(real):
                def __init__(self, command, *args, **kwargs):
                    self.scanner = Path(command[-1]).name == 'scan-secrets.py'
                    if self.scanner:
                        work['scanner'] += 1
                    elif Path(command[0]).name == 'git':
                        work['git'] += 1
                    elif command[0] == '/bin/ps':
                        work['observer'] += 1
                    self.recorded = False
                    self.started = time.monotonic()
                    self.audit = Path(kwargs.get('env', {}).get('SECRETS_LOG_DIR', '.')) / 'scan.log'
                    self.trace = self.audit.with_name('scanner-git-diagnostic.jsonl')
                    self.expected_build = None
                    if self.scanner:
                        try:
                            nodes = ast.parse(Path(command[-1]).read_text()).body
                            self.expected_build = next(ast.literal_eval(node.value) for node in nodes
                                if isinstance(node, ast.Assign) and len(node.targets) == 1
                                and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'REPORT_BUILD')
                        except Exception:
                            pass
                        command = [*command[:-1], INNER_LAUNCHER, command[-1], str(self.trace)]
                    super().__init__(command, *args, **kwargs)
                def poll(self):
                    code = super().poll()
                    self.record()
                    return code
                def wait(self, *args, **kwargs):
                    code = super().wait(*args, **kwargs)
                    self.record()
                    return code
                def record(self):
                    if not self.scanner or self.returncode is None or self.recorded:
                        return
                    self.recorded = True
                    parts = self.audit.parts
                    report = {'fixture_scanner': 'audit_boundary_v1', 'exit_status': self.returncode,
                              'elapsed_seconds': round(time.monotonic() - self.started, 6),
                              'provider': label(parts[-2], {'codex', 'copilot', 'gemini'}),
                              'bundle': label(parts[-4], {'active', 'candidate'}),
                              'view': label(parts[-3], {'pending', 'complete-0', 'complete-1', 'control'})}
                    try:
                        with self.audit.open('rb') as stream:
                            raw = stream.read(1048577)
                        report['audit_bytes'] = len(raw)
                        if len(raw) > 1048576:
                            report['audit_result'] = 'over_limit'
                        else:
                            record = json.loads(raw)
                            if not isinstance(record, dict):
                                raise ValueError
                            report['audit_result'] = 'read'
                            expected = {'provider': parts[-2], 'build': self.expected_build, 'mode': 'block',
                                'scope': 'diff', 'profile': 'pending_snapshots_v1', 'route': 'pending_scan',
                                'inspection_outcome': 'complete', 'audit_outcome': 'written'}
                            report['required_mismatches'] = [key for key, value in expected.items()
                                if type(record.get(key)) is not type(value) or record.get(key) != value]
                            if self.expected_build is None:
                                report['required_mismatches'].append('expected_build_unavailable')
                            if record.get('status') not in {'clean', 'findings'}:
                                report['required_mismatches'].append('status')
                            if not isinstance(record.get('findings', []), list):
                                report['required_mismatches'].append('findings_type')
                            if type(record.get('findingsTruncated')) is not bool:
                                report['required_mismatches'].append('truncation_type')
                            if type(record.get('omittedFindings')) is not int or record['omittedFindings'] < 0:
                                report['required_mismatches'].append('omitted_count')
                            for key, choices in {'status': {'clean', 'findings', 'incomplete'},
                                    'inspection_outcome': {'complete', 'incomplete'},
                                    'audit_outcome': {'written', 'failed', 'not_attempted'},
                                    'security_outcome': {'clean', 'findings', 'incomplete'},
                                    'enforcement': {'allow', 'deny'}}.items():
                                report[key] = label(record.get(key), choices)
                            report['cause'] = label(record.get('cause'), KNOWN_CAUSES)
                            failure = record.get('diagnostic')
                            if isinstance(failure, dict):
                                report['diagnostic'] = {'cause': label(failure.get('cause'), KNOWN_CAUSES),
                                    'operation': label(failure.get('operation'), KNOWN_OPERATIONS)}
                                if 'capture_step' in failure:
                                    report['diagnostic']['capture_step'] = label(failure['capture_step'],
                                        {'temporary_file', 'verify_capture', 'request_write', 'spawn',
                                         'wait', 'descendants', 'consume', 'cleanup'})
                                for key in ('exit_status', 'measured', 'limit', 'seconds', 'os_errno', 'attempts'):
                                    if number(failure.get(key)):
                                        report['diagnostic'][key] = failure[key]
                            result = record.get('scanResult')
                            if isinstance(result, dict):
                                report['scan_reason'] = label(result.get('reason'), KNOWN_CAUSES)
                                report['outcome'] = label(result.get('outcome'),
                                    {'complete_clean', 'complete_findings', 'incomplete'})
                                if type(result.get('coverage_complete')) is bool:
                                    report['coverage_complete'] = result['coverage_complete']
                                if number(result.get('elapsed_seconds')):
                                    report['scan_elapsed_seconds'] = result['elapsed_seconds']
                                counts = result.get('counts')
                                if isinstance(counts, dict):
                                    report['counts'] = {key: counts[key] for key in
                                        ('candidates', 'inspected_snapshots', 'candidate_bytes', 'capture_bytes',
                                         'temp_peak_bytes', 'processed_findings', 'retained_findings', 'omitted_findings')
                                        if type(counts.get(key)) is int and number(counts[key])}
                    except Exception:
                        # No audit/parser exception text crosses this boundary.
                        report['audit_result'] = 'unavailable_or_invalid'
                    try:
                        with self.trace.open('rb') as stream:
                            trace = stream.read(1048577)
                        if len(trace) > 1048576:
                            raise ValueError
                        rows = [json.loads(line) for line in trace.splitlines()]
                        if len(rows) > 257:
                            raise ValueError
                        events = []
                        limited = False
                        for row in rows:
                            if row in ({'trace_error': 'event_limit'}, {'trace_error': 'record_limit'}):
                                limited = True
                                continue
                            if (not isinstance(row, dict) or set(row) - {'operation', 'sequence', 'pid', 'group',
                                    'exit_status', 'launch_seconds', 'elapsed_seconds', 'stdout_bytes', 'stderr_bytes'}
                                    or row.get('operation') not in {'rev-parse', 'diff', 'ls-files', 'ls-tree', 'cat-file',
                                        'check-attr', 'show', 'init', 'hash-object', 'update-index', 'status', 'other_git'}
                                    or any(not number(value) for key, value in row.items() if key != 'operation')):
                                raise ValueError
                            events.append(row)
                        report['inner_trace_result'] = 'limited' if limited else 'read'
                        report['inner_git_count'] = len(events)
                        report['inner_git_seconds'] = round(sum(row.get('elapsed_seconds', 0) for row in events), 6)
                        if report.get('status') == 'incomplete' or report.get('required_mismatches') or report.get('audit_result') != 'read':
                            report['git_events'] = events[-4:]
                            report['git_events_omitted'] = max(0, len(events) - 4)
                    except Exception:
                        report['inner_trace_result'] = 'unavailable_or_invalid'
                    print(json.dumps(report, sort_keys=True), file=sys.stderr, flush=True)
            subprocess.Popen = Diagnosed
        """)
        source += "sys.argv = [" + repr(str(CLI)) + "] + sys.argv[1:]\n"
        source += "runpy.run_path(" + repr(str(CLI)) + ", run_name='__main__')\n"
        launcher.write_text(source)
        return launcher

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

    def test_historical_seven_helper_active_and_current_eight_helper_candidate(self):
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
                "scan_allowlist", "scan_stream", "scan_git", "scan_native_file", "scan_audit", "scan_engine")))
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

    def test_scanner_boundary_diagnostics_exclude_payload_strings(self):
        before = self.fingerprint()
        active = self.active_copy("diagnostic-canary")
        binaries = self.base / "diagnostic-bin"
        binaries.mkdir()
        git = binaries / "git"
        real_git = shutil.which("git")
        git.write_text("#!" + sys.executable + "\nimport os,sys\n"
            "if 'diff' in sys.argv[1:]:\n canary='gh'+'p_'+'FAKE'*9\n sys.stdout.write(canary)\n sys.stderr.write(canary)\n raise SystemExit(128)\n"
            "os.execv(" + repr(real_git) + ", [" + repr(real_git) + ", *sys.argv[1:]])\n")
        git.chmod(0o755)
        scanner = active / ".codex/hooks/scan-secrets.py"
        source = scanner.read_text().replace('if __name__ == "__main__":',
            "os.environ['PATH'] = " + repr(str(binaries)) + " + os.pathsep + os.environ['PATH']\n"
            'if __name__ == "__main__":')
        source = source.replace("raise SystemExit(main())",
            "code = main()\n        log = resolve_scan_log()\n        record = json.loads(log.read_text())\n"
            "        canary = 'gh' + 'p_' + 'FAKE' * 9\n"
            "        record.update(note=canary, command=canary, payload=canary)\n"
            "        record.setdefault('diagnostic', {})['payload'] = canary\n"
            "        log.write_text(json.dumps(record) + '\\n')\n        raise SystemExit(code)")
        scanner.write_text(source)
        result = self.run_cli(self.patch("value = 'repaired'\n"), "--check", active=active, diagnose=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "incomplete_scan")
        reports = [json.loads(line) for line in result.stderr.splitlines()]
        records = [row for row in reports if row.get("fixture_scanner") == "audit_boundary_v1"]
        work = [row for row in reports if row.get("fixture_work") == "audit_boundary_v1"]
        self.assertEqual(len(work), 1)
        self.assertEqual(work[0]["scanner"], 1)
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["fixture_scanner"], "audit_boundary_v1")
        self.assertEqual((record["provider"], record["bundle"], record["view"]), ("codex", "active", "pending"))
        self.assertEqual(record["cause"], "git_failed")
        self.assertEqual(record["diagnostic"], {"cause": "git_failed", "operation": "git_candidates", "exit_status": 128})
        self.assertEqual(record["audit_result"], "read")
        self.assertEqual(record["inner_trace_result"], "read")
        self.assertGreater(record["inner_git_count"], 0)
        self.assertIn("status", record["required_mismatches"])
        self.assertIn("inspection_outcome", record["required_mismatches"])
        self.assertEqual(record["git_events"][-1]["operation"], "diff")
        self.assertEqual(record["git_events"][-1]["exit_status"], 128)
        self.assertEqual(record["git_events"][-1]["stdout_bytes"], len(TOKEN))
        self.assertLessEqual(record["audit_bytes"], 1048576)
        self.assertLess(len(result.stderr), 4096)
        self.assertNotIn(TOKEN.encode(), result.stdout + result.stderr)
        self.assertNotIn(b'Traceback', result.stderr)
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
        result = self.run_cli(patch, "--check", diagnose=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(marker.exists(), "verification executed source Git filter configuration")
        self.assertEqual(self.target.read_bytes(), original)
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)
        result = self.run_cli(self.patch("value = '" + TOKEN + "'\n"), "--check", diagnose=True)
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

    def observation_wrapper(self, delay, *, first=0, after=None):
        """Delay the real metadata process at the OS process boundary."""
        wrapper = self.base / "observer-wrapper.py"
        observers = self.base / "observer-pids"
        git_started = self.base / "observer-git-started"
        child = ("import os,sys,time\ntime.sleep(" + repr(delay) + ")\n"
                 "os.execv('/bin/ps', ['/bin/ps', *sys.argv[1:]])\n")
        wrapper.write_text("import subprocess,runpy,sys\nfrom pathlib import Path\n"
            "real = subprocess.Popen\nobservations = 0\n"
            "def launched(command,*args,**kwargs):\n"
            " global observations\n"
            " if command[0] == '/bin/ps':\n"
            "  observations += 1\n"
            "  if observations <= " + repr(first) + " or (" + repr(str(after)) +
            " != 'None' and Path(" + repr(str(after)) + ").exists()):\n"
            "   command = [sys.executable, '-I', '-S', '-B', '-c', " + repr(child) + ", *command[1:]]\n"
            "  process = real(command,*args,**kwargs)\n"
            "  with Path(" + repr(str(observers)) + ").open('a') as stream: stream.write(str(process.pid)+'\\n')\n"
            "  return process\n"
            " if Path(command[0]).name == 'git': Path(" + repr(str(git_started)) + ").touch()\n"
            " return real(command,*args,**kwargs)\n"
            "subprocess.Popen = launched\n"
            "sys.argv = [" + repr(str(CLI)) + "] + sys.argv[1:]\n"
            "runpy.run_path(" + repr(str(CLI)) + ", run_name='__main__')\n")
        return wrapper, observers, git_started

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

    @unittest.skipIf(os.name == "nt", "POSIX observed descendant cancellation")
    def test_delayed_metadata_cleanup_stops_resistant_separate_session(self):
        active = self.active_copy("slow-observer-cancel")
        marker = self.base / 'slow-observer-child'
        scanner = active / '.codex/hooks/scan-secrets.py'
        child_code = ('import signal,time; signal.signal(signal.SIGINT,signal.SIG_IGN); '
                      'signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(60)')
        injection = ("import subprocess\n"
            "signal.signal(signal.SIGINT, signal.SIG_IGN)\n"
            "child = subprocess.Popen([sys.executable, '-c', " + repr(child_code) + "], start_new_session=True)\n"
            "Path(" + repr(str(marker)) + ").write_text(str(child.pid))\n"
            "time.sleep(60)\n")
        scanner.write_text(scanner.read_text().replace('if __name__ == "__main__":', injection + 'if __name__ == "__main__":'))
        wrapper, observers, _ = self.observation_wrapper(0.3, after=marker)
        before = self.fingerprint()
        patch = self.patch("value = 'repaired'\n")
        child = None
        try:
            with subprocess.Popen([sys.executable, '-I', '-S', '-B', str(wrapper),
                    '--patch', str(patch), '--path', 'fixture.py', '--active-hook-root', str(active),
                    '--check', '--json', '--no-input'], cwd=self.repo, env=self.env,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                deadline = time.monotonic() + 6
                while not marker.exists() and time.monotonic() < deadline and process.poll() is None:
                    time.sleep(0.02)
                self.assertTrue(marker.exists(), 'real scanner did not create its separate-session child')
                child = int(marker.read_text())
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
            print(json.dumps({'fixture_observer': 'resistant-child-cancellation',
                'delay_seconds': 0.3, 'cleanup_seconds': round(elapsed, 6),
                'observed_processes_stopped': len(pids) + 1}), flush=True)
        finally:
            # Cleanup follows leak assertions, so it cannot turn a leak into a pass.
            if child is not None:
                try:
                    os.kill(child, signal.SIGKILL)
                except ProcessLookupError:
                    pass

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

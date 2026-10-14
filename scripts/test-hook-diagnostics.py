#!/usr/bin/env python3
"""Standalone diagnostics public CLI cases; no authenticated host claim."""
from __future__ import annotations
import json
import os
import re
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

NOFOLLOW_SUPPORTED = hasattr(os, "O_NOFOLLOW") and os.scandir in os.supports_fd

ROOT = Path(__file__).resolve().parent.parent
CLIS = {"codex": ROOT / ".codex/hooks/hooks-diagnostics.py", "copilot": ROOT / ".copilot/hooks/scripts/hooks-diagnostics.py", "gemini": ROOT / ".gemini/hooks/scripts/hooks-diagnostics.py"}

class DiagnosticsTests(unittest.TestCase):
    def test_cli_fixed_parser_isolated_imports(self):
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            sentinel = cwd / "executed"
            hostile = "from pathlib import Path\nPath(" + repr(str(sentinel)) + ").write_text('bad')\nraise RuntimeError('hostile import')\n"
            for name in ("json.py", "sitecustomize.py", "os.py"):
                (cwd / name).write_text(hostile)
            for provider, cli in CLIS.items():
                with self.subTest(provider=provider):
                    result = subprocess.run([sys.executable, "-I", "-S", "-B", str(cli)], cwd=cwd, env={**os.environ, "PYTHONPATH": str(cwd)}, capture_output=True, timeout=5)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    report = json.loads(result.stdout)
                    self.assertEqual(report["security"]["outcome"], "not_scanned")
                    self.assertEqual(report["repository"]["pending_status"], "unknown")
                    self.assertLessEqual(len(result.stdout), 16384)
                    self.assertFalse(sentinel.exists())
                    for args in (["--help"], ["--doctor"]):
                        self.assertEqual(subprocess.run([sys.executable, "-I", "-S", "-B", str(cli), *args], cwd=cwd, capture_output=True, timeout=5).returncode, 0)
                    for args in (["."], ["--doctor", "."], ["--help", "--doctor"], ["--config", "evil"], ["--do"]):
                        rejected = subprocess.run([sys.executable, "-I", "-S", "-B", str(cli), *args], cwd=cwd, capture_output=True, timeout=5)
                        self.assertEqual(rejected.returncode, 2)
                        self.assertEqual(rejected.stdout, b"")
                        self.assertNotIn(b"evil", rejected.stderr)

    def launch(self, cli, cwd, *args):
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(cli), *args], cwd=cwd, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertLessEqual(len(result.stdout), 16384)
        return json.loads(result.stdout), result.stdout

    def copied_installation(self, directory, provider):
        home = Path(directory).resolve() / "home"
        cli = home / CLIS[provider].relative_to(ROOT)
        shutil.copytree(CLIS[provider].parent, cli.parent)
        template, destination = {"codex": (".codex/global-hooks.json", ".codex/hooks.json"), "copilot": (".copilot/hooks/hooks.json", ".copilot/hooks/hooks.json"), "gemini": (".gemini/global-settings.json", ".gemini/settings.json")}[provider]
        settings = home / destination
        settings.write_bytes((ROOT / template).read_bytes())
        settings.chmod(0o600)
        cwd = Path(directory).resolve() / "repository"
        cwd.mkdir()
        return cli, settings, cwd

    @unittest.skipUnless(NOFOLLOW_SUPPORTED, "descriptor-relative no-follow proof requires supported OS")
    def test_metadata_largest_retention_redaction_and_no_content_reads(self):
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory).resolve()
            for index in range(300):
                (cwd / ("small-%04d" % index)).write_bytes(b"a")
            (cwd / "largest.txt").write_bytes(b"x" * 2030848)
            (cwd / "body.txt").write_text("candidate body must never appear in diagnostic output")
            (cwd / ("x" * 170 + "github_pat_" + "not-a-real-credential")).write_bytes(b"x" * 300)
            (cwd / "password=fictional").write_bytes(b"x" * 400)
            (cwd / "control\nlabel\u202e.txt").write_bytes(b"x" * 500)
            (cwd / "linked").symlink_to(cwd / "largest.txt")
            os.mkfifo(cwd / "fifo")
            (cwd / ".git").mkdir()
            (cwd / ".git/index").write_bytes(b"index body must not be read")
            for provider, cli in CLIS.items():
                with self.subTest(provider=provider):
                    report, raw = self.launch(cli, cwd)
                    inventory = report["repository"]
                    self.assertTrue(inventory["inventory_complete"])
                    self.assertEqual(inventory["records"][0]["size"], 2030848)
                    self.assertEqual(inventory["index_bytes"], 27)
                    self.assertEqual(inventory["index_snapshots"], "unknown")
                    self.assertEqual(inventory["unsafe_observed"], 2)
                    self.assertLessEqual(len(inventory["records"]), 256)
                    self.assertGreater(inventory["records_omitted"], 0)
                    self.assertNotIn(b"fictional", raw)
                    self.assertNotIn(b"github_pat_", raw)
                    self.assertNotIn(b"candidate body", raw)
                    self.assertNotIn(b"index body", raw)
                    for record in inventory["records"]:
                        self.assertEqual(record["pending_status"], "unknown")
                        self.assertLessEqual(len(record.get("label", "").encode()), 160)

    @unittest.skipUnless(NOFOLLOW_SUPPORTED, "descriptor-relative no-follow proof requires supported OS")
    def test_metadata_entry_depth_directory_and_response_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory).resolve()
            for index in range(4097):
                (cwd / ("entry-%04d-" % index + "x" * 150)).touch()
            report, raw = self.launch(CLIS["codex"], cwd)
            self.assertFalse(report["repository"]["inventory_complete"])
            self.assertEqual(report["repository"]["entries_observed"], 4096)
            self.assertIn("entries_limit", report["repository"]["causes"])
            self.assertTrue(report["response_truncated"])
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory).resolve()
            nested = cwd
            for _ in range(34):
                nested /= "nested"
                nested.mkdir()
            report, _ = self.launch(CLIS["codex"], cwd)
            self.assertIn("depth_limit", report["repository"]["causes"])
            self.assertLessEqual(report["repository"]["directories_observed"], 33)
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory).resolve()
            for index in range(1030):
                (cwd / str(index)).mkdir()
            report, _ = self.launch(CLIS["codex"], cwd)
            self.assertIn("directories_limit", report["repository"]["causes"])
            self.assertEqual(report["repository"]["directories_observed"], 1024)

    @unittest.skipUnless(NOFOLLOW_SUPPORTED, "descriptor-relative no-follow proof requires supported OS")
    def test_doctor_missing_corrupt_assets_settings_and_registration_counts(self):
        for provider in CLIS:
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                cli, settings, cwd = self.copied_installation(directory, provider)
                report, _ = self.launch(cli, cwd, "--doctor")
                self.assertEqual(report["assets"]["health"], "unverified")
                self.assertEqual(report["registrations"]["health"], "observed")
                self.assertEqual(report["repository"]["health"], "not_collected")
                build = report["bootstrap"]["embedded_build"]
                (cli.parent / "helpers/audit.py").unlink()
                (cli.parent / "helpers/common.py").write_text("corrupt helper does not get imported")
                report, _ = self.launch(cli, cwd, "--doctor")
                self.assertEqual(report["bootstrap"]["embedded_build"], build)
                states = {item["asset"]: item["state"] for item in report["assets"]["records"]}
                self.assertEqual(states["helpers/audit.py"], "missing")
                self.assertEqual(states["helpers/common.py"], "drift")
                config = json.loads(settings.read_bytes())
                event = next(iter(config["hooks"]))
                group = config["hooks"][event][0]
                if provider == "copilot":
                    config["hooks"][event].extend([group.copy(), {"type": "command", "bash": "do not execute this user registration"}])
                else:
                    group["hooks"].extend([group["hooks"][0].copy(), {"type": "command", "command": "do not execute this user registration"}])
                settings.write_text(json.dumps(config))
                before = settings.read_bytes()
                report, raw = self.launch(cli, cwd, "--doctor")
                self.assertEqual(report["registrations"]["duplicates"], 1)
                self.assertEqual(report["registrations"]["unowned"], 1)
                self.assertEqual(report["registrations"]["health"], "uncertain")
                self.assertEqual(settings.read_bytes(), before)
                self.assertNotIn(b"do not execute", raw)
                for data, cause in ((b'{"hooks":{},"hooks":{}}', "duplicate_keys"), (b"{" * 1000, "malformed"), (b"x" * 262145, "bytes_limit"), (b'{"hooks":{},"includes":["arbitrary.json"]}', "config_includes")):
                    settings.write_bytes(data)
                    report, _ = self.launch(cli, cwd, "--doctor")
                    self.assertEqual(report["registrations"]["cause"], cause)
                    self.assertEqual(settings.read_bytes(), data)

    @unittest.skipUnless(NOFOLLOW_SUPPORTED, "descriptor-relative no-follow proof requires supported OS")
    def test_linked_settings_assets_and_repository_are_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            cli, settings, cwd = self.copied_installation(directory, "codex")
            target = cwd / "outside"
            target.write_bytes(b"must not be disclosed or treated as a helper")
            settings.unlink()
            settings.symlink_to(target)
            helper = cli.parent / "helpers/audit.py"
            helper.unlink()
            helper.symlink_to(target)
            (cwd / ".git").write_text("gitdir: arbitrary path must not be read")
            report, raw = self.launch(cli, cwd)
            self.assertEqual(report["registrations"]["cause"], "unsafe_type")
            states = {item["asset"]: item["state"] for item in report["assets"]["records"]}
            self.assertEqual(states["helpers/audit.py"], "unsafe_type")
            self.assertEqual(report["repository"]["repository_layout"], "linked_or_unknown")
            self.assertNotIn(b"must not be disclosed", raw)
            helpers = cli.parent / "helpers"
            shutil.rmtree(helpers)
            helpers.symlink_to(cwd, target_is_directory=True)
            report, _ = self.launch(cli, cwd, "--doctor")
            self.assertEqual(report["assets"]["health"], "degraded")

    def test_public_collector_clock_budget_and_build_identity(self):
        probe = '''import json, runpy, sys, time
module = runpy.run_path(sys.argv[1], run_name="diagnostics_library")
ticks = iter([0.0])
time.monotonic = lambda: next(ticks, 2.0)
report = module["diagnostics_collect"](sys.argv[1])
sys.stdout.buffer.write(module["diagnostics_encode"](report))
'''
        with tempfile.TemporaryDirectory() as directory:
            for provider, cli in CLIS.items():
                with self.subTest(provider=provider):
                    result = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", probe, str(cli)], cwd=directory, capture_output=True, timeout=5)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    report = json.loads(result.stdout)
                    self.assertEqual(report["registrations"]["cause"], "time_limit")
                    self.assertEqual(report["assets"]["health"], "degraded")
                    self.assertIn("time_limit", report["repository"]["causes"])
                    self.assertEqual(report["security"]["outcome"], "not_scanned")
                    normal, _ = self.launch(cli, directory, "--doctor")
                    self.assertEqual(report["bootstrap"]["embedded_build"], normal["bootstrap"]["embedded_build"])

    @unittest.skipUnless(NOFOLLOW_SUPPORTED, "descriptor-relative no-follow proof requires supported OS")
    def test_asset_hash_budget_and_unowned_modified_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            cli, settings, cwd = self.copied_installation(directory, "codex")
            config = json.loads(settings.read_bytes())
            handler = config["hooks"]["PreToolUse"][0]["hooks"][0].copy()
            handler["env"] = {"CUSTOM": "untrusted value not emitted"}
            config["hooks"]["PreToolUse"][0]["hooks"].append(handler)
            settings.write_text(json.dumps(config))
            report, raw = self.launch(cli, cwd, "--doctor")
            self.assertEqual(report["registrations"]["unowned"], 1)
            self.assertEqual(report["registrations"]["duplicates"], 1)
            self.assertNotIn(b"untrusted value", raw)
            with (cli.parent / "helpers/common.py").open("wb") as output:
                output.truncate(1048577)
            report, _ = self.launch(cli, cwd, "--doctor")
            self.assertLessEqual(report["assets"]["hash_bytes"], 1048576)
            states = {item["asset"]: item["state"] for item in report["assets"]["records"]}
            self.assertEqual(states["helpers/common.py"], "bytes_limit")

    def test_reported_policy_limits_follow_canonical_source(self):
        report, _ = self.launch(CLIS["codex"], ROOT, "--doctor")
        self.assertEqual(report["policy_limits"]["scanner"]["MAX_TOTAL_BYTES"], 8388608)
        self.assertEqual(report["policy_limits"]["guardian"]["MAX_COMMAND_SEGMENTS"], 128)
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory).resolve()
            shutil.copytree(ROOT / "hooks", fixture / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
            (fixture / ".codex/hooks").mkdir(parents=True)
            shutil.copy2(ROOT / ".codex/global-hooks.json", fixture / ".codex/global-hooks.json")
            scanner = fixture / "hooks/families/scan_secrets.py"
            source = scanner.read_text()
            self.assertIn("MAX_TOTAL_BYTES = 8388608", source)
            scanner.write_text(source.replace("MAX_TOTAL_BYTES = 8388608", "MAX_TOTAL_BYTES = 7340032", 1))
            cli = fixture / ".codex/hooks/hooks-diagnostics.py"
            renderer = '''from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from hooks.families.diagnostics import render
from hooks.manifest import targets
from hooks.providers import PROVIDERS
target = next(item for item in targets() if item.provider == "codex" and item.family == "diagnostics")
Path(sys.argv[2]).write_text(render(PROVIDERS["codex"], target))
'''
            generated = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", renderer, str(fixture), str(cli)], capture_output=True, timeout=5)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            changed, _ = self.launch(cli, fixture, "--doctor")
            self.assertEqual(changed["policy_limits"]["scanner"]["MAX_TOTAL_BYTES"], 7340032)
            self.assertNotEqual(report["bootstrap"]["embedded_build"], changed["bootstrap"]["embedded_build"])
            scanner.write_text(re.sub(r"(?m)^MAX_FILE_BYTES =[^\n]*\n", "", scanner.read_text()))
            generated = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", renderer, str(fixture), str(cli)], capture_output=True, timeout=5)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            changed, _ = self.launch(cli, fixture, "--doctor")
            self.assertEqual(changed["policy_limits"]["scanner"]["MAX_FILE_BYTES"], "not_defined")

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Exercise ablation through its public CLIs using disposable repositories."""

import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPTS = Path(__file__).resolve().parent


class AblationCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ablation-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()

    def cli(self, script, *args, **kwargs):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *map(str, args)],
            cwd=self.repo, capture_output=True, text=True, timeout=30, **kwargs)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True,
                              text=True, check=True).stdout

    def commit_fixture(self):
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Ablation Test", "-c", "user.email=test@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")

    def experiment(self, runner_code, *extra, env=None):
        task = self.base / "task.md"
        task.write_text("Exercise the agent outcome")
        runner = self.base / "runner.py"
        runner.write_text(runner_code)
        out = self.base / "results"
        result = self.cli("run_ablation.py", self.repo, "--task-file", task,
                          "--runs", "1", "--jobs", "1", "--out", out,
                          "--runner", f"exec {shlex.quote(sys.executable)} {shlex.quote(str(runner))}", *extra, env=env)
        return result, json.loads((out / "summary.json").read_text())

    def test_full_streams_survive_cleanup(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        stdout = b'x' * 5000 + b'FINAL-MARKER\n'
        stderr = b'e' * 700 + b'ERROR-END\n'
        result, summary = self.experiment(
            "import os\nfrom pathlib import Path\n"
            "Path('new.txt').write_text('done')\n"
            f"os.write(1, {stdout!r})\nos.write(2, {stderr!r})\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for run in summary["runs"]:
            self.assert_streams(run, stdout, stderr)
            self.assertTrue(run["ok"])
            self.assertEqual(run["files_changed"], ["new.txt"])
            self.assertEqual(run["cleanup_status"], "removed")
            self.assertTrue(run["shutdown_confirmed"])
            self.assertTrue(run["result_text_truncated"])
            self.assertTrue(run["stderr_tail_truncated"])
        self.assertEqual(self.git("worktree", "list", "--porcelain").count("worktree "), 1)

    def assert_streams(self, run, stdout, stderr):
        for name, expected in (("stdout", stdout), ("stderr", stderr)):
            path = Path(run[name + "_path"])
            self.assertTrue(path.is_absolute())
            self.assertTrue(path.is_relative_to((self.base / "results").resolve()))
            self.assertEqual(path.read_bytes(), expected)
            self.assertEqual(run[name + "_bytes"], len(expected))
        self.assertLessEqual(len(run["result_text"]), 4000)
        self.assertLessEqual(len(run["stderr_tail"]), 600)

    def test_stream_formats_preserve_bytes_and_optional_metadata(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        claude = {"result": "answer" * 1000, "is_error": False,
                  "total_cost_usd": 0.25, "num_turns": 3, "usage": {"output_tokens": 27}}
        cases = [
            (json.dumps(claude).encode(), "answer" * 666 + "answ", True),
            (b'{"type":"item.completed"}\n' + b' ' * 5000 +
             b'{"type":"turn.completed","final":"FINAL"}\n', None, True),
            (b'{"broken":', None, False),
            (b'{"type":"event"}\n{"partial":', None, False),
            (b'\xff\x00plain\r\n', None, False),
            (b'[]', None, False), (b'42', None, False), (b'null', None, False),
            (json.dumps({"result": 7, "is_error": "false", "usage": [],
                         "num_turns": True, "total_cost_usd": "bad"}).encode(), None, False),
            (json.dumps({"result": "optional metadata survived", "is_error": "false",
                         "usage": {"output_tokens": "bad"}, "num_turns": [],
                         "total_cost_usd": False}).encode(), "optional metadata survived", False),
            (b'', None, False),
        ]
        for index, (stdout, preview, truncated) in enumerate(cases):
            with self.subTest(index=index):
                if index in (8, 9):
                    # These must reach dictionary metadata handling, not the
                    # separate malformed-JSON fallback cases above.
                    self.assertIsInstance(json.loads(stdout), dict)
                result, summary = self.experiment(
                    "import os\nfrom pathlib import Path\n"
                    "Path('result.txt').write_text('done')\n"
                    f"os.write(1, {stdout!r})\n")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                for run in summary["runs"]:
                    self.assert_streams(run, stdout, b'')
                    self.assertTrue(run["ok"])
                    self.assertEqual(run["result_text"], preview if preview is not None else
                                     stdout.decode('utf-8', errors='replace')[:4000])
                    self.assertEqual(run["result_text_truncated"], truncated)
                    self.assertFalse(run["stderr_tail_truncated"])
                    if index == 0:
                        self.assertEqual(run["cost_usd"], 0.25)
                        self.assertEqual(run["num_turns"], 3)
                        self.assertEqual(run["output_tokens"], 27)
                    elif index in (8, 9):
                        self.assertFalse(run["agent_error"])
                        self.assertEqual(run["exit_code"], 0)
                        self.assertEqual(run["files_changed"], ["result.txt"])
                        self.assertNotIn("cost_usd", run)
                        self.assertNotIn("num_turns", run)
                        self.assertNotIn("output_tokens", run)

    def test_explicit_keep_retains_worktrees_and_streams(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        result, summary = self.experiment(
            "from pathlib import Path\nPath('result.txt').write_text('done')\n"
            "print('retained')\n", "--keep-worktrees")
        try:
            self.assertEqual(result.returncode, 0, result.stderr)
            for run in summary["runs"]:
                self.assertEqual(run["cleanup_status"], "retained")
                self.assertTrue(run["shutdown_confirmed"])
                self.assertTrue(Path(run["worktree_kept"]).exists())
                self.assert_streams(run, b'retained\n', b'')
        finally:
            for run in summary["runs"]:
                worktree = Path(run["worktree_kept"])
                self.git("worktree", "remove", "--force", str(worktree))
                worktree.parent.rmdir()

    def test_cancellation_before_queued_launch_has_empty_artifacts(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        result, summary = self.experiment(
            "import os, signal, time\n"
            "os.write(1, b'cancel-ready')\n"
            "os.kill(os.getppid(), signal.SIGTERM)\ntime.sleep(20)\n")
        self.assertEqual(result.returncode, 143, result.stdout + result.stderr)
        active, queued = summary["runs"]
        self.assert_streams(active, b'cancel-ready', b'')
        self.assert_streams(queued, b'', b'')
        self.assertEqual(queued["note"], "cancelled before launch")
        self.assertEqual(queued["cleanup_status"], "not_created")
        self.assertTrue(queued["shutdown_confirmed"])
        self.assertFalse(queued["ok"])

    def test_unconfirmed_shutdown_retains_worktree_and_evidence(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        # Inject a host signal permission failure at process startup, exercising
        # the public CLI's real failure path without changing process policy.
        hook = self.base / "sitecustomize.py"
        hook.write_text(
            "import os, sys\n"
            "if sys.argv[0].endswith('run_ablation.py'):\n"
            "    original = os.killpg\n"
            "    def denied(pgid, sig):\n"
            "        if sig: raise PermissionError('fixture signal denied')\n"
            "        return original(pgid, sig)\n"
            "    os.killpg = denied\n")
        log = self.base / "groups"
        env = dict(os.environ, PYTHONPATH=str(self.base))
        task = self.base / "task.md"
        task.write_text("Test shutdown failure")
        runner = self.base / "runner.py"
        runner.write_text(
            "import os, subprocess, sys\nfrom pathlib import Path\n"
            "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(20)'])\n"
            f"with open({str(log)!r}, 'a') as f: f.write(str(os.getpid()) + '\\n')\n"
            "Path('result.txt').write_text('done')\nos.write(1, b'retained-output')\n"
            "os.write(2, b'retained-error')\n")
        out = self.base / "results"
        summary = None
        try:
            result = self.cli("run_ablation.py", self.repo, "--task-file", task,
                              "--runs", "1", "--jobs", "1", "--out", out,
                              "--runner", f"exec {shlex.quote(sys.executable)} {shlex.quote(str(runner))}",
                              env=env)
            summary = json.loads((out / "summary.json").read_text())
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            for run in summary["runs"]:
                self.assertFalse(run["ok"])
                self.assertFalse(run["shutdown_confirmed"])
                self.assertEqual(run["cleanup_status"], "retained")
                self.assertTrue(Path(run["worktree_kept"]).exists())
                self.assertIn("cannot verify process group", run["note"])
                self.assert_streams(run, b'retained-output', b'retained-error')
        finally:
            if log.exists():
                for pgid in log.read_text().splitlines():
                    try:
                        os.killpg(int(pgid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            if summary:
                for run in summary["runs"]:
                    worktree = Path(run["worktree_kept"])
                    self.git("worktree", "remove", "--force", str(worktree))
                    worktree.parent.rmdir()

    def test_claude_error_flag_and_short_result_remain_compatible(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        stdout = b'{"result":"short answer","is_error":true,"usage":{"output_tokens":5}}\n'
        result, summary = self.experiment(
            "import os\nfrom pathlib import Path\n"
            "Path('partial.txt').write_text('partial')\n"
            f"os.write(1, {stdout!r})\n")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for run in summary["runs"]:
            self.assert_streams(run, stdout, b'')
            self.assertEqual(run["result_text"], "short answer")
            self.assertFalse(run["result_text_truncated"])
            self.assertTrue(run["agent_error"])
            self.assertFalse(run["ok"])
            self.assertEqual(run["exit_code"], 0)
            self.assertEqual(run["output_tokens"], 5)

    def test_cleanup_failure_retains_streams_and_reports_failure(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        (self.base / "sitecustomize.py").write_text(
            "import subprocess, sys\n"
            "if sys.argv[0].endswith('run_ablation.py'):\n"
            "    original = subprocess.run\n"
            "    def fail_remove(args, **kwargs):\n"
            "        if args[:3] == ['git', 'worktree', 'remove']:\n"
            "            return subprocess.CompletedProcess(args, 1, '', 'fixture removal failed')\n"
            "        return original(args, **kwargs)\n"
            "    subprocess.run = fail_remove\n")
        result, summary = self.experiment(
            "from pathlib import Path\nPath('new.txt').write_text('done')\nprint('evidence')\n",
            env=dict(os.environ, PYTHONPATH=str(self.base)))
        try:
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            for run in summary["runs"]:
                self.assertFalse(run["ok"])
                self.assertTrue(run["shutdown_confirmed"])
                self.assertEqual(run["cleanup_status"], "failed")
                self.assertTrue(Path(run["worktree_kept"]).exists())
                self.assert_streams(run, b'evidence\n', b'')
        finally:
            for run in summary["runs"]:
                worktree = Path(run["worktree_kept"])
                self.git("worktree", "remove", "--force", str(worktree))
                worktree.parent.rmdir()

    def test_failed_runner_with_json_output_is_unusable(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        result, summary = self.experiment(
            "from pathlib import Path\nPath('partial.txt').write_text('partial')\n"
            "print('{}')\nraise SystemExit(1)\n")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for run in summary["runs"]:
            self.assertEqual(run["exit_code"], 1)
            self.assertTrue(run["agent_error"])
            self.assertFalse(run["ok"])
            self.assert_streams(run, b"{}\n", b"")

    def test_invalid_task_files_report_usage_errors_without_running(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        invalid = self.base / "invalid.md"
        invalid.write_bytes(b"\xff")
        for task in (self.base / "missing.md", invalid, self.base):
            with self.subTest(task=task):
                result = self.cli("run_ablation.py", self.repo, "--task-file", task, "--dry-run")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(str(task), result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(result.stdout, "")
        self.assertEqual(self.git("worktree", "list", "--porcelain").count("worktree "), 1)

    def test_seed_patterns_and_aliases_exclude_history(self):
        rules = self.repo / ".claude" / "rules"
        rules.mkdir(parents=True)
        (rules / "active.md").write_text("current guidance")
        for directory in ("plans", "archive", "archives"):
            history = rules / directory
            history.mkdir()
            old = history / "old.md"
            old.write_text("historical guidance")
            (rules / f"alias-{directory}.md").symlink_to(old)
        self.commit_fixture()
        result = self.cli("map_layer.py", self.repo, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([item["path"] for item in json.loads(result.stdout)["artifacts"]],
                         [".claude/rules/active.md"])

    def test_stripping_is_not_counted_as_agent_work(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        result, summary = self.experiment(
            "from pathlib import Path\n"
            "if Path('AGENTS.md').exists(): Path('implementation.txt').write_text('done')\n")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        control, stripped = summary["runs"]
        self.assertTrue(control["ok"])
        self.assertEqual(control["files_changed"], ["implementation.txt"])
        self.assertFalse(stripped["ok"])
        self.assertEqual(stripped["files_changed"], [])
        self.assertEqual(stripped["removed"], ["AGENTS.md"])
        self.assertFalse((self.base / "results" / "stripped-1.diff").exists())

    def test_timeout_stops_descendants_before_removing_worktrees(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        task = self.base / "task.md"
        task.write_text("Test process cleanup")
        marker = self.base / "escaped-write"
        log = self.base / "children.jsonl"
        child = self.base / "child.py"
        child.write_text(
            "import os, signal, time\nfrom pathlib import Path\n"
            "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "time.sleep(3)\n"
            f"Path({str(marker)!r}).write_text('descendant survived timeout')\n")
        runner = self.base / "runner.py"
        runner.write_text(
            "import subprocess, sys, os, json, time\n"
            "os.write(1, b'before-timeout\\n'); os.write(2, b'timeout-error\\n')\n"
            f"p = subprocess.Popen([sys.executable, {str(child)!r}])\n"
            f"with open({str(log)!r}, 'a') as f: "
            "f.write(json.dumps({'pid': p.pid, 'cwd': os.getcwd()}) + '\\n')\n"
            "time.sleep(20)\n")

        def cleanup_children():
            if log.exists():
                for line in log.read_text().splitlines():
                    try:
                        os.kill(json.loads(line)["pid"], signal.SIGKILL)
                    except ProcessLookupError:
                        pass

        self.addCleanup(cleanup_children)
        out = self.base / "results"
        result = self.cli("run_ablation.py", self.repo, "--task-file", task,
                          "--runs", "1", "--jobs", "2", "--timeout", "1", "--out", out,
                          "--runner", f"exec {shlex.quote(sys.executable)} {shlex.quote(str(runner))}")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(marker.exists(), "descendant wrote after its runner timed out")
        children = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual(len(children), 2)
        for entry in children:
            with self.assertRaises(ProcessLookupError):
                os.kill(entry["pid"], 0)
            self.assertFalse(Path(entry["cwd"]).exists())
        summary = json.loads((out / "summary.json").read_text())
        runs = summary["runs"]
        expected_runs = {(arm, 1) for arm in ("control", "stripped")}
        self.assertEqual(len(runs), len(expected_runs), runs)
        self.assertEqual({(run["arm"], run["index"]) for run in runs}, expected_runs, runs)
        for run in runs:
            with self.subTest(arm=run["arm"], index=run["index"]):
                self.assertIn("timed out", run["note"])
            self.assert_streams(run, b'before-timeout\n', b'timeout-error\n')
            self.assertTrue(run["shutdown_confirmed"])
            self.assertEqual(run["cleanup_status"], "removed")
        self.assertEqual(self.git("worktree", "list", "--porcelain").count("worktree "), 1)

    def test_map_help_and_invalid_arguments_do_not_scan(self):
        (self.repo / "AGENTS.md").write_text("distinctive instructions")
        result = self.cli("map_layer.py", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout)
        self.assertNotIn("AI layer under", result.stdout)
        for args in [("--unknown",), (self.base / "missing",)]:
            with self.subTest(args=args):
                result = self.cli("map_layer.py", *args)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, "")
                self.assertNotIn("Traceback", result.stderr)

    def test_normal_runner_exit_also_stops_background_descendants(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        task = self.base / "task.md"
        task.write_text("Test successful work")
        log = self.base / "background-pids"
        runner = self.base / "runner.py"
        runner.write_text(
            "import subprocess, sys\nfrom pathlib import Path\n"
            "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(20)'], "
            "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
            f"with open({str(log)!r}, 'a') as f: f.write(str(p.pid) + '\\n')\n"
            "Path('result.txt').write_text('done')\n")

        def cleanup():
            if log.exists():
                for pid in log.read_text().splitlines():
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass

        self.addCleanup(cleanup)
        out = self.base / "results"
        result = self.cli("run_ablation.py", self.repo, "--task-file", task,
                          "--runs", "1", "--jobs", "2", "--out", out,
                          "--runner", f"exec {shlex.quote(sys.executable)} {shlex.quote(str(runner))}")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        for pid in log.read_text().splitlines():
            with self.assertRaises(ProcessLookupError):
                os.kill(int(pid), 0)
        summary = json.loads((out / "summary.json").read_text())
        self.assertTrue(all(r["ok"] for r in summary["runs"]))
        self.assertTrue(all(r["files_changed"] == ["result.txt"] for r in summary["runs"]))
        self.assertEqual(summary["runs"][0]["removed"], [])
        self.assertEqual(summary["runs"][1]["removed"], ["AGENTS.md"])
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_cancellation_stops_running_agents(self):
        (self.repo / "AGENTS.md").write_text("instructions")
        self.commit_fixture()
        task = self.base / "task.md"
        task.write_text("Test cancellation")
        ready = self.base / "ready"
        runner = self.base / "runner.py"
        runner.write_text("import os, time\n"
                          "os.write(1, b'before-cancel\\n'); os.write(2, b'cancel-error\\n')\n"
                          f"with open({str(ready)!r}, 'a') as f: f.write(str(os.getpid()) + '\\n')\n"
                          "time.sleep(20)\n")
        out = self.base / "results"
        process = subprocess.Popen(
            [sys.executable, str(SCRIPTS / "run_ablation.py"), str(self.repo),
             "--task-file", str(task), "--runs", "1", "--jobs", "2", "--out", str(out),
             "--runner", f"exec {shlex.quote(sys.executable)} {shlex.quote(str(runner))}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 5
            while not ready.exists() or len(ready.read_text().splitlines()) != 2:
                if time.monotonic() >= deadline:
                    self.fail("agents did not become ready")
                time.sleep(0.02)
            process.send_signal(signal.SIGTERM)
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 143, stdout + stderr)
            summary = json.loads((out / "summary.json").read_text())
            for run in summary["runs"]:
                self.assert_streams(run, b'before-cancel\n', b'cancel-error\n')
                self.assertTrue(run["shutdown_confirmed"])
                self.assertEqual(run["cleanup_status"], "removed")
            for pid in ready.read_text().splitlines():
                with self.assertRaises(ProcessLookupError):
                    os.kill(int(pid), 0)
            self.assertEqual(self.git("worktree", "list", "--porcelain").count("worktree "), 1,
                             (out / "summary.json").read_text() + stdout + stderr)
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)
            if ready.exists():
                for pid in ready.read_text().splitlines():
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_map_follows_local_context_and_imports_without_escaping_repo(self):
        files = {
            "AGENTS.md": "Read `brain/` for relevant guidance. [Guide](docs/guide.md).\n"
                         "[Outside](../outside.md) [Web](https://example.com/rules.md)",
            "CLAUDE.md": "@docs/required.md\n",
            "GEMINI.md": "[Guide](docs/guide.md)",
            "docs/guide.md": "[Cycle](../AGENTS.md) [More][rules]\n\n[rules]: more.md",
            "docs/more.md": "specific guidance",
            "docs/required.md": "mandatory imported guidance",
            "brain/codebase/build.md": "build guidance",
            "brain/principles/simplicity.md": "design guidance",
            "brain/index.md": "[Old](archive/old.md) [Plan](plans/current.md)",
            "brain/archive/old.md": "historical instructions",
            "brain/plans/current.md": "temporary work",
            "unrelated.md": "not referenced",
        }
        for name, text in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        (self.base / "outside.md").write_text("outside")
        (self.repo / "brain" / "escape.md").symlink_to(self.base / "outside.md")
        result = self.cli("map_layer.py", self.repo, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        artifacts = json.loads(result.stdout)["artifacts"]
        items = {i["path"]: i for i in artifacts}
        self.assertEqual(len(items), len(artifacts), "cycles duplicated inventory entries")
        self.assertEqual(set(items), set(files) - {
            "unrelated.md", "brain/archive/old.md", "brain/plans/current.md"})
        self.assertEqual(items["docs/required.md"]["kind"], "always-loaded")
        for name in ["brain/codebase/build.md", "brain/principles/simplicity.md", "docs/more.md"]:
            self.assertEqual(items[name]["kind"], "on-demand")
            self.assertTrue(items[name]["referenced_by"])

        self.commit_fixture()
        task = self.base / "task.md"
        task.write_text("Check dry-run inventory")
        common = (self.repo, "--task-file", task, "--dry-run")
        always = self.cli("run_ablation.py", *common)
        all_sources = self.cli("run_ablation.py", *common, "--scope", "all")
        self.assertEqual(always.returncode, 0, always.stderr)
        self.assertEqual(all_sources.returncode, 0, all_sources.stderr)
        self.assertIn("docs/required.md", always.stdout)
        self.assertNotIn("brain/codebase/build.md", always.stdout)
        self.assertIn("brain/codebase/build.md", all_sources.stdout)
        self.assertIn("brain/principles/simplicity.md", all_sources.stdout)


if __name__ == "__main__":
    unittest.main()

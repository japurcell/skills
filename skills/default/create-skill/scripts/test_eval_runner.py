#!/usr/bin/env python3
"""Public-CLI tests for eval_runner using fake provider executables."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPT = Path(__file__).with_name("eval_runner.py")
REPO = SCRIPT.parents[4]
COMMIT_SKILL = REPO / "skills/default/commit"


class EvalRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="eval-runner-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skill-src"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text("# Fixture\n")
        self.config = self.root / "config.json"
        self.config.write_text('{"model":"fake"}\n')
        self.fixture = self.root / "fixture"
        self.fixture.mkdir()
        subprocess.run(["git", "init", "--quiet"], cwd=self.fixture, check=True)
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.com",
                        "commit", "--allow-empty", "-m", "base"], cwd=self.fixture,
                       check=True, capture_output=True, timeout=5)
        self.provider = self.root / "fake-provider"
        self.provider.write_text("#!/usr/bin/env python3\nimport sys,time,os,json,subprocess\nif '--version' in sys.argv: print('fake 1.0')\nelif '--help' in sys.argv: print('--add-dir --cd --model --sandbox --json --output-last-message --session-id --resume --reasoning-effort --log-dir --output-format --prompt --allow-tool')\nelse:\n print(json.dumps({'type':'thread.started','thread_id':str(os.getpid())}), flush=True)\n prompt=sys.stdin.read()\n if 'FAIL' in prompt: sys.exit(1)\n if 'sleep' in prompt:\n  root=os.environ['EVAL_RUN_ROOT']\n  child=subprocess.Popen([sys.executable,'-c',\"import time; time.sleep(2); open('\"+root+\"/tmp/child-marker','w').write('alive')\"])\n  open(root+'/tmp/child.pid','w').write(str(child.pid))\n  time.sleep(10)\n")
        self.provider.chmod(0o755)

    def cli(self, *args, **kwargs):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True,
                              text=True, timeout=10, **kwargs)

    def test_help_and_preparation_errors_have_machine_friendly_streams(self):
        help_result = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True,
                                     text=True, timeout=5)
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("preflight", help_result.stdout)
        self.assertEqual(help_result.stderr, "")
        invalid = self.cli("init", "--run-root", self.root / "bad", "--skill", self.skill,
                           "--config", self.config, "--repo", self.root / "missing")
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("eval-runner:", invalid.stderr)
        self.assertEqual(invalid.stdout, "")

    def test_subcommand_help_and_strict_usage(self):
        for action in ("init", "adopt", "preflight", "turn"):
            result = self.cli(action, "--help")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("stdout", result.stdout)
            self.assertIn("stderr", result.stdout)
            self.assertIn("Exit", result.stdout)
        result = self.cli("preflight", "--prov", "codex", "--executable", self.provider)
        self.assertEqual(result.returncode, 2)

    def test_preflight_rejects_copilot_without_tool_permissions(self):
        self.provider.write_text("#!/usr/bin/env python3\nimport sys\nprint('fake' if '--version' in sys.argv else '--add-dir --model --session-id --resume --reasoning-effort --log-dir --output-format --prompt')\n")
        result = self.cli("preflight", "--provider", "copilot", "--executable", self.provider)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--allow-tool", result.stderr)

    def test_insecure_run_root_is_rejected_before_turn(self):
        run, manifest = self.init("insecure")
        run.chmod(0o755)
        result = self.turn(manifest, "smoke")
        self.assertEqual(result.returncode, 2)
        self.assertIn("private", result.stderr)

    def test_empty_and_unicode_prompt_files_are_handled_without_tracebacks(self):
        run, manifest = self.init("unicode-ñ")
        empty = run / "messages/empty.txt"
        empty.write_text("", encoding="utf-8")
        result = self.cli("turn", "--manifest", manifest, "--provider", "codex", "--executable", self.provider,
                          "--phase", "smoke", "--message-file", empty, "--setting", "model=fake")
        self.assertEqual(result.returncode, 2)
        self.assertIn("message file is empty", result.stderr)
        prompt = run / "messages/日本語.txt"
        prompt.write_text("Explain café briefly.", encoding="utf-8")
        result = self.cli("turn", "--manifest", manifest, "--provider", "codex", "--executable", self.provider,
                          "--phase", "smoke", "--message-file", prompt, "--setting", "model=fake")
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(manifest_data["turns"][0]["message_file"], str(prompt.resolve()))

    def test_preflight_handles_closed_stdout_pipe(self):
        process = subprocess.Popen([sys.executable, str(SCRIPT), "preflight", "--provider", "codex",
                                    "--executable", str(self.provider)], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        process.stdout.close()
        stderr = process.stderr.read()
        process.stderr.close()
        self.assertEqual(process.wait(timeout=5), 0, stderr)

    def test_adopted_commit_fixture_keeps_observers_and_grades(self):
        iteration = self.root / "iteration-1"
        evaluation = iteration / "eval-4-validation"
        evaluation.mkdir(parents=True)
        (evaluation / "eval_metadata.json").write_text('{"eval_id":4}\n')
        run = evaluation / "with_skill/run-1"
        prepare = COMMIT_SKILL / "evals/prepare_validation_workflow.py"
        subprocess.run([sys.executable, str(prepare), str(run), str(COMMIT_SKILL)],
                       check=True, capture_output=True, text=True, timeout=10)
        adopted = self.cli("adopt", "--run-root", run, "--config", self.config)
        self.assertEqual(adopted.returncode, 0, adopted.stderr)
        manifest = run / "manifest.json"
        (run / "messages/smoke.txt").write_text("smoke prompt")
        (run / "messages/contribution.txt").write_text("contribution prompt")
        (run / "messages/commit.txt").write_text("commit prompt")
        for phase in ("smoke", "contribution", "commit"):
            result = self.cli("turn", "--manifest", manifest, "--provider", "codex",
                              "--executable", self.provider, "--phase", phase,
                              "--message-file", run / "messages" / f"{phase}.txt",
                              "--setting", "model=fake")
            self.assertEqual(result.returncode, 0, result.stderr)
        validate = run / "skill/scripts/validate_message.py"
        first = subprocess.run([sys.executable, str(validate), str(run / "message.txt")],
                               capture_output=True, text=True, timeout=5)
        self.assertEqual(first.returncode, 1)
        message = run / "message.txt"
        message.write_bytes(message.read_bytes().replace("\u2028".encode(), b"\n"))
        (run / "repo/notes.txt").write_text(json.loads((run / "fixture.json").read_text())["expected_content"])
        subprocess.run(["git", "add", "notes.txt"], cwd=run / "repo", check=True)
        final = subprocess.run([sys.executable, str(validate), str(message)],
                               capture_output=True, text=True, timeout=5)
        self.assertEqual(final.returncode, 0, final.stderr)
        subprocess.run(["git", "commit", "-F", str(message)], cwd=run / "repo", check=True,
                       capture_output=True, text=True, timeout=10)
        grader = COMMIT_SKILL / "evals/grade_benchmark.py"
        result = subprocess.run([sys.executable, str(grader), str(iteration)], capture_output=True,
                                text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        grading = json.loads((run / "grading.json").read_text())
        self.assertEqual(grading["summary"]["failed"], 0, grading)

    def init(self, name):
        run = self.root / name
        result = self.cli("init", "--run-root", run, "--skill", self.skill, "--config", self.config,
                          "--repo", self.fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        return run, run / "manifest.json"

    def turn(self, manifest, phase, message="one.txt", prompt="private prompt"):
        root = manifest.parent
        msg = root / "messages" / message
        msg.write_text(prompt)
        return self.cli("turn", "--manifest", manifest, "--provider", "codex", "--executable", self.provider,
                        "--phase", phase, "--message-file", msg,
                        "--timeout", "1", "--setting", "model=fake")

    def test_private_runs_can_complete_fake_smokes_independently(self):
        runs = [self.init("run-a"), self.init("run-b")]
        for root, _ in runs:
            (root / "messages" / "prompt.txt").write_text("private prompt")
        jobs = [subprocess.Popen([sys.executable, str(SCRIPT), "turn", "--manifest", str(manifest),
                                  "--provider", "codex", "--executable", str(self.provider),
                                  "--phase", "smoke",
                                  "--message-file", str(root / "messages" / "prompt.txt"),
                                  "--setting", "model=fake"],
                                 cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                 for i, (root, manifest) in enumerate(runs)]
        for job in jobs:
            out, err = job.communicate(timeout=10)
            self.assertEqual(job.returncode, 0, err)
            self.assertIn('"smoke_ready": true', out)
        manifests = [json.loads((root / "manifest.json").read_text()) for root, _ in runs]
        self.assertNotEqual(manifests[0]["run_id"], manifests[1]["run_id"])
        self.assertTrue((runs[0][0] / "evidence/01-smoke.json").exists())
        self.assertTrue((runs[1][0] / "evidence/01-smoke.json").exists())

    def test_shared_external_message_is_rejected(self):
        run, manifest = self.init("run")
        external = self.root / "shared.txt"
        external.write_text("prompt")
        result = self.cli("turn", "--manifest", manifest, "--provider", "codex", "--executable", self.provider,
                          "--phase", "smoke", "--message-file", external, "--setting", "model=fake")
        self.assertEqual(result.returncode, 2)
        self.assertIn("inside this run", result.stderr)

    def test_session_identity_and_smoke_gate_are_enforced(self):
        run, manifest = self.init("run")
        self.assertEqual(self.turn(manifest, "smoke").returncode, 0)
        self.assertEqual(self.turn(manifest, "contribution", message="failed.txt", prompt="FAIL").returncode, 1)
        self.assertEqual(self.turn(manifest, "commit").returncode, 2)
        self.assertEqual(self.turn(manifest, "contribution").returncode, 0)
        self.assertEqual(self.turn(manifest, "commit").returncode, 0)

    def test_snapshot_remote_and_cwd_mismatches_fail_closed(self):
        run, manifest = self.init("run")
        data = json.loads(manifest.read_text())
        data["repo"] = str(self.fixture.resolve())
        manifest.write_text(json.dumps(data))
        result = self.turn(manifest, "smoke")
        self.assertEqual(result.returncode, 2)
        self.assertIn("repository path mismatch", result.stderr)
        data["repo"] = str((run / "repo").resolve())
        manifest.write_text(json.dumps(data))
        (run / "skill/SKILL.md").chmod(0o644)
        (run / "skill/SKILL.md").write_text("tampered")
        result = self.turn(manifest, "smoke")
        self.assertEqual(result.returncode, 2)
        self.assertIn("snapshot changed", result.stderr)

    def test_remote_fixture_is_rejected(self):
        remote = self.root / "remote.git"
        subprocess.run(["git", "init", "--bare", "--quiet", str(remote)], check=True)
        subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=self.fixture, check=True)
        result = self.cli("init", "--run-root", self.root / "bad-run", "--skill", self.skill,
                          "--config", self.config, "--repo", self.fixture)
        self.assertEqual(result.returncode, 2)
        self.assertIn("no remotes", result.stderr)
        self.assertTrue((self.root / "bad-run/preparation-error.json").exists())
        subprocess.run(["git", "remote", "remove", "origin"], cwd=self.fixture, check=True)

    def test_timeout_is_recorded_and_kills_process_group(self):
        run, manifest = self.init("run")
        result = self.turn(manifest, "smoke", message="sleep.txt", prompt="sleep")
        self.assertEqual(result.returncode, 124, result.stderr)
        record = json.loads(next((run / "evidence").glob("*.json")).read_text())
        self.assertTrue(record["timed_out"])
        self.assertFalse(json.loads(manifest.read_text())["smoke_receipt"])
        time.sleep(2.2)
        self.assertFalse((run / "tmp/child-marker").exists())

    def test_copilot_scoped_permissions_and_private_adoption(self):
        run = self.root / "prepared"
        prepare = COMMIT_SKILL / "evals/prepare_validation_workflow.py"
        subprocess.run([sys.executable, str(prepare), str(run), str(COMMIT_SKILL)], check=True, capture_output=True)
        self.assertEqual(run.stat().st_mode & 0o777, 0o700)
        run.chmod(0o755)
        result = self.cli("adopt", "--run-root", run, "--config", self.config)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(run.stat().st_mode & 0o777, 0o700)
        self.provider.write_text("""#!/usr/bin/env python3
import json, os, pathlib, subprocess, sys
root = os.environ.get('EVAL_RUN_ROOT', '')
if '--version' in sys.argv:
 print('fake 1.0')
elif '--help' in sys.argv:
 print('--add-dir --model --session-id --resume --reasoning-effort --log-dir --output-format --prompt --allow-tool')
else:
 def require(rule):
  if '--allow-tool=' + rule not in sys.argv: sys.exit(9)
 def run(*args):
  subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
 # Copilot recognizes these as read-only; no shell grant is required.
 for args in [('status',), ('diff',), ('log', '-1'), ('show', '--stat', 'HEAD'), ('rev-parse', '--show-toplevel'), ('branch', '--show-current'), ('config', '--get', 'user.name')]:
  run('git', *args)
 phase = sys.argv[sys.argv.index('--prompt') + 1]
 if phase == 'contribution':
  require(f'write({root}/repo/**)')
  pathlib.Path('notes.txt').write_text(json.loads(pathlib.Path(root, 'fixture.json').read_text())['expected_content'])
 if phase == 'commit':
  require(f'shell(python3 {root}/skill/scripts/validate_message.py:*)')
  validator = pathlib.Path(root, 'skill/scripts/validate_message.py')
  message = pathlib.Path(root, 'message.txt')
  assert subprocess.run(['python3', str(validator), str(message)], stdout=subprocess.DEVNULL).returncode == 1
  require(f'write({root}/message.txt)')
  message.write_text(message.read_text().replace(chr(0x2028), chr(10)))
  run('python3', str(validator), str(message))
  require('shell(git add:*)')
  run('git', 'add', 'notes.txt')
  require('shell(git commit:*)')
  run('git', 'commit', '-F', str(message))
 print('{}')
""")
        self.provider.chmod(0o755)
        for phase in ("smoke", "contribution", "commit"):
            prompt = run / "messages" / f"{phase}.txt"
            prompt.write_text(phase)
            result = self.cli("turn", "--manifest", run / "manifest.json", "--provider", "copilot", "--executable", self.provider, "--phase", phase, "--message-file", prompt, "--setting", "model=fake")
            self.assertEqual(result.returncode, 0, result.stderr)
        events = [json.loads(line) for line in (run / "events.jsonl").read_text().splitlines()]
        self.assertEqual([item["kind"] for item in events], ["validation", "validation", "commit"])
        run = run.resolve()
        command = json.loads((run / "evidence/01-smoke.json").read_text())["command"]
        grants = [arg for arg in command if arg.startswith("--allow-tool=")]
        self.assertIn(f"--allow-tool=write({run}/repo/**)", grants)
        self.assertIn("--allow-tool=shell(git add:*)", grants)
        self.assertIn("--allow-tool=shell(git commit:*)", grants)
        self.assertIn(f"--allow-tool=shell(python3 {run}/skill/scripts/validate_message.py:*)", grants)
        self.assertNotIn("--allow-all-tools", command)

    def test_copilot_write_rules_escape_glob_characters_in_root(self):
        run, manifest = self.init("run[1]*")
        prompt = run / "messages/smoke.txt"
        prompt.write_text("smoke")
        result = self.cli("turn", "--manifest", manifest, "--provider", "copilot", "--executable", self.provider, "--phase", "smoke", "--message-file", prompt, "--setting", "model=fake")
        self.assertEqual(result.returncode, 0, result.stderr)
        command = json.loads((run / "evidence/01-smoke.json").read_text())["command"]
        escaped = str(run.resolve()).replace("[", "[[]").replace("*", "[*]")
        self.assertIn(f"--allow-tool=write({escaped}/repo/**)", command)

    def test_sigterm_kills_descendants_and_keeps_evidence(self):
        run, manifest = self.init("term")
        msg = run / "messages/sleep.txt"
        msg.write_text("sleep")
        process = subprocess.Popen([sys.executable, str(SCRIPT), "turn", "--manifest", str(manifest), "--provider", "codex", "--executable", str(self.provider), "--phase", "smoke", "--message-file", str(msg), "--setting", "model=fake"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + 8
        while not (run / "tmp/child.pid").exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue((run / "tmp/child.pid").exists())
        process.send_signal(signal.SIGTERM)
        out, err = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 143, (out, err))
        self.assertTrue(list((run / "evidence").glob("*.json")))
        time.sleep(2.2)
        self.assertFalse((run / "tmp/child-marker").exists())

    def test_interrupt_kills_descendants_and_keeps_evidence(self):
        run, manifest = self.init("run")
        msg = run / "messages/sleep.txt"
        msg.write_text("sleep")
        process = subprocess.Popen([sys.executable, str(SCRIPT), "turn", "--manifest", str(manifest),
                                    "--provider", "codex", "--executable", str(self.provider),
                                    "--phase", "smoke", "--message-file", str(msg),
                                    "--setting", "model=fake"], cwd=run,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        child_pid = run / "tmp/child.pid"
        deadline = time.monotonic() + 8
        while not child_pid.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue(child_pid.exists(), "fake provider did not start")
        process.send_signal(signal.SIGINT)
        out, err = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 130, (out, err))
        self.assertTrue(list((run / "evidence").glob("*.json")))
        time.sleep(2.2)
        self.assertFalse((run / "tmp/child-marker").exists())


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Copied-installation acceptance tests for the qualification helper."""
import json
import hashlib
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'skills/default/execplan-implement-loop'


class QualificationFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='qualification fixture ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.bundle = self.base / 'installed bundle'
        shutil.copytree(BUNDLE, self.bundle)
        self.root = self.base / 'qualification root with spaces; $()'
        self.home = self.base / 'home'
        self.fake_calls = self.base / 'fake runner calls.jsonl'
        self.env = dict(os.environ, HOME=str(self.home), GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_CONFIG_NOSYSTEM='1')

    def run_helper(self, *args, timeout=15):
        return subprocess.run(
            [sys.executable, str(self.bundle / 'scripts/qualify.py'), *args],
            cwd=self.base, env=self.env, capture_output=True, text=True, timeout=timeout)

    def install_fake_runner(self, mode='blocked-first'):
        self.env['QUALIFY_FAKE_RUNNER_CALLS'] = str(self.fake_calls)
        self.env['QUALIFY_FAKE_RUNNER_MODE'] = mode
        fake = r'''#!/usr/bin/env python3
import json, os, pathlib, subprocess, sys, time

args = sys.argv[1:]
calls = pathlib.Path(os.environ['QUALIFY_FAKE_RUNNER_CALLS'])
calls.parent.mkdir(parents=True, exist_ok=True)
kind = 'doctor' if '--doctor' in args else 'run'
with calls.open('a', encoding='utf-8') as output:
    output.write(json.dumps({'kind': kind, 'argv': args}) + '\n')

def value(flag):
    try:
        return args[args.index(flag) + 1]
    except (ValueError, IndexError):
        return None

if kind == 'doctor':
    if os.environ.get('QUALIFY_FAKE_RUNNER_MODE') == 'doctor-blocked':
        result = {'schema_version': 1, 'status': 'diagnosed', 'reason_code': 'doctor_blocked',
                  'readiness': {'status': 'blocked', 'can_attempt': False, 'checks': [],
                                'provenance': {}, 'limitations': []},
                  'blockers': [{'reason_code': 'provider_missing'}]}
        print(json.dumps(result), flush=True)
        raise SystemExit(3)
    result = {'schema_version': 1, 'status': 'diagnosed', 'reason_code': 'doctor_complete',
              'readiness': {'status': 'unknown', 'can_attempt': True, 'checks': [],
                            'provenance': {'provider_version': 'fixture'},
                            'limitations': ['Permission remains unknown.']},
              'blockers': []}
    print(json.dumps(result), flush=True)
    raise SystemExit(0)

fake_mode = os.environ.get('QUALIFY_FAKE_RUNNER_MODE')
if fake_mode == 'hold':
    time.sleep(30)
if fake_mode in ('hold-descendant', 'orphan-descendant'):
    child = subprocess.Popen([sys.executable, '-c',
        'import signal,time; signal.signal(signal.SIGINT, signal.SIG_IGN); '
        'signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)'])
    pathlib.Path(os.environ['QUALIFY_FAKE_CHILD_PID']).write_text(str(child.pid), encoding='utf-8')
    if fake_mode == 'orphan-descendant':
        state = pathlib.Path(value('--run-dir'))
        state.mkdir(parents=True)
        print(json.dumps({'schema_version': 1, 'status': 'completed', 'reason_code': 'complete',
                          'run_directory': str(state)}), flush=True)
        raise SystemExit(0)
    time.sleep(30)

plan = pathlib.Path(args[0])
resume = value('--resume')
if resume:
    state = pathlib.Path(resume)
    for index in range(1, 4):
        artifact = plan.parent / f'qualification-{index}.txt'
        artifact.write_text(f'commit {index}\n', encoding='utf-8')
        subprocess.run(['git', '-C', str(plan.parent), 'add', '--', artifact.name], check=True)
        subprocess.run(['git', '-C', str(plan.parent), 'commit', '--quiet', '--no-gpg-sign',
                        '-m', f'qualification task {index}'], check=True)
    result = {'schema_version': 1, 'status': 'completed', 'reason_code': 'complete',
              'run_directory': str(state), 'task_counts': {'done': 3, 'total': 3}}
    print(json.dumps(result), flush=True)
    raise SystemExit(0)

state = pathlib.Path(value('--run-dir'))
state.mkdir(parents=True)
(state / 'journal.json').write_text(json.dumps({'status': 'blocked'}), encoding='utf-8')
result = {'schema_version': 1, 'status': 'blocked', 'reason_code': 'provider_blocked',
          'run_directory': str(state), 'task_counts': {'done': 0, 'total': 3}}
print(json.dumps(result), flush=True)
raise SystemExit(3)
'''
        (self.bundle / 'scripts/run.py').write_text(fake, encoding='utf-8')

    def setup_root(self):
        result = self.run_helper('setup', '--root', str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def fake_calls_read(self):
        if not self.fake_calls.exists():
            return []
        return [json.loads(line) for line in self.fake_calls.read_text().splitlines()]

    @staticmethod
    def terminate_helper(process):
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
        try:
            process.communicate(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=2)

    def complete_fake_run(self):
        self.install_fake_runner()
        self.setup_root()
        first = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run')
        self.assertEqual(first.returncode, 3, first.stdout + first.stderr)
        run_directory = json.loads(first.stdout)['run_directory']
        resumed = self.run_helper('run', '--root', str(self.root), '--resume', run_directory,
                                  '--authorize-paid-run')
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        return json.loads(resumed.stdout)

    def test_setup_creates_owned_disposable_repository_and_literal_next_argv(self):
        self.install_fake_runner()
        result = self.run_helper('setup', '--root', str(self.root))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.fake_calls_read(), [])
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'setup_complete')
        physical_root = str(self.root.resolve())
        self.assertEqual(report['root'], physical_root)
        self.assertEqual(report['project'], str((self.root / 'project').resolve()))
        self.assertEqual(report['next_argv'], [
            sys.executable, str(self.bundle / 'scripts/qualify.py'), 'run',
            '--root', physical_root, '--authorize-paid-run'])
        self.assertTrue((self.root / 'project/.git').is_dir())
        self.assertTrue((self.root / 'project/ExecPlan.md').is_file())
        manifest_path = self.root / 'manifest.json'
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest['root'], physical_root)
        self.assertEqual(manifest['baseline_commit'], report['baseline_commit'])
        self.assertEqual(manifest['schema_version'], 1)
        self.assertEqual(manifest['fixture']['sha256'],
                         hashlib.sha256((self.root / 'project/ExecPlan.md').read_bytes()).hexdigest())
        self.assertEqual(len(manifest['bundle']['sha256']), 64)
        self.assertIn('project/.git', manifest['owned_artifact_paths'])
        self.assertEqual(manifest_path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.root.stat().st_mode & 0o777, 0o700)
        git_config = (self.root / 'project/.git/config').read_text()
        self.assertIn('name = ExecPlan Qualification', git_config)
        self.assertIn('email = execplan-qualification@example.invalid', git_config)
        self.assertIn('gpgsign = false', git_config)
        self.assertFalse(self.home.exists())

    def test_run_is_doctor_first_and_blocked_state_requires_same_run_resume(self):
        self.install_fake_runner()
        self.setup_root()
        policy = self.base / 'reviewed policy.toml'
        policy.write_text('[[policy]]\n', encoding='utf-8')
        policy_before = policy.read_bytes()
        gemini = 'gemini ; $(touch must-not-exist)'
        model = 'model ; $(touch must-not-exist)'
        options = ['--authorize-paid-run', '--policy', str(policy), '--gemini', gemini,
                   '--model', model]

        first = self.run_helper('run', '--root', str(self.root), *options)
        self.assertEqual(first.returncode, 3, first.stdout + first.stderr)
        first_report = json.loads(first.stdout)
        self.assertEqual(first_report['status'], 'blocked')
        self.assertIn('run_directory', first_report, first.stdout + first.stderr)
        run_directory = first_report['run_directory']
        self.assertTrue(Path(run_directory).is_dir())
        calls = self.fake_calls_read()
        self.assertEqual([call['kind'] for call in calls], ['doctor', 'run'])
        self.assertIn('--doctor', calls[0]['argv'])
        self.assertEqual(calls[0]['argv'][calls[0]['argv'].index('--policy') + 1], str(policy))
        self.assertEqual(calls[0]['argv'][calls[0]['argv'].index('--gemini') + 1], gemini)
        self.assertEqual(calls[0]['argv'][calls[0]['argv'].index('--model') + 1], model)
        self.assertEqual(calls[1]['argv'][calls[1]['argv'].index('--policy') + 1], str(policy))
        self.assertEqual(calls[1]['argv'][calls[1]['argv'].index('--gemini') + 1], gemini)
        self.assertEqual(calls[1]['argv'][calls[1]['argv'].index('--model') + 1], model)
        self.assertEqual(calls[1]['argv'][calls[1]['argv'].index('--iteration-timeout') + 1], '300')
        self.assertGreater(float(calls[0]['argv'][calls[0]['argv'].index('--max-runtime') + 1]), 0)
        self.assertLessEqual(float(calls[1]['argv'][calls[1]['argv'].index('--max-runtime') + 1]), 600)

        refused = self.run_helper('run', '--root', str(self.root), *options)
        self.assertEqual(refused.returncode, 3, refused.stdout + refused.stderr)
        self.assertEqual(len(self.fake_calls_read()), 2)

        resumed = self.run_helper('run', '--root', str(self.root), '--resume', run_directory, *options)
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        resumed_report = json.loads(resumed.stdout)
        self.assertEqual(resumed_report['status'], 'completed')
        self.assertEqual(resumed_report['run_directory'], run_directory)
        calls = self.fake_calls_read()
        self.assertEqual([call['kind'] for call in calls], ['doctor', 'run', 'doctor', 'run'])
        self.assertIn('--resume', calls[2]['argv'])
        self.assertIn('--resume', calls[3]['argv'])
        self.assertEqual(calls[3]['argv'][calls[3]['argv'].index('--resume') + 1], run_directory)
        attempts = sorted((self.root / 'evidence/attempts').iterdir())
        self.assertEqual([path.name for path in attempts], ['attempt-0001', 'attempt-0002'])
        self.assertEqual(json.loads((attempts[0] / 'runner-summary.json').read_text())['status'], 'blocked')
        self.assertEqual(json.loads((attempts[1] / 'runner-summary.json').read_text())['status'], 'completed')
        self.assertFalse((self.base / 'must-not-exist').exists())
        self.assertEqual(policy.read_bytes(), policy_before)
        self.assertFalse(self.home.exists())

    def test_paid_authorization_is_required_before_any_runner_call(self):
        self.install_fake_runner()
        self.setup_root()

        result = self.run_helper('run', '--root', str(self.root))

        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.fake_calls_read(), [])
        self.assertEqual(list((self.root / 'evidence/attempts').iterdir()), [])

    def test_doctor_blocker_stops_before_runner(self):
        self.install_fake_runner(mode='doctor-blocked')
        self.setup_root()

        result = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run')

        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'blocked')
        self.assertEqual([call['kind'] for call in self.fake_calls_read()], ['doctor'])
        self.assertFalse(any((self.root / 'evidence/attempts').glob('*/runner-state')))

    def test_collect_records_baseline_and_three_commits_without_replacing_reports(self):
        self.complete_fake_run()
        before_calls = self.fake_calls_read()
        baseline = json.loads((self.root / 'manifest.json').read_text())['baseline_commit']

        first = self.run_helper('collect', '--root', str(self.root))

        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        first_report = json.loads(first.stdout)
        self.assertEqual(first_report['status'], 'collection_complete')
        self.assertEqual(first_report['baseline_commit'], baseline)
        self.assertEqual(first_report['git']['commits_since_baseline'], 3)
        self.assertEqual(first_report['git']['commit_count'], 4)
        self.assertEqual(first_report['missing_evidence'], [])
        first_path = Path(first_report['collection_path'])
        first_bytes = first_path.read_bytes()
        self.assertTrue(first_bytes)

        second = self.run_helper('collect', '--root', str(self.root))

        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        second_report = json.loads(second.stdout)
        self.assertNotEqual(second_report['collection_path'], str(first_path))
        self.assertEqual(first_path.read_bytes(), first_bytes)
        self.assertEqual(self.fake_calls_read(), before_calls)
        self.assertEqual(len(list((self.root / 'evidence/collections').glob('collection-*.json'))), 2)
        self.assertFalse(self.home.exists())

        progress = self.root / 'evidence/attempts/attempt-0002/runner-progress.jsonl'
        progress.unlink()
        third = self.run_helper('collect', '--root', str(self.root))
        self.assertEqual(third.returncode, 0, third.stdout + third.stderr)
        self.assertEqual(json.loads(third.stdout)['missing_evidence'], [
            {'attempt': 2, 'artifact': 'runner_progress',
             'path': 'evidence/attempts/attempt-0002/runner-progress.jsonl'}])

    def test_existing_and_foreign_roots_are_rejected_without_overwrite(self):
        self.root.mkdir()
        sentinel = self.root / 'sentinel.txt'
        sentinel.write_text('keep', encoding='utf-8')
        existing = self.run_helper('setup', '--root', str(self.root))
        self.assertEqual(existing.returncode, 2)
        self.assertEqual(sentinel.read_text(), 'keep')
        self.assertFalse((self.root / 'manifest.json').exists())

        sentinel.unlink()
        self.root.rmdir()
        self.setup_root()
        foreign = self.base / 'foreign copy'
        shutil.copytree(self.root, foreign)
        foreign_manifest = (foreign / 'manifest.json').read_bytes()
        collected = self.run_helper('collect', '--root', str(foreign))
        self.assertEqual(collected.returncode, 2)
        self.assertEqual((foreign / 'manifest.json').read_bytes(), foreign_manifest)
        self.assertEqual(list((foreign / 'evidence/collections').iterdir()), [])

    def test_malformed_partial_manifest_and_symlink_escape_are_rejected(self):
        partial = self.base / 'partial root'
        partial.mkdir()
        empty = self.run_helper('collect', '--root', str(partial))
        self.assertEqual(empty.returncode, 2)
        self.assertEqual(list(partial.iterdir()), [])

        self.setup_root()
        manifest_path = self.root / 'manifest.json'
        good_manifest = manifest_path.read_bytes()
        manifest_path.write_text('{broken', encoding='utf-8')
        malformed = self.run_helper('collect', '--root', str(self.root))
        self.assertEqual(malformed.returncode, 2)
        self.assertEqual(manifest_path.read_text(), '{broken')
        manifest_path.write_bytes(good_manifest)

        external = self.base / 'outside plan.md'
        external.write_text('outside', encoding='utf-8')
        plan = self.root / 'project/ExecPlan.md'
        plan.unlink()
        plan.symlink_to(external)
        escaped = self.run_helper('collect', '--root', str(self.root))
        self.assertEqual(escaped.returncode, 2)
        self.assertEqual(external.read_text(), 'outside')
        self.assertEqual(list((self.root / 'evidence/collections').iterdir()), [])

    def test_foreign_resume_directory_is_rejected_before_doctor(self):
        self.install_fake_runner()
        self.setup_root()
        foreign_run = self.base / 'foreign run'
        foreign_run.mkdir()

        result = self.run_helper('run', '--root', str(self.root), '--resume', str(foreign_run),
                                 '--authorize-paid-run')

        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.fake_calls_read(), [])
        self.assertEqual(list((self.root / 'evidence/attempts').iterdir()), [])

    def test_concurrent_run_is_rejected_and_signal_cleans_the_owned_child(self):
        self.install_fake_runner(mode='hold')
        self.setup_root()
        argv = [sys.executable, str(self.bundle / 'scripts/qualify.py'), 'run', '--root',
                str(self.root), '--authorize-paid-run']
        first = subprocess.Popen(argv, cwd=self.base, env=self.env, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.terminate_helper, first)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and len(self.fake_calls_read()) < 2:
            time.sleep(0.05)
        self.assertEqual([call['kind'] for call in self.fake_calls_read()], ['doctor', 'run'])

        second = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run')
        self.assertEqual(second.returncode, 3, second.stdout + second.stderr)
        self.assertEqual(len(self.fake_calls_read()), 2)
        first.send_signal(signal.SIGINT)
        stdout, stderr = first.communicate(timeout=10)
        self.assertEqual(first.returncode, 130, stdout + stderr)
        self.assertEqual(json.loads(stdout)['status'], 'interrupted')

    def test_cancellation_kills_a_descendant_that_ignores_graceful_signals(self):
        self.install_fake_runner(mode='hold-descendant')
        self.env['QUALIFY_FAKE_CHILD_PID'] = str(self.base / 'child pid')
        self.setup_root()
        argv = [sys.executable, str(self.bundle / 'scripts/qualify.py'), 'run', '--root',
                str(self.root), '--authorize-paid-run']
        helper = subprocess.Popen(argv, cwd=self.base, env=self.env, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.terminate_helper, helper)
        child_pid_file = Path(self.env['QUALIFY_FAKE_CHILD_PID'])
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and not child_pid_file.exists():
            time.sleep(0.05)
        self.assertTrue(child_pid_file.exists(), 'fake runner did not start its descendant')
        child_pid = int(child_pid_file.read_text())

        helper.send_signal(signal.SIGINT)
        stdout, stderr = helper.communicate(timeout=12)

        self.assertEqual(helper.returncode, 130, stdout + stderr)
        self.assertEqual(json.loads(stdout)['status'], 'interrupted')
        inspected = subprocess.run(['/bin/ps', '-p', str(child_pid), '-o', 'stat='],
                                   capture_output=True, text=True, check=False)
        self.assertIn(inspected.returncode, (0, 1), inspected.stderr)
        self.assertTrue(not inspected.stdout.strip() or inspected.stdout.strip().startswith('Z'),
                        inspected.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)

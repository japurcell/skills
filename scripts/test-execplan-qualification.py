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

    def install_composed_gemini(self, mode='blocked-first'):
        self.gemini = self.base / 'fake Gemini'
        self.gemini_calls = self.base / 'fake Gemini calls.jsonl'
        self.gemini_count = self.base / 'fake Gemini prompt count'
        self.gemini_child_pid = self.base / 'fake Gemini child pid'
        self.env.update(
            QUALIFY_FAKE_GEMINI_CALLS=str(self.gemini_calls),
            QUALIFY_FAKE_GEMINI_COUNT=str(self.gemini_count),
            QUALIFY_FAKE_GEMINI_CHILD_PID=str(self.gemini_child_pid),
            QUALIFY_FAKE_GEMINI_MODE=mode,
        )
        for skill in ('exec-plans', 'tdd'):
            path = self.home / '.agents/skills' / skill / 'SKILL.md'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('---\nname: ' + skill + '\n---\nFixture skill.\n')
        fake = '#!' + sys.executable + '\n' + r'''
import json, os, pathlib, subprocess, sys, time

args = sys.argv[1:]
calls = pathlib.Path(os.environ['QUALIFY_FAKE_GEMINI_CALLS'])

def record(value):
    with calls.open('a', encoding='utf-8') as output:
        output.write(json.dumps(value) + '\n')

if '--version' in args:
    record({'kind': 'version', 'argv': args})
    if os.environ['QUALIFY_FAKE_GEMINI_MODE'] == 'hold-version':
        pathlib.Path(os.environ['QUALIFY_FAKE_GEMINI_CHILD_PID']).write_text(json.dumps(
            {'provider': os.getpid(), 'doctor': os.getppid()}), encoding='utf-8')
        time.sleep(60)
    print('0.65.0')
    raise SystemExit(0)

prompt = args[args.index('--prompt') + 1]
packet = json.loads(prompt.split('\nRUNNER_PACKET=', 1)[1])
policy = args[args.index('--policy') + 1] if '--policy' in args else None
counter = pathlib.Path(os.environ['QUALIFY_FAKE_GEMINI_COUNT'])
count = int(counter.read_text()) + 1 if counter.exists() else 1
counter.write_text(str(count), encoding='utf-8')
record({'kind': 'prompt', 'argv': args, 'task_id': packet['task_id'], 'policy': policy})
print(json.dumps({'type': 'init', 'session_id': 'qualification-' + str(count),
                  'model': 'qualification-fixture'}), flush=True)

mode = os.environ['QUALIFY_FAKE_GEMINI_MODE']
if mode == 'diagnostic-first' and count == 1:
    sys.stderr.write('Startup failed: ' + os.environ['QUALIFY_API_KEY'] + '\n')
    raise SystemExit(1)
if mode == 'descendant':
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
    pathlib.Path(os.environ['QUALIFY_FAKE_GEMINI_CHILD_PID']).write_text(
        str(child.pid), encoding='utf-8')
    time.sleep(60)

if mode == 'blocked-first' and count == 1:
    result = {'schema_version': 1, 'iteration_id': packet['iteration_id'],
              'task_id': packet['task_id'], 'status': 'blocked',
              'summary': 'The worker is blocked pending review.', 'changed_files': [],
              'commit_message': None, 'plan_notes': [], 'reason_code': 'permission_denied'}
else:
    pathlib.Path('greeting.py').write_text(
        'def greet(name):\n    return f"Hello, {name}!"\n', encoding='utf-8')
    pathlib.Path('test_greeting.py').write_text(
        'import unittest\nfrom greeting import greet\n\n'
        'class GreetingTests(unittest.TestCase):\n'
        '    def test_named_person(self):\n'
        '        self.assertEqual(greet("Ada"), "Hello, Ada!")\n\n'
        '    def test_empty_name(self):\n'
        '        self.assertEqual(greet(""), "Hello, !")\n', encoding='utf-8')
    result = {'schema_version': 1, 'iteration_id': packet['iteration_id'],
              'task_id': packet['task_id'], 'status': 'ready_for_verification',
              'summary': 'Create and verify the greeting module.',
              'changed_files': ['greeting.py', 'test_greeting.py'],
              'commit_message': ('feat: create greeting module\n\nSummary:\n'
                                 '- Create greeting behavior\n\nRationale:\n'
                                 '- Complete the qualification plan\n\nTests:\n'
                                 '- Run greeting acceptance'),
              'plan_notes': [], 'reason_code': 'ready'}

print(json.dumps({'type': 'message', 'role': 'assistant',
                  'content': json.dumps(result), 'delta': True}), flush=True)
print(json.dumps({'type': 'result', 'status': 'success',
                  'stats': {'total_tokens': 12}}), flush=True)
'''
        self.gemini.write_text(fake, encoding='utf-8')
        self.gemini.chmod(0o700)

    def gemini_calls_read(self):
        if not self.gemini_calls.exists():
            return []
        return [json.loads(line) for line in self.gemini_calls.read_text().splitlines()]

    def setup_root(self):
        result = self.run_helper('setup', '--root', str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def skill_source(self, name):
        source = self.base / 'selected skills' / name
        source.mkdir(parents=True)
        (source / 'SKILL.md').write_text('---\nname: ' + name + '\n---\nSelected fixture skill.\n')
        (source / 'references').mkdir()
        (source / 'references/example.txt').write_bytes(b'copied exactly\x00\xff\n')
        (source / 'check.py').write_text('#!/usr/bin/env python3\nprint("selected helper")\n')
        (source / 'check.py').chmod(0o700)
        return source

    def test_setup_provisions_selected_skills_before_immutable_baseline(self):
        self.install_composed_gemini()
        shutil.rmtree(self.home)
        sources = {name: self.skill_source(name) for name in ('exec-plans', 'tdd')}
        before = {name: {path.relative_to(source).as_posix(): path.read_bytes()
                         for path in source.rglob('*') if path.is_file()}
                  for name, source in sources.items()}
        result = self.run_helper('setup', '--root', str(self.root),
                                 '--exec-plans-source', str(sources['exec-plans']),
                                 '--tdd-source', str(sources['tdd']))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        project = self.root / 'project'
        manifest = json.loads((self.root / 'manifest.json').read_text())
        self.assertEqual(manifest['schema_version'], 2)
        self.assertEqual(manifest['setup_state']['status'], 'complete')
        self.assertEqual({item['name'] for item in manifest['skills']}, set(sources))
        for name, source in sources.items():
            for relative, payload in before[name].items():
                owned = 'project/.gemini/skills/' + name + '/' + relative
                self.assertEqual((self.root / owned).read_bytes(), payload)
                self.assertIn(owned, manifest['owned_artifact_paths'])
                committed = subprocess.run(['git', '-C', str(project), 'show',
                                            report['baseline_commit'] + ':' + owned[8:]],
                                           env=self.env, capture_output=True, check=True)
                self.assertEqual(committed.stdout, payload)
                self.assertEqual((source / relative).read_bytes(), payload)
                if relative == 'check.py':
                    self.assertEqual((self.root / owned).stat().st_mode & 0o777, 0o700)
        self.assertEqual(subprocess.run(['git', '-C', str(project), 'status', '--porcelain'],
                                       env=self.env, capture_output=True, check=True).stdout, b'')
        self.assertEqual(self.gemini_calls_read(), [])
        self.assertFalse(self.home.exists())
        doctor = subprocess.run([sys.executable, str(self.bundle / 'scripts/run.py'),
                                 str(project / 'ExecPlan.md'), '--doctor', '--gemini', str(self.gemini)],
                                env=self.env, cwd=self.base, capture_output=True, text=True, timeout=10)
        self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)
        skills = json.loads(doctor.stdout)['readiness']['provenance']['skills']
        self.assertEqual({item['name'] for item in skills}, set(sources))
        self.assertTrue(all('/project/.gemini/skills/' in item['path'] for item in skills))

    def test_post_setup_skill_changes_remain_rejected(self):
        self.install_fake_runner()
        self.setup_root()
        project = self.root / 'project'
        shutil.copytree(self.skill_source('exec-plans'), project / '.gemini/skills/exec-plans')
        dirty = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run')
        self.assertEqual(json.loads(dirty.stdout)['reason_code'], 'project_changed_without_resume')
        subprocess.run(['git', '-C', str(project), 'add', '--', '.gemini'], env=self.env, check=True)
        subprocess.run(['git', '-C', str(project), 'commit', '--quiet', '-m', 'manual skills'],
                       env=self.env, check=True)
        changed = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run')
        self.assertEqual(json.loads(changed.stdout)['reason_code'], 'project_changed_without_resume')
        self.assertEqual(self.fake_calls_read(), [])

    def test_setup_accepts_either_explicit_skill_independently(self):
        for name in ('exec-plans', 'tdd'):
            with self.subTest(skill=name):
                self.root = self.base / ('root for ' + name)
                source = self.skill_source(name)
                result = self.run_helper('setup', '--root', str(self.root), '--' + name + '-source', str(source))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                skills = self.root / 'project/.gemini/skills'
                self.assertEqual({path.name for path in skills.iterdir()}, {name})
                collected = self.run_helper('collect', '--root', str(self.root))
                self.assertEqual(collected.returncode, 0, collected.stdout + collected.stderr)
                self.assertTrue(json.loads(collected.stdout)['git']['clean'])

    def test_setup_rejects_unsafe_skill_sources_before_creating_root(self):
        cases = ('missing', 'relative', 'missing-entrypoint', 'malformed', 'wrong-name',
                 'symlink-root', 'symlink-parent', 'symlink-child', 'fifo', 'oversized',
                 'too-many-files', 'too-many-bytes', 'too-deep', 'recursive-root')
        for case in cases:
            with self.subTest(case=case):
                source = self.base / case / 'tdd'
                source.mkdir(parents=True)
                (source / 'SKILL.md').write_text('---\nname: tdd\n---\nFixture.\n')
                self.root = self.base / ('invalid root ' + case)
                selected = source
                if case == 'missing':
                    selected = source / 'absent'
                elif case == 'relative':
                    selected = Path('relative-source')
                elif case == 'missing-entrypoint':
                    (source / 'SKILL.md').unlink()
                elif case == 'malformed':
                    (source / 'SKILL.md').write_bytes(b'\xff')
                elif case == 'wrong-name':
                    (source / 'SKILL.md').write_text('---\nname: other\n---\n')
                elif case == 'symlink-root':
                    selected = source.parent / 'linked-source'
                    selected.symlink_to(source, target_is_directory=True)
                elif case == 'symlink-parent':
                    link = self.base / 'linked-parent'
                    link.symlink_to(source.parent, target_is_directory=True)
                    selected = link / source.name
                elif case == 'symlink-child':
                    (source / 'linked').symlink_to(source / 'SKILL.md')
                elif case == 'fifo':
                    os.mkfifo(source / 'fifo')
                elif case == 'oversized':
                    with (source / 'large').open('wb') as stream:
                        stream.truncate(1024 * 1024 + 1)
                elif case == 'too-many-files':
                    for index in range(256):
                        (source / f'file-{index}').write_bytes(b'')
                elif case == 'too-many-bytes':
                    for index in range(16):
                        with (source / f'file-{index}').open('wb') as stream:
                            stream.truncate(1024 * 1024)
                elif case == 'too-deep':
                    nested = source
                    for _ in range(17):
                        nested = nested / 'deep'
                        nested.mkdir()
                elif case == 'recursive-root':
                    self.root = source / 'qualification-root'
                result = self.run_helper('setup', '--root', str(self.root), '--tdd-source', str(selected))
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)['reason_code'], 'invalid_skill_source')
                self.assertFalse(self.root.exists())
        self.assertFalse(self.home.exists())

    def test_setup_copy_failure_retains_typed_partial_root_without_publishing_skills(self):
        source = self.skill_source('tdd')
        before = (source / 'references/example.txt').read_bytes()
        injection = self.base / 'copy failure injection'
        injection.mkdir()
        (injection / 'sitecustomize.py').write_text('''import os
original = os.open
def open_file(path, *args, **kwargs):
    if '.skills-staging' in str(path) and str(path).endswith('example.txt'):
        raise OSError('injected staging copy failure')
    return original(path, *args, **kwargs)
os.open = open_file
''')
        self.env['PYTHONPATH'] = str(injection)
        result = self.run_helper('setup', '--root', str(self.root), '--tdd-source', str(source))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['reason_code'], 'qualification_setup_failed')
        manifest = json.loads((self.root / 'manifest.json').read_text())
        self.assertEqual(manifest['setup_state']['status'], 'failed')
        self.assertIsNone(manifest['baseline_commit'])
        self.assertFalse((self.root / 'project/.gemini/skills').exists())
        self.assertFalse((self.root / 'project/.git').exists())
        self.assertTrue((self.root / 'project/.gemini/.skills-staging').is_dir())
        self.assertEqual((source / 'references/example.txt').read_bytes(), before)
        self.env.pop('PYTHONPATH')
        collected = self.run_helper('collect', '--root', str(self.root))
        self.assertEqual(json.loads(collected.stdout)['reason_code'], 'qualification_setup_incomplete')
        retried = self.run_helper('setup', '--root', str(self.root), '--tdd-source', str(source))
        self.assertEqual(retried.returncode, 2, retried.stdout + retried.stderr)
        self.assertEqual((source / 'references/example.txt').read_bytes(), before)

    def test_schema_one_roots_still_collect_and_resume_without_manifest_migration(self):
        self.install_fake_runner()
        self.setup_root()
        path = self.root / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['schema_version'] = 1
        del manifest['skills'], manifest['setup_state']
        path.write_text(json.dumps(manifest))
        first = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run')
        self.assertEqual(first.returncode, 3, first.stdout + first.stderr)
        run_directory = json.loads(first.stdout)['run_directory']
        resumed = self.run_helper('run', '--root', str(self.root), '--resume', run_directory,
                                  '--authorize-paid-run')
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        collected = self.run_helper('collect', '--root', str(self.root))
        self.assertEqual(collected.returncode, 0, collected.stdout + collected.stderr)
        current = json.loads(path.read_text())
        self.assertEqual(current['schema_version'], 1)
        self.assertNotIn('skills', current)
        self.assertNotIn('setup_state', current)

    def test_provisioned_skills_keep_foreign_evidence_and_skill_paths_rejected(self):
        self.install_fake_runner()
        source = self.skill_source('tdd')
        setup = self.run_helper('setup', '--root', str(self.root), '--tdd-source', str(source))
        self.assertEqual(setup.returncode, 0, setup.stdout + setup.stderr)
        manifest_path = self.root / 'manifest.json'
        before = manifest_path.read_bytes()
        for relative in ('evidence/diagnostics', 'project/.gemini/skills/unselected'):
            with self.subTest(path=relative):
                foreign = self.root / relative
                foreign.mkdir()
                sentinel = foreign / 'operator-note.txt'
                sentinel.write_text('preserve operator data\n')
                for command in ('collect', 'run'):
                    args = [command, '--root', str(self.root)]
                    if command == 'run':
                        args.append('--authorize-paid-run')
                    rejected = self.run_helper(*args)
                    self.assertEqual(rejected.returncode, 2, rejected.stdout + rejected.stderr)
                self.assertEqual(manifest_path.read_bytes(), before)
                self.assertEqual(sentinel.read_text(), 'preserve operator data\n')
                sentinel.unlink()
                foreign.rmdir()
        self.assertEqual(self.fake_calls_read(), [])

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
        self.assertEqual(manifest['schema_version'], 2)
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
        self.assertTrue(first_report['git']['baseline_reachable'])
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

    def test_collect_only_counts_commits_when_baseline_is_an_ancestor(self):
        setup = self.setup_root()
        first = self.run_helper('collect', '--root', str(self.root))
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertTrue(json.loads(first.stdout)['git']['baseline_reachable'])
        self.assertEqual(json.loads(first.stdout)['git']['commits_since_baseline'], 0)
        project = self.root / 'project'
        for args in (('checkout', '--orphan', 'unrelated'),
                     ('commit', '--quiet', '--no-gpg-sign', '-m', 'unrelated history')):
            subprocess.run(['git', '-C', str(project), *args], env=self.env,
                           capture_output=True, text=True, check=True)
        actual = subprocess.run(['git', '-C', str(project), 'merge-base', '--is-ancestor',
                                 setup['baseline_commit'], 'HEAD'], env=self.env,
                                capture_output=True, text=True)
        self.assertEqual(actual.returncode, 1, actual.stderr)

        collected = self.run_helper('collect', '--root', str(self.root))

        self.assertEqual(collected.returncode, 0, collected.stdout + collected.stderr)
        report = json.loads(collected.stdout)
        self.assertFalse(report['git']['baseline_reachable'])
        self.assertIsNone(report['git']['commits_since_baseline'])
        self.assertEqual(report['git']['commit_count'], 1)

    def test_collect_preserves_index_bytes_and_metadata_without_losing_status(self):
        self.setup_root()
        project = self.root / 'project'
        index = project / '.git/index'
        before_bytes = index.read_bytes()
        before = index.stat()
        plan = project / 'ExecPlan.md'
        plan_stat = plan.stat()
        os.utime(plan, ns=(plan_stat.st_atime_ns, plan_stat.st_mtime_ns + 1_000_000_000))

        for dirty in (False, True, True):
            with self.subTest(dirty=dirty):
                if dirty:
                    (project / 'untracked.txt').write_text('observable status\n')
                result = self.run_helper('collect', '--root', str(self.root))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report['git']['clean'], not dirty)
                self.assertEqual(report['git']['dirty_entry_count'], int(dirty))
                self.assertEqual(index.read_bytes(), before_bytes)
                after = index.stat()
                self.assertEqual((after.st_mtime_ns, after.st_ctime_ns, after.st_ino, after.st_mode),
                                 (before.st_mtime_ns, before.st_ctime_ns, before.st_ino, before.st_mode))

    def test_collect_uses_real_saved_provider_version_and_preserves_unknown_metadata(self):
        self.install_composed_gemini()
        self.setup_root()
        attempt = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run',
                                  '--gemini', str(self.gemini))
        self.assertEqual(attempt.returncode, 3, attempt.stdout + attempt.stderr)
        doctor_path = self.root / 'evidence/attempts/attempt-0001/doctor.json'
        doctor = json.loads(doctor_path.read_text())
        self.assertEqual(doctor['readiness']['provenance']['provider']['version'], '0.65.0')

        collected = self.run_helper('collect', '--root', str(self.root))

        self.assertEqual(collected.returncode, 0, collected.stdout + collected.stderr)
        saved = json.loads(collected.stdout)['reports'][0]['doctor']
        self.assertEqual(saved['versions']['provider'], '0.65.0')
        for provenance in ({}, None, {'provider_version': 'historical-wrong-shape'},
                           {'provider': None}, {'provider': 'malformed'}, {'provider': {}},
                           {'provider': {'version': 65}}, {'provider': {'version': ''}}):
            with self.subTest(provenance=provenance):
                doctor['readiness']['provenance'] = provenance
                doctor_path.write_text(json.dumps(doctor))
                result = self.run_helper('collect', '--root', str(self.root))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                saved = json.loads(result.stdout)['reports'][0]['doctor']
                self.assertIsNone((saved['versions'] or {}).get('provider'))

    def test_collection_preserves_original_sanitized_provider_diagnostic_across_resume(self):
        self.install_composed_gemini('diagnostic-first')
        self.env['QUALIFY_API_KEY'] = 'fixture-collection-private-value'
        self.setup_root()
        first = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run',
                                '--gemini', str(self.gemini), timeout=30)
        self.assertEqual(first.returncode, 3, first.stdout + first.stderr)
        run = Path(json.loads(first.stdout)['run_directory'])
        runner = json.loads((self.root / 'evidence/attempts/attempt-0001/runner-summary.json').read_text())
        diagnostic = runner['iterations'][0]['provider_diagnostic']
        reference = diagnostic['artifact_ref']
        artifact = run / reference
        retained = artifact.read_bytes()
        self.assertNotIn(self.env['QUALIFY_API_KEY'].encode(), retained)
        collected = self.run_helper('collect', '--root', str(self.root))
        self.assertEqual(collected.returncode, 0, collected.stdout + collected.stderr)
        collection = json.loads(collected.stdout)
        self.assertEqual(collection['reports'][0]['runner']['provider_diagnostics'], [diagnostic])
        self.assertEqual(collection['reports'][0]['runner']['run_directory'], str(run))
        self.assertEqual(list(self.root.rglob(reference)), [artifact])
        resumed = self.run_helper('run', '--root', str(self.root), '--resume', str(run),
                                  '--authorize-paid-run', '--gemini', str(self.gemini), timeout=30)
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        after = self.run_helper('collect', '--root', str(self.root))
        self.assertEqual(after.returncode, 0, after.stdout + after.stderr)
        self.assertEqual([item['runner']['provider_diagnostics'] for item in json.loads(after.stdout)['reports']],
                         [[diagnostic], [diagnostic]])
        self.assertEqual(artifact.read_bytes(), retained)
        saved = json.loads((run / 'state.json').read_text())
        self.assertEqual(saved['iterations'][0]['provider_diagnostic'], diagnostic)

    def test_collection_rejects_diagnostic_escape_symlink_and_malformed_metadata(self):
        self.install_composed_gemini('diagnostic-first')
        self.env['QUALIFY_API_KEY'] = 'fixture-collection-private-value'
        self.setup_root()
        first = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run',
                                '--gemini', str(self.gemini), timeout=30)
        self.assertEqual(first.returncode, 3, first.stdout + first.stderr)
        summary = self.root / 'evidence/attempts/attempt-0001/runner-summary.json'
        original = json.loads(summary.read_text())
        run = Path(original['run_directory'])
        outside = self.base / 'outside-diagnostic'
        outside.write_bytes(b'outside')
        for changes in ({'artifact_ref': '../doctor.json'}, {'artifact_ref': str(outside)},
                        {'artifact_ref': 'linked-diagnostic'}, {'captured_bytes': True},
                        {'retained_bytes': 65537}, {'encoding': 'utf-8'}, {'artifact_ref': None}):
            with self.subTest(changes=changes):
                modified = json.loads(json.dumps(original))
                modified['iterations'][0]['provider_diagnostic'].update(changes)
                summary.write_text(json.dumps(modified))
                if changes.get('artifact_ref') == 'linked-diagnostic':
                    (run / 'linked-diagnostic').symlink_to(outside)
                collected = self.run_helper('collect', '--root', str(self.root))
                if (run / 'linked-diagnostic').is_symlink():
                    (run / 'linked-diagnostic').unlink()
                self.assertEqual(collected.returncode, 2, collected.stdout + collected.stderr)
                self.assertEqual(list((self.root / 'evidence/collections').iterdir()), [])
                self.assertEqual(outside.read_bytes(), b'outside')
        summary.write_text(json.dumps(original))
        collected = self.run_helper('collect', '--root', str(self.root))
        self.assertEqual(collected.returncode, 0, collected.stdout + collected.stderr)

    def test_real_helper_runner_composition_preserves_reviewed_resume_and_evidence(self):
        self.install_composed_gemini()
        setup = self.setup_root()
        policy = self.base / 'reviewed policy.toml'
        updated_policy = self.base / 'reviewed policy update.toml'
        policy.write_text("[[rule]]\ntoolName = 'write_file'\ndecision = 'allow'\n",
                          encoding='utf-8')
        updated_policy.write_text("# explicitly reviewed update\n[[rule]]\n"
                                  "toolName = 'write_file'\ndecision = 'allow'\n",
                                  encoding='utf-8')
        policy_bytes = policy.read_bytes()
        updated_policy_bytes = updated_policy.read_bytes()

        def selected(path):
            return {'path': str(path.resolve()),
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

        blocked = self.run_helper(
            'run', '--root', str(self.root), '--authorize-paid-run',
            '--policy', str(policy), '--gemini', str(self.gemini), timeout=30)

        self.assertEqual(blocked.returncode, 3, blocked.stdout + blocked.stderr)
        blocked_report = json.loads(blocked.stdout)
        self.assertEqual(blocked_report['status'], 'blocked')
        self.assertEqual(blocked_report.get('reason_code'), 'worker_blocked',
                         blocked.stdout + blocked.stderr)
        run_directory = blocked_report['run_directory']
        first_attempt = self.root / 'evidence/attempts/attempt-0001'
        first_doctor = json.loads((first_attempt / 'doctor.json').read_text())
        self.assertEqual(first_doctor['readiness']['status'], 'unknown')
        self.assertTrue(first_doctor['readiness']['can_attempt'])
        self.assertEqual(first_doctor['readiness']['provenance']['selected_policy'], selected(policy))
        checks = {check['id']: check for check in first_doctor['readiness']['checks']}
        for name in ('authentication', 'trust', 'effective_permission'):
            self.assertEqual(checks[name]['status'], 'unknown')
        blocked_runner = json.loads((first_attempt / 'runner-summary.json').read_text())
        self.assertEqual(blocked_runner['status'], 'blocked')
        self.assertEqual([item['status'] for item in blocked_runner['iterations']], ['blocked'])
        self.assertEqual(blocked_runner['iterations'][0]['result']['status'], 'blocked')
        self.assertEqual(blocked_runner['commits'], [])
        self.assertTrue(all(value == 0 for value in blocked_runner['failure_counts'].values()))
        self.assertEqual(blocked_runner['readiness']['provenance']['selected_policy'], selected(policy))

        refused = self.run_helper(
            'run', '--root', str(self.root), '--authorize-paid-run',
            '--policy', str(updated_policy), '--gemini', str(self.gemini))
        self.assertEqual(refused.returncode, 3, refused.stdout + refused.stderr)
        self.assertEqual(json.loads(refused.stdout)['reason_code'], 'explicit_resume_required')
        self.assertFalse((self.root / 'evidence/attempts/attempt-0002').exists())
        self.assertEqual(len([call for call in self.gemini_calls_read() if call['kind'] == 'prompt']), 1)

        resumed = self.run_helper(
            'run', '--root', str(self.root), '--resume', run_directory,
            '--authorize-paid-run', '--policy', str(updated_policy),
            '--gemini', str(self.gemini), timeout=30)

        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        resumed_report = json.loads(resumed.stdout)
        self.assertEqual(resumed_report['status'], 'completed')
        self.assertEqual(resumed_report['runner_status'], 'completed')
        self.assertEqual(resumed_report['run_directory'], run_directory)
        second_attempt = self.root / 'evidence/attempts/attempt-0002'
        second_doctor = json.loads((second_attempt / 'doctor.json').read_text())
        self.assertEqual(second_doctor['readiness']['status'], 'unknown')
        self.assertEqual(second_doctor['readiness']['provenance']['selected_policy'],
                         selected(updated_policy))
        resumed_runner = json.loads((second_attempt / 'runner-summary.json').read_text())
        self.assertEqual(resumed_runner['status'], 'completed')
        self.assertEqual(resumed_runner['task_counts'], {'total': 3, 'done': 3})
        self.assertEqual([item['status'] for item in resumed_runner['iterations']],
                         ['blocked', 'ready_for_verification'])
        self.assertEqual(resumed_runner['iterations'][0]['status'], 'blocked')
        self.assertEqual(len(resumed_runner['commits']), 3)
        self.assertEqual(resumed_runner['readiness']['provenance']['selected_policy'], selected(updated_policy))
        self.assertEqual(resumed_runner['invocations'][0]['readiness']['provenance']['selected_policy'],
                         selected(policy))
        self.assertEqual(resumed_runner['invocations'][1]['readiness']['provenance']['selected_policy'],
                         selected(updated_policy))
        self.assertEqual(resumed_runner['invocations'][-1]['policy_selection'], {
            'explicit': True, 'previous': selected(policy), 'selected': selected(updated_policy)})
        plan_text = (self.root / 'project/ExecPlan.md').read_text()
        self.assertIn('Status: done\nAcceptance: met', plan_text)
        for task in ('T1', 'T2', 'T3'):
            self.assertIn(f'- [x] [M1] {task}:', plan_text)

        prompt_calls = [call for call in self.gemini_calls_read() if call['kind'] == 'prompt']
        self.assertEqual([call['task_id'] for call in prompt_calls], ['T1', 'T1'])
        self.assertEqual([call['policy'] for call in prompt_calls],
                         [str(policy.resolve()), str(updated_policy.resolve())])
        for call, path in zip(prompt_calls, (policy, updated_policy)):
            self.assertEqual(call['argv'][call['argv'].index('--policy') + 1], str(path.resolve()))
        self.assertEqual(policy.read_bytes(), policy_bytes)
        self.assertEqual(updated_policy.read_bytes(), updated_policy_bytes)
        journal = json.loads((Path(run_directory) / 'state.json').read_text())
        self.assertEqual(journal['invocations'][0]['readiness']['provenance']['selected_policy'],
                         selected(policy))
        self.assertEqual(journal['invocations'][1]['readiness']['provenance']['selected_policy'],
                         selected(updated_policy))

        collected = self.run_helper('collect', '--root', str(self.root))

        self.assertEqual(collected.returncode, 0, collected.stdout + collected.stderr)
        collection = json.loads(collected.stdout)
        self.assertEqual(collection['status'], 'collection_complete')
        self.assertEqual(collection['baseline_commit'], setup['baseline_commit'])
        self.assertEqual(collection['missing_evidence'], [])
        self.assertTrue(collection['git']['clean'])
        self.assertEqual(collection['git']['commit_count'], 4)
        self.assertEqual(collection['git']['commits_since_baseline'], 3)
        self.assertEqual([report['runner']['status'] for report in collection['reports']],
                         ['blocked', 'completed'])
        self.assertEqual(collection['reports'][0]['doctor']['readiness']['status'], 'unknown')
        self.assertEqual(len(collection['git']['commit_log']), 4)
        self.assertFalse((self.home / '.gemini').exists())

    def test_nested_real_runner_cancellation_cleans_provider_descendant(self):
        self.install_composed_gemini(mode='descendant')
        self.setup_root()
        policy = self.base / 'reviewed cancellation policy.toml'
        policy.write_text("[[rule]]\ntoolName = 'write_file'\ndecision = 'allow'\n",
                          encoding='utf-8')
        argv = [sys.executable, str(self.bundle / 'scripts/qualify.py'), 'run', '--root',
                str(self.root), '--authorize-paid-run', '--policy', str(policy),
                '--gemini', str(self.gemini)]
        helper = subprocess.Popen(argv, cwd=self.base, env=self.env, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.terminate_helper, helper)
        deadline = time.monotonic() + 12
        while (time.monotonic() < deadline and helper.poll() is None
               and not self.gemini_child_pid.exists()):
            time.sleep(0.05)
        self.assertTrue(self.gemini_child_pid.exists(), 'real runner did not start fake Gemini descendant')
        child_pid = int(self.gemini_child_pid.read_text())

        helper.send_signal(signal.SIGINT)
        stdout, stderr = helper.communicate(timeout=18)

        self.assertEqual(helper.returncode, 130, stdout + stderr)
        self.assertEqual(json.loads(stdout)['status'], 'interrupted')
        summary_path = self.root / 'evidence/attempts/attempt-0001/runner-summary.json'
        self.assertTrue(summary_path.is_file())
        self.assertEqual(json.loads(summary_path.read_text())['status'], 'interrupted')
        inspected = subprocess.run(['/bin/ps', '-p', str(child_pid), '-o', 'stat='],
                                   capture_output=True, text=True, check=False)
        self.assertIn(inspected.returncode, (0, 1), inspected.stderr)
        self.assertTrue(not inspected.stdout.strip() or inspected.stdout.strip().startswith('Z'),
                        inspected.stdout)

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

    def test_failed_process_inspection_still_kills_descendants_and_blocks_retry(self):
        self.install_fake_runner(mode='hold-descendant')
        pidfile = self.base / 'inspection descendant pid'
        self.env['QUALIFY_FAKE_CHILD_PID'] = str(pidfile)
        injection = self.base / 'inspection failure'
        injection.mkdir()
        (injection / 'sitecustomize.py').write_text('''import os, pathlib, subprocess
original = subprocess.run
def run(argv, *args, **kwargs):
    if argv and argv[0] == '/bin/ps' and pathlib.Path(os.environ['QUALIFY_FAKE_CHILD_PID']).exists():
        raise PermissionError('injected process inventory failure')
    return original(argv, *args, **kwargs)
subprocess.run = run
''')
        self.env['PYTHONPATH'] = str(injection)
        self.setup_root()
        helper = subprocess.Popen(
            [sys.executable, str(self.bundle / 'scripts/qualify.py'), 'run',
             '--root', str(self.root), '--authorize-paid-run'],
            cwd=self.base, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.terminate_helper, helper)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and not pidfile.exists():
            time.sleep(0.05)
        self.assertTrue(pidfile.exists(), 'fake runner did not start its descendant')
        child_pid = int(pidfile.read_text())
        # Capture the process group while the owned fixture is alive. Cleanup only
        # follows the assertions, so it cannot make a leaked descendant pass.
        group = os.getpgid(child_pid)
        self.addCleanup(self.kill_fixture_group, group)
        helper.send_signal(signal.SIGINT)
        stdout, stderr = helper.communicate(timeout=12)

        self.assertEqual(helper.returncode, 3, stdout + stderr)
        self.assertEqual(json.loads(stdout)['reason_code'], 'cleanup_unconfirmed')
        inspected = subprocess.run(['/bin/ps', '-p', str(child_pid), '-o', 'stat='],
                                   capture_output=True, text=True, check=False)
        self.assertIn(inspected.returncode, (0, 1), inspected.stderr)
        self.assertTrue(not inspected.stdout.strip() or inspected.stdout.strip().startswith('Z'),
                        inspected.stdout)
        before = self.fake_calls_read()
        retry = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run')
        self.assertEqual(retry.returncode, 3, retry.stdout + retry.stderr)
        self.assertEqual(json.loads(retry.stdout)['reason_code'], 'cleanup_unconfirmed')
        self.assertEqual(self.fake_calls_read(), before)

    def test_helper_killed_during_doctor_preserves_barrier_before_runner_state_exists(self):
        self.install_composed_gemini(mode='hold-version')
        self.setup_root()
        argv = [sys.executable, str(self.bundle / 'scripts/qualify.py'), 'run',
                '--root', str(self.root), '--authorize-paid-run', '--gemini', str(self.gemini)]
        helper = subprocess.Popen(argv, cwd=self.base, env=self.env, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.terminate_helper, helper)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and not self.gemini_child_pid.exists():
            time.sleep(0.05)
        self.assertTrue(self.gemini_child_pid.exists(), 'doctor did not start fake version check')
        pids = json.loads(self.gemini_child_pid.read_text())
        groups = {os.getpgid(pid) for pid in pids.values()}
        for group in groups:
            self.addCleanup(self.kill_fixture_group, group)
        helper.kill()
        helper.communicate(timeout=3)
        for pid in pids.values():
            os.kill(pid, 0)
        manifest_path = self.root / 'manifest.json'
        before = manifest_path.read_bytes()
        record = json.loads(before)['attempts'][0]
        self.assertEqual(record['status'], 'starting')
        self.assertFalse(record['runner_started'])
        self.assertFalse((self.root / record['run_directory']).exists())

        retry = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run',
                                '--gemini', str(self.gemini))

        self.assertEqual(retry.returncode, 3, retry.stdout + retry.stderr)
        self.assertEqual(json.loads(retry.stdout)['reason_code'], 'qualification_attempt_incomplete')
        self.assertEqual(manifest_path.read_bytes(), before)
        self.assertEqual(len(self.gemini_calls_read()), 1)

    def register_version_provider_cleanup(self, pid, group):
        argv = ['/bin/ps', '-p', str(pid), '-o', 'pid=,pgid=,lstart=,command=']
        identity = subprocess.run(argv, capture_output=True, text=True, check=False)
        self.assertEqual(identity.returncode, 0, identity.stderr)
        self.assertIn(str(self.gemini), identity.stdout)

        def cleanup():
            current = subprocess.run(argv, capture_output=True, text=True, check=False)
            # Never signal a vanished/reused PID or group using stale evidence.
            if current.returncode == 0 and current.stdout == identity.stdout:
                try:
                    if os.getpgid(pid) == group:
                        self.kill_fixture_group(group)
                except ProcessLookupError:
                    pass
        self.addCleanup(cleanup)

    def assert_version_provider_alive(self, pid, group):
        inspected = subprocess.run(['/bin/ps', '-p', str(pid), '-o', 'stat='],
                                   capture_output=True, text=True, check=False)
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        self.assertTrue(inspected.stdout.strip())
        self.assertFalse(inspected.stdout.strip().startswith('Z'), inspected.stdout)
        self.assertEqual(os.getpgid(pid), group)

    def doctor_child_survival_barrier(self, *, resume=False, signal_denied=False):
        self.install_composed_gemini()
        self.setup_root()
        options = ['--authorize-paid-run', '--gemini', str(self.gemini)]
        resume_options = []
        if resume:
            first = self.run_helper('run', '--root', str(self.root), *options)
            self.assertEqual(first.returncode, 3, first.stdout + first.stderr)
            resume_options = ['--resume', json.loads(first.stdout)['run_directory']]
        self.env['QUALIFY_FAKE_GEMINI_MODE'] = 'hold-version'
        if signal_denied:
            injection = self.base / 'doctor signal denial'
            injection.mkdir()
            # Inject only the OS signal failure for this fixture-owned provider
            # in the actual doctor process. Supervision/reporting remain real.
            (injection / 'sitecustomize.py').write_text('''import errno, json, os, pathlib, sys
original = os.killpg
def killpg(group, signum):
    marker = pathlib.Path(os.environ['QUALIFY_FAKE_GEMINI_CHILD_PID'])
    if '--doctor' in sys.argv and signum and marker.exists():
        if group == json.loads(marker.read_text())['provider']:
            raise PermissionError(errno.EPERM, 'fixture-owned provider signal denial')
    return original(group, signum)
os.killpg = killpg
''')
            self.env['PYTHONPATH'] = str(injection)
        helper = subprocess.Popen(
            [sys.executable, str(self.bundle / 'scripts/qualify.py'), 'run',
             '--root', str(self.root), *resume_options, *options], cwd=self.base,
            env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.terminate_helper, helper)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and not self.gemini_child_pid.exists():
            time.sleep(0.05)
        self.assertTrue(self.gemini_child_pid.exists(), 'doctor did not start fake version check')
        pids = json.loads(self.gemini_child_pid.read_text())
        provider_group = os.getpgid(pids['provider'])
        self.assertNotEqual(provider_group, os.getpgid(pids['doctor']))
        # Record ownership while the child is live; only fixture-owned groups
        # are cleaned, after the survival and no-replacement assertions.
        self.register_version_provider_cleanup(pids['provider'], provider_group)
        if not signal_denied:
            os.kill(pids['doctor'], signal.SIGKILL)
        stdout, stderr = helper.communicate(timeout=20 if signal_denied else 8)
        if signal_denied:
            doctor = json.loads((self.root / 'evidence/attempts/attempt-0001/doctor.json').read_text())
            self.assertEqual(doctor['status'], 'diagnosed')
            self.assertEqual(doctor['reason_code'], 'cleanup_unconfirmed')
            self.assertFalse(doctor['readiness']['can_attempt'])
            self.assertEqual(json.loads(stdout)['doctor_exit_code'], 3)
        self.assert_version_provider_alive(pids['provider'], provider_group)

        self.assertEqual(helper.returncode, 3, stdout + stderr)
        self.assertEqual(json.loads(stdout)['reason_code'], 'cleanup_unconfirmed')
        manifest_path = self.root / 'manifest.json'
        before = manifest_path.read_bytes()
        attempt = json.loads(before)['attempts'][-1]
        self.assertEqual(attempt['reason_code'], 'cleanup_unconfirmed')
        self.assertFalse(attempt['runner_started'])
        calls = self.gemini_calls_read()
        for retry_options in ([], resume_options):
            retry = self.run_helper('run', '--root', str(self.root), *retry_options, *options)
            self.assertEqual(retry.returncode, 3, retry.stdout + retry.stderr)
            self.assertEqual(json.loads(retry.stdout)['reason_code'], 'cleanup_unconfirmed')
            self.assertEqual(manifest_path.read_bytes(), before)
            self.assertEqual(self.gemini_calls_read(), calls)
            self.assert_version_provider_alive(pids['provider'], provider_group)

    def test_doctor_killed_with_separate_provider_preserves_initial_barrier(self):
        self.doctor_child_survival_barrier()

    def test_doctor_killed_with_separate_provider_preserves_resume_barrier(self):
        self.doctor_child_survival_barrier(resume=True)

    def test_typed_doctor_cleanup_uncertainty_preserves_provider_barrier(self):
        self.doctor_child_survival_barrier(signal_denied=True)

    def test_lost_terminal_doctor_reports_preserve_barrier_after_normal_exit(self):
        self.install_composed_gemini(mode='hold-version')
        for report_bytes in (None, b'{partial', b'{"schema_version": 1}'):
            with self.subTest(report=report_bytes):
                self.root = self.base / f'lost report root {len(list(self.base.glob("lost report root *")))}'
                self.gemini_child_pid.unlink(missing_ok=True)
                self.setup_root()
                options = ['--authorize-paid-run', '--gemini', str(self.gemini)]
                helper = subprocess.Popen(
                    [sys.executable, str(self.bundle / 'scripts/qualify.py'), 'run',
                     '--root', str(self.root), *options], cwd=self.base, env=self.env,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                self.addCleanup(self.terminate_helper, helper)
                deadline = time.monotonic() + 8
                while time.monotonic() < deadline and not self.gemini_child_pid.exists():
                    time.sleep(0.05)
                self.assertTrue(self.gemini_child_pid.exists())
                pids = json.loads(self.gemini_child_pid.read_text())
                group = os.getpgid(pids['provider'])
                self.register_version_provider_cleanup(pids['provider'], group)
                # The real doctor writes its terminal report to its original
                # open inode; the public evidence path has been lost/corrupted.
                report_path = self.root / 'evidence/attempts/attempt-0001/doctor.json'
                report_path.unlink()
                if report_bytes is not None:
                    report_path.write_bytes(report_bytes)
                os.killpg(group, signal.SIGTERM)
                stdout, stderr = helper.communicate(timeout=8)
                self.assertEqual(helper.returncode, 3, stdout + stderr)
                result = json.loads(stdout)
                self.assertEqual(result['doctor_exit_code'], 3)
                self.assertEqual(result['reason_code'], 'cleanup_unconfirmed')
                before = (self.root / 'manifest.json').read_bytes()
                calls = self.gemini_calls_read()
                retry = self.run_helper('run', '--root', str(self.root), *options)
                self.assertEqual(retry.returncode, 3, retry.stdout + retry.stderr)
                self.assertEqual(json.loads(retry.stdout)['reason_code'], 'cleanup_unconfirmed')
                self.assertEqual((self.root / 'manifest.json').read_bytes(), before)
                self.assertEqual(self.gemini_calls_read(), calls)

    def test_real_doctor_invalid_input_and_cancellation_keep_confirmed_outcomes(self):
        self.install_composed_gemini(mode='hold-version')
        self.setup_root()
        options = ['--authorize-paid-run', '--gemini', str(self.gemini)]
        invalid = self.run_helper('run', '--root', str(self.root), *options,
                                  '--policy', str(self.base / 'missing policy.toml'))
        self.assertEqual(invalid.returncode, 2, invalid.stdout + invalid.stderr)
        self.assertNotEqual(json.loads(invalid.stdout)['reason_code'], 'cleanup_unconfirmed')
        # An ordinary invalid diagnosis is terminal and can be retried after
        # correcting the supplied input. Cancellation then lets doctor clean
        # its independently grouped provider and publish its terminal report.
        self.gemini_child_pid.unlink(missing_ok=True)
        helper = subprocess.Popen(
            [sys.executable, str(self.bundle / 'scripts/qualify.py'), 'run',
             '--root', str(self.root), *options], cwd=self.base, env=self.env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.terminate_helper, helper)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and not self.gemini_child_pid.exists():
            time.sleep(0.05)
        self.assertTrue(self.gemini_child_pid.exists())
        pids = json.loads(self.gemini_child_pid.read_text())
        group = os.getpgid(pids['provider'])
        self.register_version_provider_cleanup(pids['provider'], group)
        helper.send_signal(signal.SIGINT)
        stdout, stderr = helper.communicate(timeout=8)
        self.assertEqual(helper.returncode, 130, stdout + stderr)
        self.assertEqual(json.loads(stdout)['reason_code'], 'interrupted_during_doctor')
        inspected = subprocess.run(['/bin/ps', '-p', str(pids['provider']), '-o', 'stat='],
                                   capture_output=True, text=True, check=False)
        self.assertIn(inspected.returncode, (0, 1), inspected.stderr)
        self.assertTrue(not inspected.stdout.strip() or inspected.stdout.strip().startswith('Z'),
                        inspected.stdout)

    def test_helper_killed_before_doctor_spawn_preserves_write_ahead_barrier(self):
        self.install_fake_runner()
        self.setup_root()
        injection = self.base / 'pre-spawn crash'
        injection.mkdir()
        (injection / 'sitecustomize.py').write_text('''import os, signal, subprocess
original = subprocess.Popen
def popen(argv, *args, **kwargs):
    if '--doctor' in argv:
        os.kill(os.getpid(), signal.SIGKILL)
    return original(argv, *args, **kwargs)
subprocess.Popen = popen
''')
        self.env['PYTHONPATH'] = str(injection)
        first = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run')
        self.assertEqual(first.returncode, -signal.SIGKILL)
        self.env.pop('PYTHONPATH')
        before = (self.root / 'manifest.json').read_bytes()

        retry = self.run_helper('run', '--root', str(self.root), '--authorize-paid-run')

        self.assertEqual(retry.returncode, 3, retry.stdout + retry.stderr)
        self.assertEqual(json.loads(retry.stdout)['reason_code'], 'qualification_attempt_incomplete')
        self.assertEqual((self.root / 'manifest.json').read_bytes(), before)
        self.assertEqual(self.fake_calls_read(), [])

    @staticmethod
    def kill_fixture_group(group):
        try:
            os.killpg(group, signal.SIGKILL)
        except ProcessLookupError:
            pass


if __name__ == '__main__':
    unittest.main(verbosity=2)

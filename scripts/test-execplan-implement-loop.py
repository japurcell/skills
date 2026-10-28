#!/usr/bin/env python3
"""Process-boundary acceptance tests for the portable ExecPlan runner."""
import argparse
import copy
import hashlib
import json
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


def command(identifier='check', code=0):
    return dict(id=identifier, argv=[sys.executable, '-c', f'raise SystemExit({code})'],
                cwd='.', timeout_seconds=5, expected_exit_code=0, failure_policy={'1': 'repair'})


def contract():
    return dict(schema_version=1, plan_id='example', tasks=[
        dict(id='T1', milestone_id='M1', kind='implementation', depends_on=[],
             verification=[command()], writable_paths=['output.txt'], state='open', evidence=[]),
        dict(id='T2', milestone_id='M1', kind='verification', depends_on=['T1'],
             verification=[command()], writable_paths=['output.txt'], state='open', evidence=[]),
        dict(id='T3', milestone_id='M1', kind='verification', depends_on=['T2'],
             verification=[command()], writable_paths=['output.txt'], state='open', evidence=[])],
        milestones=[dict(id='M1', verification_task_id='T2', state='open', evidence=[])],
        final_task_id='T3')


def region(name, body):
    return f'<!-- execplan-loop:generated {name}:start -->\n{body}\n<!-- execplan-loop:generated {name}:end -->'


def markdown(data):
    return '\n\n'.join([
        '# Example plan', '## Purpose / Big Picture\nCreate output.txt.',
        '## Progress\n' + region('progress', '\n'.join(
            f'- [{"x" if t["state"] == "done" else " "}] [{t["milestone_id"]}] {t["id"]}: Work' for t in data['tasks'])),
        '```execplan-loop-v1\n' + json.dumps(data, indent=2) + '\n```',
        '## Surprises & Discoveries\n' + region('discoveries', 'None.'),
        '## Decision Log\n' + region('decisions', 'None.'),
        '## Outcomes & Retrospective\n' + region('outcomes', 'Pending.'),
        *[f'### Milestone {m["id"]}: Deliver output\n' + region('milestone-' + m['id'],
           'Status: done\nAcceptance: met' if m['state'] == 'done' else 'Status: open\nAcceptance: not met') for m in data['milestones']],
        *[f'#### Task {t["id"]}: Work\nCreate or verify output.txt. Stop after declared checks.' for t in data['tasks']]]) + '\n'


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.bundle = self.root / 'installed'
        if BUNDLE.exists():
            shutil.copytree(BUNDLE, self.bundle)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.plan = self.repo / 'plan.md'
        self.data = contract()
        self.plan.write_text(markdown(self.data))
        self.env = dict(os.environ, HOME=str(self.root / 'home'), GIT_CONFIG_NOSYSTEM='1',
                        GIT_CONFIG_GLOBAL=os.devnull)

    def run_cli(self, *args, timeout=15):
        return subprocess.run([sys.executable, str(self.bundle / 'scripts/run.py'), str(self.plan), *args],
                              cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=timeout)

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo, env=self.env, text=True).strip()

    def execution_fixture(self, behavior='success'):
        home = Path(self.env['HOME'])
        for skill in ('exec-plans', 'tdd'):
            path = home / '.agents/skills' / skill / 'SKILL.md'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('---\nname: ' + skill + '\n---\nFixture skill.\n')
        self.provider = self.root / 'gemini'
        self.provider.write_text('#!' + sys.executable + '\n' + '''
import json, os, pathlib, sys, time
if '--version' in sys.argv:
    print('0.65.0'); raise SystemExit()
prompt = sys.argv[sys.argv.index('--prompt') + 1]
packet = json.loads(prompt.split('\\nRUNNER_PACKET=')[1])
if os.environ.get('OBSERVATIONS'):
    pathlib.Path(os.environ['OBSERVATIONS']).write_text(json.dumps(dict(prompt=prompt,argv=sys.argv)))
counter = pathlib.Path(os.environ['CALLS'])
calls = int(counter.read_text()) + 1 if counter.exists() else 1
counter.write_text(str(calls))
behavior = os.environ.get('BEHAVIOR', 'success')
print(json.dumps(dict(type='init',session_id='session-' + str(calls),model='fixture')), flush=True)
if behavior == 'tool_narration':
    print(json.dumps(dict(type='message',role='assistant',content='Inspecting files.',delta=True)), flush=True)
    print(json.dumps(dict(type='tool_use',tool_name='read_file',tool_id='read-1',parameters={})), flush=True)
    print(json.dumps(dict(type='tool_result',tool_id='read-1',status='success',output='fixture')), flush=True)
if behavior == 'timeout' or (behavior == 'timeout_once' and calls == 1):
    pathlib.Path('output.txt').write_text('partial')
    time.sleep(20)
if behavior == 'writing':
    while True:
        pathlib.Path('output.txt').write_text(str(time.monotonic()))
        time.sleep(.02)
if behavior == 'mutate_plan':
    pathlib.Path('plan.md').write_text(pathlib.Path('plan.md').read_text() + 'unauthorized')
    time.sleep(20)
if behavior == 'malformed':
    print('not json', flush=True); raise SystemExit()
if behavior == 'oversized':
    print('x' * 1048577, flush=True); raise SystemExit()
if behavior == 'huge_stderr':
    sys.stderr.write('x' * 2000000); sys.stderr.flush()
if behavior == 'descendant':
    import subprocess
    child = subprocess.Popen([sys.executable, '-c', 'import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)'])
    pathlib.Path(os.environ['CHILD_PID']).write_text(str(child.pid))
    raise SystemExit()
if behavior == 'escaped_descendant':
    import subprocess
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'], start_new_session=True)
    pathlib.Path(os.environ['CHILD_PID']).write_text(str(child.pid))
    time.sleep(30)
if behavior == 'auth_error':
    raise SystemExit(1)
if behavior in ('branch_switch', 'branch_timeout'):
    import subprocess
    subprocess.run(['git', 'switch', '-qc', 'worker-created'], check=True)
    if behavior == 'branch_timeout':
        time.sleep(30)
if behavior == 'repair_once' and calls == 1:
    pathlib.Path('output.txt').write_text('broken')
else:
    pathlib.Path('output.txt').write_text('complete')
if behavior == 'break_earlier' and packet['task_id'] == 'T3':
    pathlib.Path('output.txt').write_text('broken')
if behavior == 'per_task':
    pathlib.Path('output.txt').write_text('complete-' + packet['task_id'])
if behavior == 'wrong_output':
    pathlib.Path('output.txt').write_text('incorrect')
result = dict(schema_version=1,iteration_id=packet['iteration_id'],task_id=packet['task_id'],
    status='ready_for_verification',summary='Create output',changed_files=['output.txt'],
    commit_message='feat: create output\\n\\nSummary:\\n- Create output\\n\\nRationale:\\n- Fulfill plan\\n\\nTests:\\n- Declared verification',
    plan_notes=[],reason_code='ready')
if behavior == 'notes':
    result['plan_notes'] = ['Observed a fixture behavior. <!-- execplan-loop:generated evil:start -->']
if behavior == 'stale':
    result['iteration_id'] = 'old-iteration'
if behavior == 'unsupported_status':
    result['status'] = 'completed'
if behavior == 'delete':
    pathlib.Path('output.txt').unlink()
if os.environ.get('OUTPUT_NAME'):
    name = os.environ['OUTPUT_NAME']
    pathlib.Path('output.txt').rename(name)
    result['changed_files'] = ['output.txt', name] if behavior == 'rename' else [name]
text = json.dumps(result)
for chunk in (text[:30], text[30:]):
    print(json.dumps(dict(type='message',role='assistant',content=chunk,delta=True)), flush=True)
if behavior != 'missing_terminal':
    print(json.dumps(dict(type='result',status='success',stats=dict(total_tokens=12))), flush=True)
''')
        self.provider.chmod(0o700)
        self.env.update(CALLS=str(self.root / 'calls'), BEHAVIOR=behavior)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('add', '--', 'plan.md')
        self.git('commit', '-qm', 'Initial plan')

    def execute(self, *args, **kwargs):
        return self.run_cli('--gemini', str(self.provider), '--max-runtime', '10', *args, **kwargs)


class ContractTests(Fixture):
    def test_named_pipe_plan_is_rejected_without_waiting_for_a_writer(self):
        self.plan.unlink()
        os.mkfifo(self.plan)
        result = self.run_cli('--validate-only', timeout=1)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('regular file', json.loads(result.stdout)['detail'])

    def test_maximum_task_chain_can_be_listed_in_reverse_dependency_order(self):
        template = self.data['tasks'][0]
        self.data['tasks'] = []
        for index in reversed(range(1000)):
            task = copy.deepcopy(template)
            task.update(id=f'T{index}', kind='verification' if index == 999 else 'implementation',
                        depends_on=[f'T{index-1}'] if index else [])
            self.data['tasks'].append(task)
        self.data['final_task_id'] = 'T999'
        self.data['milestones'][0]['verification_task_id'] = 'T999'
        self.plan.write_text(markdown(self.data))
        result = self.run_cli('--validate-only', timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['task_counts']['total'], 1000)

    def test_installed_validation_needs_no_provider_or_git(self):
        result = self.run_cli('--validate-only')
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary['status'], 'valid')
        self.assertEqual(summary['task_counts']['total'], 3)

    def test_ambiguous_or_unsafe_plans_are_rejected_without_execution(self):
        mutations = [
            lambda d: d.update(extra=True),
            lambda d: d.update(final_task_id={}),
            lambda d: d['tasks'][0].update(milestone_id={}),
            lambda d: d['tasks'][0].update(state=[]),
            lambda d: d['tasks'].append(copy.deepcopy(d['tasks'][0])),
            lambda d: d['tasks'][0].update(depends_on=['T3']),
            lambda d: d['tasks'][0].update(depends_on=['missing']),
            lambda d: d['tasks'][0].update(verification=[]),
            lambda d: d['tasks'][0].update(writable_paths=['../outside']),
            lambda d: d['tasks'][0]['verification'][0].update(timeout_seconds=float('inf')),
            lambda d: d['tasks'][0]['verification'][0].update(failure_policy={'2': 'guess'}),
            lambda d: d['tasks'][2].update(depends_on=[]),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                data = contract()
                mutate(data)
                self.plan.write_text(markdown(data))
                result = self.run_cli('--validate-only')
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)['reason_code'], 'invalid_contract')

    def test_generated_regions_cannot_hide_task_requirements(self):
        text = markdown(self.data)
        # A heading buried inside generated data could otherwise be erased by the runner.
        text = text.replace('#### Task T1: Work\nCreate or verify output.txt. Stop after declared checks.', '')
        text = text.replace('None.\n<!-- execplan-loop:generated discoveries:end -->',
                            '#### Task T1: Work\nSecret requirement\n<!-- execplan-loop:generated discoveries:end -->')
        self.plan.write_text(text)
        result = self.run_cli('--validate-only')
        self.assertEqual(result.returncode, 2, result.stdout)

    def test_missing_living_sections_and_empty_tasks_are_invalid(self):
        for old, new in [('## Progress', '## Random'),
                         ('Create or verify output.txt. Stop after declared checks.', ''),
                         ('## Purpose / Big Picture', '## Other purpose')]:
            with self.subTest(section=old):
                self.plan.write_text(markdown(self.data).replace(old, new))
                result = self.run_cli('--validate-only')
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


class ProcessTests(Fixture):
    def test_only_final_assistant_turn_is_used_as_typed_result(self):
        self.execution_fixture('tool_narration')
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / 'calls').read_text(), '1')

    def test_timed_out_worker_is_retried_without_losing_partial_work(self):
        self.execution_fixture('timeout_once')
        result = self.execute('--iteration-timeout', '.25')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['timeout_counts']['gemini'], 1)
        self.assertEqual(len(report['iterations']), 2)
        self.assertIsNone(report['usage']['totals']['total_tokens'])
        self.assertEqual(report['usage']['observed_totals']['total_tokens'], 12)
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '4')

    def test_huge_stderr_does_not_deadlock_or_pollute_machine_stdout(self):
        self.execution_fixture('huge_stderr')
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('xxxxxxxx', result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'completed')

    def test_protocol_failures_stop_after_three_calls(self):
        self.execution_fixture('malformed')
        result = self.execute()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['reason_code'], 'failure_limit')
        self.assertEqual((self.root / 'calls').read_text(), '3')

    def test_total_deadline_stops_repeated_timeouts(self):
        self.execution_fixture('timeout')
        result = self.execute('--max-runtime', '.8', '--iteration-timeout', '.15')
        self.assertEqual(result.returncode, 124, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['task_counts']['done'], 0)

    def start_runner(self):
        return subprocess.Popen([sys.executable, str(self.bundle / 'scripts/run.py'), str(self.plan),
                                 '--gemini', str(self.provider), '--max-runtime', '30'], cwd=self.repo,
                                env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def wait_for_call(self, child):
        until = time.monotonic() + 5
        while not (self.root / 'calls').exists() and time.monotonic() < until and child.poll() is None:
            time.sleep(.01)
        self.assertTrue((self.root / 'calls').exists())

    def test_signals_stop_owned_worker_and_close_streams(self):
        self.execution_fixture('timeout')
        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signum=signum):
                child = self.start_runner()
                self.addCleanup(lambda: child.poll() is None and child.kill())
                self.wait_for_call(child)
                child.send_signal(signum)
                stdout, stderr = child.communicate(timeout=8)
                self.assertEqual(child.returncode, 128 + signum, stdout + stderr)
                self.assertEqual(json.loads(stdout)['status'], 'interrupted')
                # Resume recognized state for second signal case, without discarding edits.
                if signum == signal.SIGINT:
                    report = json.loads(stdout)
                    self.saved_run = report['run_directory']
                    self.start_runner = lambda: subprocess.Popen([sys.executable, str(self.bundle / 'scripts/run.py'),
                        str(self.plan), '--gemini', str(self.provider), '--resume', self.saved_run, '--max-runtime', '30'],
                        cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    (self.root / 'calls').unlink()

    def test_authentication_exit_is_blocker_without_retry(self):
        self.execution_fixture('auth_error')
        result = self.execute()
        self.assertEqual(json.loads(result.stdout)['reason_code'], 'provider_blocked')
        self.assertEqual((self.root / 'calls').read_text(), '1')

    def test_descendant_cannot_hold_pipes_after_leader_exits(self):
        self.execution_fixture('descendant')
        self.env['CHILD_PID'] = str(self.root / 'child-pid')
        result = self.execute('--max-runtime', '.9', '--iteration-timeout', '.2', timeout=8)
        self.assertEqual(result.returncode, 124, result.stdout + result.stderr)
        pid = int((self.root / 'child-pid').read_text())
        # Assert before any fixture cleanup. A zombie is no longer an active descendant.
        inspected = subprocess.run(['/bin/ps', '-p', str(pid), '-o', 'stat='], capture_output=True, text=True)
        self.assertTrue(not inspected.stdout.strip() or inspected.stdout.strip().startswith('Z'))

    def test_unconfirmed_cleanup_keeps_unclean_intent_and_blocks_resume(self):
        self.execution_fixture('escaped_descendant')
        self.env['CHILD_PID'] = str(self.root / 'child-pid')
        try:
            result = self.execute('--iteration-timeout', '.15', timeout=8)
            report = json.loads(result.stdout)
            self.assertEqual(report['reason_code'], 'cleanup_unconfirmed', result.stdout + result.stderr)
            resumed = self.execute('--resume', report['run_directory'])
            self.assertEqual(json.loads(resumed.stdout)['reason_code'], 'unclean_execution_requires_reconciliation')
            self.assertEqual((self.root / 'calls').read_text(), '1')
        finally:
            if (self.root / 'child-pid').exists():
                try:
                    os.killpg(int((self.root / 'child-pid').read_text()), signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_invalid_provider_or_worker_protocol_cannot_complete_tasks(self):
        for behavior in ('oversized', 'missing_terminal', 'stale', 'unsupported_status'):
            with self.subTest(behavior=behavior):
                fixture = Fixture()
                fixture.setUp()
                try:
                    fixture.execution_fixture(behavior)
                    result = fixture.execute()
                    report = json.loads(result.stdout)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertEqual(report['reason_code'], 'failure_limit')
                    self.assertEqual(report['task_counts']['done'], 0)
                    self.assertEqual((fixture.root / 'calls').read_text(), '3')
                finally:
                    fixture.doCleanups()

    def test_broken_stdout_returns_141_without_a_traceback(self):
        self.execution_fixture()
        child = self.start_runner()
        child.stdout.close()
        child.stdout = None
        _, stderr = child.communicate(timeout=12)
        self.assertEqual(child.returncode, 141, stderr)
        self.assertNotIn('Traceback', stderr)

    def test_sigkill_requires_reconciliation_before_replacing_still_writing_worker(self):
        self.execution_fixture('writing')
        child = self.start_runner()
        self.wait_for_call(child)
        child.kill()
        child.communicate(timeout=5)
        run = next((self.repo / '.git/execplan-implement-loop/runs').iterdir())
        state = json.loads((run / 'state.json').read_text())
        pid = state['execution_in_flight']['pid']
        try:
            before = (self.repo / 'output.txt').read_text()
            time.sleep(.05)
            self.assertNotEqual((self.repo / 'output.txt').read_text(), before)
            result = self.execute('--resume', str(run))
            self.assertEqual(json.loads(result.stdout)['reason_code'], 'unclean_execution_requires_reconciliation')
            self.assertEqual((self.root / 'calls').read_text(), '1')
        finally:
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        self.env['BEHAVIOR'] = 'success'
        result = self.execute('--resume', str(run), '--acknowledge-unclean-stop')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / 'calls').read_text(), '2')


class GitTests(Fixture):
    def test_post_commit_hook_cannot_move_work_to_another_branch_silently(self):
        self.execution_fixture()
        hook = self.repo / '.git/hooks/post-commit'
        hook.write_text('#!/bin/sh\ngit branch -m hook-renamed\n')
        hook.chmod(0o700)
        result = self.execute()
        report = json.loads(result.stdout)
        self.assertEqual(report['reason_code'], 'unexpected_branch', result.stdout + result.stderr)
        self.assertEqual(report['task_counts']['done'], 0)
        self.assertEqual((self.root / 'calls').read_text(), '1')

    def test_worker_cannot_switch_branch_before_success_or_timeout(self):
        for behavior in ('branch_switch', 'branch_timeout'):
            with self.subTest(behavior=behavior):
                fixture = Fixture()
                fixture.setUp()
                try:
                    fixture.execution_fixture(behavior)
                    result = fixture.execute('--iteration-timeout', '.2')
                    self.assertEqual(json.loads(result.stdout)['reason_code'], 'unexpected_branch')
                    self.assertEqual((fixture.root / 'calls').read_text(), '1')
                    self.assertEqual(fixture.git('rev-list', '--count', 'HEAD'), '1')
                finally:
                    fixture.doCleanups()

    def test_clean_submodule_is_supported_and_dirty_submodule_blocks_fresh_run(self):
        self.execution_fixture()
        source = self.root / 'dependency-source'
        source.mkdir()
        subprocess.run(['git', 'init', '-q', str(source)], env=self.env, check=True)
        (source / 'source.txt').write_text('stable')
        subprocess.run(['git', '-C', str(source), 'add', '.'], env=self.env, check=True)
        subprocess.run(['git', '-C', str(source), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Initial dependency'], env=self.env, check=True)
        self.git('-c', 'protocol.file.allow=always', 'submodule', 'add', '-q', str(source), 'dependency')
        self.git('commit', '-qm', 'Add dependency fixture')
        self.git('config', 'submodule.dependency.ignore', 'all')
        (self.repo / 'dependency/source.txt').write_text('dirty')
        dirty = self.execute()
        self.assertEqual(json.loads(dirty.stdout)['reason_code'], 'dirty_worktree')
        self.assertFalse((self.root / 'calls').exists())
        (self.repo / 'dependency/source.txt').write_text('stable')
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_clean_filter_cannot_commit_unverified_file_contents(self):
        self.execution_fixture()
        (self.repo / '.gitattributes').write_text('output.txt filter=corrupt\n')
        self.git('add', '--', '.gitattributes')
        self.git('commit', '-qm', 'Configure fixture attributes')
        self.git('config', 'filter.corrupt.clean', 'sed s/complete/corrupted/g')
        result = self.execute()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['task_counts']['done'], 0)
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '2')

    def test_verified_deletion_has_matching_commit_evidence(self):
        (self.repo / 'output.txt').write_text('old')
        self.execution_fixture('delete')
        self.git('add', '--', 'output.txt')
        self.git('commit', '-qm', 'Seed tracked file')
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.repo / 'output.txt').exists())
        self.assertEqual(json.loads(result.stdout)['task_counts']['done'], 3)

    def test_explicit_staging_handles_leading_dash_spaces_and_pathspec_metacharacters(self):
        name = '-result [literal].txt'
        for task in self.data['tasks']:
            task['writable_paths'] = [name]
        self.plan.write_text(markdown(self.data))
        self.execution_fixture()
        self.env['OUTPUT_NAME'] = name
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git('show', 'HEAD:' + name), 'complete')

    def test_commit_created_before_journal_finalization_is_not_duplicated(self):
        self.execution_fixture()
        wrapper = self.root / 'bin'
        wrapper.mkdir()
        real_git = shutil.which('git')
        marker = self.root / 'commit-created'
        (wrapper / 'git').write_text('#!' + sys.executable + '\n' + f'''
import os, pathlib, signal, subprocess, sys
code = subprocess.call([{real_git!r}, *sys.argv[1:]])
marker = pathlib.Path({str(marker)!r})
if code == 0 and 'commit' in sys.argv and '--file' in sys.argv and not marker.exists():
    marker.write_text('created')
    os.kill(os.getppid(), signal.SIGKILL)
raise SystemExit(code)
''')
        (wrapper / 'git').chmod(0o700)
        self.env['PATH'] = str(wrapper) + os.pathsep + self.env['PATH']
        result = self.execute()
        self.assertEqual(result.returncode, -signal.SIGKILL, result.stdout + result.stderr)
        run = next((self.repo / '.git/execplan-implement-loop/runs').iterdir())
        sha = self.git('rev-parse', 'HEAD')
        blocked = self.execute('--resume', str(run))
        self.assertEqual(json.loads(blocked.stdout)['reason_code'], 'unclean_execution_requires_reconciliation')
        resumed = self.execute('--resume', str(run), '--acknowledge-unclean-stop')
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assertEqual(json.loads(resumed.stdout)['commits'][0]['sha'], sha)
        self.assertEqual((self.root / 'calls').read_text(), '1')
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '4')

    def test_second_runner_is_locked_out_even_with_a_different_run_directory(self):
        self.execution_fixture('timeout')
        child = subprocess.Popen([sys.executable, str(self.bundle / 'scripts/run.py'), str(self.plan),
                                  '--gemini', str(self.provider)], cwd=self.repo, env=self.env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            until = time.monotonic() + 5
            while not (self.root / 'calls').exists() and time.monotonic() < until:
                time.sleep(.01)
            result = self.execute('--run-dir', str(self.root / 'other-run'))
            self.assertEqual(json.loads(result.stdout)['reason_code'], 'worktree_locked')
            self.assertEqual((self.root / 'calls').read_text(), '1')
        finally:
            child.send_signal(signal.SIGTERM)
            child.communicate(timeout=8)

    def test_failed_verification_leaves_no_commit(self):
        self.data['tasks'][0]['verification'][0] = command(code=2)
        self.plan.write_text(markdown(self.data))
        self.execution_fixture()
        result = self.execute()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['reason_code'], 'verification_blocked')
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '1')
        self.assertEqual((self.repo / 'output.txt').read_text(), 'complete')

    def test_commit_hook_failure_resumes_without_reimplementing(self):
        self.execution_fixture()
        hook = self.repo / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o700)
        result = self.execute()
        report = json.loads(result.stdout)
        self.assertEqual(report['reason_code'], 'commit_failed', result.stdout + result.stderr)
        hook.write_text('#!/bin/sh\nexit 0\n')
        resumed = self.execute('--resume', report['run_directory'])
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        resumed_report = json.loads(resumed.stdout)
        self.assertEqual(resumed_report['usage']['totals']['total_tokens'], 12)
        self.assertIsNone(resumed_report['invocation_usage']['totals']['total_tokens'])
        self.assertEqual((self.root / 'calls').read_text(), '1')
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '4')

    def test_dirty_new_worktree_uses_zero_provider_calls(self):
        self.execution_fixture()
        (self.repo / 'unrelated.txt').write_text('user work')
        result = self.execute()
        self.assertEqual(json.loads(result.stdout)['reason_code'], 'dirty_worktree')
        self.assertFalse((self.root / 'calls').exists())

    def test_timeout_after_plan_mutation_never_starts_replacement(self):
        self.execution_fixture('mutate_plan')
        result = self.execute('--iteration-timeout', '.15')
        self.assertEqual(json.loads(result.stdout)['reason_code'], 'unexpected_plan_change', result.stdout + result.stderr)
        self.assertEqual((self.root / 'calls').read_text(), '1')

    def test_commit_transaction_recovers_crashes_at_filesystem_and_git_boundaries(self):
        self.execution_fixture()
        injection = self.root / 'injection'
        injection.mkdir()
        (injection / 'sitecustomize.py').write_text('''
import json, os, signal
from pathlib import Path
original = os.replace
def replace(source, target, *args, **kwargs):
    crash = False
    if str(target).endswith('state.json'):
        data = json.loads(Path(source).read_text())
        phase = (data.get('transaction') or {}).get('phase')
        crash = phase == os.environ.get('CRASH_PHASE') and not data.get('execution_in_flight')
    if os.environ.get('CRASH_PHASE') == 'plan_replaced' and str(target).endswith('plan.md'):
        crash = True
    result = original(source, target, *args, **kwargs)
    marker = Path(os.environ['CRASH_MARKER'])
    if crash and not marker.exists():
        marker.write_text('crashed')
        os.kill(os.getpid(), signal.SIGKILL)
    return result
os.replace = replace
''')
        # Each boundary starts from a fresh repository via a separate fixture.
        initial = self.git('rev-parse', 'HEAD')
        for phase in ('commit_preparing', 'plan_replaced', 'commit_pending'):
            with self.subTest(phase=phase):
                # Tests alone own this disposable repository; restoring its baseline is intentional.
                self.git('reset', '--hard', initial)
                output = self.repo / 'output.txt'
                if output.exists():
                    output.unlink()
                self.env.update(PYTHONPATH=str(injection), CRASH_PHASE=phase,
                                CRASH_MARKER=str(self.root / ('crash-' + phase)))
                result = self.execute()
                self.assertEqual(result.returncode, -signal.SIGKILL, result.stdout + result.stderr)
                run = max((self.repo / '.git/execplan-implement-loop/runs').iterdir(), key=lambda p: p.stat().st_mtime_ns)
                self.env.pop('PYTHONPATH')
                resumed = self.execute('--resume', str(run))
                self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
                self.assertEqual(len(json.loads(resumed.stdout)['commits']), 3)
                self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '4')


class LoopTests(Fixture):
    def test_two_implementation_tasks_reach_final_acceptance(self):
        second = copy.deepcopy(self.data['tasks'][0])
        second.update(id='T2', depends_on=['T1'])
        milestone = copy.deepcopy(self.data['tasks'][1])
        milestone.update(id='T3', depends_on=['T2'])
        final = copy.deepcopy(self.data['tasks'][2])
        final.update(id='T4', depends_on=['T3'])
        self.data['tasks'] = [self.data['tasks'][0], second, milestone, final]
        self.data['milestones'][0]['verification_task_id'] = 'T3'
        self.data['final_task_id'] = 'T4'
        self.plan.write_text(markdown(self.data))
        self.execution_fixture('per_task')
        result = self.execute('--max-runtime', '20', timeout=25)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['task_counts'], {'total': 4, 'done': 4})
        self.assertEqual((self.root / 'calls').read_text(), '2')
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '5')

    def test_complete_plan_has_commits_and_final_acceptance(self):
        self.execution_fixture()
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'completed')
        self.assertEqual(report['task_counts'], {'total': 3, 'done': 3})
        self.assertEqual(len(report['commits']), 3)
        self.assertEqual(report['usage']['totals']['total_tokens'], 12)
        self.assertIsNone(report['usage']['totals']['input_tokens'])
        self.assertEqual((self.root / 'calls').read_text(), '1')

    def test_declared_failure_is_repaired_then_verified(self):
        self.data['tasks'][0]['verification'][0]['argv'] = [sys.executable, '-c',
            'from pathlib import Path; raise SystemExit(0 if Path("output.txt").read_text() == "complete" else 1)']
        self.plan.write_text(markdown(self.data))
        self.execution_fixture('repair_once')
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / 'calls').read_text(), '2')
        self.assertEqual(json.loads(result.stdout)['retries']['verification'], 1)

    def test_final_sweep_obeys_final_repair_policy_and_catches_old_regression(self):
        t3 = copy.deepcopy(self.data['tasks'][0])
        t3.update(id='T3', milestone_id='M2', depends_on=['T2'])
        t4 = copy.deepcopy(self.data['tasks'][1])
        t4.update(id='T4', milestone_id='M2', depends_on=['T3'])
        t5 = copy.deepcopy(t4)
        t5.update(id='T5', depends_on=['T4'])
        t5['verification'][0]['failure_policy'] = {}
        self.data['tasks'][1]['verification'][0]['argv'] = [sys.executable, '-c',
            'from pathlib import Path; raise SystemExit(0 if Path("output.txt").read_text() == "complete" else 1)']
        self.data['tasks'] = self.data['tasks'][:2] + [t3, t4, t5]
        self.data['milestones'].append(dict(id='M2', verification_task_id='T4', state='open', evidence=[]))
        self.data['final_task_id'] = 'T5'
        self.plan.write_text(markdown(self.data))
        self.execution_fixture('break_earlier')
        result = self.execute('--max-runtime', '20', timeout=25)
        self.assertEqual(json.loads(result.stdout)['reason_code'], 'verification_blocked', result.stdout + result.stderr)
        self.assertEqual((self.root / 'calls').read_text(), '2')
        self.assertEqual(json.loads(result.stdout)['task_counts']['done'], 4)

    def test_verification_only_graph_can_request_its_authorized_repair(self):
        self.data['tasks'][0]['kind'] = 'verification'
        self.data['tasks'][0]['verification'][0]['argv'] = [sys.executable, '-c',
            'from pathlib import Path; raise SystemExit(0 if Path("output.txt").exists() else 1)']
        self.plan.write_text(markdown(self.data))
        self.execution_fixture()
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / 'calls').read_text(), '1')

    def test_worker_notes_are_rendered_as_data_and_living_status_is_current(self):
        self.execution_fixture('notes')
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = self.plan.read_text()
        self.assertIn('Observed a fixture behavior.', text)
        self.assertNotIn('<!-- execplan-loop:generated evil:start -->', text)
        self.assertIn('3 / 3', text)


class ReadinessTests(Fixture):
    def doctor_fixture(self, workspace_sources=False):
        marker = self.root / 'acceptance-ran'
        self.data['tasks'][0]['verification'][0]['argv'] = [
            sys.executable, '-c',
            f'from pathlib import Path; Path({str(marker)!r}).write_text("ran")']
        self.plan.write_text(markdown(self.data))
        self.execution_fixture()
        if workspace_sources:
            policies = self.repo / '.gemini/policies'
            policies.mkdir(parents=True)
            (policies / 'workspace.toml').write_text("marker = 'secret-workspace-marker'\n")
            settings = self.repo / '.gemini/settings.json'
            settings.write_text('{"credential":"secret-settings-marker"}\n')
            self.git('add', '--', '.gemini')
            self.git('commit', '-qm', 'Add workspace policy fixtures')
        self.install_doctor_provider()
        return marker

    def install_doctor_provider(self):
        self.provider = self.root / 'provider bin with spaces' / '-fake-gemini'
        self.provider.parent.mkdir()
        self.provider.write_text('#!' + sys.executable + '\n' + '''
import json, os, signal, sys, time
with open(os.environ['DOCTOR_LEDGER'], 'a', encoding='utf-8') as ledger:
    ledger.write(json.dumps({'argv': sys.argv[1:], 'pid': os.getpid()}) + '\\n')
if sys.argv[1:] == ['--version']:
    if os.environ.get('DOCTOR_SIGNAL_PARENT') == '1':
        print(os.environ.get('DOCTOR_VERSION', '0.65.0'), flush=True)
        os.kill(os.getppid(), signal.SIGTERM)
        raise SystemExit(0)
    time.sleep(float(os.environ.get('DOCTOR_DELAY', '0')))
    print(os.environ.get('DOCTOR_VERSION', '0.65.0'))
    raise SystemExit(0)
print('doctor must not issue provider prompts', file=sys.stderr)
raise SystemExit(97)
''')
        self.provider.chmod(0o700)
        self.ledger = self.root / 'provider-ledger.jsonl'
        self.env['DOCTOR_LEDGER'] = str(self.ledger)

    def run_doctor(self, *args, **kwargs):
        return self.run_cli('--doctor', '--gemini', str(self.provider), *args, **kwargs)

    def checks(self, report):
        return {check['id']: check for check in report['readiness']['checks']}

    def provider_calls(self):
        if not self.ledger.exists():
            return []
        return [json.loads(line) for line in self.ledger.read_text().splitlines()]

    @staticmethod
    def snapshot_tree(root):
        entries = []
        for path in sorted(root.rglob('*')):
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                entries.append((relative, 'symlink:' + os.readlink(path)))
            elif path.is_dir():
                entries.append((relative, 'directory'))
            elif path.is_file():
                entries.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))
        return entries

    def assert_doctor_summary(self, result, code, reason):
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertEqual(result.stderr, '')
        report = json.loads(result.stdout)
        self.assertEqual(result.stdout, json.dumps(report) + '\n')
        self.assertEqual(report['schema_version'], 1)
        self.assertEqual(report['status'], 'diagnosed')
        self.assertEqual(report['reason_code'], reason)
        self.assertEqual(set(report), {'schema_version', 'status', 'reason_code', 'readiness', 'blockers'})
        self.assertEqual(set(report['readiness']), {'checked_at', 'status', 'can_attempt', 'checks', 'provenance', 'limitations'})
        self.assertIn(report['readiness']['status'], ('blocked', 'unknown'))
        return report

    def test_doctor_reports_unknown_capabilities_and_only_reads_inputs(self):
        self.doctor_fixture(workspace_sources=True)
        policy = self.root / '- reviewed policy dir' / '- policy with spaces.toml'
        policy.parent.mkdir()
        policy.write_text("marker = 'secret-explicit-marker'\n")
        home = Path(self.env['HOME'])
        before_repo = self.snapshot_tree(self.repo)
        before_home = self.snapshot_tree(home)

        result = self.run_doctor(f'--policy={policy}', '--model', 'requested-model',
                                 '--approval-mode', 'auto_edit')

        report = self.assert_doctor_summary(result, 0, 'doctor_complete')
        readiness = report['readiness']
        self.assertEqual(readiness['status'], 'unknown')
        self.assertTrue(readiness['can_attempt'])
        self.assertEqual(report['blockers'], [])
        checks = self.checks(report)
        for name in ('authentication', 'trust', 'effective_permission'):
            self.assertEqual(checks[name]['status'], 'unknown')
        self.assertEqual(checks['workspace_policy']['status'], 'unknown')
        self.assertEqual(checks['provider_version']['status'], 'pass')
        provenance = readiness['provenance']
        self.assertEqual(provenance['provider']['version'], '0.65.0')
        self.assertEqual(provenance['provider']['executable'], str(self.provider.resolve()))
        self.assertEqual(provenance['requested'], {'model': 'requested-model', 'approval_mode': 'auto_edit'})
        self.assertEqual(provenance['selected_policy'], {
            'path': str(policy.resolve()), 'sha256': hashlib.sha256(policy.read_bytes()).hexdigest()})
        skills = {item['name']: item for item in provenance['skills']}
        self.assertEqual(set(skills), {'exec-plans', 'tdd'})
        for skill in skills.values():
            self.assertEqual(len(skill['sha256']), 64)
            self.assertTrue(Path(skill['path']).is_file())
        self.assertTrue(any('workspace .gemini/policies is disabled' in item.lower()
                            for item in readiness['limitations']))
        self.assertNotIn('secret-workspace-marker', result.stdout)
        self.assertNotIn('secret-settings-marker', result.stdout)
        self.assertNotIn('secret-explicit-marker', result.stdout)
        self.assertEqual([item['argv'] for item in self.provider_calls()], [['--version']])
        self.assertFalse((self.root / 'acceptance-ran').exists())
        self.assertEqual(before_repo, self.snapshot_tree(self.repo))
        self.assertEqual(before_home, self.snapshot_tree(home))
        self.assertFalse((self.repo / '.git/execplan-implement-loop.lock').exists())
        self.assertFalse((self.repo / '.git/execplan-implement-loop').exists())

    def test_doctor_collects_missing_provider_and_skill_blockers_together(self):
        self.doctor_fixture()
        (Path(self.env['HOME']) / '.agents/skills/tdd/SKILL.md').unlink()
        self.provider.unlink()

        report = self.assert_doctor_summary(self.run_doctor(), 3, 'doctor_blocked')

        self.assertEqual(report['readiness']['status'], 'blocked')
        self.assertFalse(report['readiness']['can_attempt'])
        checks = self.checks(report)
        self.assertEqual(checks['provider_version']['status'], 'blocked')
        self.assertEqual(checks['skill_tdd']['status'], 'blocked')
        self.assertEqual(checks['skill_exec_plans']['status'], 'pass')
        for name in ('authentication', 'trust', 'effective_permission'):
            self.assertEqual(checks[name]['status'], 'unknown')
        self.assertEqual(self.provider_calls(), [])

    def test_doctor_reports_wrong_provider_version_as_a_blocker(self):
        self.doctor_fixture()
        self.env['DOCTOR_VERSION'] = '9.9.9'

        report = self.assert_doctor_summary(self.run_doctor(), 3, 'doctor_blocked')

        check = self.checks(report)['provider_version']
        self.assertEqual(check['status'], 'blocked')
        self.assertEqual(check['reason_code'], 'unsupported_gemini_version')
        self.assertEqual([item['argv'] for item in self.provider_calls()], [['--version']])

    def test_invalid_plan_does_not_suppress_other_readiness_checks(self):
        self.doctor_fixture()
        self.plan.write_text('# invalid plan\n')
        self.env['DOCTOR_VERSION'] = '9.9.9'

        report = self.assert_doctor_summary(self.run_doctor(), 2, 'invalid_contract')

        checks = self.checks(report)
        self.assertEqual(checks['plan']['status'], 'blocked')
        self.assertEqual(checks['provider_version']['status'], 'blocked')
        self.assertEqual([item['argv'] for item in self.provider_calls()], [['--version']])

    def test_explicit_policy_rejects_invalid_and_unsafe_paths(self):
        self.doctor_fixture()
        cases = []
        comma = self.root / 'comma,name.toml'
        comma.write_text('value = 1\n')
        cases.append(('comma', comma))
        missing = self.root / 'missing.toml'
        cases.append(('missing', missing))
        directory = self.root / 'policy-directory.toml'
        directory.mkdir()
        cases.append(('directory', directory))
        malformed = self.root / 'malformed.toml'
        malformed.write_text('value = [\n')
        cases.append(('malformed', malformed))
        unreadable = self.root / 'unreadable.toml'
        unreadable.write_text('value = 1\n')
        unreadable.chmod(0)
        cases.append(('unreadable', unreadable))
        wrong_extension = self.root / 'policy.txt'
        wrong_extension.write_text('value = 1\n')
        cases.append(('extension', wrong_extension))
        oversized = self.root / 'oversized.toml'
        oversized.write_bytes(b'x' * (1024 * 1024 + 1))
        cases.append(('oversized', oversized))
        invalid_utf8 = self.root / 'invalid-utf8.toml'
        invalid_utf8.write_bytes(b'\xff')
        cases.append(('utf8', invalid_utf8))
        linked = self.root / 'linked.toml'
        linked.symlink_to(malformed)
        cases.append(('symlink', linked))
        linked_parent = self.root / 'linked-parent'
        linked_parent.symlink_to(self.root, target_is_directory=True)
        cases.append(('symlink component', linked_parent / 'malformed.toml'))

        for label, path in cases:
            with self.subTest(policy=label):
                report = self.assert_doctor_summary(self.run_doctor(f'--policy={path}'), 2, 'invalid_policy')
                check = self.checks(report)['explicit_policy']
                self.assertEqual(check['status'], 'blocked')
        self.assertEqual([item['argv'] for item in self.provider_calls()], [['--version']] * len(cases))

    def test_unreadable_skill_is_a_blocker_without_a_prompt(self):
        self.doctor_fixture()
        skill = Path(self.env['HOME']) / '.agents/skills/exec-plans/SKILL.md'
        skill.chmod(0)
        if os.access(skill, os.R_OK):
            self.skipTest('host privileges bypass unreadable file mode bits')

        report = self.assert_doctor_summary(self.run_doctor(), 3, 'doctor_blocked')

        self.assertEqual(self.checks(report)['skill_exec_plans']['status'], 'blocked')
        self.assertEqual(self.checks(report)['skill_exec_plans']['reason_code'], 'unreadable_skill_dependency')
        self.assertEqual([item['argv'] for item in self.provider_calls()], [['--version']])

    def test_doctor_rejects_conflicting_or_mutating_options_before_inspection(self):
        self.doctor_fixture()
        incompatible = [('--validate-only',), ('--run-dir', str(self.root / 'run')),
                        ('--acknowledge-unclean-stop',)]
        for args in incompatible:
            with self.subTest(args=args):
                result = self.run_doctor(*args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertIn('usage:', result.stderr.lower())
        self.assertEqual(self.provider_calls(), [])
        self.assertFalse((self.repo / '.git/execplan-implement-loop.lock').exists())

    def test_doctor_deadline_and_cancellation_keep_provider_bounded(self):
        self.doctor_fixture()
        timed = self.run_doctor('--max-runtime', '0.000001', timeout=5)
        self.assertEqual(timed.returncode, 124, timed.stdout + timed.stderr)
        timed_report = json.loads(timed.stdout)
        self.assertEqual(timed_report['reason_code'], 'total_deadline')
        self.assertEqual(self.provider_calls(), [])

        if self.ledger.exists():
            self.ledger.unlink()
        self.env['DOCTOR_DELAY'] = '0'
        self.env['DOCTOR_SIGNAL_PARENT'] = '1'
        cancelled = self.run_doctor('--max-runtime', '30', timeout=5)
        self.assertEqual(cancelled.returncode, 143, cancelled.stdout + cancelled.stderr)
        self.assertEqual(json.loads(cancelled.stdout)['reason_code'], 'interrupted')
        self.assertEqual([item['argv'] for item in self.provider_calls()], [['--version']])

    def test_doctor_inspects_a_recognized_resume_without_mutating_journal_or_project(self):
        self.execution_fixture()
        self.provider = self.root / 'provider bin with spaces' / '-fake-gemini'
        run_dir = self.root / 'recognized run'
        executed = self.run_cli('--gemini', str(self.root / 'gemini'), '--run-dir', str(run_dir), '--max-runtime', '10')
        self.assertEqual(executed.returncode, 0, executed.stdout + executed.stderr)
        self.install_doctor_provider()
        ledger_before = self.ledger
        state_before = (run_dir / 'state.json').read_bytes()
        summary_before = (run_dir / 'summary.json').read_bytes()
        project_before = self.snapshot_tree(self.repo)
        lock_path = self.repo / '.git/execplan-implement-loop.lock'
        lock_before = lock_path.read_bytes() if lock_path.exists() else None

        report = self.assert_doctor_summary(self.run_doctor('--resume', str(run_dir)), 0, 'doctor_complete')

        self.assertEqual(report['readiness']['provenance']['resume']['status'], 'recognized')
        self.assertEqual((run_dir / 'state.json').read_bytes(), state_before)
        self.assertEqual((run_dir / 'summary.json').read_bytes(), summary_before)
        self.assertEqual(self.snapshot_tree(self.repo), project_before)
        self.assertEqual([item['argv'] for item in self.provider_calls()], [['--version']])
        self.assertEqual(lock_path.read_bytes() if lock_path.exists() else None, lock_before)


class PackagingTests(Fixture):
    def test_live_qualification_plan_has_real_source_acceptance(self):
        self.plan.write_bytes((self.bundle / 'evals/fixtures/live-qualification.md').read_bytes())
        result = self.run_cli('--validate-only')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(self.plan.read_text().split('```execplan-loop-v1\n')[1].split('```')[0])
        check = data['tasks'][0]['verification'][0]
        def verify():
            return subprocess.run(check['argv'], cwd=self.repo, capture_output=True, timeout=10).returncode
        self.assertEqual(verify(), 1)
        (self.repo / 'greeting.py').write_text('def greet(name):\n    return "wrong"\n')
        (self.repo / 'test_greeting.py').write_text('import unittest\nfrom greeting import greet\nclass GreetingTests(unittest.TestCase):\n    def test_name(self):\n        self.assertEqual(greet("Ada"), "Hello, Ada!")\n    def test_empty(self):\n        self.assertEqual(greet(""), "Hello, !")\n')
        self.assertEqual(verify(), 1)
        (self.repo / 'greeting.py').write_text('def greet(name):\n    return "Hello, " + name + "!"\n')
        self.assertEqual(verify(), 0)

    def test_bundled_example_rejects_incorrect_deliverable_content(self):
        self.plan.write_bytes((self.bundle / 'evals/fixtures/example.md').read_bytes())
        self.execution_fixture('wrong_output')
        result = self.execute()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['task_counts']['done'], 0)
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '1')

    def test_message_reference_is_exact_and_runtime_links_resolve(self):
        self.assertEqual((self.bundle / 'references/message.md').read_bytes(),
                         (ROOT / 'skills/default/execplan-implement/references/message.md').read_bytes())
        import re
        for name in ('SKILL.md', 'references/plan-format.md'):
            source = self.bundle / name
            for target in re.findall(r'\]\(([^)]+)\)', source.read_text()):
                if '://' not in target:
                    self.assertTrue((source.parent / target).is_file(), target)

    def test_missing_worker_skill_blocks_before_prompt(self):
        self.execution_fixture()
        shutil.rmtree(Path(self.env['HOME']) / '.agents/skills/tdd')
        result = self.execute()
        self.assertEqual(json.loads(result.stdout)['reason_code'], 'missing_skill_dependency')
        self.assertFalse((self.root / 'calls').exists())

    def test_installed_prompt_and_explicit_options_keep_worker_responsibilities(self):
        self.execution_fixture()
        self.env['OBSERVATIONS'] = str(self.root / 'observations.json')
        result = self.execute('--model', 'test-model', '--approval-mode', 'auto_edit')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        observation = json.loads((self.root / 'observations.json').read_text())
        self.assertIn('Activate the `tdd` skill', observation['prompt'])
        self.assertIn('Do not commit, stage', observation['prompt'])
        self.assertIn('explicitly declined the Copilot', observation['prompt'])
        self.assertIn('test-model', observation['argv'])
        self.assertIn('auto_edit', observation['argv'])
        self.assertNotIn('--resume', observation['argv'])
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertIn('commit_success', result.stderr)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--group', choices=['contract', 'process', 'git', 'loop', 'packaging', 'readiness'])
    options = parser.parse_args()
    classes = {'contract': ContractTests, 'process': ProcessTests, 'git': GitTests, 'loop': LoopTests,
               'packaging': PackagingTests, 'readiness': ReadinessTests}
    suite = unittest.TestSuite()
    for name, cls in classes.items():
        if options.group is None or options.group == name:
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
    raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())

"""Deterministic scheduler, durable journal, verification and Git transactions."""
from __future__ import annotations

import base64
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile
import time
import uuid
from types import SimpleNamespace
from datetime import datetime, timezone

from contracts import Plan, Stop, confined, message_valid, require, worker_result
from processes import GeminiStream, Supervisor
from readiness import collect_readiness, recorded_policy, validate_policy_file
from reporting import make_blocker, provider_diagnostic

BUNDLE = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def usage_totals(iterations):
    totals, observed = {}, {}
    for field in ('total_tokens', 'input_tokens', 'output_tokens', 'duration_ms', 'tool_calls'):
        values = [(item.get('usage') or {}).get(field) for item in iterations]
        known = [value for value in values if value is not None]
        observed[field] = sum(known) if known else None
        totals[field] = sum(known) if values and len(known) == len(values) else None
    return dict(totals=totals, observed_totals=observed, iteration_count=len(iterations))


def unlinked(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise Stop('unsafe_state_path', f'Symlink in state path: {part}', 3)


def atomic(path, raw, preserve_mode=False):
    unlinked(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        if preserve_mode:
            os.fchmod(fd, stat.S_IMODE(path.stat().st_mode))
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        parent = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Engine:
    def __init__(self, args, plan, supervisor, started):
        self.args, self.plan, self.supervisor, self.started = args, plan, supervisor, started
        self.root = plan.path.parent
        self.directory = None
        self.lock = None
        self.state = None
        self.invocation = uuid.uuid4().hex
        self.current = None
        self.phase = 'preflight'
        self.integrity_errors = []
        self.readiness = None
        self.readiness_result = None
        self.selected_policy = None
        self.previous_policy = None
        self.policy_bound = False

    def event(self, kind, **fields):
        import sys
        print(json.dumps(dict(event=kind, timestamp=now(), task_id=self.current, **fields)), file=sys.stderr, flush=True)

    def git(self, *args, timeout=30):
        result = self.supervisor.run(['git', *args], self.root, timeout)
        if result.timed_out:
            self.supervisor.check()
            raise Stop('git_timeout', 'Git command timed out', 3)
        self.supervisor.check()
        if result.stdout_truncated:
            raise Stop('git_output_limit', 'Git response exceeds 1 MiB; refusing incomplete ownership information', 3)
        if result.code:
            raise Stop('git_error', f'Git {args[0]} failed (exit {result.code}); inspect repository configuration', 3)
        return result.stdout

    def head(self):
        return self.git('rev-parse', 'HEAD').decode().strip()

    def assert_branch(self):
        result = self.supervisor.run(['git', 'symbolic-ref', '--quiet', '--short', 'HEAD'], self.root, 10)
        self.supervisor.check()
        if result.code or result.timed_out or result.stdout.decode().strip() != self.branch:
            raise Stop('unexpected_branch', 'Worktree branch changed during execution', 3)

    def index(self):
        return self.git('write-tree').decode().strip()

    def changed(self):
        names = self.git('diff', '--ignore-submodules=none', '--no-renames', '--name-only', '-z', 'HEAD', '--')
        names += self.git('ls-files', '--others', '--exclude-standard', '-z')
        return sorted(set(os.fsdecode(value) for value in names.split(b'\x00') if value))

    def file_hash(self, name):
        path = confined(self.root, name)
        if path.is_symlink():
            return 'symlink:' + digest(os.fsencode(os.readlink(path)))
        if not path.exists():
            return 'deleted'
        if not path.is_file():
            raise Stop('unsupported_change', f'Not an ordinary file: {name}', 3)
        return f'{stat.S_IMODE(path.stat().st_mode) & 0o111}:' + digest(path.read_bytes())

    def fingerprint(self):
        return {name: self.file_hash(name) for name in self.changed()}

    def content_digest(self):
        names = set(os.fsdecode(v) for v in self.git('ls-files', '-z').split(b'\0') if v)
        names.update(self.changed())
        gitlinks = {}
        for entry in self.git('ls-files', '--stage', '-z').split(b'\0'):
            if entry.startswith(b'160000 '):
                metadata, name = entry.split(b'\t', 1)
                gitlinks[os.fsdecode(name)] = 'gitlink:' + metadata.split()[1].decode()
        snapshot = {name: (self.plan.immutable_hash() if name == self.plan_name else self.file_hash(name))
                    for name in sorted(names) if name not in gitlinks and ((self.root / name).exists() or (self.root / name).is_symlink())}
        snapshot.update(gitlinks)
        return digest(json.dumps(snapshot, sort_keys=True).encode())

    def verify_tree_contents(self, tree):
        algorithm = self.git('rev-parse', '--show-object-format').decode().strip()
        for entry in self.git('ls-tree', '-rz', '--full-tree', tree).split(b'\0'):
            if not entry:
                continue
            metadata, raw_name = entry.split(b'\t', 1)
            mode, kind, oid = metadata.split()
            name = os.fsdecode(raw_name)
            if kind == b'commit':
                continue  # Clean gitlinks are checked by Git; changed submodules block integrity.
            path = confined(self.root, name)
            if path.is_symlink():
                raw, expected_mode = os.fsencode(os.readlink(path)), b'120000'
            else:
                require(path.is_file(), f'Candidate file missing: {name}')
                raw = path.read_bytes()
                expected_mode = b'100755' if path.stat().st_mode & 0o111 else b'100644'
            blob = hashlib.new(algorithm, b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest().encode()
            if oid != blob or mode != expected_mode:
                raise Stop('staged_content_mismatch', f'Git filters or index state changed verified bytes: {name}', 3)

    def save(self):
        if self.directory and self.state:
            atomic(self.directory / 'state.json', json.dumps(self.state, indent=2).encode())

    def checkpoint(self):
        self.state['expected_head'] = self.head()
        self.state['expected_index'] = self.index()
        self.state['fingerprint'] = self.fingerprint()
        self.save()

    def preflight(self):
        if os.name != 'posix':
            raise Stop('unsupported_platform', 'macOS or Linux required')
        self.root = Path(self.git('rev-parse', '--show-toplevel').decode().strip()).resolve()
        require(self.plan.path.is_relative_to(self.root), 'Plan must be inside repository')
        self.plan_name = self.plan.path.relative_to(self.root).as_posix()
        self.git_dir = Path(self.git('rev-parse', '--absolute-git-dir').decode().strip()).resolve()
        lock_path = self.git_dir / 'execplan-implement-loop.lock'
        unlinked(lock_path)
        self.lock = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise Stop('worktree_locked', 'Another loop owns this worktree', 3) from error
        self.branch = self.git('symbolic-ref', '--quiet', '--short', 'HEAD').decode().strip()
        for marker in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'BISECT_LOG'):
            if (self.git_dir / marker).exists():
                raise Stop('git_operation_in_progress', marker, 3)
        self.git('ls-files', '--error-unmatch', '--', self.plan_name)
        for task in self.plan.tasks.values():
            for name in task['writable_paths']:
                confined(self.root, name)
            for command in task['verification']:
                confined(self.root, command['cwd'])
        if self.args.resume:
            self.directory = self.args.resume.absolute()
            unlinked(self.directory)
            state_path = self.directory / 'state.json'
            unlinked(state_path)
            for private in (self.directory, state_path):
                metadata = private.stat()
                require(metadata.st_uid == os.getuid() and not stat.S_IMODE(metadata.st_mode) & 0o077,
                        'State directory and journal must be owner-only')
            state = json.loads(state_path.read_text())
            require(isinstance(state, dict) and state.get('schema_version') == 1, 'Invalid journal schema')
            for field in ('invocations', 'iterations', 'commands', 'completed', 'commits'):
                require(isinstance(state.get(field), list), f'Invalid journal {field}')
            for field in ('task_states', 'evidence', 'failures', 'retries', 'timeout_counts', 'fingerprint'):
                require(isinstance(state.get(field), dict), f'Invalid journal {field}')
            require(set(state['completed']) <= set(self.plan.tasks) and len(set(state['completed'])) == len(state['completed']),
                    'Invalid completed journal tasks')
            require(set(state['task_states']) == set(self.plan.tasks), 'Journal task mapping mismatch')
            self.state = state
            for key, value in dict(worktree=str(self.root), git_dir=str(self.git_dir), branch=self.branch,
                                   plan_path=str(self.plan.path), contract_hash=self.plan.immutable_hash()).items():
                require(self.state.get(key) == value, f'Resume identity mismatch: {key}')
            if self.state.get('execution_in_flight') and not self.args.acknowledge_unclean_stop:
                raise Stop('unclean_execution_requires_reconciliation',
                           'Stop prior child tree, inspect task delta, then resume with --acknowledge-unclean-stop', 3)
            if self.args.acknowledge_unclean_stop:
                require(self.state.get('execution_in_flight'), 'Acknowledgement only applies to unclean execution')
                self.current = self.state.get('current_task')
                if not self.state.get('transaction'):
                    self.integrity(self.plan.tasks[self.current])
                self.state['execution_in_flight'] = None
                if not self.state.get('transaction'):
                    self.checkpoint()
                else:
                    self.save()
            self.start_invocation()
            if self.state.get('transaction'):
                self.current = self.state['transaction']['task_id']
                self.recover_commit()
            else:
                require(self.head() == self.state['expected_head'] and self.index() == self.state['expected_index'] and
                        self.fingerprint() == self.state['fingerprint'], 'Resume repository fingerprint mismatch')
        else:
            require(not self.args.acknowledge_unclean_stop, 'Acknowledgement requires --resume')
            require(all(t['state'] == 'open' for t in self.plan.tasks.values()), 'New runs require all-open state')
            if self.changed() or self.git('diff', '--cached', '--name-only', '-z'):
                raise Stop('dirty_worktree', 'Fresh execution requires clean index and worktree', 3)
            require(self.git('show', f'HEAD:{self.plan_name}') == self.plan.path.read_bytes(), 'Plan must match initial HEAD')
            self.directory = (self.args.run_dir or self.git_dir / 'execplan-implement-loop/runs' / uuid.uuid4().hex).absolute()
            unlinked(self.directory)
            require(not self.directory.resolve().is_relative_to(self.root) or
                    (self.args.run_dir is None and self.directory.resolve().is_relative_to(self.git_dir)),
                    'Run directory must be outside tracked worktree')
            # Git metadata is inside ordinary worktrees; this is the deliberate default exception.
            self.new_state()
            self.start_invocation()
        self.save()
        # Commit reconciliation deliberately precedes policy/provider gating.
        # Even provider-free invocations retain any explicitly selected input.
        if self.args.policy is not None:
            try:
                self.selected_policy = validate_policy_file(self.args.policy)
            except Stop as error:
                self.readiness_blocker(error.reason, error.detail)
                self.save()
                raise
            else:
                self.policy_bound = True
                self.readiness['provenance']['selected_policy'] = self.selected_policy
                self.state['invocations'][-1]['policy_selection'] = dict(
                    explicit=True, previous=self.previous_policy, selected=self.selected_policy)
            self.save()

    def start_invocation(self):
        self.previous_policy = recorded_policy(self.state['invocations'])
        self.readiness = dict(checked_at=now(), status='unknown', can_attempt=True,
                              checks=[dict(id='provider_readiness', status='unknown',
                                           reason_code='provider_check_deferred',
                                           detail='Provider checks run only when a new Gemini iteration is needed')],
                              provenance=dict(provider=dict(executable=self.args.gemini, version=None),
                                              plan=dict(path=str(self.plan.path), plan_id=self.plan.data['plan_id'],
                                                        contract_hash=self.plan.immutable_hash()),
                                              workspace=dict(root=str(self.root), git_dir=str(self.git_dir), branch=self.branch),
                                              skills=[], selected_policy=self.previous_policy,
                                              requested=dict(model=self.args.model, approval_mode=self.args.approval_mode)),
                              limitations=['Provider prerequisites, authentication, trust, and effective permission have not been checked for this invocation.',
                                           'Provenance is not a sandbox or authorization for paid use.'])
        self.state['invocations'].append(dict(id=self.invocation, started_at=now(), max_runtime=self.args.max_runtime,
                                              readiness=self.readiness))
        self.save()

    def new_state(self):
        require(not self.directory.exists(), 'Run directory already exists; use --resume')
        self.directory.mkdir(parents=True, mode=0o700)
        self.state = dict(schema_version=1, run_id=self.directory.name, worktree=str(self.root), git_dir=str(self.git_dir),
                          branch=self.branch, plan_path=str(self.plan.path), plan_id=self.plan.data['plan_id'],
                          contract_hash=self.plan.immutable_hash(), started_at=now(), invocations=[], iterations=[], commands=[],
                          completed=[], commits=[], evidence={}, timeout_counts=dict(gemini=0, verification=0),
                          retries=dict(protocol=0, transient_infrastructure=0, verification=0),
                          failures=dict(protocol=0, transient_infrastructure=0, verification=0),
                          current_task=None, task_states={i: 'open' for i in self.plan.tasks}, execution_in_flight=None, transaction=None)
        self.checkpoint()

    def dependencies(self):
        previous = self.previous_policy
        expected = self.selected_policy if self.policy_bound else previous
        policy = (Path(expected['path']) if expected else None) if self.policy_bound or self.args.policy is None else self.args.policy
        provider = shutil.which(self.args.gemini)
        def inspect(argv, cwd, timeout):
            if argv == [provider, '--version']:
                self.process_cwd = '.'
                return self.owned_process(argv, timeout, self.plan.tasks[self.current])
            return self.supervisor.run(argv, cwd, timeout)
        inspector = SimpleNamespace(check=self.supervisor.check, run=inspect)
        result = collect_readiness(plan_path=self.plan.path, workspace=self.root,
                                   gemini=self.args.gemini, policy=policy, model=self.args.model,
                                   approval_mode=self.args.approval_mode, resume=self.directory,
                                   supervisor=inspector)
        self.readiness_result, self.readiness = result, result.readiness
        observed = self.readiness['provenance']['selected_policy']
        if not self.policy_bound:
            self.selected_policy = observed if self.args.policy is not None else previous
            self.policy_bound = True
        invocation = self.state['invocations'][-1]
        invocation.update(readiness=self.readiness,
                          policy_selection=dict(explicit=self.args.policy is not None,
                                                previous=previous, selected=self.selected_policy))
        policy_checked = any(item['id'] == 'explicit_policy' for item in self.readiness['checks'])
        if self.selected_policy is not None and policy_checked and observed != self.selected_policy:
            self.readiness_blocker('policy_changed', 'Recorded policy changed or is unavailable; select reviewed bytes explicitly with --policy')
        elif not policy_checked:
            self.readiness['provenance']['selected_policy'] = self.selected_policy
        self.executable = self.readiness['provenance']['provider']['executable']
        invocation.setdefault('readiness_history', []).append(copy.deepcopy(self.readiness))
        self.save()

    def readiness_blocker(self, reason, detail):
        self.readiness.update(status='blocked', can_attempt=False)
        self.readiness['checks'].append(dict(id='selected_policy_binding', status='blocked',
                                             reason_code=reason, detail=detail[:4096]))

    def require_readiness(self):
        if not self.readiness['can_attempt']:
            if self.readiness_result.reason_code in ('interrupted', 'total_deadline', 'cleanup_unconfirmed'):
                raise Stop(self.readiness_result.reason_code, 'Readiness inspection could not finish', self.readiness_result.exit_code)
            checks = [item for item in self.readiness['checks'] if item['status'] == 'blocked']
            failure = next((item for item in checks if item['reason_code'] == 'policy_changed'), checks[0])
            code = self.readiness_result.exit_code or 3
            if failure['reason_code'] == 'policy_changed':
                code = 3
            raise Stop(failure['reason_code'], failure['detail'], code)

    def recheck_policy(self):
        if self.selected_policy is None:
            return
        try:
            observed = validate_policy_file(self.selected_policy['path'])
        except Stop:
            observed = None
        if observed != self.selected_policy:
            detail = 'Selected policy changed or is unavailable before spawn; resume with an explicitly reviewed --policy'
            self.readiness_blocker('policy_changed', detail)
            self.save()
            raise Stop('policy_changed', detail, 3)

    def integrity(self, task):
        self.assert_branch()
        if self.head() != self.state['expected_head']:
            raise Stop('unexpected_head', 'Worker or command changed HEAD', 3)
        if self.index() != self.state['expected_index']:
            raise Stop('unexpected_index', 'Worker or command changed index', 3)
        if self.plan.path.read_bytes() != self.plan.text.encode():
            raise Stop('unexpected_plan_change', 'Only runner may edit plan', 3)
        for name in self.changed():
            if name == self.plan_name and self.state.get('transaction'):
                continue
            if name == self.plan_name or not any(name == scope or (scope.endswith('/') and name.startswith(scope)) for scope in task['writable_paths']):
                raise Stop('out_of_scope_change', f'Unexpected changed path: {name}', 3)
            confined(self.root, name)
        submodules = [line.split(b'\t', 1)[-1] for line in self.git('ls-files', '--stage', '-z').split(b'\0') if line.startswith(b'160000 ')]
        if any(os.fsdecode(name) in self.changed() for name in submodules):
            raise Stop('submodule_change', 'Submodule changes require manual reconciliation', 3)

    def owned_process(self, argv, timeout, task, consume=None, before_spawn=None):
        self.state['execution_in_flight'] = dict(argv0=argv[0], task_id=task['id'], started_at=now(), pid=None)
        self.save()
        def spawned(pid):
            self.state['execution_in_flight']['pid'] = pid
            self.save()
        outcome = None
        failure = None
        try:
            if before_spawn:
                before_spawn()
            outcome = self.supervisor.run(argv, confined(self.root, self.process_cwd), timeout, consume, spawned)
        except Stop as error:
            failure = error
        except OSError as error:
            failure = Stop('cleanup_unconfirmed', f'Process supervision failed: {error}', 3)
        try:
            # Integrity must still run after deadline/signal. A separate bounded local
            # inspection window cannot authorize another executable task.
            saved_deadline = self.supervisor.deadline
            self.supervisor.deadline = max(saved_deadline, time.monotonic() + 5)
            self.supervisor.inspection = True
            try:
                self.integrity(task)
                if failure is None or failure.reason != 'cleanup_unconfirmed':
                    self.state['execution_in_flight'] = None
                self.checkpoint()
            finally:
                self.supervisor.deadline = saved_deadline
                self.supervisor.inspection = False
        except Stop as error:
            self.integrity_errors.append(error.reason)
            self.save()
            if self.supervisor.signal or time.monotonic() >= self.supervisor.deadline:
                self.supervisor.check()
            raise
        self.supervisor.check()
        if failure:
            raise failure
        return outcome

    def invoke(self, task, diagnostics):
        self.dependencies()
        self.require_readiness()
        self.phase = 'implementation'
        iteration = uuid.uuid4().hex
        self.event('task_start', iteration_id=iteration)
        self.state['task_states'][task['id']] = 'in_progress'
        packet = dict(iteration_id=iteration, task_id=task['id'], plan_path=str(self.plan.path),
                      remaining_seconds=max(0, self.supervisor.deadline - time.monotonic()),
                      partial_changed_files=self.changed(), diagnostics=diagnostics,
                      result_schema=dict(schema_version=1, iteration_id=iteration, task_id=task['id'],
                          status='ready_for_verification|blocked|failed', summary='string', changed_files=['relative/path'],
                          commit_message='string or null outside ready status', plan_notes=['string'], reason_code='string'))
        prompt = (BUNDLE / 'references/worker-prompt.md').read_text()
        prompt += '\nCommit message reference: ' + str(BUNDLE / 'references/message.md')
        prompt += '\nProtocol reference: ' + str(BUNDLE / 'references/protocol.md')
        prompt += '\nRUNNER_PACKET=' + json.dumps(packet, separators=(',', ':'))
        argv = [self.executable, '--prompt', prompt, '--output-format', 'stream-json']
        if self.args.model:
            argv += ['--model', self.args.model]
        if self.args.approval_mode:
            argv += ['--approval-mode', self.args.approval_mode]
        if self.selected_policy:
            argv += ['--policy', self.selected_policy['path']]
        stream = GeminiStream()
        record = dict(iteration_id=iteration, invocation_id=self.invocation, task_id=task['id'], started_at=now(),
                      session_id=None, model=None, requested_model=self.args.model,
                      usage=None, status='in_progress')
        self.state['iterations'].append(record)
        self.process_cwd = '.'
        try:
            result = self.owned_process(argv, self.args.iteration_timeout, task, stream.feed,
                                        before_spawn=self.recheck_policy)
            record.update(duration_seconds=result.duration, exit_code=result.code)
            if result.timed_out:
                self.state['timeout_counts']['gemini'] += 1
                self.event('iteration_timeout', iteration_id=iteration)
                record['status'] = 'timeout'
                return None
            try:
                if stream.terminal is None:
                    metadata, sanitized = provider_diagnostic(
                        result.stderr, result.stderr_captured_bytes, result.stderr_truncated)
                    record['provider_diagnostic'] = metadata
                    if sanitized is not None:
                        reference = f'provider-stderr-{iteration}.log'
                        try:
                            atomic(self.directory / reference, sanitized)
                        except (OSError, Stop) as error:
                            metadata.update(retained_bytes=0, redaction_status='content_omitted')
                            raise Stop('diagnostic_persistence_failed',
                                       'Unable to persist sanitized provider diagnostic', 3) from error
                        metadata['artifact_ref'] = reference
                if result.code and stream.terminal is None:
                    raise Stop('provider_blocked', f'Gemini exited {result.code} without terminal result', 3)
                text = stream.finish()
                if result.code:
                    raise Stop('provider_blocked', f'Gemini exited {result.code}', 3)
                proposed = worker_result(text, iteration, task['id'])
            except Stop as error:
                if error.reason == 'invalid_contract':
                    raise Stop('protocol', error.detail, 1) from error
                raise
            record['result'] = proposed
            self.state.setdefault('notes', []).extend(proposed['plan_notes'])
            record['status'] = proposed['status']
            if set(proposed['changed_files']) != set(self.changed()):
                raise Stop('protocol', 'Worker changed_files differs from cumulative Git delta', 1)
            if proposed['status'] != 'ready_for_verification':
                raise Stop('worker_' + proposed['status'], proposed['reason_code'], 3 if proposed['status'] == 'blocked' else 1)
            return proposed['commit_message']
        except Stop as error:
            status = 'blocked' if error.reason == 'worker_blocked' else 'failed'
            record.update(status=status, reason_code=error.reason)
            raise
        finally:
            record.update(session_id=stream.session_id, model=stream.model, usage=stream.usage,
                          provider_observations=stream.provider_observations,
                          usage_complete=bool(stream.usage and all(v is not None for v in stream.usage.values())))
            self.save()

    def verify(self, task):
        self.phase = 'verification'
        self.state['task_states'][task['id']] = 'verification_pending'
        commands = [(command, command['failure_policy']) for command in task['verification']]
        if task['id'] == self.plan.data['final_task_id']:
            # Final candidate must pass every milestone again, regardless of old evidence.
            commands = [(command, task['verification'][0]['failure_policy']) for m in self.plan.milestones.values()
                        for command in self.plan.tasks[m['verification_task_id']]['verification']] + commands
        snapshot = self.content_digest()
        evidence = []
        self.state['evidence'][task['id']] = evidence
        for command, failure_policy in commands:
            self.event('verification_start', command_id=command['id'])
            self.process_cwd = command['cwd']
            outcome = self.owned_process(command['argv'], command['timeout_seconds'], task)
            log = f'verification-{self.invocation}-{task["id"]}-{uuid.uuid4().hex}.log'
            atomic(self.directory / log, b'STDOUT (bounded tail)\n' + outcome.stdout + b'\nSTDERR (bounded tail)\n' + outcome.stderr)
            record = dict(task_id=task['id'], command_id=command['id'], invocation_id=self.invocation, timestamp=now(),
                          exit_code=outcome.code, duration_seconds=outcome.duration, timed_out=outcome.timed_out,
                          stdout_truncated=outcome.stdout_truncated, stderr_truncated=outcome.stderr_truncated,
                          candidate_digest=snapshot, log_reference=log)
            self.state['commands'].append(record)
            if self.content_digest() != snapshot:
                raise Stop('verification_mutated_candidate', 'Verification changed deliverable bytes', 3)
            if outcome.timed_out:
                self.state['timeout_counts']['verification'] += 1
            if outcome.timed_out or outcome.code != command['expected_exit_code']:
                self.event('verification_fail', command_id=command['id'], exit_code=outcome.code, timed_out=outcome.timed_out)
                self.save()
                # Timeouts consume the verification failure allowance, but never infer repair permission.
                if outcome.timed_out:
                    self.state['failures']['verification'] += 1
                    self.save()
                    raise Stop('verification_timeout', f'Check {command["id"]} timed out', 3)
                if failure_policy.get(str(outcome.code)) != 'repair':
                    raise Stop('verification_blocked', f'Check {command["id"]} exit {outcome.code} has no repair policy', 3)
                raise Stop('verification', f'Check {command["id"]} failed; diagnostics: {self.directory / log}', 1)
            evidence.append({key: record[key] for key in ('command_id', 'invocation_id', 'timestamp', 'exit_code', 'candidate_digest', 'log_reference')})
            self.event('verification_pass', command_id=command['id'])
        self.save()
        return snapshot

    def commit(self, task, message, candidate):
        self.phase = 'commit_preparing'
        message_valid(message)
        before = self.plan.path.read_bytes()
        after = self.plan.render(set(self.state['completed']) | {task['id']}, self.state['evidence'], self.state.get('notes', []))
        paths = sorted(set(self.changed()) | {self.plan_name})
        self.state['transaction'] = dict(task_id=task['id'], phase='commit_preparing', parent=self.head(),
                                         before_plan=base64.b64encode(before).decode(), after_plan=base64.b64encode(after).decode(),
                                         fingerprint=self.fingerprint(), index=self.index(), paths=paths,
                                         message=message, message_digest=digest(message.encode()), candidate_digest=candidate, tree=None)
        self.state['task_states'][task['id']] = 'commit_preparing'
        self.save()  # Write-ahead intent precedes both plan and index mutations.
        self.recover_commit()

    def recover_commit(self):
        self.assert_branch()
        transaction = self.state['transaction']
        identifier = transaction['task_id']
        self.current = identifier
        self.phase = transaction['phase']
        before, after = (base64.b64decode(transaction[key]) for key in ('before_plan', 'after_plan'))
        current_head = self.head()
        if current_head != transaction['parent']:
            require(transaction['tree'] is not None, 'Unexpected commit before candidate preparation')
            require(self.git('show', '-s', '--format=%P', 'HEAD').decode().strip() == transaction['parent'] and
                    self.git('rev-parse', 'HEAD^{tree}').decode().strip() == transaction['tree'] and
                    self.git('show', '-s', '--format=%B', 'HEAD').decode().strip() == transaction['message'].strip(),
                    'HEAD does not match prepared transaction')
            require(not self.changed() and not self.git('diff', '--cached', '--name-only'), 'Unexpected changes after commit')
            self.finish_commit(current_head)
            return
        require(self.plan.path.read_bytes() in (before, after), 'Unknown plan transaction state')
        actual = self.fingerprint()
        wanted = dict(transaction['fingerprint'])
        actual.pop(self.plan_name, None)
        wanted.pop(self.plan_name, None)
        require(actual == wanted, 'Prepared candidate changed; manual reconciliation required')
        staged = set(os.fsdecode(v) for v in self.git('diff', '--cached', '--name-only', '-z').split(b'\0') if v)
        require(staged <= set(transaction['paths']), 'Unknown staged paths during recovery')
        for name in staged:
            if name != self.plan_name:
                require(not self.git('--literal-pathspecs', 'diff', '--name-only', '--', name), 'Staged content differs from prepared worktree')
        if self.plan.path.read_bytes() == before:
            atomic(self.plan.path, after, preserve_mode=True)
        self.plan = Plan(self.plan.path)
        if transaction['phase'] == 'commit_preparing':
            try:
                self.verify(self.plan.tasks[identifier])
            except Stop as error:
                raise Stop('rendered_plan_verification_failed', error.detail, 3) from error
            transaction['phase'] = 'rendered_verified'
            self.save()
        self.git('--literal-pathspecs', 'add', '--', *transaction['paths'])
        tree = self.index()
        self.verify_tree_contents(tree)
        if transaction['tree']:
            require(tree == transaction['tree'], 'Prepared index tree changed')
        transaction.update(tree=tree, phase='commit_pending')
        self.state['task_states'][identifier] = 'commit_pending'
        self.save()
        message_path = self.directory / 'commit-message.txt'
        atomic(message_path, transaction['message'].encode())
        self.event('commit_start')
        self.state['execution_in_flight'] = dict(task_id=identifier, argv0='git commit', pid=None, started_at=now())
        self.save()
        result = self.supervisor.run(['git', 'commit', '--file', str(message_path)], self.root, 60,
                                     spawned=lambda pid: self.commit_spawned(pid))
        self.state['execution_in_flight'] = None
        self.save()
        self.supervisor.check()
        if result.code or result.timed_out:
            self.event('commit_failure', exit_code=result.code)
            raise Stop('commit_failed', 'Commit failed; preserve staged work and resume after fixing Git/hook configuration', 3)
        self.recover_commit()

    def commit_spawned(self, pid):
        self.state['execution_in_flight']['pid'] = pid
        self.save()

    def finish_commit(self, sha):
        self.assert_branch()
        transaction = self.state['transaction']
        identifier = transaction['task_id']
        self.plan = Plan(self.plan.path)
        self.verify_tree_contents(sha)
        require(self.content_digest() == transaction['candidate_digest'], 'Committed candidate differs from verified content')
        if identifier not in self.state['completed']:
            self.state['completed'].append(identifier)
            self.state['commits'].append(dict(task_id=identifier, sha=sha, candidate_digest=transaction['candidate_digest']))
        self.state['task_states'][identifier] = 'done'
        self.state.pop('pending_message', None)
        self.state['diagnostics'] = ''
        self.state.update(transaction=None, execution_in_flight=None, current_task=None)
        self.state['failures'] = dict.fromkeys(self.state['failures'], 0)
        self.checkpoint()
        self.event('commit_success', sha=sha)

    def retry(self, error):
        kind = error.reason
        self.state['failures'][kind] += 1
        count = self.state['failures'][kind]
        if count >= 3:
            raise Stop('failure_limit', f'Three {kind} failures without verified progress', 1)
        self.state['retries'][kind] += 1
        self.save()
        self.event('retry', failure_class=kind, count=count)
        until = min(self.supervisor.deadline, time.monotonic() + min(30, 2 ** (count - 1)))
        while time.monotonic() < until:
            self.supervisor.check()
            time.sleep(min(.05, max(0, until - time.monotonic())))
        self.supervisor.check()

    def execute(self):
        self.preflight()
        while len(self.state['completed']) < len(self.plan.tasks):
            self.supervisor.check()
            current = self.state.get('current_task')
            task = self.plan.tasks[current] if current else next((t for t in self.plan.tasks.values()
                   if t['id'] not in self.state['completed'] and set(t['depends_on']) <= set(self.state['completed'])), None)
            if task is None:
                raise Stop('no_ready_task', 'Unfinished graph has no ready task', 3)
            self.current = task['id']
            self.state['current_task'] = self.current
            self.checkpoint()
            diagnostics = self.state.get('diagnostics', '')
            message = self.state.get('pending_message')
            needs_worker = task['kind'] == 'implementation' and message is None or bool(diagnostics)
            try:
                if not needs_worker:
                    self.event('task_start')
                if needs_worker:
                    message = self.invoke(task, diagnostics)
                    if message is None:
                        continue
                    self.state['pending_message'] = message
                    self.state['diagnostics'] = ''
                    self.save()
                candidate = self.verify(task)
                if message is None:
                    message = f'docs: record {task["id"]} verification\n\nSummary:\n- Record plan evidence\n\nRationale:\n- Gate dependent tasks\n\nTests:\n- Run declared verification commands\n'
                self.commit(task, message, candidate)
                self.state.pop('pending_message', None)
                self.state['diagnostics'] = ''
                self.save()
            except Stop as error:
                self.event('task_failure', reason_code=error.reason)
                if error.reason in ('protocol', 'transient_infrastructure', 'verification'):
                    self.state['diagnostics'] = error.detail
                    self.state.pop('pending_message', None)
                    self.retry(error)
                    continue
                raise
        self.phase = 'completed'
        return 'completed', 'all_acceptance_met', 0

    def report(self, status, reason, detail=''):
        elapsed = time.monotonic() - self.started
        state = self.state or {}
        completed = state.get('completed', [])
        blockers = [] if reason == 'all_acceptance_met' else [make_blocker(
            reason, task_id=state.get('current_task') or self.current,
            run_directory=self.directory, plan_path=self.plan.path,
            run_script=BUNDLE / 'scripts/run.py', fallback_source='recovery')]
        summary = dict(schema_version=1, run_id=state.get('run_id'), invocation_id=self.invocation,
                       status=status, reason_code=reason, detail=detail, plan_path=str(self.plan.path),
                       worktree=str(self.root), run_directory=str(self.directory) if self.directory else None,
                       timestamp=now(), elapsed_seconds=elapsed, remaining_seconds=max(0, self.args.max_runtime - elapsed),
                       current_task=state.get('current_task'), phase=self.phase,
                       task_counts=dict(total=len(self.plan.tasks), done=len(completed)),
                       milestone_counts=dict(total=len(self.plan.milestones), done=sum(m['verification_task_id'] in completed for m in self.plan.milestones.values())),
                       completed_task_ids=completed, pending_task_ids=[i for i in self.plan.tasks if i not in completed],
                       commits=state.get('commits', []), iterations=state.get('iterations', []), commands=state.get('commands', []),
                       usage=usage_totals(state.get('iterations', [])),
                       invocation_usage=usage_totals([i for i in state.get('iterations', []) if i['invocation_id'] == self.invocation]),
                       retries=state.get('retries', {}), timeout_counts=state.get('timeout_counts', {}),
                       failure_counts=state.get('failures', {}), task_states=state.get('task_states', {}),
                       cumulative_elapsed_seconds=sum(i.get('elapsed_seconds', 0) for i in state.get('invocations', [])
                                                      if i['id'] != self.invocation) + elapsed,
                       invocation_iteration_count=sum(i['invocation_id'] == self.invocation for i in state.get('iterations', [])),
                       invocations=state.get('invocations', []), integrity_errors=self.integrity_errors,
                       readiness=self.readiness, blockers=blockers,
                       usage_complete=bool(state.get('iterations')) and all(i.get('usage_complete', False) for i in state.get('iterations', [])))
        if self.state and self.directory:
            self.state['last_outcome'] = dict(status=status, reason_code=reason, invocation_id=self.invocation)
            if self.state['invocations'] and self.state['invocations'][-1]['id'] == self.invocation:
                self.state['invocations'][-1].update(ended_at=now(), elapsed_seconds=elapsed, status=status)
            self.save()
            atomic(self.directory / 'summary.json', json.dumps(summary, indent=2).encode())
        self.event('final_status', status=status, reason_code=reason)
        return summary

    def close(self):
        if self.lock is not None:
            os.close(self.lock)

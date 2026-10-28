"""Read-only readiness collection shared by doctor and execution preflight.

Public integration seam for T8:

    collect_readiness(*, plan_path, workspace, gemini, policy, model,
                      approval_mode, resume, supervisor) -> ReadinessReport

The collector never creates state, acquires locks, edits files, evaluates Gemini
policy, or starts a prompt. It returns the same bounded readiness snapshot for a
doctor report or a caller-owned invocation journal.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tomllib
from typing import Any, Callable

from contracts import Plan, Stop, confined, decode

PINNED_GEMINI_VERSION = '0.65.0'
FILE_LIMIT = 1024 * 1024
CHECK_DETAIL_LIMIT = 4096
POLICY_DIRECTORY_LIMIT = 64


@dataclass(frozen=True)
class ReadinessReport:
    """Result returned by the shared, side-effect-free collector."""

    readiness: dict[str, Any]
    blockers: list[dict[str, str]]
    exit_code: int
    reason_code: str


class _CheckFailure(Exception):
    def __init__(self, reason: str, detail: str):
        super().__init__(detail)
        self.reason, self.detail = reason, detail


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _detail(value: object) -> str:
    return str(value)[:CHECK_DETAIL_LIMIT]


def _physical_without_symlinks(value: Path | str) -> Path:
    """Return an absolute physical path, rejecting every symlink component."""
    path = Path(os.path.abspath(os.fspath(value)))
    current = Path(path.anchor)
    for index, part in enumerate(path.parts[1:]):
        current = current / part
        try:
            metadata = current.lstat()
        except FileNotFoundError as error:
            raise _CheckFailure('missing_path', f'Path does not exist: {current}') from error
        except OSError as error:
            raise _CheckFailure('unreadable_path', f'Cannot inspect path: {current}') from error
        if stat.S_ISLNK(metadata.st_mode):
            raise _CheckFailure('symlink_path', f'Symlink path component is not allowed: {current}')
        if index < len(path.parts[1:]) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise _CheckFailure('invalid_path', f'Parent path is not a directory: {current}')
    return path


def _read_regular(path: Path, limit: int = FILE_LIMIT) -> bytes:
    """Read a bounded regular file without following its final symlink."""
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise _CheckFailure('not_regular_file', f'Expected a regular file: {path}')
        if metadata.st_size > limit:
            raise _CheckFailure('file_too_large', f'File exceeds {limit} bytes: {path}')
        with os.fdopen(descriptor, 'rb', closefd=False) as source:
            raw = source.read(limit + 1)
        if len(raw) > limit:
            raise _CheckFailure('file_too_large', f'File exceeds {limit} bytes: {path}')
        return raw
    finally:
        os.close(descriptor)


def validate_policy_file(value: Path | str) -> dict[str, str]:
    """Validate one reviewed TOML file and return its physical path and digest.

    T8 may call this immediately before each provider spawn to detect a changed
    policy. It checks syntax only; it does not evaluate grants or precedence.
    """
    try:
        path = _physical_without_symlinks(value)
        if ',' in str(path):
            raise _CheckFailure('policy_path_comma', 'Policy paths cannot contain commas')
        if path.suffix != '.toml':
            raise _CheckFailure('policy_extension', 'Explicit policy must use a .toml file')
        raw = _read_regular(path)
        text = raw.decode('utf-8')
        tomllib.loads(text)
    except UnicodeError as error:
        raise Stop('invalid_policy', 'Explicit policy must be UTF-8', 2) from error
    except tomllib.TOMLDecodeError as error:
        raise Stop('invalid_policy', f'Explicit policy has invalid TOML: {error}', 2) from error
    except RecursionError as error:
        raise Stop('invalid_policy', 'Explicit policy is too deeply nested to parse safely', 2) from error
    except _CheckFailure as error:
        raise Stop('invalid_policy', error.detail, 2) from error
    except OSError as error:
        raise Stop('invalid_policy', f'Cannot read explicit policy: {error.strerror or error}', 2) from error
    return {'path': str(path), 'sha256': _digest(raw)}


def _observe_file(path: Path) -> dict[str, str | None]:
    """Inventory a conventional config file without retaining its contents."""
    try:
        safe_path = _physical_without_symlinks(path)
        raw = _read_regular(safe_path)
    except _CheckFailure as error:
        state = 'absent' if error.reason == 'missing_path' else 'unreadable'
        return {'path': str(path), 'state': state, 'sha256': None, 'reason_code': error.reason}
    except OSError:
        return {'path': str(path), 'state': 'unreadable', 'sha256': None}
    return {'path': str(path), 'state': 'observed', 'sha256': _digest(raw)}


def _observe_policy_directory(path: Path, check_deadline: Callable[[], None]) -> dict[str, Any]:
    entry: dict[str, Any] = {'path': str(path), 'state': 'absent', 'files': []}
    try:
        safe_path = _physical_without_symlinks(path)
        metadata = safe_path.lstat()
    except _CheckFailure as error:
        if error.reason != 'missing_path':
            entry.update(state='unreadable', reason_code=error.reason)
        return entry
    except OSError:
        entry.update(state='unreadable', reason_code='unreadable_path')
        return entry
    if stat.S_ISLNK(metadata.st_mode):
        entry.update(state='unreadable', reason_code='symlink_path')
        return entry
    if not stat.S_ISDIR(metadata.st_mode):
        entry.update(state='unreadable', reason_code='not_directory')
        return entry
    entry['state'] = 'observed'
    selected: list[Path] = []
    truncated = False
    try:
        with os.scandir(safe_path) as children:
            for index, child in enumerate(children, start=1):
                if index % 32 == 0:
                    check_deadline()
                if not child.name.endswith('.toml'):
                    continue
                selected.append(safe_path / child.name)
                selected.sort(key=lambda item: item.name)
                if len(selected) > POLICY_DIRECTORY_LIMIT:
                    selected.pop()
                    truncated = True
    except OSError:
        entry.update(state='unreadable', reason_code='unreadable_directory')
        return entry
    for child in selected:
        try:
            raw = _read_regular(child)
            state, checksum = 'observed', _digest(raw)
        except _CheckFailure as error:
            state, checksum = 'unreadable', None
        except OSError:
            state, checksum = 'unreadable', None
        entry['files'].append({'path': str(child), 'state': state, 'sha256': checksum})
    if truncated:
        entry['truncated'] = True
    return entry


class _Collector:
    def __init__(self, *, plan_path: Path, workspace: Path | None, gemini: str,
                 policy: Path | None, model: str | None, approval_mode: str | None,
                 resume: Path | None, supervisor: Any):
        self.plan_path = plan_path
        self.expected_workspace = workspace
        self.gemini = gemini
        self.policy = policy
        self.model = model
        self.approval_mode = approval_mode
        self.resume = resume
        self.supervisor = supervisor
        self.checks: list[dict[str, str]] = []
        self.blockers: list[dict[str, str]] = []
        self.limitations = [
            'Authentication, project trust, and effective permission remain unknown without an authorized provider attempt.',
            'A successful --version check proves local executable and version availability only.',
            'Workspace .gemini/policies is disabled in Gemini CLI 0.65.0; observed files are inventory only.',
            'User/workspace config inventory is limited to conventional .gemini paths and does not model policy precedence.',
            'No known local blocker is not permission or authorization for paid use.',
        ]
        self.plan: Plan | None = None
        self.workspace = self.plan_path.parent
        self.git_executable: str | None = None
        self.git_root: Path | None = None
        self.git_dir: Path | None = None
        self.git_version: str | None = None
        self.branch: str | None = None
        self.head: str | None = None
        self.git_status = 'unknown'
        self.git_identity: dict[str, str | None] = {'name': None, 'email': None}
        self.provider_executable: str | None = None
        self.provider_version: str | None = None
        self.skills: list[dict[str, str | None]] = []
        self.selected_policy: dict[str, str] | None = None
        self.policy_sources: list[dict[str, Any]] = []
        self.resume_info: dict[str, Any] = {'status': 'not_requested'}
        self.fatal_reason: str | None = None
        self.terminal_reason: str | None = None
        self.terminal_code: int | None = None

    def _check(self, identifier: str, status: str, reason: str, detail: object = '') -> None:
        entry = {'id': identifier, 'status': status, 'reason_code': reason, 'detail': _detail(detail)}
        self.checks.append(entry)
        if status == 'blocked':
            self.blockers.append({'check_id': identifier, 'reason_code': reason,
                                  'detail': entry['detail']})

    def _fatal(self, reason: str) -> None:
        if self.fatal_reason is None:
            self.fatal_reason = reason

    def _run(self, argv: list[str], cwd: Path, timeout: float = 5.0):
        self.supervisor.check()
        outcome = self.supervisor.run(argv, cwd, timeout)
        self.supervisor.check()
        return outcome

    def _git(self, *args: str, allow_exit_1: bool = False):
        if self.git_executable is None:
            raise _CheckFailure('missing_git', 'Git executable is unavailable')
        try:
            result = self._run([self.git_executable, *args], self.plan_path.parent, 5.0)
        except Stop as error:
            if error.reason in ('interrupted', 'total_deadline', 'cleanup_unconfirmed'):
                raise
            raise _CheckFailure(error.reason, error.detail) from error
        if result.timed_out:
            raise _CheckFailure('git_timeout', 'A bounded local Git query timed out')
        if result.stdout_truncated or result.stderr_truncated:
            raise _CheckFailure('git_output_limit', 'A local Git query exceeded the 1 MiB output bound')
        if result.code and not (allow_exit_1 and result.code == 1):
            raise _CheckFailure('git_query_failed', f'Local Git query failed (exit {result.code})')
        return result

    def _collect_platform(self) -> None:
        supported = sys.version_info >= (3, 12) and sys.platform in ('darwin', 'linux')
        version = sys.version.split()[0]
        self._check('platform', 'pass' if supported else 'blocked',
                    'supported_platform' if supported else 'unsupported_platform',
                    f'{sys.platform}; Python {version}; requires macOS/Linux and Python 3.12+')

    def _collect_plan(self) -> None:
        try:
            self.plan = Plan(self.plan_path)
            self._check('plan', 'pass', 'valid_contract',
                        f'Valid plan {self.plan.data["plan_id"]}; {len(self.plan.tasks)} tasks')
        except Stop as error:
            self._fatal(error.reason)
            self._check('plan', 'blocked', error.reason, error.detail)
        except OSError as error:
            self._fatal('invalid_contract')
            self._check('plan', 'blocked', 'plan_io_error', error.strerror or str(error))

    def _collect_git(self) -> None:
        self.git_executable = shutil.which('git')
        if self.git_executable is None:
            self._check('git_version', 'blocked', 'missing_git', 'Git executable is unavailable')
            self._check('workspace_state', 'blocked', 'missing_git', 'Cannot inspect repository without Git')
            return
        try:
            version = self._git('--version')
            output = version.stdout.decode('utf-8', 'replace').strip()
            match = re.fullmatch(r'git version ([0-9]+(?:\.[0-9]+){1,3})(?:\s+.*)?', output)
            if not match:
                self._check('git_version', 'blocked', 'git_version_unrecognized',
                            'Git --version did not return a supported version string')
                self._check('workspace_state', 'blocked', 'git_version_unrecognized',
                            'Cannot verify the local Git version')
                return
            self.git_version = match.group(1)
            self._check('git_version', 'pass', 'git_version_available', self.git_version)
        except _CheckFailure as error:
            self._check('git_version', 'blocked', error.reason, error.detail)
            self._check('workspace_state', 'blocked', error.reason, error.detail)
            return
        try:
            top = self._git('rev-parse', '--show-toplevel')
        except _CheckFailure as error:
            self.workspace = self.plan_path.parent.resolve()
            self._check('workspace_state', 'blocked', 'not_git_worktree', error.detail)
            return
        try:
            self.git_root = Path(top.stdout.decode('utf-8').strip()).resolve(strict=True)
        except (UnicodeError, OSError) as error:
            self._check('workspace_state', 'blocked', 'git_root_unavailable', str(error))
            return
        self.workspace = self.git_root
        if self.expected_workspace is not None:
            try:
                expected = self.expected_workspace.resolve(strict=True)
            except OSError:
                expected = self.expected_workspace.absolute()
            if expected != self.git_root:
                self._check('workspace_state', 'blocked', 'workspace_identity_mismatch',
                            'Git worktree differs from the caller workspace')
        try:
            git_dir = self._git('rev-parse', '--absolute-git-dir')
            self.git_dir = Path(git_dir.stdout.decode('utf-8').strip()).resolve()
        except (_CheckFailure, UnicodeError, OSError) as error:
            detail = error.detail if isinstance(error, _CheckFailure) else str(error)
            self._check('workspace_state', 'blocked', 'git_directory_unavailable', detail)
        try:
            branch = self._git('symbolic-ref', '--quiet', '--short', 'HEAD')
            self.branch = branch.stdout.decode('utf-8').strip()
            if not self.branch:
                raise _CheckFailure('detached_head', 'Worktree HEAD is detached')
        except (_CheckFailure, UnicodeError) as error:
            reason = error.reason if isinstance(error, _CheckFailure) else 'detached_head'
            detail = error.detail if isinstance(error, _CheckFailure) else 'Worktree branch name is not UTF-8'
            self._check('workspace_state', 'blocked', reason, detail)
        try:
            head = self._git('rev-parse', 'HEAD')
            self.head = head.stdout.decode('ascii').strip()
        except (_CheckFailure, UnicodeError) as error:
            reason = error.reason if isinstance(error, _CheckFailure) else 'git_head_unavailable'
            detail = error.detail if isinstance(error, _CheckFailure) else 'Git HEAD is not ASCII'
            self._check('workspace_state', 'blocked', reason, detail)
        try:
            name = self._git('config', '--get', 'user.name', allow_exit_1=True)
            email = self._git('config', '--get', 'user.email', allow_exit_1=True)
            self.git_identity = {
                'name': name.stdout.decode('utf-8', 'replace').strip()[:512] or None,
                'email': email.stdout.decode('utf-8', 'replace').strip()[:512] or None,
            }
            if self.git_identity['name'] and self.git_identity['email']:
                self._check('git_identity', 'pass', 'git_identity_available', 'Git user name and email are configured')
            else:
                self._check('git_identity', 'blocked', 'missing_git_identity',
                            'Configure repository-local Git user.name and user.email before execution')
        except _CheckFailure as error:
            self._check('git_identity', 'blocked', error.reason, error.detail)
        try:
            status = self._git('--no-optional-locks', '-c', 'core.fsmonitor=false', 'status',
                               '--ignore-submodules=none', '--porcelain=v1',
                               '--untracked-files=normal', '-z')
            self.git_status = 'dirty' if status.stdout else 'clean'
        except _CheckFailure as error:
            self.git_status = 'unknown'
            self._check('workspace_state', 'blocked', error.reason, error.detail)
            return
        if self.git_dir is not None:
            active_operations = [name for name in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD',
                               'rebase-merge', 'rebase-apply', 'BISECT_LOG')
                                 if (self.git_dir / name).exists()]
            if active_operations:
                self._check('workspace_state', 'blocked', 'git_operation_in_progress',
                            'Git operation in progress: ' + ', '.join(active_operations))
        if self.plan_path.is_relative_to(self.git_root):
            plan_name = self.plan_path.relative_to(self.git_root).as_posix()
            try:
                self._git('ls-files', '--error-unmatch', '--', plan_name)
            except _CheckFailure:
                self._check('workspace_state', 'blocked', 'untracked_plan', 'Plan must be tracked in the worktree')
            else:
                try:
                    committed = self._git('show', f'HEAD:{plan_name}')
                    if self.plan is not None and committed.stdout != self.plan.text.encode('utf-8'):
                        self._check('workspace_state', 'blocked', 'plan_not_at_head',
                                    'Plan differs from the version recorded at HEAD')
                except _CheckFailure as error:
                    self._check('workspace_state', 'blocked', error.reason, error.detail)
            if self.plan is not None:
                try:
                    for task in self.plan.tasks.values():
                        for name in task['writable_paths']:
                            confined(self.git_root, name)
                        for command in task['verification']:
                            cwd = confined(self.git_root, command['cwd'])
                            if not cwd.is_dir():
                                raise Stop('invalid_contract', f'Verification cwd is not a directory: {command["cwd"]}')
                except Stop as error:
                    self._fatal('invalid_contract')
                    self._check('plan_paths', 'blocked', error.reason, error.detail)
        else:
            self._check('workspace_state', 'blocked', 'plan_outside_worktree',
                        'Plan must be inside the Git worktree')
        if self.resume is None and self.git_status == 'dirty':
            self._check('workspace_state', 'blocked', 'dirty_worktree',
                        'Fresh execution requires a clean worktree and index')
        if self.git_status != 'unknown' and not any(c['id'] == 'workspace_state' for c in self.checks):
            self._check('workspace_state', 'pass', 'workspace_inspected',
                        'Clean worktree' if self.git_status == 'clean' else 'Dirty worktree selected for resume inspection')

    def _collect_provider(self) -> None:
        executable = shutil.which(self.gemini)
        if executable is None:
            self._check('provider_version', 'blocked', 'missing_gemini',
                        'Gemini CLI executable is unavailable')
            return
        self.provider_executable = str(Path(executable).resolve())
        try:
            outcome = self._run([executable, '--version'], self.workspace, 10.0)
        except Stop as error:
            if error.reason in ('interrupted', 'total_deadline', 'cleanup_unconfirmed'):
                raise
            self._check('provider_version', 'blocked', error.reason, error.detail)
            return
        except OSError as error:
            self._check('provider_version', 'blocked', 'provider_version_failed', error.strerror or str(error))
            return
        if outcome.timed_out:
            self._check('provider_version', 'blocked', 'provider_version_timeout',
                        'Gemini --version exceeded its bounded local timeout')
            return
        if outcome.stdout_truncated or outcome.stderr_truncated:
            self._check('provider_version', 'blocked', 'provider_version_output_limit',
                        'Gemini --version exceeded the 1 MiB output bound')
            return
        output = outcome.stdout.decode('utf-8', 'replace').strip()
        observed = (output if len(output) <= 128 and
                    re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?', output)
                    else None)
        self.provider_version = observed or None
        if outcome.code != 0:
            self._check('provider_version', 'blocked', 'provider_version_failed',
                        f'Gemini --version exited {outcome.code}')
        elif observed != PINNED_GEMINI_VERSION:
            detail = (f'Requires Gemini CLI {PINNED_GEMINI_VERSION}; observed {observed}' if observed
                      else 'Gemini --version did not return a supported version string')
            self._check('provider_version', 'blocked', 'unsupported_gemini_version', detail)
        else:
            self._check('provider_version', 'pass', 'supported_gemini_version', observed)

    def _collect_skills(self) -> None:
        home = Path.home()
        for name in ('exec-plans', 'tdd'):
            candidates = [self.workspace / '.agents/skills' / name / 'SKILL.md',
                          self.workspace / '.gemini/skills' / name / 'SKILL.md',
                          home / '.agents/skills' / name / 'SKILL.md',
                          home / '.gemini/skills' / name / 'SKILL.md']
            selected = None
            unreadable_candidate = None
            for candidate in candidates:
                try:
                    metadata = candidate.stat()
                except FileNotFoundError:
                    if candidate.is_symlink():
                        selected = candidate
                        unreadable_candidate = 'symlink_path'
                        break
                    continue
                except OSError:
                    selected = candidate
                    unreadable_candidate = 'unreadable_skill_dependency'
                    break
                if stat.S_ISREG(metadata.st_mode):
                    selected = candidate
                    break
            if selected is None:
                self.skills.append({'name': name, 'path': None, 'sha256': None})
                self._check('skill_' + name.replace('-', '_'), 'blocked', 'missing_skill_dependency',
                            f'Gemini-visible {name}/SKILL.md is required')
                continue
            record: dict[str, str | None] = {'name': name, 'path': str(selected), 'sha256': None}
            try:
                if unreadable_candidate:
                    raise _CheckFailure(unreadable_candidate, f'Cannot safely read skill file: {selected}')
                raw = _read_regular(selected)
                record['sha256'] = _digest(raw)
                self._check('skill_' + name.replace('-', '_'), 'pass', 'skill_file_readable',
                            f'Read {name}/SKILL.md at {selected}')
            except _CheckFailure as error:
                self._check('skill_' + name.replace('-', '_'), 'blocked', error.reason, error.detail)
            except OSError as error:
                self._check('skill_' + name.replace('-', '_'), 'blocked', 'unreadable_skill_dependency',
                            f'Cannot read {name}/SKILL.md at {selected}: {error.strerror or error}')
            self.skills.append(record)

    def _collect_policy(self) -> None:
        if self.policy is None:
            self._check('explicit_policy', 'unknown', 'no_explicit_policy',
                        'No reviewed --policy file was selected; inherited provider policy is not evaluated')
            return
        try:
            self.selected_policy = validate_policy_file(self.policy)
        except Stop as error:
            self._fatal('invalid_policy')
            self._check('explicit_policy', 'blocked', 'invalid_policy', error.detail)
        else:
            self._check('explicit_policy', 'pass', 'explicit_policy_syntax_valid',
                        f'Validated TOML syntax and SHA-256 for {self.selected_policy["path"]}')

    def _collect_policy_sources(self) -> None:
        for scope, base in (('workspace', self.workspace), ('user', Path.home())):
            gemini = base / '.gemini'
            setting = _observe_file(gemini / 'settings.json')
            policy_dir = _observe_policy_directory(gemini / 'policies', self.supervisor.check)
            self.policy_sources.append({'scope': scope, 'kind': 'settings', **setting})
            self.policy_sources.append({'scope': scope, 'kind': 'policy_directory', **policy_dir})
        self._check('workspace_policy', 'unknown', 'workspace_policy_disabled',
                    'Workspace .gemini/policies discovery is disabled in Gemini CLI 0.65.0')

    def _resume_fingerprint(self) -> dict[str, str]:
        if self.git_root is None:
            raise _CheckFailure('not_git_worktree', 'Cannot compare journal files without a Git worktree')
        changed = self._git('diff', '--ignore-submodules=none', '--no-renames', '--name-only', '-z', 'HEAD', '--')
        untracked = self._git('ls-files', '--others', '--exclude-standard', '-z')
        names = {os.fsdecode(value) for value in changed.stdout.split(b'\0') + untracked.stdout.split(b'\0') if value}
        current: dict[str, str] = {}
        for name in sorted(names):
            try:
                path = confined(self.git_root, name)
            except Stop as error:
                raise _CheckFailure('resume_path_escape', error.detail) from error
            try:
                metadata = path.lstat()
            except FileNotFoundError:
                current[name] = 'deleted'
                continue
            except OSError as error:
                raise _CheckFailure('resume_file_unreadable', f'Cannot inspect changed file: {name}') from error
            if stat.S_ISLNK(metadata.st_mode):
                value = 'symlink:' + _digest(os.fsencode(os.readlink(path)))
            elif stat.S_ISREG(metadata.st_mode):
                try:
                    raw = _read_regular(path, limit=FILE_LIMIT)
                except (_CheckFailure, OSError) as error:
                    raise _CheckFailure('resume_file_unreadable', f'Cannot inspect changed file: {name}') from error
                executable = stat.S_IMODE(metadata.st_mode) & 0o111
                value = f'{executable}:' + _digest(raw)
            else:
                raise _CheckFailure('resume_file_unsupported', f'Changed path is not an ordinary file: {name}')
            current[name] = value
        return current

    def _collect_resume(self) -> None:
        if self.resume is None:
            self.resume_info = {'status': 'not_requested'}
            self._check('resume', 'unknown', 'resume_not_requested', 'Fresh-run readiness inspection')
            return
        try:
            directory = _physical_without_symlinks(self.resume)
            metadata = directory.lstat()
            if not stat.S_ISDIR(metadata.st_mode):
                raise _CheckFailure('invalid_resume_state', 'Resume path must be a directory')
            if metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) & 0o077:
                raise _CheckFailure('invalid_resume_state', 'Resume directory must be owner-only and owned by the current user')
            state_path = directory / 'state.json'
            state = decode(_read_regular(state_path))
            state_meta = state_path.stat()
            if state_meta.st_uid != os.getuid() or stat.S_IMODE(state_meta.st_mode) & 0o077:
                raise _CheckFailure('invalid_resume_state', 'Resume journal must be owner-only and owned by the current user')
            if not isinstance(state, dict) or state.get('schema_version') != 1:
                raise _CheckFailure('invalid_resume_state', 'Resume journal schema is not recognized')
            for field in ('invocations', 'iterations', 'commands', 'completed', 'commits'):
                if not isinstance(state.get(field), list):
                    raise _CheckFailure('invalid_resume_state', f'Resume journal field {field} is invalid')
            for field in ('task_states', 'evidence', 'fingerprint'):
                if not isinstance(state.get(field), dict):
                    raise _CheckFailure('invalid_resume_state', f'Resume journal field {field} is invalid')
            if self.plan is None or self.git_root is None or self.git_dir is None:
                raise _CheckFailure('resume_identity_unavailable', 'Plan or Git workspace identity is unavailable')
            identity = {
                'worktree': str(self.git_root),
                'git_dir': str(self.git_dir),
                'branch': self.branch,
                'plan_path': str(self.plan_path),
                'plan_id': self.plan.data['plan_id'],
                'contract_hash': self.plan.immutable_hash(),
                'run_id': directory.name,
            }
            if any(state.get(field) != value for field, value in identity.items()):
                raise _CheckFailure('resume_identity_mismatch', 'Resume journal does not belong to this plan and worktree')
            in_flight = state.get('execution_in_flight') is not None
            transaction = state.get('transaction')
            if transaction is not None:
                transaction_fields = ('task_id', 'phase', 'parent', 'before_plan', 'after_plan',
                                      'fingerprint', 'index', 'paths', 'message', 'message_digest',
                                      'candidate_digest', 'tree')
                task_id = transaction.get('task_id') if isinstance(transaction, dict) else None
                if (not isinstance(transaction, dict) or
                        not set(transaction_fields) <= transaction.keys() or
                        not isinstance(task_id, str) or task_id not in self.plan.tasks or
                        transaction.get('phase') not in ('commit_preparing', 'rendered_verified', 'commit_pending')):
                    raise _CheckFailure('invalid_resume_state', 'Resume commit transaction is not recognized')
            actual_head = self.head
            if not in_flight and transaction is None:
                if state.get('expected_head') != actual_head:
                    raise _CheckFailure('resume_head_mismatch', 'Worktree HEAD differs from the recorded resume HEAD')
                if self._resume_fingerprint() != state['fingerprint']:
                    raise _CheckFailure('resume_fingerprint_mismatch', 'Worktree files differ from the recorded resume fingerprint')
                staged = self._git('diff', '--cached', '--quiet', 'HEAD', allow_exit_1=True)
                if staged.code != 0:
                    raise _CheckFailure('resume_index_mismatch', 'Index differs from the recorded committed HEAD')
            self.resume_info = {'status': 'recognized', 'path': str(directory), 'run_id': state.get('run_id'),
                                'current_task': state.get('current_task'), 'in_flight': in_flight,
                                'transaction_pending': transaction is not None}
            if in_flight:
                self._check('resume', 'blocked', 'unclean_execution_requires_reconciliation',
                            'A prior child may still be active; inspect and reconcile before resuming')
            else:
                self._check('resume', 'pass', 'resume_recognized',
                            'Read-only resume identity and journal inspection succeeded')
        except Stop as error:
            if error.reason in ('interrupted', 'total_deadline', 'cleanup_unconfirmed'):
                raise
            self._fatal('invalid_resume_state')
            self.resume_info = {'status': 'invalid'}
            self._check('resume', 'blocked', 'invalid_resume_state', error.detail)
        except _CheckFailure as error:
            if error.reason == 'resume_identity_mismatch' or error.reason.startswith('resume_') and error.reason != 'invalid_resume_state':
                self.resume_info = {'status': 'blocked', 'path': str(self.resume), 'reason_code': error.reason}
                self._check('resume', 'blocked', error.reason, error.detail)
            else:
                self._fatal('invalid_resume_state')
                self.resume_info = {'status': 'invalid', 'path': str(self.resume)}
                self._check('resume', 'blocked', 'invalid_resume_state', error.detail)
        except (OSError, UnicodeError, ValueError, RecursionError) as error:
            self._fatal('invalid_resume_state')
            self.resume_info = {'status': 'invalid', 'path': str(self.resume)}
            self._check('resume', 'blocked', 'invalid_resume_state', error.strerror if isinstance(error, OSError) else str(error))

    def _collect_unknowns(self) -> None:
        self._check('authentication', 'unknown', 'provider_attempt_required',
                    'Authentication cannot be established by local inspection')
        self._check('trust', 'unknown', 'provider_attempt_required',
                    'Workspace trust cannot be established by local inspection')
        self._check('effective_permission', 'unknown', 'provider_attempt_required',
                    'Effective permissions cannot be established from readable policy files')

    def _report(self) -> ReadinessReport:
        blocked = bool(self.blockers)
        readiness_status = 'blocked' if blocked or self.terminal_reason else 'unknown'
        can_attempt = not blocked and self.terminal_reason is None
        plan_provenance: dict[str, Any] = {'path': str(self.plan_path), 'plan_id': None, 'contract_hash': None,
                                           'sha256': None}
        if self.plan is not None:
            plan_provenance.update(plan_id=self.plan.data['plan_id'],
                                   contract_hash=self.plan.immutable_hash(),
                                   sha256=_digest(self.plan.text.encode('utf-8')))
        provenance = {
            'host': {'platform': sys.platform, 'python_version': sys.version.split()[0]},
            'git': {'executable': self.git_executable, 'version': self.git_version},
            'provider': {'executable': self.provider_executable or self.gemini,
                         'version': self.provider_version},
            'plan': plan_provenance,
            'workspace': {'root': str(self.git_root) if self.git_root else str(self.workspace),
                          'git_dir': str(self.git_dir) if self.git_dir else None,
                          'branch': self.branch, 'head': self.head, 'status': self.git_status,
                          'identity': self.git_identity},
            'skills': self.skills,
            'selected_policy': self.selected_policy,
            'discovered_policy_sources': self.policy_sources,
            'requested': {'model': self.model, 'approval_mode': self.approval_mode},
            'resume': self.resume_info,
        }
        readiness = {'checked_at': _timestamp(), 'status': readiness_status,
                     'can_attempt': can_attempt, 'checks': self.checks[:128],
                     'provenance': provenance, 'limitations': self.limitations[:32]}
        if self.terminal_reason:
            exit_code = self.terminal_code or 3
            reason = self.terminal_reason
        elif self.fatal_reason:
            exit_code = 2
            reason = self.fatal_reason
        elif blocked:
            exit_code = 3
            reason = 'doctor_blocked'
        else:
            exit_code = 0
            reason = 'doctor_complete'
        return ReadinessReport(readiness, self.blockers[:128], exit_code, reason)

    def collect(self) -> ReadinessReport:
        try:
            self.supervisor.check()
            self._collect_platform()
            self._collect_plan()
            self._collect_git()
            self._collect_provider()
            self._collect_skills()
            self._collect_policy()
            self._collect_policy_sources()
            self._collect_resume()
            self._collect_unknowns()
            self.supervisor.check()
        except Stop as error:
            self.terminal_reason, self.terminal_code = error.reason, error.code
            self._check('diagnosis', 'blocked', error.reason, error.detail)
        except (OSError, ValueError, RecursionError) as error:
            self.terminal_reason, self.terminal_code = 'doctor_inspection_error', 3
            detail = error.strerror if isinstance(error, OSError) else str(error)
            self._check('diagnosis', 'blocked', 'doctor_inspection_error', detail)
        return self._report()


def collect_readiness(*, plan_path: Path, workspace: Path | None, gemini: str,
                      policy: Path | None, model: str | None, approval_mode: str | None,
                      resume: Path | None, supervisor: Any) -> ReadinessReport:
    """Collect a bounded local readiness snapshot without changing any state.

    T8 can persist ``result.readiness`` in its invocation journal and block on
    ``result.exit_code`` before a new provider attempt. The collector accepts a
    valid plan path, an optional expected worktree root, and the same supervisor
    the caller uses for deadline and cancellation handling.
    """
    return _Collector(plan_path=plan_path, workspace=workspace, gemini=gemini, policy=policy,
                      model=model, approval_mode=approval_mode, resume=resume,
                      supervisor=supervisor).collect()

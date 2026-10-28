#!/usr/bin/env python3
"""Prepare, run, and collect evidence from a disposable ExecPlan qualification."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import signal
import stat
import subprocess
import sys
import time

try:
    import fcntl
except ImportError:  # Native Windows supports setup only; the runner is POSIX-only.
    fcntl = None


SCHEMA_VERSION = 1
FIXTURE_RELATIVE_PATH = Path('evals/fixtures/live-qualification.md')


class QualificationError(Exception):
    def __init__(self, detail: str, *, code: int = 2, reason_code: str = 'qualification_error'):
        super().__init__(detail)
        self.code = code
        self.reason_code = reason_code


class BlockedError(QualificationError):
    def __init__(self, detail: str, *, reason_code: str = 'qualification_blocked'):
        super().__init__(detail, code=3, reason_code=reason_code)


class ChildResult:
    def __init__(self, code: int, *, timed_out: bool = False, interrupted: int | None = None,
                 cleanup_error: str | None = None):
        self.code = code
        self.timed_out = timed_out
        self.interrupted = interrupted
        self.cleanup_error = cleanup_error


def _bundle_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _git_environment() -> dict[str, str]:
    env = dict(os.environ)
    for key in list(env):
        if key.startswith('GIT_'):
            env.pop(key, None)
    env['GIT_CONFIG_GLOBAL'] = os.devnull
    env['GIT_CONFIG_NOSYSTEM'] = '1'
    env['GIT_TERMINAL_PROMPT'] = '0'
    return env


def _git(project: Path, *args: str) -> str:
    try:
        result = subprocess.run(['git', '-C', str(project), *args], cwd=project,
                                env=_git_environment(), stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, timeout=10, check=False)
    except subprocess.TimeoutExpired as error:
        raise QualificationError(f'Git {args[0]} exceeded its 10-second bound') from error
    if result.returncode:
        detail = result.stderr.strip() or f'Git exited {result.returncode}'
        raise QualificationError(f'Git {args[0]} failed: {detail}')
    return result.stdout.strip()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _bundle_digest(bundle: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(bundle.rglob('*'), key=lambda item: item.relative_to(bundle).as_posix()):
        relative = path.relative_to(bundle)
        if '__pycache__' in relative.parts or path.suffix == '.pyc':
            continue
        if path.is_symlink():
            raise QualificationError(f'Bundle contains a symlink: {relative.as_posix()}')
        if not path.is_file():
            continue
        name = relative.as_posix().encode('utf-8')
        digest.update(len(name).to_bytes(8, 'big'))
        digest.update(name)
        with path.open('rb') as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b''):
                digest.update(chunk)
    return digest.hexdigest()


def _write_json_exclusive(path: Path, value: object, mode: int = 0o600) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, mode)
    with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as output:
        json.dump(value, output, ensure_ascii=False, indent=2, sort_keys=True)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())


def _write_bytes_exclusive(path: Path, payload: bytes, mode: int = 0o600) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, mode)
    with os.fdopen(descriptor, 'wb') as output:
        output.write(payload)
        output.flush()
        os.fsync(output.fileno())


def _atomic_manifest(root: Path, manifest: dict[str, object]) -> None:
    path = root / 'manifest.json'
    if path.is_symlink() or not path.is_file():
        raise QualificationError('Owned manifest is missing or is a symlink')
    temporary = root / f'.manifest.json.pending-{os.getpid()}-{time.time_ns()}'
    _write_json_exclusive(temporary, manifest)
    os.replace(temporary, path)
    path.chmod(0o600)
    descriptor = os.open(root, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def _physical_root(value: str) -> Path:
    raw = Path(value)
    if not raw.is_absolute():
        raise QualificationError('--root must be an absolute path')
    try:
        root = raw.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise QualificationError(f'Qualification root is unavailable: {raw}: {error}') from error
    if not root.is_dir():
        raise QualificationError(f'Qualification root is not a directory: {root}')
    return root


def _safe_relative(value: object, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise QualificationError(f'Manifest {label} must be a nonempty relative path')
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ('', '.', '..') for part in path.parts):
        raise QualificationError(f'Manifest {label} escapes the owned root')
    return path


def _owned_path(root: Path, relative: str, *, must_exist: bool = False) -> Path:
    parsed = _safe_relative(relative, 'artifact path')
    candidate = root.joinpath(*parsed.parts)
    current = root
    for part in parsed.parts:
        current = current / part
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            if must_exist:
                raise QualificationError(f'Owned artifact is missing: {relative}')
            continue
        except OSError as error:
            raise QualificationError(f'Cannot inspect owned artifact {relative}: {error}') from error
        if stat.S_ISLNK(mode):
            raise QualificationError(f'Owned artifact path contains a symlink: {relative}')
    try:
        resolved = candidate.resolve(strict=must_exist)
    except OSError as error:
        raise QualificationError(f'Cannot resolve owned artifact {relative}: {error}') from error
    if not resolved.is_relative_to(root):
        raise QualificationError(f'Owned artifact escapes the root: {relative}')
    return candidate


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise QualificationError(f'Manifest repeats key {key!r}')
        result[key] = value
    return result


def _expected_owned_paths(manifest: dict[str, object]) -> set[str]:
    expected = {
        'manifest.json', 'project', 'project/.git', 'project/ExecPlan.md',
        'evidence', 'evidence/attempts', 'evidence/collections', 'evidence/run.lock',
    }
    attempts = manifest.get('attempts')
    collections = manifest.get('collections')
    if not isinstance(attempts, list) or not isinstance(collections, list):
        raise QualificationError('Manifest attempt and collection ledgers must be arrays')
    seen_numbers: set[int] = set()
    seen_attempt_paths: set[str] = set()
    seen_run_paths: set[str] = set()
    attempt_fields = {
        'number', 'attempt_path', 'run_directory', 'status', 'started_at', 'finished_at',
        'doctor_report', 'doctor_stderr', 'runner_summary', 'runner_progress',
        'runner_started', 'exit_code', 'runner_status', 'reason_code',
    }
    for attempt in attempts:
        if not isinstance(attempt, dict):
            raise QualificationError('Manifest contains a malformed attempt record')
        if set(attempt) != attempt_fields:
            raise QualificationError('Manifest attempt record has unknown or missing fields')
        number = attempt.get('number')
        if type(number) is not int or number < 1 or number in seen_numbers:
            raise QualificationError('Manifest contains an invalid or duplicate attempt number')
        seen_numbers.add(number)
        attempt_path = _safe_relative(attempt.get('attempt_path'), 'attempt path').as_posix()
        if attempt_path != f'evidence/attempts/attempt-{number:04d}' or attempt_path in seen_attempt_paths:
            raise QualificationError('Manifest attempt path does not match its number')
        seen_attempt_paths.add(attempt_path)
        run_path = _safe_relative(attempt.get('run_directory'), 'run directory').as_posix()
        if run_path != f'{attempt_path}/runner-state' and run_path not in seen_run_paths:
            raise QualificationError('Manifest resume target is not an earlier owned run directory')
        if type(attempt.get('runner_started')) is not bool:
            raise QualificationError('Manifest runner_started value must be a boolean')
        if attempt.get('exit_code') is not None and type(attempt.get('exit_code')) is not int:
            raise QualificationError('Manifest exit code must be an integer or null')
        if not isinstance(attempt.get('status'), str):
            raise QualificationError('Manifest attempt status must be a string')
        if not isinstance(attempt.get('started_at'), str):
            raise QualificationError('Manifest attempt start time must be a string')
        if attempt.get('finished_at') is not None and not isinstance(attempt.get('finished_at'), str):
            raise QualificationError('Manifest attempt finish time must be a string or null')
        if attempt.get('runner_status') is not None and not isinstance(attempt.get('runner_status'), str):
            raise QualificationError('Manifest runner status must be a string or null')
        if attempt.get('reason_code') is not None and not isinstance(attempt.get('reason_code'), str):
            raise QualificationError('Manifest reason code must be a string or null')
        seen_run_paths.add(run_path)
        expected.add(attempt_path)
        expected.update(f'{attempt_path}/{name}' for name in (
            'doctor.json', 'doctor-stderr.log', 'runner-summary.json', 'runner-progress.jsonl'))
        expected.add(run_path)
        for field, filename in (
            ('doctor_report', 'doctor.json'), ('doctor_stderr', 'doctor-stderr.log'),
            ('runner_summary', 'runner-summary.json'), ('runner_progress', 'runner-progress.jsonl'),
        ):
            artifact = _safe_relative(attempt.get(field), field).as_posix()
            if artifact != f'{attempt_path}/{filename}':
                raise QualificationError(f'Manifest {field} does not match its owned report path')
            expected.add(artifact)
    seen_collection_numbers: set[int] = set()
    seen_collection_paths: set[str] = set()
    for collection in collections:
        if not isinstance(collection, dict):
            raise QualificationError('Manifest contains a malformed collection record')
        if set(collection) != {'number', 'path', 'created_at'}:
            raise QualificationError('Manifest collection record has unknown or missing fields')
        number = collection.get('number')
        if type(number) is not int or number < 1 or number in seen_collection_numbers:
            raise QualificationError('Manifest contains an invalid or duplicate collection number')
        seen_collection_numbers.add(number)
        path = _safe_relative(collection.get('path'), 'collection path').as_posix()
        if path != f'evidence/collections/collection-{number:04d}.json' or path in seen_collection_paths:
            raise QualificationError('Manifest collection path does not match its number')
        if not isinstance(collection.get('created_at'), str):
            raise QualificationError('Manifest collection time must be a string')
        seen_collection_paths.add(path)
        expected.add(path)
    return expected


def _validate_evidence_tree(root: Path, manifest: dict[str, object]) -> None:
    evidence = _owned_path(root, 'evidence', must_exist=True)
    attempts_dir = _owned_path(root, 'evidence/attempts', must_exist=True)
    collections_dir = _owned_path(root, 'evidence/collections', must_exist=True)
    lock = _owned_path(root, 'evidence/run.lock', must_exist=True)
    if not evidence.is_dir() or not attempts_dir.is_dir() or not collections_dir.is_dir():
        raise QualificationError('Owned evidence directories have an invalid type')
    if not lock.is_file():
        raise QualificationError('Owned run lock has an invalid type')
    if {path.name for path in evidence.iterdir()} != {'attempts', 'collections', 'run.lock'}:
        raise QualificationError('Evidence root contains an unowned path')

    attempt_records = manifest['attempts']
    expected_attempt_names = {Path(record['attempt_path']).name for record in attempt_records}
    actual_attempt_names = {path.name for path in attempts_dir.iterdir()}
    if not actual_attempt_names <= expected_attempt_names:
        raise QualificationError('Attempt directory contents do not match the owner manifest')
    for record in attempt_records:
        attempt_path = _owned_path(root, record['attempt_path'])
        if not attempt_path.exists():
            continue
        if not attempt_path.is_dir():
            raise QualificationError(f"Owned attempt is not a directory: {record['attempt_path']}")
        expected_names = {'doctor.json', 'doctor-stderr.log', 'runner-summary.json',
                          'runner-progress.jsonl'}
        run_path = _owned_path(root, record['run_directory'])
        if run_path.parent == attempt_path:
            expected_names.add(run_path.name)
        actual_names = {path.name for path in attempt_path.iterdir()}
        if not actual_names <= expected_names:
            raise QualificationError(f"Unexpected evidence in {record['attempt_path']}")
        for path in attempt_path.iterdir():
            if path.is_symlink():
                raise QualificationError(f'Attempt evidence is a symlink: {path.relative_to(root)}')
            if path.name in ('doctor.json', 'doctor-stderr.log', 'runner-summary.json',
                             'runner-progress.jsonl') and not path.is_file():
                raise QualificationError(f'Attempt report has an invalid type: {path.relative_to(root)}')
        if run_path.exists():
            if not run_path.is_dir():
                raise QualificationError(f'Run state path is not a directory: {run_path.relative_to(root)}')
            for child in run_path.rglob('*'):
                if child.is_symlink():
                    raise QualificationError(f'Run state contains a symlink: {child.relative_to(root)}')

    collection_records = manifest['collections']
    expected_collection_names = {Path(record['path']).name for record in collection_records}
    actual_collection_names = {path.name for path in collections_dir.iterdir()}
    if not actual_collection_names <= expected_collection_names:
        raise QualificationError('Collection files do not match the owner manifest')
    for path in collections_dir.iterdir():
        if path.is_symlink() or not path.is_file():
            raise QualificationError(f'Collection evidence has an invalid type: {path.name}')


def _load_root(root_value: str) -> tuple[Path, dict[str, object]]:
    root = _physical_root(root_value)
    if os.name != 'nt' and root.stat().st_mode & 0o077:
        raise QualificationError('Qualification root must be readable only by its owner')
    if {path.name for path in root.iterdir()} != {'manifest.json', 'project', 'evidence'}:
        raise QualificationError('Qualification root contains an unowned path')
    manifest_path = _owned_path(root, 'manifest.json', must_exist=True)
    if not manifest_path.is_file():
        raise QualificationError('Owned manifest is not a regular file')
    if os.name != 'nt' and manifest_path.stat().st_mode & 0o077:
        raise QualificationError('Owned manifest must be readable only by its owner')
    if manifest_path.stat().st_size > 1024 * 1024:
        raise QualificationError('Owned manifest exceeds the 1 MiB limit')
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'),
                              object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise QualificationError(f'Owned manifest is malformed or unreadable: {error}') from error
    manifest_fields = {'schema_version', 'root', 'project', 'baseline_commit', 'bundle',
                       'fixture', 'owned_artifact_paths', 'attempts', 'collections'}
    if (not isinstance(manifest, dict) or manifest.get('schema_version') != SCHEMA_VERSION
            or set(manifest) != manifest_fields):
        raise QualificationError('Owned manifest has an unsupported schema')
    if manifest.get('root') != str(root):
        raise QualificationError('Manifest belongs to a different physical root')
    if manifest.get('project') != 'project':
        raise QualificationError('Manifest project path is invalid')
    baseline = manifest.get('baseline_commit')
    if not isinstance(baseline, str) or len(baseline) not in (40, 64) or any(c not in '0123456789abcdef' for c in baseline):
        raise QualificationError('Manifest baseline commit is malformed')
    for field in ('bundle', 'fixture'):
        value = manifest.get(field)
        if (not isinstance(value, dict) or set(value) != {'path', 'sha256'}
                or not isinstance(value.get('sha256'), str)
                or len(value['sha256']) != 64
                or any(char not in '0123456789abcdef' for char in value['sha256'])):
            raise QualificationError(f'Manifest {field} digest is malformed')
        if not isinstance(value.get('path'), str):
            raise QualificationError(f'Manifest {field} path is malformed')
    if not Path(manifest['bundle']['path']).is_absolute():
        raise QualificationError('Manifest bundle path must be absolute')
    if manifest['fixture']['path'] != FIXTURE_RELATIVE_PATH.as_posix():
        raise QualificationError('Manifest fixture path is invalid')
    owned = manifest.get('owned_artifact_paths')
    if not isinstance(owned, list) or any(not isinstance(item, str) for item in owned):
        raise QualificationError('Manifest owned artifact paths are malformed')
    if len(set(owned)) != len(owned) or set(owned) != _expected_owned_paths(manifest):
        raise QualificationError('Manifest owned artifact paths do not match its ledger')
    for rel in owned:
        _owned_path(root, rel)
    for rel, kind in (('project', 'directory'), ('project/.git', 'directory'),
                      ('project/ExecPlan.md', 'file'), ('evidence', 'directory')):
        path = _owned_path(root, rel, must_exist=True)
        if (kind == 'directory' and not path.is_dir()) or (kind == 'file' and not path.is_file()):
            raise QualificationError(f'Owned path has an invalid type: {rel}')
    _validate_evidence_tree(root, manifest)
    return root, manifest


@contextmanager
def _run_lock(root: Path):
    if fcntl is None:
        raise QualificationError('Run and collect are supported on macOS and Linux only')
    path = _owned_path(root, 'evidence/run.lock', must_exist=True)
    flags = os.O_RDWR
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise BlockedError('Another qualification operation is active for this root',
                               reason_code='concurrent_run') from error
        yield
    finally:
        os.close(descriptor)


def _add_owned_paths(manifest: dict[str, object]) -> None:
    manifest['owned_artifact_paths'] = sorted(_expected_owned_paths(manifest))


def _attempt_number(manifest: dict[str, object]) -> int:
    attempts = manifest['attempts']
    return max((record['number'] for record in attempts), default=0) + 1


def _resume_target(root: Path, manifest: dict[str, object], value: str | None) -> tuple[str | None, str | None]:
    existing: set[str] = set()
    for attempt in manifest['attempts']:
        relative = attempt['run_directory']
        path = _owned_path(root, relative)
        if path.exists():
            if not path.is_dir():
                raise QualificationError(f'Recorded run state is not a directory: {relative}')
            existing.add(relative)
    if len(existing) > 1:
        raise QualificationError('Manifest records more than one run with state; inspect this root')
    if value is None:
        if existing:
            relative = next(iter(existing))
            absolute = str(_owned_path(root, relative, must_exist=True).resolve(strict=True))
            raise BlockedError(f'Run state exists; resume this same run explicitly with --resume {absolute}',
                               reason_code='explicit_resume_required')
        return None, None
    if not Path(value).is_absolute():
        raise QualificationError('--resume must be an absolute run directory path')
    target = Path(value).resolve(strict=True)
    if not target.is_dir() or not target.is_relative_to(root):
        raise QualificationError('--resume must name an existing run directory owned by this root')
    matches = {attempt['run_directory'] for attempt in manifest['attempts']
               if _owned_path(root, attempt['run_directory']).resolve(strict=False) == target}
    if len(matches) != 1 or not existing or target != _owned_path(root, next(iter(existing)), must_exist=True).resolve(strict=True):
        raise QualificationError('--resume must name the same run directory recorded by this root')
    return next(iter(matches)), str(target)


def _seconds(remaining: float) -> str:
    if remaining <= 0:
        return '0.001'
    return f'{remaining:.3f}'


def _child_environment() -> dict[str, str]:
    env = _git_environment()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


_caught_signal: int | None = None


@contextmanager
def _catch_signals():
    global _caught_signal
    _caught_signal = None
    previous: dict[int, object] = {}

    def handle(signum, _frame):
        global _caught_signal
        if _caught_signal is None:
            _caught_signal = signum

    for signum in (signal.SIGINT, signal.SIGTERM):
        previous[signum] = signal.signal(signum, handle)
    try:
        yield
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)
        _caught_signal = None


def _active_group(pgid: int) -> bool:
    result = subprocess.run(['/bin/ps', '-axo', 'pgid=,stat='], stdin=subprocess.DEVNULL,
                            capture_output=True, text=True, timeout=2, check=False)
    if result.returncode:
        raise QualificationError(f'Cannot inspect child process group {pgid}: {result.stderr.strip()}')
    for line in result.stdout.splitlines():
        fields = line.split(None, 1)
        if len(fields) == 2 and fields[0].isdigit() and int(fields[0]) == pgid:
            if not fields[1].startswith('Z'):
                return True
    return False


def _signal_group(pgid: int, signum: int) -> None:
    try:
        os.killpg(pgid, signum)
    except ProcessLookupError:
        pass


def _stop_group(pgid: int, child: subprocess.Popen[bytes], signum: int) -> str | None:
    _signal_group(pgid, signum)
    graceful_until = time.monotonic() + 5
    while time.monotonic() < graceful_until:
        if not _active_group(pgid):
            break
        time.sleep(0.05)
    try:
        active = _active_group(pgid)
    except (OSError, subprocess.SubprocessError, QualificationError) as error:
        active = True
        inspect_error = str(error)
    else:
        inspect_error = None
    if active:
        _signal_group(pgid, signal.SIGKILL)
        kill_until = time.monotonic() + 2
        while time.monotonic() < kill_until:
            try:
                if not _active_group(pgid):
                    active = False
                    break
            except (OSError, subprocess.SubprocessError, QualificationError) as error:
                inspect_error = str(error)
                break
            time.sleep(0.05)
    try:
        child.wait(timeout=2)
    except subprocess.TimeoutExpired:
        return 'Runner leader did not exit after bounded process-group cleanup'
    if active:
        return inspect_error or 'Runner descendants remain active after bounded process-group cleanup'
    return None


def _supervised_child(root: Path, argv: list[str], cwd: Path, stdout_path: Path,
                      stderr_path: Path, deadline: float) -> ChildResult:
    for path in (stdout_path, stderr_path):
        _owned_path(root, path.relative_to(root).as_posix())
        _write_bytes_exclusive(path, b'')
    with stdout_path.open('ab') as stdout, stderr_path.open('ab') as stderr:
        try:
            child = subprocess.Popen(argv, cwd=cwd, env=_child_environment(),
                                     stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                     start_new_session=True, close_fds=True)
        except OSError as error:
            raise QualificationError(f'Could not start the foreground runner: {error}') from error
        while child.poll() is None:
            if _caught_signal is not None:
                signum = _caught_signal
                cleanup = _stop_group(child.pid, child, signum)
                return ChildResult(128 + signum, interrupted=signum, cleanup_error=cleanup)
            if time.monotonic() >= deadline:
                cleanup = _stop_group(child.pid, child, signal.SIGTERM)
                return ChildResult(124, timed_out=True, cleanup_error=cleanup)
            time.sleep(0.05)
        code = child.wait()
        if code < 0:
            code = 128 + abs(code)
        try:
            has_descendants = _active_group(child.pid)
        except (OSError, subprocess.SubprocessError, QualificationError) as error:
            return ChildResult(code, cleanup_error=f'Could not confirm runner cleanup: {error}')
        if has_descendants:
            cleanup = _stop_group(child.pid, child, signal.SIGTERM)
            return ChildResult(code, cleanup_error=cleanup or 'Runner exited with a surviving descendant')
        return ChildResult(code)


def _read_json(path: Path) -> dict[str, object] | None:
    if not path.is_file() or path.stat().st_size > 1024 * 1024:
        return None
    try:
        value = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError, QualificationError):
        return None
    return value if isinstance(value, dict) else None


def _optional_args(args: argparse.Namespace) -> list[str]:
    result: list[str] = []
    for flag, value in (('--policy', args.policy), ('--gemini', args.gemini), ('--model', args.model)):
        if value is not None:
            result.extend((flag, value))
    return result


def _run_qualification(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    started = time.monotonic()
    deadline = started + 600
    initial_root = _physical_root(args.root)
    with _run_lock(initial_root):
        root, manifest = _load_root(args.root)
        project = _owned_path(root, 'project', must_exist=True)
        plan = _owned_path(root, 'project/ExecPlan.md', must_exist=True)
        if plan.is_symlink() or not plan.is_file():
            raise QualificationError('Owned ExecPlan is missing or is a symlink')
        if Path(_git(project, 'rev-parse', '--show-toplevel')).resolve(strict=True) != project.resolve(strict=True):
            raise QualificationError('Project Git root does not match the owned project directory')

        resume_relative, resume_absolute = _resume_target(root, manifest, args.resume)
        if resume_relative is None:
            head = _git(project, 'rev-parse', 'HEAD')
            status = _git(project, 'status', '--porcelain', '--untracked-files=all')
            if head != manifest['baseline_commit'] or status:
                raise BlockedError('Disposable project changed outside a recorded runner state; inspect it before running',
                                   reason_code='project_changed_without_resume')

        number = _attempt_number(manifest)
        attempt_rel = f'evidence/attempts/attempt-{number:04d}'
        attempt_path = _owned_path(root, attempt_rel)
        if attempt_path.exists():
            raise QualificationError('Next attempt path already exists; refusing to overwrite it')
        if resume_relative is None:
            run_relative = f'{attempt_rel}/runner-state'
        else:
            run_relative = resume_relative
        run_path = _owned_path(root, run_relative)
        if resume_relative is None and run_path.exists():
            raise QualificationError('New runner state path already exists; refusing to overwrite it')
        record: dict[str, object] = {
            'number': number, 'attempt_path': attempt_rel, 'run_directory': run_relative,
            'status': 'starting', 'started_at': _now(), 'finished_at': None,
            'doctor_report': f'{attempt_rel}/doctor.json',
            'doctor_stderr': f'{attempt_rel}/doctor-stderr.log',
            'runner_summary': f'{attempt_rel}/runner-summary.json',
            'runner_progress': f'{attempt_rel}/runner-progress.jsonl',
            'runner_started': False, 'exit_code': None, 'runner_status': None,
            'reason_code': None,
        }
        manifest['attempts'].append(record)
        _add_owned_paths(manifest)
        _atomic_manifest(root, manifest)
        attempt_path.mkdir(mode=0o700)

        options = _optional_args(args)
        runner = _bundle_root() / 'scripts/run.py'
        common = [sys.executable, str(runner), str(plan)]
        doctor_argv = [*common, '--doctor', '--max-runtime', _seconds(deadline - time.monotonic())]
        if resume_absolute:
            doctor_argv.extend(('--resume', resume_absolute))
        doctor_argv.extend(options)
        with _catch_signals():
            doctor_result = _supervised_child(
                root, doctor_argv, project, _owned_path(root, record['doctor_report']),
                _owned_path(root, record['doctor_stderr']), deadline)
            doctor_report = _read_json(_owned_path(root, record['doctor_report']))
            doctor_code = doctor_result.code
            doctor_reason = None if doctor_report is None else doctor_report.get('reason_code')
            doctor_ready = None if doctor_report is None else doctor_report.get('readiness')
            doctor_can_attempt = isinstance(doctor_ready, dict) and doctor_ready.get('can_attempt') is True
            doctor_valid = (doctor_report is not None and doctor_report.get('schema_version') == 1
                            and doctor_report.get('status') == 'diagnosed'
                            and isinstance(doctor_ready, dict)
                            and doctor_ready.get('status') in ('blocked', 'unknown')
                            and isinstance(doctor_ready.get('can_attempt'), bool)
                            and not (doctor_ready.get('status') == 'blocked'
                                     and doctor_ready.get('can_attempt') is True))
            if doctor_result.cleanup_error:
                final = {'schema_version': SCHEMA_VERSION, 'status': 'blocked',
                         'reason_code': 'cleanup_unconfirmed', 'detail': doctor_result.cleanup_error,
                         'root': str(root), 'attempt': number, 'doctor_exit_code': doctor_code,
                         'signal': doctor_result.interrupted,
                         'exit_code': 3}
                code = 3
            elif doctor_result.interrupted is not None:
                final = {'schema_version': SCHEMA_VERSION, 'status': 'interrupted',
                         'reason_code': 'interrupted_during_doctor', 'root': str(root),
                         'attempt': number, 'exit_code': doctor_result.code,
                         'doctor_report': str(_owned_path(root, record['doctor_report']))}
                code = doctor_result.code
            elif doctor_result.timed_out:
                final = {'schema_version': SCHEMA_VERSION, 'status': 'deadline',
                         'reason_code': 'doctor_deadline', 'root': str(root), 'attempt': number,
                         'exit_code': 124, 'doctor_report': str(_owned_path(root, record['doctor_report']))}
                code = 124
            elif not doctor_valid:
                final = {'schema_version': SCHEMA_VERSION, 'status': 'failed',
                         'reason_code': 'doctor_report_invalid', 'root': str(root),
                         'attempt': number, 'exit_code': 1,
                         'doctor_report': str(_owned_path(root, record['doctor_report']))}
                code = 1
            elif doctor_code != 0 or not doctor_can_attempt:
                if doctor_code == 0:
                    doctor_reason = 'doctor_blocked' if isinstance(doctor_ready, dict) and doctor_ready.get('status') == 'blocked' else 'doctor_inconsistent_readiness'
                if doctor_code == 124:
                    doctor_status, code, fallback_reason = 'deadline', 124, 'doctor_deadline'
                elif doctor_code in (130, 143):
                    doctor_status, code, fallback_reason = 'interrupted', doctor_code, 'doctor_interrupted'
                elif doctor_code == 2:
                    doctor_status, code, fallback_reason = 'invalid', 2, 'doctor_invalid'
                elif doctor_code == 3 or not doctor_can_attempt:
                    doctor_status, code, fallback_reason = 'blocked', 3, 'doctor_blocked'
                else:
                    doctor_status, code, fallback_reason = 'failed', doctor_code, 'doctor_failed'
                final = {'schema_version': SCHEMA_VERSION, 'status': doctor_status,
                         'reason_code': doctor_reason or fallback_reason, 'root': str(root),
                         'attempt': number, 'doctor_exit_code': doctor_code, 'exit_code': code,
                         'doctor_report': str(_owned_path(root, record['doctor_report']))}
            else:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    final = {'schema_version': SCHEMA_VERSION, 'status': 'deadline',
                             'reason_code': 'total_deadline', 'root': str(root),
                             'attempt': number, 'exit_code': 124}
                    code = 124
                else:
                    if resume_absolute:
                        runner_argv = [*common, '--resume', resume_absolute]
                    else:
                        runner_argv = [*common, '--run-dir', str(run_path)]
                    runner_argv.extend(('--max-runtime', _seconds(remaining),
                                        '--iteration-timeout', '300'))
                    runner_argv.extend(options)
                    record['runner_started'] = True
                    record['status'] = 'running'
                    _atomic_manifest(root, manifest)
                    runner_result = _supervised_child(
                        root, runner_argv, project, _owned_path(root, record['runner_summary']),
                        _owned_path(root, record['runner_progress']), deadline)
                    runner_report = _read_json(_owned_path(root, record['runner_summary']))
                    runner_code = runner_result.code
                    if runner_result.cleanup_error:
                        final = {'schema_version': SCHEMA_VERSION, 'status': 'blocked',
                                 'reason_code': 'cleanup_unconfirmed',
                                 'detail': runner_result.cleanup_error, 'root': str(root),
                                 'attempt': number, 'run_directory': str(_owned_path(root, run_relative)),
                                 'runner_exit_code': runner_code,
                                 'runner_status': None if runner_report is None else runner_report.get('status'),
                                 'runner_reason_code': None if runner_report is None else runner_report.get('reason_code'),
                                 'exit_code': 3}
                        code = 3
                    elif runner_result.interrupted is not None:
                        final = {'schema_version': SCHEMA_VERSION, 'status': 'interrupted',
                                 'reason_code': 'interrupted', 'root': str(root), 'attempt': number,
                                 'run_directory': str(_owned_path(root, run_relative)),
                                 'runner_exit_code': runner_code,
                                 'runner_status': None if runner_report is None else runner_report.get('status'),
                                 'exit_code': runner_code}
                        code = runner_code
                    elif runner_result.timed_out:
                        final = {'schema_version': SCHEMA_VERSION, 'status': 'deadline',
                                 'reason_code': 'run_deadline', 'root': str(root), 'attempt': number,
                                 'run_directory': str(_owned_path(root, run_relative)),
                                 'runner_exit_code': runner_code,
                                 'runner_status': None if runner_report is None else runner_report.get('status'),
                                 'exit_code': 124}
                        code = 124
                    elif runner_report is None:
                        final = {'schema_version': SCHEMA_VERSION, 'status': 'failed',
                                 'reason_code': 'runner_summary_missing_or_invalid', 'root': str(root),
                                 'attempt': number, 'run_directory': str(_owned_path(root, run_relative)),
                                 'runner_exit_code': runner_code,
                                 'summary_path': str(_owned_path(root, record['runner_summary']))}
                        code = runner_code or 1
                    else:
                        runner_status = runner_report.get('status')
                        runner_reason = runner_report.get('reason_code')
                        runner_valid = (runner_report.get('schema_version') == 1
                                        and isinstance(runner_status, str)
                                        and isinstance(runner_reason, str))
                        final = {'schema_version': SCHEMA_VERSION,
                                 'status': runner_status if runner_valid else 'failed',
                                 'reason_code': runner_reason if runner_valid else 'runner_summary_invalid',
                                 'root': str(root), 'attempt': number,
                                 'run_directory': str(_owned_path(root, run_relative)),
                                 'runner_exit_code': runner_code,
                                 'runner_status': runner_status,
                                 'runner_reason_code': runner_reason,
                                 'exit_code': runner_code,
                                 'summary_path': str(_owned_path(root, record['runner_summary']))}
                        code = runner_code
                        if not runner_valid:
                            code = runner_code or 1
                        elif runner_status != {
                            0: 'completed', 1: 'failed', 2: 'invalid', 3: 'blocked',
                            124: 'deadline', 130: 'interrupted', 143: 'interrupted',
                        }.get(runner_code):
                            final['status'] = 'failed'
                            final['reason_code'] = 'runner_exit_status_mismatch'
                            code = runner_code or 1

        record['finished_at'] = _now()
        record['status'] = str(final['status'])
        record['exit_code'] = code
        runner_report_value = locals().get('runner_report')
        record['runner_status'] = (runner_report_value.get('status')
                                   if isinstance(runner_report_value, dict)
                                   and isinstance(runner_report_value.get('status'), str) else None)
        record['reason_code'] = str(final['reason_code'])
        _atomic_manifest(root, manifest)
        return code, final


def _collect_qualification(root_value: str) -> dict[str, object]:
    initial_root = _physical_root(root_value)
    with _run_lock(initial_root):
        root, manifest = _load_root(root_value)
        project = _owned_path(root, 'project', must_exist=True)
        if Path(_git(project, 'rev-parse', '--show-toplevel')).resolve(strict=True) != project.resolve(strict=True):
            raise QualificationError('Project Git root does not match the owned project directory')

        baseline = manifest['baseline_commit']
        head = _git(project, 'rev-parse', 'HEAD')
        branch = _git(project, 'branch', '--show-current')
        porcelain = _git(project, 'status', '--porcelain=v1', '--untracked-files=all')
        commit_count = int(_git(project, 'rev-list', '--count', 'HEAD'))
        range_result = subprocess.run(
            ['git', '-C', str(project), 'rev-list', '--count', f'{baseline}..HEAD'],
            cwd=project, env=_git_environment(), stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=10, check=False)
        baseline_reachable = range_result.returncode == 0
        commits_since_baseline = int(range_result.stdout.strip()) if baseline_reachable else None
        log_text = _git(project, 'log', '--max-count=100', '--format=%H%x09%s', 'HEAD')
        commit_log = []
        for line in log_text.splitlines():
            fields = line.split('\t', 1)
            if fields and len(fields[0]) in (40, 64):
                commit_log.append({'sha': fields[0], 'subject': fields[1] if len(fields) > 1 else ''})

        missing: list[dict[str, object]] = []
        reports: list[dict[str, object]] = []
        for attempt in manifest['attempts']:
            attempt_path = _owned_path(root, attempt['attempt_path'])
            if not attempt_path.is_dir():
                missing.append({'attempt': attempt['number'], 'artifact': 'attempt_directory',
                                'path': attempt['attempt_path']})
                continue
            doctor_path = _owned_path(root, attempt['doctor_report'])
            doctor_report = _read_json(doctor_path)
            if doctor_report is None:
                missing.append({'attempt': attempt['number'], 'artifact': 'doctor_report',
                                'path': attempt['doctor_report']})
            runner_report = None
            if attempt['runner_started']:
                runner_path = _owned_path(root, attempt['runner_summary'])
                runner_report = _read_json(runner_path)
                if runner_report is None:
                    missing.append({'attempt': attempt['number'], 'artifact': 'runner_summary',
                                    'path': attempt['runner_summary']})
                progress_path = _owned_path(root, attempt['runner_progress'])
                if not progress_path.is_file():
                    missing.append({'attempt': attempt['number'], 'artifact': 'runner_progress',
                                    'path': attempt['runner_progress']})
            else:
                progress_path = _owned_path(root, attempt['runner_progress'])
                runner_path = _owned_path(root, attempt['runner_summary'])
                if progress_path.exists() or runner_path.exists():
                    missing.append({'attempt': attempt['number'], 'artifact': 'unexpected_runner_output',
                                    'path': attempt['attempt_path']})
            versions = None
            if doctor_report is not None:
                versions = doctor_report.get('versions')
                if versions is None and isinstance(doctor_report.get('readiness'), dict):
                    provenance = doctor_report['readiness'].get('provenance')
                    if isinstance(provenance, dict):
                        versions = {'provider': provenance.get('provider_version')}
            reports.append({
                'attempt': attempt['number'], 'status': attempt['status'],
                'exit_code': attempt['exit_code'], 'reason_code': attempt['reason_code'],
                'doctor': None if doctor_report is None else {
                    'status': doctor_report.get('status'),
                    'reason_code': doctor_report.get('reason_code'),
                    'readiness': doctor_report.get('readiness'),
                    'blockers': doctor_report.get('blockers'),
                    'versions': versions,
                },
                'runner': None if runner_report is None else {
                    'status': runner_report.get('status'),
                    'reason_code': runner_report.get('reason_code'),
                    'run_directory': runner_report.get('run_directory'),
                },
                'doctor_report_path': attempt['doctor_report'],
                'runner_summary_path': attempt['runner_summary'] if attempt['runner_started'] else None,
                'runner_progress_path': attempt['runner_progress'] if attempt['runner_started'] else None,
            })

        number = max((item['number'] for item in manifest['collections']), default=0) + 1
        collection_rel = f'evidence/collections/collection-{number:04d}.json'
        collection_path = _owned_path(root, collection_rel)
        if collection_path.exists():
            raise QualificationError('Next collection path already exists; refusing to overwrite it')
        collection_record = {'number': number, 'path': collection_rel, 'created_at': _now()}
        manifest['collections'].append(collection_record)
        _add_owned_paths(manifest)

        report = {
            'schema_version': SCHEMA_VERSION, 'status': 'collection_complete',
            'root': str(root), 'collected_at': collection_record['created_at'],
            'baseline_commit': baseline,
            'git': {
                'branch': branch, 'head': head, 'clean': not porcelain,
                'dirty_entry_count': len(porcelain.splitlines()),
                'commit_count': commit_count, 'commits_since_baseline': commits_since_baseline,
                'baseline_reachable': baseline_reachable, 'commit_log': commit_log,
                'commit_log_truncated': commit_count > len(commit_log),
            },
            'reports': reports, 'missing_evidence': missing,
            'collection_path': str(collection_path),
        }
        _atomic_manifest(root, manifest)
        _write_json_exclusive(collection_path, report)
        return report


def _setup(root_value: str) -> dict[str, object]:
    raw_root = Path(root_value)
    if not raw_root.is_absolute():
        raise QualificationError('--root for setup must be an absolute path')
    if raw_root.exists() or raw_root.is_symlink():
        raise QualificationError(f'Refusing to overwrite an existing root: {raw_root}')
    root = raw_root.resolve(strict=False)
    if root.exists() or root.is_symlink():
        raise QualificationError(f'Refusing to overwrite an existing root: {root}')
    if not root.parent.is_dir():
        raise QualificationError(f'Root parent must already exist: {root.parent}')

    bundle = _bundle_root()
    fixture = bundle / FIXTURE_RELATIVE_PATH
    if not fixture.is_file() or fixture.is_symlink():
        raise QualificationError(f'Bundled qualification fixture is missing or unsafe: {fixture}')
    bundle_digest = _bundle_digest(bundle)
    fixture_digest = _sha256_file(fixture)

    root.mkdir(mode=0o700)
    root.chmod(0o700)
    project = root / 'project'
    evidence = root / 'evidence'
    project.mkdir(mode=0o700)
    evidence.mkdir(mode=0o700)
    (evidence / 'attempts').mkdir(mode=0o700)
    (evidence / 'collections').mkdir(mode=0o700)
    _write_bytes_exclusive(evidence / 'run.lock', b'')
    plan = project / 'ExecPlan.md'
    with fixture.open('rb') as source, plan.open('xb') as destination:
        os.chmod(plan, 0o600)
        while chunk := source.read(1024 * 1024):
            destination.write(chunk)
        destination.flush()
        os.fsync(destination.fileno())

    init = subprocess.run(['git', 'init', '--template=', '--initial-branch=main', '--quiet'],
                          cwd=project, env=_git_environment(), stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, check=False)
    if init.returncode:
        detail = init.stderr.strip() or f'Git init exited {init.returncode}'
        raise QualificationError(f'Could not initialize disposable Git repository: {detail}')
    for key, value in (
        ('user.name', 'ExecPlan Qualification'),
        ('user.email', 'execplan-qualification@example.invalid'),
        ('commit.gpgsign', 'false'),
    ):
        _git(project, 'config', '--local', key, value)
    _git(project, 'add', '--', 'ExecPlan.md')
    _git(project, 'commit', '--quiet', '--no-gpg-sign', '-m', 'qualification baseline')
    baseline = _git(project, 'rev-parse', 'HEAD')
    if _git(project, 'status', '--porcelain'):
        raise QualificationError('Disposable repository was not clean after baseline commit')

    manifest = {
        'schema_version': SCHEMA_VERSION,
        'root': str(root),
        'project': 'project',
        'baseline_commit': baseline,
        'bundle': {'path': str(bundle), 'sha256': bundle_digest},
        'fixture': {'path': FIXTURE_RELATIVE_PATH.as_posix(), 'sha256': fixture_digest},
        'owned_artifact_paths': [
            'manifest.json', 'project', 'project/.git', 'project/ExecPlan.md',
            'evidence', 'evidence/attempts', 'evidence/collections', 'evidence/run.lock',
        ],
        'attempts': [],
        'collections': [],
    }
    manifest_path = root / 'manifest.json'
    _write_json_exclusive(manifest_path, manifest)
    manifest_path.chmod(0o600)
    next_argv = [sys.executable, str(Path(__file__).resolve()), 'run', '--root',
                 str(root), '--authorize-paid-run']
    return {'schema_version': SCHEMA_VERSION, 'status': 'setup_complete',
            'root': str(root), 'project': str(project), 'baseline_commit': baseline,
            'manifest': str(manifest_path), 'next_argv': next_argv}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest='command', required=True)
    setup = commands.add_parser('setup', allow_abbrev=False,
                                help='create a new disposable qualification repository')
    setup.add_argument('--root', required=True, help='absolute new directory for qualification files')
    run = commands.add_parser('run', allow_abbrev=False, help='run or resume a qualification')
    run.add_argument('--root', required=True, help='owned qualification root')
    run.add_argument('--resume', help='explicit run directory to resume')
    run.add_argument('--authorize-paid-run', action='store_true', required=True,
                     help='confirm the caller authorized a paid provider attempt')
    run.add_argument('--policy', help='reviewed provider policy file')
    run.add_argument('--gemini', help='Gemini executable path or name')
    run.add_argument('--model', help='explicit provider model')
    collect = commands.add_parser('collect', allow_abbrev=False,
                                  help='refresh local Git and saved-report evidence')
    collect.add_argument('--root', required=True, help='owned qualification root')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == 'setup':
            report = _setup(args.root)
            code = 0
        elif args.command == 'run':
            if sys.platform not in ('darwin', 'linux'):
                raise QualificationError('Run is supported on macOS and Linux only')
            code, report = _run_qualification(args)
        else:
            if sys.platform not in ('darwin', 'linux'):
                raise QualificationError('Collect is supported on macOS and Linux only')
            report = _collect_qualification(args.root)
            code = 0
        print(json.dumps(report, ensure_ascii=False, sort_keys=True), flush=True)
        return code
    except (OSError, QualificationError, ValueError, subprocess.SubprocessError) as error:
        code = error.code if isinstance(error, QualificationError) else 2
        print(json.dumps({'schema_version': SCHEMA_VERSION,
                          'status': 'blocked' if code == 3 else 'invalid' if code == 2 else 'failed',
                          'reason_code': (error.reason_code if isinstance(error, QualificationError)
                                          else 'qualification_error'),
                          'detail': str(error), 'exit_code': code},
                         ensure_ascii=False, sort_keys=True), flush=True)
        return code


if __name__ == '__main__':
    raise SystemExit(main())

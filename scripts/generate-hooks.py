#!/usr/bin/env python3
"""Render and check the checked-in provider-local hook scripts.

Examples:
  python3 scripts/generate-hooks.py --check  Verify checked-in hooks are current.
  python3 scripts/generate-hooks.py --write  Regenerate stale checked-in hooks.

Exit codes: 0 success, 1 stale checked-in output, 2 usage or generator failure,
and 130 interruption. Output lists generated or stale repository-relative paths.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import importlib
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tempfile
import time
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hooks.manifest import GeneratedTarget, targets
from hooks.providers import PROVIDERS


OWNERSHIP_PREFIX = "# Generated from hooks/families/"
LOCK_NAME = ".generate-hooks.lock"
LOCK_TIMEOUT_SECONDS = 1.0
TEST_FAILURE_ENVIRONMENT = "GENERATE_HOOKS_TEST_FAIL_AFTER_REPLACEMENTS"
TEST_INTERRUPT_ENVIRONMENT = "GENERATE_HOOKS_TEST_INTERRUPT_AFTER_REPLACEMENTS"
ALLOWED_HOOK_ROOTS = (
    PurePosixPath(".copilot/hooks"),
    PurePosixPath(".gemini/hooks"),
    PurePosixPath(".github/hooks"),
    PurePosixPath(".codex/hooks"),
)


class GenerateError(ValueError):
    """A safe diagnostic for invalid canonical inputs or filesystem state."""


@dataclass(frozen=True)
class RenderedOutput:
    target: GeneratedTarget
    content: bytes


@dataclass(frozen=True)
class CheckResult:
    stale_paths: tuple[PurePosixPath, ...]
    undeclared_owned_paths: tuple[PurePosixPath, ...]

    @property
    def is_current(self) -> bool:
        return not self.stale_paths and not self.undeclared_owned_paths


@dataclass(frozen=True)
class WriteResult:
    changed_paths: tuple[PurePosixPath, ...]
    unchanged_count: int


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, allow_abbrev=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--write", action="store_true", help="atomically update stale checked-in outputs")
    actions.add_argument("--check", action="store_true", help="report stale checked-in outputs without writing")
    arguments = parser.parse_args(argv)
    if not arguments.write and not arguments.check:
        parser.print_help(sys.stdout)
        parser.error("choose exactly one of --write or --check")
    return arguments


def _is_reparse_point(details: os.stat_result) -> bool:
    attributes = getattr(details, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & flag)


def _assert_safe_component(path: Path, label: str) -> None:
    try:
        details = path.lstat()
    except FileNotFoundError:
        return
    except OSError as error:
        raise GenerateError(f"Unable to inspect {label}: {path}: {error}") from error
    if stat.S_ISLNK(details.st_mode) or _is_reparse_point(details):
        raise GenerateError(f"{label} must not be a symbolic link or reparse point: {path}")


def _contained_path(repo_root: Path, output_path: PurePosixPath) -> Path:
    if output_path.is_absolute() or ".." in output_path.parts:
        raise GenerateError(f"Output path must be contained in a provider hook tree: {output_path}")
    if not any(output_path.is_relative_to(root) for root in ALLOWED_HOOK_ROOTS):
        raise GenerateError(f"Output path must be contained in a provider hook tree: {output_path}")
    return repo_root.joinpath(*output_path.parts)


def validate_target(repo_root: Path, target: GeneratedTarget) -> Path:
    """Validate one target before read-only comparison or any write begins."""
    if target.mode != 0o755:
        raise GenerateError(f"Generated target must use executable mode 0o755: {target.output_path}")
    if target.provider not in PROVIDERS:
        raise GenerateError(f"Unknown provider {target.provider!r} for {target.output_path}")
    path = _contained_path(repo_root, target.output_path)
    _assert_safe_component(repo_root, "Repository root")
    current = repo_root
    for component in target.output_path.parts:
        current = current / component
        _assert_safe_component(current, "Output path component")
    if not path.parent.is_dir():
        raise GenerateError(f"Output parent directory does not exist: {path.parent}")
    return path


def validate_rendered_output(repo_root: Path, output: RenderedOutput) -> None:
    """Reject malformed renderings before the write boundary is entered."""
    validate_target(repo_root, output.target)
    try:
        text = output.content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise GenerateError(f"Rendered output is not UTF-8: {output.target.output_path}") from error
    expected_header = f"# Generated from hooks/families/{output.target.family}.py by scripts/generate-hooks.py. Do not edit.\n"
    if not text.startswith("#!/usr/bin/env python3\n" + expected_header):
        raise GenerateError(f"Rendered output has an invalid generated header: {output.target.output_path}")
    if "\r" in text or not text.endswith("\n"):
        raise GenerateError(f"Rendered output must use LF endings and a terminal newline: {output.target.output_path}")
    try:
        compile(text, str(output.target.output_path), "exec")
    except SyntaxError as error:
        raise GenerateError(f"Rendered output is invalid Python: {output.target.output_path}: {error.msg}") from error


def render_all(repo_root: Path) -> tuple[RenderedOutput, ...]:
    """Render every declared target in memory without changing the filesystem."""
    declared_targets = targets()
    seen_paths: set[PurePosixPath] = set()
    rendered: list[RenderedOutput] = []
    for target in declared_targets:
        if target.output_path in seen_paths:
            raise GenerateError(f"Duplicate generated output path: {target.output_path}")
        seen_paths.add(target.output_path)
        validate_target(repo_root, target)
        provider = PROVIDERS[target.provider]
        try:
            family = importlib.import_module(f"hooks.families.{target.family}")
            content = family.render(provider, target)
        except (ImportError, AttributeError, ValueError) as error:
            raise GenerateError(f"Unable to render {target.output_path}: {error}") from error
        output = RenderedOutput(target, content.encode("utf-8"))
        validate_rendered_output(repo_root, output)
        rendered.append(output)
    return tuple(rendered)


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def _output_is_current(path: Path, output: RenderedOutput) -> bool:
    """Return whether one generated output matches its meaningful host metadata."""
    return (
        path.is_file()
        and path.read_bytes() == output.content
        and (os.name == "nt" or _mode(path) == output.target.mode)
    )


def _owned_undeclared_paths(repo_root: Path, declared: set[PurePosixPath]) -> tuple[PurePosixPath, ...]:
    found: list[PurePosixPath] = []
    for root in ALLOWED_HOOK_ROOTS:
        directory = repo_root.joinpath(*root.parts)
        _assert_safe_component(directory, "Provider hook root")
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.py"):
            _assert_safe_component(path, "Generated output")
            relative = PurePosixPath(path.relative_to(repo_root).as_posix())
            if relative in declared:
                continue
            try:
                first_lines = path.read_text(encoding="utf-8").splitlines()[:2]
            except (OSError, UnicodeDecodeError) as error:
                raise GenerateError(f"Unable to inspect provider hook file: {path}: {error}") from error
            if len(first_lines) > 1 and first_lines[1].startswith(OWNERSHIP_PREFIX):
                found.append(relative)
    return tuple(sorted(found))


def check_outputs(repo_root: Path, outputs: tuple[RenderedOutput, ...]) -> CheckResult:
    """Compare expected files and POSIX modes, when meaningful, without writing state."""
    stale: list[PurePosixPath] = []
    declared = {output.target.output_path for output in outputs}
    for output in outputs:
        path = validate_target(repo_root, output.target)
        if not _output_is_current(path, output):
            stale.append(output.target.output_path)
    return CheckResult(tuple(stale), _owned_undeclared_paths(repo_root, declared))


def _create_lock(repo_root: Path) -> Path:
    lock_path = repo_root / LOCK_NAME
    deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
    while True:
        try:
            descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise GenerateError(f"Timed out waiting for generator lock: {lock_path}") from None
            time.sleep(0.05)
            continue
        try:
            os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return lock_path


def _stage(path: Path, content: bytes, mode: int) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(prefix=".generate-hooks-stage-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        return temporary
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def write_outputs(repo_root: Path, outputs: tuple[RenderedOutput, ...]) -> WriteResult:
    """Atomically replace stale outputs and restore all of them after a failure."""
    for output in outputs:
        validate_rendered_output(repo_root, output)
    changes = tuple(
        output for output in outputs
        if not _output_is_current(validate_target(repo_root, output.target), output)
    )
    if not changes:
        return WriteResult((), len(outputs))
    lock_path: Path | None = None
    staged: dict[Path, Path] = {}
    backups: dict[Path, tuple[Path | None, int | None]] = {}
    replaced: list[Path] = []
    try:
        lock_path = _create_lock(repo_root)
        for output in changes:
            destination = validate_target(repo_root, output.target)
            staged[destination] = _stage(destination, output.content, output.target.mode)
            if destination.exists():
                backups[destination] = (_stage(destination, destination.read_bytes(), _mode(destination)), _mode(destination))
            else:
                backups[destination] = (None, None)
        for index, output in enumerate(changes, start=1):
            destination = validate_target(repo_root, output.target)
            os.replace(staged[destination], destination)
            replaced.append(destination)
            failure_after = os.environ.get(TEST_FAILURE_ENVIRONMENT)
            if failure_after and index >= int(failure_after):
                raise OSError("injected transaction failure")
            interrupt_after = os.environ.get(TEST_INTERRUPT_ENVIRONMENT)
            if interrupt_after and index >= int(interrupt_after):
                raise KeyboardInterrupt
        return WriteResult(tuple(output.target.output_path for output in changes), len(outputs) - len(changes))
    except KeyboardInterrupt:
        _rollback(replaced, backups)
        raise
    except (OSError, ValueError, GenerateError) as error:
        _rollback(replaced, backups)
        raise GenerateError(f"Write failed; rollback completed: {error}") from error
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)
        for backup, _mode_value in backups.values():
            if backup is not None:
                backup.unlink(missing_ok=True)
        if lock_path is not None:
            lock_path.unlink(missing_ok=True)


def _rollback(replaced: list[Path], backups: dict[Path, tuple[Path | None, int | None]]) -> None:
    for destination in reversed(replaced):
        backup, mode = backups[destination]
        if backup is None:
            destination.unlink(missing_ok=True)
        else:
            os.replace(backup, destination)
            if mode is not None:
                os.chmod(destination, mode)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        arguments = parse_arguments(argv)
        outputs = render_all(REPO_ROOT)
        if arguments.check:
            result = check_outputs(REPO_ROOT, outputs)
            if result.is_current:
                print(f"Generated hooks are current ({len(outputs)} files).")
                return 0
            for path in (*result.stale_paths, *result.undeclared_owned_paths):
                print(path.as_posix())
            return 1
        result = write_outputs(REPO_ROOT, outputs)
        if result.changed_paths:
            for path in result.changed_paths:
                print(path.as_posix())
        else:
            print(f"Generated hooks already current ({result.unchanged_count} files).")
        return 0
    except KeyboardInterrupt:
        print("Generator interrupted; cleaned up staged outputs.", file=sys.stderr)
        return 130
    except GenerateError as error:
        print(f"generate-hooks: {error}. Resolve the reported path and retry.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

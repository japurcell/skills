#!/usr/bin/env python3
"""Copy and prune installed skill artifacts, then rebase shared reference links."""

from __future__ import annotations

import argparse
from contextlib import contextmanager, nullcontext
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys


MARKDOWN_SUFFIXES = {".md", ".markdown"}
REFERENCE_PREFIX_BOUNDARY = r"(?<![A-Za-z0-9._/-])"
SKILL_EXCLUSIONS = ("evals", "README.md", "LICENSE.txt", "LICENSE.md")
TEST_DIRECTORY_NAMES = {"tests", "__tests__"}
TEST_SCRIPT_NAME = re.compile(r"^(?:test(?:[_-].*)?|.+\.test)\.(?:py|sh|ps1)$")
ARTIFACT_POLICY = {
    "directory_names": ("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"),
    "file_names": (".DS_Store",),
    "file_suffixes": (".pyc", ".pyo"),
}


def artifact_excluded(name: str, is_directory: bool, is_link: bool) -> bool:
    return (
        ((is_directory or is_link) and name in ARTIFACT_POLICY["directory_names"])
        or (
            (not is_directory or is_link)
            and (
                name in ARTIFACT_POLICY["file_names"]
                or name.endswith(ARTIFACT_POLICY["file_suffixes"])
            )
        )
    )


def filtered_entries(directory: Path):
    """Do not inspect children whose names alone exclude them for either type."""
    with os.scandir(directory) as entries:
        for entry in entries:
            # A link can match either category, so stat only names whose type matters.
            if (
                entry.name in ARTIFACT_POLICY["directory_names"]
                or entry.name in ARTIFACT_POLICY["file_names"]
                or entry.name.endswith(ARTIFACT_POLICY["file_suffixes"])
            ):
                is_link = entry.is_symlink()
                is_directory = entry.is_dir(follow_symlinks=False)
                if artifact_excluded(entry.name, is_directory, is_link):
                    continue
            yield entry


def reject_linked_ancestors(path: Path) -> None:
    for component in (path, *path.parents):
        # macOS exposes these standard system paths as aliases to /private.
        if sys.platform == "darwin" and str(component) in ("/var", "/tmp", "/etc"):
            continue
        if is_link_or_junction(component):
            raise ValueError(f"Refusing linked destination directory: {component}")


def copy_filtered(source_dir: Path, destination_dir: Path, *, replace: bool = False) -> int:
    """Copy allowed entries with native cp, without following destination links."""
    reject_linked_ancestors(destination_dir.parent)
    source_real = source_dir.resolve()
    source_is_link = is_link_or_junction(source_dir)
    if source_is_link and is_link_or_junction(destination_dir) and not replace:
        destination_real = destination_dir.parent.resolve() / destination_dir.name
    else:
        destination_real = destination_dir.resolve()
    if source_real == destination_real or source_real in destination_real.parents or destination_real in source_real.parents:
        raise ValueError("Refusing overlapping source and destination")
    if not source_dir.exists() and not source_is_link:
        raise FileNotFoundError(source_dir)
    if replace:
        reject_linked_ancestors(destination_dir)
        remove_pruned_path(destination_dir)
    if source_is_link:
        if destination_dir.is_symlink():
            destination_dir.unlink()
        elif destination_dir.exists():
            raise ValueError(f"Refusing to replace destination with linked skill: {destination_dir}")
        return subprocess.run(["cp", "-Rp", "--", str(source_dir), str(destination_dir)], check=False).returncode
    reject_linked_ancestors(destination_dir)
    changed_modes = []
    succeeded = False

    def writable(path: Path) -> None:
        details = path.lstat()
        mode = _checked_write_access_mode(path, details)
        if not mode & stat.S_IWUSR:
            path.chmod(mode | stat.S_IWUSR)
            changed_modes.append((path, mode))

    def copy_directory(source: Path, destination: Path) -> None:
        if destination.exists():
            if not destination.is_dir() or is_link_or_junction(destination):
                raise ValueError(f"Refusing linked or non-directory destination: {destination}")
            writable(destination)
        else:
            destination.mkdir()
        directories, batch = [], []
        size = 0

        def flush() -> None:
            nonlocal size
            if batch:
                subprocess.run(["cp", "-Rp", "--", *batch, str(destination)], check=True)
                batch.clear()
                size = 0

        for entry in filtered_entries(source):
            target = destination / entry.name
            if entry.is_dir(follow_symlinks=False) and not is_link_or_junction(Path(entry.path)):
                directories.append((Path(entry.path), target))
                continue
            if is_link_or_junction(target):
                remove_pruned_path(target)
            elif target.exists():
                details = target.lstat()
                if stat.S_ISDIR(details.st_mode):
                    raise ValueError(f"Refusing directory in place of destination file: {target}")
                if stat.S_ISREG(details.st_mode):
                    _checked_write_access_mode(target, details)
                    if details.st_nlink > 1:
                        target.unlink()
                    else:
                        writable(target)
            argument = entry.path
            if batch and size + len(os.fsencode(argument)) > 65536:
                flush()
            batch.append(argument)
            size += len(os.fsencode(argument)) + 1
        flush()
        for child_source, child_destination in directories:
            copy_directory(child_source, child_destination)
        shutil.copystat(source, destination, follow_symlinks=False)

    try:
        copy_directory(source_dir, destination_dir)
        succeeded = True
        return 0
    finally:
        if not succeeded:
            for path, mode in reversed(changed_modes):
                if path.exists() and not is_link_or_junction(path):
                    path.chmod(mode)


def portable_relative_path(target: Path, start: Path) -> str:
    return os.path.relpath(target, start=start).replace(os.sep, "/")


def is_link_or_junction(path: Path) -> bool:
    try:
        details = path.lstat()
    except OSError:
        return False

    if stat.S_ISLNK(details.st_mode):
        return True

    is_junction = getattr(os.path, "isjunction", None)
    if is_junction is not None and is_junction(path):
        return True

    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(details, "st_file_attributes", 0) & reparse_point)


def has_link_component(root: Path, relative_path: Path) -> bool:
    current = root
    for component in relative_path.parts:
        current /= component
        if is_link_or_junction(current):
            return True
    return False


def _checked_write_access_mode(path: Path, details: os.stat_result) -> int:
    """Return the original mode, rejecting unsafe temporary owner-write access."""
    mode = stat.S_IMODE(details.st_mode)
    if not mode & stat.S_IWUSR and stat.S_ISREG(details.st_mode) and details.st_nlink > 1:
        raise PermissionError(f"Refusing to change read-only hard-linked file: {path}")
    return mode


def _walk_without_links(root: Path):
    for current_dir, child_dirs, filenames in os.walk(root, followlinks=False):
        directory = Path(current_dir)
        child_dirs[:] = [
            name for name in child_dirs if not is_link_or_junction(directory / name)
        ]
        yield directory, child_dirs, filenames


def regular_markdown_files(root: Path):
    for directory, _, filenames in _walk_without_links(root):
        for filename in filenames:
            path = directory / filename
            if is_link_or_junction(path) or path.suffix.lower() not in MARKDOWN_SUFFIXES:
                continue
            try:
                if stat.S_ISREG(path.lstat().st_mode):
                    yield path
            except OSError:
                continue


def copy_with_preserved_modes(source_dir: Path, destination_dir: Path, command: list[str]) -> int:
    """Allow cp -p to refresh only corresponding read-only destination entries."""
    changed_modes: list[tuple[Path, Path, int]] = []
    succeeded = False
    try:
        if not is_link_or_junction(source_dir) and not is_link_or_junction(destination_dir):
            for source_parent, _, filenames in _walk_without_links(source_dir):
                for source in (source_parent, *(source_parent / name for name in filenames)):
                    relative = source.relative_to(source_dir)
                    destination = destination_dir / relative
                    if is_link_or_junction(source) or has_link_component(destination_dir, relative):
                        continue
                    if is_link_or_junction(destination):
                        continue
                    try:
                        source_stat = source.lstat()
                        destination_stat = destination.lstat()
                    except FileNotFoundError:
                        continue
                    if stat.S_IFMT(source_stat.st_mode) != stat.S_IFMT(destination_stat.st_mode):
                        continue
                    if not (
                        stat.S_ISREG(destination_stat.st_mode)
                        or stat.S_ISDIR(destination_stat.st_mode)
                    ):
                        continue
                    mode = _checked_write_access_mode(destination, destination_stat)
                    if not mode & stat.S_IWUSR:
                        destination.chmod(mode | stat.S_IWUSR)
                        changed_modes.append((source, destination, mode))
        result = subprocess.run(command, check=False)
        succeeded = result.returncode == 0
        return result.returncode
    finally:
        for source, destination, original_mode in reversed(changed_modes):
            # On success cp -p owns the new source mode. On failure undo every
            # temporary elevation, including when the subprocess cannot start.
            if not is_link_or_junction(destination):
                mode = stat.S_IMODE(source.stat().st_mode) if succeeded else original_mode
                destination.chmod(mode)


@contextmanager
def temporary_write_access(root: Path, *, include_files: bool = False):
    """Restore modes on surviving installed entries without following links."""
    changed_modes: list[tuple[Path, int]] = []

    def make_writable(path: Path) -> None:
        if is_link_or_junction(path):
            return
        details = path.lstat()
        if not (
            stat.S_ISDIR(details.st_mode)
            or (include_files and stat.S_ISREG(details.st_mode))
        ):
            return
        mode = _checked_write_access_mode(path, details)
        if not mode & stat.S_IWUSR:
            path.chmod(mode | stat.S_IWUSR)
            changed_modes.append((path, mode))

    try:
        if root.exists() and not is_link_or_junction(root):
            make_writable(root)
            for directory, child_dirs, filenames in _walk_without_links(root):
                for name in child_dirs:
                    make_writable(directory / name)
                if include_files:
                    for name in filenames:
                        make_writable(directory / name)
        yield
    finally:
        for path, mode in reversed(changed_modes):
            if path.exists() and not is_link_or_junction(path):
                path.chmod(mode)


def remove_pruned_path(path: Path) -> None:
    if is_link_or_junction(path):
        # lstat retains the directory type for Windows junctions, including
        # Python versions that have no os.path.isjunction().
        if stat.S_ISDIR(path.lstat().st_mode):
            path.rmdir()
        else:
            path.unlink()
    elif path.exists():
        # POSIX unlink needs writable parents, not writable files. Windows
        # also needs a clear ReadOnly attribute; refuse to change a shared
        # inode's attribute rather than mutating an external hard link.
        with temporary_write_access(path, include_files=os.name == "nt"):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def prune_skill_exclusions(destination_dir: Path) -> None:
    for name in SKILL_EXCLUSIONS:
        remove_pruned_path(destination_dir / name)


def prune_skill_test_files(destination_dir: Path) -> None:
    """Remove conventional test scripts and test-only directories from a copied skill."""
    for current_dir, child_dirs, filenames in os.walk(destination_dir, followlinks=False):
        directory = Path(current_dir)
        for name in tuple(child_dirs):
            candidate = directory / name
            if name in TEST_DIRECTORY_NAMES:
                remove_pruned_path(candidate)
                child_dirs.remove(name)
            elif is_link_or_junction(candidate):
                child_dirs.remove(name)
        for name in filenames:
            if TEST_SCRIPT_NAME.fullmatch(name):
                remove_pruned_path(directory / name)


def prune_skill_artifacts(destination_dir: Path) -> None:
    for current_dir, child_dirs, filenames in os.walk(destination_dir, followlinks=False):
        directory = Path(current_dir)
        for name in tuple(child_dirs):
            path = directory / name
            link = is_link_or_junction(path)
            if artifact_excluded(name, not link, link):
                remove_pruned_path(path)
                child_dirs.remove(name)
            elif link:
                child_dirs.remove(name)
        for name in filenames:
            path = directory / name
            if artifact_excluded(name, False, is_link_or_junction(path)):
                remove_pruned_path(path)


def rebase_skill_references(
    source_dir: Path,
    destination_dir: Path,
    references_source: Path,
    references_destination: Path,
) -> None:
    # A category entry may itself be a symlink or Windows junction. Check it
    # before normalizing paths so we never rewrite through its external target.
    if is_link_or_junction(source_dir) or is_link_or_junction(destination_dir):
        return
    if not references_source.is_dir():
        return

    source_dir = Path(os.path.abspath(source_dir))
    destination_dir = Path(os.path.abspath(destination_dir))
    references_source = Path(os.path.abspath(references_source))
    references_destination = Path(os.path.abspath(references_destination))

    for destination_file in sorted(regular_markdown_files(destination_dir)):
        relative_path = destination_file.relative_to(destination_dir)
        source_file = source_dir / relative_path
        if has_link_component(source_dir, relative_path):
            continue
        try:
            if not stat.S_ISREG(source_file.lstat().st_mode):
                continue
        except OSError:
            continue

        source_prefix = portable_relative_path(references_source, source_file.parent)
        destination_prefix = portable_relative_path(
            references_destination, destination_file.parent
        )
        if source_prefix == destination_prefix:
            continue

        content = destination_file.read_bytes()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            continue

        prefix_pattern = re.compile(
            REFERENCE_PREFIX_BOUNDARY + r"(?:\./)*" + re.escape(source_prefix) + r"/"
        )
        rebased = prefix_pattern.sub(lambda match: f"{destination_prefix}/", text)
        if rebased != text:
            # cp -p preserves read-only files and directories. In-place writes
            # need no writable parent or temporary file; restore the file mode
            # even if writing fails, and never change the source's permissions.
            details = destination_file.stat()
            original_mode = _checked_write_access_mode(destination_file, details)
            try:
                if not original_mode & stat.S_IWUSR:
                    destination_file.chmod(original_mode | stat.S_IWUSR)
                destination_file.write_bytes(rebased.encode("utf-8"))
            finally:
                destination_file.chmod(original_mode)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--destination-dir", type=Path)
    parser.add_argument("--print-artifact-policy", action="store_true", help="Print the shared exclusion policy as JSON.")
    parser.add_argument("--copy-filtered", action="store_true", help="Copy the skill using the shared artifact exclusions.")
    parser.add_argument("--replace-destination", action="store_true", help="Replace the destination before a filtered copy.")
    parser.add_argument("--references-source", type=Path)
    parser.add_argument("--references-destination", type=Path)
    parser.add_argument(
        "--prune", action="store_true",
        help="Remove installed exclusions, test scripts and stale artifacts before rebasing.",
    )
    parser.add_argument(
        "--prune-test-files", action="store_true",
        help="Remove conventional tests and stale artifacts from the installed skill.",
    )
    parser.add_argument(
        "--copy-command", nargs=argparse.REMAINDER,
        help="Run the installer copy command with scoped, temporary destination write access.",
    )
    args = parser.parse_args()

    if args.print_artifact_policy:
        print(json.dumps(ARTIFACT_POLICY))
        return 0
    if args.source_dir is None or args.destination_dir is None:
        parser.error("--source-dir and --destination-dir are required")
    if args.copy_filtered and args.copy_command:
        parser.error("--copy-filtered and --copy-command cannot be combined")
    if args.replace_destination and not args.copy_filtered:
        parser.error("--replace-destination requires --copy-filtered")
    if (args.references_source is None) != (args.references_destination is None):
        parser.error("--references-source and --references-destination must be used together")
    if args.copy_filtered:
        status = copy_filtered(args.source_dir, args.destination_dir, replace=args.replace_destination)
        if status:
            return status
    if args.copy_command:
        status = copy_with_preserved_modes(args.source_dir, args.destination_dir, args.copy_command)
        if status:
            return status
    should_prune = (
        (args.prune or args.prune_test_files)
        and not is_link_or_junction(args.source_dir)
        and not is_link_or_junction(args.destination_dir)
    )
    if should_prune:
        reject_linked_ancestors(args.destination_dir)
    # Source modes may make the copied root and evals directories read-only.
    # Keep pruning inside this scope, then restore every surviving directory.
    with temporary_write_access(args.destination_dir) if should_prune else nullcontext():
        if should_prune:
            prune_skill_artifacts(args.destination_dir)
            if args.prune:
                prune_skill_exclusions(args.destination_dir)
            prune_skill_test_files(args.destination_dir)
        if args.references_source is None:
            return 0
        rebase_skill_references(
            args.source_dir, args.destination_dir,
            args.references_source, args.references_destination,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

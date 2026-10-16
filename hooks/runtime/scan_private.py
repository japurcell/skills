"""Owner-only current-invocation files accessed relative to held directories.

This POSIX dispatcher boundary deliberately refuses unproved platforms. The
scanner's ordinary Git and non-LFS paths keep their separate platform support.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import stat
import time

from .scan_budget import unique
from .scan_lfs import identity
from .scan_types import ScanSecurityError


def encoded(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def decoded(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))


class Directory:
    def __init__(self, path, context, resources, *, private=True):
        self.context = context
        self.path = Path(path)
        self.resources = resources
        selected = self.path
        for alias in (Path("/tmp"), Path("/var")):
            if selected.is_relative_to(alias) and alias.is_symlink() and alias.lstat().st_uid == 0:
                selected = alias.resolve(strict=True) / selected.relative_to(alias)
                break
        self.path = selected
        parent = os.open(selected.anchor, os.O_RDONLY | os.O_DIRECTORY)
        resources.callback(os.close, parent)
        for component in selected.parts[1:]:
            context.check_deadline()
            self.parent_descriptor = parent
            parent = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            resources.callback(os.close, parent)
        self.descriptor = parent
        self.info = os.fstat(parent)
        self.mode = stat.S_IMODE(self.info.st_mode)
        if (self.info.st_uid != os.getuid() or (self.mode != 0o700 if private else bool(self.mode & 0o022))):
            raise ScanSecurityError("handoff_invalid", "repository")

    def name(self, name):
        if not name or name in {".", ".."} or any(c in name for c in "/\\\0"):
            raise ScanSecurityError("handoff_invalid", "repository")
        return name

    def validate(self):
        self.context.check_deadline()
        current = self.path.lstat()
        if (current.st_dev, current.st_ino) != (self.info.st_dev, self.info.st_ino) or stat.S_IMODE(current.st_mode) != self.mode:
            raise ScanSecurityError("handoff_invalid", "repository")

    def child(self, name, *, create=False):
        self.name(name)
        if create:
            os.mkdir(name, 0o700, dir_fd=self.descriptor)
        # Ancestry remains held by this object through the child lifetime.
        child = object.__new__(Directory)
        child.context, child.path, child.resources = self.context, self.path / name, self.resources
        child.descriptor = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.descriptor)
        self.resources.callback(child.close)
        child.info = os.fstat(child.descriptor)
        child.mode = 0o700
        if child.info.st_uid != os.getuid() or stat.S_IMODE(child.info.st_mode) != 0o700:
            raise ScanSecurityError("handoff_invalid", "repository")
        return child

    def cleanup(self):
        """Clear only our held inode, then remove only its now-empty name.

        A caller replacing the original root name cannot turn cleanup into a
        recursive deletion of its replacement. Finding a renamed owned inode
        is confined to the already-held immediate parent, never a global walk.
        """
        deadline = time.monotonic() + 10
        remaining = self.context.limits.max_objects * 4 + 4096

        def check():
            nonlocal remaining
            remaining -= 1
            if remaining < 0 or time.monotonic() >= deadline:
                raise ScanSecurityError("cleanup_failed", "repository", capture_step="cleanup")

        def empty(descriptor, depth=0):
            if depth > 64:
                raise ScanSecurityError("cleanup_failed", "repository", capture_step="cleanup")
            with os.scandir(descriptor) as entries:
                for entry in entries:
                    check()
                    info = entry.stat(follow_symlinks=False)
                    if stat.S_ISDIR(info.st_mode):
                        child = os.open(entry.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
                        try:
                            opened = os.fstat(child)
                            if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                                raise ScanSecurityError("cleanup_failed", "repository", capture_step="cleanup")
                            empty(child, depth + 1)
                        finally:
                            os.close(child)
                        # This can remove only an empty directory. A concurrent
                        # nonempty foreign replacement is preserved by rmdir.
                        os.rmdir(entry.name, dir_fd=descriptor)
                    else:
                        os.unlink(entry.name, dir_fd=descriptor)
        try:
            empty(self.descriptor)
            with os.scandir(self.parent_descriptor) as entries:
                for entry in entries:
                    check()
                    info = entry.stat(follow_symlinks=False)
                    if (info.st_dev, info.st_ino) == (self.info.st_dev, self.info.st_ino):
                        os.rmdir(entry.name, dir_fd=self.parent_descriptor)
                        return
            raise ScanSecurityError("cleanup_failed", "repository", capture_step="cleanup")
        except OSError:
            raise ScanSecurityError("cleanup_failed", "repository", capture_step="cleanup") from None

    def close(self):
        if self.descriptor is not None:
            os.close(self.descriptor)
            self.descriptor = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @contextlib.contextmanager
    def open(self, name):
        self.name(name)
        descriptor = os.open(name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=self.descriptor)
        try:
            info = os.fstat(descriptor)
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1
                    or stat.S_IMODE(info.st_mode) not in {0o400, 0o600, 0o500, 0o700}):
                raise ScanSecurityError("handoff_invalid", "repository")
            with os.fdopen(os.dup(descriptor), "rb") as handle:
                yield handle, info
                if identity(info) != identity(os.fstat(handle.fileno())):
                    raise ScanSecurityError("handoff_invalid", "repository")
        finally:
            os.close(descriptor)

    def read(self, name, maximum=131072):
        with self.open(name) as (handle, info):
            if info.st_size > maximum:
                raise ScanSecurityError("handoff_invalid", "repository")
            raw = handle.read(maximum + 1)
            if len(raw) != info.st_size:
                raise ScanSecurityError("handoff_invalid", "repository")
            self.context.charge_capture(len(raw))
            return raw

    def write(self, name, raw, mode=0o600):
        self.name(name)
        self.context.charge_temp(len(raw))
        descriptor = os.open(name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, mode, dir_fd=self.descriptor)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
        return self.path / name

    @contextlib.contextmanager
    def create(self, name):
        self.name(name)
        descriptor = os.open(name, os.O_CREAT | os.O_EXCL | os.O_RDWR | os.O_NOFOLLOW, 0o600, dir_fd=self.descriptor)
        with os.fdopen(descriptor, "w+b") as handle:
            yield handle

    def copy(self, name, handle, expected, *, maximum, mode=0o400):
        self.name(name)
        descriptor = os.open(name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600, dir_fd=self.descriptor)
        digest = hashlib.sha256()
        size = 0
        with os.fdopen(descriptor, "wb") as target:
            while True:
                self.context.check_deadline()
                chunk = handle.read(65536)
                if not chunk:
                    break
                size += len(chunk)
                if size > maximum:
                    raise ScanSecurityError("handoff_invalid", "candidate_read")
                self.context.charge_capture(len(chunk))
                self.context.charge_temp(len(chunk))
                target.write(chunk)
                digest.update(chunk)
            if digest.hexdigest() != expected:
                raise ScanSecurityError("handoff_invalid", "candidate_read")
            os.fchmod(target.fileno(), mode)
        return self.path / name, size

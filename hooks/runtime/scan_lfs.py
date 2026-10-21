"""Strict local LFS pointer acquisition and verified private payload snapshots.

No network, source configuration execution, detector policy, or upload lives
here. A pointer is recognized before it can be mistaken for payload coverage.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import stat
import tempfile
import sys

from .scan_git import VerifiedCapture, Snapshot, _verify_private_capture, capture_git
from .scan_types import ScanSecurityError, ScanLimitExceeded

VERSION = b"version https://git-lfs.github.com/spec/v1"


def pointer(capture, start, size):
    prefix = b"".join(capture.chunks(start, min(size, 256)))
    if not prefix.startswith((VERSION, b"version https://hawser.github.com/spec/")):
        return None
    if size >= 1024:
        raise ScanSecurityError("lfs_pointer_invalid", "candidate_scan")
    raw = b"".join(capture.chunks(start, size))
    match = re.fullmatch(re.escape(VERSION) + rb"\noid sha256:([0-9a-f]{64})\nsize (0|[1-9][0-9]{0,18})\n", raw)
    if match is None or int(match[2]) >= 2**63:
        raise ScanSecurityError("lfs_pointer_invalid", "candidate_scan")
    return match[1].decode(), int(match[2])


def identity(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


class PayloadStore:
    def __init__(self, repository, resources, *, directory=None):
        self.repository = repository
        self.context = repository.context
        self.resources = resources
        self.directory = directory
        self.objects = {}
        self.bytes = 0
        self.charged = 0
        self.configuration_checked = False
        # Parent-owned named payloads remain physically resident after scanner
        # graph resources close and through required audit/handoff emission.
        # Only anonymous standalone captures are removed/released here.
        if directory is None:
            resources.callback(lambda: self.context.release_temp(self.charged))

    def validate_configuration(self):
        if self.configuration_checked:
            return
        raw = self.repository.read_selected_index(self.repository.common / "config", missing=True, maximum=65536) or b""
        private = self.repository.directory / "lfs-source-config"
        self.repository.put(private, raw)
        with capture_git(self.context, ["config", "--no-includes", "--file", str(private), "--null", "--list"],
                         cwd=self.repository.root, deadline=self.context.deadline) as captured:
            for row in captured.records(b"\0"):
                key, _, value = row.partition(b"\n")
                key = key.lower()
                if (key.startswith((b"include.", b"includeif.", b"lfs.customtransfer.", b"lfs.extension."))
                        or key in {b"extensions.worktreeconfig", b"lfs.standalonetransferagent"}
                        or key == b"lfs.storage" and value != b"lfs"):
                    raise ScanSecurityError("lfs_unsupported", "repository")
        self.configuration_checked = True

    def acquire(self, oid, size, *, git_objects):
        if oid in self.objects:
            if self.objects[oid].byte_count != size:
                raise ScanSecurityError("lfs_payload_invalid", "candidate_read")
            return self.objects[oid]
        context = self.context
        context.check_deadline()
        if sys.platform != "darwin":
            raise ScanSecurityError("lfs_unsupported", "candidate_read")
        if git_objects + len(self.objects) + 1 > context.limits.max_objects:
            raise ScanLimitExceeded("object_count_limit", "candidate_read", measured=git_objects + len(self.objects) + 1, limit=context.limits.max_objects)
        if size > context.limits.max_candidate_bytes:
            raise ScanLimitExceeded("total_bytes_limit", "candidate_read", measured=size, limit=context.limits.max_candidate_bytes)
        self.validate_configuration()
        source = self.repository.common / "lfs" / "objects" / oid[:2] / oid[2:4] / oid
        # The captured destination survives scanner exit only when the current
        # dispatcher owns it. Source and private bytes never share an inode.
        if self.directory is None:
            target = self.resources.enter_context(tempfile.TemporaryFile(mode="w+b"))
        else:
            target = self.resources.enter_context(self.directory.create(oid))
        _verify_private_capture(target)
        digest = hashlib.sha256()
        try:
            with self.repository.open_selected(source) as descriptor:
                before = os.fstat(descriptor)
                if not stat.S_ISREG(before.st_mode) or before.st_size != size or before.st_nlink != 1:
                    raise ScanSecurityError("lfs_payload_invalid", "candidate_read")
                with os.fdopen(os.dup(descriptor), "rb") as handle:
                    remaining = size
                    while remaining:
                        context.check_deadline()
                        chunk = handle.read(min(65536, remaining))
                        if not chunk:
                            raise ScanSecurityError("lfs_payload_invalid", "candidate_read")
                        context.charge_capture(len(chunk))
                        self.charged += len(chunk)
                        context.charge_temp(len(chunk))
                        target.write(chunk)
                        digest.update(chunk)
                        remaining -= len(chunk)
                    if handle.read(1) or identity(before) != identity(os.fstat(handle.fileno())):
                        raise ScanSecurityError("candidate_changed", "candidate_read")
                if digest.hexdigest() != oid:
                    raise ScanSecurityError("lfs_payload_invalid", "candidate_read")
        except (OSError, ValueError):
            raise ScanSecurityError("lfs_payload_unavailable", "candidate_read") from None
        target.flush()
        os.fchmod(target.fileno(), 0o400)
        capture = VerifiedCapture(context, target, size, context.deadline, "candidate_read")
        snapshot = Snapshot(("publication-lfs", oid), capture, 0, size)
        snapshot.classify()
        self.objects[oid] = snapshot
        self.bytes += size
        return snapshot

    def records(self):
        return [{"oid": oid, "size": snapshot.byte_count, "path": "payloads/" + oid}
                for oid, snapshot in sorted(self.objects.items())]

"""Verified immutable outgoing Git coverage, independent of worktree/index state.

One private spool stores verified object bodies. Object IDs bound graph memory;
logical paths are streamed separately so byte dedup cannot erase path policy.
No source repository config participates in object capture.
"""
from __future__ import annotations

import contextlib
import hashlib
import os
from pathlib import Path
import re
import stat
import tempfile
import time

from .scan_types import ScanFailure, ScanSecurityError, ScanLimitExceeded
from .scan_git import capture_git, VerifiedCapture, Snapshot, ScanBudget
from .scan_engine import ScanResult, RetainedFindings, build_findings_json, is_credential_path, redact_match
from .scan_stream import StreamReport, full_line_events, scan_line_events
from .scan_lfs import PayloadStore, pointer

POLICY = "publication_v1"
UNITS = dict(max_objects="objects", max_candidate_bytes="bytes", max_seconds="seconds",
             max_capture_bytes="bytes", max_temp_bytes="bytes")


def _ordinary_directory(path):
    # Metadata ancestry is checked through the existing held-parent primitive
    # when reading sentinel leaves below this directory. Never resolve an object
    # root symlink into a newly trusted source directory.
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise ScanSecurityError("history_unsupported", "repository")


def _optional_metadata(repository, path):
    try:
        return repository.read_selected_index(path, missing=True, maximum=65536)
    except FileNotFoundError:
        # info/ itself is optional in valid Git repositories. Held-parent reads
        # still reject links/reparse points, and required roots are checked by
        # their own non-optional operations before reaching this helper.
        return None
    except OSError:
        raise ScanSecurityError("history_unsupported", "repository") from None


def validate_storage(repository, oid=None):
    context = repository.context
    context.check_deadline()
    objects = repository.common / "objects"
    _ordinary_directory(objects)
    for directory in (repository.common, repository.gitdir):
        for relative in ("shallow", "info/grafts"):
            if _optional_metadata(repository, directory / relative):
                raise ScanSecurityError("history_unsupported", "repository")
    for name in ("alternates", "http-alternates"):
        if _optional_metadata(repository, objects / "info" / name):
            raise ScanSecurityError("history_unsupported", "repository")
    # Reject redirected pack/index metadata and redirected loose-object roots.
    # The body hash remains authoritative if ordinary source files change.
    with os.scandir(objects) as entries:
        for entry in entries:
            context.check_deadline()
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ScanSecurityError("history_unsupported", "repository")
            if entry.name in {"info", "pack"} or re.fullmatch(r"[0-9a-f]{2}", entry.name):
                _ordinary_directory(Path(entry.path))
    pack = objects / "pack"
    if pack.exists():
        with os.scandir(pack) as entries:
            for entry in entries:
                context.check_deadline()
                info = entry.stat(follow_symlinks=False)
                if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                    raise ScanSecurityError("history_unsupported", "repository")
    if oid:
        loose = objects / oid[:2] / oid[2:]
        try:
            info = loose.lstat()
        except FileNotFoundError:
            pass
        else:
            if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ScanSecurityError("history_unsupported", "repository")


def prepare_repository(repository):
    # Assert protected original Git metadata ancestry without importing config.
    repository.read_selected_index(repository.common / "config", missing=True, parent_only=True)
    private = repository.directory / "repository.git"
    repository.private = private
    (private / "objects").mkdir(parents=True, mode=0o700)
    (private / "refs").mkdir(mode=0o700)
    sha256 = repository.object_format == "sha256"
    config = b"[core]\nrepositoryformatversion = " + (b"1" if sha256 else b"0") + b"\nbare = true\n"
    if sha256:
        config += b"[extensions]\nobjectformat = sha256\n"
    repository.put(private / "config", config)
    repository.put(private / "HEAD", b"ref: refs/heads/publication-unused\n")
    repository.environment.update(GIT_DIR=str(private), GIT_COMMON_DIR=str(private),
        GIT_INDEX_FILE=str(private / "unused-index"), GIT_OBJECT_DIRECTORY=str(repository.common / "objects"),
        GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1")


class MissingObject(Exception):
    pass


class SpoolCapture(VerifiedCapture):
    """A bounded range in our append-only private spool, safe for nested reads."""
    def chunks(self, offset=0, length=None, chunk_bytes=65536):
        length = self.size - offset if length is None else length
        if offset < 0 or length < 0 or offset + length > self.size or chunk_bytes <= 0:
            raise ScanSecurityError("git_output_invalid", "candidate_read")
        remaining = length
        while remaining:
            self.context.check_deadline()
            self.handle.seek(offset + length - remaining)
            chunk = self.handle.read(min(remaining, chunk_bytes, 65536))
            if not chunk:
                raise ScanSecurityError("git_output_invalid", "candidate_read")
            remaining -= len(chunk)
            yield chunk
        self.context.check_deadline()


class TreeNames:
    """One invocation-private disk index, never an unbounded set of path names."""
    def __init__(self, repository, resources):
        try:
            import sqlite3
        except ImportError:
            raise ScanSecurityError("publication_validation_unavailable", "candidate_read") from None
        self.sqlite = sqlite3
        self.context = repository.context
        self.path = repository.directory / "tree-names.sqlite3"
        self.size = 0
        self.connection = None
        descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
        os.close(descriptor)
        resources.callback(self.close)
        self.connection = sqlite3.connect(self.path, timeout=0, autocommit=True, cached_statements=4)
        # Python 3.14 enables defensive mode, which silently refuses OFF.
        # Only scanner-owned SQL ever reaches this disposable empty database.
        self.connection.setconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE, False)
        self.connection.set_progress_handler(lambda: int(time.monotonic() >= self.context.deadline), 100)
        # This disposable index needs no crash recovery. No WAL, rollback
        # journal, mmap or file-backed SQL temporary store may escape accounting.
        if self.execute("PRAGMA journal_mode=OFF").fetchone() != ("off",):
            raise ScanSecurityError("candidate_read_failed", "candidate_read")
        for statement in ("PRAGMA synchronous=OFF", "PRAGMA mmap_size=0", "PRAGMA cache_size=-64",
                          "PRAGMA cache_spill=ON", "PRAGMA temp_store=MEMORY"):
            self.execute(statement)
        self.execute("CREATE TABLE names(scope INTEGER, name BLOB, PRIMARY KEY(scope,name)) WITHOUT ROWID")
        self.scope = 0

    def account(self):
        size = self.path.stat().st_size
        growth = size - self.size
        self.size = size
        if growth >= 0:
            self.context.charge_temp(growth)
        else:
            self.context.release_temp(-growth)

    def execute(self, sql, parameters=()):
        self.context.check_deadline()
        try:
            cursor = self.connection.execute(sql, parameters)
        except self.sqlite.IntegrityError:
            raise ScanSecurityError("git_output_invalid", "candidate_read") from None
        except self.sqlite.Error:
            self.context.check_deadline()
            raise ScanSecurityError("candidate_read_failed", "candidate_read") from None
        finally:
            self.account()
        self.context.check_deadline()
        return cursor

    def begin(self):
        self.scope += 1
        return self.scope

    def add(self, scope, name):
        self.execute("INSERT INTO names(scope,name) VALUES(?,?)", (scope, name))

    def finish(self, scope):
        self.execute("DELETE FROM names WHERE scope=?", (scope,))

    def close(self):
        try:
            if self.connection is not None:
                self.connection.close()
            self.path.unlink()
        finally:
            self.context.release_temp(self.size)


class HeaderLine:
    """Constant fragments for header syntax, including arbitrarily long idents."""
    def __init__(self):
        self.prefix = bytearray()
        self.length = 0
        self.previous = b""
        self.identity_phase = None
        self.identity_invalid = False
        self.identity_tail = bytearray()

    def feed(self, raw):
        self.length += len(raw)
        self.prefix.extend(raw[:max(0, 256-len(self.prefix))])
        if b"\0" in raw:
            raise ScanSecurityError("git_output_invalid", "candidate_read")
        # The final ' <' starts the email in Git's ident grammar. Names and
        # email bodies need no retained buffer, only delimiter/tail state.
        window = self.previous + raw
        opening = window.rfind(b" <")
        if opening >= 0:
            self.identity_phase = "email"
            self.identity_invalid = False
            self.identity_tail.clear()
            remaining = window[opening+2:]
        else:
            remaining = raw
        if self.identity_phase == "email":
            closing = remaining.find(b">")
            email = remaining if closing < 0 else remaining[:closing]
            self.identity_invalid = self.identity_invalid or b"<" in email
            if closing >= 0:
                self.identity_phase = "tail"
                remaining = remaining[closing+1:]
            else:
                remaining = b""
        if self.identity_phase == "tail":
            if len(self.identity_tail)+len(remaining) > 128:
                self.identity_invalid = True
            self.identity_tail.extend(remaining[:max(0,128-len(self.identity_tail))])
        if raw:
            self.previous = raw[-1:]

    def valid_identity(self):
        # A valid Git timestamp fits a machine integer, so 128 tail bytes do
        # not impose a bound on legal names/emails/signature continuations.
        return (self.identity_phase == "tail" and not self.identity_invalid
                and re.fullmatch(rb" -?[0-9]+ [+-][0-9]{4}", self.identity_tail) is not None)


class ObjectStore:
    def __init__(self, repository, resources):
        self.repository = repository
        self.context = repository.context
        self.handle = resources.enter_context(tempfile.TemporaryFile(mode="w+b"))
        self.objects = {}
        self.verified_objects = 0
        self.external_objects = lambda: 0
        self.verified_bytes = 0
        self.size = 0
        resources.callback(lambda: self.context.release_temp(self.size))
        self.names = TreeNames(repository, resources)
        self.validated_trees = set()

    def capture(self, oid):
        if oid in self.objects:
            return self.objects[oid]
        context = self.context
        validate_storage(self.repository, oid)
        with capture_git(context, ["cat-file", "--batch"], cwd=self.repository.root,
                         input_bytes=oid.encode() + b"\n", deadline=context.deadline) as capture:
            capture.handle.seek(0)
            header = capture.handle.readline(256)
            if header == oid.encode() + b" missing\n" and capture.size == len(header):
                raise MissingObject
            match = re.fullmatch(oid.encode() + rb" (blob|tree|commit|tag) (0|[1-9][0-9]*)\n", header)
            if match is None:
                raise ScanSecurityError("git_output_invalid", "candidate_read")
            kind = match[1].decode()
            size = int(match[2])
            offset = len(header)
            if capture.size != offset + size + 1:
                raise ScanSecurityError("git_output_invalid", "candidate_read")
            capture.handle.seek(offset + size)
            if capture.handle.read(1) != b"\n":
                raise ScanSecurityError("git_output_invalid", "candidate_read")
            digest = hashlib.new(self.repository.object_format)
            digest.update(kind.encode() + b" " + str(size).encode() + b"\0")
            # Do not expose graph or policy bytes until the entire object verifies.
            for chunk in capture.chunks(offset, size):
                digest.update(chunk)
            if digest.hexdigest() != oid:
                raise ScanSecurityError("git_output_invalid", "candidate_read")
            self.verified_objects += 1
            self.verified_bytes += size
            if self.verified_objects + self.external_objects() > context.limits.max_objects:
                raise ScanLimitExceeded("object_count_limit", "candidate_read", measured=self.verified_objects + self.external_objects(), limit=context.limits.max_objects)
            start = self.size
            self.size += size
            self.context.charge_temp(size)
            self.handle.seek(start)
            for chunk in capture.chunks(offset, size):
                self.handle.write(chunk)
            self.handle.flush()
            self.objects[oid] = kind, start, size
        validate_storage(self.repository, oid)
        return self.objects[oid]

    def view(self, oid):
        kind, start, size = self.capture(oid)
        return SpoolCapture(self.context, self.handle, self.size, self.context.deadline, "candidate_read"), start, size

    def header(self, oid):
        capture, start, size = self.view(oid)
        kind = self.objects[oid][0]
        width = 40 if self.repository.object_format == "sha1" else 64
        oid_pattern = rb"[0-9a-f]{" + str(width).encode() + rb"}"
        consumed = number = 0
        rows = []
        parents = set()
        identities = set()
        line = HeaderLine()
        for chunk in capture.chunks(start, size):
            cursor = 0
            while cursor < len(chunk):
                end = chunk.find(b"\n", cursor)
                fragment = chunk[cursor:] if end < 0 else chunk[cursor:end]
                line.feed(fragment)
                consumed += len(fragment)
                if end < 0:
                    break
                consumed += 1
                if not line.length:
                    return rows, consumed
                row = bytes(line.prefix)
                if kind == "commit":
                    if number == 0:
                        rows.append(row)
                    elif row.startswith(b"parent "):
                        if line.length != len(row) or re.fullmatch(rb"parent " + oid_pattern, row) is None:
                            raise ScanSecurityError("git_output_invalid", "candidate_read")
                        parent = row[7:].decode()
                        if parent not in parents:
                            # This bounds retained unique parent IDs by the
                            # existing verified-object budget, never by names or
                            # repeated edge occurrences. Keep first-declared order.
                            if self.capture(parent)[0] != "commit":
                                raise ScanSecurityError("git_output_invalid", "candidate_read")
                            parents.add(parent)
                            rows.append(row)
                    elif row.startswith((b"author ", b"committer ")):
                        identity = row.partition(b" ")[0]
                        if identity in identities or not line.valid_identity():
                            raise ScanSecurityError("git_output_invalid", "candidate_read")
                        identities.add(identity)
                        rows.append(row)
                    elif row.startswith(b"tree "):
                        raise ScanSecurityError("git_output_invalid", "candidate_read")
                elif number < 3:
                    rows.append(row)
                elif row.startswith((b"object ", b"type ", b"tag ")):
                    raise ScanSecurityError("git_output_invalid", "candidate_read")
                number += 1
                line = HeaderLine()
                cursor = end+1
        raise ScanSecurityError("git_output_invalid", "candidate_read")

    def structure(self, oid):
        kind, _, _ = self.capture(oid)
        if kind == "blob":
            return (), None
        if kind == "tree":
            return ((child, "tree" if mode == b"40000" else "blob") for mode, _, child in self.tree(oid)), None
        rows, message = self.header(oid)
        width = 40 if self.repository.object_format == "sha1" else 64
        oid_pattern = rb"[0-9a-f]{" + str(width).encode() + rb"}"
        if kind == "commit":
            if not rows or re.fullmatch(rb"tree " + oid_pattern, rows[0]) is None:
                raise ScanSecurityError("git_output_invalid", "candidate_read")
            authors = [row for row in rows if row.startswith(b"author ")]
            committers = [row for row in rows if row.startswith(b"committer ")]
            if len(authors) != 1 or len(committers) != 1:
                raise ScanSecurityError("git_output_invalid", "candidate_read")
            children = [(rows[0][5:].decode(), "tree")]
            for row in rows[1:]:
                if row.startswith(b"parent "):
                    if re.fullmatch(rb"parent " + oid_pattern, row) is None:
                        raise ScanSecurityError("git_output_invalid", "candidate_read")
                    children.append((row[7:].decode(), "commit"))
                elif row.startswith(b"tree "):
                    raise ScanSecurityError("git_output_invalid", "candidate_read")
            return children, message
        if (len(rows) < 3 or re.fullmatch(rb"object " + oid_pattern, rows[0]) is None
                or rows[1] not in {b"type commit", b"type tree", b"type blob", b"type tag"}
                or not rows[2].startswith(b"tag ") or len(rows[2]) <= 4
                or any(row.startswith((b"object ", b"type ", b"tag ")) for row in rows[3:])):
            raise ScanSecurityError("git_output_invalid", "candidate_read")
        child = rows[0][7:].decode()
        if self.capture(child)[0] != rows[1][5:].decode():
            raise ScanSecurityError("git_output_invalid", "candidate_read")
        return [(child, rows[1][5:].decode())], message

    def tree(self, oid):
        capture, start, size = self.view(oid)
        if self.objects[oid][0] != "tree":
            raise ScanSecurityError("git_output_invalid", "candidate_read")
        width = 20 if self.repository.object_format == "sha1" else 32
        pending = bytearray()
        scope = self.names.begin() if oid not in self.validated_trees else None
        previous = None
        for chunk in capture.chunks(start, size):
            pending.extend(chunk)
            while True:
                end = pending.find(b"\0")
                if end < 0:
                    mode, separator, name = pending.partition(b" ")
                    if separator and len(name) > 4096:
                        raise ScanSecurityError("publication_path_unsupported", "candidate_read", measured=len(name), limit=4096)
                    if not separator and len(mode) > 6:
                        raise ScanSecurityError("git_output_invalid", "candidate_read")
                    break
                if len(pending) < end + 1 + width:
                    break
                header = bytes(pending[:end])
                child = bytes(pending[end + 1:end + 1 + width]).hex()
                del pending[:end + 1 + width]
                mode, separator, name = header.partition(b" ")
                if not separator or mode not in {b"40000", b"100644", b"100755", b"120000", b"160000"}:
                    raise ScanSecurityError("git_output_invalid", "candidate_read")
                if len(name) > 4096:
                    raise ScanSecurityError("publication_path_unsupported", "candidate_read", measured=len(name), limit=4096)
                if (mode == b"160000" or not name or name in {b".", b"..", b".git"} or b"/" in name
                        or b"\\" in name or b"\r" in name or b"\n" in name):
                    raise ScanSecurityError("publication_path_unsupported", "candidate_read")
                order = name + (b"/" if mode == b"40000" else b"\0")
                if previous is not None and order <= previous:
                    raise ScanSecurityError("git_output_invalid", "candidate_read")
                previous = order
                if scope is not None:
                    self.names.add(scope, name)
                yield mode, os.fsdecode(name), child
        if pending:
            raise ScanSecurityError("git_output_invalid", "candidate_read")
        if scope is not None:
            self.names.finish(scope)
            self.validated_trees.add(oid)


def walk_graph(store, tips, excluded, visit=None):
    """DFS retains iterators, never a breadth expansion of repeated OID edges."""
    visited = set()
    frames = [iter((oid, None) for oid in tips)]
    while frames:
        store.context.check_deadline()
        try:
            oid, expected = next(frames[-1])
        except StopIteration:
            frames.pop()
            continue
        kind, _, _ = store.capture(oid)
        if expected is not None and kind != expected:
            raise ScanSecurityError("git_output_invalid", "candidate_read")
        if oid in visited or oid in excluded:
            continue
        children, message = store.structure(oid)
        visited.add(oid)
        if visit is not None:
            visit(oid, kind, children, message)
        frames.append(iter(children))
    return visited


def scan(repository, transaction, build, *, payload_directory=None, retained=None):
    context = repository.context
    budget = ScanBudget(context)
    findings = RetainedFindings()
    report = StreamReport(findings)
    checked = candidates = paths = message_bytes = 0
    failure = None
    selected = set()
    scanned = set()
    logical_blobs = set()
    store = payloads = None
    lfs_scanned = set()
    lfs_seen_paths = set()
    lfs_occurrences = lfs_logical_bytes = 0
    identity = hashlib.sha256(b"publication-scope-v1\0" + bytes.fromhex(transaction.identity))

    def content(oid, label, message=None):
        nonlocal checked, candidates, message_bytes
        if oid in scanned:
            return
        kind, _, size = store.capture(oid)
        capture, start, _ = store.view(oid)
        offset = message or 0
        budget.charge(size - offset)
        if kind == "blob":
            logical_blobs.add(oid)
        else:
            message_bytes += size - offset
        candidates += 1
        snapshot = Snapshot(("publication", label), capture, start + offset, size - offset)
        snapshot.classify()
        scan_line_events(label, full_line_events(snapshot.chunks(), snapshot.classification, context.check_deadline),
                         report, lambda _: False, redact_match, context.check_deadline)
        checked += 1
        scanned.add(oid)
        if kind == "blob":
            payload(oid, label)
        identity.update(oid.encode() + b"\0" + snapshot.digest)
        if report.stopped:
            raise ScanLimitExceeded("findings_limit", "candidate_scan", measured=report.processed, limit=1000)

    def payload(oid, label):
        nonlocal checked, candidates, lfs_occurrences, lfs_logical_bytes
        capture, start, size = store.view(oid)
        declared = pointer(capture, start, size)
        if declared is None:
            return None
        digest, declared_size = declared
        snapshot = payloads.acquire(digest, declared_size, git_objects=store.verified_objects)
        if digest not in lfs_scanned:
            budget.charge(declared_size)
            candidates += 1
            scan_line_events(label, full_line_events(snapshot.chunks(), snapshot.classification, context.check_deadline),
                             report, lambda _: False, redact_match, context.check_deadline)
            checked += 1
            snapshot.capture.handle.close()
            lfs_scanned.add(digest)
            identity.update(b"lfs\0" + digest.encode() + b"\0" + str(declared_size).encode())
        return declared

    def occurrence_tree(tree):
        nonlocal checked, candidates, paths, lfs_occurrences, lfs_logical_bytes
        frames = [("", iter(store.tree(tree)))]
        while frames:
            context.check_deadline()
            prefix, entries = frames[-1]
            try:
                mode, name, child = next(entries)
            except StopIteration:
                frames.pop()
                continue
            path = prefix + name
            path_bytes = len(os.fsencode(path))
            if path_bytes > 4096:
                raise ScanSecurityError("publication_path_unsupported", "candidate_read", measured=path_bytes, limit=4096)
            kind, _, size = store.capture(child)
            if mode == b"40000":
                if kind != "tree":
                    raise ScanSecurityError("git_output_invalid", "candidate_read")
                frames.append((path + "/", iter(store.tree(child))))
                continue
            if kind != "blob":
                raise ScanSecurityError("git_output_invalid", "candidate_read")
            paths += 1
            candidates += 1
            # Charge every logical occurrence, crediting only its first
            # full-content scan's already charged bytes.
            if child in logical_blobs:
                budget.charge(size)
            elif child in baseline:
                budget.charge(size)
            if is_credential_path(path):
                report.record_findings(1, (("credential_path", "critical", path, 1, "[SENSITIVE PATH]"),))
            if child not in baseline:
                selected.add(child)
                content(child, path)
            declared = payload(child, path)
            if declared is not None:
                digest, declared_size = declared
                # Full matching is deduplicated by payload OID; logical bytes
                # retain every outgoing commit/path occurrence.
                if digest in lfs_seen_paths:
                    budget.charge(declared_size)
                lfs_seen_paths.add(digest)
                lfs_occurrences += 1
                lfs_logical_bytes += declared_size
            checked += 1
            identity.update(b"path\0" + os.fsencode(path) + b"\0" + child.encode())
            if report.stopped:
                raise ScanLimitExceeded("findings_limit", "candidate_scan", measured=report.processed, limit=1000)

    baseline = set()
    try:
        local_tips = [row[1].decode() for row in transaction.records if set(row[1]) != {48}]
        if local_tips:
            with contextlib.ExitStack() as resources:
                store = ObjectStore(repository, resources)
                payloads = PayloadStore(repository, resources, directory=payload_directory)
                store.external_objects = lambda: len(payloads.objects)
                # Each baseline contributes exclusions only after its entire graph
                # verified locally. A missing node contributes no partial exclusions.
                remote_tips = dict.fromkeys(row[3].decode() for row in transaction.records if set(row[3]) != {48})
                for old in remote_tips:
                    try:
                        complete = walk_graph(store, [old], baseline)
                    except MissingObject:
                        continue
                    baseline.update(complete)
                direct_trees = set(local_tips)

                def visit(oid, kind, children, message):
                    selected.add(oid)
                    if kind in {"commit", "tag"}:
                        content(oid, kind + ":" + oid, message)
                    elif kind == "blob":
                        content(oid, "blob:" + oid)
                    if kind == "commit":
                        if store.capture(children[0][0])[0] != "tree":
                            raise ScanSecurityError("git_output_invalid", "candidate_read")
                        occurrence_tree(children[0][0])
                    elif kind == "tree" and oid in direct_trees:
                        occurrence_tree(oid)
                    elif kind == "tag" and store.capture(children[0][0])[0] == "tree":
                        occurrence_tree(children[0][0])

                try:
                    walk_graph(store, local_tips, baseline, visit)
                except MissingObject:
                    raise ScanSecurityError("object_missing", "candidate_read") from None
                for digest, snapshot in payloads.objects.items():
                    if digest not in lfs_seen_paths:
                        lfs_occurrences += 1
                        lfs_logical_bytes += snapshot.byte_count
                validate_storage(repository)
                if store.verified_objects + len(payloads.objects) > context.limits.max_objects:
                    raise ScanLimitExceeded("object_count_limit", "candidate_read", measured=store.verified_objects + len(payloads.objects), limit=context.limits.max_objects)
                if retained is not None:
                    retained.extend(payloads.records())
                context.check_deadline()
    except KeyboardInterrupt:
        failure = ScanFailure("cancelled", "candidate_scan")
    except Exception as exc:
        failure = exc if isinstance(exc, ScanFailure) else ScanFailure("internal_error", context.phase)
    complete = failure is None
    counts = dict(candidates=candidates, inspected_snapshots=checked, candidate_bytes=budget.used_bytes,
        capture_bytes=context.capture_bytes, temp_peak_bytes=context.temp_peak_bytes,
        processed_findings=report.processed, retained_findings=len(findings), omitted_findings=max(0, report.processed - len(findings)),
        git_objects=store.verified_objects if store else 0, selected_objects=len(selected), path_occurrences=paths,
        message_bytes=message_bytes, object_body_bytes=store.verified_bytes if store else 0, transaction_bytes=len(transaction.raw),
        lfs_objects=len(payloads.objects) if payloads else 0, lfs_payload_bytes=payloads.bytes if payloads else 0,
        lfs_occurrences=lfs_occurrences, lfs_logical_bytes=lfs_logical_bytes)
    return ScanResult(1, build, POLICY, "outgoing", identity.hexdigest(),
        "incomplete" if not complete else "complete_findings" if report.processed else "complete_clean", complete,
        build_findings_json(findings), counts, round(max(0., time.monotonic() - context.started), 6),
        failure.cause if failure else "findings" if report.processed else "clean", failure=failure, root=repository.root)

"""Bounded historical display state. No detector, Git process, or content reads.

The report is never a cache or an authorization receipt. Readers neither lock
nor repair storage; only explicit scans write. Deadlines bound our loops and
lock acquisition, not an uninterruptible kernel filesystem operation.
"""
from __future__ import annotations

import contextlib
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time

SCHEMA = "scan_secrets_status_v1"
MAX_REPORT_BYTES = 65536
MAX_METADATA_BYTES = 4096
MAX_PARENTS = 128
IO_SECONDS = 2.0


class StatusError(Exception):
    def __init__(self, reason):
        self.reason = reason


def deadline_check(deadline):
    if time.monotonic() >= deadline:
        raise StatusError("status_timeout")


def linked(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def bounded_read(path, limit, deadline, *, missing=False):
    deadline_check(deadline)
    try:
        info = path.lstat()
    except FileNotFoundError:
        if missing:
            return None
        raise StatusError("repository_metadata_unavailable") from None
    if linked(info) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
        raise StatusError("repository_metadata_invalid")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
    try:
        opened = os.fstat(descriptor)
        identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        if identity(info) != identity(opened):
            raise StatusError("repository_metadata_invalid")
        raw = bytearray()
        while len(raw) <= limit:
            deadline_check(deadline)
            chunk = os.read(descriptor, min(16384, limit + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
        if len(raw) > limit or identity(opened) != identity(os.fstat(descriptor)):
            raise StatusError("repository_metadata_invalid")
        return bytes(raw)
    finally:
        os.close(descriptor)


def canonical_directory(path, deadline):
    deadline_check(deadline)
    resolved = path.resolve(strict=True)
    if not sys_platform_darwin():
        return resolved
    # APFS may be case sensitive or insensitive. F_GETPATH supplies the actual
    # spelling without guessing by lowercasing paths or enumerating directories.
    import fcntl
    descriptor = os.open(resolved, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        raw = fcntl.fcntl(descriptor, fcntl.F_GETPATH, b"\0" * 1024)
        path_bytes, separator, _ = raw.partition(b"\0")
        if not separator or not path_bytes:
            raise StatusError("repository_metadata_invalid")
        return Path(os.fsdecode(path_bytes))
    finally:
        os.close(descriptor)


def _metadata_path(raw, relative_to):
    try:
        text = os.fsdecode(raw.rstrip(b"\r\n"))
        if not text or "\n" in text or "\r" in text or "\0" in text:
            raise ValueError
        path = Path(text)
        return (path if path.is_absolute() else relative_to / path).resolve(strict=True)
    except (OSError, ValueError, RuntimeError):
        raise StatusError("repository_metadata_invalid") from None


def discover(requested, deadline):
    """Identify only explicit worktree metadata; ignore ambient GIT_* variables."""
    try:
        current = canonical_directory(Path(requested), deadline)
    except (FileNotFoundError, NotADirectoryError):
        return None
    if not current.is_dir():
        return None
    for _ in range(MAX_PARENTS):
        deadline_check(deadline)
        marker = current / ".git"
        try:
            info = marker.lstat()
        except FileNotFoundError:
            if current.parent == current:
                return None
            current = current.parent
            continue
        if linked(info):
            raise StatusError("repository_metadata_invalid")
        if stat.S_ISDIR(info.st_mode):
            gitdir = canonical_directory(marker, deadline)
        elif stat.S_ISREG(info.st_mode):
            raw = bounded_read(marker, MAX_METADATA_BYTES, deadline)
            if not raw.startswith(b"gitdir: "):
                raise StatusError("repository_metadata_invalid")
            gitdir = canonical_directory(_metadata_path(raw[8:], current), deadline)
        else:
            raise StatusError("repository_metadata_invalid")
        info = gitdir.lstat()
        if linked(info) or not stat.S_ISDIR(info.st_mode):
            raise StatusError("repository_metadata_invalid")
        head = bounded_read(gitdir / "HEAD", MAX_METADATA_BYTES, deadline)
        if not head or b"\0" in head:
            raise StatusError("repository_metadata_invalid")
        common_raw = bounded_read(gitdir / "commondir", MAX_METADATA_BYTES, deadline, missing=True)
        common = canonical_directory(_metadata_path(common_raw, gitdir), deadline) if common_raw is not None else gitdir
        info = common.lstat()
        if linked(info) or not stat.S_ISDIR(info.st_mode):
            raise StatusError("repository_metadata_invalid")
        return repository_identity(current, gitdir, common)
    raise StatusError("repository_metadata_limit")


def repository_identity(root, gitdir, common):
    identity = hashlib.sha256(os.fsencode(os.path.normcase(str(common))) + b"\0" +
                              os.fsencode(os.path.normcase(str(gitdir)))).hexdigest()
    return {"root": root, "gitdir": gitdir, "common": common, "identity": identity}


def envelope(outcome, reason, *, last_scan=None, identity=None):
    return {"schema": SCHEMA, "historical": True, "authorizes_publication": False,
            "outcome": outcome, "reason": reason, "worktree_identity": identity,
            "last_scan": last_scan,
            "message": "Last scan only; current content has not been checked by status. This never grants permission to publish."}


def read_status(requested, data_root, bundle):
    deadline = time.monotonic() + IO_SECONDS
    try:
        repository = discover(requested, deadline)
        if repository is None:
            return envelope("not_scanned", "not_repository"), 0
        with Store(data_root(), repository, bundle, deadline, write=False) as store:
            last = store.read()
        return envelope("last_scan" if last else "not_scanned", "last_scan_recorded" if last else "report_missing",
                        last_scan=last, identity=repository["identity"]), 0
    except StatusError as error:
        return envelope("unavailable", error.reason), 2
    except (OSError, ValueError, RuntimeError):
        return envelope("unavailable", "status_unavailable"), 2


COUNT_KEYS = frozenset(("candidates", "inspected_snapshots", "candidate_bytes", "capture_bytes", "temp_peak_bytes",
                        "processed_findings", "retained_findings", "omitted_findings"))
REASONS = frozenset(("clean", "findings", "git_unavailable", "audit_unavailable", "input_invalid", "git_failed",
    "git_capture_failed", "git_descendant_running", "git_head_invalid", "git_output_invalid", "repository_unavailable",
    "scan_timeout", "git_timeout", "snapshot_count_limit", "total_bytes_limit", "git_output_limit", "git_input_limit",
    "candidate_unsafe", "candidate_read_failed", "log_unavailable", "log_unsafe", "log_lock_timeout",
    "log_configuration_invalid", "log_record_limit", "capture_bytes_limit", "temporary_bytes_limit",
    "conversion_unsupported", "candidate_changed", "index_unresolved", "index_flags_unsupported", "cleanup_failed",
    "findings_limit", "internal_error", "runtime_unavailable", "cancelled", "transaction_invalid", "transaction_interactive",
    "transaction_unavailable", "transaction_timeout", "transaction_bytes_limit", "transaction_records_limit",
    "object_count_limit", "publication_path_unsupported", "history_unsupported", "object_missing", "lfs_unsupported", "lfs_pointer_invalid", "lfs_payload_invalid", "lfs_payload_unavailable", "handoff_invalid", "dispatch_platform_unsupported", "publication_validation_unavailable"))
RECORD_KEYS = frozenset(("schema", "worktree_identity", "completed_at", "completed_ns", "completion_order_ns",
    "scanner_version", "policy_version", "build", "scope", "scope_identity", "outcome", "security_outcome",
    "coverage_complete", "counts", "reason", "audit_outcome", "status_outcome"))


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise StatusError("status_corrupt")
        result[key] = value
    return result


def validate_record(value, identity):
    """Only documented safe scalars/counts survive an existing report read."""
    try:
        publication = type(value) is dict and value.get("policy_version") == "publication_v1"
        publication_keys = {"action", "transaction_identity", "destination_identity", "budget_profile", "accounting_units", "limits", "budget_identity"}
        if type(value) is not dict or value.keys() != RECORD_KEYS | (publication_keys if publication else set()):
            raise ValueError
        if publication:
            if value["action"] != "pre-push" or value["budget_profile"] != "publication":
                raise ValueError
            for key in ("transaction_identity", "destination_identity", "budget_identity"):
                if type(value[key]) is not str or re.fullmatch(r"[0-9a-f]{64}", value[key]) is None:
                    raise ValueError
            units = dict(max_objects="objects", max_candidate_bytes="bytes", max_seconds="seconds", max_capture_bytes="bytes", max_temp_bytes="bytes")
            if value["accounting_units"] != units or type(value["limits"]) is not dict or value["limits"].keys() != units.keys():
                raise ValueError
            ranges = dict(max_objects=(1,100000), max_candidate_bytes=(1048576,1073741824), max_seconds=(1,600),
                          max_capture_bytes=(1048576,2147483648), max_temp_bytes=(1048576,3221225472))
            for key, (low, high) in ranges.items():
                number = value["limits"][key]
                if type(number) not in ((int,float) if key == "max_seconds" else (int,)) or not low <= number <= high:
                    raise ValueError
        if value["schema"] != "scan_secrets_last_scan_v1" or value["worktree_identity"] != identity:
            raise ValueError
        if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value["scanner_version"]) is None or len(value["scanner_version"]) > 32:
            raise ValueError
        if ((value["policy_version"], value["scope"]) not in {("pending_snapshots_v1", "worktree"), ("pending_snapshots_v1", "index"), ("selected_index_v1", "index"), ("selected_staged_v1", "index"), ("publication_v1", "outgoing")}):
            raise ValueError
        for key in ("build", "scope_identity"):
            if value[key] is not None and re.fullmatch(r"[0-9a-f]{64}", value[key]) is None:
                raise ValueError
        for key in ("completed_ns", "completion_order_ns"):
            if type(value[key]) is not int or not 0 < value[key] < 2**63:
                raise ValueError
        if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z", value["completed_at"]) is None:
            raise ValueError
        datetime.fromisoformat(value["completed_at"].replace("Z", "+00:00"))
        if type(value["coverage_complete"]) is not bool or value["reason"] not in REASONS:
            raise ValueError
        if value["outcome"] not in {"complete_clean", "complete_findings", "incomplete"}:
            raise ValueError
        if value["audit_outcome"] not in {"written", "failed", "not_attempted"} or value["status_outcome"] != "written":
            raise ValueError
        counts = value["counts"]
        publication_counts = {"git_objects", "selected_objects", "path_occurrences", "message_bytes", "object_body_bytes", "transaction_bytes"}
        lfs_counts = {"lfs_objects", "lfs_payload_bytes", "lfs_occurrences", "lfs_logical_bytes"}
        expected_counts = COUNT_KEYS | (publication_counts if publication else set())
        # Historical pre-LFS publication records remain informational. Accept
        # exactly either known shape; partial/unknown fields still corrupt it.
        if type(counts) is not dict or (counts.keys() != expected_counts and
                (not publication or counts.keys() != expected_counts | lfs_counts)):
            raise ValueError
        if any(type(number) is not int or not 0 <= number < 2**63 for number in counts.values()):
            raise ValueError
        expected_security = "findings" if counts["processed_findings"] else "clean" if value["coverage_complete"] else "incomplete"
        if value["security_outcome"] != expected_security:
            raise ValueError
        if value["outcome"] != "incomplete":
            expected = "complete_findings" if counts["processed_findings"] else "complete_clean"
            if not value["coverage_complete"] or value["outcome"] != expected or value["audit_outcome"] != "written":
                raise ValueError
        if counts["retained_findings"] + counts["omitted_findings"] != counts["processed_findings"]:
            raise ValueError
        return value
    except (ValueError, TypeError, KeyError, OverflowError):
        raise StatusError("status_corrupt") from None


def _private(info, *, directory=False):
    if linked(info) or not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)):
        raise StatusError("status_unsafe")
    if not directory and info.st_nlink != 1:
        raise StatusError("status_unsafe")
    if os.name == "posix" and (info.st_uid != os.geteuid() or info.st_mode & 0o077):
        raise StatusError("status_permissions")


def _windows_private(handle, *, create=False, owner_only=True):
    """Apply/verify a protected DACL containing only the current owner SID.

    No PowerShell, external command, inherited broad ACL, or mode-bit claim is
    used. Native Windows execution is separately required validation.
    """
    if os.name != "nt":
        return
    import ctypes
    from ctypes import wintypes
    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    pointer = ctypes.c_void_p
    advapi.OpenProcessToken.argtypes = (wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE))
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    token = wintypes.HANDLE()
    if not advapi.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(token)):
        raise StatusError("status_permissions")
    try:
        required = wintypes.DWORD()
        advapi.GetTokenInformation(token, 1, None, 0, ctypes.byref(required))
        buffer = ctypes.create_string_buffer(required.value)
        if not advapi.GetTokenInformation(token, 1, buffer, len(buffer), ctypes.byref(required)):
            raise StatusError("status_permissions")
        sid = ctypes.cast(buffer, ctypes.POINTER(pointer))[0]
        text = wintypes.LPWSTR()
        advapi.ConvertSidToStringSidW.argtypes = (pointer, ctypes.POINTER(wintypes.LPWSTR))
        if not advapi.ConvertSidToStringSidW(sid, ctypes.byref(text)):
            raise StatusError("status_permissions")
        try:
            owner = text.value
        finally:
            kernel.LocalFree(ctypes.cast(text, pointer))
    finally:
        kernel.CloseHandle(token)
    descriptor = pointer()
    advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(pointer), pointer)
    if create:
        if not advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW("O:" + owner + "D:P(A;;FA;;;" + owner + ")", 1, ctypes.byref(descriptor), None):
            raise StatusError("status_permissions")
        try:
            acl, present, defaulted = pointer(), wintypes.BOOL(), wintypes.BOOL()
            advapi.GetSecurityDescriptorDacl.argtypes = (pointer, ctypes.POINTER(wintypes.BOOL), ctypes.POINTER(pointer), ctypes.POINTER(wintypes.BOOL))
            if not advapi.GetSecurityDescriptorDacl(descriptor, ctypes.byref(present), ctypes.byref(acl), ctypes.byref(defaulted)) or not present or not acl:
                raise StatusError("status_permissions")
            advapi.SetSecurityInfo.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, pointer, pointer, pointer, pointer)
            advapi.SetSecurityInfo.restype = wintypes.DWORD
            if advapi.SetSecurityInfo(handle, 1, 0x80000005, sid, None, acl, None):
                raise StatusError("status_permissions")
        finally:
            kernel.LocalFree(descriptor)
    actual_owner, acl, descriptor = pointer(), pointer(), pointer()
    advapi.GetSecurityInfo.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD,
        ctypes.POINTER(pointer), pointer, ctypes.POINTER(pointer), pointer, ctypes.POINTER(pointer))
    advapi.GetSecurityInfo.restype = wintypes.DWORD
    if advapi.GetSecurityInfo(handle, 1, 5, ctypes.byref(actual_owner), None, ctypes.byref(acl), None, ctypes.byref(descriptor)):
        raise StatusError("status_permissions")
    try:
        advapi.EqualSid.argtypes = (pointer, pointer)
        if not advapi.EqualSid(actual_owner, sid):
            raise StatusError("status_permissions")
        if not owner_only:
            return  # The audit writer owns the app parent; status owns its child.
        if not acl:
            raise StatusError("status_permissions")
        # ACL header: revision/reserved/size/count/reserved, followed by ACEs.
        header = ctypes.string_at(acl, 8)
        if int.from_bytes(header[4:6], "little") != 1:
            raise StatusError("status_permissions")
        ace = pointer()
        advapi.GetAce.argtypes = (pointer, wintypes.DWORD, ctypes.POINTER(pointer))
        if not advapi.GetAce(acl, 0, ctypes.byref(ace)):
            raise StatusError("status_permissions")
        prefix = ctypes.string_at(ace, 8)
        if prefix[0] != 0 or int.from_bytes(prefix[4:8], "little") != 0x1f01ff or not advapi.EqualSid(pointer(ace.value + 8), sid):
            raise StatusError("status_permissions")
    finally:
        kernel.LocalFree(descriptor)


def _safe_ancestors(path, deadline):
    """Reject redirected user locations, allowing only macOS system aliases."""
    current = Path(path.anchor)
    for component in path.parts[1:]:
        deadline_check(deadline)
        current = current / component
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if linked(info):
            if not (sys_platform_darwin() and str(current) in {"/var", "/tmp"} and info.st_uid == 0):
                raise StatusError("status_unsafe")


def sys_platform_darwin():
    import sys
    return sys.platform == "darwin"


def inside_directory(path, directory, deadline):
    if path.is_relative_to(directory):
        return True
    root = directory.stat()
    # Path spelling is insufficient on case-insensitive volumes. Compare the
    # existing ancestors without following a user root to canonicalize it again.
    for ancestor in (path, *path.parents):
        deadline_check(deadline)
        try:
            info = ancestor.stat()
        except FileNotFoundError:
            continue
        if (info.st_dev, info.st_ino) == (root.st_dev, root.st_ino):
            return True
    return False


class Store:
    """A private directory handle anchors POSIX report operations after checks."""
    def __init__(self, data_root, repository, bundle, deadline, *, write):
        self.deadline, self.write, self.repository = deadline, write, repository
        raw = Path(data_root)
        if not raw.is_absolute():
            raise StatusError("status_location_invalid")
        raw = Path(os.path.abspath(raw))
        _safe_ancestors(raw, deadline)
        # Canonicalize only the trusted macOS system prefix. Resolving the
        # user-selected hierarchy again would follow an ancestor substituted
        # after validation, defeating the no-follow directory-handle walk.
        if sys_platform_darwin():
            for alias in (Path("/var"), Path("/tmp")):
                if raw.is_relative_to(alias):
                    raw = alias.resolve(strict=True) / raw.relative_to(alias)
                    break
        self.path = raw / "status"
        for forbidden in (repository["root"], Path(bundle).resolve()):
            if inside_directory(self.path, forbidden, deadline):
                raise StatusError("status_location_invalid")
        self.name = repository["identity"] + ".json"
        self.fd = None
        self.native = None
        self.resources = contextlib.ExitStack()
        self.missing = False

    def __enter__(self):
        try:
            if os.name == "posix":
                descriptor = os.open(self.path.anchor, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    current = Path(self.path.anchor)
                    for component in self.path.parts[1:]:
                        deadline_check(self.deadline)
                        current = current / component
                        if self.write:
                            try:
                                os.mkdir(component, 0o700, dir_fd=descriptor)
                            except FileExistsError:
                                pass
                        try:
                            next_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
                        except FileNotFoundError:
                            self.missing = True
                            return self
                        os.close(descriptor)
                        descriptor = next_fd
                        if current in {self.path.parent, self.path}:
                            _private(os.fstat(descriptor), directory=True)
                    self.fd, descriptor = descriptor, None
                finally:
                    if descriptor is not None:
                        os.close(descriptor)
                return self
            from .scan_native_file import WindowsDirectoryHandles
            self.native = WindowsDirectoryHandles(self.resources)
            self.native.pin_root(Path(self.path.anchor))
            current = Path(self.path.anchor)
            for component in self.path.parts[1:]:
                current = current / component
                boundary = current in {self.path.parent, self.path}
                # Validation rights suffice on existing parents. Setting owner
                # and DACL is confined to an exclusively created status object.
                while True:
                    deadline_check(self.deadline)
                    try:
                        created = self.native.descend(component, access=0x20000 if boundary else 0)
                        break
                    except FileNotFoundError:
                        if not self.write:
                            self.missing = True
                            return self
                        try:
                            created = self.native.descend(component, create=True, exclusive=True,
                                access=0xe0000 if boundary else 0)
                            break
                        except FileExistsError:
                            continue
                if boundary:
                    _windows_private(self.native.parent, create=created, owner_only=current == self.path)
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *args):
        try:
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
        finally:
            self.resources.close()

    def info(self, name):
        if self.native is not None:
            info = self.native.stat(name)
            if info is None:
                raise FileNotFoundError
            return info
        return os.stat(name, dir_fd=self.fd, follow_symlinks=False)

    def open(self, name, flags):
        while True:
            deadline_check(self.deadline)
            try:
                info = self.info(name)
            except FileNotFoundError:
                info = None
            if info is not None:
                _private(info)
            created = info is None and bool(flags & os.O_CREAT)
            open_flags = flags | (os.O_EXCL if created else 0)
            open_flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
            try:
                descriptor = (os.open(name, open_flags, 0o600, dir_fd=self.fd) if self.native is None else
                    self.native.open(name, open_flags, access=0xe0000 if created else 0x20000,
                        share_delete=name == self.name and flags & os.O_ACCMODE == os.O_RDONLY))
                break
            except FileExistsError:
                if flags & os.O_EXCL:
                    raise
                # Another explicit writer created the stable lock first. Retry
                # through all existing-file checks without changing its ACL.
        try:
            opened = os.fstat(descriptor)
            _private(opened)
            if self.native is not None:
                import msvcrt
                _windows_private(msvcrt.get_osfhandle(descriptor), create=created)
            if self.native is None and info is not None and (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                raise StatusError("status_unsafe")
            return descriptor
        except BaseException:
            os.close(descriptor)
            raise

    def read(self):
        if self.missing:
            return None
        try:
            descriptor = self.open(self.name, os.O_RDONLY)
        except FileNotFoundError:
            return None
        try:
            before = os.fstat(descriptor)
            if before.st_size > MAX_REPORT_BYTES:
                raise StatusError("status_oversized")
            raw = bytearray()
            while len(raw) <= MAX_REPORT_BYTES:
                deadline_check(self.deadline)
                chunk = os.read(descriptor, min(16384, MAX_REPORT_BYTES + 1 - len(raw)))
                if not chunk:
                    break
                raw.extend(chunk)
            after = os.fstat(descriptor)
            if len(raw) > MAX_REPORT_BYTES:
                raise StatusError("status_oversized")
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise StatusError("status_corrupt")
        finally:
            os.close(descriptor)
        try:
            return validate_record(json.loads(raw, object_pairs_hook=unique_object), self.repository["identity"])
        except (ValueError, UnicodeError, RecursionError):
            raise StatusError("status_corrupt") from None

    def replace(self, record):
        raw = (json.dumps(validate_record(record, self.repository["identity"]), ensure_ascii=True, separators=(",", ":")) + "\n").encode("ascii")
        if len(raw) > MAX_REPORT_BYTES:
            raise StatusError("status_oversized")
        lock = self.open(self.name + ".lock", os.O_RDWR | os.O_CREAT)
        locked = False
        temporary = None
        try:
            while True:
                deadline_check(self.deadline)
                try:
                    if os.name == "posix":
                        import fcntl
                        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    else:
                        import msvcrt
                        msvcrt.locking(lock, msvcrt.LK_NBLCK, 1)
                    locked = True
                    break
                except (BlockingIOError, PermissionError):
                    time.sleep(min(0.02, max(0, self.deadline - time.monotonic())))
            try:
                previous = self.read()
            except StatusError as error:
                if error.reason not in {"status_corrupt", "status_oversized"}:
                    raise
                previous = None  # An explicit check repairs malformed display bytes.
            if previous is not None and (previous["completed_ns"], previous["completion_order_ns"]) > (record["completed_ns"], record["completion_order_ns"]):
                return "superseded"
            temporary = self.name + "." + os.urandom(16).hex() + ".tmp"
            descriptor = self.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
            try:
                offset = 0
                while offset < len(raw):
                    deadline_check(self.deadline)
                    written = os.write(descriptor, raw[offset:])
                    if written <= 0:
                        raise StatusError("status_unavailable")
                    offset += written
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            deadline_check(self.deadline)
            # Recheck before replacement, never chmod or overwrite linked targets.
            try:
                _private(self.info(self.name))
            except FileNotFoundError:
                pass
            if self.fd is not None:
                os.replace(temporary, self.name, src_dir_fd=self.fd, dst_dir_fd=self.fd)
            else:
                self.native.replace(temporary, self.name)
            temporary = None
            return "written"
        finally:
            if temporary is not None:
                try:
                    if self.fd is not None:
                        os.unlink(temporary, dir_fd=self.fd)
                    else:
                        self.native.remove(temporary)
                except OSError:
                    pass
            if locked:
                if os.name == "posix":
                    import fcntl
                    fcntl.flock(lock, fcntl.LOCK_UN)
                else:
                    import msvcrt
                    os.lseek(lock, 0, os.SEEK_SET)
                    msvcrt.locking(lock, msvcrt.LK_UNLCK, 1)
            os.close(lock)


def save_status(requested, data_root, bundle, result, *, version, captured_repository=None):
    completed_ns, completion_order_ns = time.time_ns(), time.monotonic_ns()
    deadline = time.monotonic() + IO_SECONDS
    try:
        repository = (repository_identity(**captured_repository) if captured_repository is not None
                      else discover(requested, deadline))
        if repository is None:
            raise StatusError("not_repository")
        counts = result.get("counts", {key: 0 for key in COUNT_KEYS})
        coverage = result.get("coverage_complete", False)
        record = {"schema": "scan_secrets_last_scan_v1", "worktree_identity": repository["identity"],
            "completed_ns": completed_ns, "completion_order_ns": completion_order_ns,
            "completed_at": datetime.fromtimestamp(completed_ns / 1_000_000_000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "scanner_version": version, "policy_version": result.get("policy_version", "pending_snapshots_v1"),
            "build": result.get("build"), "scope": result["scope"], "scope_identity": result.get("scope_identity"),
            "outcome": result["outcome"], "security_outcome": "findings" if counts["processed_findings"] else "clean" if coverage else "incomplete",
            "coverage_complete": coverage, "counts": counts, "reason": result["reason"],
            "audit_outcome": result.get("audit_outcome", "not_attempted"), "status_outcome": "written"}
        if record["policy_version"] == "publication_v1":
            for key in ("action", "transaction_identity", "destination_identity", "budget_profile", "accounting_units", "limits", "budget_identity"):
                record[key] = result[key]
        with Store(data_root(), repository, bundle, deadline, write=True) as store:
            return store.replace(record), "status_saved"
    except StatusError as error:
        return "failed", error.reason
    except (OSError, ValueError, RuntimeError):
        return "failed", "status_unavailable"

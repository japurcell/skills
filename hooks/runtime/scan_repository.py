"""CLI-owned protected repository metadata, raw index and attribute policy.

Only discovery and config queries see the original Git directory. Content
acquisition uses a private config/index/HEAD with no executable drivers. Object
reads borrow the original object store, with replacements and lazy fetch off.
"""
from __future__ import annotations

import contextlib
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile

from .scan_types import GitCommandError, ScanSecurityError, ScanLimitExceeded
from .scan_git import capture_git, has_head, run_git, _worktree_descriptor


class NotRepository(Exception):
    pass


class ProtectedRepository:
    def __init__(self, context, requested, *, selected_index=None, capture_selected_index=False, publication=False):
        self.publication = publication
        self.capture_selected_index = capture_selected_index
        self.selected_index = selected_index
        self.context = context
        self.requested = Path(requested).resolve()
        self.executable = shutil.which("git")
        self.resources = contextlib.ExitStack()
        self.charged = 0
        self.environment = {}
        self.root = self.requested

    def __enter__(self):
        try:
            self.prepare()
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *args):
        self.context.repository_context = None
        try:
            self.resources.close()
        finally:
            self.context.release_temp(self.charged)

    def put(self, path, raw):
        self.context.check_deadline()
        self.context.charge_temp(len(raw))
        self.charged += len(raw)
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with path.open("xb") as handle:
            os.chmod(path, 0o600)
            handle.write(raw)

    def remove(self, path):
        size = path.stat().st_size
        path.unlink()
        self.charged -= size
        self.context.release_temp(size)

    def read(self, path, *, missing=False, descriptor=None, maximum=None):
        try:
            info = path.lstat() if descriptor is None else os.fstat(descriptor)
        except FileNotFoundError:
            if missing:
                return None
            raise
        if (not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_file_attributes", 0) & 0x400):
            raise ScanSecurityError("candidate_unsafe", "repository")
        limit = self.context.limits.max_capture_bytes if maximum is None else min(maximum, self.context.limits.max_capture_bytes)
        if info.st_size > limit:
            raise ScanLimitExceeded("git_output_limit", "repository", measured=info.st_size, limit=limit)
        descriptor = (os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
                      if descriptor is None else os.dup(descriptor))
        with os.fdopen(descriptor, "rb") as handle:
            opened = os.fstat(handle.fileno())
            identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
            if identity(info) != identity(opened):
                raise ScanSecurityError("candidate_changed", "repository")
            raw = bytearray()
            while True:
                self.context.check_deadline()
                chunk = handle.read(min(65536, limit + 1 - len(raw)))
                if not chunk:
                    break
                raw.extend(chunk)
                self.context.charge_capture(len(chunk))
                if len(raw) > limit:
                    raise ScanLimitExceeded("git_output_limit", "repository", measured=len(raw), limit=limit)
            if identity(opened) != identity(os.fstat(handle.fileno())):
                raise ScanSecurityError("candidate_changed", "repository")
        return bytes(raw)

    @contextlib.contextmanager
    def open_selected(self, path, *, missing=False, parent_only=False):
        """Hold every metadata ancestor and return a non-following leaf descriptor."""
        if sys.platform == "darwin":
            for alias in (Path("/tmp"), Path("/var")):
                if path.is_relative_to(alias):
                    info = alias.lstat()
                    if stat.S_ISLNK(info.st_mode) and info.st_uid == 0:
                        path = alias.resolve(strict=True) / path.relative_to(alias)
                    break
        with contextlib.ExitStack() as resources:
            parts = path.relative_to(Path(path.anchor)).parts
            if not parts:
                raise ScanSecurityError("candidate_unsafe", "git_index")
            if os.name == "nt":
                from .scan_native_file import WindowsDirectoryHandles
                native = WindowsDirectoryHandles(resources)
                native.pin_root(Path(path.anchor))
                for part in parts[:-1]:
                    self.context.check_deadline()
                    native.descend(part)
                opener = lambda: native.open(parts[-1], os.O_RDONLY)
            else:
                parent = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
                resources.callback(os.close, parent)
                for part in parts[:-1]:
                    self.context.check_deadline()
                    parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                    resources.callback(os.close, parent)
                opener = lambda: os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
            if parent_only:
                # Publication needs this held ancestry, not unused config bytes.
                yield None
                return
            try:
                descriptor = opener()
            except FileNotFoundError:
                if missing:
                    yield None
                    return
                raise
            resources.callback(os.close, descriptor)
            yield descriptor

    def read_selected_index(self, path, *, missing, maximum=None, parent_only=False):
        with self.open_selected(path, missing=missing, parent_only=parent_only) as descriptor:
            if descriptor is None:
                return None
            return self.read(path, descriptor=descriptor, maximum=maximum)

    def query(self, *args, cwd=None, allow_nonzero=False, data=None):
        if self.publication:
            with capture_git(self.context, list(args), cwd=cwd or self.root, deadline=self.context.deadline, input_bytes=data) as capture:
                if capture.size > 65536:
                    raise GitCommandError("git_output_invalid", "repository")
                return b"".join(capture.chunks())
        return run_git(self.context, list(args), cwd=cwd or self.root,
                       deadline=self.context.deadline, allow_nonzero=allow_nonzero,
                       input_bytes=data, text=False)

    def prepare(self):
        if not self.requested.is_dir():
            raise NotRepository
        if not self.executable:
            raise GitCommandError("git_unavailable", "repository")
        directory = Path(self.resources.enter_context(tempfile.TemporaryDirectory(prefix="scan-checkpoint-")))
        self.directory = directory
        home = directory / "home"
        home.mkdir(mode=0o700)
        keys = ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "TMPDIR")
        self.environment = {key: os.environ[key] for key in keys if key in os.environ}
        self.environment.update(PATH=os.pathsep.join(dict.fromkeys([str(Path(self.executable).parent), os.defpath])),
            HOME=str(home), USERPROFILE=str(home), XDG_CONFIG_HOME=str(home),
            GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull, GIT_CONFIG_NOSYSTEM="1",
            GIT_ATTR_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="", GIT_PAGER="cat",
            GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0", LC_ALL="C")
        settings = {"core.hooksPath": os.devnull, "core.fsmonitor": "false", "core.untrackedCache": "false",
                    "core.attributesFile": os.devnull, "core.pager": "cat", "core.quotePath": "true",
                    "maintenance.auto": "false", "gc.auto": "0"}
        self.environment["GIT_CONFIG_COUNT"] = str(len(settings))
        for index, (key, value) in enumerate(settings.items()):
            self.environment[f"GIT_CONFIG_KEY_{index}"] = key
            self.environment[f"GIT_CONFIG_VALUE_{index}"] = value
        self.context.repository_context = self
        # rev-parse does not refresh the index, run converters or invoke hooks.
        # Only these non-content discovery queries see local configuration.
        try:
            raw = self.query("rev-parse", "--path-format=absolute", "--show-toplevel", "--absolute-git-dir", "--git-common-dir", "--show-object-format", cwd=self.requested)
        except GitCommandError as exc:
            if exc.cause == "git_failed" and exc.numbers.get("exit_status") == 128:
                if not any((parent / ".git").exists() for parent in (self.requested, *self.requested.parents)):
                    raise NotRepository from None
            raise
        rows = raw.splitlines()
        if len(rows) != 4 or rows[3] not in {b"sha1", b"sha256"}:
            raise GitCommandError("git_output_invalid", "repository")
        self.root, gitdir, common = (Path(os.fsdecode(value)).resolve(strict=True) for value in rows[:3])
        self.gitdir, self.common = gitdir, common
        self.object_format = rows[3].decode("ascii")
        if self.publication:
            from .scan_publication import prepare_repository
            prepare_repository(self)
            return
        index_path = gitdir / "index"
        if self.capture_selected_index:
            if self.selected_index is not None:
                if not self.selected_index or "\0" in self.selected_index:
                    raise ScanSecurityError("candidate_unsafe", "git_index")
                index_path = Path(os.path.abspath(self.selected_index))
            index = self.read_selected_index(index_path, missing=self.selected_index is None)
        else:
            index = self.read(index_path, missing=True)
        self.index_identity = hashlib.sha256(b"selected-index-v1\0" + (index if index is not None else b"absent")).hexdigest()
        # Git loads config.worktree only when its extension is enabled. Scope
        # labels retain that precedence without importing command overrides or
        # invoking --worktree in an ordinary multi-worktree repository.
        config = self.query("config", "--includes", "--null", "--show-scope", "--list")
        scoped = config.split(b"\0")
        if scoped[-1] or len(scoped) % 2 != 1:
            raise GitCommandError("git_output_invalid", "repository")
        selected = {}
        for offset in range(0, len(scoped) - 1, 2):
            scope, record = scoped[offset:offset + 2]
            if scope not in {b"system", b"global", b"local", b"worktree", b"command"} or not record:
                raise GitCommandError("git_output_invalid", "repository")
            if scope not in {b"local", b"worktree"}:
                continue
            key, separator, value = record.partition(b"\n")
            if not separator:
                value = b"true"
            key = key.lower()
            if key in {b"core.autocrlf", b"diff.algorithm", b"diff.indentheuristic", b"core.attributesfile", b"core.excludesfile"}:
                selected[key] = value
        self.default_conversion = selected.get(b"core.autocrlf", b"false").lower()
        if self.default_conversion not in {b"false", b"no", b"off", b"0", b"true", b"yes", b"on", b"1", b"input"}:
            raise GitCommandError("git_output_invalid", "repository")
        self.algorithm = selected.get(b"diff.algorithm", b"myers").lower()
        self.indent = selected.get(b"diff.indentheuristic", b"true").lower()
        if self.algorithm not in {b"default", b"myers", b"minimal", b"patience", b"histogram"} or self.indent not in {b"true", b"yes", b"on", b"1", b"false", b"no", b"off", b"0"}:
            raise GitCommandError("git_output_invalid", "repository")
        self.extra_attributes = None
        if b"core.attributesfile" in selected:
            attribute_path = Path(os.fsdecode(selected[b"core.attributesfile"])).expanduser()
            if not attribute_path.is_absolute():
                attribute_path = self.root / attribute_path
            self.extra_attributes = self.read(attribute_path, missing=True)
        self.info_attributes = self.read(common / "info" / "attributes", missing=True)
        root_has_head = has_head(self.context, self.root, deadline=self.context.deadline)
        head = self.query("rev-parse", "--verify", "HEAD").strip() if root_has_head else b""
        if head and re.fullmatch(rb"[0-9a-f]{40}|[0-9a-f]{64}", head) is None:
            raise GitCommandError("git_output_invalid", "repository")
        private = directory / "repository.git"
        self.private = private
        (private / "objects").mkdir(parents=True, mode=0o700)
        (private / "refs" / "heads").mkdir(parents=True, mode=0o700)
        config = b"[core]\nrepositoryformatversion = " + (b"1" if rows[3] == b"sha256" else b"0") + b"\nbare = false\nautocrlf = false\n"
        config += b"[diff]\nalgorithm = " + self.algorithm + b"\nindentheuristic = " + self.indent + b"\n"
        if rows[3] == b"sha256":
            config += b"[extensions]\nobjectformat = sha256\n"
        self.put(private / "config", config)
        self.put(private / "HEAD", head + b"\n" if head else b"ref: refs/heads/checkpoint-unborn\n")
        if index is not None:
            self.put(private / "index", index)
        # Split-index metadata refers to sibling immutable sharedindex files.
        count = 0
        with os.scandir(gitdir) as entries:
            for entry in entries:
                self.context.check_deadline()
                if re.fullmatch(r"sharedindex\.[0-9a-f]{40}|sharedindex\.[0-9a-f]{64}", entry.name):
                    count += 1
                    if count > 64:
                        raise GitCommandError("git_output_invalid", "repository")
                    raw = (self.read_selected_index(Path(entry.path), missing=False) if self.capture_selected_index
                           else self.read(Path(entry.path)))
                    self.put(private / entry.name, raw)
        exclude = self.read(common / "info" / "exclude", missing=True)
        if exclude is not None:
            self.put(private / "info" / "exclude", exclude)
        self.put(private / "info" / "attributes", b"* -filter -working-tree-encoding -ident -text -eol -crlf\n")
        if self.extra_attributes is not None:
            self.put(directory / "global-attributes", self.extra_attributes)
        self.environment.update(GIT_DIR=str(private), GIT_COMMON_DIR=str(private), GIT_INDEX_FILE=str(private / "index"),
                                GIT_WORK_TREE=str(self.root), GIT_OBJECT_DIRECTORY=str(common / "objects"))

    def validate_index(self, scope):
        if scope == "staged":
            return
        with capture_git(self.context, ["ls-files", "-v", "-z"], cwd=self.root, deadline=self.context.deadline) as capture:
            for row in capture.records(b"\0"):
                if row[:1] not in {b"H", b"M"}:
                    raise ScanSecurityError("index_flags_unsupported", "git_index")

    def conversions(self, paths):
        # Capture only attribute ancestors used by this pending candidate set.
        # Git then resolves attributes in an immutable private tree; its config
        # still has no filter, fsmonitor, textconv, hook or remote definitions.
        from .scan_git import worktree_conversions
        view = self.directory / "attributes-view"
        view.mkdir(mode=0o700, exist_ok=True)
        names = {".gitattributes"}
        for path in paths:
            names.update(str(parent / ".gitattributes") for parent in PurePosixPath(path).parents if str(parent) != ".")
        for name in sorted(names):
            with _worktree_descriptor(self.root, name, allow_missing=True) as descriptor:
                if descriptor is None:
                    continue
                info = os.fstat(descriptor)
                if info.st_size > self.context.limits.max_capture_bytes:
                    raise ScanLimitExceeded("git_output_limit", "git_diff", measured=info.st_size, limit=self.context.limits.max_capture_bytes)
                raw = self.read(self.root / name, descriptor=descriptor)
                self.put(view / name, raw)
        attrs = self.private / "info" / "attributes"
        self.remove(attrs)
        self.put(attrs, self.info_attributes or b"")
        previous = self.environment.copy()
        self.environment["GIT_WORK_TREE"] = str(view)
        settings = int(self.environment["GIT_CONFIG_COUNT"])
        overrides = {"core.autocrlf": os.fsdecode(self.default_conversion)}
        if self.extra_attributes is not None:
            overrides["core.attributesFile"] = str(self.directory / "global-attributes")
        for key, value in overrides.items():
            self.environment[f"GIT_CONFIG_KEY_{settings}"] = key
            self.environment[f"GIT_CONFIG_VALUE_{settings}"] = value
            settings += 1
        self.environment["GIT_CONFIG_COUNT"] = str(settings)
        try:
            return worktree_conversions(self.context, view, paths, protected=True)
        finally:
            self.environment = previous
            self.remove(attrs)
            self.put(attrs, b"* -filter -working-tree-encoding -ident -text -eol -crlf\n")

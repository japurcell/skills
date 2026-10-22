#!/usr/bin/env python3
"""Preflight text-fixture patches through independently identified real scanners."""
from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import select
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time

VERSION = "1.0.0"
SCHEMA = "security_fixture_verification_v1"
ROOT = Path(__file__).resolve().parent.parent
PROVIDERS = {"codex": ".codex/hooks", "copilot": ".copilot/hooks/scripts", "gemini": ".gemini/hooks/scripts"}
LIMIT = 64 * 1024 * 1024
PATCH_LIMIT = 1024 * 1024
MAX_PATHS = 4096
MAX_TARGETS = 64
TIMEOUT = 12
DEADLINE = None
CANCEL_REQUESTS = 0
CANCELLED_AT = None
INSPECTOR = None
PROCESS_BYTES = 1024 * 1024
CLEANUP_SECONDS = 2.0
# Observation may use half the cleanup envelope; escalation and reaping share
# its remaining absolute deadline rather than multiplying independent waits.
PROCESS_SECONDS = CLEANUP_SECONDS / 2
REAP_SECONDS = 0.1
# Native confirmation, exact-child reaps and ordinary temporary teardown share
# this finalization allowance; none receives a separate cleanup deadline.
FINALIZE_SECONDS = REAP_SECONDS / 2


class Failure(Exception):
    def __init__(self, reason, code=2, phase="preflight", **measurements):
        self.reason, self.code, self.phase = reason, code, phase
        self.measurements = measurements


class Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's message can contain a credential-bearing argument.
        raise Failure("invalid_arguments", 3, "arguments")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unsafe(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def relative(value):
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or ".." in path.parts or ".git" in path.parts
            or "\\" in value or ":" in value or str(path) != value
            or any(ord(c) < 32 or ord(c) > 126 for c in value)):
        raise Failure("unsafe_path", 3, "paths")
    return value


def regular(root, name, missing=False):
    relative(name)
    path = root
    for part in PurePosixPath(name).parts:
        path = path / part
        try:
            info = path.lstat()
        except FileNotFoundError:
            if missing:
                return None
            raise Failure("missing_file", 3, "paths") from None
        if unsafe(info):
            raise Failure("unsafe_path", 3, "paths")
        if path != root / name and not stat.S_ISDIR(info.st_mode):
            raise Failure("unsafe_path", 3, "paths")
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise Failure("unsafe_file", 3, "paths")
    return path


def read_file(path, bound=LIMIT, *, phase="capture"):
    check_cancelled()
    # Filesystem snapshots use no-follow descriptors and compare opened identity.
    info = path.lstat()
    if unsafe(info) or not stat.S_ISREG(info.st_mode):
        raise Failure("unsafe_file", 3, phase)
    if info.st_size > bound:
        raise Failure("patch_limit" if phase == "input" else "capture_limit",
                      3 if phase == "input" else 2, phase,
                      limit=bound, measured=info.st_size, unit="bytes")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
            raise Failure("state_drift", 2, "capture")
        data = stream.read(bound + 1)
        after = os.fstat(stream.fileno())
    if len(data) > bound:
        raise Failure("patch_limit" if phase == "input" else "capture_limit",
                      3 if phase == "input" else 2, phase,
                      limit=bound, measured=max(len(data), after.st_size), unit="bytes")
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_mode)
    if identity(opened) != identity(after):
        raise Failure("state_drift", 2, "capture")
    return data, stat.S_IMODE(opened.st_mode), identity(opened)



def check_cancelled():
    if CANCEL_REQUESTS:
        raise KeyboardInterrupt


def wait_process(process, timeout):
    """Wait for kernel exit notification on macOS, then reap the exact child."""
    if process.poll() is not None:
        return process.returncode
    if not hasattr(select, "kqueue"):
        return process.wait(timeout=timeout)
    deadline = time.monotonic() + timeout
    with contextlib.closing(select.kqueue()) as queue:
        event = select.kevent(process.pid, filter=select.KQ_FILTER_PROC,
                             flags=select.KQ_EV_ADD | select.KQ_EV_ONESHOT,
                             fflags=select.KQ_NOTE_EXIT)
        try:
            queue.control([event], 0, 0)
        except ProcessLookupError:
            # The kernel can remove a dying PID before waitpid is ready. Reap
            # only our exact child, within the same remaining wait allowance.
            return process.wait(timeout=max(0, deadline - time.monotonic()))
        if process.poll() is not None:
            return process.returncode
        events = queue.control(None, 1, max(0, deadline - time.monotonic()))
        if not events:
            raise subprocess.TimeoutExpired(process.args, timeout)
        # NOTE_EXIT may precede waitpid readiness by a short kernel teardown
        # interval. Reaping shares this wait's remaining absolute allowance.
        return process.wait(timeout=max(0, deadline - time.monotonic()))


def process_snapshot(*, deadline=None, interruptible=True):
    """Read bounded PID/parent/group/start/state metadata, never command text."""
    with tempfile.TemporaryFile() as output:
        started = time.monotonic()
        # Observation includes process startup. Cleanup supplies its own absolute
        # deadline; ordinary observations share the invocation's remaining time.
        deadline = DEADLINE if deadline is None else deadline
        allowance = PROCESS_SECONDS
        if deadline is not None:
            allowance = max(0, min(allowance, deadline - started - (REAP_SECONDS if interruptible else FINALIZE_SECONDS)))
        try:
            observer = subprocess.Popen(["/bin/ps", "-axo", "pid=,ppid=,pgid=,lstart=,stat="],
                stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.DEVNULL,
                env={"LC_ALL": "C", "PATH": os.defpath}, start_new_session=True)
        except OSError:
            raise Failure("process_observation_unavailable", 2, "cleanup") from None
        try:
            try:
                observation_deadline = started + allowance
                while True:
                    if interruptible:
                        check_cancelled()
                    remaining = max(0, observation_deadline - time.monotonic())
                    try:
                        wait_process(observer, min(0.02, remaining) if interruptible else remaining)
                        if interruptible:
                            check_cancelled()
                        break
                    except subprocess.TimeoutExpired:
                        if time.monotonic() >= observation_deadline:
                            raise
            except subprocess.TimeoutExpired:
                raise Failure("process_observation_timeout", 2, "cleanup", limit=round(allowance, 3), measured=round(time.monotonic() - started, 3), unit="seconds") from None
            if observer.returncode:
                raise Failure("process_observation_unavailable", 2, "cleanup")
            measured = os.fstat(output.fileno()).st_size
            if measured > PROCESS_BYTES:
                raise Failure("process_observation_limit", 2, "cleanup", limit=PROCESS_BYTES, measured=measured, unit="bytes")
            output.seek(0)
            raw = output.read(PROCESS_BYTES + 1)
            result = {}
            for line in raw.splitlines():
                fields = line.split()
                if len(fields) != 9 or not all(value.isdigit() for value in fields[:3]):
                    raise Failure("process_observation_invalid", 2, "cleanup")
                pid, parent, group = map(int, fields[:3])
                result[pid] = (parent, group, tuple(fields[3:8]), fields[8])
            return result
        finally:
            if observer.poll() is None:
                with contextlib.suppress(ProcessLookupError, PermissionError):
                    os.killpg(observer.pid, signal.SIGKILL)
            reap_deadline = deadline
            if CANCELLED_AT is not None:
                reap_deadline = min(reap_deadline, CANCELLED_AT + CLEANUP_SECONDS) if reap_deadline is not None else CANCELLED_AT + CLEANUP_SECONDS
            allowance = REAP_SECONDS if reap_deadline is None else max(0, min(REAP_SECONDS, reap_deadline - time.monotonic()))
            with contextlib.suppress(subprocess.TimeoutExpired):
                wait_process(observer, allowance)


def process_query_helper():
    """Fixed numeric queries only; the parent bounds every native call over IPC."""
    import errno
    if sys.platform == "darwin":
        import ctypes
        class BSDInfo(ctypes.Structure):
            # Public proc_bsdinfo, SDK sys/proc_info.h / PROC_PIDTBSDINFO.
            _fields_ = [(name, ctypes.c_uint32) for name in (
                "flags", "status", "xstatus", "pid", "ppid", "uid", "gid",
                "ruid", "rgid", "svuid", "svgid", "reserved")] + [
                ("comm", ctypes.c_char * 16), ("name", ctypes.c_char * 32)] + [
                (name, ctypes.c_uint32) for name in (
                    "nfiles", "pgid", "jobc", "tdev", "tpgid")] + [
                ("nice", ctypes.c_int32), ("seconds", ctypes.c_uint64),
                ("microseconds", ctypes.c_uint64)]
        if ctypes.sizeof(BSDInfo) != 136 or BSDInfo.seconds.offset != 120:
            raise SystemExit(2)
        library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
        query = library.proc_pidinfo
        query.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64,
                          ctypes.c_void_p, ctypes.c_int]
        query.restype = ctypes.c_int
        def native(pid):
            info = BSDInfo()
            ctypes.set_errno(0)
            size = query(pid, 3, 0, ctypes.byref(info), ctypes.sizeof(info))
            if size <= 0 and ctypes.get_errno() == errno.ESRCH:
                return None
            if size != ctypes.sizeof(info):
                raise OSError(ctypes.get_errno() or errno.EIO, "native query")
            if info.pid != pid or info.status not in (1, 2, 3, 4, 5) or info.microseconds >= 1000000:
                raise ValueError("native result")
            state = "stopped" if info.status == 4 else "zombie" if info.status == 5 else "live"
            return [info.pid, info.ppid, info.pgid, info.seconds, info.microseconds, state]
    elif sys.platform.startswith("linux"):
        ticks_per_second = os.sysconf("SC_CLK_TCK")
        with open("/proc/stat", "rb") as stream:
            boot = stream.read(PROCESS_BYTES + 1)
        match = re.search(rb"^btime ([0-9]+)$", boot, re.MULTILINE)
        if len(boot) > PROCESS_BYTES or match is None or ticks_per_second <= 0:
            raise SystemExit(2)
        boot_seconds = int(match[1])
        def native(pid):
            try:
                with open("/proc/" + str(pid) + "/stat", "rb") as stream:
                    raw = stream.read(16385)
            except FileNotFoundError:
                return None
            prefix, separator, suffix = raw.rpartition(b") ")
            fields = suffix.split()
            if (len(raw) > 16384 or not separator or not prefix.startswith(str(pid).encode() + b" (")
                    or len(fields) < 20 or fields[0] not in (b"R", b"S", b"D", b"Z", b"T", b"t", b"X", b"x", b"K", b"W", b"P", b"I")
                    or not all(fields[n].isdigit() for n in (1, 2, 19))):
                raise ValueError("native result")
            ticks = int(fields[19])
            state = "stopped" if fields[0] in (b"T", b"t") else "zombie" if fields[0] in (b"Z", b"X", b"x") else "live"
            return [pid, int(fields[1]), int(fields[2]), boot_seconds + ticks // ticks_per_second, ticks, state]
    else:
        raise SystemExit(2)
    while True:
        raw = sys.stdin.buffer.readline(16385)
        if not raw:
            return
        try:
            if len(raw) > 16384:
                raise ValueError("request")
            pids = json.loads(raw)
            if (not isinstance(pids, list) or len(pids) > 256
                    or any(type(pid) is not int or not 0 < pid < 2 ** 31 for pid in pids)
                    or len(set(pids)) != len(pids)):
                raise ValueError("request")
            result = {str(pid): native(pid) for pid in pids}
            for row in result.values():
                if row is not None:
                    row.append(time.localtime(row[3]).tm_gmtoff)
        except Exception:
            # Absence is represented only by native ESRCH/ENOENT, never denial,
            # partial structures, malformed records, or another native failure.
            result = {"error": "native_query_unavailable"}
        print(json.dumps(result, separators=(",", ":")), flush=True)


class ProcessInspector:
    def __init__(self):
        code = ("import runpy;runpy.run_path(" + repr(str(Path(__file__).resolve()))
                + ",run_name='fixture_process_helper')['process_query_helper']()")
        try:
            self.process = subprocess.Popen([sys.executable, "-I", "-S", "-B", "-c", code],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                env={"LC_ALL": "C", "PATH": os.defpath}, start_new_session=True)
        except OSError:
            raise Failure("process_observation_native_unavailable", 2, "cleanup") from None
        try:
            os.set_blocking(self.process.stdin.fileno(), False)
            os.set_blocking(self.process.stdout.fileno(), False)
        except OSError:
            self.close(time.monotonic() + REAP_SECONDS)
            raise Failure("process_observation_native_unavailable", 2, "cleanup") from None

    def query(self, pids, deadline, *, interruptible=False):
        pids = sorted(pids)
        if not pids:
            return {}
        started = time.monotonic()
        if not interruptible:
            deadline -= FINALIZE_SECONDS
        allowance = max(0, min(PROCESS_SECONDS, deadline - started))
        deadline = started + allowance
        request = json.dumps(pids, separators=(",", ":")).encode() + b"\n"
        received = bytearray()
        try:
            while request or b"\n" not in received:
                if interruptible:
                    check_cancelled()
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise Failure("process_observation_timeout", 2, "cleanup", limit=round(allowance, 3), measured=round(time.monotonic() - started, 3), unit="seconds")
                ready, writable, _ = select.select(
                    [] if request else [self.process.stdout], [self.process.stdin] if request else [], [],
                    min(0.02, remaining))
                if writable:
                    request = request[os.write(self.process.stdin.fileno(), request):]
                if ready:
                    chunk = os.read(self.process.stdout.fileno(), 65537 - len(received))
                    if not chunk:
                        raise ValueError("closed native helper")
                    received.extend(chunk)
                    if len(received) > 65536:
                        raise ValueError("native result bound")
            result = json.loads(received)
            if not isinstance(result, dict) or set(result) != {str(pid) for pid in pids}:
                raise ValueError("incomplete native result")
            for pid in pids:
                row = result[str(pid)]
                if row is None:
                    continue
                if (not isinstance(row, list) or len(row) != 7 or row[0] != pid
                        or any(type(value) is not int for value in row[:5])
                        or not 0 <= row[1] < 2 ** 31 or not 0 < row[2] < 2 ** 31
                        or not 0 < row[3] < 2 ** 63 or not 0 <= row[4] < 2 ** 63
                        or row[5] not in ("live", "stopped", "zombie")
                        or type(row[6]) is not int or not -86400 < row[6] < 86400):
                    raise ValueError("invalid native result")
            return {int(pid): row for pid, row in result.items()}
        except (OSError, ValueError, TypeError):
            raise Failure("process_observation_native_unavailable", 2, "cleanup") from None

    def close(self, deadline):
        started = time.monotonic()
        allowance = max(0, min(REAP_SECONDS, deadline - started))
        try:
            if self.process.poll() is None:
                with contextlib.suppress(ProcessLookupError, PermissionError):
                    os.killpg(self.process.pid, signal.SIGKILL)
            with contextlib.suppress(OSError, subprocess.TimeoutExpired):
                wait_process(self.process, max(0, min(allowance, deadline - time.monotonic())))
            if self.process.poll() is None:
                # Signal delivery is not exit proof. A denied signal or expired
                # reap must not turn a live helper into successful cancellation.
                raise Failure("process_cleanup_incomplete", 2, "cleanup",
                    resource="native_helper", limit=round(allowance, 3),
                    measured=round(time.monotonic() - started, 3), unit="seconds")
        finally:
            self.process.stdin.close()
            self.process.stdout.close()


def native_living(known, identities, deadline):
    current = INSPECTOR.query(known, deadline)
    living = {}
    for pid, row in current.items():
        if row is None:
            continue
        identity = (row[3], row[4])
        if (tuple(time.asctime(time.gmtime(row[3] + row[6])).encode("ascii").split()) != known[pid][2]
                or pid in identities and identity != identities[pid]):
            raise Failure("process_observation_identity_mismatch", 2, "cleanup")
        identities[pid] = identity
        if row[5] != "zombie":
            living[pid] = row
    return living


def freeze_descendants(known, identities, deadline):
    while True:
        living = native_living(known, identities, deadline)
        pending = {pid: row for pid, row in living.items() if row[5] != "stopped"}
        if not pending:
            return living
        for pid in pending:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.kill(pid, signal.SIGSTOP)
        # Delivery is asynchronous. A successful signal is not stop proof;
        # acknowledge every identity through the bounded native helper first.
        time.sleep(min(0.001, max(0, deadline - time.monotonic())))


def remember_descendants(process, known, snapshot):
    # Retain observed ancestors after reparenting so a separate Git session and
    # any children it creates remain discoverable after the scanner exits.
    # A child may change process groups after observation; its start identity
    # stays stable. Use the current group only when choosing how to signal it.
    roots = {pid for pid, previous in known.items()
             if pid in snapshot and snapshot[pid][2] == previous[2]}
    if process.returncode is None and process.pid in snapshot:
        known.setdefault(process.pid, snapshot[process.pid])
        roots.add(process.pid)
    while roots:
        children = {pid for pid, record in snapshot.items() if record[0] in roots and pid not in known}
        for pid in children:
            known[pid] = snapshot[pid]
        roots = children
    if len(known) > 256:
        raise Failure("descendant_limit", 2, "cleanup", limit=256, measured=len(known), unit="processes")


def living_descendants(known, snapshot):
    return {pid: current for pid, previous in known.items()
            if (current := snapshot.get(pid)) is not None
            and current[2] == previous[2] and not current[3].startswith(b"Z")}


def signal_observed(living, signum):
    for pid, record in living.items():
        try:
            if record[1] == pid:
                os.killpg(pid, signum)
            else:
                os.kill(pid, signum)
        except (ProcessLookupError, PermissionError):
            # A group can disappear between the bounded snapshot and signal.
            # Fresh observation below decides whether cleanup actually finished.
            pass


def stop_process(process, known):
    started = time.monotonic()
    deadline = min(started, CANCELLED_AT if CANCELLED_AT is not None else started) + CLEANUP_SECONDS
    identities = {}
    try:
        if process.poll() is None:
            # This exact unreaped child cannot have its PID recycled.
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.kill(process.pid, signal.SIGSTOP)
            if process.pid not in known:
                row = INSPECTOR.query([process.pid], deadline)[process.pid]
                if row is not None:
                    known[process.pid] = (row[1], row[2], tuple(time.asctime(time.gmtime(row[3] + row[6])).encode("ascii").split()), b"T")
        while True:
            frozen = freeze_descendants(known, identities, deadline)
            if process.pid in known and process.pid not in frozen and process.poll() is None:
                # An exact owned child still alive in the kernel cannot also be
                # absent from native observation. Do not treat unknown as exit.
                raise Failure("process_observation_native_unavailable", 2, "cleanup")
            # Acknowledged stopped ancestors remain alive while this fresh graph
            # discovers children born during an earlier metadata capture/return.
            snapshot = process_snapshot(deadline=deadline, interruptible=False)
            remember_descendants(process, known, snapshot)
            living = living_descendants(known, snapshot)
            if any(pid not in frozen for pid in living):
                continue
            current = native_living(known, identities, deadline)
            if any(row[5] != "stopped" for row in current.values()):
                continue
            # Closure was collected after every live ancestor's stop was
            # acknowledged. Revalidate identities and current groups before kill.
            verified = {pid: (row[1], row[2], known[pid][2], b"T") for pid, row in current.items()}
            signal_observed(verified, signal.SIGKILL)
            while native_living(known, identities, deadline):
                if time.monotonic() >= deadline:
                    raise Failure("process_cleanup_incomplete", 2, "cleanup", limit=CLEANUP_SECONDS, unit="seconds")
            process.poll()
            return
    finally:
        if process.poll() is None:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(process.pid, signal.SIGKILL)
        with contextlib.suppress(subprocess.TimeoutExpired):
            wait_process(process, max(0, min(REAP_SECONDS, deadline - time.monotonic())))



def enforce_output_bounds(out, err):
    for stream, name, limit in ((out, "stdout", LIMIT), (err, "stderr", PATCH_LIMIT)):
        measured = os.fstat(stream.fileno()).st_size
        if measured > limit:
            raise Failure("subprocess_output_limit", 2, "subprocess",
                          limit=limit, measured=measured, unit="bytes", stream=name)


def run(command, *, cwd, env, data=None, check=True, timeout=TIMEOUT):
    if os.name == "nt":
        raise Failure("bounded_descendant_cleanup_unavailable", 2, "platform")
    if DEADLINE is not None:
        timeout = min(timeout, DEADLINE - time.monotonic())
        if timeout <= 0:
            raise Failure("operation_time_limit", 2, "subprocess", limit=180, measured=round(time.monotonic() - DEADLINE + 180, 3), unit="seconds")
    check_cancelled()
    # Spools bound retained output and avoid pipe EOF being held by descendants.
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                   stdout=out, stderr=err, start_new_session=os.name != "nt")
        known = {}
        observed_at = time.monotonic()
        try:
            started = time.monotonic()
            request = data or b""
            while True:
                check_cancelled()
                if process.poll() is None and time.monotonic() - observed_at >= 0.05:
                    remember_descendants(process, known, process_snapshot())
                    observed_at = time.monotonic()
                if time.monotonic() - started > timeout:
                    raise Failure("subprocess_timeout", 2, "subprocess", limit=timeout, measured=round(time.monotonic() - started, 3), unit="seconds")
                enforce_output_bounds(out, err)
                try:
                    process.communicate(input=request, timeout=min(0.02, timeout))
                    break
                except subprocess.TimeoutExpired:
                    request = None
            out.seek(0)
            output = out.read(LIMIT + 1)
            enforce_output_bounds(out, err)
            if check and process.returncode:
                raise Failure("git_or_hook_failed", 2, "subprocess")
            return process.returncode, output
        finally:
            stop_process(process, known)


def environment(home, git):
    # No caller Git configuration, hook environment, Python startup, or scanner bypasses.
    keys = ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP")
    env = {k: os.environ[k] for k in keys if k in os.environ}
    env.update(PATH=os.pathsep.join(dict.fromkeys([str(Path(git).parent), os.defpath])),
               HOME=str(home), USERPROFILE=str(home), CODEX_HOME=str(home / ".codex"),
               XDG_CONFIG_HOME=str(home / ".config"), GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0",
               GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1", LC_ALL="C", TMPDIR=str(home.parent))
    return env


class Git:
    def __init__(self, executable, env):
        self.executable, self.env = executable, env

    def __call__(self, repo, *args, data=None, check=True, status=False):
        if args and args[0] == "init":
            args = (*args, "--object-format=" + getattr(self, "object_format", "sha1"))
        result = run([self.executable, "--no-replace-objects", "-c", "core.hooksPath=" + os.devnull,
                    "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false",
                    "-C", str(repo), *args], cwd=repo, env=self.env, data=data, check=check)
        return result if status else result[1]



def directory_no_links(path):
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        info = current.lstat()
        if unsafe(info) or not stat.S_ISDIR(info.st_mode):
            raise Failure("unsafe_directory", 3, "paths")


def read_patch_stdin():
    fd = sys.stdin.fileno()
    deadline = time.monotonic() + 2
    result = bytearray()
    while True:
        check_cancelled()
        if time.monotonic() >= deadline:
            raise Failure("stdin_timeout", 2, "input", limit=2, measured=round(time.monotonic() - deadline + 2, 3), unit="seconds")
        if os.name == "nt" and not stat.S_ISREG(os.fstat(fd).st_mode):
            import ctypes
            import msvcrt
            available = ctypes.c_ulong()
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            if not kernel.PeekNamedPipe(ctypes.c_void_p(msvcrt.get_osfhandle(fd)), None, 0, None, ctypes.byref(available), None):
                if ctypes.get_last_error() in (109, 233):
                    return bytes(result)
                raise Failure("stdin_unavailable", 2, "input")
            ready = available.value > 0
        elif os.name != "nt":
            import select
            ready = bool(select.select([fd], [], [], 0.02)[0])
        else:
            ready = True
        if not ready:
            time.sleep(0.01)
            continue
        chunk = os.read(fd, min(65536, PATCH_LIMIT + 1 - len(result)))
        if not chunk:
            return bytes(result)
        result.extend(chunk)
        if len(result) > PATCH_LIMIT:
            raise Failure("patch_limit", 3, "input", limit=PATCH_LIMIT, measured=len(result), unit="bytes")


def entries(raw):
    result = {}
    for row in raw.split(b"\0"):
        if not row:
            continue
        meta, name = row.split(b"\t", 1)
        mode, oid, stage = meta.decode("ascii").split()
        if stage != "0" or mode not in {"100644", "100755"}:
            raise Failure("unsupported_index", 3, "capture")
        name = relative(name.decode("utf-8"))
        result[name] = (mode, oid)
    return result


def capture(git, repo):
    top = git(repo, "rev-parse", "--show-toplevel", check=False).strip()
    if not top:
        raise Failure("not_repository", 3, "capture")
    if top.decode() != str(repo):
        raise Failure("run_from_repository_root", 3, "capture")
    object_format = git(repo, "rev-parse", "--show-object-format").strip().decode()
    if object_format not in {"sha1", "sha256"}:
        raise Failure("unsupported_object_format", 3, "capture")
    git.object_format = object_format
    index_path = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-path", "index").strip().decode())
    index = read_file(index_path) if index_path.exists() else None
    head_code, head_raw = git(repo, "rev-parse", "--verify", "HEAD", check=False, status=True)
    head = head_raw.strip()
    if head_code:
        branch_code, branch_raw = git(repo, "symbolic-ref", "--quiet", "HEAD", check=False, status=True)
        branch = branch_raw.strip()
        if branch_code or not branch.startswith(b"refs/heads/"):
            raise Failure("head_capture_failed", 2, "capture")
        ref_code, _ = git(repo, "show-ref", "--verify", "--quiet", branch.decode(), check=False, status=True)
        if ref_code != 1:
            raise Failure("head_capture_failed", 2, "capture")
        head = b""
    if head and not re.fullmatch(rb"[0-9a-f]{40}|[0-9a-f]{64}", head):
        raise Failure("invalid_head", 3, "capture")
    tree = {}
    if head:
        for row in git(repo, "ls-tree", "-rz", "--full-tree", head.decode()).split(b"\0"):
            if row:
                meta, name = row.split(b"\t", 1)
                mode, kind, oid = meta.decode().split()
                if kind != "blob" or mode not in {"100644", "100755"}:
                    raise Failure("unsupported_head", 3, "capture")
                tree[relative(name.decode())] = (mode, oid)
    selected = entries(git(repo, "ls-files", "--stage", "-z"))
    # Sparse and assume-unchanged states cannot faithfully prove worktree coverage.
    flags = git(repo, "ls-files", "-v", "-z").split(b"\0")
    if any(row and row[:1] != b"H" for row in flags):
        raise Failure("unsupported_index_flags", 3, "capture")
    untracked = {relative(p.decode()) for p in git(repo, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if p}
    names = set(tree) | set(selected) | untracked
    if len(names) > MAX_PATHS:
        raise Failure("path_limit", 2, "capture", limit=MAX_PATHS, measured=len(names), unit="paths")
    work = {}
    for name in sorted(names):
        path = regular(repo, name, missing=True)
        work[name] = read_file(path) if path else None
    captured_bytes = sum(len(v[0]) for v in work.values() if v)
    if captured_bytes > LIMIT:
        raise Failure("capture_limit", 2, "capture", limit=LIMIT, measured=captured_bytes, unit="bytes")
    # Source Git status may execute configured clean filters. Raw index,
    # object IDs and captured working bytes already supply the required state.
    return {"head": head, "tree": tree, "selected": selected, "work": work, "index": index, "object_format": object_format}


def put(root, name, data, mode):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_bytes(data)
    path.chmod(mode)


def acquire_objects(git, live, state):
    oids = sorted({oid for table in (state["tree"], state["selected"]) for mode, oid in table.values()})
    if not oids:
        return {}
    request = ("\n".join(oids) + "\n").encode("ascii")
    rows = git(live, "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)", data=request).splitlines()
    if len(rows) != len(oids):
        raise Failure("invalid_object_capture", 2, "capture")
    sizes = {}
    total = 0
    for oid, row in zip(oids, rows):
        parts = row.split()
        if len(parts) != 3 or parts[0] != oid.encode() or parts[1] != b"blob" or not parts[2].isdigit():
            raise Failure("invalid_object_capture", 2, "capture")
        size = int(parts[2])
        if size + len(oid) + 64 > LIMIT:
            raise Failure("object_capture_limit", 2, "capture", limit=LIMIT - len(oid) - 64, measured=size, unit="bytes")
        total += size
        if total > 2 * LIMIT:
            raise Failure("object_capture_limit", 2, "capture", limit=2 * LIMIT, measured=total, unit="bytes")
        sizes[oid] = size
    batches, batch, used = [], [], 0
    for oid in oids:
        required = sizes[oid] + len(oid) + 64
        if batch and used + required > LIMIT:
            batches.append(batch)
            batch, used = [], 0
        batch.append(oid)
        used += required
    if batch:
        batches.append(batch)
    objects = {}
    for batch in batches:
        raw = git(live, "cat-file", "--batch", data=("\n".join(batch) + "\n").encode("ascii"))
        offset = 0
        for oid in batch:
            header = (oid + " blob " + str(sizes[oid]) + "\n").encode("ascii")
            if raw[offset:offset + len(header)] != header:
                raise Failure("invalid_object_capture", 2, "capture")
            offset += len(header)
            end = offset + sizes[oid]
            if raw[end:end + 1] != b"\n":
                raise Failure("invalid_object_capture", 2, "capture")
            objects[oid] = raw[offset:end]
            offset = end + 1
        if offset != len(raw):
            raise Failure("invalid_object_capture", 2, "capture")
    return objects


def reproduce(git, live, state, destination):
    destination.mkdir(mode=0o700)
    git(destination, "init", "-q")
    # Verification intentionally inspects captured raw bytes with no copied
    # conversion helpers. Keep tracked attributes as data, but override executable
    # or encoding transformations at the highest-priority private attribute layer.
    put(destination, ".git/info/attributes", b"* -filter -working-tree-encoding -ident\n", 0o600)
    objects = acquire_objects(git, live, state)
    # Fast-import stores raw blobs and constructs the HEAD tree without clean
    # filters, tracked attributes, copied config, or one process per file.
    stream = bytearray()
    for oid, data in objects.items():
        stream.extend(("blob\ndata " + str(len(data)) + "\n").encode("ascii"))
        stream.extend(data)
        stream.extend(b"\n")
    if state["head"]:
        git(destination, "symbolic-ref", "HEAD", "refs/heads/preflight")
        message = b"isolated baseline\n"
        stream.extend(b"commit refs/heads/preflight\ncommitter Fixture <fixture@example.invalid> 0 +0000\n")
        stream.extend(("data " + str(len(message)) + "\n").encode("ascii"))
        stream.extend(message)
        for name, (mode, oid) in state["tree"].items():
            stream.extend(("M " + mode + " " + oid + " " + json.dumps(name, ensure_ascii=True) + "\n").encode("ascii"))
        stream.extend(b"\n")
    stream.extend(b"done\n")
    git(destination, "fast-import", "--quiet", "--done", data=bytes(stream))
    index = b"".join((mode + " " + oid + "\t" + name).encode("ascii") + b"\0"
                     for name, (mode, oid) in state["selected"].items())
    git(destination, "update-index", "-z", "--index-info", data=index)
    for name, item in state["work"].items():
        if item:
            put(destination, name, item[0], item[1])


def complete_views(git, pending, base, state, targets):
    # Real Git identifies changed paths; a fresh unborn repository forces the
    # maintained detector to inspect their complete bytes without diff suppression.
    tracked_changes = {relative(p.decode()) for p in git(pending, "diff", "--name-only", "--no-renames", "-z").split(b"\0") if p}
    staged_changes = {relative(p.decode()) for p in git(pending, "diff", "--cached", "--name-only", "--no-renames", "-z").split(b"\0") if p}
    untracked = {relative(p.decode()) for p in git(pending, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if p}
    work_view, index_view = base / "complete-worktree", base / "complete-index"
    for view in (work_view, index_view):
        view.mkdir(mode=0o700)
        git(view, "init", "-q")
        put(view, ".git/info/attributes", b"* -filter -working-tree-encoding -ident\n", 0o600)
    for name in sorted(tracked_changes | staged_changes | untracked | set(targets)):
        path = regular(pending, name, missing=True)
        if path:
            data, mode, _ = read_file(path)
            put(work_view, name, data, mode)
    for name in sorted(staged_changes):
        item = state["selected"].get(name)
        if item:
            mode, oid = item
            data = git(pending, "cat-file", "blob", oid)
            put(index_view, name, data, int(mode, 8) & 0o777)
    return (work_view, index_view)


SCANNER_HELPERS = ("helpers/common.py", "helpers/audit.py")
RESULT_HELPERS = tuple("helpers/" + name + ".py" for name in (
    "scan_types", "scan_reporting", "scan_allowlist", "scan_stream",
    "scan_git", "scan_audit", "scan_engine"))

NATIVE_HELPER = "helpers/scan_native_file.py"
REVIEWED_RESULT_CLOSURES = (RESULT_HELPERS, (*RESULT_HELPERS, NATIVE_HELPER),
                           (*RESULT_HELPERS, NATIVE_HELPER, "helpers/scan_native_process.py"))


def bundle(root, destination):
    identities = {}
    for provider, folder in PROVIDERS.items():
        origin = root / folder
        directory_no_links(origin)
        target = destination / provider
        target.mkdir(parents=True, mode=0o700)
        path = regular(origin, "scan-secrets.py")
        data, mode, _ = read_file(path, PATCH_LIMIT)
        put(target, "scan-secrets.py", data, mode)
        values = {}
        for node in ast.parse(data.decode("utf-8")).body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                if node.targets[0].id in {"REPORT_BUILD", "DIAG_BUILD", "DIAG_ASSETS"}:
                    values[node.targets[0].id] = ast.literal_eval(node.value)
        if not re.fullmatch("[0-9a-f]{16}", values.get("REPORT_BUILD", "")):
            raise Failure("unsupported_scanner_build", 3, "build")
        expected = dict(values.get("DIAG_ASSETS", []))
        declared = set(REVIEWED_RESULT_CLOSURES[-1]).intersection(expected)
        if declared and declared not in [set(closure) for closure in REVIEWED_RESULT_CLOSURES]:
            raise Failure("unsupported_scanner_closure", 2, "build")
        # Inventory entries for Guardian/diagnostics never authorize copying or
        # executing additional code. Only these reviewed scanner closures do.
        selected = next((closure for closure in REVIEWED_RESULT_CLOSURES if set(closure) == declared), ())
        helpers = SCANNER_HELPERS + selected
        for name in helpers:
            path = regular(origin, name)
            data, mode, _ = read_file(path, PATCH_LIMIT)
            if digest(data) != expected.get(name):
                raise Failure("scanner_asset_drift", 2, "build")
            put(target, name, data, mode)
        identities[provider] = {"build": values["REPORT_BUILD"], "diagnostics_build": values.get("DIAG_BUILD"),
                                "coverage_schema": 1 if declared else 0,
                                "bundle": digest(b"".join((target / n).read_bytes() for n in
                                                          ("scan-secrets.py", *helpers)))}
    return identities


def strict_json(raw):
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=object_pairs)


def validate_coverage(record, identity, status, findings, truncated, omitted):
    """Keep explicit inspection truth separate from bounded display retention."""
    present = bool(findings)
    if identity["coverage_schema"] == 0:
        if truncated is not False or omitted != 0:
            raise Failure("incomplete_scan", 2, "scan", findings_present=present)
        return
    result = record.get("scanResult")
    if not isinstance(result, dict):
        raise Failure("invalid_scan_result_schema", 2, "scan", findings_present=present)
    checks = {"schema_version": 1, "build": identity["build"],
              "policy_version": "pending_snapshots_v1", "scope": "diff",
              "outcome": "complete_clean" if status == "clean" else "complete_findings",
              "coverage_complete": True, "reason": "clean" if status == "clean" else "findings",
              "audit_outcome": "written", "status_outcome": "not_attempted"}
    count_names = {"candidates", "inspected_snapshots", "candidate_bytes", "capture_bytes",
                   "temp_peak_bytes", "processed_findings", "retained_findings", "omitted_findings"}
    counts = result.get("counts")
    elapsed = result.get("elapsed_seconds")
    if (set(result) != set(checks) | {"scope_identity", "counts", "elapsed_seconds"}
            or any(type(result.get(k)) is not type(v) or result[k] != v for k, v in checks.items())
            or not isinstance(result.get("scope_identity"), str)
            or re.fullmatch("[0-9a-f]{64}", result["scope_identity"]) is None
            or type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0
            or not isinstance(counts, dict) or set(counts) != count_names
            or any(type(value) is not int or not 0 <= value <= 9223372036854775807 for value in counts.values())):
        raise Failure("invalid_scan_result_schema", 2, "scan", findings_present=present)
    processed, retained, dropped = (counts[name] for name in
        ("processed_findings", "retained_findings", "omitted_findings"))
    if (processed != retained + dropped or len(findings) > retained or retained > 100
            or counts["inspected_snapshots"] > counts["candidates"]
            or omitted != processed - len(findings) or truncated != bool(omitted)
            or (status == "clean" and (processed or findings or omitted or truncated))
            or (status == "findings" and not processed)):
        raise Failure("inconsistent_scanner_result", 2, "scan", findings_present=present)


def scan(git, bundle_root, identities, repo, logs, expected="clean"):
    for provider in PROVIDERS:
        log = logs / provider
        log.mkdir(parents=True, mode=0o700)
        env = {**git.env, "SCAN_MODE": "block", "SCAN_SCOPE": "diff", "GUARD_MODE": "block",
               "SECRETS_LOG_DIR": str(log), "AUDIT_LOG": str(log / "audit.log"),
               "AUDIT_LOCK": str(log / "audit.lock"), "OBSERVABILITY_TESTING": "1",
               "OBSERVABILITY_LOG_PATH": str(log / "observability.jsonl")}
        if provider == "copilot":
            payload = {"hook_event_name": "preToolUse", "toolName": "bash", "toolArgs": {"command": "git status"}}
        else:
            payload = {"hook_event_name": "PreToolUse" if provider == "codex" else "BeforeTool",
                       "tool_name": "exec_command" if provider == "codex" else "run_shell_command",
                       "tool_input": {"cmd": "git status", "login": False} if provider == "codex" else {"command": "git status"},
                       "cwd": str(repo)}
        code, raw = run([sys.executable, "-I", "-S", "-B", str(bundle_root / provider / "scan-secrets.py")],
                        cwd=repo, env=env, data=json.dumps(payload).encode())
        try:
            if len(raw) > 16384:
                raise Failure("scanner_output_limit", 2, "scan", limit=16384, measured=len(raw), unit="bytes")
            response = strict_json(raw)
            records = [strict_json(row) for row in read_file(log / "scan.log", PATCH_LIMIT)[0].splitlines()]
            record = records[-1]
            if not isinstance(response, dict) or not isinstance(record, dict):
                raise Failure("invalid_scanner_result", 2, "scan")
        except (ValueError, IndexError, OSError):
            raise Failure("invalid_scanner_result", 2, "scan") from None
        # Validate infrastructure and native output before assigning a security
        # result. A findings-shaped log cannot hide a malformed allow response
        # or unavailable audit behind a nonzero-but-misclassified result.
        audit_path = regular(log, "scan.log")
        audit_bytes, audit_mode, _ = read_file(audit_path, PATCH_LIMIT)
        if not audit_bytes.endswith(b"\n") or len(records) != 1 or (os.name != "nt" and audit_mode & 0o077):
            raise Failure("invalid_required_audit", 2, "scan")
        status = record.get("status")
        findings = record.get("findings", [])
        truncated = record.get("findingsTruncated")
        omitted = record.get("omittedFindings")
        checks = {"provider": provider, "build": identities[provider]["build"], "mode": "block", "scope": "diff",
                  "profile": "pending_snapshots_v1", "route": "pending_scan",
                  "inspection_outcome": "complete", "audit_outcome": "written"}
        if (any(record.get(k) != v for k, v in checks.items())
                or status not in {"clean", "findings"} or not isinstance(findings, list)
                or type(truncated) is not bool or type(omitted) is not int or omitted < 0):
            raise Failure("incomplete_scan", 2, "scan", findings_present=bool(findings))
        validate_coverage(record, identities[provider], status, findings, truncated, omitted)
        if status == "clean":
            if findings or record.get("security_outcome") != "clean" or record.get("enforcement") != "allow":
                raise Failure("inconsistent_scanner_result", 2, "scan", findings_present=bool(findings))
            if response != {}:
                raise Failure("invalid_native_permission", 2, "scan")
        else:
            if not findings or record.get("security_outcome") != "findings" or record.get("enforcement") != "deny":
                raise Failure("inconsistent_scanner_result", 2, "scan", findings_present=bool(findings))
            native = response if provider == "gemini" else response.get("hookSpecificOutput", {})
            deny = native.get("decision") == "deny" if provider == "gemini" else native.get("permissionDecision") == "deny"
            reason = native.get("reason" if provider == "gemini" else "permissionDecisionReason")
            if not deny or not isinstance(reason, str) or not reason.startswith("scan-secrets blocked:"):
                raise Failure("invalid_native_permission", 2, "scan", findings_present=True)
        if status != expected:
            raise Failure("findings" if status == "findings" else "control_not_detected",
                          1 if status == "findings" else 2, "scan", findings_present=bool(findings))
        if expected == "findings" and not any(isinstance(f, dict) and f.get("pattern") == "github_classic_pat" for f in findings):
            raise Failure("control_not_detected", 2, "scan")



def parser():
    result = Parser(description=__doc__, allow_abbrev=False,
                    epilog="Example: --patch repair.patch --path scripts/fixture.py --active-hook-root /reviewed/home --check. "
                    "Active root contains .codex/hooks, .copilot/hooks/scripts and .gemini/hooks/scripts. "
                    "Verification leaves live targets and the index unchanged. No environment configuration is accepted. "
                    "Bounds: patch 1 MiB; state 64 MiB/4096 paths; 64 targets; each child 12 seconds; total 180 seconds; stdin 2 seconds. "
                    "POSIX checking requires /bin/ps access to numeric process metadata (1 MiB, at most 1 second per observation, 0.1 seconds for observer reaping); cleanup is bounded at 2 seconds and 256 observed processes. "
                    "Windows checking refuses before subprocess launch until bounded descendant cleanup is available. "
                    "Exit: 0 verified, 1 findings, 2 incomplete, 3 invalid invocation, 130 canceled.")
    result.add_argument("--version", action="version", version="%(prog)s " + VERSION + " schema=" + SCHEMA)
    result.add_argument("--patch", required=True, help="Unified Git text patch, or - for bounded stdin")
    result.add_argument("--path", action="append", required=True, help="Exact existing regular text fixture target; repeat for each target")
    result.add_argument("--active-hook-root", required=True, type=Path, help="Reviewed active home/source root, supplied explicitly")
    result.add_argument("--check", action="store_true", required=True, help="Verify without changing checkout or index")
    for name in ("json", "no-input", "quiet", "no-color"):
        result.add_argument("--" + name, action="store_true")
    return result


def execute(args):
    if os.name == "nt":
        raise Failure("bounded_descendant_cleanup_unavailable", 2, "platform")
    global DEADLINE, INSPECTOR
    DEADLINE = time.monotonic() + 180
    targets = [relative(p) for p in args.path]
    if len(targets) > MAX_TARGETS:
        raise Failure("target_limit", 3, "arguments", limit=MAX_TARGETS, measured=len(targets), unit="paths")
    if len(set(targets)) != len(targets):
        raise Failure("invalid_targets", 3, "arguments")
    process_snapshot()  # Refuse before launching Git/scanners if observation is unavailable.
    check_cancelled()
    INSPECTOR = ProcessInspector()
    if INSPECTOR.query([os.getpid()], DEADLINE, interruptible=True)[os.getpid()] is None:
        # Our own running PID cannot be absent. Do not accept a broken native
        # observer as authoritative before any Git/scanner can be launched.
        raise Failure("process_observation_native_unavailable", 2, "cleanup")
    git_path = shutil.which("git", path=os.defpath + os.pathsep + "/opt/homebrew/bin")
    if git_path is None:
        raise Failure("git_unavailable", 2, "capture")
    live = Path.cwd().resolve()
    with tempfile.TemporaryDirectory(prefix="verified-fixture-") as temporary:
        base = Path(temporary).resolve()
        base.chmod(0o700)
        home = base / "home"
        home.mkdir(mode=0o700)
        git = Git(git_path, environment(home, git_path))
        if args.patch == "-":
            if sys.stdin.isatty():
                raise Failure("patch_stdin_required", 3, "input")
            patch = read_patch_stdin()
        else:
            patch = read_file(Path(args.patch).absolute(), PATCH_LIMIT, phase="input")[0]
        if len(patch) > PATCH_LIMIT:
            raise Failure("patch_limit", 3, "input", limit=PATCH_LIMIT, measured=len(patch), unit="bytes")
        if any(marker in patch for marker in (b"GIT binary patch", b"Binary files ", b"rename from ", b"rename to ", b"copy from ", b"new file mode ", b"deleted file mode ", b"old mode ", b"new mode ")):
            raise Failure("unsupported_patch", 3, "input")
        state = capture(git, live)
        for name in targets:
            if not state["work"].get(name) or b"\0" in state["work"][name][0]:
                raise Failure("target_requires_regular_text", 3, "paths")
            try:
                state["work"][name][0].decode("utf-8")
            except UnicodeError:
                raise Failure("target_requires_regular_text", 3, "paths") from None
        work = base / "pending"
        reproduce(git, live, state, work)
        stats = git(work, "apply", "--numstat", "-z", "-", data=patch)
        changed = []
        for record in stats.split(b"\0"):
            if record:
                added, removed, path = record.split(b"\t", 2)
                if not added.isdigit() or not removed.isdigit():
                    raise Failure("unsupported_patch", 3, "input")
                changed.append(relative(path.decode()))
        if set(changed) != set(targets) or len(changed) != len(targets):
            raise Failure("patch_target_mismatch", 3, "input")
        git(work, "apply", "--check", "--whitespace=nowarn", "-", data=patch)
        git(work, "apply", "--whitespace=nowarn", "-", data=patch)
        for name in targets:
            data, mode, _ = read_file(regular(work, name))
            if b"\0" in data:
                raise Failure("target_requires_regular_text", 3, "paths")
            try:
                data.decode("utf-8")
            except UnicodeError:
                raise Failure("target_requires_regular_text", 3, "paths") from None
        views = complete_views(git, work, base, state, targets)
        control = base / "credential-control"
        control.mkdir(mode=0o700)
        git(control, "init", "-q")
        # Unmistakably fake, assembled only in private disposable storage.
        put(control, "credential-control.txt", ("gh" + "p_" + "FAKE" * 9).encode(), 0o600)
        builds = {}
        for label, origin in (("active", args.active_hook_root.absolute()), ("candidate", ROOT)):
            builds[label] = bundle(origin, base / label)
            scan(git, base / label, builds[label], work, base / "logs" / label / "pending")
            for number, view in enumerate(views):
                scan(git, base / label, builds[label], view, base / "logs" / label / ("complete-" + str(number)))
            scan(git, base / label, builds[label], control, base / "logs" / label / "control", expected="findings")
        if capture(git, live) != state:
            raise Failure("state_drift", 2, "capture")
        return {"schema": SCHEMA, "version": VERSION, "result": "verified",
                "reason": "complete_clean", "phase": "complete", "targets": len(targets), "builds": builds, "controls_detected": 6}



def failure_action(reason):
    if reason == "git_unavailable":
        return "Install Git or restore it in the supported system search path, then rerun --check."
    if reason == "bounded_descendant_cleanup_unavailable":
        return "Run verification on a supported POSIX host with process-observation access."
    if reason.startswith("process_observation_"):
        return "Restore /bin/ps and supported native identity access with responsive numeric metadata within the 1-second observation allowance, then rerun --check."
    if reason == "process_cleanup_incomplete":
        return "Stop remaining verifier-owned children and restore process-observation access before retrying --check."
    if reason == "descendant_limit":
        return "Investigate excessive children in the reviewed scanner or Git process before retrying --check."
    if reason in {"path_limit", "target_limit", "capture_limit", "object_capture_limit", "patch_limit"}:
        return "Reduce the fixture/state workload within the documented path and byte bounds, then rerun --check."
    if reason in {"operation_time_limit", "subprocess_timeout"}:
        return "Investigate stalled Git/scanner processes or reduce the workload within the documented time bound, then retry --check."
    if reason in {"subprocess_output_limit", "scanner_output_limit"}:
        return "Review excessive output from Git or the selected scanner bundle before retrying --check."
    if reason.startswith("stdin_") or reason == "patch_stdin_required":
        return "Provide a complete EOF-terminated patch on stdin, or use --patch PATH, then rerun --check."
    if reason == "invalid_arguments":
        return "Run --help and supply the documented explicit --check arguments."
    if reason in {"not_repository", "run_from_repository_root"}:
        return "Run from the Git repository root containing the named fixtures, then retry --check."
    if reason == "state_drift":
        return "Wait for concurrent edits to finish, regenerate the patch against current files, and rerun --check."
    if reason in {"unsupported_index", "unsupported_index_flags"}:
        return "Resolve index conflicts and unsupported index flags, then retry --check."
    if reason in {"head_capture_failed", "invalid_head", "invalid_object_capture", "unsupported_head"}:
        return "Repair Git HEAD or object storage while preserving pending fixture content, then retry --check."
    if reason in {"invalid_targets", "patch_target_mismatch", "unsupported_patch"}:
        return "Regenerate a text-only patch against current files and name each regular fixture target exactly once."
    if reason in {"unsafe_path", "unsafe_file", "unsafe_directory", "missing_file", "target_requires_regular_text"}:
        return "Select existing regular UTF-8 fixtures using safe repository-relative paths, then retry --check."
    if reason == "findings":
        return "Repair the fixture representation while preserving its intended runtime controls, then rerun --check."
    if reason == "git_or_hook_failed":
        return "Check Git and the reviewed scanner dependencies before retrying --check."
    return "Select complete reviewed scanner bundles with working audit storage and readable fixture files, then retry --check."


def main():
    command = parser()
    if len(sys.argv) == 1 or sys.argv[1:] in (["help"], ["help", "check"]):
        command.print_help()
        return 0
    report = None
    code = 0
    try:
        args = command.parse_args()
        def interrupted(signum, frame):
            global CANCEL_REQUESTS, CANCELLED_AT
            if CANCELLED_AT is None:
                CANCELLED_AT = time.monotonic()
            CANCEL_REQUESTS += 1
        for signum in (signal.SIGINT, signal.SIGTERM):
            signal.signal(signum, interrupted)
        report = execute(args)
        check_cancelled()
    except Failure as failure:
        code = failure.code
        report = {"schema": SCHEMA, "version": VERSION, "result": "rejected", "reason": failure.reason,
                  "phase": failure.phase, **failure.measurements,
                  "action": failure_action(failure.reason)}
    except KeyboardInterrupt:
        code = 130
        report = {"schema": SCHEMA, "version": VERSION, "result": "canceled", "reason": "interrupted", "phase": "cancellation"}
    except Exception:  # Fail closed without payload-derived exception text.
        code = 2
        report = {"schema": SCHEMA, "version": VERSION, "result": "rejected", "reason": "unsafe_or_unavailable_state", "phase": "preflight"}
    finally:
        if INSPECTOR is not None:
            try:
                INSPECTOR.close(CANCELLED_AT + CLEANUP_SECONDS if CANCELLED_AT is not None
                                else time.monotonic() + REAP_SECONDS)
            except Exception as failure:
                # Finalization follows the primary outcome, but its failure is
                # still terminal. Never expose payload-derived exception text.
                code = 2
                report = {"schema": SCHEMA, "version": VERSION, "result": "rejected",
                          "reason": "process_cleanup_incomplete", "phase": "cleanup",
                          **(failure.measurements if isinstance(failure, Failure) else {}),
                          "action": failure_action("process_cleanup_incomplete")}
    # Filesystem teardown is synchronous. Budget its routine work above and
    # report a real overrun honestly; arbitrary filesystem/scheduler stalls do
    # not have a universal real-time guarantee.
    if CANCELLED_AT is not None and time.monotonic() >= CANCELLED_AT + CLEANUP_SECONDS:
        code = 2
        report = {"schema": SCHEMA, "version": VERSION, "result": "rejected",
                  "reason": "process_cleanup_incomplete", "phase": "cleanup",
                  "limit": CLEANUP_SECONDS, "measured": round(time.monotonic() - CANCELLED_AT, 3),
                  "unit": "seconds", "action": failure_action("process_cleanup_incomplete")}
    try:
        if "--json" in sys.argv:
            print(json.dumps(report, sort_keys=True), flush=True)
        elif code:
            print("Fixture preflight rejected: " + report["reason"] + ". " + report.get("action", "Retry --check when ready."), file=sys.stderr)
        elif not args.quiet:
            print("Fixture patch " + report["result"] + ".")
    except BrokenPipeError:
        with contextlib.suppress(OSError):
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return code or 2
    return code


if __name__ == "__main__":
    try:
        try:
            exit_code = main()
        except SystemExit as requested_exit:
            exit_code = requested_exit.code
        sys.stdout.flush()
    except BrokenPipeError:
        with contextlib.suppress(OSError):
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        exit_code = 2
    raise SystemExit(exit_code)

"""Owned native scanner processes; no detector, gate or publication policy.

Create the root suspended, put it in a non-breakaway kill-on-close Job Object,
then resume its returned initial thread. Only duplicated standard handles are
inherited. No CPython process handles or argument-conversion internals are used.
"""
from __future__ import annotations

import contextlib
import ctypes
import errno
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time

from .scan_native_file import WindowsDirectoryHandles


class _StartupInfo(ctypes.Structure):
    _fields_ = [
        ("size", ctypes.c_uint32), ("reserved", ctypes.c_wchar_p),
        ("desktop", ctypes.c_wchar_p), ("title", ctypes.c_wchar_p),
        ("x", ctypes.c_uint32), ("y", ctypes.c_uint32),
        ("x_size", ctypes.c_uint32), ("y_size", ctypes.c_uint32),
        ("x_chars", ctypes.c_uint32), ("y_chars", ctypes.c_uint32),
        ("fill", ctypes.c_uint32), ("flags", ctypes.c_uint32),
        ("show", ctypes.c_uint16), ("reserved_size", ctypes.c_uint16),
        ("reserved_bytes", ctypes.c_void_p), ("stdin", ctypes.c_void_p),
        ("stdout", ctypes.c_void_p), ("stderr", ctypes.c_void_p),
    ]


class _StartupInfoEx(ctypes.Structure):
    _fields_ = [("startup", _StartupInfo), ("attributes", ctypes.c_void_p)]


class _ProcessInformation(ctypes.Structure):
    _fields_ = [("process", ctypes.c_void_p), ("thread", ctypes.c_void_p),
                ("pid", ctypes.c_uint32), ("tid", ctypes.c_uint32)]


class _JobBasicLimits(ctypes.Structure):
    _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                ("flags", ctypes.c_uint32), ("minimum_working_set", ctypes.c_size_t),
                ("maximum_working_set", ctypes.c_size_t), ("active_limit", ctypes.c_uint32),
                ("affinity", ctypes.c_size_t), ("priority", ctypes.c_uint32),
                ("scheduling", ctypes.c_uint32)]


class _IoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint64) for name in
                ("read_operations", "write_operations", "other_operations",
                 "read_bytes", "write_bytes", "other_bytes")]


class _JobExtendedLimits(ctypes.Structure):
    _fields_ = [("basic", _JobBasicLimits), ("io", _IoCounters),
                ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
                ("peak_process_memory", ctypes.c_size_t), ("peak_job_memory", ctypes.c_size_t)]


class _JobAccounting(ctypes.Structure):
    _fields_ = [("user", ctypes.c_int64), ("kernel", ctypes.c_int64),
                ("period_user", ctypes.c_int64), ("period_kernel", ctypes.c_int64),
                ("faults", ctypes.c_uint32), ("total", ctypes.c_uint32),
                ("active", ctypes.c_uint32), ("terminated", ctypes.c_uint32)]


class _Api:
    def __init__(self):
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        pointer, dword, boolean = ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int
        declarations = {
            "GetCurrentProcess": ([], pointer),
            "GetSystemDirectoryW": ([ctypes.c_wchar_p, dword], dword),
            "CloseHandle": ([pointer], boolean),
            "DuplicateHandle": ([pointer, pointer, pointer, ctypes.POINTER(pointer), dword, boolean, dword], boolean),
            "CreateJobObjectW": ([pointer, ctypes.c_wchar_p], pointer),
            "SetInformationJobObject": ([pointer, ctypes.c_int, pointer, dword], boolean),
            "QueryInformationJobObject": ([pointer, ctypes.c_int, pointer, dword, pointer], boolean),
            "AssignProcessToJobObject": ([pointer, pointer], boolean),
            "TerminateJobObject": ([pointer, dword], boolean),
            "InitializeProcThreadAttributeList": ([pointer, dword, dword, ctypes.POINTER(ctypes.c_size_t)], boolean),
            "UpdateProcThreadAttribute": ([pointer, dword, ctypes.c_size_t, pointer, ctypes.c_size_t, pointer, pointer], boolean),
            "DeleteProcThreadAttributeList": ([pointer], None),
            "CreateProcessW": ([ctypes.c_wchar_p, ctypes.c_wchar_p, pointer, pointer,
                                boolean, dword, pointer, ctypes.c_wchar_p,
                                ctypes.POINTER(_StartupInfo), ctypes.POINTER(_ProcessInformation)], boolean),
            "ResumeThread": ([pointer], dword),
            "WaitForSingleObject": ([pointer, dword], dword),
            "GetExitCodeProcess": ([pointer, ctypes.POINTER(dword)], boolean),
            "TerminateProcess": ([pointer, dword], boolean),
        }
        for name, (arguments, result) in declarations.items():
            function = getattr(self.kernel, name)
            function.argtypes, function.restype = arguments, result

    def checked(self, result):
        if not result:
            raise ctypes.WinError(ctypes.get_last_error())
        return result


_api = None


def _native_api():
    global _api
    if _api is None:
        _api = _Api()
    return _api


class _Interrupt:
    def __init__(self):
        self.pending = False

    def check(self):
        if self.pending:
            raise KeyboardInterrupt


@contextlib.contextmanager
def _owned_interrupt():
    """Keep ordinary SIGINT flag-only until all owned native handles close."""
    state = _Interrupt()
    previous = signal.getsignal(signal.SIGINT)
    if (threading.current_thread() is not threading.main_thread() or
            previous is not signal.default_int_handler and not getattr(previous, "_scan_interrupt", False)):
        yield state
        return
    def interrupt(number, frame):
        state.pending = True
    interrupt._scan_interrupt = True
    signal.signal(signal.SIGINT, interrupt)
    try:
        yield state
    finally:
        signal.signal(signal.SIGINT, previous)
        if state.pending:
            previous(signal.SIGINT, None)


def _quote(argument):
    """Apply the five public subprocess/MS CRT rules, always quoting a word."""
    if type(argument) is not str or "\0" in argument:
        raise OSError(errno.EINVAL, "Invalid native argument")
    result, slashes = ['"'], 0
    for character in argument:
        if character == "\\":
            slashes += 1
            continue
        if character == '"':
            result.append("\\" * (2 * slashes + 1) + '"')
        else:
            result.append("\\" * slashes + character)
        slashes = 0
    result.append("\\" * (2 * slashes) + '"')
    return "".join(result)


def _held_path(path, resources, *, file=False, system_image=False):
    path = Path(path)
    if not path.is_absolute() or re.fullmatch(r"[A-Za-z]:\\", path.anchor) is None:
        raise OSError(errno.EINVAL, "Unsupported native path")
    parts = path.parts[1:]
    reserved = {"CON", "PRN", "AUX", "NUL", "CLOCK$", "CONIN$", "CONOUT$"}
    reserved.update(prefix + suffix for prefix in ("COM", "LPT") for suffix in "123456789¹²³")
    if (file and not parts) or any(
            part in {".", ".."} or part.endswith((".", " "))
            or part.split(".", 1)[0].upper() in reserved or ":" in part for part in parts):
        raise OSError(errno.EINVAL, "Unsupported native path")
    native = WindowsDirectoryHandles(resources)
    native.pin_root(Path(path.anchor))
    for part in parts[:-1] if file else parts:
        native.descend(part)
    if file:
        if system_image:
            native.pin_readonly_image(parts[-1])
        else:
            handle, _ = native.open_handle(parts[-1])
            resources.callback(native.kernel.CloseHandle, handle)
    return str(path)


def _command(api, arguments, resources):
    if not arguments:
        raise OSError(errno.EINVAL, "Invalid native arguments")
    executable = _held_path(arguments[0], resources, file=True)
    suffix = Path(executable).suffix.lower()
    if suffix in {".cmd", ".bat"}:
        # This compatibility subset cannot perform shell expansion. Ordinary
        # native Git receives all supported argv through the MS CRT path below.
        if (any(character in executable for character in '&|<>()^%!"\r\n\0')
                or any(type(word) is not str or not word or
                       any(character.isspace() or character in '&|<>()^%!"\0' for character in word)
                       for word in arguments[1:])):
            raise OSError(errno.EINVAL, "Unsupported native batch arguments")
        directory = ctypes.create_unicode_buffer(32768)
        length = api.kernel.GetSystemDirectoryW(directory, len(directory))
        if not length or length >= len(directory):
            raise OSError(errno.EIO, "Native system directory unavailable")
        interpreter = _held_path(Path(directory.value) / "cmd.exe", resources, file=True, system_image=True)
        body = '"' + executable + '"'
        if len(arguments) > 1:
            body += " " + " ".join(arguments[1:])
        command = _quote(interpreter) + ' /d /s /v:off /c "' + body + '"'
        if len(command.encode("utf-16-le")) // 2 > 8191:
            raise OSError(errno.E2BIG, "Unsupported native batch command length")
        return interpreter, command
    if suffix not in {".exe", ".com"}:
        raise OSError(errno.ENOEXEC, "Unsupported native executable")
    return executable, " ".join(_quote(word) for word in arguments)


class NativeProcess:
    """An explicitly closed process owner, registered before start can create handles."""
    def __init__(self, arguments):
        self.args = tuple(arguments)
        self.pid, self.returncode = 0, None
        self._resources = contextlib.ExitStack()
        self._api = self._process = self._job = None
        self._closed = False
        self._interrupt = _Interrupt()

    def start(self, *, cwd, environment, stdin, stdout):
        try:
            # This context closes last, after root, job and inherited handles.
            self._interrupt = self._resources.enter_context(_owned_interrupt())
            self._start(cwd=cwd, environment=environment, stdin=stdin, stdout=stdout)
            self._interrupt.check()
        except BaseException:
            self.close()
            raise

    def _start(self, *, cwd, environment, stdin, stdout):
        import msvcrt
        self._api = api = _native_api()
        kernel = api.kernel
        self._job = api.checked(kernel.CreateJobObjectW(None, None))
        self._resources.callback(kernel.CloseHandle, self._job)
        limits = _JobExtendedLimits()
        limits.basic.flags = 0x2000  # KILL_ON_JOB_CLOSE; neither breakaway flag.
        api.checked(kernel.SetInformationJobObject(self._job, 9, ctypes.byref(limits), ctypes.sizeof(limits)))
        executable, command = _command(api, self.args, self._resources)
        directory = _held_path(cwd, self._resources)
        if len(command.encode("utf-16-le")) // 2 >= 32767:
            raise OSError(errno.E2BIG, "Native command is too long")
        seen = set()
        for key, value in environment.items():
            if (type(key) is not str or type(value) is not str or not key or
                    "=" in key[1:] or "\0" in key or "\0" in value or key.upper() in seen):
                raise OSError(errno.EINVAL, "Invalid native environment")
            seen.add(key.upper())
        block = "\0".join(key + "=" + environment[key] for key in sorted(environment, key=str.upper)) + "\0\0"
        environment_buffer = ctypes.create_unicode_buffer(block)
        with contextlib.ExitStack() as startup_resources:
            null_input = startup_resources.enter_context(open(os.devnull, "rb", buffering=0))
            null_error = startup_resources.enter_context(open(os.devnull, "wb", buffering=0))
            handles = []
            current = kernel.GetCurrentProcess()
            for stream in (stdin or null_input, stdout, null_error):
                duplicate = ctypes.c_void_p()
                api.checked(kernel.DuplicateHandle(current, msvcrt.get_osfhandle(stream.fileno()),
                                                   current, ctypes.byref(duplicate), 0, True, 2))
                startup_resources.callback(kernel.CloseHandle, duplicate.value)
                handles.append(duplicate.value)
            inherited = (ctypes.c_void_p * len(handles))(*handles)
            size = ctypes.c_size_t()
            if kernel.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(size)) or ctypes.get_last_error() != 122:
                raise OSError(errno.EIO, "Native handle list unavailable")
            attributes = ctypes.create_string_buffer(size.value)
            api.checked(kernel.InitializeProcThreadAttributeList(attributes, 1, 0, ctypes.byref(size)))
            startup_resources.callback(kernel.DeleteProcThreadAttributeList, attributes)
            api.checked(kernel.UpdateProcThreadAttribute(attributes, 0, 0x20002,
                        inherited, ctypes.sizeof(inherited), None, None))
            startup = _StartupInfoEx()
            startup.startup.size = ctypes.sizeof(startup)
            startup.startup.flags = 0x100  # STARTF_USESTDHANDLES.
            startup.startup.stdin, startup.startup.stdout, startup.startup.stderr = handles
            startup.attributes = ctypes.cast(attributes, ctypes.c_void_p)
            information = _ProcessInformation()
            # SUSPENDED | NEW_PROCESS_GROUP | UNICODE_ENVIRONMENT | EXTENDED_STARTUPINFO_PRESENT.
            api.checked(kernel.CreateProcessW(executable, ctypes.create_unicode_buffer(command), None, None,
                        True, 0x00080604, environment_buffer, directory,
                        ctypes.byref(startup.startup), ctypes.byref(information)))
            self._process, self.pid = information.process, int(information.pid)
            self._resources.callback(kernel.CloseHandle, self._process)
            startup_resources.callback(kernel.CloseHandle, information.thread)
            api.checked(kernel.AssignProcessToJobObject(self._job, self._process))
            resumed = kernel.ResumeThread(information.thread)
            if resumed != 1:
                if resumed == 0xFFFFFFFF:
                    raise ctypes.WinError(ctypes.get_last_error())
                raise OSError(errno.EIO, "Native initial thread was not suspended once")

    def poll(self):
        self._interrupt.check()
        return self._poll()

    def _poll(self):
        if self.returncode is not None:
            return self.returncode
        state = self._api.kernel.WaitForSingleObject(self._process, 0)
        if state == 258:
            return None
        if state != 0:
            raise ctypes.WinError(ctypes.get_last_error())
        code = ctypes.c_uint32()
        self._api.checked(self._api.kernel.GetExitCodeProcess(self._process, ctypes.byref(code)))
        self.returncode = int(code.value)
        return self.returncode

    def wait(self, timeout):
        if not math.isfinite(timeout) or timeout < 0:
            raise ValueError("A finite native wait is required")
        if self.poll() is None:
            state = self._api.kernel.WaitForSingleObject(self._process, min(0xFFFFFFFE, math.ceil(timeout * 1000)))
            if state == 258:
                raise subprocess.TimeoutExpired(self.args, timeout)
            if state != 0:
                raise ctypes.WinError(ctypes.get_last_error())
        return self.poll()

    def active_processes(self):
        accounting = _JobAccounting()
        self._api.checked(self._api.kernel.QueryInformationJobObject(
            self._job, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None))
        return int(accounting.active)

    def close(self):
        if self._closed:
            return
        self._closed = True
        active_exception = sys.exception()
        failure = None
        try:
            if self._api is not None:
                kernel = self._api.kernel
                # The root can be unassigned when construction failed.
                if self._process is not None and self._poll() is None:
                    if not kernel.TerminateProcess(self._process, 1) and self._poll() is None:
                        failure = ctypes.WinError(ctypes.get_last_error())
                if self._job is not None and not kernel.TerminateJobObject(self._job, 1):
                    failure = ctypes.WinError(ctypes.get_last_error())
                deadline = time.monotonic() + 0.75
                if self._process is not None:
                    state = kernel.WaitForSingleObject(self._process,
                        max(0, min(750, math.ceil((deadline - time.monotonic()) * 1000))))
                    if state != 0:
                        raise OSError(errno.EIO, "Native root cleanup failed")
                    self._poll()
                while self._job is not None and self.active_processes():
                    if time.monotonic() >= deadline:
                        raise OSError(errno.EIO, "Native cleanup exceeded its allowance")
                    time.sleep(min(0.005, max(0, deadline - time.monotonic())))
        except (OSError, subprocess.TimeoutExpired) as error:
            failure = error
        finally:
            self._resources.close()
        if failure is not None and active_exception is None:
            raise OSError(errno.EIO, "Native process cleanup failed") from None

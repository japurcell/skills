"""Dependency-neutral Windows operations relative to verified directory handles.

No policy, scanner, audit, ACL or deadline decisions belong in this module.
Unsupported native operations raise OSError for callers to report safely.
"""
from __future__ import annotations

import errno
import os
import stat

class WindowsDirectoryHandles:
    """Open every child relative to a held native directory, without reparsing."""

    def __init__(self, resources):
        import ctypes
        from ctypes import wintypes
        self.ctypes = ctypes
        self.resources = resources
        self.parent = None
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.native = ctypes.WinDLL("ntdll")

        class UnicodeString(ctypes.Structure):
            _fields_ = [("length", wintypes.USHORT), ("maximum", wintypes.USHORT),
                       ("buffer", wintypes.LPWSTR)]

        class ObjectAttributes(ctypes.Structure):
            _fields_ = [("length", wintypes.ULONG), ("root", wintypes.HANDLE),
                       ("name", ctypes.POINTER(UnicodeString)), ("attributes", wintypes.ULONG),
                       ("security", ctypes.c_void_p), ("quality", ctypes.c_void_p)]

        class IoStatus(ctypes.Structure):
            _fields_ = [("status", ctypes.c_void_p), ("information", ctypes.c_size_t)]

        class FileInformation(ctypes.Structure):
            _fields_ = [("attributes", wintypes.DWORD), ("created", wintypes.FILETIME),
                       ("accessed", wintypes.FILETIME), ("written", wintypes.FILETIME),
                       ("volume", wintypes.DWORD), ("size_high", wintypes.DWORD),
                       ("size_low", wintypes.DWORD), ("links", wintypes.DWORD),
                       ("index_high", wintypes.DWORD), ("index_low", wintypes.DWORD)]

        self.UnicodeString, self.ObjectAttributes, self.IoStatus = UnicodeString, ObjectAttributes, IoStatus
        self.FileInformation = FileInformation
        self.kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
            ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        self.kernel.CreateFileW.restype = wintypes.HANDLE
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel.CloseHandle.restype = wintypes.BOOL
        self.kernel.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(FileInformation)]
        self.kernel.GetFileInformationByHandle.restype = wintypes.BOOL
        self.kernel.SetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.c_int,
            ctypes.c_void_p, wintypes.DWORD]
        self.kernel.SetFileInformationByHandle.restype = wintypes.BOOL
        self.native.NtCreateFile.argtypes = [ctypes.POINTER(wintypes.HANDLE), wintypes.ULONG,
            ctypes.POINTER(ObjectAttributes), ctypes.POINTER(IoStatus), ctypes.c_void_p,
            wintypes.ULONG, wintypes.ULONG, wintypes.ULONG, wintypes.ULONG, ctypes.c_void_p, wintypes.ULONG]
        self.native.NtCreateFile.restype = wintypes.LONG
        self.native.RtlNtStatusToDosError.argtypes = [wintypes.LONG]
        self.native.RtlNtStatusToDosError.restype = wintypes.ULONG

    def information(self, handle):
        info = self.FileInformation()
        if not self.kernel.GetFileInformationByHandle(handle, self.ctypes.byref(info)):
            raise self.ctypes.WinError(self.ctypes.get_last_error())
        if info.attributes & 0x400:
            raise OSError(errno.ELOOP, "Unsafe native file")
        return info

    def validate_name(self, name):
        # A single component plus RootDirectory never resolves mutable ancestors.
        if not name or name in {".", ".."} or any(char in name for char in "\\/:\0"):
            raise OSError(errno.ELOOP, "Unsafe native file")

    def open_handle(self, name, access=0, *, directory=False, create=False, exclusive=False, share_delete=False):
        self.validate_name(name)
        from ctypes import wintypes
        length = len(name.encode("utf-16-le"))
        if length > 65532:
            raise OSError(errno.ENAMETOOLONG, "Native component is too long")
        buffer = self.ctypes.create_unicode_buffer(name, length // 2 + 1)
        text = self.UnicodeString(length, length + 2, self.ctypes.cast(buffer, wintypes.LPWSTR))
        # OBJ_CASE_INSENSITIVE | OBJ_DONT_REPARSE: fail if name parsing
        # encounters any reparse, in addition to opening the leaf itself.
        attributes = self.ObjectAttributes(self.ctypes.sizeof(self.ObjectAttributes), self.parent,
            self.ctypes.pointer(text), 0x1040, None, None)
        handle, status = wintypes.HANDLE(), self.IoStatus()
        # SYNCHRONIZE + synchronous nonalert I/O, OPEN_REPARSE_POINT, and an
        # explicit directory/non-directory constraint. Delete sharing is opt-in.
        result = self.native.NtCreateFile(self.ctypes.byref(handle), access | 0x100080,
            self.ctypes.byref(attributes), self.ctypes.byref(status), None, 0, 7 if share_delete else 3,
            2 if create and exclusive else (3 if create else 1), 0x200020 | (1 if directory else 0x40), None, 0)
        if result < 0:
            raise self.ctypes.WinError(self.native.RtlNtStatusToDosError(result))
        try:
            info = self.information(handle)
            if bool(info.attributes & 0x10) != directory or (not directory and info.links != 1):
                raise OSError(errno.ELOOP, "Unsafe native file")
            return handle.value, status.information == 2
        except BaseException:
            self.kernel.CloseHandle(handle)
            raise

    def pin_root(self, path, *, access=0):
        handle = self.kernel.CreateFileW(str(path), 0x1000a0 | access, 3, None, 3, 0x02200000, None)
        if handle == self.ctypes.c_void_p(-1).value:
            raise self.ctypes.WinError(self.ctypes.get_last_error())
        self.resources.callback(self.kernel.CloseHandle, handle)
        if not self.information(handle).attributes & 0x10:
            raise OSError(errno.ELOOP, "Unsafe native file")
        self.parent = handle

    def descend(self, name, *, create=False, exclusive=False, access=0):
        handle, created = self.open_handle(name, 0x20 | access, directory=True, create=create, exclusive=exclusive)
        self.resources.callback(self.kernel.CloseHandle, handle)
        self.parent = handle
        return created

    def stat(self, name):
        from types import SimpleNamespace
        try:
            handle, _ = self.open_handle(name)
        except FileNotFoundError:
            return None
        try:
            info = self.information(handle)
            return SimpleNamespace(st_mode=stat.S_IFREG, st_nlink=info.links,
                st_size=(info.size_high << 32) | info.size_low, st_file_attributes=info.attributes)
        finally:
            self.kernel.CloseHandle(handle)

    def open(self, name, flags, *, access=0, normalize_readonly=False, share_delete=False):
        import msvcrt
        access |= 0x80000000 if flags & os.O_RDWR or not flags & os.O_WRONLY else 0
        if flags & (os.O_WRONLY | os.O_RDWR):
            access |= 0x40000000
        handle, _ = self.open_handle(name, access | (0x100 if normalize_readonly else 0),
            create=bool(flags & os.O_CREAT), exclusive=bool(flags & os.O_EXCL), share_delete=share_delete)
        try:
            # Windows chmod only controls the readonly attribute. Preserve that
            # behavior through the verified handle, without a pathname or DACL write.
            class BasicInformation(self.ctypes.Structure):
                _fields_ = [("created", self.ctypes.c_longlong), ("accessed", self.ctypes.c_longlong),
                           ("written", self.ctypes.c_longlong), ("changed", self.ctypes.c_longlong),
                           ("attributes", self.ctypes.c_ulong)]
            attributes = self.information(handle).attributes
            if normalize_readonly and attributes & 1:
                info = BasicInformation(0, 0, 0, 0, (attributes & ~1) or 0x80)
                if not self.kernel.SetFileInformationByHandle(handle, 0, self.ctypes.byref(info), self.ctypes.sizeof(info)):
                    raise self.ctypes.WinError(self.ctypes.get_last_error())
            descriptor = msvcrt.open_osfhandle(handle, (flags & os.O_APPEND) | os.O_NOINHERIT)
        except BaseException:
            self.kernel.CloseHandle(handle)
            raise
        try:
            msvcrt.setmode(descriptor, os.O_BINARY)
            return descriptor
        except BaseException:
            os.close(descriptor)
            raise

    def mutate_name(self, name, destination=None):
        from ctypes import wintypes
        if destination is not None:
            self.validate_name(destination)
        handle, _ = self.open_handle(name, 0x10000)
        try:
            if destination is None:
                info = wintypes.BOOLEAN(1)
                kind = 4  # FileDispositionInfo
            else:
                class Rename(self.ctypes.Structure):
                    _fields_ = [("replace", wintypes.DWORD), ("root", wintypes.HANDLE),
                               ("length", wintypes.DWORD), ("name", wintypes.WCHAR * (len(destination.encode("utf-16-le")) // 2 + 1))]
                info = Rename(1, self.parent, len(destination.encode("utf-16-le")), destination)
                kind = 3  # FileRenameInfo, relative destination under the same held parent
            if not self.kernel.SetFileInformationByHandle(handle, kind, self.ctypes.byref(info), self.ctypes.sizeof(info)):
                raise self.ctypes.WinError(self.ctypes.get_last_error())
        finally:
            self.kernel.CloseHandle(handle)

    def replace(self, source, destination):
        self.mutate_name(source, destination)

    def remove(self, name):
        self.mutate_name(name)

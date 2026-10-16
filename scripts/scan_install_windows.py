"""Windows-only handle-relative packaging; no provider or detector imports.

API references and execution limits are retained in t3c-evidence.md.
"""
from contextlib import contextmanager, ExitStack
import ctypes
from ctypes import wintypes
import os
from pathlib import PurePosixPath
import secrets
import time

READ_CONTROL = 0x20000
CREATE_SECURITY = 0xe0000
DELETE = 0x10000

def private(handle, *, create=False, ancestor=False, drive_root=False, creation_parent=False):
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
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.LocalFree.argtypes = (pointer,)
    advapi.GetTokenInformation.argtypes = (wintypes.HANDLE, wintypes.DWORD, pointer, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD))
    token = wintypes.HANDLE()
    if not advapi.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(token)):
        raise OSError("Unsafe installation access control")
    try:
        required = wintypes.DWORD()
        advapi.GetTokenInformation(token, 1, None, 0, ctypes.byref(required))
        if not 0 < required.value <= 65536:
            raise OSError("Unsafe installation access control")
        buffer = ctypes.create_string_buffer(required.value)
        if not advapi.GetTokenInformation(token, 1, buffer, len(buffer), ctypes.byref(required)):
            raise OSError("Unsafe installation access control")
        sid = ctypes.cast(buffer, ctypes.POINTER(pointer))[0]
        text = wintypes.LPWSTR()
        advapi.ConvertSidToStringSidW.argtypes = (pointer, ctypes.POINTER(wintypes.LPWSTR))
        if not advapi.ConvertSidToStringSidW(sid, ctypes.byref(text)):
            raise OSError("Unsafe installation access control")
        try:
            owner = text.value
        finally:
            kernel.LocalFree(ctypes.cast(text, pointer))
    finally:
        kernel.CloseHandle(token)
    descriptor = pointer()
    advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(pointer), pointer)
    if create:
        if not advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW("O:" + owner + "D:P(A;OICI;FA;;;" + owner + ")", 1, ctypes.byref(descriptor), None):
            raise OSError("Unsafe installation access control")
        try:
            acl, present, defaulted = pointer(), wintypes.BOOL(), wintypes.BOOL()
            advapi.GetSecurityDescriptorDacl.argtypes = (pointer, ctypes.POINTER(wintypes.BOOL), ctypes.POINTER(pointer), ctypes.POINTER(wintypes.BOOL))
            if not advapi.GetSecurityDescriptorDacl(descriptor, ctypes.byref(present), ctypes.byref(acl), ctypes.byref(defaulted)) or not present or not acl:
                raise OSError("Unsafe installation access control")
            advapi.SetSecurityInfo.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, pointer, pointer, pointer, pointer)
            advapi.SetSecurityInfo.restype = wintypes.DWORD
            if advapi.SetSecurityInfo(handle, 1, 0x80000005, sid, None, acl, None):
                raise OSError("Unsafe installation access control")
        finally:
            kernel.LocalFree(descriptor)
    actual_owner, acl, descriptor = pointer(), pointer(), pointer()
    advapi.GetSecurityInfo.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD,
        ctypes.POINTER(pointer), pointer, ctypes.POINTER(pointer), pointer, ctypes.POINTER(pointer))
    advapi.GetSecurityInfo.restype = wintypes.DWORD
    if advapi.GetSecurityInfo(handle, 1, 5, ctypes.byref(actual_owner), None, ctypes.byref(acl), None, ctypes.byref(descriptor)):
        raise OSError("Unsafe installation access control")
    try:
        advapi.EqualSid.argtypes = (pointer, pointer)
        def sid_text(value):
            text = wintypes.LPWSTR()
            if not advapi.ConvertSidToStringSidW(value, ctypes.byref(text)):
                raise OSError("Unsafe installation access control")
            try:
                return text.value
            finally:
                kernel.LocalFree(ctypes.cast(text, pointer))
        trusted = {owner, "S-1-5-18", "S-1-5-32-544"}
        if (sid_text(actual_owner) not in trusted if ancestor else not advapi.EqualSid(actual_owner, sid)):
            raise OSError("Unsafe installation access control")
        if not acl:
            raise OSError("Unsafe installation access control")
        # ACL header: revision/reserved/size/count/reserved, followed by ACEs.
        header = ctypes.string_at(acl, 8)
        count = int.from_bytes(header[4:6], "little")
        ace = pointer()
        advapi.GetAce.argtypes = (pointer, wintypes.DWORD, ctypes.POINTER(pointer))
        if ancestor:
            if not 0 < count <= 64:
                raise OSError("Unsafe installation access control")
            # Directory add-file/add-child rights at a drive root cannot replace
            # the protected child subsequently opened with OBJ_DONT_REPARSE.
            dangerous = 0x500d0150 | (0 if drive_root and not creation_parent else 6)
            for index in range(count):
                if not advapi.GetAce(acl, index, ctypes.byref(ace)):
                    raise OSError("Unsafe installation access control")
                prefix = ctypes.string_at(ace, 8)
                if prefix[0] not in {0, 1}:
                    raise OSError("Unsafe installation access control")
                effective = not prefix[1] & 8
                inherited_on_new_child = creation_parent and prefix[1] & 3
                if prefix[0] == 0 and (effective or inherited_on_new_child) and sid_text(pointer(ace.value + 8)) not in trusted and int.from_bytes(prefix[4:8], "little") & dangerous:
                    raise OSError("Unsafe installation access control")
            return
        if count != 1:
            raise OSError("Unsafe installation access control")
        if not advapi.GetAce(acl, 0, ctypes.byref(ace)):
            raise OSError("Unsafe installation access control")
        prefix = ctypes.string_at(ace, 8)
        if prefix[0] != 0 or int.from_bytes(prefix[4:8], "little") != 0x1f01ff or not advapi.EqualSid(pointer(ace.value + 8), sid):
            raise OSError("Unsafe installation access control")
    finally:
        kernel.LocalFree(descriptor)


class PackageDirectory:
    def __init__(self, native, failure):
        self.native, self.failure = native, failure
        self.deadline = time.monotonic() + 10
        native.kernel.GetFileInformationByHandleEx.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
        native.kernel.GetFileInformationByHandleEx.restype = wintypes.BOOL

    def check(self):
        if time.monotonic() > self.deadline:
            raise self.failure("installation_timeout")

    @contextmanager
    def at(self, parent):
        original = self.native.parent
        self.native.parent = parent
        try:
            yield
        finally:
            self.native.parent = original

    @contextmanager
    def directory(self, parent, name, *, create=False, delete=False):
        self.check()
        with self.at(parent):
            handle, _ = self.native.open_handle(name, 1 | READ_CONTROL | (CREATE_SECURITY if create else 0) | (DELETE if delete else 0),
                directory=True, create=create, exclusive=create, share_delete=delete)
        try:
            private(handle, create=create)
            yield handle
        finally:
            self.native.kernel.CloseHandle(handle)

    def entries(self, handle):
        class Entry(ctypes.Structure):
            _fields_ = [("next", wintypes.DWORD), ("index", wintypes.DWORD),
                *((name, ctypes.c_longlong) for name in ("created", "accessed", "written", "changed", "size", "allocated")),
                ("attributes", wintypes.DWORD), ("length", wintypes.DWORD), ("ea", wintypes.DWORD),
                ("short_length", ctypes.c_byte), ("short_name", wintypes.WCHAR * 12),
                ("id", ctypes.c_longlong), ("name", wintypes.WCHAR * 1)]
        names, consumed, restart = {}, 0, True
        while True:
            self.check()
            buffer = ctypes.create_string_buffer(65536)
            if not self.native.kernel.GetFileInformationByHandleEx(handle, 11 if restart else 10, buffer, len(buffer)):
                if ctypes.get_last_error() == 18:  # ERROR_NO_MORE_FILES
                    return names
                raise ctypes.WinError(ctypes.get_last_error())
            restart = False
            consumed += len(buffer)
            if consumed > 1048576:
                raise self.failure("installation_inventory_invalid")
            offset = 0
            while True:
                self.check()
                if offset + Entry.name.offset > len(buffer):
                    raise self.failure("installation_inventory_invalid")
                entry = Entry.from_buffer(buffer, offset)
                if entry.length % 2 or entry.length > 1024 or offset + Entry.name.offset + entry.length > len(buffer):
                    raise self.failure("installation_inventory_invalid")
                name = ctypes.string_at(ctypes.addressof(buffer) + offset + Entry.name.offset, entry.length).decode("utf-16-le")
                if name not in {".", ".."}:
                    self.native.validate_name(name)
                    if name in names or len(names) >= 64 or entry.attributes & 0x400:
                        raise self.failure("installation_inventory_invalid")
                    names[name] = bool(entry.attributes & 0x10)
                if not entry.next:
                    break
                if entry.next % 8 or entry.next < Entry.name.offset + entry.length:
                    raise self.failure("installation_inventory_invalid")
                offset += entry.next

    def read_tree(self, parent, name):
        inventory, files = set(), {}
        def visit(handle, prefix="", depth=0):
            if depth > 4:
                raise self.failure("installation_inventory_invalid")
            for child, directory in self.entries(handle).items():
                relative = prefix + child
                inventory.add(relative)
                if len(inventory) > 64:
                    raise self.failure("installation_inventory_invalid")
                if directory:
                    with self.directory(handle, child) as nested:
                        visit(nested, relative + "/", depth + 1)
                else:
                    with self.at(handle):
                        descriptor = self.native.open(child, os.O_RDONLY, access=READ_CONTROL)
                    try:
                        import msvcrt
                        private(msvcrt.get_osfhandle(descriptor))
                        info = os.fstat(descriptor)
                        if info.st_size > 1048576:
                            raise self.failure("installation_inventory_invalid")
                        raw = os.read(descriptor, 1048577)
                        if len(raw) != info.st_size:
                            raise self.failure("installation_inventory_invalid")
                        files[relative] = raw
                    finally:
                        os.close(descriptor)
        try:
            with self.directory(parent, name) as root:
                visit(root)
        except FileNotFoundError:
            # Missing children of an existing root are not an absent bundle.
            with self.at(parent):
                try:
                    handle, _ = self.native.open_handle(name, directory=True)
                except FileNotFoundError:
                    return None
                self.native.kernel.CloseHandle(handle)
            raise self.failure("installation_inventory_invalid") from None
        return inventory, files

    def rename(self, parent, source, destination):
        self.check()
        self.native.validate_name(destination)
        # Source and destination directory names are interpreted under one held parent.
        with self.directory(parent, source, delete=True) as handle:
            units = len(destination.encode("utf-16-le")) // 2
            class Rename(ctypes.Structure):
                _fields_ = [("replace", wintypes.BOOL), ("root", wintypes.HANDLE),
                    ("length", wintypes.DWORD), ("name", wintypes.WCHAR * (units + 1))]
            value = Rename(False, parent, units * 2, destination)
            if not self.native.kernel.SetFileInformationByHandle(handle, 3, ctypes.byref(value), ctypes.sizeof(value)):
                raise ctypes.WinError(ctypes.get_last_error())

    def dispose(self, handle):
        value = wintypes.BOOLEAN(1)
        if not self.native.kernel.SetFileInformationByHandle(handle, 4, ctypes.byref(value), ctypes.sizeof(value)):
            raise ctypes.WinError(ctypes.get_last_error())

    def remove_tree(self, parent, name, owned, *, prefix="", partial=False):
        # Called only after exact ownership validation, or for this invocation's new stage.
        self.check()
        with self.directory(parent, name, delete=True) as handle:
            entries = self.entries(handle)
            expected = {item[len(prefix):].split("/", 1)[0] for item in owned if item.startswith(prefix)}
            if (not set(entries).issubset(expected)) or (not partial and set(entries) != expected):
                raise self.failure("installation_ownership_invalid")
            for child, directory in entries.items():
                if directory:
                    self.remove_tree(handle, child, owned, prefix=prefix + child + "/", partial=partial)
                else:
                    with self.at(handle):
                        leaf, _ = self.native.open_handle(child, DELETE | READ_CONTROL, share_delete=True)
                    try:
                        private(leaf)
                        self.dispose(leaf)
                    finally:
                        self.native.kernel.CloseHandle(leaf)
            self.dispose(handle)

    def write_tree(self, stage, payload):
        with self.directory(self.native.parent, stage) as root:
            def put(handle, parts, raw):
                self.check()
                if len(parts) > 1:
                    child = parts[0]
                    if child in self.entries(handle):
                        with self.directory(handle, child) as nested:
                            put(nested, parts[1:], raw)
                    else:
                        with self.directory(handle, child, create=True) as nested:
                            put(nested, parts[1:], raw)
                    return
                with self.at(handle):
                    descriptor = self.native.open(parts[0], os.O_WRONLY | os.O_CREAT | os.O_EXCL, access=CREATE_SECURITY)
                try:
                    import msvcrt
                    private(msvcrt.get_osfhandle(descriptor), create=True)
                    with os.fdopen(descriptor, "wb", closefd=False) as stream:
                        stream.write(raw)
                        stream.flush()
                        os.fsync(stream.fileno())
                finally:
                    os.close(descriptor)
            for relative, raw in payload.items():
                put(root, PurePosixPath(relative).parts, raw)

    @contextmanager
    def lock(self, parent, name):
        import msvcrt
        self.check()
        with self.at(parent):
            try:
                descriptor = self.native.open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL, access=CREATE_SECURITY)
                created = True
            except FileExistsError:
                descriptor = self.native.open(name, os.O_RDWR, access=READ_CONTROL)
                created = False
        locked = False
        try:
            private(msvcrt.get_osfhandle(descriptor), create=created)
            if os.fstat(descriptor).st_size == 0:
                os.write(descriptor, b"0")
            os.lseek(descriptor, 0, os.SEEK_SET)
            try:
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            except OSError:
                raise self.failure("installation_busy") from None
            locked = True
            yield
        finally:
            if locked:
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            os.close(descriptor)


def install(destination, assets, payload, validate, failure, *, dry_run):
    namespace = {}
    exec(compile(assets["hooks/runtime/scan_native_file.py"], "scan_native_file.py", "exec"), namespace)
    with ExitStack() as resources:
        native = namespace["WindowsDirectoryHandles"](resources)
        native.pin_root(destination.anchor, access=READ_CONTROL)
        private(native.parent, ancestor=True, drive_root=True)
        for component in destination.parent.parts[1:]:
            try:
                native.descend(component, access=READ_CONTROL)
                private(native.parent, ancestor=True)
            except FileNotFoundError:
                private(native.parent, ancestor=True, creation_parent=True)
                if dry_run:
                    return
                native.descend(component, create=True, exclusive=True, access=CREATE_SECURITY)
                private(native.parent, create=True)
        parent = native.parent
        private(parent, ancestor=True, creation_parent=True)
        owned = set(payload)
        for relative in payload:
            owned.update(str(part) for part in PurePosixPath(relative).parents if str(part) != ".")
        tree = PackageDirectory(native, failure)
        name, previous = destination.name, destination.name + ".previous"
        def inspect(child):
            observed = tree.read_tree(parent, child)
            if observed is not None:
                inventory, files = observed
                validate(inventory, files.__getitem__, assets, destination)
            return observed is not None
        if dry_run:
            inspect(name)
            inspect(previous)
            return
        with tree.lock(parent, name + ".install-lock"):
            current, backup = inspect(name), inspect(previous)
            if backup and not current:
                tree.rename(parent, previous, name)
                current = True
            elif backup:
                tree.remove_tree(parent, previous, owned)
            stage = ".scan-secrets-stage-" + secrets.token_hex(12)
            staged = False
            try:
                # The exclusive new stage is this invocation's only cleanup target.
                with tree.directory(parent, stage, create=True):
                    pass
                staged = True
                tree.write_tree(stage, payload)
                if current:
                    tree.rename(parent, name, previous)
                try:
                    tree.rename(parent, stage, name)
                    staged = False
                except BaseException:
                    if current:
                        tree.deadline = time.monotonic() + 5
                        tree.rename(parent, previous, name)
                    raise
                if current:
                    tree.remove_tree(parent, previous, owned)
            finally:
                if staged:
                    tree.deadline = time.monotonic() + 5
                    tree.remove_tree(parent, stage, owned, partial=True)

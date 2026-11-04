"""Qualification-only fixed fixture. External trusted controller is prerequisite."""
import json
import hashlib
import os
import re
import struct
import sys
import time

NODE_SHA256 = "d702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5"
ARCHIVE_SHA256 = "d2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5"
HEADERS_SHA256 = "33bf331af1c9812d25f82efb53de793b36b54c23b8ad49652c4325bbe7f98216"
NODE_LIB_SHA256 = "a0a84aa03917b578d286010b7521837e9ff1136ffb2e4a406c14316c33fd06f7"
MIB = 1024 * 1024
NATIVE_CASES = (
    "positive-user", "positive-admin", "acl-change", "wrong-digest", "missing-image",
    "changed-image", "changed-parent", "reparse-image", "reparse-parent", "hardlink",
    "nonfile", "broad-child", "broad-root", "unprotected-root", "denied-metadata", "denied-sharing",
    "wrong-arch", "malformed-pe", "api-mismatch", "extra-dll", "conflicting-import", "local-redirection",
    "manifest-redirection", "throw-before", "require-failure", "throw-after", "nonzero",
    "stdout-overflow", "stderr-overflow", "timeout", "retained-writer", "changed-selection",
    "replaced-owned-file", "oversized-artifact", "synthetic-close", "synthetic-overflow-close",
    "forged-success", "unknown-result", "extra-result",
)


class Refusal(Exception):
    def __init__(self, phase, reason, state="refused"):
        self.phase, self.reason, self.state = phase, reason, state


class Windows:
    """Private implementation of this one fixed fixture, never a native API."""
    def __init__(self):
        import ctypes as c
        self.c = c
        if c.sizeof(c.c_void_p) != 8:
            raise Refusal("prerequisite", "platform", "unknown")
        self.DWORD, self.BOOL, self.HANDLE = c.c_uint32, c.c_int32, c.c_void_p
        D, B, H, P, W = self.DWORD, self.BOOL, self.HANDLE, c.c_void_p, c.c_wchar_p
        PD, PH = c.POINTER(D), c.POINTER(H)
        # Fixed system images only. This does not change Node's DLL search policy.
        self.kernel = c.WinDLL("kernel32.dll", use_last_error=True, winmode=0x800)
        self.security = c.WinDLL("advapi32.dll", use_last_error=True, winmode=0x800)
        def bind(library, name, result, args):
            function = getattr(library, name)
            function.restype, function.argtypes = result, args
            setattr(self, name, function)
        for name, result, args in (
            ("GetCurrentProcess", H, []), ("GetCurrentThread", H, []),
            ("CloseHandle", B, [H]), ("LocalFree", H, [H]),
            ("CreateFileW", H, [W, D, D, P, D, D, H]),
            ("CreateDirectoryW", B, [W, P]), ("RemoveDirectoryW", B, [W]),
            ("DeleteFileW", B, [W]), ("MoveFileExW", B, [W, W, D]),
            ("CreateHardLinkW", B, [W, W, P]), ("CreateSymbolicLinkW", c.c_ubyte, [W, W, D]),
            ("ReadFile", B, [H, P, D, PD, P]), ("WriteFile", B, [H, P, D, PD, P]),
            ("SetFilePointerEx", B, [H, c.c_int64, P, D]),
            ("GetFileType", D, [H]), ("GetFileInformationByHandleEx", B, [H, c.c_int, P, D]),
            ("GetFinalPathNameByHandleW", D, [H, P, D, D]),
            ("GetSystemDirectoryW", D, [P, D]), ("GetWindowsDirectoryW", D, [P, D]),
            ("GetVolumeInformationW", B, [W, P, D, PD, PD, PD, P, D]),
            ("CreatePipe", B, [PH, PH, P, D]), ("SetHandleInformation", B, [H, D, D]),
            ("InitializeProcThreadAttributeList", B, [P, D, D, c.POINTER(c.c_size_t)]),
            ("UpdateProcThreadAttribute", B, [P, D, c.c_size_t, P, c.c_size_t, P, P]),
            ("DeleteProcThreadAttributeList", None, [P]),
            ("CreateProcessW", B, [W, P, P, P, B, D, P, W, P, P]),
            ("PeekNamedPipe", B, [H, P, D, PD, PD, PD]),
            ("WaitForSingleObject", D, [H, D]), ("GetExitCodeProcess", B, [H, PD]),
            ("TerminateProcess", B, [H, D]),
            ("K32EnumProcessModulesEx", B, [H, P, D, PD, D]),
            ("K32GetModuleFileNameExW", D, [H, H, P, D]),
        ):
            bind(self.kernel, name, result, args)
        for name, result, args in (
            ("OpenProcessToken", B, [H, D, PH]), ("OpenThreadToken", B, [H, D, B, PH]),
            ("GetTokenInformation", B, [H, c.c_int, P, D, PD]),
            ("IsValidSid", B, [P]), ("GetLengthSid", D, [P]),
            ("CreateWellKnownSid", B, [c.c_int, P, P, PD]),
            ("InitializeSecurityDescriptor", B, [P, D]),
            ("SetSecurityDescriptorOwner", B, [P, P, B]),
            ("SetSecurityDescriptorDacl", B, [P, B, P, B]),
            ("SetSecurityDescriptorControl", B, [P, c.c_uint16, c.c_uint16]),
            ("InitializeAcl", B, [P, D, D]), ("AddAccessAllowedAceEx", B, [P, D, D, D, P]),
            ("GetSecurityInfo", D, [H, c.c_int, D, PH, PH, PH, PH, PH]),
            ("SetSecurityInfo", D, [H, c.c_int, D, P, P, P, P]),
            ("IsValidSecurityDescriptor", B, [P]), ("GetSecurityDescriptorLength", D, [P]),
            ("GetSecurityDescriptorControl", B, [P, c.POINTER(c.c_uint16), PD]),
            ("GetSecurityDescriptorDacl", B, [P, c.POINTER(B), PH, c.POINTER(B)]),
            ("IsValidAcl", B, [P]), ("GetAclInformation", B, [P, P, D, c.c_int]),
            ("GetAce", B, [P, D, PH]),
        ):
            bind(self.security, name, result, args)
        class SA(c.Structure):
            _fields_ = [("length", D), ("descriptor", P), ("inherit", B)]
        class SD(c.Structure):
            _fields_ = [("revision", c.c_ubyte), ("reserved", c.c_ubyte),
                        ("control", c.c_uint16), ("owner", P), ("group", P),
                        ("sacl", P), ("dacl", P)]
        class STANDARD(c.Structure):
            _fields_ = [("allocation", c.c_int64), ("size", c.c_int64),
                        ("links", D), ("delete", c.c_ubyte), ("directory", c.c_ubyte)]
        class TAG(c.Structure):
            _fields_ = [("attributes", D), ("tag", D)]
        class FILEID(c.Structure):
            _fields_ = [("volume", c.c_uint64), ("id", c.c_ubyte * 16)]
        class STARTUP(c.Structure):
            _fields_ = [("cb", D), ("reserved", W), ("desktop", W), ("title", W),
                        ("x", D), ("y", D), ("xsize", D), ("ysize", D),
                        ("xchars", D), ("ychars", D), ("fill", D), ("flags", D),
                        ("show", c.c_uint16), ("reservedsize", c.c_uint16),
                        ("reservedbytes", P), ("stdin", H), ("stdout", H), ("stderr", H)]
        class STARTUPEX(c.Structure):
            _fields_ = [("startup", STARTUP), ("attributes", P)]
        class PROCESS(c.Structure):
            _fields_ = [("process", H), ("thread", H), ("pid", D), ("tid", D)]
        self.SA, self.SD = SA, SD
        self.STANDARD, self.TAG, self.FILEID = STANDARD, TAG, FILEID
        self.STARTUPEX, self.PROCESS = STARTUPEX, PROCESS
        if any(c.sizeof(kind) != size for kind, size in
               ((SA, 24), (SD, 40), (STANDARD, 24), (TAG, 8), (FILEID, 24), (STARTUP, 104), (STARTUPEX, 112), (PROCESS, 24))):
            raise Refusal("prerequisite", "native", "unknown")
        self.invalid = c.c_void_p(-1).value
        self.resources, self.buffers, self.pins, self.created = [], [], [], []
        self.pin_paths = {}
        self.first = None
        self.process = None
        self.thread_resource = None
        self.child_pipe_ends = []
        self.exit_code = None
        self.stdin_parent = None
        self.output = None
        self.retained_writer = None
        self.exited, self.eof, self.closed = True, [True, True], False
        self.retained = True
        self.close_failed = False
        self.stage_bytes = 0
        self.captured, self.discarded = [0, 0], [0, 0]
        self.pipe_failed, self.wait_failed, self.termination_attempted = [False, False], False, False

    def fail(self, phase, reason, state="refused"):
        failure = Refusal(phase, reason, state)
        if self.first is None:
            # Keep closed evidence, never a raised exception/traceback that
            # retains descriptor pointers or operation-local buffers.
            self.first = Refusal(phase, reason, state)
        return failure

    def checked(self, result, phase="custody"):
        if not result:
            code = self.c.get_last_error()  # Own this call's thread-local error now.
            reason = {2: "missing", 3: "missing", 5: "access", 32: "sharing", 80: "changed", 183: "changed"}.get(code, "native")
            raise self.fail(phase, reason, "unknown" if reason == "native" else "refused")
        return result

    def own(self, value, kind="handle"):
        if not value or value == self.invalid:
            self.checked(False)
        resource = [value, kind, False]
        self.resources.append(resource)
        return resource

    def release(self, resource):
        if resource[2]:
            return
        resource[2] = True  # One attempt, including failed closes. Never retry a reused value.
        value, kind, _ = resource
        try:
            if kind == "handle":
                if not self.CloseHandle(value):
                    self.close_failed = True
                    self.fail("close", "close", "unknown")
            elif kind == "descriptor":
                if self.LocalFree(value):
                    self.close_failed = True
                    self.fail("close", "close", "unknown")
            elif kind == "attributes":
                self.DeleteProcThreadAttributeList(value)
        except BaseException:
            self.close_failed = True
            self.fail("close", "close", "unknown")

    def identity(self):
        c = self.c
        thread = self.HANDLE()
        if self.OpenThreadToken(self.GetCurrentThread(), 0x8, True, c.byref(thread)):
            acquired = self.own(thread.value)
            self.release(acquired)
            raise self.fail("prerequisite", "identity")
        if c.get_last_error() != 1008:  # ERROR_NO_TOKEN only; not an arbitrary failure.
            raise self.fail("prerequisite", "identity", "unknown")
        token = self.HANDLE()
        self.checked(self.OpenProcessToken(self.GetCurrentProcess(), 0x8, c.byref(token)), "prerequisite")
        owned = self.own(token.value)
        try:
            length = self.DWORD()
            okay = self.GetTokenInformation(token, 1, None, 0, c.byref(length))
            if okay or c.get_last_error() != 122 or not 8 <= length.value <= 65536:
                raise self.fail("prerequisite", "identity", "unknown")
            buffer = c.create_string_buffer(length.value)
            self.checked(self.GetTokenInformation(token, 1, buffer, len(buffer), c.byref(length)), "prerequisite")
            pointer = c.cast(buffer, c.POINTER(self.HANDLE))[0]
            start = c.addressof(buffer)
            if not pointer or not start <= pointer <= start + len(buffer) - 8:
                raise self.fail("prerequisite", "identity", "unknown")
            self.checked(self.IsValidSid(pointer), "prerequisite")
            size = self.GetLengthSid(pointer)
            if not 8 <= size <= 68 or pointer + size > start + len(buffer):
                raise self.fail("prerequisite", "identity", "unknown")
            self.user = c.string_at(pointer, size)
        finally:
            self.release(owned)
        self.trusted = [self.user]
        for sid_type in (22, 26):  # WinLocalSystemSid, WinBuiltinAdministratorsSid.
            buffer, length = c.create_string_buffer(68), self.DWORD(68)
            self.checked(self.CreateWellKnownSid(sid_type, None, buffer, c.byref(length)), "prerequisite")
            if not 8 <= length.value <= 68 or not self.IsValidSid(buffer):
                raise self.fail("prerequisite", "identity", "unknown")
            sid = bytes(buffer[:length.value])
            if sid not in self.trusted:
                self.trusted.append(sid)

    def security_attributes(self, directory=False, administrators=False, broad=False, protected=True, process=False):
        c = self.c
        trustees = list(self.trusted if administrators else [self.user])
        if broad:
            buffer, length = c.create_string_buffer(68), self.DWORD(68)
            self.checked(self.CreateWellKnownSid(1, None, buffer, c.byref(length)))  # WinWorldSid.
            trustees.append(bytes(buffer[:length.value]))
        sid_buffers = [c.create_string_buffer(sid) for sid in trustees]
        acl = c.create_string_buffer(8 + sum(8 + len(sid) for sid in trustees))
        descriptor = self.SD()
        self.checked(self.InitializeAcl(acl, len(acl), 2))
        for sid in sid_buffers:
            self.checked(self.AddAccessAllowedAceEx(acl, 2, 3 if directory else 0,
                                                   0x10000000 if process else 0x1F01FF, sid))
        self.checked(self.InitializeSecurityDescriptor(c.byref(descriptor), 1))
        self.checked(self.SetSecurityDescriptorOwner(c.byref(descriptor), sid_buffers[0], False))
        self.checked(self.SetSecurityDescriptorDacl(c.byref(descriptor), True, acl, False))
        self.checked(self.SetSecurityDescriptorControl(c.byref(descriptor), 0x1000, 0x1000 if protected else 0))
        attributes = self.SA(c.sizeof(self.SA), c.addressof(descriptor), False)
        self.buffers.extend([sid_buffers, acl, descriptor, attributes])
        return attributes

    def inspect_security(self, handle, directory, anchor=False):
        c = self.c
        owner, dacl, descriptor = self.HANDLE(), self.HANDLE(), self.HANDLE()
        status = self.GetSecurityInfo(handle, 1, 5, c.byref(owner), None, c.byref(dacl), None, c.byref(descriptor))
        if status != 0:
            raise self.fail("custody", "access" if status == 5 else "native", "unknown")
        allocation = self.own(descriptor.value, "descriptor")
        try:
            if not self.IsValidSecurityDescriptor(descriptor):
                raise self.fail("custody", "dacl")
            length = self.GetSecurityDescriptorLength(descriptor)
            if not 20 <= length <= 256 * 1024:
                raise self.fail("custody", "bounds")
            start, end = descriptor.value, descriptor.value + length
            def sid_at(pointer, limit=end):
                if not pointer or not start <= pointer <= limit - 8:
                    raise self.fail("custody", "dacl")
                if not self.IsValidSid(pointer):
                    raise self.fail("custody", "dacl")
                size = self.GetLengthSid(pointer)
                if not 8 <= size <= 68 or pointer + size > limit:
                    raise self.fail("custody", "dacl")
                return c.string_at(pointer, size)
            actual_owner = sid_at(owner.value)
            if actual_owner not in (self.trusted if anchor else [self.user]):
                raise self.fail("custody", "owner")
            control, revision = c.c_uint16(), self.DWORD()
            self.checked(self.GetSecurityDescriptorControl(descriptor, c.byref(control), c.byref(revision)))
            if not control.value & 0x8000:  # GetSecurityInfo must give bounded self-relative storage.
                raise self.fail("custody", "dacl")
            if not anchor and not control.value & 0x1000:
                raise self.fail("custody", "dacl")
            present, defaulted, checked_acl = self.BOOL(), self.BOOL(), self.HANDLE()
            self.checked(self.GetSecurityDescriptorDacl(descriptor, c.byref(present), c.byref(checked_acl), c.byref(defaulted)))
            if not present.value or not dacl.value or checked_acl.value != dacl.value:
                raise self.fail("custody", "dacl")
            if not start <= dacl.value <= end - 8 or not self.IsValidAcl(dacl):
                raise self.fail("custody", "dacl")
            header = c.string_at(dacl, 8)
            _, _, acl_size, count, _ = struct.unpack("<BBHHH", header)
            info = (self.DWORD * 3)()
            self.checked(self.GetAclInformation(dacl, info, c.sizeof(info), 2))
            if not 8 <= acl_size <= 65535 or dacl.value + acl_size > end or count != info[0] or count > 256:
                raise self.fail("custody", "bounds")
            if not 1 <= count <= (256 if anchor else 3):
                raise self.fail("custody", "dacl")
            seen = set()
            for index in range(count):
                ace = self.HANDLE()
                self.checked(self.GetAce(dacl, index, c.byref(ace)))
                if not dacl.value + 8 <= ace.value <= dacl.value + acl_size - 8:
                    raise self.fail("custody", "dacl")
                kind, flags, size, mask = struct.unpack("<BBHI", c.string_at(ace, 8))
                if kind != 0 or size < 16 or ace.value + size > dacl.value + acl_size:
                    raise self.fail("custody", "dacl")
                trustee = sid_at(ace.value + 8, ace.value + size)
                if 8 + len(trustee) != size or trustee in seen:
                    raise self.fail("custody", "dacl")
                seen.add(trustee)
                if anchor:
                    if flags & ~0x13 or (trustee not in self.trusted and mask & ~0x1200A9):
                        raise self.fail("custody", "dacl")
                elif (trustee not in self.trusted or mask != 0x1F01FF
                      or flags != (3 if directory else 0)):
                    raise self.fail("custody", "dacl")
            if not anchor and self.user not in seen:
                raise self.fail("custody", "dacl")
        finally:
            self.release(allocation)

    def info(self, handle, directory, trusted_os=False):
        c = self.c
        standard, tag, identity = self.STANDARD(), self.TAG(), self.FILEID()
        for category, value in ((1, standard), (9, tag), (18, identity)):
            self.checked(self.GetFileInformationByHandleEx(handle, category, c.byref(value), c.sizeof(value)))
        if self.GetFileType(handle) != 1 or bool(standard.directory) != directory:
            raise self.fail("custody", "type")
        if tag.attributes & 0x400 or tag.tag:
            raise self.fail("custody", "reparse")
        if standard.delete or (not directory and (standard.links < 1 if trusted_os else standard.links != 1)):
            raise self.fail("custody", "links")
        if not identity.volume or not any(identity.id):
            raise self.fail("custody", "identity", "unknown")
        return (identity.volume, bytes(identity.id)), standard.size

    def final_path(self, handle, guid=True):
        c = self.c
        buffer = c.create_unicode_buffer(4097)
        length = self.GetFinalPathNameByHandleW(handle, buffer, len(buffer), 1 if guid else 0)
        if not 0 < length < len(buffer):
            raise self.fail("custody", "namespace", "unknown")
        value = buffer.value
        if len(value.encode("utf-8")) > 4096 or (guid and not re.match(r"^\\\\\?\\Volume\{[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}\}\\", value)):
            raise self.fail("custody", "namespace")
        return value.rstrip("\\")

    def open_pin(self, path, directory=False, policy="private", expected=None, temporary=False):
        if not dos_path(path) and not (directory and re.fullmatch(r"[A-Z]:\\", path)):
            raise self.fail("custody", "namespace")
        key = path.casefold().rstrip("\\")
        previous = self.pin_paths.get(key)
        if previous is not None and not previous["handle"][2] and not temporary:
            identity, _ = self.info(previous["handle"][0], directory, previous["policy"] == "host" and policy == "host")
            if identity != previous["identity"] or (expected is not None and identity != expected):
                raise self.fail("custody", "changed")
            if policy != "host" and previous["policy"] == "host":
                self.inspect_security(previous["handle"][0], directory, policy == "anchor")
                previous["policy"] = policy
            return previous
        flags = 0x200000 | (0x2000000 if directory else 0)
        handle = self.CreateFileW(path, 0x120089, 1, None, 3, flags, None)
        if handle == self.invalid or not handle:
            self.checked(False)
        resource = self.own(handle)
        identity, size = self.info(handle, directory, policy == "host")
        if policy != "host":
            self.inspect_security(handle, directory, policy == "anchor")
        final = self.final_path(handle)
        parent_pin = self.pin_paths.get(os.path.dirname(path).casefold().rstrip("\\"))
        if parent_pin is not None and parent_pin["path"].casefold().rstrip("\\") != key:
            if os.path.dirname(final).rstrip("\\").casefold() != parent_pin["final"].casefold():
                raise self.fail("custody", "namespace")
        dos = self.final_path(handle, False)
        if dos[4:].casefold().rstrip("\\") != path.casefold().rstrip("\\"):
            raise self.fail("custody", "namespace")
        if expected is not None and identity != expected:
            raise self.fail("custody", "changed")
        pin = {"path": path, "directory": directory, "policy": policy,
               "identity": identity, "final": final, "handle": resource,
               "size": size}
        self.pins.append(pin)
        if not temporary:
            self.pin_paths[key] = pin
        return pin

    def walk(self, path, anchor=False):
        if not dos_path(path):
            raise self.fail("custody", "namespace")
        components = path[3:].split("\\")
        current = path[:3]
        previous = self.open_pin(current, True, "host")
        for index, component in enumerate(components):
            current = os.path.join(current, component)
            pin = self.open_pin(current, True, "anchor" if anchor and index == len(components) - 1 else "host")
            if os.path.dirname(pin["final"]).rstrip("\\").casefold() != previous["final"].casefold():
                raise self.fail("custody", "namespace")
            previous = pin
        return previous

    def held_bytes(self, pin, cap):
        c = self.c
        if not 0 <= pin["size"] <= cap:
            raise self.fail("preflight", "bounds")
        handle = pin["handle"][0]
        self.checked(self.SetFilePointerEx(handle, 0, None, 0))
        chunks, total = [], 0
        while total <= cap:
            buffer, count = c.create_string_buffer(65536), self.DWORD()
            self.checked(self.ReadFile(handle, buffer, min(len(buffer), cap + 1 - total), c.byref(count), None))
            if count.value == 0:
                break
            chunks.append(buffer.raw[:count.value])
            total += count.value
        if total != pin["size"] or total > cap:
            raise self.fail("preflight", "bounds")
        result = b"".join(chunks)
        actual = hashlib.sha256(result).hexdigest()
        if "sha256" in pin and pin["sha256"] != actual:
            raise self.fail("custody", "changed")
        pin["sha256"] = actual
        return result

    def recheck(self):
        # Temporary reopens are owned, inspected, compared, then closed once.
        for pin in tuple(self.pins):
            if pin["handle"][2]:
                continue
            actual, size = self.info(pin["handle"][0], pin["directory"], pin["policy"] == "host")
            if actual != pin["identity"] or (not pin["directory"] and size != pin["size"]):
                raise self.fail("custody", "changed")
            if pin["policy"] != "host":
                self.inspect_security(pin["handle"][0], pin["directory"], pin["policy"] == "anchor")
            if "sha256" in pin:
                self.held_bytes(pin, pin["size"])
            temporary = self.open_pin(pin["path"], pin["directory"], pin["policy"], pin["identity"], temporary=True)
            try:
                if temporary["final"].casefold() != pin["final"].casefold():
                    raise self.fail("custody", "changed")
            finally:
                self.release(temporary["handle"])
                self.pins.remove(temporary)

    def raw_identity(self, handle):
        value = self.FILEID()
        self.checked(self.GetFileInformationByHandleEx(handle, 18, self.c.byref(value), self.c.sizeof(value)))
        if not value.volume or not any(value.id):
            raise self.fail("custody", "identity", "unknown")
        return value.volume, bytes(value.id)

    def remember_created(self, path, directory, handle=None):
        temporary = None
        if handle is None:
            value = self.CreateFileW(path, 0x120089, 1, None, 3,
                                     0x200000 | (0x2000000 if directory else 0), None)
            if value == self.invalid or not value:
                self.checked(False)
            temporary = self.own(value)
            handle = value
        try:
            identity = self.raw_identity(handle)
            record = {"path": path, "directory": directory, "identity": identity}
            self.created.append(record)
            return record
        finally:
            if temporary:
                self.release(temporary)

    def create_directory(self, path, administrators=False, broad=False, protected=True):
        if not dos_path(path):
            raise self.fail("provision", "bounds")
        attributes = self.security_attributes(True, administrators, broad, protected)
        self.checked(self.CreateDirectoryW(path, self.c.byref(attributes)), "provision")
        # From this point the path is exclusively ours even if opening its ID
        # subsequently fails. Unknown identity means retain, never guessed delete.
        self.created.append({"path": path, "directory": True, "identity": None})
        record = self.remember_created(path, True)
        self.created.pop(-2)
        return record

    def create_file(self, path, data, administrators=False, broad=False):
        c = self.c
        if not dos_path(path):
            raise self.fail("provision", "bounds")
        if len(data) + self.stage_bytes > 256 * MIB:
            raise self.fail("provision", "bounds")
        self.stage_bytes += len(data)
        attributes = self.security_attributes(False, administrators, broad)
        value = self.CreateFileW(path, 0xC0000000, 0, c.byref(attributes), 1, 0x200000, None)
        if value == self.invalid or not value:
            self.checked(False, "provision")
        owned = self.own(value)
        self.created.append({"path": path, "directory": False, "identity": None})
        try:
            record = self.remember_created(path, False, value)
            self.created.pop(-2)
            for offset in range(0, len(data), 65536):
                chunk = data[offset:offset + 65536]
                buffer, count = c.create_string_buffer(chunk), self.DWORD()
                self.checked(self.WriteFile(value, buffer, len(chunk), c.byref(count), None), "provision")
                if count.value != len(chunk):
                    raise self.fail("provision", "native", "unknown")
            return record
        finally:
            self.release(owned)

    def system_path(self, function):
        buffer = self.c.create_unicode_buffer(4097)
        length = function(buffer, len(buffer))
        if not 0 < length < len(buffer) or not dos_path(buffer.value):
            raise self.fail("prerequisite", "namespace", "unknown")
        return buffer.value

    def ntfs(self, path):
        c = self.c
        serial, maximum, flags = self.DWORD(), self.DWORD(), self.DWORD()
        filesystem = c.create_unicode_buffer(32)
        self.checked(self.GetVolumeInformationW(path[:3], None, 0, c.byref(serial), c.byref(maximum),
                                                c.byref(flags), filesystem, len(filesystem)), "prerequisite")
        if filesystem.value != "NTFS" or not flags.value & 8:
            raise self.fail("prerequisite", "filesystem", "unknown")

    def inventory(self, root, expected):
        found = set()
        with os.scandir(root) as entries:
            for entry in entries:
                if len(found) == 16 or entry.name in found:
                    raise self.fail("preflight", "inventory")
                found.add(entry.name)
        if found != set(expected):
            raise self.fail("preflight", "inventory")

    def check_source(self, selected):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.walk(root, True)
        total = 0
        for relative in SOURCE_FILES:
            path = os.path.join(root, *relative.split("/"))
            self.walk(os.path.dirname(path), True)
            pin = self.open_pin(path, policy="anchor")
            data = self.held_bytes(pin, MIB)
            total += len(data)
            if total > 6 * MIB or hashlib.sha256(data).hexdigest() != selected["sourceSha256"][relative]:
                raise self.fail("preflight", "source")
            if relative.endswith("-child.mjs"):
                self.child_source = data

    def selected_input(self, root, relative, expected, cap):
        path = os.path.join(root, *relative.split("/"))
        self.walk(os.path.dirname(path), True)
        pin = self.open_pin(path, policy="anchor")
        data = self.held_bytes(pin, cap)
        if hashlib.sha256(data).hexdigest() != expected:
            raise self.fail("preflight", "hash")
        return data

    def authenticate_inputs(self, selected):
        root = selected["inputRoot"]
        self.walk(root, True)
        receipt = self.selected_input(root, "control/build-receipt.json", selected["buildReceiptSha256"], MIB)
        try:
            build = json.loads(receipt.decode("utf-8"), object_pairs_hook=unique_object)
            validate_build_receipt(build, selected)
        except Refusal:
            raise
        except Exception:
            raise self.fail("preflight", "receipt") from None
        self.build, self.receipt_bytes = build, receipt
        # Builder/tool/SDK authority is an independently accepted external
        # prerequisite. The frozen complete receipt binds those exact inputs;
        # this loader does not invent qualification of their installation ACLs
        # or execute a candidate compiler/inspector to establish its own trust.
        toolchain = build["toolchain"]
        records = [toolchain[key] for key in ("compiler", "linker", "inspector")]
        records += toolchain["sdkInputs"] + toolchain["headerInputs"] + toolchain["libraryInputs"]
        if len(records) > 256:
            raise self.fail("preflight", "bounds")
        self.selected_input(root, "runtime/node-v24.22.1-win-x64.zip", ARCHIVE_SHA256, 128 * MIB)
        self.selected_input(root, "build-input/node-v24.22.1-headers.tar.xz", HEADERS_SHA256, 128 * MIB)
        self.selected_input(root, "build-input/win-x64/node.lib", NODE_LIB_SHA256, 128 * MIB)
        self.node_bytes = self.selected_input(root, "runtime/node.exe", NODE_SHA256, 128 * MIB)
        self.artifacts = {}
        for name, record in build["artifacts"].items():
            data = self.selected_input(root, "output/" + record["file"], record["sha256"], 4 * MIB)
            if len(data) != record["bytes"] or inspect_pe(data) != {
                    key: record[key] for key in ("machine", "pe", "imports", "exports")}:
                raise self.fail("preflight", "artifact")
            self.artifacts[name] = data

    def create_stage(self, selected, case):
        self.ntfs(selected["stageParent"])
        self.walk(selected["stageParent"], True)
        administrators = case == "positive-admin"
        root = os.path.join(selected["stageParent"], "factory-loader-" + os.urandom(16).hex())
        self.stage_root, self.code, self.cwd = root, os.path.join(root, "code"), os.path.join(root, "cwd")
        self.controls = os.path.join(root, "controls")
        self.create_directory(root, administrators, case == "broad-root", case != "unprotected-root")
        root_record = self.created[-1]
        self.open_pin(root, True, expected=root_record["identity"])
        directory_ids = {}
        for path in (self.code, self.cwd, self.controls):
            record = self.create_directory(path, administrators)
            directory_ids[path] = record["identity"]
        self.image_paths = {"node": os.path.join(self.code, "node.exe"),
                            "addon": os.path.join(self.code, "windows-storage-loader-canary.node")}
        artifact = self.artifacts["apiMismatch" if case == "api-mismatch" else "positive"]
        entries = {"node.exe": self.node_bytes,
                   "windows-storage-loader-child.mjs": self.child_source,
                   "build-receipt.json": self.receipt_bytes,
                   "windows-storage-loader-canary.node": artifact,
                   "selection.json": self.selection_bytes}
        self.stage_expected = set(entries) - ({"windows-storage-loader-canary.node"}
                                           if case in ("missing-image", "require-failure") else set())
        if sum(map(len, entries.values())) > 256 * MIB:
            raise self.fail("provision", "bounds")
        expected_ids = {}
        for name, data in entries.items():
            if case in ("missing-image", "require-failure") and name.endswith(".node"):
                continue
            if case == "wrong-digest" and name.endswith(".node"):
                data += b"fixture-change"
            if case == "wrong-arch" and name.endswith(".node"):
                data = self.artifacts["wrongArch"]
            if case == "malformed-pe" and name.endswith(".node"):
                data = b"not-a-PE-image"
            path = os.path.join(self.code, name)
            record = self.create_file(path, data, administrators, case == "broad-child" and name.endswith(".node"))
            expected_ids[name] = record["identity"]
        addon = self.image_paths["addon"]
        self.create_file(os.path.join(self.controls, "replace-addon.bin"), artifact, administrators)
        self.create_file(os.path.join(self.controls, "replace-node.bin"), self.node_bytes, administrators)
        if case == "changed-selection":
            path = os.path.join(self.code, "selection.json")
            self.checked(self.DeleteFileW(path), "control")
            self.create_file(path, self.selection_bytes + b" ", administrators)
        if case == "changed-image":
            self.checked(self.DeleteFileW(addon), "control")
            self.create_file(addon, artifact, administrators)
        if case == "oversized-artifact":
            self.create_file(os.path.join(self.code, "oversized.node"), b"x" * (4 * MIB + 1), administrators)
            oversized = self.open_pin(os.path.join(self.code, "oversized.node"))
            self.held_bytes(oversized, 4 * MIB)
        if case in ("extra-dll", "conflicting-import", "local-redirection", "manifest-redirection"):
            name = {"extra-dll": "extra.dll", "local-redirection": "node.exe.local",
                    "manifest-redirection": "node.exe.manifest"}.get(case)
            if case == "conflicting-import":
                name = next((item["library"] for item in self.build["artifacts"]["positive"]["imports"]
                             if item["library"] != "node.exe"), None)
                if name is None:
                    raise self.fail("prerequisite", "control", "unknown")
            self.create_file(os.path.join(self.code, name), b"fixture-only-never-executed", administrators)
        if case == "changed-parent":
            moved = os.path.join(root, "changed-code")
            self.checked(self.MoveFileExW(self.code, moved, 0), "control")
            self.create_directory(self.code, administrators)
            for name, data in entries.items():
                self.create_file(os.path.join(self.code, name), data, administrators)
        if case == "reparse-parent":
            moved = os.path.join(root, "actual-code")
            self.checked(self.MoveFileExW(self.code, moved, 0), "control")
            if not self.CreateSymbolicLinkW(self.code, moved, 3):
                raise self.fail("prerequisite", "control", "unknown")
        if case in ("reparse-image", "hardlink", "nonfile"):
            if case == "hardlink":
                link = os.path.join(root, "hardlink-control.node")
                self.checked(self.CreateHardLinkW(link, addon, None), "control")
                self.remember_created(link, False)
            else:
                self.checked(self.DeleteFileW(addon), "control")
                # The original is gone. Its recorded identity is retained; a
                # replacement is deliberately not deletion-authorized by it.
                if case == "reparse-image":
                    source = os.path.join(selected["inputRoot"], "output", "windows-storage-loader-canary.node")
                    if not self.CreateSymbolicLinkW(addon, source, 2):
                        raise self.fail("prerequisite", "control", "unknown")
                else:
                    self.checked(self.CreateDirectoryW(addon, self.c.byref(self.security_attributes(True, administrators))), "control")
        if case == "denied-sharing":
            value = self.CreateFileW(addon, 0x120089, 0, None, 3, 0x200000, None)
            if value == self.invalid or not value:
                self.checked(False, "control")
            self.own(value)  # Deliberately retained conflicting owned open.
        if case == "denied-metadata":
            self.change_acl(addon, empty=True)
        for path in (self.code, self.cwd, self.controls):
            self.open_pin(path, True, expected=directory_ids[path])
        self.inventory(self.code, entries if case not in ("missing-image", "require-failure")
                       else [name for name in entries if not name.endswith(".node")])
        self.inventory(self.cwd, ())
        for name in entries:
            if case == "require-failure" and name.endswith(".node"):
                continue
            pin = self.open_pin(os.path.join(self.code, name), expected=expected_ids.get(name))
            cap = 128 * MIB if name == "node.exe" else 4 * MIB if name.endswith(".node") else MIB
            data = self.held_bytes(pin, cap)
            if name.endswith(".node") and case in ("wrong-arch", "malformed-pe"):
                actual = inspect_pe(data)
                if actual["machine"] != "amd64" or actual["pe"] != "pe32+":
                    raise self.fail("preflight", "artifact")
            expected = NODE_SHA256 if name == "node.exe" else hashlib.sha256(entries[name]).hexdigest()
            if name.endswith(".node"):
                expected = self.build["artifacts"]["apiMismatch" if case == "api-mismatch" else "positive"]["sha256"]
            if hashlib.sha256(data).hexdigest() != expected:
                raise self.fail("preflight", "hash")
            if name.endswith(".node") and case not in ("api-mismatch",):
                actual = inspect_pe(data)
                if actual["machine"] != "amd64" or actual["pe"] != "pe32+":
                    raise self.fail("preflight", "artifact")
        self.inventory(self.controls, ("replace-addon.bin", "replace-node.bin"))
        self.inventory(root, ("code", "cwd", "controls"))
        self.recheck()

    def staged_inventory(self):
        self.inventory(self.code, self.stage_expected)
        self.inventory(self.cwd, ())
        self.inventory(self.controls, ("replace-addon.bin", "replace-node.bin"))
        self.inventory(self.stage_root, ("code", "cwd", "controls"))

    def change_acl(self, path, empty=False):
        c = self.c
        value = self.CreateFileW(path, 0x40080, 7, None, 3, 0x200000, None)  # WRITE_DAC + read attributes, no data write.
        if value == self.invalid or not value:
            self.checked(False, "control")
        owned = self.own(value)
        try:
            expected = next((record["identity"] for record in self.created if record["path"] == path), None)
            if expected is None or self.raw_identity(value) != expected:
                raise self.fail("control", "changed")
            if empty:
                acl = c.create_string_buffer(8)
                self.checked(self.InitializeAcl(acl, len(acl), 2), "control")
            else:
                attributes = self.security_attributes(broad=True)
                descriptor = c.cast(attributes.descriptor, c.POINTER(self.SD)).contents
                acl = descriptor.dacl
            status = self.SetSecurityInfo(value, 1, 0x80000004, None, None, acl, None)
            if status != 0:
                raise self.fail("control", "native", "unknown")
        finally:
            self.release(owned)

    def sharing_controls(self):
        for role, path in list(self.image_paths.items()) + [("parent", self.code)]:
            flags = 0x200000 | (0x2000000 if role == "parent" else 0)
            for access in (0x40000000, 0x10000):  # Real write and delete access attempts.
                value = self.CreateFileW(path, access, 7, None, 3, flags, None)
                if value != self.invalid and value:
                    self.release(self.own(value))
                    raise self.fail("control", "sharing")
                if self.c.get_last_error() != 32:
                    raise self.fail("control", "control", "unknown")
            if self.MoveFileExW(path, path + ".blocked", 0):
                raise self.fail("control", "sharing")
            if self.c.get_last_error() != 32:
                raise self.fail("control", "control", "unknown")
            if role != "parent":
                if self.DeleteFileW(path):
                    raise self.fail("control", "sharing")
                if self.c.get_last_error() != 32:
                    raise self.fail("control", "control", "unknown")
                replacement = os.path.join(self.controls, "replace-" + role + ".bin")
                if self.MoveFileExW(replacement, path, 1):
                    raise self.fail("control", "sharing")
                if self.c.get_last_error() != 32:
                    raise self.fail("control", "control", "unknown")
            # Parent replacement first requires renaming/removing the admitted
            # directory. The actual denied rename/delete-open above stops that
            # finite actor before it can install a replacement.

    def modules(self, require_canary=False):
        c = self.c
        observations = []
        system_pin = self.open_pin(self.system_directory, True, "host")
        for _ in range(2):  # Two fixed observations, never a stabilization retry.
            modules, needed = (self.HANDLE * 256)(), self.DWORD()
            self.checked(self.K32EnumProcessModulesEx(self.process[0], modules, c.sizeof(modules), c.byref(needed), 3), "modules")
            if needed.value == 0 or needed.value > c.sizeof(modules) or needed.value % c.sizeof(self.HANDLE):
                raise self.fail("modules", "modules", "unknown")
            snapshot, node_seen, addon_seen = [], False, False
            for index in range(needed.value // c.sizeof(self.HANDLE)):
                path_buffer = c.create_unicode_buffer(4097)
                length = self.K32GetModuleFileNameExW(self.process[0], modules[index], path_buffer, len(path_buffer))
                if not 0 < length < len(path_buffer) - 1 or not dos_path(path_buffer.value):
                    raise self.fail("modules", "modules", "unknown")
                path = path_buffer.value
                pin = self.open_pin(path, policy="host")
                if pin["identity"] == self.pin_paths[self.image_paths["node"].casefold()]["identity"]:
                    node_seen = True
                elif self.image_paths["addon"].casefold() in self.pin_paths and pin["identity"] == self.pin_paths[self.image_paths["addon"].casefold()]["identity"]:
                    addon_seen = True
                else:
                    parent = self.walk(os.path.dirname(path))
                    if parent["identity"] != system_pin["identity"] or os.path.dirname(pin["final"]).rstrip("\\").casefold() != system_pin["final"].casefold():
                        raise self.fail("modules", "modules")
                snapshot.append((modules[index], pin["identity"]))
            if not node_seen or (require_canary and not addon_seen):
                raise self.fail("modules", "modules", "unknown")
            observations.append(tuple(sorted(snapshot)))
        if observations[0] != observations[1]:
            raise self.fail("modules", "modules", "unknown")

    def pipe(self, child_reads):
        c = self.c
        read, write = self.HANDLE(), self.HANDLE()
        attributes = self.security_attributes(process=True)
        if not self.CreatePipe(c.byref(read), c.byref(write), c.byref(attributes), 4096):
            # Failed API output parameters are not owned initialized handles.
            self.checked(False, "process")
        read_owned, write_owned = self.own(read.value), self.own(write.value)
        child, parent = (read_owned, write_owned) if child_reads else (write_owned, read_owned)
        self.child_pipe_ends.append(child)
        self.checked(self.SetHandleInformation(child[0], 1, 1), "process")
        self.checked(self.SetHandleInformation(parent[0], 1, 0), "process")
        return child, parent

    def start(self, case):
        c = self.c
        stdin_child, self.stdin_parent = self.pipe(True)
        stdout_child, stdout_parent = self.pipe(False)
        stderr_child, stderr_parent = self.pipe(False)
        self.output = [stdout_parent, stderr_parent]
        self.eof = [False, False]
        size = c.c_size_t()
        okay = self.InitializeProcThreadAttributeList(None, 1, 0, c.byref(size))
        if okay or c.get_last_error() != 122 or not 1 <= size.value <= 65536:
            raise self.fail("process", "native", "unknown")
        buffer = c.create_string_buffer(size.value)
        self.buffers.append(buffer)
        self.checked(self.InitializeProcThreadAttributeList(buffer, 1, 0, c.byref(size)), "process")
        attributes = self.own(c.addressof(buffer), "attributes")
        handles = (self.HANDLE * 3)(stdin_child[0], stdout_child[0], stderr_child[0])
        self.buffers.append(handles)
        self.checked(self.UpdateProcThreadAttribute(buffer, 0, 0x20002, handles, c.sizeof(handles), None, None), "process")
        startup, info = self.STARTUPEX(), self.PROCESS()
        startup.startup.cb = c.sizeof(startup)
        startup.startup.flags = 0x100
        startup.startup.stdin, startup.startup.stdout, startup.startup.stderr = handles
        startup.attributes = c.addressof(buffer)
        child_case = case if case in ("positive-user", "positive-admin", "throw-before", "require-failure", "throw-after", "nonzero",
                                      "stdout-overflow", "stderr-overflow", "timeout", "retained-writer", "api-mismatch",
                                      "forged-success", "unknown-result", "extra-result") else "positive-user"
        if case == "synthetic-overflow-close":
            child_case = "stdout-overflow"
        application = self.image_paths["node"]
        script = os.path.join(self.code, "windows-storage-loader-child.mjs")
        # Accepted DOS paths contain no quote; fixed arguments never end in a
        # backslash. No shell or caller-provided command fragment is involved.
        command = c.create_unicode_buffer('"' + application + '" "' + script + '" ' + child_case)
        environment = {"SystemRoot": self.windows_directory, "WINDIR": self.windows_directory,
                       "PATH": self.code + ";" + self.system_directory,
                       "TEMP": self.cwd, "TMP": self.cwd}
        block = c.create_unicode_buffer("\0".join(key + "=" + environment[key] for key in sorted(environment, key=str.casefold)) + "\0\0")
        process_security = self.security_attributes(process=True)
        self.recheck()
        self.staged_inventory()
        if time.monotonic() >= self.work_deadline:
            raise self.fail("process", "deadline", "unknown")
        created = self.CreateProcessW(application, command, c.byref(process_security), c.byref(process_security),
                                      True, 0x80400, block, self.cwd, c.byref(startup), c.byref(info))
        if not created:
            self.checked(False, "process")
        self.process = self.own(info.process)
        self.exited = False
        self.thread_resource = self.own(info.thread)
        self.release(self.thread_resource)
        self.release(attributes)
        for resource in (stdin_child, stderr_child):
            self.release(resource)
        self.retained_writer = stdout_child if case == "retained-writer" else None
        if not self.retained_writer:
            self.release(stdout_child)
        self.buffers.extend([command, block, startup, info])
        if self.close_failed:
            raise self.fail("close", "close", "unknown")

    def send(self, command):
        data = ('{"command":"' + command + '"}\n').encode("ascii")
        buffer, written = self.c.create_string_buffer(data), self.DWORD()
        self.checked(self.WriteFile(self.stdin_parent[0], buffer, len(data), self.c.byref(written), None), "protocol")
        if written.value != len(data):
            raise self.fail("protocol", "protocol", "unknown")

    def exited_now(self):
        if self.process is None:
            return True
        if self.exited:
            return True
        if self.wait_failed:
            return False
        status = self.WaitForSingleObject(self.process[0], 0)
        if status == 0:
            self.exited = True  # Actual process HANDLE signaled, independent of exit-code query.
            code = self.DWORD()
            self.checked(self.GetExitCodeProcess(self.process[0], self.c.byref(code)), "process")
            self.exit_code = code.value
        elif status != 258:
            self.wait_failed = True
            raise self.fail("process", "native", "unknown")
        return self.exited

    def drain_once(self, stream, captured, discard_only=False):
        if self.eof[stream] or self.pipe_failed[stream]:
            return b""
        c = self.c
        available = self.DWORD()
        if not self.PeekNamedPipe(self.output[stream][0], None, 0, None, c.byref(available), None):
            if c.get_last_error() == 109:
                self.eof[stream] = True
                return b""
            self.pipe_failed[stream] = True
            raise self.fail("process", "eof", "unknown")
        if not available.value:
            return b""  # Zero available is NOT EOF.
        remaining = 8192 - captured[stream]
        if available.value > remaining and not discard_only:
            self.fail("protocol", "bounds")
        discarding = discard_only or remaining == 0
        if discarding:
            # Root-approved prototype refinement: at most another 8192 bytes,
            # discarded only after irreversible failure, never parsed/exported.
            if self.first is None:
                raise self.fail("protocol", "bounds")
            remaining = 8192 - self.discarded[stream]
        if remaining <= 0:
            return b""
        length = min(available.value, 1024, remaining)
        buffer, count = c.create_string_buffer(length), self.DWORD()
        read = self.ReadFile(self.output[stream][0], buffer, length, c.byref(count), None)
        if not read:
            self.pipe_failed[stream] = True
            self.checked(False, "process")
        if not 0 <= count.value <= length:
            raise self.fail("process", "eof", "unknown")
        if count.value == 0:
            self.eof[stream] = True
            return b""
        if discarding:
            self.discarded[stream] += count.value
            return b""
        captured[stream] += count.value
        return buffer.raw[:count.value]

    def run_child(self, case):
        self.start(case)
        captured, pending, phase = self.captured, b"", "ready"
        self.child_result = None
        try:
            while time.monotonic() < self.work_deadline:
                for stream in (0, 1):
                    data = self.drain_once(stream, captured)
                    if stream == 0 and phase != "overflow":
                        pending += data
                if self.first and phase != "exit":
                    raise Refusal(self.first.phase, self.first.reason, self.first.state)
                if len(pending) > 1024:
                    raise self.fail("protocol", "bounds")
                while b"\n" in pending:
                    line, pending = pending.split(b"\n", 1)
                    if phase == "ready":
                        if line != b'{"scope":"windows-storage-loader-child","event":"ready"}':
                            raise self.fail("protocol", "protocol")
                        self.recheck()
                        self.staged_inventory()
                        self.modules()
                        if case in ("positive-user", "positive-admin"):
                            self.sharing_controls()
                        if case == "acl-change":
                            self.change_acl(self.image_paths["addon"])
                            self.recheck()
                        self.send("load")
                        # This one fixed negative transport case must reach the
                        # actual 8192 stream cap rather than the earlier record
                        # cap. Its bytes are opaque, never parsed or successful.
                        phase = "overflow" if case in ("stdout-overflow", "synthetic-overflow-close") else "result"
                    elif phase == "result":
                        try:
                            record = json.loads(line.decode("ascii"), object_pairs_hook=unique_object)
                        except Exception:
                            raise self.fail("protocol", "protocol") from None
                        if not isinstance(record, dict) or set(record) != {"scope", "event", "state", "reason"}:
                            raise self.fail("protocol", "protocol")
                        if (record["scope"] != "windows-storage-loader-child" or record["event"] != "result"
                                or (record["state"], record["reason"]) not in (("called", "none"), ("failed", "loader"),
                                  ("failed", "call"), ("failed", "before"), ("failed", "after"), ("failed", "bounds"))):
                            raise self.fail("protocol", "protocol")
                        self.child_result = record
                        self.recheck()
                        self.staged_inventory()
                        self.modules(record["state"] == "called" or record["reason"] == "after")
                        if case in ("positive-user", "positive-admin"):
                            self.sharing_controls()
                        self.send("release")
                        self.release(self.stdin_parent)
                        phase = "exit"
                        if record["state"] != "called":
                            self.fail("load", record["reason"])
                    else:
                        raise self.fail("protocol", "protocol")
                if self.exited_now():
                    if self.retained_writer and not self.eof[0]:
                        # An exact exited process with a deliberately held owned
                        # writer is a real finite non-EOF observation. Latch it,
                        # release this known writer once, then observe actual EOF.
                        self.fail("process", "eof", "unknown")
                        self.release(self.retained_writer)
                        self.retained_writer = None
                    if all(self.eof):
                        break
                time.sleep(0.005)
            if not self.exited or not all(self.eof):
                raise self.fail("process", "deadline", "unknown")
            if pending or phase != "exit" or captured[1]:
                raise self.fail("protocol", "protocol")
            if case == "nonzero" and self.exit_code != 23:
                raise self.fail("control", "control", "unknown")
            if self.exit_code != 0:
                raise self.fail("process", "exit")
            if self.child_result["state"] != "called":
                raise self.fail("load", self.child_result["reason"])
        except Refusal as failure:
            self.fail(failure.phase, failure.reason, failure.state)
        except Exception:
            self.fail("protocol", "protocol", "unknown")
        finally:
            self.close_child(captured)

    def close_child(self, captured):
        # No unowned PID lookup or child-tree inference. Termination is a request;
        # WaitForSingleObject and both independent pipe EOF remain necessary.
        if self.process is None:
            return
        if not self.exited and not self.termination_attempted:
            self.termination_attempted = True
            try:
                terminated = self.TerminateProcess(self.process[0], 1)
            except Exception:
                terminated = False
            if not terminated:
                self.fail("process", "native", "unknown")
        if self.stdin_parent:
            self.release(self.stdin_parent)
        for resource in self.child_pipe_ends:
            self.release(resource)
        if self.thread_resource:
            self.release(self.thread_resource)
        for resource in self.resources:
            if resource[1] == "attributes":
                self.release(resource)
        if self.retained_writer:
            self.release(self.retained_writer)
            self.retained_writer = None
        while time.monotonic() < self.deadline:
            try:
                self.exited_now()
            except Exception:
                self.fail("process", "native", "unknown")
            for stream in (0, 1):
                try:
                    self.drain_once(stream, captured, discard_only=self.first is not None)
                except Exception:
                    self.fail("process", "eof", "unknown")
            if self.exited and all(self.eof):
                return
            time.sleep(0.005)
        self.fail("process", "eof" if self.exited else "deadline", "unknown")

    def inert_refusal(self, receipt):
        # Eligibility has ended. Returning/unwinding would drop custody while
        # exact exit/required EOF remains unknown. Keep the complete context
        # inert until the fixed outer transport terminates this controller.
        # OS teardown is UNKNOWN custody/closure, not an owned-close result.
        try:
            sys.stdout.write(json.dumps(receipt, separators=(",", ":")) + "\n")
            sys.stdout.flush()
        except BaseException:
            pass  # Broken outer transport cannot voluntarily drop custody.
        while True:
            try:
                time.sleep(1)
            except BaseException:
                pass

    def close_all(self):
        if not self.exited or not all(self.eof):
            raise RuntimeError("pins must remain owned")
        for resource in reversed(self.resources):
            self.release(resource)
        self.closed = not self.close_failed
        self.buffers.clear()

    def cleanup(self):
        if not self.closed or not self.exited or not all(self.eof):
            return False
        # Inspect every recorded object before deleting any, using only no-follow
        # opens. A missing/replaced/unknown object preserves the complete stage.
        inspected = []
        try:
            for record in self.created:
                if record["identity"] is None:
                    return False
                if not (record["path"] == self.stage_root or record["path"].startswith(self.stage_root + "\\")):
                    return False
                value = self.CreateFileW(record["path"], 0x120089, 7, None, 3,
                                         0x200000 | (0x2000000 if record["directory"] else 0), None)
                if not value or value == self.invalid:
                    return False
                resource = self.own(value)
                inspected.append((record, resource))
                identity, _ = self.info(value, record["directory"])
                if identity != record["identity"]:
                    return False
            for record, resource in reversed(inspected):
                function = self.RemoveDirectoryW if record["directory"] else self.DeleteFileW
                if not function(record["path"]):
                    return False
                self.release(resource)
            return not self.close_failed
        except Exception:
            return False
        finally:
            for _, resource in reversed(inspected):
                self.release(resource)

    def after_release_controls(self):
        path = self.image_paths["addon"]
        renamed = path + ".released"
        self.checked(self.MoveFileExW(path, renamed, 0), "cleanup")
        record = next(record for record in self.created if record["path"] == path)
        record["path"] = renamed
        self.checked(self.DeleteFileW(renamed), "cleanup")
        self.created.remove(record)


def native_receipt(selected, selected_sha, case, controller):
    failure = controller.first
    variant = "apiMismatch" if case == "api-mismatch" else "wrongArch" if case == "wrong-arch" else "positive"
    artifact_sha = controller.build["artifacts"][variant]["sha256"] if hasattr(controller, "build") else selected["artifactSha256"]
    return {"scope": "windows-storage-loader-fixture", "case": case,
            "state": failure.state if failure else "pass",
            "phase": failure.phase if failure else "complete",
            "reason": failure.reason if failure else "none",
            "selectionSha256": selected_sha, "sourceCommit": selected["sourceCommit"],
            "nodeSha256": NODE_SHA256, "artifactSha256": artifact_sha,
            "buildReceiptSha256": selected["buildReceiptSha256"],
            "processStarted": controller.process is not None,
            "processExit": controller.process is not None and controller.exited,
            "stdoutEOF": controller.process is not None and controller.eof[0],
            "stderrEOF": controller.process is not None and controller.eof[1],
            "ownedClose": controller.closed,
            "capture": controller.captured, "discard": controller.discarded,
            "stage": ("retained" if controller.retained else "removed") if controller.created else "not-created"}


def execute_native(selected, selected_sha, selection_path, case, entered):
    controller = Windows()
    controller.deadline, controller.work_deadline = entered + 30, entered + 25
    try:
        controller.identity()
        controller.system_directory = controller.system_path(controller.GetSystemDirectoryW)
        controller.windows_directory = controller.system_path(controller.GetWindowsDirectoryW)
        controller.walk(controller.system_directory)
        version = sys.getwindowsversion()
        if selected["windowsBuild"] != "%d.%d.%d" % (version.major, version.minor, version.build):
            raise controller.fail("prerequisite", "platform", "unknown")
        if not dos_path(selection_path):
            raise controller.fail("selection", "selection")
        folded = selection_path.casefold()
        if folded.startswith(selected["inputRoot"].casefold() + "\\output\\") or folded.startswith(selected["stageParent"].casefold() + "\\"):
            raise controller.fail("selection", "selection")
        controller.walk(os.path.dirname(selection_path), True)
        selection_pin = controller.open_pin(selection_path, policy="anchor")
        controller.selection_bytes = controller.held_bytes(selection_pin, MIB)
        if hashlib.sha256(controller.selection_bytes).hexdigest() != selected_sha:
            raise controller.fail("selection", "selection")
        controller.walk(os.path.dirname(sys.executable), True)
        python_pin = controller.open_pin(sys.executable, policy="anchor")
        if hashlib.sha256(controller.held_bytes(python_pin, 128 * MIB)).hexdigest() != selected["pythonSha256"]:
            raise controller.fail("prerequisite", "runtime", "unknown")
        controller.check_source(selected)
        controller.authenticate_inputs(selected)
        if time.monotonic() >= controller.work_deadline:
            raise controller.fail("preflight", "deadline", "unknown")
        controller.create_stage(selected, case)
        controller.run_child(case)
        if controller.exited and all(controller.eof) and time.monotonic() < controller.deadline:
            controller.recheck()
            controller.staged_inventory()
    except Refusal as failure:
        controller.fail(failure.phase, failure.reason, failure.state)
    except Exception:
        controller.fail("custody", "native", "unknown")
    # Partial process creation can fail after the exact process was acquired.
    # It still owns the same termination/wait/drain obligations.
    if controller.process is not None and (not controller.exited or not all(controller.eof)):
        controller.close_child(controller.captured)
    if controller.process is None:
        # No process was created. These booleans mean no live-child obligation
        # internally; the exported receipt explicitly says not started/no EOF.
        controller.exited, controller.eof = True, [True, True]
    if not controller.exited or not all(controller.eof):
        controller.inert_refusal(native_receipt(selected, selected_sha, case, controller))
    if case in ("synthetic-close", "synthetic-overflow-close"):
        controller.fail("close", "close", "unknown")
        controller.close_failed = True  # Synthetic only; real releases still run.
    controller.close_all()
    if time.monotonic() >= controller.deadline:
        controller.fail("process", "deadline", "unknown")
    try:
        if case == "replaced-owned-file" and controller.first is None:
            path = os.path.join(controller.code, "build-receipt.json")
            controller.checked(controller.DeleteFileW(path), "control")
            controller.create_file(path, b"known-replacement-preserve")
            controller.created.pop()  # Not admitted for cleanup by the old ID.
            controller.fail("cleanup", "changed")
        if controller.first is None and case in ("positive-user", "positive-admin"):
            controller.after_release_controls()
        if time.monotonic() >= controller.deadline:
            controller.fail("process", "deadline", "unknown")
        if (controller.closed and (controller.first is None or controller.first.state != "unknown")
                and case not in ("retained-writer", "synthetic-close", "synthetic-overflow-close", "replaced-owned-file")):
            controller.retained = not controller.cleanup()
        if controller.first is None and controller.retained:
            controller.fail("cleanup", "changed", "unknown")
    except Refusal as failure:
        controller.fail(failure.phase, failure.reason, failure.state)
    except Exception:
        controller.fail("cleanup", "native", "unknown")
    if controller.close_failed:
        controller.closed = False
    if controller.first is None and time.monotonic() >= controller.deadline:
        # All facts/owned cleanup are already known here, but eligibility ended.
        # This is a policy refusal, never a late conversion to successful proof.
        controller.fail("process", "deadline")
    receipt = native_receipt(selected, selected_sha, case, controller)
    if len(json.dumps(receipt, separators=(",", ":")).encode("ascii")) + 1 > 1024:
        raise Refusal("protocol", "bounds", "unknown")
    return receipt


def fields(value, names):
    if not isinstance(value, dict) or set(value) != set(names):
        raise Refusal("preflight", "receipt")


def validate_build_receipt(build, selected):
    fields(build, ("schema", "sourceSha256", "nodeArchiveSha256", "headersArchiveSha256",
                   "nodeImportLibrarySha256", "toolchain", "artifacts"))
    if (type(build["schema"]) is not int or build["schema"] != 1
            or build["sourceSha256"] != selected["sourceSha256"][SOURCE_FILES[1]]
            or build["nodeArchiveSha256"] != ARCHIVE_SHA256
            or build["headersArchiveSha256"] != HEADERS_SHA256
            or build["nodeImportLibrarySha256"] != NODE_LIB_SHA256):
        raise Refusal("preflight", "receipt")
    toolchain = build["toolchain"]
    fields(toolchain, ("compiler", "linker", "inspector", "sdkVersion", "sdkInputs",
                       "headerInputs", "libraryInputs", "environmentSha256", "commands", "flags"))
    for key in ("compiler", "linker", "inspector"):
        record = toolchain[key]
        fields(record, ("path", "sha256", "version"))
        if not dos_path(record["path"]) or not digest(record["sha256"]) or not isinstance(record["version"], str) or not 1 <= len(record["version"]) <= 128:
            raise Refusal("preflight", "receipt")
    if (not isinstance(toolchain["sdkVersion"], str)
            or not re.fullmatch(r"[0-9]+(?:\.[0-9]+){2,3}", toolchain["sdkVersion"])
            or not digest(toolchain["environmentSha256"])
            or toolchain["flags"] != ["/TC", "/W4", "/WX", "/MT", "/LD", "/DNAPI_VERSION=8"]):
        raise Refusal("preflight", "receipt")
    for key in ("sdkInputs", "headerInputs", "libraryInputs"):
        if not isinstance(toolchain[key], list) or not 1 <= len(toolchain[key]) <= 256:
            raise Refusal("preflight", "receipt")
        seen = set()
        for record in toolchain[key]:
            fields(record, ("path", "sha256"))
            if not dos_path(record["path"]) or not digest(record["sha256"]) or record["path"].casefold() in seen:
                raise Refusal("preflight", "receipt")
            seen.add(record["path"].casefold())
    commands = toolchain["commands"]
    if (not isinstance(commands, list) or not 3 <= len(commands) <= 16
            or not all(isinstance(command, str) and 1 <= len(command.encode("utf-8")) <= 4096
                       and not any(character in command for character in "\x00\r\n") for command in commands)):
        raise Refusal("preflight", "receipt")
    fields(build["artifacts"], ("positive", "wrongArch", "apiMismatch"))
    for key, record in build["artifacts"].items():
        fields(record, ("file", "sha256", "bytes", "machine", "pe", "api", "imports", "exports", "delayImports", "resources"))
        expected_file = {"positive": "windows-storage-loader-canary.node",
                         "wrongArch": "windows-storage-loader-wrong-arch.node",
                         "apiMismatch": "windows-storage-loader-api-mismatch.node"}[key]
        if (record["file"] != expected_file or not digest(record["sha256"])
                or type(record["bytes"]) is not int or not 1 <= record["bytes"] <= 4 * MIB
                or record["machine"] != ("i386" if key == "wrongArch" else "amd64")
                or record["pe"] != ("pe32" if key == "wrongArch" else "pe32+")
                or type(record["api"]) is not int or record["api"] != (999 if key == "apiMismatch" else 8)
                or record["exports"] != ["napi_register_module_v1", "node_api_module_get_api_version_v1"]
                or record["delayImports"] != [] or record["resources"] is not False):
            raise Refusal("preflight", "receipt")
        imports = record["imports"]
        if not isinstance(imports, list) or not 1 <= len(imports) <= 64:
            raise Refusal("preflight", "receipt")
        previous = ""
        for imported in imports:
            fields(imported, ("library", "functions"))
            library, functions = imported["library"], imported["functions"]
            if (not isinstance(library, str) or not re.fullmatch(r"[a-z0-9_.-]{1,128}\.dll|node\.exe", library)
                    or library <= previous or not isinstance(functions, list) or not 1 <= len(functions) <= 256
                    or functions != sorted(set(functions))
                    or not all(isinstance(name, str) and re.fullmatch(r"[A-Za-z_?@$][A-Za-z0-9_?@$]{0,255}", name) for name in functions)):
                raise Refusal("preflight", "receipt")
            previous = library
        node = next((item for item in imports if item["library"] == "node.exe"), None)
        if node is None or node["functions"] != ["napi_create_function", "napi_create_string_utf8", "napi_set_named_property", "napi_throw_error"]:
            raise Refusal("preflight", "receipt")
    if build["artifacts"]["positive"]["sha256"] != selected["artifactSha256"]:
        raise Refusal("preflight", "receipt")


def inspect_pe(data):
    """Actual bounded PE inventory. Expected names come only from frozen receipt."""
    def take(offset, size):
        if not 0 <= offset <= len(data) or not 0 <= size <= len(data) - offset:
            raise Refusal("preflight", "artifact")
        return data[offset:offset + size]
    def number(offset, form):
        return struct.unpack(form, take(offset, struct.calcsize(form)))[0]
    if take(0, 2) != b"MZ":
        raise Refusal("preflight", "artifact")
    nt = number(0x3C, "<I")
    if take(nt, 4) != b"PE\0\0":
        raise Refusal("preflight", "artifact")
    machine, sections, _, _, _, optional_size, characteristics = struct.unpack("<HHIIIHH", take(nt + 4, 20))
    if machine not in (0x8664, 0x14C) or not 1 <= sections <= 32 or not characteristics & 0x2000:
        raise Refusal("preflight", "artifact")
    optional = nt + 24
    take(optional, optional_size)
    magic = number(optional, "<H")
    if (machine, magic) not in ((0x8664, 0x20B), (0x14C, 0x10B)):
        raise Refusal("preflight", "artifact")
    directory_start = optional + (112 if magic == 0x20B else 96)
    count = number(directory_start - 4, "<I")
    if count != 16 or directory_start + count * 8 > optional + optional_size:
        raise Refusal("preflight", "artifact")
    directories = [struct.unpack("<II", take(directory_start + index * 8, 8)) for index in range(count)]
    if directories[13] != (0, 0) or directories[2] != (0, 0) or directories[14] != (0, 0):
        raise Refusal("preflight", "artifact")  # delay imports, resources/manifest, CLR forbidden.
    section_map = []
    for index in range(sections):
        offset = optional + optional_size + index * 40
        virtual_size, virtual, raw_size, raw = struct.unpack("<IIII", take(offset + 8, 16))
        take(raw, raw_size)
        if virtual_size > 128 * MIB or raw_size > 4 * MIB:
            raise Refusal("preflight", "artifact")
        section_map.append((virtual, raw_size, raw))
    def rva(address, size=1):
        matches = [raw + address - virtual for virtual, raw_size, raw in section_map
                   if virtual <= address and address + size <= virtual + raw_size]
        if len(matches) != 1:
            raise Refusal("preflight", "artifact")
        take(matches[0], size)
        return matches[0]
    def name(address):
        offset = rva(address)
        result = bytearray()
        for index in range(257):
            byte = take(offset + index, 1)[0]
            rva(address + index)
            if byte == 0:
                try:
                    return result.decode("ascii")
                except UnicodeError:
                    raise Refusal("preflight", "artifact") from None
            result.append(byte)
        raise Refusal("preflight", "artifact")
    imports, import_rva = [], directories[1][0]
    if not import_rva or not 20 <= directories[1][1] <= 65 * 20:
        raise Refusal("preflight", "artifact")
    terminated = False
    for index in range(65):
        if (index + 1) * 20 > directories[1][1]:
            break
        original, timestamp, forwarder, library, first = struct.unpack("<IIIII", take(rva(import_rva + index * 20, 20), 20))
        if not any((original, timestamp, forwarder, library, first)):
            terminated = True
            break
        if not original or timestamp or forwarder or not library or not first:
            raise Refusal("preflight", "artifact")
        functions, width = [], 8 if magic == 0x20B else 4
        for function_index in range(257):
            address = number(rva(original + function_index * width, width), "<Q" if width == 8 else "<I")
            if address == 0:
                break
            if address & (1 << (width * 8 - 1)):
                raise Refusal("preflight", "artifact")  # No ordinal imports in this reviewed profile.
            functions.append(name(address + 2))
        else:
            raise Refusal("preflight", "bounds")
        if not functions or len(functions) != len(set(functions)):
            raise Refusal("preflight", "artifact")
        imports.append({"library": name(library).lower(), "functions": sorted(functions)})
    if not terminated or not imports or len({item["library"] for item in imports}) != len(imports):
        raise Refusal("preflight", "artifact")
    export_rva, export_size = directories[0]
    if not export_rva or export_size < 40:
        raise Refusal("preflight", "artifact")
    export = rva(export_rva, 40)
    functions, names_count, addresses, names, ordinals = struct.unpack("<IIIII", take(export + 20, 20))
    if functions != 2 or names_count != 2:
        raise Refusal("preflight", "artifact")
    exports = []
    for index in range(names_count):
        exports.append(name(number(rva(names + index * 4, 4), "<I")))
        ordinal = number(rva(ordinals + index * 2, 2), "<H")
        if ordinal >= functions:
            raise Refusal("preflight", "artifact")
        target = number(rva(addresses + ordinal * 4, 4), "<I")
        if export_rva <= target < export_rva + export_size:
            raise Refusal("preflight", "artifact")  # No forwarded export.
        rva(target)
    return {"machine": "amd64" if machine == 0x8664 else "i386",
            "pe": "pe32+" if magic == 0x20B else "pe32",
            "imports": sorted(imports, key=lambda item: item["library"]), "exports": sorted(exports)}

SOURCE_FILES = (
    "qualification/windows-storage-loader-fixture.py",
    "qualification/windows-storage-loader-canary.c",
    "qualification/windows-storage-loader-child.mjs",
    "qualification/windows-storage-loader.qualification.mjs",
    "test/windows-storage-loader-contract.test.mjs",
    "qualification/windows-storage-loader.md",
)
SELECTION_FIELDS = {"schema", "sourceCommit", "sourceSha256", "inputRoot",
                    "stageParent", "pythonSha256", "buildReceiptSha256",
                    "artifactSha256", "windowsBuild"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("selection")
        result[key] = value
    return result


def digest(value, length=64):
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{%d}" % length, value)


def dos_path(value):
    if not isinstance(value, str) or len(value.encode("utf-8")) > 4096:
        return False
    if not re.fullmatch(r"[A-Z]:\\[^\\]+(?:\\[^\\]+)*", value):
        return False
    parts = value[3:].split("\\")
    return (len(parts) <= 64 and all(part not in (".", "..")
            and not part.endswith((".", " ")) and len(part.encode("utf-8")) <= 255
            and not re.search(r'[<>:"/|?*;\x00-\x1f]', part)
            and not re.match(r"(?i)^(?:CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])(?:\.|$)", part)
            for part in parts))


def read_selection(path, expected):
    if not digest(expected):
        raise ValueError("selection")
    with open(path, "rb") as stream:
        raw = stream.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024 or hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("selection")
    selected = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    if not isinstance(selected, dict) or set(selected) != SELECTION_FIELDS:
        raise ValueError("selection")
    if type(selected["schema"]) is not int or selected["schema"] != 1:
        raise ValueError("selection")
    if not digest(selected["sourceCommit"], 40):
        raise ValueError("selection")
    sources = selected["sourceSha256"]
    if not isinstance(sources, dict) or set(sources) != set(SOURCE_FILES):
        raise ValueError("selection")
    if not all(digest(value) for value in sources.values()):
        raise ValueError("selection")
    if not all(digest(selected[key]) for key in ("pythonSha256", "buildReceiptSha256", "artifactSha256")):
        raise ValueError("selection")
    if not dos_path(selected["inputRoot"]) or not dos_path(selected["stageParent"]):
        raise ValueError("selection")
    source, stage = selected["inputRoot"].casefold(), selected["stageParent"].casefold()
    if source == stage or source.startswith(stage + "\\") or stage.startswith(source + "\\"):
        raise ValueError("selection")
    if not isinstance(selected["windowsBuild"], str) or not re.fullmatch(r"10\.0\.[0-9]{4,6}", selected["windowsBuild"]):
        raise ValueError("selection")
    return selected


def main():
    # Never let argument/parser/OS diagnostics escape the closed receipt.
    entered = time.monotonic()
    selected = None
    result = {"scope": "windows-storage-loader-fixture", "case": "invalid",
              "state": "refused", "phase": "selection", "reason": "selection"}
    try:
        if len(sys.argv) != 7 or sys.argv[1::2] != ["--selection", "--sha256", "--case"]:
            raise ValueError("selection")
        if sys.argv[6] not in NATIVE_CASES + ("selection-only",):
            raise ValueError("selection")
        result["case"] = sys.argv[6]
        selected = read_selection(sys.argv[2], sys.argv[4])
        if sys.version_info[:3] != (3, 13, 14) or not sys.flags.isolated or not sys.flags.no_site:
            raise Refusal("prerequisite", "runtime", "unknown")
        if sys.argv[6] == "selection-only":
            result.update(phase="prerequisite", reason="native-required")
        elif sys.platform != "win32":
            result.update(state="unknown", phase="prerequisite", reason="platform")
        else:
            result = execute_native(selected, sys.argv[4], sys.argv[2], sys.argv[6], entered)
    except Refusal as failure:
        result.update(state=failure.state, phase=failure.phase, reason=failure.reason)
    except Exception:
        if selected is not None:
            result.update(state="unknown", phase="prerequisite", reason="native")
    sys.stdout.write(json.dumps(result, separators=(",", ":")) + "\n")
    return 0 if result["state"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

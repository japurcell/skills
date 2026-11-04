"""Read-only closed facts for one newly created Windows fixture workspace."""
import json
import sys
import tempfile


class ObservationUnproven(Exception):
    def __init__(self, reason):
        self.reason = reason


def _native_owner_facts():
    import ctypes as ct

    pointer, dword, integer = ct.c_void_p, ct.c_uint32, ct.c_int32
    if ct.sizeof(pointer) != 8:
        raise ObservationUnproven("platform")
    try:
        advapi = ct.WinDLL(r"C:\Windows\System32\advapi32.dll", use_last_error=True, winmode=0x800)
        kernel = ct.WinDLL(r"C:\Windows\System32\kernel32.dll", use_last_error=True, winmode=0x800)
    except Exception:
        raise ObservationUnproven("api-load") from None
    signatures = [
        (advapi.GetNamedSecurityInfoW,
         [ct.c_wchar_p, integer, dword, ct.POINTER(pointer), pointer, pointer, pointer, ct.POINTER(pointer)], dword),
        (advapi.OpenProcessToken, [pointer, dword, ct.POINTER(pointer)], integer),
        (advapi.GetTokenInformation, [pointer, integer, pointer, dword, ct.POINTER(dword)], integer),
        (advapi.CreateWellKnownSid, [integer, pointer, pointer, ct.POINTER(dword)], integer),
        (advapi.IsValidSid, [pointer], integer),
        (advapi.GetLengthSid, [pointer], dword),
        (advapi.EqualSid, [pointer, pointer], integer),
        (kernel.GetCurrentProcess, [], pointer),
        (kernel.CloseHandle, [pointer], integer),
        (kernel.LocalFree, [pointer], pointer),
    ]
    for function, arguments, result in signatures:
        function.argtypes, function.restype = arguments, result

    def sid_length(sid):
        if not sid or not advapi.IsValidSid(sid):
            raise ObservationUnproven("sid")
        length = advapi.GetLengthSid(sid)
        if not 8 <= length <= 68:
            raise ObservationUnproven("sid")
        return length

    def token_sid(token, information_class):
        needed = dword()
        succeeded = advapi.GetTokenInformation(token, information_class, None, 0, ct.byref(needed))
        if succeeded or ct.get_last_error() != 122 or not ct.sizeof(pointer) <= needed.value <= 4096:
            raise ObservationUnproven("token-information")
        buffer = ct.create_string_buffer(needed.value)
        filled = dword()
        if not advapi.GetTokenInformation(token, information_class, buffer, len(buffer), ct.byref(filled)):
            raise ObservationUnproven("token-information")
        if not ct.sizeof(pointer) <= filled.value <= len(buffer):
            raise ObservationUnproven("token-information")
        sid = ct.cast(buffer, ct.POINTER(pointer))[0]
        start = ct.addressof(buffer)
        if sid is None or sid < start + ct.sizeof(pointer) or sid > start + filled.value - 8:
            raise ObservationUnproven("token-information")
        if sid + sid_length(sid) > start + filled.value:
            raise ObservationUnproven("token-information")
        return buffer, sid

    # No caller path is accepted. The only inspected object is created here.
    with tempfile.TemporaryDirectory(prefix="ruminate-owner-facts-") as workspace:
        owner, descriptor, token = pointer(), pointer(), pointer()
        try:
            error = advapi.GetNamedSecurityInfoW(workspace, 1, 1, ct.byref(owner), None,
                                                 None, None, ct.byref(descriptor))
            if error or not owner or not descriptor:
                raise ObservationUnproven("security")
            if not advapi.OpenProcessToken(kernel.GetCurrentProcess(), 8, ct.byref(token)) or not token:
                raise ObservationUnproven("token")
            user_buffer, user_sid = token_sid(token, 1)
            owner_buffer, default_owner_sid = token_sid(token, 4)
            admin = ct.create_string_buffer(68)
            admin_size = dword(len(admin))
            if not advapi.CreateWellKnownSid(26, None, admin, ct.byref(admin_size)):
                raise ObservationUnproven("sid")
            admin_sid = ct.cast(admin, pointer)
            if not 8 <= admin_size.value <= len(admin) or sid_length(admin_sid) > admin_size.value:
                raise ObservationUnproven("sid")
            sid_length(owner)
            # Keep both token buffers alive until every SID comparison returns.
            facts = {
                "ownerEqualsTokenUser": bool(advapi.EqualSid(owner, user_sid)),
                "ownerEqualsTokenOwner": bool(advapi.EqualSid(owner, default_owner_sid)),
                "ownerEqualsAdministrators": bool(advapi.EqualSid(owner, admin_sid)),
                "tokenOwnerEqualsTokenUser": bool(advapi.EqualSid(default_owner_sid, user_sid)),
            }
        finally:
            cleanup_failed = False
            if token:
                try:
                    cleanup_failed = not bool(kernel.CloseHandle(token))
                except Exception:
                    cleanup_failed = True
            if descriptor:
                try:
                    cleanup_failed = bool(kernel.LocalFree(descriptor)) or cleanup_failed
                except Exception:
                    cleanup_failed = True
            if cleanup_failed:
                raise ObservationUnproven("cleanup")
        return facts


def main():
    reason, facts = None, None
    if len(sys.argv) != 1:
        reason = "arguments"
    elif sys.platform != "win32":
        reason = "platform"
    else:
        try:
            facts = _native_owner_facts()
        except ObservationUnproven as error:
            reason = error.reason
        except Exception:
            reason = "unexpected"
    value = {"scope": "windows-new-workspace-owner-facts", "schema": 1,
             "state": "observed" if facts is not None else "unproven"}
    if facts is not None:
        value.update(facts)
    else:
        value["reason"] = reason
    print(json.dumps(value, separators=(",", ":")))
    return 0 if facts is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())

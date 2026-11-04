"""Bounded no-replace operation. This helper issues no receipt or durability claim."""
import ctypes
import errno
import json
import os
import stat
import sys

LIMIT = 16384


def identity(info):
    return f"{info.st_dev}:{info.st_ino}"


def directory(info, expected):
    return stat.S_ISDIR(info.st_mode) and info.st_ino != 0 and identity(info) == expected


def run(request):
    keys = {"source", "destination", "sourceIdentity", "sourceParentIdentity", "destinationParentIdentity"}
    if not isinstance(request, dict) or set(request) != keys:
        return "refused"
    if any(not isinstance(v, str) or not v or len(v.encode()) > 4096 or "\x00" in v for v in request.values()):
        return "refused"
    source, destination = request["source"], request["destination"]
    if any(not os.path.isabs(p) or os.path.normpath(p) != p for p in (source, destination)):
        return "refused"
    sp, sn = os.path.split(source)
    dp, dn = os.path.split(destination)
    if not sn or not dn or sn in (".", "..") or dn in (".", "..") or source == destination:
        return "refused"
    if os.path.realpath(sp) != sp or os.path.realpath(dp) != dp:
        return "refused"
    if sys.platform not in ("darwin", "linux") or (sys.platform == "linux" and os.uname().machine != "x86_64"):
        return "unsupported"
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    sf = df = None
    try:
        sf, df = os.open(sp, flags), os.open(dp, flags)
        source_parent, destination_parent = os.fstat(sf), os.fstat(df)
        if not directory(source_parent, request["sourceParentIdentity"]) or not directory(destination_parent, request["destinationParentIdentity"]):
            return "refused"
        source_info = os.stat(sn, dir_fd=sf, follow_symlinks=False)
        if not directory(source_info, request["sourceIdentity"]):
            return "refused"
        if source_parent.st_dev != destination_parent.st_dev or source_info.st_dev != source_parent.st_dev:
            return "unsupported"
        if not directory(os.stat(sp, follow_symlinks=False), request["sourceParentIdentity"]) or not directory(os.stat(dp, follow_symlinks=False), request["destinationParentIdentity"]):
            return "refused"
        try:
            lib = ctypes.CDLL(None, use_errno=True)
            fn = getattr(lib, "renameatx_np" if sys.platform == "darwin" else "renameat2")
        except (OSError, AttributeError):
            return "unsupported"
        fn.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
        fn.restype = ctypes.c_int
        result = fn(sf, os.fsencode(sn), df, os.fsencode(dn), 4 if sys.platform == "darwin" else 1)
        if result != 0:
            error = ctypes.get_errno()
            if error in (errno.EEXIST, errno.ENOTEMPTY):
                return "collision"
            if error in (errno.ENOSYS, errno.ENOTSUP, errno.EINVAL, errno.EXDEV):
                return "unsupported"
            return "unknown"
        try:
            if not directory(os.stat(sp, follow_symlinks=False), request["sourceParentIdentity"]) or not directory(os.stat(dp, follow_symlinks=False), request["destinationParentIdentity"]):
                return "unknown"
            try:
                os.stat(sn, dir_fd=sf, follow_symlinks=False)
                return "unknown"
            except FileNotFoundError:
                pass
            if not directory(os.stat(dn, dir_fd=df, follow_symlinks=False), request["sourceIdentity"]):
                return "unknown"
            return "moved"
        except OSError:
            return "unknown"
    except OSError:
        return "refused"
    finally:
        if sf is not None:
            os.close(sf)
        if df is not None:
            os.close(df)


def main():
    try:
        data = sys.stdin.buffer.read(LIMIT + 1)
        if len(data) > LIMIT:
            result = "refused"
        else:
            def unique(pairs):
                value = {}
                for key, item in pairs:
                    if key in value:
                        raise ValueError()
                    value[key] = item
                return value
            result = run(json.loads(data.decode("utf-8"), object_pairs_hook=unique))
    except Exception:
        result = "refused"
    sys.stdout.write(result + "\n")


if __name__ == "__main__":
    main()

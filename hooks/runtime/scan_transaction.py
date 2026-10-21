"""Bounded, single-read pre-push input and destination binding.

The exact bytes remain invocation-owned on Transaction.raw for T6/T7 replay.
Nothing in this module resolves a ref, consults tracking state or emits input.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
import re
import select
import stat
import sys
import time

from .scan_types import ScanSecurityError, ScanLimitExceeded

MAX_BYTES = 1048576
MAX_RECORDS = 4096
SECONDS = 2


@dataclass(frozen=True)
class Transaction:
    raw: bytes
    records: tuple[tuple[bytes, bytes, bytes, bytes], ...]
    identity: str
    destination_identity: str


def identities(raw, remote, url):
    destination = hashlib.sha256(b"publication-destination-v1\0" + os.fsencode(remote) + b"\0" + os.fsencode(url)).hexdigest()
    transaction = hashlib.sha256(b"publication-transaction-v1\0" + bytes.fromhex(destination) + b"\0" + raw).hexdigest()
    return transaction, destination


def _ready(descriptor, deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise ScanLimitExceeded("transaction_timeout", "input", seconds=SECONDS)
    if os.name != "nt":
        return bool(select.select([descriptor], [], [], min(remaining, .02))[0])
    # Windows anonymous pipes cannot be selected, and blocking reads do not
    # have a bounded EOF wait on supported Python 3.13 installations.
    import ctypes
    import msvcrt
    if stat.S_ISREG(os.fstat(descriptor).st_mode):
        return True
    available = ctypes.c_ulong()
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    if not kernel.PeekNamedPipe(ctypes.c_void_p(msvcrt.get_osfhandle(descriptor)), None, 0, None, ctypes.byref(available), None):
        if ctypes.get_last_error() == 109:  # broken pipe: a read returns EOF
            return True
        raise ScanSecurityError("transaction_unavailable", "input")
    if available.value:
        return True
    time.sleep(min(remaining, .01))
    return False


def capture_transaction(object_format, remote, url, context):
    deadline = time.monotonic() + SECONDS
    try:
        descriptor = sys.stdin.fileno()
        if os.isatty(descriptor):
            raise ScanSecurityError("transaction_interactive", "input")
        raw = bytearray()
        while True:
            context.check_deadline()
            if not _ready(descriptor, deadline):
                continue
            chunk = os.read(descriptor, min(65536, MAX_BYTES + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
            if len(raw) > MAX_BYTES:
                raise ScanLimitExceeded("transaction_bytes_limit", "input", measured=len(raw), limit=MAX_BYTES)
        raw = bytes(raw)
        records = []
        remote_refs = set()
        oid = rb"[0-9a-f]{" + (b"40" if object_format == "sha1" else b"64") + rb"}"
        pattern = re.compile(rb"([^ \t\r\n\x00-\x20]+) (" + oid + rb") ([^ \t\r\n\x00-\x20]+) (" + oid + rb")\n")
        offset = 0
        while offset < len(raw):
            if time.monotonic() >= deadline:
                raise ScanLimitExceeded("transaction_timeout", "input", seconds=SECONDS)
            match = pattern.match(raw, offset)
            if match is None:
                raise ScanSecurityError("transaction_invalid", "input")
            local_ref, local, remote_ref, old = match.groups()
            parts = remote_ref.split(b"/")
            if (not remote_ref.startswith(b"refs/") or remote_ref.endswith((b"/", b"."))
                    or any(not part or part.startswith(b".") or part.endswith(b".lock") for part in parts)
                    or b".." in remote_ref or b"@{" in remote_ref or b"\x7f" in remote_ref
                    or remote_ref in remote_refs or set(local) == set(old) == {48}
                    or any(c in remote_ref for c in (b"~", b"^", b":", b"?", b"*", b"[", b"\\"))):
                raise ScanSecurityError("transaction_invalid", "input")
            remote_refs.add(remote_ref)
            records.append((local_ref, local, remote_ref, old))
            if len(records) > MAX_RECORDS:
                raise ScanLimitExceeded("transaction_records_limit", "input", measured=len(records), limit=MAX_RECORDS)
            offset = match.end()
        if time.monotonic() >= deadline:
            raise ScanLimitExceeded("transaction_timeout", "input", seconds=SECONDS)
        identity, destination = identities(raw, remote, url)
        context.charge_capture(len(raw))
        return Transaction(raw, tuple(records), identity, destination)
    except (OSError, ValueError, AttributeError):
        raise ScanSecurityError("transaction_unavailable", "input") from None

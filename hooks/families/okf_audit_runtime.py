"""Bounded, content-free audit records for repository OKF stop checks."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any, Mapping


MAX_LINE = 4096


def _reject_linked_path(location: Path) -> None:
    current = Path(location.anchor)
    for part in location.parts[1:]:
        current /= part
        try:
            details = current.lstat()
        except FileNotFoundError:
            continue
        linked = stat.S_ISLNK(details.st_mode)
        if hasattr(details, "st_file_attributes"):
            linked = linked or bool(details.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
        if linked:
            raise OSError("linked OKF audit path")


def record(root: Path, payload: Mapping[str, Any] | None, outcome: str, findings: int, provider: str) -> None:
    paths = sorted(
        path.relative_to(root).as_posix()
        for bundle in ("instructions", "memory")
        for path in (root / ".agents" / bundle).rglob("*.md")
        if path.is_file()
    )
    if not paths:
        return
    session = "" if payload is None else str(payload.get("sessionId") or payload.get("session_id") or "")
    event = "" if payload is None else str(payload.get("hook_event_name") or "")
    base: dict[str, Any] = {
        "hook": "lint-okf",
        "outcome": outcome,
        "attempt": "retry" if payload is not None and (payload.get("stop_hook_active") is True or payload.get("stopHookActive") is True) else "first",
        "checked": len(paths),
        "findings": findings,
        "session": hashlib.sha256(session.encode()).hexdigest()[:16] if session else "",
        "event": event[:32],
    }
    selected: list[str] = []
    for path in paths:
        candidate = {**base, "paths": [*selected, path], "omitted_paths": len(paths) - len(selected) - 1}
        if len(json.dumps(candidate, ensure_ascii=False, separators=(",", ":")).encode()) + 1 > MAX_LINE:
            break
        selected.append(path)
    line = json.dumps({**base, "paths": selected, "omitted_paths": len(paths) - len(selected)}, ensure_ascii=False, separators=(",", ":")) + "\n"
    if len(line.encode()) > MAX_LINE:
        raise OSError("OKF audit metadata exceeds 4 KiB")
    location = Path(os.environ.get("AUDIT_LOG", str(Path.home() / f".{provider}" / "hooks" / "audit.log"))).absolute()
    try:
        if os.name != "nt" and location.parts[:2] == ("/", "var") and Path("/var").resolve() == Path("/private/var"):
            location = Path("/private/var").joinpath(*location.parts[2:])
        _reject_linked_path(location)
        location.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(location, flags, 0o600)
        try:
            with os.fdopen(descriptor, "r+b", closefd=False) as stream:
                stream.seek(0, os.SEEK_END)
                size = stream.tell()
                stream.seek(max(0, size - MAX_LINE))
                previous = stream.read().splitlines()[-1:] or []
                if previous != [line.rstrip("\n").encode()]:
                    stream.seek(0, os.SEEK_END)
                    stream.write(line.encode())
                    stream.flush()
        finally:
            os.close(descriptor)
    except OSError:
        print("lint-okf warning: audit log unavailable", file=sys.stderr)

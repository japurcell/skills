#!/usr/bin/env python3
"""Shared durable byte writes; callers own destination validation and transactions."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile


def write_synced_bytes(descriptor: int, content: bytes, *, mode: int | None = None) -> None:
    """Write and sync bytes, taking ownership of the supplied descriptor."""
    try:
        if mode is not None and hasattr(os, "fchmod"):
            os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor != -1:
            os.close(descriptor)


def stage_bytes(
    path: Path,
    content: bytes,
    *,
    prefix: str,
    suffix: str = "",
    mode: int | None = None,
) -> Path:
    """Create a synced sibling temporary file, removing it if writing fails."""
    descriptor, name = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=path.parent)
    temporary = Path(name)
    try:
        write_synced_bytes(descriptor, content, mode=mode)
        return temporary
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def atomic_write_bytes(
    path: Path,
    content: bytes,
    *,
    suffix: str = "",
    mode: int | None = None,
) -> None:
    """Replace a destination with synced bytes and remove any staging residue."""
    temporary = stage_bytes(path, content, prefix=f".{path.name}.", suffix=suffix, mode=mode)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)

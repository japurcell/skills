"""Strict finite schema-1 checkpoint and publication budget admission."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import stat

DEFAULTS = {
    "checkpoint": dict(max_objects=4096, max_candidate_bytes=67108864, max_seconds=30,
                       max_capture_bytes=134217728, max_temp_bytes=268435456),
    "publication": dict(max_objects=20000, max_candidate_bytes=268435456, max_seconds=120,
                        max_capture_bytes=536870912, max_temp_bytes=805306368),
}
RANGES = {
    "checkpoint": dict(max_objects=(1, 16384), max_candidate_bytes=(1048576, 536870912),
                       max_seconds=(1, 120), max_capture_bytes=(1048576, 1073741824),
                       max_temp_bytes=(1048576, 2147483648)),
    "publication": dict(max_objects=(1, 100000), max_candidate_bytes=(1048576, 1073741824),
                        max_seconds=(1, 600), max_capture_bytes=(1048576, 2147483648),
                        max_temp_bytes=(1048576, 3221225472)),
}


def unique(pairs):
    value = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate field")
        value[key] = child
    return value


def load_budget(path: str | None):
    if path is None:
        document = dict(schema_version=1, **DEFAULTS)
        raw = json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
    else:
        requested = Path(path).absolute()
        selected = requested.parent.resolve(strict=True) / requested.name
        # A pipe, device, symlink or concurrent replacement is not a budget file.
        for parent in (selected, *selected.parents):
            info = parent.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("unsafe budget")
        descriptor = os.open(selected, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(descriptor, "rb") as handle:
            before = os.fstat(handle.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > 65536:
                raise ValueError("unsafe budget")
            raw = handle.read(65537)
            after = os.fstat(handle.fileno())
        identity = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        if len(raw) > 65536 or identity(before) != identity(after) or identity(after) != identity(selected.lstat()):
            raise ValueError("changed budget")
        document = json.loads(raw, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
    if (not isinstance(document, dict) or set(document) != {"schema_version", "checkpoint", "publication"}
            or type(document["schema_version"]) is not int or document["schema_version"] != 1):
        raise ValueError("invalid schema")
    for profile, fields in RANGES.items():
        values = document[profile]
        if not isinstance(values, dict) or set(values) != set(fields):
            raise ValueError("invalid profile")
        for key, (minimum, maximum) in fields.items():
            value = values[key]
            accepted = (int, float) if key == "max_seconds" else (int,)
            if type(value) not in accepted or not math.isfinite(value) or not minimum <= value <= maximum:
                raise ValueError("invalid limit")
    return document["checkpoint"], hashlib.sha256(raw).hexdigest()

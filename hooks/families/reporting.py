"""Pure build identity and embedded bounded security-report primitives."""
from __future__ import annotations

import hashlib
from pathlib import Path

from hooks.families.scan_runtime import MODULES as SCAN_RUNTIME_MODULES


def build_identity(family: str) -> str:
    """Hash trusted canonical inputs at generation, never during a hook call."""
    root = Path(__file__).resolve().parent
    names = ("reporting.py", "common.py", "audit.py", family + ".py")
    if family == "scan_secrets":
        names += ("scanner_stream.py", "diagnostics.py", "scan_runtime.py")
    digest = hashlib.sha256()
    for name in names:
        digest.update(name.encode("ascii") + b"\0" + (root / name).read_bytes())
    for name in ("providers.py", "manifest.py"):
        digest.update(name.encode("ascii") + b"\0" + (root.parent / name).read_bytes())
    runtime_names = ({name + ".py" for name in SCAN_RUNTIME_MODULES} if family == "scan_secrets" else
                     {"scan_reporting.py", "scan_allowlist.py", "tool_guard_policy.py"})
    for path in sorted((root.parent / "runtime").glob("*.py")):
        if runtime_names is not None and path.name not in runtime_names:
            continue
        digest.update(path.name.encode("ascii") + b"\0" + path.read_bytes())
    if family == "scan_secrets":
        name = "scripts/trusted_hook_launch.py"
        digest.update(name.encode("ascii") + b"\0" + (root.parents[1] / name).read_bytes())
    return digest.hexdigest()[:16]


_RUNTIME_SOURCE = (Path(__file__).resolve().parents[1] / "runtime/scan_reporting.py").read_text()
CREDENTIAL_LABEL_SOURCE = _RUNTIME_SOURCE.split("# Bounds apply", 1)[0]
CREDENTIAL_LABEL_SOURCE = CREDENTIAL_LABEL_SOURCE.split("import unicodedata\n", 1)[1][:-1]

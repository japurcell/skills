"""Pure build identity and embedded bounded security-report primitives."""
from __future__ import annotations

import hashlib
from pathlib import Path


def build_identity(family: str) -> str:
    """Hash trusted canonical inputs at generation, never during a hook call."""
    root = Path(__file__).resolve().parent
    names = ("reporting.py", "allowlist.py", "common.py", "audit.py", family + ".py")
    if family == "scan_secrets":
        names += ("scanner_stream.py", "diagnostics.py")
    digest = hashlib.sha256()
    for name in names:
        digest.update(name.encode("ascii") + b"\0" + (root / name).read_bytes())
    for name in ("providers.py", "manifest.py"):
        digest.update(name.encode("ascii") + b"\0" + (root.parent / name).read_bytes())
    return digest.hexdigest()[:16]


SOURCE = r'''
# Bounds apply to retained report fields before JSON serialization. Labels are
# ASCII, so each retained character costs at most two JSON bytes after escaping.
REPORT_LABEL_CHARS = 160


def report_text(value, limit=REPORT_LABEL_CHARS):
    text = unicodedata.normalize("NFKC", value[:4096]) if isinstance(value, str) else ""
    text = "".join(char if 32 <= ord(char) <= 126 else " " for char in text)
    return text if len(text) <= limit else text[:limit - 3] + "..."


def report_label(value):
    text = unicodedata.normalize("NFKC", value[:4096]) if isinstance(value, str) else ""
    # Labels have no need to reproduce a credential-bearing identifier. Omit the
    # whole label, including credentials crossing the display clipping boundary.
    if re.search(r"(?i)(?:gh[pousr]_|github_pat_|akia|sk-|sk_live_|xox[baprs]-|bearer\s|(?:token|secret|password|passwd|api[_-]?key|authorization)\s*[:=]|https?://[^/\s]*@)", text):
        return "[REDACTED]"
    return report_text(text)


def report_json_bytes(value):
    """Exact ensure_ascii JSON byte cost without serializing retained data."""
    if isinstance(value, str):
        return 2 + sum(2 if char in '\\"' or char in '\b\f\n\r\t' else
                       6 if ord(char) < 32 or 127 <= ord(char) <= 65535 else
                       12 if ord(char) > 65535 else 1 for char in value)
    if isinstance(value, dict):
        return 2 + max(0, len(value) - 1) + sum(report_json_bytes(key) + 1 + report_json_bytes(child) for key, child in value.items())
    if isinstance(value, (list, tuple)):
        return 2 + max(0, len(value) - 1) + sum(report_json_bytes(child) for child in value)
    if value is None:
        return 4
    if isinstance(value, bool):
        return 4 if value else 5
    return len(str(value))
'''

"""Shared mechanics for disposable hook benchmarks, outside measured launches."""
from __future__ import annotations

import os
from pathlib import Path
import re

from tool_guard_corpus import PROVIDERS, script_path


def disposable_environment(home: Path, provider: str) -> dict[str, str]:
    """Redirect common state while retaining caller-specific environment overlays."""
    env = os.environ.copy()
    for key in ("SKIP_TOOL_GUARD", "TOOL_GUARD_ALLOWLIST"):
        env.pop(key, None)
    env.update({
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "XDG_CACHE_HOME": str(home / ".cache"),
        "XDG_DATA_HOME": str(home / ".local/share"),
        "AUDIT_LOG": str(home / "audit.log"),
        "AUDIT_LOCK": str(home / "audit.lock"),
        "TOOL_GUARD_LOG_DIR": str(home / "guard" if provider == "gemini" else home / "guard.log"),
    })
    return env


def collect_macos_rss(command, checked_launch):
    """Use a separate checked launch; callers retain timeout/error/cwd policy."""
    memory = checked_launch(["/usr/bin/time", "-l", *command])
    match = re.search(rb"([0-9]+)\s+maximum resident set size", memory.stderr)
    return memory, int(match.group(1)) if match is not None else None


def guardian_runtime_footprint() -> tuple[tuple[str, ...], tuple[str, ...], str]:
    """Name runtime scripts, recursive Python helper roots, and canonical policy."""
    scripts = tuple(script_path(Path("."), provider).as_posix() for provider in PROVIDERS)
    helpers = tuple(str(Path(path).parent / "helpers") + "/" for path in scripts)
    return scripts, helpers, "hooks/families/tool_guard.py"

#!/usr/bin/env python3
"""Isolated subprocess support for public Tool Guardian tests."""

from __future__ import annotations

from collections.abc import Mapping
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from tool_guard_corpus import script_path


def guard_test_environment(
    inherited: Mapping[str, str],
    directory: Path,
    *,
    home: Path,
    log: Path,
    mode: str,
) -> dict[str, str]:
    """Set fixture-owned paths while retaining the caller's inheritance policy."""
    return {
        **inherited,
        "HOME": str(home),
        "GUARD_MODE": mode,
        "TOOL_GUARD_LOG_DIR": str(log),
        "AUDIT_LOG": str(directory / "audit.log"),
        "OBSERVABILITY_LOG_PATH": str(directory / "observability.jsonl"),
    }


def invoke_guard(
    root: Path,
    provider: str,
    payload: str | bytes,
    *,
    mode: str = "block",
    allowlist: str | None = None,
    script: Path | None = None,
) -> subprocess.CompletedProcess:
    """Run the actual provider entrypoint with fixture-owned home and logs."""
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        home = directory / "home"
        home.mkdir()
        env = {
            key: value for key, value in os.environ.items()
            if key not in {
                "SKIP_TOOL_GUARD", "TOOL_GUARD_ALLOWLIST", "AUDIT_LOCK",
                "AUDIT_PASSIVE_LOG_SHADOW_LOG", "GEMINI_PASSIVE_SHADOW_LOG",
                "COPILOT_OBSERVABILITY_LOG_PATH", "GEMINI_OBSERVABILITY_LOG_PATH",
            }
        }
        env = guard_test_environment(
            env, directory, home=home, log=directory / "guard-log", mode=mode,
        )
        if allowlist is not None:
            env["TOOL_GUARD_ALLOWLIST"] = allowlist
        return subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(script or script_path(root, provider))],
            input=payload,
            text=isinstance(payload, str),
            capture_output=True,
            env=env,
            timeout=5,
        )


def native_decision(response: dict) -> str | None:
    """Read the native decision shapes exercised by the public schema tests."""
    return (
        response.get("permissionDecision") or response.get("decision")
        or response.get("hookSpecificOutput", {}).get("permissionDecision")
        or ("allow" if response == {} else None)
    )

"""Render runtime-local OKF mechanics and content-free audit helpers."""

from __future__ import annotations

from pathlib import Path

from hooks.manifest import GeneratedTarget
from hooks.providers import Provider


_SOURCES = {"okf.py": "okf_runtime.py", "okf_audit.py": "okf_audit_runtime.py"}


def render(provider: Provider, target: GeneratedTarget) -> str:
    """Share mechanics while each adapter retains its provider policy."""
    if target.provider != provider.name or provider.name not in {"github", "gemini", "codex"}:
        raise ValueError(f"Unsupported OKF target/provider: {target.output_path}")
    try:
        source = _SOURCES[target.output_path.name]
    except KeyError as error:
        raise ValueError(f"Unsupported OKF target: {target.output_path}") from error
    body = Path(__file__).with_name(source).read_text(encoding="utf-8")
    return (
        "#!/usr/bin/env python3\n"
        "# Generated from hooks/families/okf.py by scripts/generate-hooks.py. Do not edit.\n"
        + body
    )

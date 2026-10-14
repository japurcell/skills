"""Small raw provider adapters for public hook tests."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def hook_entrypoint(root: Path, provider: str, filename: str) -> Path:
    directory = ".codex/hooks" if provider == "codex" else f".{provider}/hooks/scripts"
    return root / directory / filename


def raw_tool_envelope(provider: str, tool: str, value: object) -> dict:
    """Wrap exactly the supplied tool and value; leave aliases and shapes to callers."""
    if provider == "copilot":
        return {"hook_event_name": "preToolUse", "toolName": tool, "toolArgs": value}
    return {"hook_event_name": "PreToolUse" if provider == "codex" else "BeforeTool",
            "tool_name": tool, "tool_input": value}


def fresh_common(root: Path, module_name: str):
    """Load an uncached module so patched state cannot leak between test cases."""
    path = hook_entrypoint(root, "codex", "helpers/common.py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

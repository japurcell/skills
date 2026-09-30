#!/usr/bin/env python3
# Generated from hooks/families/repository_runtime.py by scripts/generate-hooks.py. Do not edit.

from __future__ import annotations
import hashlib
import os
from pathlib import Path
import sys
from helpers.runtime_config import load_runtime_config

def main():
    package = Path(__file__).resolve().parent
    os.environ["AGENT_ASSETS_RUNTIME_CONFIG"] = str(package / "runtime.json")
    config, _skills, root = load_runtime_config()
    handlers = {"required-skills": "skill-context-injector.py" if config["provider"] == "gemini" else "load-required-skills.py",
                "tool-guard": "tool-guard.py", "scan-secrets": "scan-secrets.py", "scan-secrets-end": "scan-secrets.py"}
    if len(sys.argv) != 2 or sys.argv[1] not in handlers:
        raise ValueError("Choose an installed hook")
    handler = package / handlers[sys.argv[1]]
    if not handler.is_file():
        raise ValueError("Hook is not installed")
    override = os.environ.get("AGENT_ASSETS_STATE_DIR")
    if override:
        base = Path(override).expanduser()
        if not base.is_absolute():
            raise ValueError("AGENT_ASSETS_STATE_DIR must be absolute")
    elif sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local"))) / "agent-assets"
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Application Support/agent-assets"
    else:
        base = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "agent-assets"
    identity = hashlib.sha256(os.path.normcase(str(root.resolve())).encode("utf-8")).hexdigest()[:24]
    state = base / config["provider"] / identity
    if state.resolve().is_relative_to(root):
        raise ValueError("Runtime state must be outside the installed repository")
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.environ.update({"AUDIT_LOG": str(state / "audit.log"), "AUDIT_LOCK": str(state / "audit.log.lock"),
                       "GUARD_MODE": "block", "SCAN_SCOPE": "diff",
                       "SCAN_MODE": "warn" if sys.argv[1] == "scan-secrets-end" and config["provider"] != "codex" else "block",
                       "AGENT_ASSETS_AUDIT_DIR": str(state), "SECRETS_LOG_DIR": str(state / "secrets"),
                       "TOOL_GUARD_LOG_DIR": str(state / "guard" if config["provider"] == "gemini" else state / "guard.log"),
                       "OBSERVABILITY_LOG_PATH": str(state / "observability.ndjson"),
                       "COPILOT_OBSERVABILITY_LOG_PATH": str(state / "observability.ndjson"),
                       "GEMINI_OBSERVABILITY_LOG_PATH": str(state / "observability.ndjson"),
                       "PYTHONDONTWRITEBYTECODE": "1"})
    os.chdir(root)
    os.execv(sys.executable, [sys.executable, "-B", str(handler)])

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print("agent-assets runtime configuration unavailable: " + str(error), file=sys.stderr)
        raise SystemExit(2)

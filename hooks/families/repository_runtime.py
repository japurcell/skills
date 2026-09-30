"""Self-contained installed repository launcher and validated configuration helper."""

CONFIG_SOURCE = r'''from __future__ import annotations
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate runtime configuration key")
        result[key] = value
    return result

def _safe(root, path):
    relative = path.relative_to(root)
    current = root
    for part in relative.parts:
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Linked runtime path")
    return path

def load_runtime_config():
    path = Path(os.environ["AGENT_ASSETS_RUNTIME_CONFIG"])
    if not path.is_absolute() or path.name != "runtime.json":
        raise ValueError("Runtime configuration must be an absolute package path")
    root = path.parents[3]
    _safe(root, path)
    config = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    if (not isinstance(config, dict) or set(config) != {"schema_version", "provider", "installation_id", "skills", "references", "required_skill_files"}
            or config["schema_version"] != 1 or config["provider"] not in {"codex", "copilot", "gemini"}
            or not isinstance(config["installation_id"], str) or not re.fullmatch(r"[0-9a-f-]{36}", config["installation_id"])):
        raise ValueError("Invalid runtime configuration")
    prefix = {"codex": ".codex", "copilot": ".github", "gemini": ".gemini"}[config["provider"]]
    if path != root / prefix / "hooks/agent-assets/runtime.json":
        raise ValueError("Runtime provider/package mismatch")
    if config["skills"] != "../../../.agents/skills" or config["references"] != "../../../.agents/references":
        raise ValueError("Invalid package-relative asset roots")
    skills = _safe(root, root / ".agents/skills")
    _safe(root, root / ".agents/references")
    files = config["required_skill_files"]
    if not isinstance(files, list) or any(not isinstance(name, str) or not name for name in files) or len(set(files)) != len(files):
        raise ValueError("Invalid required skill files")
    for name in files:
        parts = PurePosixPath(name).parts
        if PurePosixPath(name).is_absolute() or any(part in {".", ".."} for part in parts) or "\\" in name or ":" in name:
            raise ValueError("Required skill path leaves package")
        _safe(root, skills.joinpath(*parts))
    return config, skills, root
'''

LAUNCH_SOURCE = r'''from __future__ import annotations
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
'''


def render(provider, target):
    source = CONFIG_SOURCE if target.output_path.name == "runtime_config.py" else LAUNCH_SOURCE
    return "#!/usr/bin/env python3\n# Generated from hooks/families/repository_runtime.py by scripts/generate-hooks.py. Do not edit.\n\n" + source

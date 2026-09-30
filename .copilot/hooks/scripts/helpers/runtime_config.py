#!/usr/bin/env python3
# Generated from hooks/families/repository_runtime.py by scripts/generate-hooks.py. Do not edit.

from __future__ import annotations
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

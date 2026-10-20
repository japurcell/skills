"""Shared mechanics for disposable hook benchmarks, outside measured launches."""
from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import os
import shutil
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


def prepare_failure(case, home: Path):
    """Establish and prove failures before launching the measured subprocess."""
    injection = (case.fixture_metadata or {}).get("injection", "none")
    if injection == "audit-unavailable":
        obstacle = home / "audit-obstacle"
        if not obstacle.exists():
            obstacle.write_text("intentional non-directory audit parent\n", encoding="utf-8")
        if not obstacle.is_file() or obstacle.is_symlink():
            raise ValueError("audit failure injection is not an isolated regular file")
        return replace(case, environment={**case.environment, "TOOL_GUARD_LOG_DIR": str(obstacle / "guard.log")})
    if injection == "missing-policy":
        source = home / "bootstrap-source"
        if not source.exists():
            shutil.copytree(case.script.parent, source, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            (source / "helpers/tool_guard_policy.py").unlink()
        if (source / "helpers/tool_guard_policy.py").exists():
            raise ValueError("bootstrap failure injection did not remove policy")
        return replace(case, script=source / case.script.name)
    if injection == "malformed-json":
        try:
            json.loads(case.payload)
        except (ValueError, UnicodeDecodeError):
            return case
        raise ValueError("transport failure injection is valid JSON")
    if injection != "none":
        raise ValueError("unknown failure injection")
    return case


def verify_audit(home: Path, case, calls: int) -> dict:
    contract = case.fixture_metadata["contract"]
    audit = contract["audit"]
    injection = case.fixture_metadata["injection"]
    injection_proof = None
    if injection == "audit-unavailable":
        obstacle = home / "audit-obstacle"
        if not obstacle.is_file() or obstacle.is_symlink():
            raise ValueError("audit failure condition missing")
        injection_proof = {"kind": injection, "parent_is_regular_file": True,
                           "sha256": hashlib.sha256(obstacle.read_bytes()).hexdigest()}
    elif injection == "missing-policy":
        missing = home / "bootstrap-source/helpers/tool_guard_policy.py"
        if missing.exists() or not missing.parent.is_dir():
            raise ValueError("missing-policy failure condition missing")
        injection_proof = {"kind": injection, "policy_absent": True}
    elif injection == "malformed-json":
        try:
            json.loads(case.payload)
        except (ValueError, UnicodeDecodeError):
            injection_proof = {"kind": injection, "invalid_json": True}
        else:
            raise ValueError("transport failure condition missing")
    files = [home / "guard.log"] if not case.name.startswith("gemini.") else sorted((home / "guard").glob("*.log"))
    evidence, records = [], []
    for path in files:
        if not path.is_file():
            continue
        data = path.read_bytes()
        evidence.append({"path": str(path.relative_to(home)), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        for line in data.decode("utf-8").splitlines():
            start = line.find("{")
            if start < 0:
                raise ValueError("invalid completed audit record")
            record = json.loads(line[start:])
            if record.get("mode") != contract["mode"] or record.get("event") != audit["event"]:
                raise ValueError("completed audit event/mode mismatch")
            if any(record.get(key) != value for key, value in contract["record_attribution"].items()):
                raise ValueError("completed audit attribution mismatch")
            records.append(record)
    required = calls * audit["records_per_call"]
    return {"records": len(records), "required_records": required, "calls": calls,
            "status": audit["outcome"] if len(records) == required else "missing or unexpected",
            "audit_outcome": audit["outcome"], "legacy_exception": False, "files": evidence,
            "failure_injection": injection_proof, "verified_after_elapsed": True}


def guardian_decision(provider: str, output: dict, *, contract: dict | None = None) -> str:
    from tool_guard_corpus import decision
    if (contract and contract["mode"] == "warn" and contract["decision"] == "allow"
            and contract["attribution"].get("security_outcome") == "findings"):
        output = {key: value for key, value in output.items()
                  if key not in {"systemMessage", "reason", "permissionDecisionReason"}}
    return decision(provider, output)


def guardian_canonical_paths() -> tuple[str, ...]:
    return ("hooks/families/tool_guard.py", "hooks/families/reporting.py", "hooks/families/allowlist.py",
            "hooks/families/common.py", "hooks/families/audit.py")

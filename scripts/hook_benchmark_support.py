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


def guardian_benchmark_environment(*, cold: bool = False) -> dict[str, str]:
    """Fixed audit and bytecode defaults; callers retain their overlay order."""
    return {"OBSERVABILITY_TESTING": "1", "PYTHONDONTWRITEBYTECODE": "1" if cold else "",
            "PYTHONPYCACHEPREFIX": "",
            "AUDIT_PASSIVE_LOG_MODE": "default", "AUDIT_LOG_MAX_BYTES": "134217728",
            "AUDIT_LOG_MAX_BACKUPS": "0"}


def collect_macos_rss(command, checked_launch):
    """Use a separate checked launch; callers retain timeout/error/cwd policy."""
    memory = checked_launch(["/usr/bin/time", "-l", *command])
    match = re.search(rb"([0-9]+)\s+maximum resident set size", memory.stderr)
    return memory, int(match.group(1)) if match is not None else None


def guardian_runtime_footprint() -> tuple[tuple[str, ...], tuple[str, ...], str]:
    """Name runtime scripts, recursive Python helper roots, and canonical renderer."""
    scripts = tuple(script_path(Path("."), provider).as_posix() for provider in PROVIDERS)
    helpers = tuple(str(Path(path).parent / "helpers") + "/" for path in scripts)
    return scripts, helpers, "hooks/families/tool_guard.py"


def transport_failure_proof(case) -> dict | None:
    """Inspect current transport bytes and limits without caching or mutation."""
    metadata = case.fixture_metadata or {}
    injection = metadata.get("injection", "none")
    if injection == "raw-envelope":
        return reader_boundary_proof(case)
    if injection == "malformed-json":
        try:
            json.loads(case.payload)
        except (ValueError, UnicodeDecodeError):
            return (reader_boundary_proof(case) if "reader_limits" in metadata
                    else {"kind": injection, "invalid_json": True})
    return None


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
    if injection in {"raw-envelope", "malformed-json"}:
        if transport_failure_proof(case) is None:
            raise ValueError("transport failure injection is valid JSON")
        return case
    if injection != "none":
        raise ValueError("unknown failure injection")
    return case


def read_audit_records(home: Path, case, *, require_json: bool = True):
    """Return file evidence and lazy records, preserving first-failure ordering."""
    files = [home / "guard.log"] if not case.name.startswith("gemini.") else sorted((home / "guard").glob("*.log"))
    evidence = []

    def records():
        for path in files:
            if not path.is_file():
                continue
            data = path.read_bytes()
            evidence.append({"path": str(path.relative_to(home)), "bytes": len(data),
                             "sha256": hashlib.sha256(data).hexdigest()})
            for line in data.decode("utf-8").splitlines():
                start = line.find("{")
                if start < 0 and require_json:
                    raise ValueError("invalid completed audit record")
                yield json.loads(line[start:]) if start >= 0 else {}

    return evidence, records()


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
    elif injection in {"raw-envelope", "malformed-json"}:
        injection_proof = transport_failure_proof(case)
        if injection_proof is None:
            raise ValueError("transport failure condition missing")
    evidence, completed = read_audit_records(home, case)
    records = []
    for record in completed:
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


def guardian_response_matches(provider: str, exit_code: int, output: dict,
                              expected: str, *, contract: dict | None = None) -> bool:
    """Check permission success, then validate any reviewed response attribution."""
    from fixtures.tool_guard_resource_cases import validate_response
    if exit_code or guardian_decision(provider, output, contract=contract) != expected:
        return False
    if contract is not None:
        validate_response(contract, output, provider=provider)
    return True


def guardian_canonical_paths() -> tuple[str, ...]:
    # Retain retired inputs when verifying frozen baseline source archives.
    return ("hooks/families/tool_guard.py", "hooks/families/reporting.py", "hooks/families/allowlist.py",
            "hooks/families/common.py", "hooks/families/audit.py", "hooks/runtime/tool_guard_policy.py")


def reader_boundary_proof(case) -> dict:
    """Prove declared transport outcomes independently, outside subprocess clocks."""
    from fixtures.tool_guard_resource_cases import raw_structural_size, valid_reader_limits
    metadata = case.fixture_metadata
    limits = metadata.get("reader_limits")
    if not valid_reader_limits(limits):
        raise ValueError("missing reviewed reader limits")
    markers = raw_structural_size(case.payload)
    if type(metadata.get("structural_markers")) is not int or markers != metadata["structural_markers"]:
        raise ValueError("stale structural marker count")
    try:
        json.loads(case.payload)
        valid = True
    except (ValueError, UnicodeDecodeError):
        valid = False
    injection = metadata["injection"]
    if valid != (injection == "raw-envelope"):
        raise ValueError("transport injection JSON validity mismatch")
    exceeded = (len(case.payload) > limits["max_bytes"]
                or limits["max_markers"] is not None and markers > limits["max_markers"])
    if valid and exceeded != (metadata["contract"]["audit"]["outcome"] == "not_attempted"):
        raise ValueError("raw boundary failure condition missing")
    return {"kind": injection, "payload_bytes": len(case.payload), "reviewed_limits": limits,
            "structural_markers": markers, "valid_json": valid, "reader_limit_exceeded": exceeded}

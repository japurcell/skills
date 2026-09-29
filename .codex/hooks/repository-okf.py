#!/usr/bin/env python3
"""Repository-local Codex Stop adapter for the canonical OKF linter."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from helpers.common import convert_windows_path_to_posix, emit_json, read_json_input  # noqa: E402
from helpers.okf_audit import record as audit_record  # noqa: E402

MAX_OUTPUT = 8192
MAX_DIAGNOSTICS = 20
ID = re.compile(r"OKF[0-9]{3}\Z")


def response_size(value: dict[str, str]) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode())


def rerun() -> str:
    platform = os.environ.get("OKF_LINT_TEST_PLATFORM")
    return "python scripts/lint-okf.py" if platform == "windows" or (platform is None and os.name == "nt") else "./scripts/lint-okf.py"


def checkout(payload: dict[str, object]) -> Path:
    raw = payload.get("cwd")
    if not isinstance(raw, str) or not raw:
        raise ValueError("missing cwd")
    cwd = Path(convert_windows_path_to_posix(raw))
    if not cwd.is_absolute():
        cwd = ROOT / cwd
    try:
        cwd.resolve().relative_to(ROOT)
    except ValueError as error:
        raise ValueError("cwd outside adapter checkout") from error
    if not cwd.is_dir():
        raise ValueError("cwd is not a directory")
    return ROOT


def diagnostics(root: Path) -> list[dict[str, object]]:
    linter = root / "scripts/lint-okf.py"
    if not linter.is_file():
        raise ValueError("missing scripts/lint-okf.py")
    completed = subprocess.run([sys.executable, str(linter), "--format", "json"], cwd=root, capture_output=True, text=True, timeout=8, check=False)
    if completed.returncode not in (0, 1):
        raise ValueError("central linter incomplete")
    parsed = json.loads(completed.stdout)
    if not isinstance(parsed, dict) or set(parsed) != {"schema_version", "diagnostics"} or parsed["schema_version"] != 1 or not isinstance(parsed["diagnostics"], list):
        raise ValueError("invalid linter JSON")
    values = parsed["diagnostics"]
    for item in values:
        if not isinstance(item, dict) or set(item) != {"id", "path", "line", "column", "message"} or not isinstance(item["id"], str) or not ID.fullmatch(item["id"]) or not isinstance(item["path"], str) or not item["path"] or type(item["line"]) is not int or item["line"] < 1 or type(item["column"]) is not int or item["column"] < 1 or not isinstance(item["message"], str) or not item["message"]:
            raise ValueError("invalid linter diagnostic")
    if (completed.returncode == 0) != (not values):
        raise ValueError("inconsistent linter status")
    return sorted(values, key=lambda item: (item["path"], item["line"], item["column"], item["id"]))


def finding_reason(values: list[dict[str, object]], retry: bool) -> str:
    count = len(values)
    noun = "diagnostic" if count == 1 else "diagnostics"
    header = f"repository-okf: {'unresolved' if retry else 'blocked'}; {count} {noun}\n" + (
        "OKF unresolved after repair attempt:" if retry else "OKF validation failed:"
    )
    lines = [f"{item['path']}:{item['line']}:{item['column']}: {item['id']} {' '.join(str(item['message']).splitlines())}" for item in values[:MAX_DIAGNOSTICS]]
    envelope = (lambda text: {"systemMessage": text}) if retry else (lambda text: {"decision": "block", "reason": text})
    selected: list[str] = []
    for line in lines:
        candidate = "\n".join((header, *selected, line, f"{len(values)-len(selected)-1} additional diagnostics omitted.", f"Rerun: {rerun()}"))
        if response_size(envelope(candidate)) >= MAX_OUTPUT:
            break
        selected.append(line)
    reason = "\n".join((header, *selected, f"{len(values)-len(selected)} additional diagnostics omitted.", f"Rerun: {rerun()}"))
    return reason


def main() -> int:
    payload: dict[str, object] | None = None
    root: Path | None = None
    outcome = "incomplete"
    findings = 0
    try:
        payload = read_json_input()
        root = checkout(payload)
        values = diagnostics(root)
        findings = len(values)
        if not values:
            outcome = "pass"
            emit_json({"systemMessage": "repository-okf: pass; 0 diagnostics"})
            return 0
        outcome = "fail"
        retry = payload.get("stop_hook_active") is True or payload.get("stopHookActive") is True
        reason = finding_reason(values, retry)
        emit_json({"systemMessage": reason} if retry else {"decision": "block", "reason": reason})
    except Exception:
        emit_json({"systemMessage": f"repository-okf: incomplete; OKF900: repository OKF validation incomplete. Rerun: {rerun()}"})
    finally:
        if root is not None:
            try:
                audit_record(root, payload, outcome, findings, "codex")
            except Exception:
                print("lint-okf warning: audit log unavailable", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

"""Translate full-repository OKF lint findings into Gemini hook decisions."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.common import convert_windows_path_to_posix, emit_json, read_json_input  # noqa: E402
from helpers.okf_audit import record as audit_record
from helpers.okf import diagnostic_line, is_diagnostic, one_line as _one_line, response_size, rerun_command, run_linter_process, sorted_diagnostics


MAX_PROVIDER_JSON_BYTES = 8_192
MAX_DIAGNOSTICS = 20
DIAGNOSTIC_ID = re.compile(r"^OKF[0-9]{3}$")


class LintFailure(Exception):
    """An untrustworthy lint result that must be surfaced as OKF900."""


def _repository_for_payload(payload: Mapping[str, Any]) -> Path:
    raw_cwd = payload.get("cwd") or payload.get("working_directory") or os.environ.get("GEMINI_CWD") or os.getcwd()
    if not isinstance(raw_cwd, str) or not raw_cwd.strip():
        raise LintFailure("payload cwd is missing or invalid")

    cwd = Path(convert_windows_path_to_posix(raw_cwd)).expanduser()
    if not cwd.is_dir():
        raise LintFailure("payload cwd does not name a directory")

    repository = SCRIPT_DIR.parents[2]
    try:
        cwd.resolve().relative_to(repository)
    except ValueError as error:
        raise LintFailure("payload cwd is outside the adapter checkout") from error
    return repository


def _validated_diagnostics(value: object) -> list[dict[str, object]]:
    if not isinstance(value, dict) or set(value) != {"schema_version", "diagnostics"}:
        raise LintFailure("linter returned an invalid JSON envelope")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise LintFailure("linter returned an unsupported JSON schema")
    diagnostics = value["diagnostics"]
    if not isinstance(diagnostics, list):
        raise LintFailure("linter JSON diagnostics must be a list")

    normalized: list[dict[str, object]] = []
    for item in diagnostics:
        if not isinstance(item, dict) or set(item) != {"id", "path", "line", "column", "message"}:
            raise LintFailure("linter JSON diagnostic must be an object")
        if not is_diagnostic(item, DIAGNOSTIC_ID, mapping_type=dict, exact_integer_type=False):
            raise LintFailure("linter JSON contains an invalid diagnostic")
        normalized.append(dict(item))
    return sorted_diagnostics(normalized)


def _run_linter(repository: Path) -> list[dict[str, object]]:
    linter = repository / "scripts" / "lint-okf.py"
    if not linter.is_file():
        raise LintFailure("scripts/lint-okf.py is unavailable")
    try:
        result = run_linter_process(repository)
    except subprocess.TimeoutExpired as error:
        raise LintFailure("scripts/lint-okf.py timed out after 8 seconds") from error
    except OSError as error:
        raise LintFailure(f"could not run scripts/lint-okf.py: {error}") from error

    if result.returncode == 2:
        raise LintFailure("scripts/lint-okf.py returned exit 2")
    if result.returncode not in {0, 1}:
        raise LintFailure(f"scripts/lint-okf.py returned unexpected exit {result.returncode}")
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise LintFailure("scripts/lint-okf.py returned invalid JSON") from error
    diagnostics = _validated_diagnostics(parsed)
    if result.returncode == 0 and diagnostics:
        raise LintFailure("scripts/lint-okf.py returned diagnostics with exit 0")
    if result.returncode == 1 and not diagnostics:
        raise LintFailure("scripts/lint-okf.py returned exit 1 without diagnostics")
    return diagnostics


def _rerun_command() -> str:
    return rerun_command()


def _bounded_text(value: str, limit: int) -> str:
    encoded = value.encode("utf-8")
    if len(encoded) <= limit:
        return value
    return encoded[: max(0, limit - 3)].decode("utf-8", errors="ignore") + "..."


def _serialized_response_size(payload: Mapping[str, Any] | None, reason: str) -> int:
    response = _response_for_failure(payload, reason)
    return response_size(response)


def _format_reason(payload: Mapping[str, Any], diagnostics: list[dict[str, object]]) -> str:
    header = f"OKF lint found {len(diagnostics)} diagnostic(s):"
    lines: list[str] = []
    for diagnostic in diagnostics[:MAX_DIAGNOSTICS]:
        lines.append(diagnostic_line(diagnostic, normalize_path=True, normalize_message=True))

    selected: list[str] = []
    for line in lines:
        omitted = len(diagnostics) - len(selected) - 1
        suffix = (f"{omitted} additional diagnostic(s) omitted.", f"Run: {_rerun_command()}")
        candidate = "\n".join((header, *selected, line, *suffix))
        if _serialized_response_size(payload, candidate) >= MAX_PROVIDER_JSON_BYTES:
            if not selected:
                low = 0
                high = len(line)
                while low < high:
                    midpoint = (low + high + 1) // 2
                    truncated = line[:midpoint] + ("..." if midpoint < len(line) else "")
                    candidate = "\n".join((header, truncated, *suffix))
                    if _serialized_response_size(payload, candidate) < MAX_PROVIDER_JSON_BYTES:
                        low = midpoint
                    else:
                        high = midpoint - 1
                selected.append(line[:low] + ("..." if low < len(line) else ""))
            break
        selected.append(line)

    omitted = len(diagnostics) - len(selected)
    reason = "\n".join((header, *selected, f"{omitted} additional diagnostic(s) omitted.", f"Run: {_rerun_command()}"))
    if _serialized_response_size(payload, reason) >= MAX_PROVIDER_JSON_BYTES:
        raise LintFailure("diagnostic output could not be safely bounded")
    return reason


def _okf900_reason(error: BaseException) -> str:
    detail = _bounded_text(_one_line(str(error)).strip() or "untrusted linter failure", 7_000)
    return f"lint-okf: incomplete; OKF900: {detail}\n0 additional diagnostic(s) omitted.\nRun: {_rerun_command()}"


def _response_for_failure(payload: Mapping[str, Any] | None, reason: str) -> dict[str, object]:
    event = "" if payload is None else str(payload.get("hook_event_name") or payload.get("hookEventName") or "")
    stop_hook_active = payload is not None and (payload.get("stop_hook_active") is True or payload.get("stopHookActive") is True)
    if event == "AfterAgent" and stop_hook_active:
        return {"continue": True, "systemMessage": "OKF unresolved after repair attempt.\n" + reason}
    if event in {"AfterTool", "AfterAgent"}:
        return {"decision": "deny", "reason": reason}
    return {"continue": False, "stopReason": reason}


def _emit_response(payload: Mapping[str, Any] | None, response: dict[str, object]) -> None:
    if response_size(response) >= MAX_PROVIDER_JSON_BYTES:
        reason = f"OKF900: response exceeded provider limit.\nRun: {_rerun_command()}"
        response = {"continue": True, "systemMessage": reason} if response.get("continue") is True else _response_for_failure(payload, reason)
    emit_json(response)


def main() -> int:
    payload: Mapping[str, Any] | None = None
    repository: Path | None = None
    outcome = "incomplete"
    findings = 0
    try:
        payload = read_json_input()
        repository = _repository_for_payload(payload)
        diagnostics = _run_linter(repository)
        findings = len(diagnostics)
        if not diagnostics:
            outcome = "pass"
            _emit_response(payload, {"systemMessage": "lint-okf: pass; 0 diagnostics"} if payload.get("hook_event_name") == "AfterAgent" else {})
            return 0

        outcome = "fail"
        reason = _format_reason(payload, diagnostics)
        if payload.get("hook_event_name") == "AfterAgent":
            retry = payload.get("stop_hook_active") is True or payload.get("stopHookActive") is True
            noun = "diagnostic" if len(diagnostics) == 1 else "diagnostics"
            reason = f"lint-okf: {'unresolved' if retry else 'blocked'}; {len(diagnostics)} {noun}\n" + reason
        _emit_response(payload, _response_for_failure(payload, reason))
        return 0
    except (LintFailure, ValueError) as error:
        if payload is not None and payload.get("hook_event_name") == "AfterAgent":
            _emit_response(payload, {"continue": True, "systemMessage": _okf900_reason(error)})
        else:
            _emit_response(payload, _response_for_failure(payload, _okf900_reason(error)))
        return 0
    except Exception as error:  # noqa: BLE001 - provider boundary must remain JSON-only.
        if payload is not None and payload.get("hook_event_name") == "AfterAgent":
            _emit_response(payload, {"continue": True, "systemMessage": _okf900_reason(error)})
        else:
            _emit_response(payload, _response_for_failure(payload, _okf900_reason(error)))
    finally:
        if repository is not None and payload is not None and payload.get("hook_event_name") == "AfterAgent":
            try:
                audit_record(repository, payload, outcome, findings, "gemini")
            except Exception:
                print("lint-okf warning: audit log unavailable", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

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
CHECKOUT_ROOT = SCRIPT_DIR.parents[2]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.common import convert_windows_path_to_posix, emit_json, first_present, read_json_input, run_command, stringify_value


MAX_DISPLAY_DIAGNOSTICS = 20
MAX_HOOK_OUTPUT_BYTES = 8192
DIAGNOSTIC_ID_RE = re.compile(r"OKF\d{3}\Z")


class LinterExecutionFailure(ValueError):
    def __init__(self, message: str, diagnostics: list[dict[str, Any]]) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics


def _event_name(payload: dict[str, object]) -> str:
    raw_event = stringify_value(first_present(payload, "hook_event_name", "hookEventName"))
    event_name = {
        "postToolUse": "postToolUse",
        "PostToolUse": "postToolUse",
        "agentStop": "agentStop",
        "Stop": "agentStop",
        "subagentStop": "subagentStop",
        "SubagentStop": "subagentStop",
    }.get(raw_event, raw_event)
    if event_name:
        return event_name
    if "toolName" in payload or "tool_name" in payload:
        return "postToolUse"
    return "agentStop"


def _repo_root(payload: dict[str, object]) -> Path:
    cwd = stringify_value(first_present(payload, "cwd", "workingDirectory", "working_directory"))
    if not cwd:
        raise ValueError("missing cwd")
    payload_cwd = Path(convert_windows_path_to_posix(cwd))
    if not payload_cwd.is_absolute():
        payload_cwd = CHECKOUT_ROOT / payload_cwd
    try:
        payload_cwd.resolve().relative_to(CHECKOUT_ROOT)
    except ValueError as error:
        raise ValueError("cwd is outside the checkout") from error
    return CHECKOUT_ROOT


def _response(event_name: str, reason: str) -> dict[str, str]:
    if event_name == "postToolUse":
        return {"additionalContext": reason}
    return {"decision": "block", "reason": reason}


def _clean_response(event_name: str) -> dict[str, str]:
    if event_name in {"agentStop", "subagentStop"}:
        return {"decision": "allow"}
    return {}


def _is_diagnostic(value: object) -> bool:
    if not isinstance(value, Mapping) or set(value) != {"id", "path", "line", "column", "message"}:
        return False
    return (
        isinstance(value["id"], str)
        and DIAGNOSTIC_ID_RE.fullmatch(value["id"]) is not None
        and isinstance(value["path"], str)
        and bool(value["path"])
        and type(value["line"]) is int
        and value["line"] >= 1
        and type(value["column"]) is int
        and value["column"] >= 1
        and isinstance(value["message"], str)
        and bool(value["message"])
    )


def _diagnostics_from_report(report: object) -> list[dict[str, Any]]:
    if not isinstance(report, Mapping) or set(report) != {"schema_version", "diagnostics"}:
        raise ValueError("invalid linter JSON envelope")
    if type(report["schema_version"]) is not int or report["schema_version"] != 1 or not isinstance(report["diagnostics"], list):
        raise ValueError("invalid linter JSON schema")
    diagnostics = report["diagnostics"]
    if not all(_is_diagnostic(item) for item in diagnostics):
        raise ValueError("invalid linter diagnostic")
    return sorted(
        (dict(item) for item in diagnostics),
        key=lambda item: (item["path"], item["line"], item["column"], item["id"]),
    )


def _rerun_command() -> str:
    platform = os.environ.get("OKF_LINT_TEST_PLATFORM")
    if platform == "windows" or (platform is None and os.name == "nt"):
        return "python scripts/lint-okf.py"
    return "./scripts/lint-okf.py"


def _response_size(event_name: str, reason: str) -> int:
    return len(json.dumps(_response(event_name, reason), ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _omitted_diagnostics_line(omitted: int) -> str:
    return f"{omitted} additional diagnostics omitted."


def _format_diagnostics(event_name: str, diagnostics: list[dict[str, Any]]) -> str:
    rendered = [
        f"{item['path']}:{item['line']}:{item['column']}: {item['id']} {item['message']}"
        for item in diagnostics[:MAX_DISPLAY_DIAGNOSTICS]
    ]
    for displayed in range(len(rendered), -1, -1):
        omitted = len(diagnostics) - displayed
        lines = ["OKF validation failed:", *rendered[:displayed]]
        lines.append(_omitted_diagnostics_line(omitted))
        lines.extend((f"Rerun: {_rerun_command()}", ""))
        reason = "\n".join(lines)
        if _response_size(event_name, reason) < MAX_HOOK_OUTPUT_BYTES:
            return reason
    raise ValueError("unable to format bounded diagnostics")


def _okf900_response(event_name: str, omitted_diagnostics: int) -> dict[str, str]:
    return _response(
        event_name,
        "\n".join(
            (
                "OKF900: unable to run OKF validation.",
                _omitted_diagnostics_line(omitted_diagnostics),
                f"Rerun: {_rerun_command()}",
            )
        ),
    )


def _run_linter(repo_root: Path) -> list[dict[str, Any]]:
    linter = repo_root / "scripts" / "lint-okf.py"
    if not linter.is_file():
        raise ValueError("missing scripts/lint-okf.py")
    result = run_command(
        [sys.executable, str(linter), "--format", "json"],
        cwd=str(repo_root),
        capture_output=True,
        timeout=8,
    )
    diagnostics = _diagnostics_from_report(json.loads(result.stdout))
    if result.returncode == 0:
        if diagnostics:
            raise LinterExecutionFailure("clean linter exit included diagnostics", diagnostics)
        return []
    if result.returncode == 1:
        if not diagnostics:
            raise LinterExecutionFailure("finding linter exit omitted diagnostics", diagnostics)
        return diagnostics
    if result.returncode == 2:
        raise LinterExecutionFailure("linter exited 2", diagnostics)
    raise LinterExecutionFailure(f"unexpected linter exit {result.returncode}", diagnostics)


def _emit_response(event_name: str, response: dict[str, str], omitted_diagnostics: int = 0) -> None:
    encoded = json.dumps(response, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) >= MAX_HOOK_OUTPUT_BYTES:
        response = _response(
            event_name,
            "\n".join(
                (
                    "OKF validation failed. Diagnostics were truncated.",
                    _omitted_diagnostics_line(omitted_diagnostics),
                    f"Rerun: {_rerun_command()}",
                )
            ),
        )
    emit_json(response)


def main() -> int:
    event_name = ""
    diagnostics: list[dict[str, Any]] | None = None
    try:
        payload = read_json_input()
        event_name = _event_name(payload)
        repo_root = _repo_root(payload)
        diagnostics = _run_linter(repo_root)
        if not diagnostics:
            _emit_response(event_name, _clean_response(event_name))
            return 0
        _emit_response(event_name, _response(event_name, _format_diagnostics(event_name, diagnostics)), len(diagnostics))
    except LinterExecutionFailure as error:
        _emit_response(event_name, _okf900_response(event_name, len(error.diagnostics)), len(error.diagnostics))
    except (Exception, subprocess.TimeoutExpired):
        omitted_diagnostics = len(diagnostics) if diagnostics is not None else 0
        _emit_response(
            event_name,
            _okf900_response(event_name, omitted_diagnostics),
            omitted_diagnostics,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# Generated from hooks/families/okf.py by scripts/generate-hooks.py. Do not edit.
"""Neutral OKF transport and diagnostic mechanics, without provider decisions."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .common import run_command


DIAGNOSTIC_FIELDS = {"id", "path", "line", "column", "message"}


def _valid_position(value: object, exact_integer_type: bool) -> bool:
    if not isinstance(value, int) or isinstance(value, bool):
        return False
    return (not exact_integer_type or type(value) is int) and value >= 1


def is_diagnostic(
    value: object, identifier: re.Pattern[str], *, mapping_type: type = Mapping, exact_integer_type: bool = True,
) -> bool:
    if not isinstance(value, Mapping) or not isinstance(value, mapping_type) or set(value) != DIAGNOSTIC_FIELDS:
        return False
    return (
        isinstance(value["id"], str)
        and identifier.fullmatch(value["id"]) is not None
        and isinstance(value["path"], str)
        and bool(value["path"])
        and _valid_position(value["line"], exact_integer_type)
        and _valid_position(value["column"], exact_integer_type)
        and isinstance(value["message"], str)
        and bool(value["message"])
    )


def sorted_diagnostics(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(values, key=lambda item: (item["path"], item["line"], item["column"], item["id"]))


def run_linter_process(root: Path) -> subprocess.CompletedProcess[str]:
    return run_command(
        [sys.executable, str(root / "scripts" / "lint-okf.py"), "--format", "json"],
        cwd=str(root), capture_output=True, timeout=8,
    )


def rerun_command() -> str:
    platform = os.environ.get("OKF_LINT_TEST_PLATFORM")
    return "python scripts/lint-okf.py" if platform == "windows" or (platform is None and os.name == "nt") else "./scripts/lint-okf.py"


def response_size(value: Mapping[str, Any]) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def one_line(value: str) -> str:
    return " ".join(value.splitlines())


def diagnostic_line(value: Mapping[str, Any], *, normalize_path: bool = False, normalize_message: bool = False) -> str:
    path = one_line(str(value["path"])) if normalize_path else str(value["path"])
    message = one_line(str(value["message"])) if normalize_message else str(value["message"])
    return f"{path}:{value['line']}:{value['column']}: {value['id']} {message}"

#!/usr/bin/env python3
# Generated from hooks/families/rtk.py by scripts/generate-hooks.py. Do not edit.
"""Rewrite explicit RTK shell invocations only when a verified prerelease is installed."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.common import emit_json, read_json_input

PROVIDER = "gemini"
APPROVED_ASSET_DIGESTS = {
    "05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321",
    "10345f57214b2f9a14f3de1ae1f4235f6eef0669dfed9ab1758a94601b7b829a",
    "4993afdf43a93d09dcce1bef0b0167464f96aa9e973fa5644ca244604a1846b8",
    "bf8a1d0e44afb28db9e88859e1f7668c56ecd074264f0c36637c4e07a0c2f1db",
    "636262ec8341455c09a3826329f90c92a57e2ef64d8761511eb123f1b84642d7",
}


def verified(binary: Path) -> bool:
    try:
        receipt = json.loads((binary.parent / "receipt.json").read_text(encoding="utf-8"))
        return (receipt.get("tag") == "dev-0.50.0-rc.451"
                and receipt.get("asset_sha256") in APPROVED_ASSET_DIGESTS
                and hashlib.sha256(binary.read_bytes()).hexdigest() == receipt.get("binary_sha256"))
    except (OSError, ValueError):
        return False


def split_segments(command: str, powershell: bool) -> list[tuple[int, int]] | None:
    if "`" in command or "$(" in command or "\n" in command or "\r" in command:
        return None
    segments = []
    quote = None
    escaped = False
    start = 0
    index = 0
    while index < len(command):
        char = command[index]
        if escaped:
            escaped = False
        elif char == "\\" and quote != "'":
            escaped = True
        elif quote:
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char in ";&|":
            if command.startswith("&&", index) or command.startswith("||", index):
                segments.append((start, index))
                index += 1
                start = index + 1
            elif char == ";":
                segments.append((start, index))
                start = index + 1
            elif powershell and char == "&" and not command[start:index].strip():
                pass
            else:
                return None
        index += 1
    if quote or escaped:
        return None
    segments.append((start, len(command)))
    return segments


def command_token(command: str, start: int, end: int, powershell: bool) -> tuple[int, int, str, bool] | None:
    while start < end and command[start].isspace():
        start += 1
    called = False
    if powershell and command[start:start + 1] == "&":
        called = True
        start += 1
        while start < end and command[start].isspace():
            start += 1
    if start >= end:
        return None
    token_start = start
    quote = None
    escaped = False
    while start < end:
        char = command[start]
        if escaped:
            escaped = False
        elif char == "\\" and not powershell and quote != "'":
            escaped = True
        elif quote:
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char.isspace():
            break
        start += 1
    token = command[token_start:start]
    if token.startswith(("'", '"')) and token[-1:] == token[:1]:
        token = token[1:-1]
    return token_start, start, token, called


def rewrite(command: str, powershell: bool) -> str | None:
    segments = split_segments(command, powershell)
    if segments is None:
        return None
    launcher = SCRIPT_DIR / "rtk-agent-launcher.py"
    if powershell:
        quoted = "'" + str(launcher).replace("'", "''") + "'"
        replacement = f"python {quoted}"
    else:
        import shlex
        replacement = "python3 " + shlex.quote(str(launcher))
    changes = []
    for start, end in segments:
        found = command_token(command, start, end, powershell)
        if found is None:
            continue
        token_start, token_end, token, called = found
        basename = re.split(r"[/\\]", token)[-1]
        if basename != "rtk" and not (powershell and basename.lower() == "rtk.exe"):
            continue
        changes.append((token_start, token_end, ("" if called or not powershell else "& ") + replacement))
    if not changes:
        return None
    for start, end, replacement in reversed(changes):
        command = command[:start] + replacement + command[end:]
    return command


def main() -> int:
    try:
        payload = read_json_input()
        if PROVIDER == "copilot":
            tool = payload.get("toolName") or payload.get("tool_name")
            args = payload.get("toolArgs") if "toolArgs" in payload else payload.get("tool_input")
            if isinstance(args, str):
                args = json.loads(args)
            powershell = tool == "powershell" or (tool == "Bash" and os.name == "nt")
            supported = tool in ("bash", "powershell", "Bash")
        else:
            tool = payload.get("tool_name")
            args = payload.get("tool_input")
            powershell = os.name == "nt"
            supported = tool == ("run_shell_command" if PROVIDER == "gemini" else "Bash")
        if not supported or not isinstance(args, dict) or not isinstance(args.get("command"), str):
            emit_json({})
            return 0
        binary = Path.home() / ".agents/rtk/dev-0.50.0-rc.451" / ("rtk.exe" if powershell else "rtk")
        if not binary.is_file() or not verified(binary):
            emit_json({})
            return 0
        updated = rewrite(args["command"], powershell)
        if updated is None:
            emit_json({})
            return 0
        new_args = args | {"command": updated}
        if PROVIDER == "copilot" and "toolArgs" in payload:
            output = {"modifiedArgs": new_args}
        elif PROVIDER == "gemini":
            output = {"hookSpecificOutput": {"tool_input": new_args}}
        else:
            output = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", "updatedInput": new_args}}
        emit_json(output)
    except Exception:
        emit_json({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

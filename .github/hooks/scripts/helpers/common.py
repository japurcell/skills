from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Sequence


def read_json_input() -> dict:
    raw_input = sys.stdin.read()

    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid hook input: expected a JSON object") from exc

    if not isinstance(payload, dict):
        raise ValueError("Invalid hook input: expected a JSON object")

    return payload


def emit_json(payload: dict) -> None:
    try:
        sys.stdout.buffer.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        sys.stdout.buffer.flush()
    except Exception:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        sys.stdout.write("\n")
        sys.stdout.flush()


def sanitize_log_field(value: object) -> str:
    return str(value or "").translate({ord("\r"): " ", ord("\n"): " ", ord("\t"): " "})


def first_present(payload: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return ""


def nested_present(payload: Mapping[str, Any], *keys: str) -> Any:
    current: Any = payload

    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return ""
        current = current[key]

    return current if current is not None else ""


def convert_windows_path_to_posix(path_str: str) -> str:
    if not path_str:
        return ""
    if os.name == "nt":
        return path_str.replace("/", "\\")

    if len(path_str) >= 2 and path_str[1] == ":" and path_str[0].isalpha():
        drive = path_str[0].lower()
        rest = path_str[2:].replace("\\", "/")
        if not rest.startswith("/"):
            rest = "/" + rest

        if os.path.exists(f"/mnt/{drive}"):
            return f"/mnt/{drive}{rest}"
        elif os.path.exists(f"/{drive}"):
            return f"/{drive}{rest}"
        else:
            return f"/mnt/{drive}{rest}"

    if "\\" in path_str:
        return path_str.replace("\\", "/")

    return path_str


def stringify_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    if isinstance(value, (dict, list, bool, int, float)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def trim_ws(value: str) -> str:
    return value.strip()


def resolve_skill_file_path(skill_file: str, skills_dir: str, home: str | None) -> str:
    if not skill_file:
        raise ValueError("Skill file path is empty")

    normalized = skill_file
    if os.name != "nt" and len(skill_file) >= 2 and skill_file[1] == ":" and skill_file[0].isalpha():
        normalized = convert_windows_path_to_posix(skill_file)

    if normalized.startswith("~/"):
        if not home:
            raise ValueError("Cannot expand ~/: HOME is not set")
        return str(Path(home, normalized[2:]))

    path = Path(normalized)
    if not path.is_absolute():
        return str(Path(skills_dir, path))

    return str(path)


def merge_env_skill_files(raw: str | None, skills_dir: str, home: str | None) -> list[str]:
    if not raw:
        return []

    import os
    import re

    if os.name == "nt":
        parts = re.split(r"[\r\n,;]", raw)
    else:
        parts = re.split(r"[\r\n,;]|(?<!\b[a-zA-Z]):", raw)

    resolved: list[str] = []

    for part in parts:
        item = trim_ws(part)
        if not item:
            continue

        resolved_path = resolve_skill_file_path(item, skills_dir, home)
        if resolved_path not in resolved:
            resolved.append(resolved_path)

    return resolved


def strip_yaml_frontmatter(text: str) -> str:
    lines = text.splitlines()
    body: list[str] = []
    in_header = False
    first_line = True

    for line in lines:
        if first_line:
            first_line = False
            if line == "---":
                in_header = True
                continue

        if in_header:
            if line == "---":
                in_header = False
            continue

        body.append(line)

    return "\n".join(body)


def run_command(
    args: Sequence[str],
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    check: bool = False,
    capture_output: bool = False,
    text: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    if isinstance(args, (str, bytes)):
        raise TypeError("run_command requires a sequence of arguments; shell execution is disabled")

    return subprocess.run(
        list(args),
        cwd=cwd,
        env=env,
        check=check,
        capture_output=capture_output,
        text=text,
        timeout=timeout,
        shell=False,
    )

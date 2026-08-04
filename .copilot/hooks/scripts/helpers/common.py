from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence


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
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.write("\n")
    sys.stdout.flush()


def sanitize_log_field(value: object) -> str:
    return str(value or "").translate({ord("\r"): " ", ord("\n"): " ", ord("\t"): " "})


def trim_ws(value: str) -> str:
    return value.strip()


def resolve_skill_file_path(skill_file: str, skills_dir: str, home: str | None) -> str:
    if not skill_file:
        raise ValueError("Skill file path is empty")

    if skill_file.startswith("~/"):
        if not home:
            raise ValueError("Cannot expand ~/: HOME is not set")
        return str(Path(home, skill_file[2:]))

    path = Path(skill_file)
    if not path.is_absolute():
        return str(Path(skills_dir, path))

    return str(path)


def merge_env_skill_files(raw: str | None, skills_dir: str, home: str | None) -> list[str]:
    if not raw:
        return []

    normalized = raw.replace("\r", "\n").replace(":", "\n").replace(",", "\n")
    resolved: list[str] = []

    for line in normalized.splitlines():
        item = trim_ws(line)
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

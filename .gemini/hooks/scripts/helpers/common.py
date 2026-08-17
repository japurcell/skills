from __future__ import annotations

import json
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

    try:
        from .observability import begin_hook_capture

        begin_hook_capture(payload)
    except Exception:
        pass

    return payload


def emit_json(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.write("\n")
    sys.stdout.flush()

    try:
        from .observability import complete_hook_capture

        complete_hook_capture(payload)
    except Exception:
        pass


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


def run_gemini_passive_log_hook(script_name: str, build_log_message_func) -> int:
    from .audit import audit_init, audit_log_passive_event

    def noop() -> None:
        emit_json({})
        raise SystemExit(0)

    try:
        input_payload = read_json_input()

        if not isinstance(input_payload, dict):
            noop()

        if not audit_init():
            noop()

        log_string = build_log_message_func(input_payload)

        if log_string and not audit_log_passive_event(script_name, log_string):
            noop()

        noop()
    except ValueError as exc:
        print(f"{script_name}: {exc}", file=sys.stderr)
        noop()
    except Exception as exc:  # noqa: BLE001
        print(f"{script_name}: unexpected error: {exc}", file=sys.stderr)
        noop()
    return 0

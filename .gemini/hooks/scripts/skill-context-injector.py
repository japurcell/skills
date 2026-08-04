#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_init, audit_log_event  # noqa: E402
from helpers.common import (  # noqa: E402
    emit_json,
    merge_env_skill_files,
    read_json_input,
    sanitize_log_field,
    strip_yaml_frontmatter,
)


SCRIPT_NAME = Path(__file__).name


def hard_stop(reason: str) -> None:
    message = reason.strip() or "Hook failed"
    print(f"Hook hard stop: {message}", file=sys.stderr)
    emit_json({"continue": False, "stopReason": message, "suppressOutput": True})
    raise SystemExit(0)


def build_output(context_payload: str, event_name: str, count: int) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": context_payload,
        },
        "systemMessage": f"Required skill context loaded from {count} file(s).",
        "suppressOutput": True,
    }


def parse_skill_context(skill_file: Path) -> str:
    return strip_yaml_frontmatter(skill_file.read_text(encoding="utf-8"))


def main() -> int:
    try:
        input_payload = read_json_input()
        event_name = str(input_payload.get("hook_event_name") or "")
        if not event_name:
            hard_stop("Missing required field: hook_event_name")

        if event_name not in {"SessionStart", "BeforeAgent", "AfterTool"}:
            hard_stop(f"Unsupported hook event for context injection: {event_name}")

        session_id = str(input_payload.get("session_id") or "")
        timestamp = str(input_payload.get("timestamp") or "")
        cwd = str(input_payload.get("cwd") or "")

        if not audit_init():
            hard_stop("audit_init failed")

        safe_session_id = sanitize_log_field(session_id)
        safe_timestamp = sanitize_log_field(timestamp)
        safe_event_name = sanitize_log_field(event_name)
        safe_cwd = sanitize_log_field(cwd)

        if not audit_log_event(
            SCRIPT_NAME,
            f"[{safe_timestamp}] Hook: {safe_event_name}, CWD: {safe_cwd}, Session: {safe_session_id}",
        ):
            hard_stop("Failed to write initial audit event")

        skills_dir = (
            os.environ.get("AGENTS_SKILLS_DIR")
            or os.environ.get("COPILOT_SKILLS_DIR")
            or str(Path.home() / ".agents" / "skills")
        )
        home = os.environ.get("HOME")

        required_skill_files = merge_env_skill_files(
            os.environ.get("AGENTS_REQUIRED_SKILL_FILES"),
            skills_dir,
            home,
        )

        if not required_skill_files:
            if not audit_log_event(
                SCRIPT_NAME,
                f"[{safe_timestamp}] Message: No skills loaded, Hook: {safe_event_name}, CWD: {safe_cwd}, Session: {safe_session_id}",
            ):
                hard_stop("Failed to write audit event")

            emit_json({"systemMessage": "No skills loaded", "suppressOutput": True})
            return 0

        context_parts: list[str] = []

        for raw_skill_file in required_skill_files:
            skill_path = Path(raw_skill_file)
            if not skill_path.exists():
                hard_stop(f"Required skill file not found: {raw_skill_file}")
            if not skill_path.is_file():
                hard_stop(f"Required skill file not found: {raw_skill_file}")
            if not os.access(skill_path, os.R_OK):
                hard_stop(f"Required skill file not readable: {raw_skill_file}")

            try:
                skill_context = parse_skill_context(skill_path)
            except OSError as exc:
                hard_stop(f"Failed to read skill file: {raw_skill_file} ({exc})")

            context_parts.append(
                f"<!-- BEGIN REQUIRED SKILL: {raw_skill_file} -->\n"
                f"{skill_context}\n"
                f"<!-- END REQUIRED SKILL: {raw_skill_file} -->"
            )

            if not audit_log_event(
                SCRIPT_NAME,
                f"[{safe_timestamp}] Message: loaded required skill file: {sanitize_log_field(raw_skill_file)}, Hook: {safe_event_name}, CWD: {safe_cwd}, Session: {safe_session_id}",
            ):
                hard_stop(f"Failed to write audit event for loaded skill: {raw_skill_file}")

        emit_json(build_output("\n\n".join(context_parts), event_name, len(required_skill_files)))
        return 0
    except ValueError as exc:
        hard_stop(str(exc))
    except Exception as exc:  # noqa: BLE001 - top-level fallback
        hard_stop(f"Unexpected exception: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

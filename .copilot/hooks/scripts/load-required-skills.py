#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path

from helpers.audit import audit_log_event
from helpers.common import (
    emit_json,
    merge_env_skill_files,
    read_json_input,
    sanitize_log_field,
    strip_yaml_frontmatter,
)


SCRIPT_NAME = Path(__file__).name


def build_output(message: str, event_name: str, is_failure: bool) -> dict:
    payload = {
        "systemMessage": "Required skill context was NOT loaded." if is_failure else None,
        "additionalContext": message,
    }
    if payload["systemMessage"] is None:
        payload.pop("systemMessage")

    if event_name in {"SessionStart", "SubagentStart"}:
        payload["hookSpecificOutput"] = {
            "hookEventName": event_name,
            "additionalContext": message,
        }

    return payload


def fail_with_context(reason: str, event_name: str = "") -> None:
    safe_reason = reason.strip() or "Hook failed"
    safe_session_id = sanitize_log_field(SESSION_ID)

    print(f"Copilot/VS Code hook failure: {safe_reason}", file=sys.stderr)
    audit_log_event(
        SCRIPT_NAME,
        f"Error: {sanitize_log_field(safe_reason)}, Session: {safe_session_id}",
    )
    emit_json(
        build_output(
            "Required skill context was NOT loaded.\n\n"
            f"Reason: {safe_reason}\n\n"
            "Instruction to agent: stop normal work, tell the user this hook failed, "
            "and ask them to fix the hook or required skill files before proceeding.",
            event_name,
            True,
        )
    )
    raise SystemExit(0)


def parse_skill_context(skill_file: Path) -> str:
    return strip_yaml_frontmatter(skill_file.read_text(encoding="utf-8"))


def main() -> int:
    global SESSION_ID

    try:
        input_payload = read_json_input()
        if not isinstance(input_payload, dict):
            fail_with_context("Invalid hook input: expected a JSON object")

        event_name = str(
            input_payload.get("hook_event_name")
            or input_payload.get("hookEventName")
            or ""
        )
        SESSION_ID = str(input_payload.get("sessionId") or input_payload.get("session_id") or "")

        skills_dir = (
            os.environ.get("COPILOT_SKILLS_DIR")
            or os.environ.get("AGENTS_SKILLS_DIR")
            or str(Path.home() / ".agents" / "skills")
        )
        home = os.environ.get("HOME")

        required_skill_files = merge_env_skill_files(
            os.environ.get("AGENTS_REQUIRED_SKILL_FILES"),
            skills_dir,
            home,
        )

        safe_session_id = sanitize_log_field(SESSION_ID)

        if not required_skill_files:
            audit_log_event(
                SCRIPT_NAME,
                f"Message: No skills loaded, Event: {event_name}, Session: {safe_session_id}",
            )
            emit_json({"systemMessage": "No skills loaded"})
            return 0

        context_parts: list[str] = []

        for raw_skill_file in required_skill_files:
            skill_path = Path(raw_skill_file)
            if not skill_path.exists():
                fail_with_context(f"Required skill file not found: {raw_skill_file}", event_name)
            if not skill_path.is_file():
                fail_with_context(f"Required skill file not found: {raw_skill_file}", event_name)
            if not os.access(skill_path, os.R_OK):
                fail_with_context(f"Required skill file not readable: {raw_skill_file}", event_name)

            try:
                skill_context = parse_skill_context(skill_path)
            except OSError as exc:
                fail_with_context(f"Failed to read skill file: {raw_skill_file} ({exc})", event_name)

            context_parts.append(f"<!-- BEGIN REQUIRED SKILL: {raw_skill_file} -->\n{skill_context}\n<!-- END REQUIRED SKILL: {raw_skill_file} -->")

            audit_log_event(
                SCRIPT_NAME,
                f"Message: Loaded skill {sanitize_log_field(raw_skill_file)}, Event: {event_name}, Session: {safe_session_id}",
            )

        required_skill_context = "Required skill context loaded.\n\n" + "\n\n".join(context_parts)
        emit_json(build_output(required_skill_context, event_name, False))
        return 0
    except ValueError as exc:
        fail_with_context(str(exc))
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        fail_with_context(f"Unexpected exception: {exc}", "")
    return 0


if __name__ == "__main__":
    SESSION_ID = ""
    raise SystemExit(main())


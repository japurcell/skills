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
    load_required_skill_context,
)


SCRIPT_NAME = Path(__file__).name


def build_output(message: str, event_name: str, is_failure: bool) -> dict:
    payload = {
        "systemMessage": "load-required-skills: blocked; required context unavailable" if is_failure else None,
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


def emit_progress_message(message: str) -> None:
    emit_json({"type": "progress", "message": message})


def supports_progress_messages(event_name: str) -> bool:
    return event_name in {"", "sessionStart", "subagentStart"}


def fail_with_context(reason: str, session_id: str = "", event_name: str = "") -> None:
    safe_reason = reason.strip() or "Hook failed"
    safe_session_id = sanitize_log_field(session_id)

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


def main() -> int:
    session_id = ""
    try:
        input_payload = read_json_input()
        if not isinstance(input_payload, dict):
            fail_with_context("Invalid hook input: expected a JSON object", session_id)

        event_name = str(
            input_payload.get("hook_event_name")
            or input_payload.get("hookEventName")
            or ""
        )
        session_id = str(input_payload.get("sessionId") or input_payload.get("session_id") or "")

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

        safe_session_id = sanitize_log_field(session_id)

        if not required_skill_files:
            audit_log_event(
                SCRIPT_NAME,
                f"Message: No skills loaded, Event: {event_name}, Session: {safe_session_id}",
            )
            emit_json({"systemMessage": "load-required-skills: pass; 0 skill files"})
            return 0

        context_parts: list[str] = []

        for raw_skill_file in required_skill_files:
            context_parts.append(load_required_skill_context(raw_skill_file, lambda reason: fail_with_context(reason, session_id, event_name)))

            audit_log_event(
                SCRIPT_NAME,
                f"Message: Loaded skill {sanitize_log_field(raw_skill_file)}, Event: {event_name}, Session: {safe_session_id}",
            )

        count = len(required_skill_files)
        if supports_progress_messages(event_name):
            emit_progress_message(f"load-required-skills: pass; {count} skill {'file' if count == 1 else 'files'}")
        required_skill_context = "Required skill context loaded.\n\n" + "\n\n".join(context_parts)
        emit_json(build_output(required_skill_context, event_name, False))
        return 0
    except ValueError as exc:
        fail_with_context(str(exc), session_id)
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        fail_with_context(f"Unexpected exception: {exc}", session_id, "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

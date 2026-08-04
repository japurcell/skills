from __future__ import annotations

import fcntl
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from .common import first_present, stringify_value


OBSERVABILITY_RUNTIME = "gemini"
OBSERVABILITY_LOG_NAME = "observability.ndjson"
OBSERVABILITY_DEFAULT_LOCK_WAIT_MS = 50
OBSERVABILITY_DEFAULT_MAX_RECORD_BYTES = 8192
OBSERVABILITY_DEFAULT_MAX_STRING_CHARS = 1024
OBSERVABILITY_DEFAULT_MAX_ITEMS = 32

SECRET_FIELD_NAMES = {
    "access_key",
    "apikey",
    "api_key",
    "authorization",
    "client_secret",
    "password",
    "passphrase",
    "private_key",
    "refresh_token",
    "secret",
    "token",
}

TOKEN_PATTERNS = (
    re.compile(r"gh[pousr]_[A-Za-z0-9]{36}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk_live_[0-9A-Za-z]{16,}"),
    re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}"),
)

SOURCE_EVENT_NAME_MAP = {
    "send-event.py": "send-event",
    "log-session-start.py": "SessionStart",
    "skill-context-injector.py": "SessionStart",
    "log-after-agent.py": "AfterAgent",
    "log-notification.py": "Notification",
    "log-session-end.py": "SessionEnd",
}

TERMINAL_EVENT_NAMES = {"session_end", "subagent_stop"}

_STATE: dict[str, Any] = {}


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _truthy_env(*names: str) -> bool:
    return any(_truthy(os.environ.get(name)) for name in names)


def _disabled() -> bool:
    return _truthy_env("GEMINI_OBSERVABILITY_DISABLE", "OBSERVABILITY_DISABLE")


def _capture_event_enabled() -> bool:
    return _truthy_env("OBSERVABILITY_CAPTURE_EVENT", "GEMINI_OBSERVABILITY_CAPTURE_EVENT")


def _include_transcript() -> bool:
    return _truthy_env("OBSERVABILITY_INCLUDE_TRANSCRIPT", "GEMINI_OBSERVABILITY_INCLUDE_TRANSCRIPT")


def _log_path() -> Path:
    override = os.environ.get("GEMINI_OBSERVABILITY_LOG_PATH") or os.environ.get("OBSERVABILITY_LOG_PATH")
    if override:
        return Path(override)
    return Path.home() / ".gemini" / "hooks" / "logs" / OBSERVABILITY_LOG_NAME


def _lock_path(log_path: Path) -> Path:
    return Path(f"{log_path}.lock")


def _lock_wait_seconds(value: str | None) -> float:
    try:
        milliseconds = max(1, int(float(value or str(OBSERVABILITY_DEFAULT_LOCK_WAIT_MS))))
    except ValueError:
        milliseconds = OBSERVABILITY_DEFAULT_LOCK_WAIT_MS
    return milliseconds / 1000.0


def _lock_wait_ms() -> str | None:
    return os.environ.get("GEMINI_OBSERVABILITY_LOCK_WAIT_MS") or os.environ.get("OBSERVABILITY_LOCK_WAIT_MS")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _acquire_lock(lock_path: Path, timeout_seconds: float) -> int | None:
    _ensure_parent(lock_path)
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    deadline = time.monotonic() + timeout_seconds

    while True:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return lock_fd
        except BlockingIOError:
            if time.monotonic() >= deadline:
                os.close(lock_fd)
                return None
            time.sleep(0.01)
        except OSError:
            os.close(lock_fd)
            return None


def _append_record(path: Path, record: dict[str, Any]) -> None:
    _ensure_parent(path)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def _sanitize_string(value: str, *, key: str | None = None) -> str:
    lowered_key = (key or "").replace("-", "_").lower()
    if lowered_key in SECRET_FIELD_NAMES:
        return "[REDACTED]"
    if lowered_key in {"transcript", "transcript_path"} and not _include_transcript():
        return "[TRANSCRIPT OMITTED]"

    sanitized = value.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    for pattern in TOKEN_PATTERNS:
        sanitized = pattern.sub(lambda match: f"{match.group(0)[:4]}...{match.group(0)[-4:]}", sanitized)
    if len(sanitized) > OBSERVABILITY_DEFAULT_MAX_STRING_CHARS:
        cap = OBSERVABILITY_DEFAULT_MAX_STRING_CHARS
        omitted = len(sanitized) - cap
        marker = f"...[capped {omitted} chars]..."
        head = max(0, cap - len(marker))
        sanitized = f"{sanitized[:head]}{marker}"
    return sanitized


def _sanitize_value(value: Any, *, key: str | None = None, depth: int = 0) -> Any:
    if depth > 4:
        return "[CAPPED]"

    if isinstance(value, str):
        return _sanitize_string(value, key=key)
    if isinstance(value, bytes):
        return _sanitize_string(value.decode("utf-8", errors="replace"), key=key)
    if isinstance(value, Mapping):
        items: dict[str, Any] = {}
        for index, (child_key, child_value) in enumerate(value.items()):
            if index >= OBSERVABILITY_DEFAULT_MAX_ITEMS:
                items["_capped"] = True
                items["_capped_items"] = max(0, len(value) - OBSERVABILITY_DEFAULT_MAX_ITEMS)
                break
            child_key_text = str(child_key)
            items[child_key_text] = _sanitize_value(child_value, key=child_key_text, depth=depth + 1)
        return items
    if isinstance(value, list):
        sanitized = [_sanitize_value(item, key=key, depth=depth + 1) for item in value[:OBSERVABILITY_DEFAULT_MAX_ITEMS]]
        if len(value) > OBSERVABILITY_DEFAULT_MAX_ITEMS:
            sanitized.append(
                {
                    "_capped": True,
                    "_capped_items": len(value) - OBSERVABILITY_DEFAULT_MAX_ITEMS,
                }
            )
        return sanitized
    if isinstance(value, tuple):
        return [_sanitize_value(item, key=key, depth=depth + 1) for item in value]
    return value


def _current_hook_name() -> str:
    return Path(sys.argv[0]).name or "unknown"


def _source_event_name(hook_name: str, payload: Mapping[str, Any]) -> str:
    override = os.environ.get("OBSERVABILITY_SOURCE_EVENT_NAME") or os.environ.get("GEMINI_OBSERVABILITY_SOURCE_EVENT_NAME")
    if override:
        return override

    candidate = first_present(payload, "hook_event_name", "hookEventName", "source_event_name", "sourceEventName")
    if candidate:
        return stringify_value(candidate)

    return SOURCE_EVENT_NAME_MAP.get(hook_name, hook_name.removesuffix(".py"))


def _canonical_event_name(source_event_name: str) -> str:
    normalized = source_event_name.replace("-", "_")
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = re.sub(r"__+", "_", normalized)
    return normalized.strip("_").lower()


def _timestamp(payload: Mapping[str, Any]) -> str:
    timestamp = stringify_value(first_present(payload, "timestamp", "time"))
    if timestamp:
        return timestamp
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _session_id(payload: Mapping[str, Any]) -> str:
    return stringify_value(first_present(payload, "session_id", "sessionId"))


def _cwd(payload: Mapping[str, Any]) -> str:
    return stringify_value(first_present(payload, "cwd", "workingDirectory", "working_directory"))


def _agent_id(payload: Mapping[str, Any]) -> str:
    return stringify_value(first_present(payload, "agent_id", "agentId", "agentID"))


def _agent_type(payload: Mapping[str, Any]) -> str:
    return stringify_value(first_present(payload, "agent_type", "agentType", "agent_name", "agentName"))


def _tool_name(payload: Mapping[str, Any]) -> str:
    return stringify_value(first_present(payload, "tool_name", "toolName"))


def _notification_type(payload: Mapping[str, Any]) -> str:
    return stringify_value(first_present(payload, "notification_type", "notificationType"))


def _decision(payload: Mapping[str, Any]) -> str:
    return stringify_value(first_present(payload, "decision"))


def _reason(payload: Mapping[str, Any]) -> str:
    return stringify_value(first_present(payload, "reason"))


def _stop_hook_active(payload: Mapping[str, Any]) -> str:
    return stringify_value(first_present(payload, "stop_hook_active", "stopHookActive"))


def _promoted_fields(payload: Mapping[str, Any]) -> dict[str, Any]:
    promoted: dict[str, Any] = {}
    for key, value in (
        ("session_id", _session_id(payload)),
        ("agent_id", _agent_id(payload)),
        ("agent_type", _agent_type(payload)),
        ("tool_name", _tool_name(payload)),
        ("notification_type", _notification_type(payload)),
        ("decision", _decision(payload)),
        ("reason", _reason(payload)),
        ("stop_hook_active", _stop_hook_active(payload)),
        ("cwd", _cwd(payload)),
    ):
        if value:
            promoted[key] = value

    transcript_path = stringify_value(first_present(payload, "transcript_path", "transcriptPath"))
    if transcript_path:
        promoted["transcript_path"] = transcript_path

    return promoted


def _derive_outcome(raw_payload: Mapping[str, Any], effective_payload: Mapping[str, Any]) -> str:
    decision = _decision(effective_payload)
    if decision:
        return decision
    if effective_payload.get("systemMessage"):
        return "system_message"
    if effective_payload.get("additionalContext") or effective_payload.get("hookSpecificOutput"):
        return "context_added"
    if effective_payload != raw_payload:
        return "mutated"
    return "success"


def _build_record(
    record_type: str,
    raw_payload: Mapping[str, Any],
    *,
    source_event_name: str | None = None,
    effective_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source = source_event_name or _source_event_name(_current_hook_name(), raw_payload)
    event_name = _canonical_event_name(source)
    record: dict[str, Any] = {
        "record_type": record_type,
        "runtime": OBSERVABILITY_RUNTIME,
        "event_name": event_name,
        "source_event_name": source,
        "hook_name": _current_hook_name(),
        "timestamp": _timestamp(raw_payload),
        "session_id": _session_id(raw_payload),
        "raw_payload": dict(raw_payload),
    }
    cwd = _cwd(raw_payload)
    if cwd:
        record["cwd"] = cwd
    record.update(_promoted_fields(raw_payload))
    if effective_payload is not None:
        record["effective_payload"] = dict(effective_payload)
    return record


def _prepare_record(record: dict[str, Any]) -> dict[str, Any]:
    sanitized = _sanitize_value(record)
    if not isinstance(sanitized, dict):
        sanitized = {"record_type": record.get("record_type", "hook_execution"), "raw_payload": sanitized}

    serialized = json.dumps(sanitized, ensure_ascii=False, separators=(",", ":"))
    if len(serialized.encode("utf-8")) <= OBSERVABILITY_DEFAULT_MAX_RECORD_BYTES:
        return sanitized

    fallback = dict(sanitized)
    raw_payload = fallback.get("raw_payload")
    effective_payload = fallback.get("effective_payload")
    if isinstance(raw_payload, dict):
        fallback["raw_payload"] = {
            "_capped": True,
            "_keys": list(raw_payload.keys())[:OBSERVABILITY_DEFAULT_MAX_ITEMS],
        }
    elif raw_payload is not None:
        fallback["raw_payload"] = "[CAPPED]"
    if effective_payload is not None:
        fallback["effective_payload"] = "[CAPPED]"

    serialized = json.dumps(fallback, ensure_ascii=False, separators=(",", ":"))
    if len(serialized.encode("utf-8")) <= OBSERVABILITY_DEFAULT_MAX_RECORD_BYTES:
        return fallback

    minimal = {
        "record_type": fallback.get("record_type", "hook_execution"),
        "runtime": fallback.get("runtime", OBSERVABILITY_RUNTIME),
        "event_name": fallback.get("event_name", "unknown"),
        "source_event_name": fallback.get("source_event_name", "unknown"),
        "hook_name": fallback.get("hook_name", "unknown"),
        "timestamp": fallback.get("timestamp", ""),
        "session_id": fallback.get("session_id", ""),
        "raw_payload": "[CAPPED]",
    }
    if "duration_ms" in fallback:
        minimal["duration_ms"] = fallback["duration_ms"]
    if "outcome" in fallback:
        minimal["outcome"] = fallback["outcome"]
    return minimal


def _write_record(record: dict[str, Any]) -> bool:
    if _disabled():
        return False

    prepared = _prepare_record(record)
    log_path = _log_path()
    lock_path = _lock_path(log_path)
    timeout_seconds = _lock_wait_seconds(_lock_wait_ms())

    try:
        lock_fd = _acquire_lock(lock_path, timeout_seconds)
    except OSError:
        return False
    if lock_fd is None:
        return False

    try:
        _append_record(log_path, prepared)
    except OSError:
        return False
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)

    return True


def begin_hook_capture(payload: Mapping[str, Any]) -> None:
    if _disabled():
        return

    hook_name = _current_hook_name()
    raw_payload = dict(payload)
    source_event_name = _source_event_name(hook_name, raw_payload)
    _STATE.clear()
    _STATE.update(
        {
            "active": True,
            "completed": False,
            "hook_name": hook_name,
            "source_event_name": source_event_name,
            "event_name": _canonical_event_name(source_event_name),
            "raw_payload": raw_payload,
            "started_at": time.perf_counter(),
        }
    )

    if _capture_event_enabled() or hook_name == "send-event.py":
        _write_record(_build_record("event_capture", raw_payload, source_event_name=source_event_name))


def complete_hook_capture(output_payload: Mapping[str, Any]) -> None:
    if _disabled():
        return
    if not _STATE.get("active") or _STATE.get("completed"):
        return

    raw_payload = _STATE.get("raw_payload") or {}
    if not isinstance(raw_payload, Mapping):
        raw_payload = {}

    hook_name = str(_STATE.get("hook_name") or _current_hook_name())
    source_event_name = str(_STATE.get("source_event_name") or _source_event_name(hook_name, raw_payload))
    event_name = _canonical_event_name(source_event_name)
    started_at = float(_STATE.get("started_at") or time.perf_counter())
    duration_ms = max(0, int(round((time.perf_counter() - started_at) * 1000)))
    effective_payload = dict(output_payload)

    hook_record = _build_record(
        "hook_execution",
        raw_payload,
        source_event_name=source_event_name,
        effective_payload=effective_payload,
    )
    hook_record["event_name"] = event_name
    hook_record["source_event_name"] = source_event_name
    hook_record["duration_ms"] = duration_ms
    hook_record["outcome"] = _derive_outcome(raw_payload, effective_payload)
    if effective_payload != raw_payload:
        hook_record["mutated"] = True
    _write_record(hook_record)

    if event_name in TERMINAL_EVENT_NAMES:
        rollup_record = _build_record(
            "rollup",
            raw_payload,
            source_event_name=source_event_name,
            effective_payload=effective_payload,
        )
        rollup_record["event_name"] = event_name
        rollup_record["source_event_name"] = source_event_name
        rollup_record["duration_ms"] = duration_ms
        rollup_record["outcome"] = hook_record["outcome"]
        rollup_record["summary"] = {
            "session_id": hook_record.get("session_id", ""),
            "agent_id": hook_record.get("agent_id", ""),
            "agent_type": hook_record.get("agent_type", ""),
        }
        _write_record(rollup_record)

    _STATE["completed"] = True

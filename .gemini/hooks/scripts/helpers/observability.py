from __future__ import annotations

import fcntl
import json
import os
import re
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
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
    "accesskey",
    "accesstoken",
    "apikey",
    "authorization",
    "clientsecret",
    "idtoken",
    "password",
    "passphrase",
    "privatekey",
    "refreshtoken",
    "secret",
    "secretkey",
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
    "agentStop": "agentStop",
    "errorOccurred": "errorOccurred",
    "notification": "notification",
    "postToolUse": "postToolUse",
    "postToolUseFailure": "postToolUseFailure",
    "preToolUse": "preToolUse",
    "sessionEnd": "sessionEnd",
    "sessionStart": "sessionStart",
    "subagentStart": "subagentStart",
    "subagentStop": "subagentStop",
    "AfterAgent": "AfterAgent",
    "BeforeTool": "BeforeTool",
    "SessionEnd": "SessionEnd",
    "SessionStart": "SessionStart",
    "SubagentStart": "SubagentStart",
    "send-event.py": "send-event",
    "log-session-start.py": "SessionStart",
    "skill-context-injector.py": "SessionStart",
    "log-after-agent.py": "AfterAgent",
    "log-notification.py": "Notification",
    "log-session-end.py": "SessionEnd",
}

CANONICAL_EVENT_NAME_MAP = {
    "agentStop": "agent_stop",
    "errorOccurred": "error_occurred",
    "notification": "notification",
    "postToolUse": "after_tool",
    "postToolUseFailure": "after_tool_failure",
    "preToolUse": "before_tool",
    "sessionEnd": "session_end",
    "sessionStart": "session_start",
    "subagentStart": "subagent_start",
    "subagentStop": "subagent_stop",
    "AfterAgent": "agent_stop",
    "BeforeTool": "before_tool",
    "SessionEnd": "session_end",
    "SessionStart": "session_start",
    "SubagentStart": "subagent_start",
}

TERMINAL_EVENT_NAMES = {"session_end", "subagent_stop", "agent_stop"}

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


def _max_bytes() -> int:
    default = 10 * 1024 * 1024  # 10MB
    val = (
        os.environ.get("GEMINI_OBSERVABILITY_LOG_MAX_BYTES")
        if OBSERVABILITY_RUNTIME == "gemini"
        else os.environ.get("COPILOT_OBSERVABILITY_LOG_MAX_BYTES")
    ) or os.environ.get("OBSERVABILITY_LOG_MAX_BYTES")
    if val:
        try:
            # Allow exact threshold configuration but clamp at 0
            return max(0, int(val))
        except ValueError:
            pass
    return default


def _backup_count() -> int:
    default = 100
    val = (
        os.environ.get("GEMINI_OBSERVABILITY_LOG_BACKUP_COUNT")
        if OBSERVABILITY_RUNTIME == "gemini"
        else os.environ.get("COPILOT_OBSERVABILITY_LOG_BACKUP_COUNT")
    ) or os.environ.get("OBSERVABILITY_LOG_BACKUP_COUNT")
    if val:
        try:
            # Allow exact threshold configuration but clamp at 0
            return max(0, int(val))
        except ValueError:
            pass
    return default


def _rotate_log_if_needed(log_path: Path) -> None:
    try:
        backup_count = _backup_count()

        # Always pre-scan and prune stale backups regardless of active log size
        existing_backups = set()
        prefix = f"{log_path.name}."
        try:
            if log_path.parent.exists():
                for entry in log_path.parent.iterdir():
                    if entry.name.startswith(prefix):
                        suffix = entry.name[len(prefix):]
                        if suffix.isdigit():
                            existing_backups.add(int(suffix))
        except OSError:
            pass

        # Prune any backups that exceed the current backup_count
        for i in existing_backups:
            if i > backup_count:
                try:
                    os.remove(str(log_path.with_name(f"{log_path.name}.{i}")))
                except OSError:
                    pass

        # If active log doesn't exist or hasn't reached the limit, we are done
        if not log_path.exists():
            return
            
        st_size = log_path.stat().st_size
        if st_size == 0:
            return
            
        max_bytes = _max_bytes()
        if st_size < max_bytes:
            return

        # Active log exceeded max_bytes. Rotate it.
        if backup_count <= 0:
            try:
                os.remove(str(log_path))
            except OSError:
                pass
            return

        # Shift existing backups from backup_count - 1 down to 1
        for i in range(backup_count - 1, 0, -1):
            if i in existing_backups:
                sfn = log_path.with_name(f"{log_path.name}.{i}")
                dfn = log_path.with_name(f"{log_path.name}.{i+1}")
                try:
                    if dfn.exists():
                        os.remove(str(dfn))
                    sfn.rename(dfn)
                except OSError:
                    pass

        # Move active log to .1
        dfn = log_path.with_name(f"{log_path.name}.1")
        try:
            if dfn.exists():
                os.remove(str(dfn))
            log_path.rename(dfn)
        except OSError:
            pass
    except Exception:
        # Fail-open: ensure any rotation failure does not prevent logging
        pass


def _sanitize_string(value: str, *, key: str | None = None) -> str:
    lowered_key = (key or "").replace("-", "").replace("_", "").lower()
    is_secret = (
        lowered_key in SECRET_FIELD_NAMES or
        any(secret in lowered_key for secret in SECRET_FIELD_NAMES) or
        lowered_key.endswith(("password", "token", "secret", "key", "passphrase"))
    )
    if is_secret:
        return "[REDACTED]"
    if lowered_key in {"transcript", "transcriptpath"} and not _include_transcript():
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

    if hook_name == "send-event.py":
        candidate = first_present(payload, "hook_event_name", "hookEventName", "source_event_name", "sourceEventName")
        if candidate:
            return stringify_value(candidate)

    if hook_name == "load-required-skills.py":
        if first_present(payload, "agentId", "agent_id", "agentName", "agent_name", "transcriptPath", "transcript_path"):
            return "subagentStart"
        return "sessionStart"

    if hook_name == "bell.py":
        return "sessionEnd"

    candidate = first_present(payload, "hook_event_name", "hookEventName", "source_event_name", "sourceEventName")
    if candidate:
        return stringify_value(candidate)

    return SOURCE_EVENT_NAME_MAP.get(hook_name, hook_name.removesuffix(".py"))


def _canonical_event_name(source_event_name: str) -> str:
    if source_event_name in CANONICAL_EVENT_NAME_MAP:
        return CANONICAL_EVENT_NAME_MAP[source_event_name]

    normalized = source_event_name.replace("-", "_")
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = re.sub(r"__+", "_", normalized)
    return normalized.strip("_").lower()


def _timestamp(payload: Mapping[str, Any]) -> str:
    timestamp = stringify_value(first_present(payload, "timestamp", "time"))
    if timestamp:
        return timestamp
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def _tool_use_id(payload: Mapping[str, Any]) -> str:
    return stringify_value(first_present(payload, "tool_use_id", "toolUseId"))


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
        ("tool_use_id", _tool_use_id(payload)),
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
        _rotate_log_if_needed(log_path)
        _append_record(log_path, prepared)
    except OSError:
        return False
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)

    return True


SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    parent_session_id TEXT,
    workspace_root TEXT NOT NULL,
    runtime TEXT,
    status TEXT,
    start_time_ms INTEGER,
    end_time_ms INTEGER,
    total_duration_ms INTEGER,
    has_errors INTEGER DEFAULT 0,
    transcript_path TEXT,
    FOREIGN KEY(parent_session_id) REFERENCES sessions(session_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS spans (
    span_id TEXT PRIMARY KEY,
    parent_span_id TEXT,
    session_id TEXT NOT NULL,
    sequence_no INTEGER NOT NULL,
    event_name TEXT,
    source_event_name TEXT,
    hook_name TEXT,
    timestamp_ms INTEGER,
    updated_at_ms INTEGER,
    pid INTEGER,
    duration_ms INTEGER,
    status TEXT,
    outcome TEXT,
    late_arrival INTEGER DEFAULT 0,
    transcript_chunk_path TEXT,
    metadata TEXT,
    FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY(parent_span_id) REFERENCES spans(span_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_parent ON sessions(parent_session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_workspace_start ON sessions(workspace_root, start_time_ms);
CREATE INDEX IF NOT EXISTS idx_spans_session ON spans(session_id);
CREATE INDEX IF NOT EXISTS idx_spans_parent ON spans(parent_span_id);
CREATE INDEX IF NOT EXISTS idx_spans_session_status ON spans(session_id, status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_spans_session_sequence ON spans(session_id, sequence_no);
"""


def _sqlite_disabled() -> bool:
    return _truthy_env(
        "COPILOT_OBSERVABILITY_DISABLE_SQLITE",
        "GEMINI_OBSERVABILITY_DISABLE_SQLITE",
        "OBSERVABILITY_DISABLE_SQLITE",
        "OBSERVABILITY_FORCE_NDJSON"
    )


def _workspace_root(payload: Mapping[str, Any] | None = None) -> str:
    for env_var in ["WORKSPACE_ROOT", "GEMINI_PROJECT_DIR", "COPILOT_PROJECT_DIR"]:
        val = os.environ.get(env_var)
        if val:
            return str(Path(val).resolve())

    start_path = None
    if payload:
        cwd_val = _cwd(payload)
        if cwd_val:
            start_path = Path(cwd_val)
    if not start_path:
        start_path = Path.cwd()

    start_path = start_path.resolve()
    curr = start_path
    while True:
        if (curr / ".git").exists() or (curr / ".gemini").exists() or (curr / ".copilot").exists():
            return str(curr)
        parent = curr.parent
        if parent == curr:
            break
        curr = parent
    return str(start_path)


def _get_db_path() -> Path:
    return _log_path().parent / "observability_v1.db"


def _busy_timeout_ms() -> int:
    val = None
    if OBSERVABILITY_RUNTIME == "copilot":
        val = os.environ.get("COPILOT_OBSERVABILITY_BUSY_TIMEOUT_MS")
    elif OBSERVABILITY_RUNTIME == "gemini":
        val = os.environ.get("GEMINI_OBSERVABILITY_BUSY_TIMEOUT_MS")

    if not val:
        val = os.environ.get("OBSERVABILITY_BUSY_TIMEOUT_MS")

    if val:
        try:
            return max(0, int(val))
        except ValueError:
            pass
    return 50


def _finalization_busy_timeout_ms() -> int:
    val = None
    if OBSERVABILITY_RUNTIME == "copilot":
        val = os.environ.get("COPILOT_OBSERVABILITY_FINALIZATION_BUSY_TIMEOUT_MS")
    elif OBSERVABILITY_RUNTIME == "gemini":
        val = os.environ.get("GEMINI_OBSERVABILITY_FINALIZATION_BUSY_TIMEOUT_MS")

    if not val:
        val = os.environ.get("OBSERVABILITY_FINALIZATION_BUSY_TIMEOUT_MS")

    if val:
        try:
            return max(0, int(val))
        except ValueError:
            pass
    return 5000


def _supports_returning() -> bool:
    try:
        parts = [int(x) for x in sqlite3.sqlite_version.split(".")]
        return tuple(parts) >= (3, 35, 0)
    except Exception:
        return False


def _connect_db(db_path: Path, busy_timeout: int) -> sqlite3.Connection:
    _ensure_parent(db_path)
    if not db_path.exists():
        fd = os.open(str(db_path), os.O_CREAT | os.O_RDWR, 0o600)
        os.close(fd)
    else:
        try:
            os.chmod(str(db_path), 0o600)
        except Exception:
            pass
    conn = sqlite3.connect(str(db_path), timeout=busy_timeout / 1000.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA auto_vacuum=INCREMENTAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def _init_schema_if_needed(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("PRAGMA user_version;")
    version = cursor.fetchone()[0]
    if version == 0:
        cursor.executescript(SCHEMA_DDL)
        cursor.execute("PRAGMA user_version = 1;")
    elif version != 1:
        raise sqlite3.OperationalError("mismatched schema version")


def _connect_and_init_db(db_path: Path, busy_timeout: int) -> sqlite3.Connection:
    try:
        conn = _connect_db(db_path, busy_timeout)
        _init_schema_if_needed(conn)
        return conn
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        try:
            if db_path.exists():
                db_path.unlink()
            for suffix in ["-wal", "-shm"]:
                p = Path(str(db_path) + suffix)
                if p.exists():
                    p.unlink()
        except Exception:
            pass
        conn = _connect_db(db_path, busy_timeout)
        cursor = conn.cursor()
        cursor.executescript(SCHEMA_DDL)
        cursor.execute("PRAGMA user_version = 1;")
        return conn


def _timestamp_to_ms(ts_str: str) -> int:
    try:
        clean_ts = ts_str.strip()
        if clean_ts.endswith("Z"):
            clean_ts = clean_ts[:-1] + "+00:00"
        dt = datetime.fromisoformat(clean_ts)
        return int(dt.timestamp() * 1000)
    except Exception:
        return int(time.time() * 1000)


def _ensure_session(conn: sqlite3.Connection, session_id: str, workspace_root: str, timestamp_ms: int) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO sessions (session_id, workspace_root, runtime, status, start_time_ms, has_errors) VALUES (?, ?, ?, 'running', ?, 0)",
        (session_id, workspace_root, OBSERVABILITY_RUNTIME, timestamp_ms)
    )


def begin_hook_capture(payload: Mapping[str, Any]) -> None:
    if _disabled():
        return

    hook_name = _current_hook_name()
    raw_payload = dict(payload)
    source_event_name = _source_event_name(hook_name, raw_payload)
    _STATE.clear()

    span_id = f"span-{uuid.uuid4()}"
    _STATE.update(
        {
            "active": True,
            "completed": False,
            "span_id": span_id,
            "hook_name": hook_name,
            "source_event_name": source_event_name,
            "event_name": _canonical_event_name(source_event_name),
            "raw_payload": raw_payload,
            "started_at": time.perf_counter(),
        }
    )

    session_id = _session_id(raw_payload)
    sqlite_success = False

    if not _sqlite_disabled() and session_id:
        workspace_root = _workspace_root(raw_payload)
        ts_str = _timestamp(raw_payload)
        timestamp_ms = _timestamp_to_ms(ts_str)
        event_name = _canonical_event_name(source_event_name)
        db_path = _get_db_path()
        busy_timeout = _busy_timeout_ms()

        try:
            conn = _connect_and_init_db(db_path, busy_timeout)
            conn.execute("BEGIN IMMEDIATE")
            try:
                _ensure_session(conn, session_id, workspace_root, timestamp_ms)

                if event_name == "session_start":
                    conn.execute(
                        "UPDATE sessions SET status = 'running', start_time_ms = COALESCE(start_time_ms, ?) WHERE session_id = ?",
                        (timestamp_ms, session_id)
                    )

                cursor = conn.cursor()
                if _supports_returning():
                    cursor.execute(
                        """
                        INSERT INTO spans (span_id, session_id, sequence_no, event_name, source_event_name, hook_name, timestamp_ms, updated_at_ms, pid, status, late_arrival, metadata)
                        SELECT ?, s.session_id, COALESCE(MAX(sp.sequence_no), 0) + 1, ?, ?, ?, ?, ?, ?, 'running',
                               CASE WHEN s.status = 'finalizing' THEN 1 ELSE 0 END, ?
                        FROM sessions s
                        LEFT JOIN spans sp ON sp.session_id = s.session_id
                        WHERE s.session_id = ?
                          AND s.status IN ('running', 'finalizing')
                        GROUP BY s.session_id
                        RETURNING sequence_no;
                        """,
                        (span_id, event_name, source_event_name, hook_name, timestamp_ms, timestamp_ms, os.getpid(), json.dumps({}), session_id)
                    )
                    row = cursor.fetchone()
                    if row:
                        _STATE["sequence_no"] = row[0]
                        sqlite_success = True
                else:
                    cursor.execute(
                        """
                        INSERT INTO spans (span_id, session_id, sequence_no, event_name, source_event_name, hook_name, timestamp_ms, updated_at_ms, pid, status, late_arrival, metadata)
                        SELECT ?, s.session_id, COALESCE(MAX(sp.sequence_no), 0) + 1, ?, ?, ?, ?, ?, ?, 'running',
                               CASE WHEN s.status = 'finalizing' THEN 1 ELSE 0 END, ?
                        FROM sessions s
                        LEFT JOIN spans sp ON sp.session_id = s.session_id
                        WHERE s.session_id = ?
                          AND s.status IN ('running', 'finalizing')
                        GROUP BY s.session_id;
                        """,
                        (span_id, event_name, source_event_name, hook_name, timestamp_ms, timestamp_ms, os.getpid(), json.dumps({}), session_id)
                    )
                    if cursor.rowcount > 0:
                        sqlite_success = True
                        cursor.execute("SELECT sequence_no FROM spans WHERE span_id = ?", (span_id,))
                        row = cursor.fetchone()
                        if row:
                            _STATE["sequence_no"] = row[0]
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        except Exception:
            pass

    _STATE["sqlite_success"] = sqlite_success

    if not sqlite_success:
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

    sqlite_success = False
    span_id = _STATE.get("span_id")
    if not _sqlite_disabled() and _STATE.get("sqlite_success") and span_id:
        sanitized_raw = _sanitize_value(raw_payload)
        sanitized_eff = _sanitize_value(effective_payload)
        meta = {
            "duration_ms": duration_ms,
            "outcome": hook_record["outcome"],
            "raw_payload": sanitized_raw,
            "effective_payload": sanitized_eff,
        }
        if "mutated" in hook_record:
            meta["mutated"] = True

        db_path = _get_db_path()
        busy_timeout = _busy_timeout_ms()

        try:
            conn = _connect_and_init_db(db_path, busy_timeout)
            conn.execute("BEGIN IMMEDIATE")
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE spans SET
                        status = 'completed',
                        duration_ms = ?,
                        outcome = ?,
                        updated_at_ms = ?,
                        metadata = ?
                    WHERE span_id = ?;
                    """,
                    (duration_ms, hook_record["outcome"], int(time.time() * 1000), json.dumps(meta, ensure_ascii=False), span_id)
                )
                if cursor.rowcount > 0:
                    sqlite_success = True
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        except Exception:
            pass

    if not sqlite_success:
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

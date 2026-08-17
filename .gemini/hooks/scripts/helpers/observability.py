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
    re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk_live_[0-9A-Za-z]{16,}"),
    re.compile(r"AIza[0-9A-Za-z-_]{35}"),
    re.compile(r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*"),
    re.compile(r"(?<=://)[^:]+:[^@]+(?=@)"),
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


def _sanitize_string(value: str, *, key: str | None = None, bypass_capping: bool = False) -> str:
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
    if not bypass_capping and len(sanitized) > OBSERVABILITY_DEFAULT_MAX_STRING_CHARS:
        cap = OBSERVABILITY_DEFAULT_MAX_STRING_CHARS
        omitted = len(sanitized) - cap
        marker = f"...[capped {omitted} chars]..."
        head = max(0, cap - len(marker))
        sanitized = f"{sanitized[:head]}{marker}"
    return sanitized


def _sanitize_value(value: Any, *, key: str | None = None, depth: int = 0, bypass_capping: bool = False) -> Any:
    if not bypass_capping and depth > 4:
        return "[CAPPED]"

    if isinstance(value, str):
        return _sanitize_string(value, key=key, bypass_capping=bypass_capping)
    if isinstance(value, bytes):
        return _sanitize_string(value.decode("utf-8", errors="replace"), key=key, bypass_capping=bypass_capping)
    if isinstance(value, Mapping):
        items: dict[str, Any] = {}
        for index, (child_key, child_value) in enumerate(value.items()):
            if not bypass_capping and index >= OBSERVABILITY_DEFAULT_MAX_ITEMS:
                items["_capped"] = True
                items["_capped_items"] = max(0, len(value) - OBSERVABILITY_DEFAULT_MAX_ITEMS)
                break
            child_key_text = str(child_key)
            items[child_key_text] = _sanitize_value(child_value, key=child_key_text, depth=depth + 1, bypass_capping=bypass_capping)
        return items
    if isinstance(value, list):
        if bypass_capping:
            sanitized = [_sanitize_value(item, key=key, depth=depth + 1, bypass_capping=bypass_capping) for item in value]
        else:
            sanitized = [_sanitize_value(item, key=key, depth=depth + 1, bypass_capping=bypass_capping) for item in value[:OBSERVABILITY_DEFAULT_MAX_ITEMS]]
            if len(value) > OBSERVABILITY_DEFAULT_MAX_ITEMS:
                sanitized.append(
                    {
                        "_capped": True,
                        "_capped_items": len(value) - OBSERVABILITY_DEFAULT_MAX_ITEMS,
                    }
                )
        return sanitized
    if isinstance(value, tuple):
        return [_sanitize_value(item, key=key, depth=depth + 1, bypass_capping=bypass_capping) for item in value]
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


def _backup_corrupt_db(db_path: Path) -> None:
    try:
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        backup_path = db_path.with_name(f"{db_path.name}.corrupt.{date_str}")
        if backup_path.exists():
            try:
                backup_path.unlink()
            except Exception:
                pass
        if db_path.exists():
            db_path.rename(backup_path)
        for suffix in ["-wal", "-shm"]:
            p = Path(str(db_path) + suffix)
            if p.exists():
                p.unlink()
    except Exception:
        pass


def _connect_and_init_db(db_path: Path, busy_timeout: int) -> sqlite3.Connection:
    try:
        conn = _connect_db(db_path, busy_timeout)
        try:
            _init_schema_if_needed(conn)
            return conn
        except Exception as e:
            conn.close()
            raise e
    except Exception as e:
        err_msg = str(e).lower()
        is_transient = "locked" in err_msg or "busy" in err_msg
        is_mismatch = "mismatched schema version" in err_msg
        is_corrupt = "malformed" in err_msg or "not a database" in err_msg or "corrupt" in err_msg

        if (is_mismatch or is_corrupt) and not is_transient:
            try:
                if is_corrupt:
                    _backup_corrupt_db(db_path)
                else:
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
        else:
            raise e


def _handle_write_corruption(db_path: Path, exc: Exception) -> None:
    err_msg = str(exc).lower()
    is_corrupt = "malformed" in err_msg or "not a database" in err_msg or "corrupt" in err_msg
    if is_corrupt:
        _backup_corrupt_db(db_path)


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


def _write_registry_file(child_session_id: str, parent_session_id: str) -> None:
    try:
        registry_dir = _get_db_path().parent / "registries" / "subagents"
        registry_dir.mkdir(parents=True, exist_ok=True)
        registry_file = registry_dir / f"{child_session_id}.json"
        temp_file = registry_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump({"parent_session_id": parent_session_id}, f)
        temp_file.replace(registry_file)
    except Exception:
        pass


def _backfill_parent_session_id(conn: sqlite3.Connection, session_id: str, workspace_root: str, timestamp_ms: int) -> None:
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT parent_session_id FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if row and row[0] is not None:
            return

        registry_file = _get_db_path().parent / "registries" / "subagents" / f"{session_id}.json"
        if registry_file.exists():
            with open(registry_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            parent_session_id = data.get("parent_session_id")
            if parent_session_id:
                _ensure_session(conn, parent_session_id, workspace_root, timestamp_ms)
                conn.execute(
                    "UPDATE sessions SET parent_session_id = ? WHERE session_id = ?",
                    (parent_session_id, session_id)
                )
    except Exception:
        pass


def _finalization_timeout_ms() -> int:
    val = None
    if OBSERVABILITY_RUNTIME == "copilot":
        val = os.environ.get("COPILOT_OBSERVABILITY_FINALIZATION_TIMEOUT_MS")
    elif OBSERVABILITY_RUNTIME == "gemini":
        val = os.environ.get("GEMINI_OBSERVABILITY_FINALIZATION_TIMEOUT_MS")

    if not val:
        val = os.environ.get("OBSERVABILITY_FINALIZATION_TIMEOUT_MS")

    if val:
        try:
            return max(0, int(val))
        except ValueError:
            pass
    return 5000


def _running_span_stale_ms() -> int:
    val = None
    if OBSERVABILITY_RUNTIME == "copilot":
        val = os.environ.get("COPILOT_OBSERVABILITY_RUNNING_SPAN_STALE_MS")
    elif OBSERVABILITY_RUNTIME == "gemini":
        val = os.environ.get("GEMINI_OBSERVABILITY_RUNNING_SPAN_STALE_MS")

    if not val:
        val = os.environ.get("OBSERVABILITY_RUNNING_SPAN_STALE_MS")

    if val:
        try:
            return max(0, int(val))
        except ValueError:
            pass
    return 30000


def _pid_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _cap_payload_content(raw: dict[str, Any], effective: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any] | None, bool]:
    payload_dict = {"raw": raw}
    if effective is not None:
        payload_dict["effective"] = effective
    
    payload_str = json.dumps(payload_dict, ensure_ascii=False)
    if len(payload_str.encode("utf-8")) <= 512 * 1024:
        return raw, effective, False

    capped = False
    
    def shrink_obj(obj: Any) -> Any:
        nonlocal capped
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                new_dict[k] = shrink_obj(v)
            return new_dict
        elif isinstance(obj, list):
            return [shrink_obj(x) for x in obj]
        elif isinstance(obj, str):
            if len(obj.encode("utf-8")) > 10 * 1024:
                capped = True
                return obj[:1024] + "... [CAPPED]"
            return obj
        return obj

    r_raw = shrink_obj(raw)
    r_eff = shrink_obj(effective) if effective is not None else None

    payload_dict = {"raw": r_raw}
    if r_eff is not None:
        payload_dict["effective"] = r_eff
    
    payload_str = json.dumps(payload_dict, ensure_ascii=False)
    if len(payload_str.encode("utf-8")) > 512 * 1024:
        capped = True
        r_raw = {"payload_capped_error": "Payload exceeded 512KB limits and was cleared."}
        r_eff = {"payload_capped_error": "Payload exceeded 512KB limits and was cleared."} if r_eff is not None else None

    return r_raw, r_eff, True


def _write_transcript_chunk(
    session_id: str,
    span_id: str,
    parent_span_id: str | None,
    event_name: str,
    source_event_name: str,
    hook_record: dict[str, Any],
    db_path: Path,
    busy_timeout: int,
    timestamp_ms: int,
    sanitized_raw: dict[str, Any],
    sanitized_eff: dict[str, Any] | None,
    meta: dict[str, Any],
    sequence_no: int
) -> None:
    is_lifecycle = event_name in {"session_start", "session_end", "subagent_start", "subagent_stop", "agent_stop"}
    is_mutated = "mutated" in hook_record
    is_textual_or_mutated = (not is_lifecycle) or is_mutated

    if is_textual_or_mutated:
        try:
            import datetime
            dt = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, tz=datetime.timezone.utc)
            iso_timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{int(timestamp_ms % 1000):03d}Z"

            r_raw, r_eff, is_capped = _cap_payload_content(sanitized_raw, sanitized_eff if is_mutated else None)

            if is_capped:
                meta["payload_capped"] = True
                meta["raw_payload"] = r_raw
                if r_eff is not None:
                    meta["effective_payload"] = r_eff
                try:
                    with _connect_and_init_db(db_path, busy_timeout) as update_conn:
                        update_conn.execute("BEGIN IMMEDIATE")
                        update_conn.execute("UPDATE spans SET metadata = ? WHERE span_id = ?", (json.dumps(meta, ensure_ascii=False), span_id))
                        update_conn.commit()
                except Exception:
                    pass

            chunk_data = {
                "session_id": session_id,
                "span_id": span_id,
                "parent_span_id": parent_span_id or None,
                "event_name": event_name,
                "source_event_name": source_event_name,
                "timestamp": iso_timestamp,
                "outcome": hook_record["outcome"],
                "payload": {
                    "raw": r_raw
                }
            }
            if is_mutated and r_eff is not None:
                chunk_data["payload"]["effective"] = r_eff
            if is_capped:
                chunk_data["payload_capped"] = True

            active_dir = db_path.parent / "transcripts" / "active" / session_id
            active_dir.mkdir(parents=True, exist_ok=True)
            chunk_file = active_dir / f"{sequence_no:06d}_{span_id}.json"
            
            temp_chunk = chunk_file.with_suffix(".tmp")
            with open(temp_chunk, "w", encoding="utf-8") as f:
                json.dump(chunk_data, f, ensure_ascii=False)
            temp_chunk.replace(chunk_file)
            
            try:
                with _connect_and_init_db(db_path, busy_timeout) as update_conn:
                    update_conn.execute("BEGIN IMMEDIATE")
                    update_conn.execute("UPDATE spans SET transcript_chunk_path = ? WHERE span_id = ?", (str(chunk_file), span_id))
                    update_conn.commit()
            except Exception:
                pass

        except Exception:
            pass


def _finalize_session(session_id: str, db_path: Path, normal_busy_timeout: int) -> None:
    finalizer_busy = _finalization_busy_timeout_ms()
    timeout_budget = _finalization_timeout_ms()
    stale_threshold = _running_span_stale_ms()
    
    start_time = time.monotonic()
    
    try:
        with _connect_and_init_db(db_path, finalizer_busy) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                conn.execute(
                    "UPDATE sessions SET status = 'finalizing' WHERE session_id = ? AND status = 'running'",
                    (session_id,)
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
    except Exception:
        pass

    polling_cadence = 0.01
    has_uncompleted = True
    
    while time.monotonic() - start_time < (timeout_budget / 1000.0):
        running_spans = []
        try:
            with _connect_and_init_db(db_path, finalizer_busy) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT span_id, updated_at_ms, pid FROM spans WHERE session_id = ? AND status = 'running'",
                    (session_id,)
                )
                running_spans = cursor.fetchall()
        except Exception:
            pass
        
        if not running_spans:
            has_uncompleted = False
            break
            
        now_ms = int(time.time() * 1000)
        any_changed = False
        
        for span_id, updated_at_ms, pid in running_spans:
            pid_dead = False
            if pid:
                pid_dead = not _pid_exists(pid)
            
            stale_age = False
            if updated_at_ms and (now_ms - updated_at_ms > stale_threshold):
                stale_age = True
                
            if pid_dead or stale_age:
                try:
                    with _connect_and_init_db(db_path, finalizer_busy) as conn:
                        conn.execute("BEGIN IMMEDIATE")
                        try:
                            conn.execute(
                                "UPDATE spans SET status = 'abandoned', updated_at_ms = ? WHERE span_id = ?",
                                (now_ms, span_id)
                            )
                            conn.execute(
                                "UPDATE sessions SET has_errors = 1 WHERE session_id = ?",
                                (session_id,)
                            )
                            conn.commit()
                            any_changed = True
                        except Exception:
                            conn.rollback()
                except Exception:
                    pass
                    
        if not any_changed:
            time.sleep(polling_cadence)
            
    if has_uncompleted:
        try:
            with _connect_and_init_db(db_path, finalizer_busy) as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    conn.execute(
                        "UPDATE sessions SET status = 'failed-finalization', has_errors = 1 WHERE session_id = ?",
                        (session_id,)
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()
        except Exception:
            pass
        return
        
    now_epoch_ms = int(time.time() * 1000)
    try:
        with _connect_and_init_db(db_path, finalizer_busy) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT start_time_ms FROM sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                start_ms = row[0] if (row and row[0]) else now_epoch_ms
                duration_ms = max(0, now_epoch_ms - start_ms)
                
                conn.execute(
                    """
                    UPDATE sessions SET
                        status = 'sealing',
                        end_time_ms = ?,
                        total_duration_ms = ?
                    WHERE session_id = ?;
                    """,
                    (now_epoch_ms, duration_ms, session_id)
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
    except Exception:
        pass

    try:
        with _connect_and_init_db(db_path, finalizer_busy) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT start_time_ms FROM sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                start_ms = row[0] if (row and row[0]) else now_epoch_ms
                _backfill_parent_session_id(conn, session_id, _workspace_root({}), start_ms)
                conn.commit()
            except Exception:
                conn.rollback()
    except Exception:
        pass

    active_dir = db_path.parent / "transcripts" / "active" / session_id
    saved_dir = db_path.parent / "transcripts" / "saved"
    saved_file = saved_dir / f"{session_id}.jsonl"
    
    merged_lines = []
    if active_dir.exists():
        chunk_files = sorted(active_dir.glob("*.json"))
        for chunk_file in chunk_files:
            try:
                with open(chunk_file, "r", encoding="utf-8") as f:
                    chunk_data = json.load(f)
                    
                if not chunk_data.get("parent_session_id"):
                    try:
                        with _connect_and_init_db(db_path, finalizer_busy) as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT parent_session_id FROM sessions WHERE session_id = ?", (session_id,))
                            row = cursor.fetchone()
                            if row and row[0]:
                                chunk_data["parent_session_id"] = row[0]
                    except Exception:
                        pass
                merged_lines.append(json.dumps(chunk_data, ensure_ascii=False) + "\n")
            except Exception:
                pass

    has_errors = 0
    try:
        with _connect_and_init_db(db_path, finalizer_busy) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT has_errors FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row and row[0]:
                has_errors = row[0]
    except Exception:
        pass
        
    retained = False
    if has_errors:
        retained = True
    else:
        force_sampling = None
        if OBSERVABILITY_RUNTIME == "copilot":
            force_sampling = os.environ.get("COPILOT_OBSERVABILITY_SAMPLING_FORCE")
        elif OBSERVABILITY_RUNTIME == "gemini":
            force_sampling = os.environ.get("GEMINI_OBSERVABILITY_SAMPLING_FORCE")
            
        if not force_sampling:
            force_sampling = os.environ.get("OBSERVABILITY_SAMPLING_FORCE")
            
        if force_sampling:
            if force_sampling.strip().lower() in {"1", "true", "yes", "on"}:
                retained = True
            elif force_sampling.strip().lower() in {"0", "false", "no", "off"}:
                retained = False
        else:
            import random
            retained = random.random() < 0.05

    if retained and merged_lines:
        try:
            saved_dir.mkdir(parents=True, exist_ok=True)
            temp_saved = saved_file.with_suffix(".tmp")
            with open(temp_saved, "w", encoding="utf-8") as f:
                f.writelines(merged_lines)
            temp_saved.replace(saved_file)
            
            with _connect_and_init_db(db_path, finalizer_busy) as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    conn.execute(
                        "UPDATE sessions SET transcript_path = ? WHERE session_id = ?",
                        (str(saved_file), session_id)
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()
        except Exception:
            pass

    if active_dir.exists():
        try:
            import shutil
            shutil.rmtree(active_dir)
        except Exception:
            pass

    try:
        registry_file = db_path.parent / "registries" / "subagents" / f"{session_id}.json"
        if registry_file.exists():
            os.remove(registry_file)
    except Exception:
        pass

    final_status = "failed" if has_errors else "success"
    try:
        with _connect_and_init_db(db_path, finalizer_busy) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                conn.execute(
                    "UPDATE sessions SET status = ? WHERE session_id = ?",
                    (final_status, session_id)
                )
                conn.commit()
            except Exception:
                conn.rollback()
    except Exception:
        pass


def _should_launch_maintenance(sentinel_path: Path) -> bool:
    try:
        if not sentinel_path.exists():
            return True
        mtime = sentinel_path.stat().st_mtime
        if time.time() - mtime > 86400:
            return True
    except Exception:
        return True
    return False


def _launch_detached_maintenance(sentinel_path: Path) -> None:
    try:
        _ensure_parent(sentinel_path)
        sentinel_path.touch(exist_ok=True)
        
        import subprocess
        scripts_dir = str(Path(__file__).resolve().parent.parent)
        subprocess.Popen(
            [sys.executable, "-m", "helpers.observability", "--maintenance"],
            cwd=scripts_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True
        )
    except Exception:
        pass


def _trigger_detached_maintenance_if_needed(event_name: str) -> None:
    if event_name != "session_start" and event_name not in TERMINAL_EVENT_NAMES:
        return
    sentinel_path = _log_path().parent / ".maintenance_last_run"
    if _should_launch_maintenance(sentinel_path):
        _launch_detached_maintenance(sentinel_path)


def _scavenge_stale_directories_and_registries(db_path: Path) -> None:
    now = time.time()
    stale_threshold = 24 * 3600
    
    active_base = db_path.parent / "transcripts" / "active"
    if active_base.exists():
        for item in active_base.iterdir():
            if item.is_dir():
                try:
                    mtime = item.stat().st_mtime
                    if now - mtime > stale_threshold:
                        import shutil
                        shutil.rmtree(item)
                except Exception:
                    pass
                    
    registry_base = db_path.parent / "registries" / "subagents"
    if registry_base.exists():
        for item in registry_base.iterdir():
            if item.is_file() and item.suffix == ".json":
                try:
                    mtime = item.stat().st_mtime
                    if now - mtime > stale_threshold:
                        item.unlink()
                except Exception:
                    pass


def _run_maintenance_work() -> None:
    try:
        db_path = _get_db_path()
        finalizer_busy = _finalization_busy_timeout_ms()
        
        now_ms = int(time.time() * 1000)
        error_threshold_ms = now_ms - 90 * 24 * 3600 * 1000
        success_threshold_ms = now_ms - 14 * 24 * 3600 * 1000
        
        conn = _connect_and_init_db(db_path, finalizer_busy)
        conn.execute("BEGIN IMMEDIATE")
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT session_id, transcript_path
                FROM sessions
                WHERE (has_errors = 1 AND start_time_ms < ?)
                   OR (has_errors = 0 AND start_time_ms < ?)
                """,
                (error_threshold_ms, success_threshold_ms)
            )
            expired_sessions = cursor.fetchall()
            
            saved_dir = db_path.parent / "transcripts" / "saved"
            for session_id, transcript_path_str in expired_sessions:
                if transcript_path_str:
                    t_path = Path(transcript_path_str)
                    if t_path.exists():
                        try:
                            t_path.unlink()
                        except Exception:
                            pass
                std_saved_file = saved_dir / f"{session_id}.jsonl"
                if std_saved_file.exists():
                    try:
                        std_saved_file.unlink()
                    except Exception:
                        pass
                
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
        except Exception:
            conn.rollback()
        finally:
            conn.close()
            
        try:
            conn = _connect_and_init_db(db_path, finalizer_busy)
            conn.execute("PRAGMA incremental_vacuum;")
            conn.close()
        except Exception:
            pass
            
        _scavenge_stale_directories_and_registries(db_path)
    except Exception:
        pass


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
    event_name = _STATE.get("event_name") or _canonical_event_name(source_event_name)

    if event_name == "subagent_start" and session_id:
        parent_session_id = (
            os.environ.get("GEMINI_SESSION_ID")
            or os.environ.get("COPILOT_SESSION_ID")
            or os.environ.get("OBSERVABILITY_SESSION_ID")
            or os.environ.get("SESSION_ID")
            or raw_payload.get("parent_session_id")
            or raw_payload.get("parentSessionId")
        )
        if parent_session_id:
            _write_registry_file(session_id, parent_session_id)

    sqlite_success = False

    if not _sqlite_disabled() and session_id:
        workspace_root = _workspace_root(raw_payload)
        ts_str = _timestamp(raw_payload)
        timestamp_ms = _timestamp_to_ms(ts_str)
        db_path = _get_db_path()
        busy_timeout = _busy_timeout_ms()

        try:
            conn = _connect_and_init_db(db_path, busy_timeout)
            conn.execute("BEGIN IMMEDIATE")
            try:
                _ensure_session(conn, session_id, workspace_root, timestamp_ms)
                _backfill_parent_session_id(conn, session_id, workspace_root, timestamp_ms)

                if event_name == "session_start":
                    conn.execute(
                        "UPDATE sessions SET status = 'running', start_time_ms = COALESCE(start_time_ms, ?) WHERE session_id = ?",
                        (timestamp_ms, session_id)
                    )
                elif event_name in TERMINAL_EVENT_NAMES:
                    conn.execute(
                        "UPDATE sessions SET status = 'finalizing' WHERE session_id = ?",
                        (session_id,)
                    )

                cursor = conn.cursor()
                parent_span_id = raw_payload.get("parent_span_id") or raw_payload.get("parentSpanId")
                if _supports_returning():
                    cursor.execute(
                        """
                        INSERT INTO spans (span_id, parent_span_id, session_id, sequence_no, event_name, source_event_name, hook_name, timestamp_ms, updated_at_ms, pid, status, late_arrival, metadata)
                        SELECT ?, ?, s.session_id, COALESCE(MAX(sp.sequence_no), 0) + 1, ?, ?, ?, ?, ?, ?, 'running',
                               CASE WHEN s.status = 'finalizing' THEN 1 ELSE 0 END, ?
                        FROM sessions s
                        LEFT JOIN spans sp ON sp.session_id = s.session_id
                        WHERE s.session_id = ?
                          AND s.status IN ('running', 'finalizing')
                        GROUP BY s.session_id
                        RETURNING sequence_no;
                        """,
                        (span_id, parent_span_id, event_name, source_event_name, hook_name, timestamp_ms, timestamp_ms, os.getpid(), json.dumps({}), session_id)
                    )
                    row = cursor.fetchone()
                    if row:
                        _STATE["sequence_no"] = row[0]
                        sqlite_success = True
                    else:
                        _STATE["rejected"] = True
                        sqlite_success = True
                else:
                    cursor.execute(
                        """
                        INSERT INTO spans (span_id, parent_span_id, session_id, sequence_no, event_name, source_event_name, hook_name, timestamp_ms, updated_at_ms, pid, status, late_arrival, metadata)
                        SELECT ?, ?, s.session_id, COALESCE(MAX(sp.sequence_no), 0) + 1, ?, ?, ?, ?, ?, ?, 'running',
                               CASE WHEN s.status = 'finalizing' THEN 1 ELSE 0 END, ?
                        FROM sessions s
                        LEFT JOIN spans sp ON sp.session_id = s.session_id
                        WHERE s.session_id = ?
                          AND s.status IN ('running', 'finalizing')
                        GROUP BY s.session_id;
                        """,
                        (span_id, parent_span_id, event_name, source_event_name, hook_name, timestamp_ms, timestamp_ms, os.getpid(), json.dumps({}), session_id)
                    )
                    if cursor.rowcount > 0:
                        sqlite_success = True
                        cursor.execute("SELECT sequence_no FROM spans WHERE span_id = ?", (span_id,))
                        row = cursor.fetchone()
                        if row:
                            _STATE["sequence_no"] = row[0]
                    else:
                        _STATE["rejected"] = True
                        sqlite_success = True
                conn.commit()
            except sqlite3.DatabaseError as e:
                conn.rollback()
                _handle_write_corruption(db_path, e)
                raise
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

    try:
        _trigger_detached_maintenance_if_needed(event_name)
    except Exception:
        pass


def complete_hook_capture(output_payload: Mapping[str, Any]) -> None:
    if _disabled():
        return
    if not _STATE.get("active") or _STATE.get("completed"):
        return
    if _STATE.get("rejected"):
        _STATE["completed"] = True
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
    session_id = _session_id(raw_payload)
    if not _sqlite_disabled() and _STATE.get("sqlite_success") and span_id and session_id:
        sanitized_raw = _sanitize_value(raw_payload, bypass_capping=True)
        sanitized_eff = _sanitize_value(effective_payload, bypass_capping=True)
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
                workspace_root = _workspace_root(raw_payload)
                ts_str = _timestamp(raw_payload)
                timestamp_ms = _timestamp_to_ms(ts_str)
                _backfill_parent_session_id(conn, session_id, workspace_root, timestamp_ms)

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
            except sqlite3.DatabaseError as e:
                conn.rollback()
                _handle_write_corruption(db_path, e)
                raise
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        except Exception:
            pass

        if sqlite_success:
            sequence_no = _STATE.get("sequence_no")
            if sequence_no is not None:
                parent_span_id = raw_payload.get("parent_span_id") or raw_payload.get("parentSpanId")
                _write_transcript_chunk(
                    session_id=session_id,
                    span_id=span_id,
                    parent_span_id=parent_span_id,
                    event_name=event_name,
                    source_event_name=source_event_name,
                    hook_record=hook_record,
                    db_path=db_path,
                    busy_timeout=busy_timeout,
                    timestamp_ms=timestamp_ms,
                    sanitized_raw=sanitized_raw,
                    sanitized_eff=sanitized_eff,
                    meta=meta,
                    sequence_no=sequence_no
                )
                
            if event_name in TERMINAL_EVENT_NAMES:
                _finalize_session(session_id, db_path, busy_timeout)

    if not sqlite_success and not _STATE.get("rejected"):
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

    try:
        _trigger_detached_maintenance_if_needed(event_name)
    except Exception:
        pass

    _STATE["completed"] = True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--maintenance":
        _run_maintenance_work()
        sys.exit(0)

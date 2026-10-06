"""Worktree-local durable coordination with short, bounded SQLite transactions."""
from __future__ import annotations

from contextlib import closing
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import sys
import time
from typing import Callable, Any
import uuid


class LifecycleError(ValueError):
    def __init__(self, code: str, cause: str, *, exit_code: int = 2,
                 retry_eligible: bool = False, next_action: str | None = None) -> None:
        super().__init__(cause)
        self.code = code
        self.exit_code = exit_code
        self.retry_eligible = retry_eligible
        self.next_action = next_action or "Restore valid configured context at the next eligible integration event."


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def uid() -> str:
    return str(uuid.uuid4())


def local_path(root: Path, relative: str) -> Path:
    """Resolve an owned local path without traversing links or leaving this worktree."""
    target = root / relative
    if not target.is_relative_to(root) or any(part in ("..", ".") for part in Path(relative).parts):
        raise LifecycleError("BINDING_INVALID", "runtime path leaves the worktree")
    current = root
    for part in Path(relative).parts:
        current /= part
        if current.is_symlink():
            raise LifecycleError("BINDING_INVALID", "runtime/configuration path is linked or ambiguous")
    if not target.resolve().is_relative_to(root):
        raise LifecycleError("BINDING_INVALID", "runtime path resolves outside the worktree")
    return target


def write_private(path: Path, value: object) -> None:
    """Write one ignored owner-only runtime file without disclosing its content."""
    temporary = path.with_name(f".{uid()}.tmp")
    try:
        with os.fdopen(os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
                       "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


class StateStore:
    """One aggregate runtime record, atomically revised in a local SQLite row.

    Callbacks only change deterministic records. Guidance loading and subprocess
    checks run outside transactions. Public status projects safe fields only.
    """
    def __init__(self, root: Path, state_dir: str, budget: float = 2, attempts: int = 3) -> None:
        self.root = root
        self.directory = local_path(root, state_dir)
        self.path = local_path(root, state_dir + "/brain.sqlite3")
        self.marker = local_path(root, state_dir + "/binding.json")
        self.budget = budget
        self.attempts = attempts
        self.remaining_contention = budget
        self.capabilities: dict[str, object] = {}

    def _connect(self, *, readonly: bool) -> sqlite3.Connection:
        if sys.version_info < (3, 12) or sqlite3.sqlite_version_info < (3, 15, 2):
            raise LifecycleError("RUNTIME_UNSUPPORTED", "Python 3.12+ and SQLite 3.15.2+ are required")
        if readonly:
            connection = sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True, timeout=0,
                                         isolation_level=None)
        else:
            connection = sqlite3.connect(self.path, timeout=0, isolation_level=None)
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA busy_timeout=0")
            if not readonly:
                connection.execute("PRAGMA journal_mode=DELETE")
                connection.execute("PRAGMA synchronous=EXTRA")
                if sys.platform == "darwin":
                    connection.execute("PRAGMA fullfsync=ON")
            self.capabilities = {
                "sqlite_version": sqlite3.sqlite_version,
                "journal_mode": connection.execute("PRAGMA journal_mode").fetchone()[0],
                "synchronous": connection.execute("PRAGMA synchronous").fetchone()[0],
                "foreign_keys": connection.execute("PRAGMA foreign_keys").fetchone()[0],
                "fullfsync_requested": sys.platform == "darwin" and not readonly,
                "fullfsync_observed": bool(connection.execute("PRAGMA fullfsync").fetchone()[0]),
                "filesystem_durability": "unverified", "access": "read_only" if readonly else "read_write",
            }
            if not readonly and (self.capabilities["journal_mode"] != "delete"
                                 or self.capabilities["synchronous"] != 3
                                 or self.capabilities["foreign_keys"] != 1):
                raise LifecycleError("RUNTIME_UNSUPPORTED", "required SQLite settings are unavailable")
            return connection
        except BaseException:
            connection.close()
            raise

    def initialize(self, repository_id: str, repository_root: str) -> None:
        if self.marker.exists() or self.path.exists():
            self.read()
            return
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        binding = {"schema_version": 1, "repository_id": repository_id,
                   "repository_root": repository_root, "worktree_root": str(self.root), "worktree_id": uid()}
        # Exclusive sentinel first: interruption can never make expected state
        # look like an empty queue on the next event.
        try:
            with os.fdopen(os.open(self.marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
                           "w", encoding="utf-8") as stream:
                json.dump(binding, stream)
                stream.flush()
                os.fsync(stream.fileno())
        except FileExistsError:
            self.read()
            return
        initial = binding | {"revision": 0, "sessions": {}, "invocations": {},
                             "owner": None, "ownership_generation": 0}
        try:
            with closing(self._connect(readonly=False)) as connection:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute("CREATE TABLE runtime (id INTEGER PRIMARY KEY CHECK(id=1), record TEXT NOT NULL)")
                connection.execute("INSERT INTO runtime VALUES (1, ?)", (json.dumps(initial),))
                connection.commit()
            os.chmod(self.path, 0o600)
        except sqlite3.Error as exc:
            raise LifecycleError("STATE_UNAVAILABLE", "expected state could not be initialized; preserve binding and recover", exit_code=1) from exc

    def _decode(self, connection: sqlite3.Connection) -> dict[str, Any]:
        row = connection.execute("SELECT record FROM runtime WHERE id=1").fetchone()
        if not row:
            raise ValueError("missing runtime record")
        from .config import _unique_object, _reject_constant, _finite_float
        options = {"object_pairs_hook": _unique_object, "parse_constant": _reject_constant, "parse_float": _finite_float}
        record = json.loads(row[0], **options)
        marker = json.loads(self.marker.read_text(encoding="utf-8"), **options)
        for field in ("schema_version", "repository_id", "repository_root", "worktree_root", "worktree_id"):
            if record[field] != marker[field]:
                raise ValueError("binding mismatch")
        if type(record["schema_version"]) is not int or record["schema_version"] != 1 or record["worktree_root"] != str(self.root):
            raise ValueError("unsupported or relocated state")
        validate_state(record)
        return record

    def read(self) -> dict[str, Any]:
        if not self.path.is_file() or not self.marker.is_file():
            raise LifecycleError("STATE_UNAVAILABLE", "expected local state or binding is missing; pending work is unknown", exit_code=1)
        for attempt in range(self.attempts):
            try:
                with closing(self._connect(readonly=True)) as connection:
                    return self._decode(connection)
            except sqlite3.OperationalError as exc:
                if "locked" in str(exc).lower() or "busy" in str(exc).lower():
                    if self._wait(attempt):
                        continue
                    raise LifecycleError("STATE_CONTENDED", "bounded contention exhausted while reading expected state; pending work remains", exit_code=1, retry_eligible=True) from exc
                raise LifecycleError("STATE_UNAVAILABLE", "expected local state is corrupt or unavailable; preserve recoverable files", exit_code=1) from exc
            except (sqlite3.Error, OSError, ValueError, KeyError, TypeError) as exc:
                raise LifecycleError("STATE_UNAVAILABLE", "expected local state is corrupt or has a mismatched binding; preserve recoverable files", exit_code=1) from exc
        raise LifecycleError("STATE_CONTENDED", "bounded state read exhausted", exit_code=1, retry_eligible=True)

    def _wait(self, attempt: int) -> bool:
        if attempt + 1 >= self.attempts or self.remaining_contention <= 0:
            return False
        before = time.monotonic()
        time.sleep(min((0.25, 0.75)[min(attempt, 1)], self.remaining_contention))
        self.remaining_contention = max(0, self.remaining_contention - (time.monotonic() - before))
        # One immediate final query is allowed after the remaining wait is
        # spent. Semantic/check time consumes none of this cumulative budget.
        return True

    def change(self, expected_revision: int, update: Callable[[dict[str, Any]], Any]) -> Any:
        for attempt in range(self.attempts):
            try:
                with closing(self._connect(readonly=False)) as connection:
                    connection.execute("BEGIN IMMEDIATE")
                    record = self._decode(connection)
                    if record["revision"] != expected_revision:
                        raise LifecycleError("STATE_CHANGED", "another operation changed state; reload at an eligible event", exit_code=1, retry_eligible=True)
                    result = update(record)
                    record["revision"] += 1
                    connection.execute("UPDATE runtime SET record=? WHERE id=1", (json.dumps(record),))
                    connection.commit()
                    return result
            except sqlite3.OperationalError as exc:
                if "locked" not in str(exc).lower() and "busy" not in str(exc).lower():
                    raise LifecycleError("STATE_UNAVAILABLE", "state write failed; preserve pending work", exit_code=1) from exc
                if not self._wait(attempt):
                    break
            except (sqlite3.Error, OSError, ValueError, KeyError, TypeError) as exc:
                if isinstance(exc, LifecycleError):
                    raise
                raise LifecycleError("STATE_UNAVAILABLE", "state write is unavailable; preserve pending work", exit_code=1) from exc
        raise LifecycleError("STATE_CONTENDED", "bounded state contention exhausted; pending work remains", exit_code=1, retry_eligible=True)


def validate_state(record: dict) -> None:
    """Reject structurally damaged operational records before projection or writes."""
    def object_fields(value: Any, required: set[str]) -> dict:
        if not isinstance(value, dict) or required - value.keys():
            raise ValueError("missing or invalid durable fields")
        return value

    def integer(value: Any, minimum: int = 0, maximum: int | None = None) -> None:
        if type(value) is not int or value < minimum or (maximum is not None and value > maximum):
            raise ValueError("invalid durable generation/count")

    def text(value: Any) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("invalid durable identity/text")

    def identity(value: Any) -> None:
        text(value)
        if str(uuid.UUID(value)) != value:
            raise ValueError("invalid durable UUID")

    def revision(value: Any) -> None:
        if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            raise ValueError("invalid durable revision")

    def number(value: Any) -> None:
        if type(value) not in (float, int) or not 0 < value <= sys.float_info.max or not math.isfinite(value):
            raise ValueError("invalid durable time")

    def boolean(value: Any) -> None:
        if type(value) is not bool:
            raise ValueError("invalid durable boolean")

    def scope(value: Any) -> None:
        fields = {"paths", "concepts", "actions", "dependencies", "providers", "runtimes"}
        item = object_fields(value, fields)
        if item.keys() != fields:
            raise ValueError("invalid durable scope")
        for values in item.values():
            if not isinstance(values, list):
                raise ValueError("invalid durable selector list")
            for part in values:
                text(part)

    object_fields(record, {"schema_version", "repository_id", "repository_root", "worktree_root", "worktree_id",
                           "revision", "sessions", "invocations", "owner", "ownership_generation"})
    identity(record["repository_id"])
    identity(record["worktree_id"])
    text(record["repository_root"])
    text(record["worktree_root"])
    integer(record["revision"])
    integer(record["ownership_generation"])
    object_fields(record["sessions"], set())
    object_fields(record["invocations"], set())
    for key, session in record["sessions"].items():
        revision(key)
        object_fields(session, {"id", "task_id", "status", "checkpoint", "scope", "input_generation",
                                "input_revision", "agents", "obligations", "root_agent"})
        identity(session["id"])
        identity(session["task_id"])
        if session["status"] not in ("active", "awaiting_user", "ready_to_complete", "completed", "incomplete", "paused", "cancelled") or session["checkpoint"] not in ("active", "awaiting_user", "ready_to_complete", "completed"):
            raise ValueError("invalid durable work-session status")
        integer(session["input_generation"], 1)
        revision(session["input_revision"])
        scope(session["scope"])
        object_fields(session["agents"], {session["root_agent"]})
        object_fields(session["obligations"], set())
        for agent_id, agent in session["agents"].items():
            revision(agent_id)
            object_fields(agent, {"id", "parent", "context_generation", "status", "scope", "assigned"})
            identity(agent["id"])
            if agent["parent"] is not None:
                identity(agent["parent"])
            integer(agent["context_generation"], 1)
            scope(agent["scope"])
            if agent["status"] not in ("active", "completed", "incomplete") or not isinstance(agent["assigned"], list) or any(value != "scope_review" for value in agent["assigned"]):
                raise ValueError("invalid durable child assignment/status")
            if "delivery" in agent:
                delivery = object_fields(agent["delivery"], {"complete", "available", "context_generation", "input_generation", "input_revision", "guidance_revision", "config_revision", "delivered_at"})
                boolean(delivery["complete"])
                boolean(delivery["available"])
                integer(delivery["context_generation"], 1)
                integer(delivery["input_generation"], 1)
                for field in ("input_revision", "guidance_revision", "config_revision"):
                    revision(delivery[field])
                number(delivery["delivered_at"])
        for obligation_id, obligation in session["obligations"].items():
            identity(obligation_id)
            object_fields(obligation, {"id", "kind", "scope", "input_generation", "status", "stage_outcome",
                                      "attempt_count", "semantic_repairs", "assigned_agent_id", "check_receipts"})
            if obligation["id"] != obligation_id or obligation["kind"] not in ("learn", "child_review") or obligation["status"] not in ("pending", "active", "completed") or obligation["stage_outcome"] not in ("no_change", "changed", "incomplete"):
                raise ValueError("invalid durable obligation")
            scope(obligation["scope"])
            integer(obligation["input_generation"], 1)
            integer(obligation["attempt_count"], 0, 3)
            integer(obligation["semantic_repairs"], 0, 1)
            if obligation["assigned_agent_id"] is not None:
                identity(obligation["assigned_agent_id"])
            for field in ("retry_needed", "repair_exhausted"):
                if field in obligation:
                    boolean(obligation[field])
            if "owner_agent_id" in obligation:
                identity(obligation["owner_agent_id"])
                integer(obligation["owner_generation"], 1)
            if "prepared" in obligation:
                revision(obligation["prepared"])
            if "publication" in obligation:
                publication = object_fields(obligation["publication"], {"id", "history_path", "status", "affected_ids", "paths"})
                identity(publication["id"])
                text(publication["history_path"])
                if publication["status"] not in ("prepared", "intent", "checked", "published", "completed", "reversed", "conflict"):
                    raise ValueError("invalid durable publication status")
                for field in ("affected_ids", "paths"):
                    if not isinstance(publication[field], list):
                        raise ValueError("invalid durable publication members")
                    for part in publication[field]:
                        identity(part) if field == "affected_ids" else text(part)
            if not isinstance(obligation["check_receipts"], list):
                raise ValueError("invalid durable receipts")
            for receipt in obligation["check_receipts"]:
                object_fields(receipt, {"id", "checker_id", "exit_code", "timed_out", "input_revision", "config_revision", "owner_generation", "attempt_id", "checked_at"})
                identity(receipt["id"])
                identity(receipt["attempt_id"])
                text(receipt["checker_id"])
                revision(receipt["input_revision"])
                revision(receipt["config_revision"])
                integer(receipt["owner_generation"], 1)
                boolean(receipt["timed_out"])
                number(receipt["checked_at"])
                if receipt["exit_code"] is not None and type(receipt["exit_code"]) is not int:
                    raise ValueError("invalid durable check exit")
    if record["owner"] is not None:
        owner = object_fields(record["owner"], {"obligation_id", "agent_id", "generation", "expires_at"})
        identity(owner["obligation_id"])
        identity(owner["agent_id"])
        integer(owner["generation"], 1)
        number(owner["expires_at"])
    for key, invocation in record["invocations"].items():
        revision(key)
        object_fields(invocation, {"file", "attempt_id", "stage", "session_key", "agent_key", "agent_id", "obligation_id", "owner_generation", "input_generation", "context_generation", "input_revision", "integration", "config_path", "expires_at", "revoked"})
        for field in ("attempt_id", "agent_id", "obligation_id"):
            identity(invocation[field])
        for field in ("owner_generation", "input_generation", "context_generation"):
            integer(invocation[field], 1)
        revision(invocation["input_revision"])
        number(invocation["expires_at"])
        boolean(invocation["revoked"])
        text(invocation["file"])
        text(invocation["config_path"])
        if invocation["stage"] != "learn":
            raise ValueError("unsupported durable stage")
        integration = object_fields(invocation["integration"], {"id", "core_version", "adapter_version", "certification_id", "config_revision"})
        identity(integration["certification_id"])
        revision(integration["config_revision"])
        for field in ("id", "core_version", "adapter_version"):
            text(integration[field])
        session = record["sessions"][invocation["session_key"]]
        if session["agents"][invocation["agent_key"]]["id"] != invocation["agent_id"] or invocation["obligation_id"] not in session["obligations"]:
            raise ValueError("invalid durable registration references")

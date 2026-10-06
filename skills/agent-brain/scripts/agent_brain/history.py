"""Portable exact inverse history and durable pending-operation indications."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from contextlib import contextmanager

from .state import LifecycleError, digest, local_path, write_private

MAX_HISTORY_BYTES = 8 * 1024 * 1024


def validate_size(journal: dict, *, reserve: int = 0) -> None:
    size = len(json.dumps(journal, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    if size + reserve > MAX_HISTORY_BYTES:
        raise LifecycleError("PUBLICATION_TOO_LARGE", "exact publication history exceeds the 8 MiB limit; reduce the coherent proposed set without truncating evidence or inverse bytes")


def revision(content: str | None) -> str | None:
    return hashlib.sha256(content.encode("utf-8")).hexdigest() if content is not None else None


def text_bytes(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


@contextmanager
def exclusive(store):
    """OS-owned publication lock releases on process death, with bounded waits."""
    path = local_path(store.root, str(store.directory.relative_to(store.root)) + "/publication.lock")
    with open(path, "a+b") as stream:
        if os.name == "posix":
            import fcntl
            acquire = lambda: fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            release = lambda: fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        else:
            import msvcrt
            if path.stat().st_size == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            acquire = lambda: msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            release = lambda: msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        for attempt in range(store.attempts):
            try:
                acquire()
                break
            except OSError as exc:
                if not store._wait(attempt):
                    raise LifecycleError("PUBLICATION_CONTENDED", "bounded publication contention exhausted; pending set retained", exit_code=1, retry_eligible=True) from exc
        try:
            yield
        finally:
            release()


def sync_directory(directory: Path) -> None:
    if os.name == "posix":
        descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def replace_content(path: Path, content: str | None) -> None:
    """Individual destination-local replacement; no set-wide atomicity claim."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        path.unlink(missing_ok=True)
    else:
        descriptor, temporary = tempfile.mkstemp(prefix=".agent-brain-", dir=path.parent)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content.encode("utf-8"))
                stream.flush()
                os.fsync(stream.fileno())
            if path.exists():
                os.chmod(temporary, path.stat().st_mode & 0o777)
            os.replace(temporary, path)
        finally:
            Path(temporary).unlink(missing_ok=True)
    sync_directory(path.parent)


def save(root: Path, path: str, journal: dict) -> None:
    journal["integrity"] = digest({key: value for key, value in journal.items() if key != "integrity"})
    validate_size(journal)
    target = local_path(root, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_private(target, journal)
    sync_directory(target.parent)


def read(root: Path, path: str) -> dict:
    try:
        from .config import _unique_object, _reject_constant, _finite_float, _uuid, _relative_path, _string
        raw = local_path(root, path).read_bytes()
        if len(raw) > MAX_HISTORY_BYTES:
            raise ValueError("history exceeds finite size bound")
        journal = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_reject_constant, parse_float=_finite_float)
        if not isinstance(journal, dict):
            raise ValueError("history is not an object")
        if journal["integrity"] != digest({key: value for key, value in journal.items() if key != "integrity"}):
            raise ValueError("journal integrity mismatch")
        if type(journal["schema_version"]) is not int or journal["schema_version"] != 1 or not isinstance(journal["changes"], list) or not journal["changes"]:
            raise ValueError("invalid history")
        for field in ("id", "obligation_id", "work_session_id", "agent_id", "attempt_id"):
            _uuid(journal[field], field)
        if type(journal["owner_generation"]) is not int or journal["owner_generation"] < 1:
            raise ValueError("invalid history ownership generation")
        for field in ("base_input_revision", "config_revision"):
            value = journal[field]
            if not isinstance(value, str) or len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
                raise ValueError("invalid history input revision")
        for field in ("rationale", "intent"):
            _string(journal[field], field)
        if not isinstance(journal["evidence"], list) or not isinstance(journal["check_receipts"], list):
            raise ValueError("invalid history evidence/checks")
        from .lifecycle import scope_record
        if scope_record(journal["scope"]) != journal["scope"]:
            raise ValueError("invalid history scope")
        if journal["status"] not in ("prepared", "intent", "published", "checked", "completed", "reversed", "conflict"):
            raise ValueError("invalid history status")
        if not isinstance(journal["relevant_files"], dict) or not isinstance(journal["payload"], dict) or not isinstance(journal["affected_ids"], list):
            raise ValueError("invalid history records")
        if "source_work" in journal:
            work = journal["source_work"]
            if not isinstance(work, list) or work != sorted(set(work)):
                raise ValueError("invalid history source work")
            for source in work:
                _relative_path(source, "history source identity")
        for identity in journal["affected_ids"]:
            _uuid(identity, "affected identity")
        for key, value in journal["relevant_files"].items():
            _relative_path(key, "relevant input path")
            if not isinstance(value, str) or len(value) != 64:
                raise ValueError("invalid relevant input revision")
        seen = set()
        for item in journal["changes"]:
            if not isinstance(item, dict) or item.keys() != {"path", "before", "after", "before_revision", "after_revision"}:
                raise ValueError("invalid history change")
            _relative_path(item["path"], "history path")
            if item["path"] in seen:
                raise ValueError("duplicate history path")
            seen.add(item["path"])
            for field in ("before", "after"):
                if item[field] is not None and not isinstance(item[field], str):
                    raise ValueError("invalid history content")
            local_path(root, item["path"])
            if (revision(item["before"]) != item["before_revision"] or revision(item["after"]) != item["after_revision"]):
                raise ValueError("history bytes differ from recorded hashes")
        return journal
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
        raise LifecycleError("PUBLICATION_HISTORY_UNAVAILABLE", "preserve missing/corrupt publication history; affected context is unavailable", exit_code=1) from exc


def pending_path(config) -> str:
    return config.state_dir + "/publication.json"


def pending(root: Path, config, store=None) -> dict | None:
    from .lifecycle import read_json
    path = local_path(root, pending_path(config))
    if not path.exists():
        from .state import StateStore
        store = store or StateStore(root, config.state_dir, float(config.limits["contention_seconds"]))
        if not store.path.exists() and not store.marker.exists():
            return None
        state = store.read()
        found = []
        for session in state["sessions"].values():
            for obligation in session["obligations"].values():
                publication = obligation.get("publication")
                if publication is None or obligation["status"] == "completed":
                    continue
                journal = read(root, publication["history_path"])
                if journal["status"] in ("intent", "published", "checked") or (obligation["kind"] == "dream" and journal["status"] == "completed"):
                    found.append({"history_path": publication["history_path"], "paths": [item["path"] for item in journal["changes"]]})
        if len(found) > 1:
            raise LifecycleError("PUBLICATION_HISTORY_UNAVAILABLE", "multiple pending publication sets require reconciliation", exit_code=1)
        return found[0] if found else None
    try:
        value = read_json(path.read_text(encoding="utf-8"))
        if value.keys() != {"history_path", "paths"} or not isinstance(value["paths"], list):
            raise ValueError("invalid pending publication")
        for part in value["paths"]:
            local_path(root, part)
        journal = read(root, value["history_path"])
        if value["paths"] != [item["path"] for item in journal["changes"]]:
            raise ValueError("pending paths differ from exact history set")
        return value
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
        raise LifecycleError("PUBLICATION_HISTORY_UNAVAILABLE", "pending publication is missing or corrupt; preserve affected files", exit_code=1) from exc


def mark_pending(root: Path, config, path: str, changes: list[dict]) -> None:
    target = local_path(root, pending_path(config))
    write_private(target, {"history_path": path, "paths": [item["path"] for item in changes]})
    sync_directory(target.parent)


def clear_pending(root: Path, config) -> None:
    path = local_path(root, pending_path(config))
    path.unlink(missing_ok=True)
    sync_directory(path.parent)

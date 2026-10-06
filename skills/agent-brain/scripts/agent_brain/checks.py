"""Attributable review validation and bounded trusted argument-list checks."""
from __future__ import annotations

import os
from pathlib import Path
import signal
import subprocess
import time

from .config import _keys, _object, _relative_path, _string
from .records import AgentBrainConfig
from .state import LifecycleError, digest, local_path


def checked_review(payload: dict, config: AgentBrainConfig, root: Path,
                   scope: dict, guidance: dict) -> tuple[list[dict], str]:
    from .lifecycle import file_revision, scope_record
    _keys(payload, "stage input", {"schema_version", "outcome", "review"})
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1 or payload["outcome"] != "no_change":
        raise LifecycleError("REVIEW_INVALID", "M3 supports only versioned scoped no-change reviews")
    review = _object(payload["review"], "review")
    _keys(review, "review", {"scope", "guidance", "sources", "note"})
    _string(review["note"], "review note")
    if scope_record(review["scope"]) != scope:
        raise LifecycleError("REVIEW_SCOPE_MISMATCH", "reviewed scope differs from the assigned obligation")
    expected = [{key: item[key] for key in ("id", "content_revision", "input_revision")} for item in guidance["units"]]
    if review["guidance"] != expected or not guidance["complete"]:
        raise LifecycleError("GUIDANCE_REVIEW_STALE", "review must identify every currently delivered guidance revision in order")
    if not isinstance(review["sources"], list) or not review["sources"]:
        raise LifecycleError("REVIEW_EVIDENCE_REQUIRED", "review requires attributable current source identities and verification notes")
    known_sources = {item["path"] for item in guidance["artifacts"]}
    for selector in scope["paths"]:
        if not any(char in selector for char in "*?["):
            known_sources.add(selector)
    seen = set()
    for source in review["sources"]:
        item = _object(source, "review source")
        _keys(item, "review source", {"path", "revision", "note"})
        path = _relative_path(item["path"], "review source path")
        _string(item["note"], "source verification note")
        if path not in known_sources or path in seen:
            raise LifecycleError("REVIEW_SOURCE_INVALID", "review source is duplicated or outside current delivered/assigned scope")
        seen.add(path)
        actual = local_path(root, path)
        if not actual.is_file() or item["revision"] != file_revision(actual):
            raise LifecycleError("REVIEW_SOURCE_STALE", "review source bytes no longer match their attributable revision")

    results = []
    deadline = time.monotonic() + float(config.limits["check_timeout_seconds"])
    trusted = {item["id"]: item for item in config.checks["trusted"]}
    for checker_id in config.checks["required"]:
        if checker_id in ("guidance", "review_sources"):
            results.append({"checker_id": checker_id, "exit_code": 0, "timed_out": False})
            continue
        checker = trusted[checker_id]
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            results.append({"checker_id": checker_id, "exit_code": None, "timed_out": True})
            continue
        process = None
        try:
            process = subprocess.Popen(checker["argv"], cwd=root, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False,
                start_new_session=os.name == "posix")
            code = process.wait(timeout=min(float(checker["timeout_seconds"]), remaining))
            results.append({"checker_id": checker_id, "exit_code": code, "timed_out": False})
        except subprocess.TimeoutExpired:
            _stop(process)
            results.append({"checker_id": checker_id, "exit_code": None, "timed_out": True})
        except OSError:
            results.append({"checker_id": checker_id, "exit_code": None, "timed_out": False})
        except BaseException:
            if process is not None:
                _stop(process)
            raise
    return results, digest(payload)


def _stop(process: subprocess.Popen) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass
    process.wait()

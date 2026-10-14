#!/usr/bin/env python3
# Generated from hooks/families/scan_secrets.py by scripts/generate-hooks.py. Do not edit.
from __future__ import annotations

import codecs
import contextlib
import json
import os
import re
import shutil
import signal
import stat
import sys
import tempfile
import time
import unicodedata
from collections.abc import Iterator
from datetime import datetime, timezone
from typing import BinaryIO
from pathlib import Path, PurePosixPath

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.common import emit_json, read_json_input  # noqa: E402

import hashlib as _diag_hashlib
import heapq as _diag_heapq
import json as _diag_json
import os as _diag_os
from pathlib import Path as _DiagPath
import re as _diag_re
import stat as _diag_stat
import sys as _diag_sys
import time as _diag_time
import unicodedata as _diag_unicode


class _DiagnosticsUnavailable(Exception):
    """Fixed cause, never a filesystem exception or input string."""


def _diag_unsafe(info):
    return (_diag_stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & 0x400))


def _diag_directory_flags():
    if not (hasattr(_diag_os, "O_NOFOLLOW") and hasattr(_diag_os, "O_DIRECTORY")
            and _diag_os.open in _diag_os.supports_dir_fd
            and _diag_os.stat in _diag_os.supports_dir_fd
            and _diag_os.scandir in _diag_os.supports_fd):
        raise _DiagnosticsUnavailable("limited_platform")
    return _diag_os.O_RDONLY | _diag_os.O_DIRECTORY | _diag_os.O_NOFOLLOW


def _diag_open_directory(path):
    """Retain no-follow descriptors for every absolute path component."""
    flags = _diag_directory_flags()
    path = _DiagPath(_diag_os.path.abspath(path))
    fd = _diag_os.open(path.anchor, flags)
    try:
        for part in path.parts[1:]:
            new_fd = _diag_os.open(part, flags, dir_fd=fd)
            _diag_os.close(fd)
            fd = new_fd
        return fd
    except BaseException:
        _diag_os.close(fd)
        raise


def _diag_label(value):
    # Inspect the entire bounded filesystem label before clipping.
    if _diag_re.search(r"(?i)(gh[pousr]_|github_pat_|sk_(?:live|test)_|rk_live_|xox[baprs]-|AKIA|ASIA|https?[:/]|auth|password|passwd|secret|token|bearer)", value):
        return "[REDACTED]"
    value = "".join(char for char in value if not _diag_unicode.category(char).startswith("C") and char not in "\u2028\u2029")
    try:
        return value.encode("utf-8")[:DIAG_LIMITS["label_bytes"]].decode("utf-8", "ignore")
    except UnicodeError:
        return "[REDACTED]"


def _diag_inventory(deadline):
    report = {"health": "unknown", "kind": "worktree_metadata", "pending_status": "unknown",
              "index_snapshots": "unknown", "index_bytes": None, "repository_layout": "unknown",
              "inventory_complete": False, "directories_observed": 0, "entries_observed": 0,
              "regular_observed": 0, "unsafe_observed": 0, "records_omitted": 0,
              "records": [], "causes": [], "ranking": "largest_observed"}
    heap = []
    unsafe = []
    flags = None

    def note(cause):
        if cause not in report["causes"]:
            report["causes"].append(cause)

    def walk(fd, prefix, depth):
        if _diag_time.monotonic() >= deadline:
            note("time_limit")
            return
        report["directories_observed"] += 1
        with _diag_os.scandir(fd) as entries:
            for entry in entries:
                if _diag_time.monotonic() >= deadline:
                    note("time_limit")
                    return
                if report["entries_observed"] >= DIAG_LIMITS["entries"]:
                    note("entries_limit")
                    return
                report["entries_observed"] += 1
                try:
                    info = _diag_os.stat(entry.name, dir_fd=fd, follow_symlinks=False)
                except OSError:
                    note("metadata_unavailable")
                    continue
                if entry.name == ".git":
                    if depth == 0:
                        report["repository_layout"] = "directory" if _diag_stat.S_ISDIR(info.st_mode) and not _diag_unsafe(info) else "linked_or_unknown"
                        if report["repository_layout"] == "directory":
                            git_fd = None
                            try:
                                git_fd = _diag_os.open(entry.name, flags, dir_fd=fd)
                                index_info = _diag_os.stat("index", dir_fd=git_fd, follow_symlinks=False)
                                if _diag_stat.S_ISREG(index_info.st_mode) and not _diag_unsafe(index_info):
                                    report["index_bytes"] = index_info.st_size
                            except OSError:
                                pass
                            finally:
                                if git_fd is not None:
                                    _diag_os.close(git_fd)
                    continue
                label = _diag_label(prefix + entry.name)
                if _diag_unsafe(info) or not (_diag_stat.S_ISDIR(info.st_mode) or _diag_stat.S_ISREG(info.st_mode)):
                    report["unsafe_observed"] += 1
                    if len(unsafe) < DIAG_LIMITS["unsafe_records"]:
                        unsafe.append({"label": label, "kind": "unsafe_type", "size": None, "pending_status": "unknown"})
                    continue
                if _diag_stat.S_ISDIR(info.st_mode):
                    if depth >= DIAG_LIMITS["depth"]:
                        note("depth_limit")
                        continue
                    if report["directories_observed"] >= DIAG_LIMITS["directories"]:
                        note("directories_limit")
                        continue
                    child = None
                    try:
                        child = _diag_os.open(entry.name, flags, dir_fd=fd)
                        opened = _diag_os.fstat(child)
                        if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                            note("metadata_changed")
                            continue
                        walk(child, prefix + entry.name + "/", depth + 1)
                    except OSError:
                        note("metadata_unavailable")
                    finally:
                        if child is not None:
                            _diag_os.close(child)
                    if "time_limit" in report["causes"] or "entries_limit" in report["causes"]:
                        return
                else:
                    report["regular_observed"] += 1
                    record = (info.st_size, report["entries_observed"], label)
                    capacity = DIAG_LIMITS["records"] - DIAG_LIMITS["unsafe_records"]
                    if len(heap) < capacity:
                        _diag_heapq.heappush(heap, record)
                    elif record[:2] > heap[0][:2]:
                        _diag_heapq.heapreplace(heap, record)
    root = None
    try:
        if _diag_time.monotonic() >= deadline:
            raise _DiagnosticsUnavailable("time_limit")
        flags = _diag_directory_flags()
        root = _diag_os.open(".", flags)
        walk(root, "", 0)
        report["inventory_complete"] = not report["causes"]
        report["health"] = "observed" if report["inventory_complete"] else "incomplete"
    except _DiagnosticsUnavailable as error:
        note(str(error))
        report["health"] = "limited" if str(error) == "limited_platform" else "incomplete"
    except OSError:
        note("metadata_unavailable")
        report["health"] = "incomplete"
    finally:
        if root is not None:
            _diag_os.close(root)
    records = [{"size": size, "label": label, "kind": "regular", "pending_status": "unknown"}
               for size, _, label in sorted(heap, reverse=True)] + unsafe
    for index, record in enumerate(records, 1):
        record["id"] = "candidate-%04d" % index
    report["records"] = records
    report["records_omitted"] = report["regular_observed"] + report["unsafe_observed"] - len(records)
    return report


def _diag_read_fixed(root, relative, limit, deadline):
    """Read only fixed owned relative assets/settings, never config-selected paths."""
    if _diag_time.monotonic() >= deadline:
        raise _DiagnosticsUnavailable("time_limit")
    parts = _DiagPath(relative).parts
    if not parts or _DiagPath(relative).is_absolute() or any(part in (".", "..") for part in parts):
        raise _DiagnosticsUnavailable("invalid_installation_metadata")
    try:
        parent = _diag_open_directory(root)
    except OSError:
        raise _DiagnosticsUnavailable("unavailable") from None
    fd = None
    try:
        for part in parts[:-1]:
            new = _diag_os.open(part, _diag_directory_flags(), dir_fd=parent)
            _diag_os.close(parent)
            parent = new
        before = _diag_os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        if _diag_unsafe(before) or not _diag_stat.S_ISREG(before.st_mode):
            raise _DiagnosticsUnavailable("unsafe_type")
        if before.st_size > limit:
            raise _DiagnosticsUnavailable("bytes_limit")
        fd = _diag_os.open(parts[-1], _diag_os.O_RDONLY | _diag_os.O_NOFOLLOW | _diag_os.O_NONBLOCK, dir_fd=parent)
        opened = _diag_os.fstat(fd)
        if not _diag_stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise _DiagnosticsUnavailable("metadata_changed")
        raw = bytearray()
        while len(raw) <= limit:
            if _diag_time.monotonic() >= deadline:
                raise _DiagnosticsUnavailable("time_limit")
            chunk = _diag_os.read(fd, min(65536, limit + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
        after = _diag_os.fstat(fd)
        if len(raw) > limit:
            raise _DiagnosticsUnavailable("bytes_limit")
        if (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise _DiagnosticsUnavailable("metadata_changed")
        return bytes(raw), opened
    except FileNotFoundError:
        raise _DiagnosticsUnavailable("missing") from None
    except OSError:
        raise _DiagnosticsUnavailable("unavailable") from None
    finally:
        _diag_os.close(parent)
        if fd is not None:
            _diag_os.close(fd)


def _diag_assets(script, deadline):
    records = []
    total = 0
    for name, expected in DIAG_ASSETS[:DIAG_LIMITS["assets"]]:
        try:
            raw, info = _diag_read_fixed(_DiagPath(script).parent, name, DIAG_LIMITS["hash_bytes"] - total, deadline)
            total += len(raw)
            observed = _diag_hashlib.sha256(raw).hexdigest()
            state = "unverified" if expected is None else ("matches" if observed == expected else "drift")
            if _diag_os.name != "nt" and (info.st_mode & 0o022 or info.st_uid != _diag_os.getuid()):
                state = "unsafe_owner_or_mode"
            records.append({"asset": name, "state": state, "observed_sha256": observed})
        except _DiagnosticsUnavailable as error:
            records.append({"asset": name, "state": str(error)})
    complete = len(DIAG_ASSETS) <= DIAG_LIMITS["assets"] and all(item["state"] in ("matches", "unverified") for item in records)
    return {"health": "unverified" if complete else "degraded", "complete": complete,
            "hash_bytes": total, "records": records, "meaning": "on_disk_observation"}


def _diag_unique(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise _DiagnosticsUnavailable("duplicate_keys")
        obj[key] = value
    return obj


def _diag_fingerprint(event, matcher, handler):
    return _diag_json.dumps([event, matcher, handler], sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _diag_registrations(script, deadline):
    root = _DiagPath(script).parent
    root = root.parent if DIAG_PROVIDER == "codex" else root.parent.parent
    relative = "hooks/hooks.json" if DIAG_PROVIDER == "copilot" else ("hooks.json" if DIAG_PROVIDER == "codex" else "settings.json")
    result = {"health": "uncertain", "owned": 0, "unowned": 0, "duplicates": 0,
              "missing": len(DIAG_REGISTRATIONS), "events": [], "cause": "unknown"}
    try:
        raw, info = _diag_read_fixed(root, relative, DIAG_LIMITS["settings_bytes"], deadline)
        config = _diag_json.loads(raw.decode("utf-8"), object_pairs_hook=_diag_unique,
                                  parse_constant=lambda _: (_ for _ in ()).throw(_DiagnosticsUnavailable("malformed")))
        if not isinstance(config, dict) or not isinstance(config.get("hooks"), dict):
            raise _DiagnosticsUnavailable("malformed")
        if any(key in config for key in ("include", "includes", "extends")):
            raise _DiagnosticsUnavailable("config_includes")
        expected = set(DIAG_REGISTRATIONS)
        seen = set()
        matched = set()
        events = set()
        for event, groups in config["hooks"].items():
            if _diag_time.monotonic() >= deadline:
                raise _DiagnosticsUnavailable("time_limit")
            if not isinstance(groups, list):
                raise _DiagnosticsUnavailable("malformed")
            events.add(event if event in DIAG_EVENTS else "unknown")
            for group in groups:
                if not isinstance(group, dict):
                    raise _DiagnosticsUnavailable("malformed")
                handlers = [group] if DIAG_PROVIDER == "copilot" else group.get("hooks")
                if not isinstance(handlers, list):
                    raise _DiagnosticsUnavailable("malformed")
                for handler in handlers:
                    if not isinstance(handler, dict):
                        raise _DiagnosticsUnavailable("malformed")
                    key = _diag_fingerprint(event, None if DIAG_PROVIDER == "copilot" else group.get("matcher"), handler)
                    commands = {field: handler[field] for field in ("bash", "powershell", "command", "commandWindows") if field in handler}
                    duplicate_key = _diag_fingerprint(event, None, commands or handler)
                    if duplicate_key in seen:
                        result["duplicates"] += 1
                    seen.add(duplicate_key)
                    if key in expected:
                        result["owned"] += 1
                        matched.add(key)
                    else:
                        result["unowned"] += 1
        result["missing"] = len(expected - matched)
        result["events"] = sorted(events)
        result["cause"] = "observed"
        if _diag_os.name != "nt" and (info.st_mode & 0o022 or info.st_uid != _diag_os.getuid()):
            result["cause"] = "unsafe_owner_or_mode"
        elif not (result["missing"] or result["duplicates"] or result["unowned"]):
            result["health"] = "observed"
    except (_DiagnosticsUnavailable, UnicodeError, ValueError, RecursionError) as error:
        result["cause"] = str(error) if isinstance(error, _DiagnosticsUnavailable) else "malformed"
    return result


def diagnostics_collect(script_path, *, doctor=False):
    """Collect fixed installation observations and optional process-cwd metadata.

    script_path must be the loaded hook's own __file__, never a payload path.
    No required scanner/helper imports or audit initialization are needed.
    """
    deadline = _diag_time.monotonic() + DIAG_LIMITS["seconds"]
    report = {"schema": "hooks-diagnostics-v1", "provider": DIAG_PROVIDER,
              "policy_limits": DIAG_POLICY_LIMITS,
              "bootstrap": {"health": "loaded", "embedded_build": DIAG_BUILD,
                            "origin": "source_or_installed_unverified", "profile": "metadata-v1"},
              "security": {"health": "unknown", "outcome": "not_scanned"},
              "audit": {"health": "unknown", "outcome": "not_attempted"},
              "repository": {"health": "not_collected", "pending_status": "unknown", "index_snapshots": "unknown"}}
    report["assets"] = _diag_assets(script_path, deadline)
    report["registrations"] = _diag_registrations(script_path, deadline)
    if not doctor:
        report["repository"] = _diag_inventory(deadline)
    return report


def diagnostics_encode(report, *, wrap=None):
    """Preserve counts/health/largest sizes while bounding the entire response."""
    repository = report["repository"]

    def encode():
        text = _diag_json.dumps(report, ensure_ascii=True, separators=(",", ":"))
        output = text if wrap is None else _diag_json.dumps(wrap(text), ensure_ascii=True, separators=(",", ":"))
        return (output + "\n").encode("utf-8")

    raw = encode()
    if len(raw) > DIAG_LIMITS["response_bytes"]:
        report["response_truncated"] = True
        for record in repository.get("records", []):
            record.pop("label", None)
        raw = encode()
    while len(raw) > DIAG_LIMITS["response_bytes"] and repository.get("records"):
        repository["records"].pop()
        repository["records_omitted"] += 1
        raw = encode()
    while len(raw) > DIAG_LIMITS["response_bytes"] and report["assets"]["records"]:
        report["assets"]["records"].pop()
        report["assets"]["details_omitted"] = report["assets"].get("details_omitted", 0) + 1
        raw = encode()
    return raw

# BEGIN PROVIDER ADAPTER
DIAG_PROVIDER = 'gemini'
DIAG_LIMITS = {'directories': 1024, 'entries': 4096, 'records': 256, 'unsafe_records': 16, 'depth': 32, 'label_bytes': 160, 'seconds': 1.0, 'response_bytes': 16384, 'assets': 64, 'hash_bytes': 1048576, 'settings_bytes': 262144}
DIAG_BUILD = 'f74e7cd0b165167b45b68b37485be3ca0151a68b62c263d0c1e61a57eec83348'
DIAG_ASSETS = [('helpers/common.py', '475673132bfcc0081345e4142e8efdfddd5c47ceb6991793f1ac3df1752f26ac'), ('helpers/audit.py', '0a41a58053222793ff30388309ccd0196a1e85603d003f7965ff340d2d8a5661'), ('tool-guard.py', None), ('helpers/tool_guard_policy.py', 'ae9e918541a62874a329074d9cff4721ae9c37f42333a1360c1dcda23e63cab6'), ('scan-secrets.py', None), ('hooks-diagnostics.py', None)]
DIAG_POLICY_LIMITS = {'scope': 'canonical scanner constants and Guardian input-bound subset', 'scanner': {'MAX_FILES': 256, 'MAX_FILE_BYTES': 'not_defined', 'MAX_TOTAL_BYTES': 8388608, 'MAX_SCAN_SECONDS': 8.0}, 'guardian': {'MAX_SCAN_TEXT': 32768, 'MAX_NATIVE_DATA_BYTES': 65536, 'MAX_NATIVE_PATCH_BYTES': 262144, 'MAX_COMMAND_SEGMENTS': 128, 'MAX_COMMAND_TOKENS': 256, 'MAX_STRUCTURED_DEPTH': 32, 'MAX_STRUCTURED_NODES': 256, 'MAX_STRUCTURED_STRINGS': 128}}
DIAG_EVENTS = ['AfterAgent', 'AfterModel', 'AfterTool', 'BeforeAgent', 'BeforeModel', 'BeforeTool', 'BeforeToolSelection', 'Notification', 'PreCompress', 'SessionEnd', 'SessionStart']
DIAG_REGISTRATIONS = ['["SessionStart",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"SessionStart"},"type":"command"}]', '["SessionStart",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/skill-context-injector.py\\"","description":"Loads required skill files and injects them as context before each agent turn.","env":{"AGENTS_REQUIRED_SKILL_FILES":"caveman/SKILL.md"},"name":"skill-context-injector","type":"command"}]', '["AfterAgent",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"AfterAgent"},"type":"command"}]', '["BeforeAgent",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"BeforeAgent"},"type":"command"}]', '["BeforeModel",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"BeforeModel"},"type":"command"}]', '["AfterModel",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"AfterModel"},"type":"command"}]', '["BeforeToolSelection",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"BeforeToolSelection"},"type":"command"}]', '["BeforeTool","*",{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"BeforeTool"},"type":"command"}]', '["BeforeTool","*",{"command":"python \\"$HOME/.gemini/hooks/scripts/tool-guard.py\\"","description":"Blocks dangerous Gemini tool invocations using same policy patterns as Copilot tool-guard.","name":"tool-guard","type":"command"}]', '["BeforeTool","*",{"command":"python \\"$HOME/.gemini/hooks/scripts/scan-secrets.py\\"","description":"Scans workspace diffs for secrets before running any tool.","env":{"SCAN_MODE":"block","SCAN_SCOPE":"diff"},"name":"scan-secrets","type":"command"}]', '["BeforeTool","run_shell_command",{"command":"python \\"$HOME/.gemini/hooks/scripts/rtk-hook-gemini.py\\"","timeout":5000,"type":"command"}]', '["AfterTool",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"AfterTool"},"type":"command"}]', '["PreCompress",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"PreCompress"},"type":"command"}]', '["Notification",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"Notification"},"type":"command"}]', '["SessionEnd",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"SessionEnd"},"type":"command"}]', '["SessionEnd",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/scan-secrets.py\\"","description":"Scans modified files for potential secrets and logs env-file access during Gemini session shutdown.","env":{"SCAN_MODE":"warn"},"name":"scan-secrets","type":"command"}]']
# END PROVIDER ADAPTER


def _diagnostic_request(payload):
    if not isinstance(payload, dict):
        return False
    if DIAG_PROVIDER == "copilot":
        event, tool_key, args_key = "preToolUse", "toolName", "toolArgs"
        # Native Copilot CLI envelopes omit the event name.
        if payload.get("hook_event_name", event) != event or payload.get(tool_key) != "bash":
            return False
        metadata = {"sessionId": 256, "cwd": 8192}
    else:
        event = "PreToolUse" if DIAG_PROVIDER == "codex" else "BeforeTool"
        tool_key, args_key = "tool_name", "tool_input"
        tools = {"exec_command", "functions.exec_command"} if DIAG_PROVIDER == "codex" else {"run_shell_command"}
        if payload.get("hook_event_name") != event or type(payload.get(tool_key)) is not str or payload[tool_key] not in tools:
            return False
        metadata = {"session_id": 256, "cwd": 8192, "transcript_path": 8192, "tool_use_id": 256}
    if not set(payload) <= {"hook_event_name", tool_key, args_key, "timestamp", *metadata}:
        return False
    if any(type(payload[key]) is not str or len(payload[key]) > limit for key, limit in metadata.items() if key in payload):
        return False
    if "timestamp" in payload:
        stamp = payload["timestamp"]
        if DIAG_PROVIDER == "copilot":
            if type(stamp) is not int or not 0 <= stamp <= 9223372036854775807:
                return False
        elif type(stamp) is not str or len(stamp) > 128:
            return False
    args = payload.get(args_key)
    if not isinstance(args, dict):
        return False
    if DIAG_PROVIDER == "codex":
        if not {"cmd", "login"} <= set(args) or not set(args) <= {"cmd", "login", "max_output_tokens", "yield_time_ms"}:
            return False
        if args["cmd"] != "hooks-diagnostics-v1" or args["login"] is not False:
            return False
        return all(type(args[key]) is int and 0 <= args[key] <= 2147483647 for key in ("max_output_tokens", "yield_time_ms") if key in args)
    return args == {"command": "hooks-diagnostics-v1"}


# BEGIN PROVIDER ADAPTER
def _diagnostic_denial(text):
    reason = "scan-secrets diagnostics (request not executed):" + text
    if DIAG_PROVIDER == "gemini":
        return {"decision": "deny", "reason": reason}
    if DIAG_PROVIDER == "codex":
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}
    return {"continue": True, "permissionDecision": "deny", "permissionDecisionReason": reason,
            "hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": reason}}
# END PROVIDER ADAPTER


_SCAN_PAYLOAD = None
_SCAN_INPUT_ERROR = ""
_SCAN_INPUT_LOADED = False
_SCAN_STARTED = None


def _load_scan_payload():
    global _SCAN_PAYLOAD, _SCAN_INPUT_ERROR, _SCAN_INPUT_LOADED
    if _SCAN_INPUT_LOADED:
        return
    _SCAN_INPUT_LOADED = True
    try:
        _SCAN_PAYLOAD = read_json_input()
    except ValueError:
        _SCAN_INPUT_ERROR = "input_invalid"
    except Exception:
        _SCAN_INPUT_ERROR = "internal_error"


if __name__ == "__main__":
    # Recovery routing reads stdin before main. Ordinary scans inherit this
    # same start so transport cannot extend the overall security work budget.
    _SCAN_STARTED = time.monotonic()
    _load_scan_payload()
    if _diagnostic_request(_SCAN_PAYLOAD):
        _report = diagnostics_collect(__file__)
        _report.update(action="diagnostics", security_outcome="not_scanned", enforcement="deny", audit_outcome="not_attempted")
        _payload_cwd = _SCAN_PAYLOAD.get("cwd")
        # Inventory is process cwd only. Never resolve/stat/open the payload path.
        try:
            _location_verified = _payload_cwd is None or _payload_cwd == os.getcwd()
        except OSError:
            _location_verified = False
        _report["repository"]["repository_location"] = "process_cwd" if _location_verified else "unverified"
        sys.stdout.buffer.write(diagnostics_encode(_report, wrap=_diagnostic_denial))
        raise SystemExit(0)



SCRIPT_NAME = Path(__file__).name
TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".csv",
    ".env",
    ".go",
    ".h",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".md",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".svg",
    ".tf",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
MAX_FILES = 256
MAX_TOTAL_BYTES = 8388608
MAX_GIT_OUTPUT_BYTES = 8388608
MAX_SCAN_SECONDS = 8.0
GIT_COMPLETION_WAIT_SECONDS = 0.005
MAX_RETAINED_FINDINGS = 100
MAX_PROCESSED_FINDINGS = 1000
MAX_LOG_RECORD_BYTES = 65536
LOG_LOCK_TIMEOUT_SECONDS = 1.0
LOG_LOCK_POLL_SECONDS = 0.05
CANDIDATE_STAGED = "staged"
CANDIDATE_WORKTREE = "worktree"
CANDIDATE_UNTRACKED = "untracked"
CANDIDATE_UNMERGED_STAGES = ("unmerged-base", "unmerged-ours", "unmerged-theirs")
CANDIDATE_UNMERGED_WORKTREE = "unmerged-worktree"
INCOMPLETE_LOG: dict[str, object] | None = None
SCAN_ACTION = "scan"
SCAN_REPORT = None
SCAN_FINDINGS = []
SCAN_SECURITY_OUTCOME = "incomplete"
REPORT_BUILD = "d9249a2bd53c0685"
REPORT_PROVIDER = DIAG_PROVIDER


SCAN_PHASE = "initialization"
INCOMPLETE_CAUSES = {
    "git_unavailable": ("Git is unavailable", "Check Git availability in the hook environment.", ""),
    "audit_unavailable": ("audit storage is unavailable", "Check hook audit storage.", ""),
    "input_invalid": ("hook input is invalid", "Check the provider hook envelope.", ""),
    "git_failed": ("Git command failed", "Check repository accessibility and Git health.", ""),
    "git_capture_failed": ("Git capture failed", "Check temporary storage and Git execution.", ""),
    "git_descendant_running": ("Git left a running descendant", "Check Git process completion and retry.", ""),
    "git_head_invalid": ("Git HEAD verification failed", "Check repository HEAD and integrity.", ""),
    "git_output_invalid": ("Git output is invalid", "Check Git compatibility and repository integrity.", ""),
    "repository_unavailable": ("repository inspection failed", "Check repository accessibility.", ""),
    "scan_timeout": ("scan time limit reached", "Check repository size and Git responsiveness, then retry.", "seconds"),
    "git_timeout": ("Git time limit reached", "Check Git responsiveness and retry.", "seconds"),
    "snapshot_count_limit": ("candidate snapshot limit exceeded", "Check pending snapshots and unintended generated artifacts.", "snapshots"),
    "total_bytes_limit": ("total candidate byte limit exceeded", "Check pending scan size and unintended generated artifacts.", "bytes"),
    "git_output_limit": ("Git capture byte limit exceeded", "Check pending scan size and Git output volume.", "bytes"),
    "git_input_limit": ("Git request byte limit exceeded", "Check pending scan size.", "bytes"),
    "candidate_unsafe": ("candidate cannot be read safely", "Check pending file types and repository boundaries.", ""),
    "candidate_read_failed": ("candidate read failed", "Check pending file accessibility.", ""),
    "log_unavailable": ("scan log is unavailable", "Check secure hook log storage.", ""),
    "log_unsafe": ("scan log cannot be accessed safely", "Check secure hook log storage and file types.", ""),
    "log_lock_timeout": ("scan log lock time limit reached", "Check concurrent hook log writers and retry.", "seconds"),
    "log_configuration_invalid": ("scan log rotation configuration is invalid", "Check hook log rotation settings.", ""),
    "log_record_limit": ("scan log record byte limit exceeded", "Check hook log rotation settings and scan volume.", "bytes"),
    "internal_error": ("internal scanner failure", "Check the hook installation and retry.", ""),
}
INCOMPLETE_OPERATIONS = {
    "initialization", "input", "repository", "git_repository", "git_head",
    "git_candidates", "git_index", "git_diff", "git_command",
    "candidate_read", "candidate_scan", "scan_log",
}


class ScanFailure(RuntimeError):
    """Carry only scanner-owned vocabulary and bounded numeric measurements."""

    def __init__(self, cause: str, operation: str | None = None, **numbers: int) -> None:
        self.cause = cause if cause in INCOMPLETE_CAUSES else "internal_error"
        phase = SCAN_PHASE if operation is None else operation
        self.operation = phase if phase in INCOMPLETE_OPERATIONS else "initialization"
        self.numbers = {
            key: value for key, value in numbers.items()
            if key in {"exit_status", "measured", "limit", "seconds"}
            and type(value) is int
            and (-2147483648 if key == "exit_status" else 0) <= value <= 9223372036854775807
        }
        super().__init__(self.cause)

    def diagnostic(self) -> dict[str, object]:
        return {"cause": self.cause, "operation": self.operation, **self.numbers}

    def detail(self) -> str:
        description, recovery, unit = INCOMPLETE_CAUSES[self.cause]
        measures = []
        if "exit_status" in self.numbers:
            measures.append(f"exit status {self.numbers['exit_status']}")
        if "measured" in self.numbers:
            measures.append(f"measured {self.numbers['measured']} {unit}".rstrip())
        if "limit" in self.numbers:
            measures.append(f"limit {self.numbers['limit']} {unit}".rstrip())
        if "seconds" in self.numbers:
            measures.append(f"limit {self.numbers['seconds']} seconds")
        suffix = f" ({', '.join(measures)})" if measures else ""
        return f"{self.cause}/{self.operation}: {description}{suffix}. {recovery}"


class GitCommandError(ScanFailure):
    pass


class ScanSecurityError(ScanFailure):
    pass


class ScanLimitExceeded(ScanSecurityError):
    pass


def enforce_deadline(deadline: float | None) -> None:
    if deadline is not None and time.monotonic() >= deadline:
        raise ScanLimitExceeded("scan_timeout", seconds=int(MAX_SCAN_SECONDS))


def noop() -> None:
    emit_json({})
    raise SystemExit(0)
# BEGIN PROVIDER ADAPTER
def emit_block_denial(reason: str) -> None:
    emit_json({"decision": "deny", "reason": reason})
# END PROVIDER ADAPTER
import codecs
import re
import sys
import unicodedata

_STREAM_SEPARATORS = re.compile(r"[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]+")
_STREAM_BINARY_TABLE = bytes(value if value in (9, 10, 13) or 32 <= value <= 126
                             else 32 for value in range(256))
_STREAM_POSSIBLE_PREFIX = re.compile(r"gh|github_pat_|AKIA|sk_live_|xox")


def _stream_check():
    pass


def full_line_events(chunks, classification, check_budget=_stream_check):
    """Yield start/data/end tuples, omitting token-free empty full lines.

    Input is verified replay of at most 65536 bytes per chunk. Classification
    must already cover the entire snapshot. Empty lines advance numbering.
    """
    if classification not in ("text", "binary"):
        raise ValueError("invalid stream classification")
    decoder = codecs.getincrementaldecoder("utf-8")("replace")
    line_number = 1
    active = False
    pending_cr = False

    def decoded():
        for chunk in chunks:
            check_budget()
            if not isinstance(chunk, bytes) or len(chunk) > 65536:
                raise ValueError("invalid stream chunk")
            if classification == "binary":
                text = chunk.translate(_STREAM_BINARY_TABLE).decode("ascii")
            else:
                text = decoder.decode(chunk)
            for offset in range(0, len(text), 65536):
                yield text[offset:offset + 65536]
        if classification == "text":
            yield decoder.decode(b"", final=True)

    for text in decoded():
        check_budget()
        if not text:
            continue
        if pending_cr and text.startswith("\n"):
            text = text[1:]
        pending_cr = text.endswith("\r") if text else False
        position = 0
        for separator in _STREAM_SEPARATORS.finditer(text):
            if separator.start() > position:
                if not active:
                    yield ("start", line_number)
                    active = True
                yield ("data", text[position:separator.start()])
            if active:
                yield ("end", None)
                active = False
            run = separator.group()
            line_number += len(run) - run.count("\r\n")
            position = separator.end()
        if position < len(text):
            if not active:
                yield ("start", line_number)
                active = True
            yield ("data", text[position:])
    if active:
        yield ("end", None)


class StreamDiffError(ValueError):
    """Malformed verified diff; caller maps to git_output_invalid/git_diff."""


_STREAM_BYTE_SEPARATOR = re.compile(rb"\r\n|[\r\n]")
_STREAM_HUNK_START = re.compile(rb"\+[0-9]")
_STREAM_DIGITS = re.compile(rb"[0-9]*")


def _diff_byte_parts(chunks, check_budget):
    pending_cr = False
    first = bytearray()
    last = None
    for chunk in chunks:
        check_budget()
        if not isinstance(chunk, bytes) or len(chunk) > 65536:
            raise ValueError("invalid stream chunk")
        if not chunk:
            continue
        if len(first) < 11:
            first.extend(chunk[:11 - len(first)])
        last = chunk[-1]
        if pending_cr and chunk.startswith(b"\n"):
            chunk = chunk[1:]
        pending_cr = chunk.endswith(b"\r") if chunk else False
        position = 0
        for separator in _STREAM_BYTE_SEPARATOR.finditer(chunk):
            if separator.start() > position:
                yield ("data", chunk[position:separator.start()])
            yield ("end", None)
            position = separator.end()
        if position < len(chunk):
            yield ("data", chunk[position:])
    if last is not None and (bytes(first) != b"diff --git " or last != 10):
        raise StreamDiffError("invalid diff framing")


class _DiffLine:
    def __init__(self):
        self.prefix = b""
        self.kind = None
        self.decoder = None
        self.digits = b""
        self.hunk_state = "seek"
        self.plus = b""

    def hunk_data(self, data):
        if self.hunk_state == "done":
            return
        if self.hunk_state == "seek":
            data = self.plus + data
            match = _STREAM_HUNK_START.search(data)
            if match is None:
                self.plus = b"+" if data.endswith(b"+") else b""
                return
            data = data[match.start() + 1:]
            self.hunk_state = "digits"
        count = _STREAM_DIGITS.match(data).end()
        if len(self.digits) + count > 20:
            raise StreamDiffError("invalid diff hunk number")
        self.digits += data[:count]
        if count < len(data):
            self.hunk_state = "done"


def diff_added_line_events(chunks, check_budget=_stream_check):
    """Parse verified Git capture chunks, yielding only numbered added lines.

    CR/LF splitting precedes filesystem decoding with surrogateescape. Headers
    are discarded after an 11-byte discriminator; hunk numbers retain <=20
    decimal digits. This function never acquires or executes Git itself.
    """
    current_line = None
    line = _DiffLine()
    first_line = True
    for part, data in _diff_byte_parts(chunks, check_budget):
        check_budget()
        if part == "data" and line.kind is None:
            needed = 11 - len(line.prefix)
            line.prefix += data[:needed]
            data = data[needed:]
            if len(line.prefix) < 11:
                continue
        if line.kind is None:
            prefix = line.prefix
            line.prefix = b""
            if first_line and not prefix.startswith(b"diff --git "):
                raise StreamDiffError("invalid diff framing")
            first_line = False
            if prefix.startswith(b"diff --git "):
                current_line = None
                line.kind = "ignore"
            elif prefix.startswith(b"@@"):
                line.kind = "hunk"
            elif current_line is None:
                line.kind = "ignore"
            elif prefix.startswith(b"+"):
                line.kind = "added"
                line.decoder = codecs.getincrementaldecoder(sys.getfilesystemencoding())("surrogateescape")
                yield ("start", current_line)
                prefix = prefix[1:]
            elif prefix.startswith((b"-", b"\\")):
                line.kind = "ignore"
            elif prefix.startswith(b" "):
                line.kind = "context"
            else:
                raise StreamDiffError("invalid diff hunk content")
            if part == "data":
                data = prefix + data
            else:
                data = prefix
        if data:
            if line.kind == "hunk":
                line.hunk_data(data)
            elif line.kind == "added":
                # Prefix replay can add at most 11 bytes to a full fragment.
                # Keep every exported text event within the chunk contract.
                for offset in range(0, len(data), 65536):
                    text = line.decoder.decode(data[offset:offset + 65536])
                    for start in range(0, len(text), 65536):
                        yield ("data", text[start:start + 65536])
        if part == "end":
            if line.kind == "hunk":
                if not line.digits:
                    raise StreamDiffError("invalid diff hunk number")
                current_line = int(line.digits)
            elif line.kind == "added":
                text = line.decoder.decode(b"", final=True)
                if text:
                    yield ("data", text)
                yield ("end", None)
                current_line += 1
            elif line.kind == "context":
                current_line += 1
            line = _DiffLine()


# Every supported regex has an independent search cursor. The bounded regex
# search proves a minimum candidate in C; only a greedy span persists between
# fragments. Future patterns require an explicit entry and oracle fixtures.
_STREAM_PATTERNS = (
    ("github_classic_pat", "high", r"gh[pousr]_[A-Za-z0-9]{36}", 40, None),
    ("github_fine_grained_pat", "high", r"github_pat_[A-Za-z0-9_]{20,}", 31, r"[A-Za-z0-9_]*"),
    ("aws_access_key", "high", r"AKIA[0-9A-Z]{16}", 20, None),
    ("stripe_live_key", "high", r"sk_live_[0-9A-Za-z]{16,}", 24, r"[0-9A-Za-z]*"),
    ("slack_token", "medium", r"xox[baprs]-[0-9A-Za-z-]{10,}", 15, r"[0-9A-Za-z-]*"),
)
_STREAM_COMPILED = tuple((name, severity, re.compile(pattern), minimum,
                          re.compile(tail) if tail else None)
                         for name, severity, pattern, minimum, tail in _STREAM_PATTERNS)
_STREAM_FORBIDDEN_ESCAPE = re.compile(r"\\(?:n|r|t|x0[9ad]|u000[9ad])", re.IGNORECASE)
_STREAM_NONSPACE = re.compile(r"[^ ]")


class StreamReport:
    """Caller-owned report shared across candidates, including path findings."""

    def __init__(self, findings=None, processed=0):
        self.findings = findings if findings is not None else []
        self.processed = processed
        self.stopped = processed >= 1000


class _StreamPattern:
    def __init__(self, definition, path, line, is_allowlisted, redact, check_budget):
        self.name, self.severity, self.regex, self.minimum, self.tail = definition
        suffix = f":{line}:{self.name}:"
        first = _STREAM_NONSPACE.search(path)
        offset = first.start() if first else len(path)
        self.capacity = max(0, 8192 - (len(path) - offset + len(suffix)))
        self.key = path[offset:] + suffix if self.capacity else ""
        if (_STREAM_FORBIDDEN_ESCAPE.search(self.key)
                or any(unicodedata.category(char) == "Cc" for char in self.key)):
            self.capacity = 0
            self.key = ""
        self.is_allowlisted = is_allowlisted
        self.redact = redact
        self.check_budget = check_budget
        self.carry = ""
        self.length = 0
        self.first = ""
        self.last = ""
        self.value = ""
        self.count = 0
        self.matches = []

    def extend(self, text):
        if not text:
            return
        if not self.length:
            self.first = text[:4]
        self.length += len(text)
        self.last = (self.last + text[-4:])[-4:]
        if self.value is not None:
            if self.length <= self.capacity:
                self.value += text
            else:
                self.value = None

    def finish_match(self):
        if self.length:
            self.check_budget()
            if self.value is None or not self.is_allowlisted(self.key + self.value):
                self.count = min(1000, self.count + 1)
                if len(self.matches) < 100:
                    # Existing redaction keeps the first/last four for every
                    # supported token. The spacer preserves its length > 8 rule.
                    self.matches.append(self.redact(self.first + ":" + self.last))
            self.length = 0
            self.first = self.last = self.value = ""

    def feed(self, fragment):
        if self.count >= 1000:
            return
        text = self.carry + fragment
        self.carry = ""
        position = 0
        if self.length:
            end = self.tail.match(text).end()
            self.extend(text[:end])
            if end == len(text):
                return
            self.finish_match()
            position = end
        while position < len(text) and self.count < 1000:
            match = self.regex.search(text, position)
            if match is None:
                # Failed minimum candidates can contain later starts. Replaying
                # this bounded suffix preserves regex.search/finditer restart.
                self.carry = text[max(position, len(text) - self.minimum + 1):]
                return
            self.extend(match.group())
            position = match.end()
            if self.tail is not None and position == len(text):
                return
            self.finish_match()


def scan_line_events(path, events, report, is_allowlisted, redact,
                     check_budget=_stream_check):
    """Consume bounded events and update report in legacy line/pattern order.

    is_allowlisted(key) delegates to allowlist_contains('scan_secrets', key,
    entries); redact(value) is the existing redact_match helper. Credential-path
    findings must be inserted into the same report before this call. Events are
    drained after the cap to preserve late diff validation and deadline checks.
    The caller owns source/Git error mapping; failures are never hidden.
    """
    machines = None
    line = None
    prefix_carry = ""
    for kind, value in events:
        check_budget()
        if report.stopped:
            continue
        if kind == "start":
            if line is not None:
                raise ValueError("nested stream line")
            line = value
            prefix_carry = ""
        elif kind == "data":
            if line is None or not isinstance(value, str) or len(value) > 65536:
                raise ValueError("invalid stream data")
            if machines is None:
                # Most short lines contain no token prefix. Search in C before
                # allocating five per-pattern states; retain only enough suffix
                # to recognize a prefix split across adjacent data fragments.
                candidate = prefix_carry + value
                if _STREAM_POSSIBLE_PREFIX.search(candidate) is None:
                    prefix_carry = candidate[-10:]
                    continue
                machines = [_StreamPattern(definition, path, line, is_allowlisted, redact, check_budget)
                            for definition in _STREAM_COMPILED]
                value = candidate
                prefix_carry = ""
            for machine in machines:
                machine.feed(value)
        elif kind == "end":
            if line is None:
                raise ValueError("unopened stream line")
            for machine in machines or ():
                machine.finish_match()
                accepted = min(machine.count, 1000 - report.processed)
                for redacted in machine.matches[:min(accepted, max(0, 100 - len(report.findings)))]:
                    report.findings.append((machine.name, machine.severity, path, line, redacted))
                report.processed += accepted
                if report.processed == 1000:
                    report.stopped = True
                    break
            machines = None
            line = None
            prefix_carry = ""
        else:
            raise ValueError("invalid stream event")
    if line is not None and not report.stopped:
        raise ValueError("unterminated stream line")

# Bounds apply to retained report fields before JSON serialization. Labels are
# ASCII, so each retained character costs at most two JSON bytes after escaping.
REPORT_LABEL_CHARS = 160


def report_text(value, limit=REPORT_LABEL_CHARS):
    text = unicodedata.normalize("NFKC", value[:4096]) if isinstance(value, str) else ""
    text = "".join(char if 32 <= ord(char) <= 126 else " " for char in text)
    return text if len(text) <= limit else text[:limit - 3] + "..."


def report_label(value):
    text = unicodedata.normalize("NFKC", value[:4096]) if isinstance(value, str) else ""
    # Labels have no need to reproduce a credential-bearing identifier. Omit the
    # whole label, including credentials crossing the display clipping boundary.
    if re.search(r"(?i)(?:gh[pousr]_|github_pat_|akia|sk-|sk_live_|xox[baprs]-|bearer\s|(?:token|secret|password|passwd|api[_-]?key|authorization)\s*[:=]|https?://[^/\s]*@)", text):
        return "[REDACTED]"
    return report_text(text)


def report_json_bytes(value):
    """Exact ensure_ascii JSON byte cost without serializing retained data."""
    if isinstance(value, str):
        return 2 + sum(2 if char in '\\"' or char in '\b\f\n\r\t' else
                       6 if ord(char) < 32 or 127 <= ord(char) <= 65535 else
                       12 if ord(char) > 65535 else 1 for char in value)
    if isinstance(value, dict):
        return 2 + max(0, len(value) - 1) + sum(report_json_bytes(key) + 1 + report_json_bytes(child) for key, child in value.items())
    if isinstance(value, (list, tuple)):
        return 2 + max(0, len(value) - 1) + sum(report_json_bytes(child) for child in value)
    if value is None:
        return 4
    if isinstance(value, bool):
        return 4 if value else 5
    return len(str(value))


def read_payload() -> dict:
    _load_scan_payload()
    if _SCAN_INPUT_ERROR:
        raise ScanSecurityError(_SCAN_INPUT_ERROR, "input")
    payload = _SCAN_PAYLOAD
    if not isinstance(payload, dict):
        raise ScanSecurityError("input_invalid", "input")
    return payload


def git_available() -> bool:
    return shutil.which("git") is not None


@contextlib.contextmanager
def capture_git(
    args: list[str],
    *,
    cwd: Path,
    allow_nonzero: bool = False,
    deadline: float | None = None,
    input_bytes: bytes | None = None,
) -> Iterator[VerifiedCapture | None]:
    import subprocess

    global SCAN_PHASE
    options = args[:args.index("--")] if "--" in args else args
    command = args[1] if args and args[0] == "--literal-pathspecs" else args[0] if args else ""
    operation = {
        "rev-parse": "git_head" if args[1:3] == ["--verify", "HEAD"] else "git_repository",
        "symbolic-ref": "git_head", "show-ref": "git_head",
        "ls-files": "git_index" if "--stage" in options else "git_candidates",
        "diff": "git_candidates" if "--name-only" in options else "git_diff",
        "cat-file": "git_index", "show": "git_index",
    }.get(command, "git_command")
    SCAN_PHASE = operation
    git_executable = shutil.which("git")
    if git_executable is None:
        raise GitCommandError("git_unavailable")

    now = time.monotonic()
    command_deadline = now + 5.0
    if deadline is not None:
        command_deadline = min(command_deadline, deadline)
    if command_deadline <= now:
        raise ScanLimitExceeded("scan_timeout", seconds=int(MAX_SCAN_SECONDS))

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = ""
    env["GIT_LITERAL_PATHSPECS"] = "1"
    popen_options: dict[str, object] = {
        "cwd": str(cwd),
        "env": env,
        "stdin": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "posix":
        popen_options["start_new_session"] = True
    if os.name == "nt":
        popen_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    try:
        with contextlib.ExitStack() as resources:
            capture = resources.enter_context(tempfile.TemporaryFile(mode="w+b"))
            _verify_private_capture(capture)
            if input_bytes is not None:
                if len(input_bytes) > MAX_GIT_OUTPUT_BYTES:
                    raise ScanLimitExceeded("git_input_limit", operation, measured=len(input_bytes), limit=MAX_GIT_OUTPUT_BYTES)
                request = resources.enter_context(tempfile.TemporaryFile(mode="w+b"))
                _verify_private_capture(request)
                request.write(input_bytes)
                request.seek(0)
                popen_options["stdin"] = request
            process = subprocess.Popen([git_executable, *args], stdout=capture, **popen_options)
            observed_descendants: list[int] = []
            try:
                while True:
                    size = os.fstat(capture.fileno()).st_size
                    if size > MAX_GIT_OUTPUT_BYTES:
                        raise ScanLimitExceeded("git_output_limit", operation, measured=size, limit=MAX_GIT_OUTPUT_BYTES)
                    if time.monotonic() >= command_deadline:
                        enforce_deadline(deadline)
                        raise ScanLimitExceeded("git_timeout", operation, seconds=5)
                    return_code = process.poll()
                    if return_code is not None:
                        break
                    try:
                        # Short slices avoid cumulative exponential-wait overshoot
                        # across hundreds of bounded, short-lived Git calls.
                        process.wait(timeout=min(
                            GIT_COMPLETION_WAIT_SECONDS,
                            max(0.0, command_deadline - time.monotonic()),
                        ))
                    except subprocess.TimeoutExpired:
                        pass

                if os.name == "posix":
                    try:
                        os.killpg(process.pid, 0)
                    except ProcessLookupError:
                        pass
                    else:
                        raise GitCommandError("git_descendant_running")
                elif os.name == "nt":
                    observed_descendants = _windows_git_descendants(process.pid)
                    if observed_descendants:
                        raise GitCommandError("git_descendant_running")
                size = os.fstat(capture.fileno()).st_size
                if size > MAX_GIT_OUTPUT_BYTES:
                    raise ScanLimitExceeded("git_output_limit", operation, measured=size, limit=MAX_GIT_OUTPUT_BYTES)
                if return_code != 0:
                    if allow_nonzero and size == 0:
                        if args == ["rev-parse", "--verify", "HEAD"] and return_code == 128:
                            yield None
                            return
                        if (len(args) == 4 and args[:3] == ["show-ref", "--verify", "--quiet"]
                                and return_code == 1):
                            yield None
                            return
                    raise GitCommandError("git_failed", operation, exit_status=return_code)
                _verify_private_capture(capture)
                yield VerifiedCapture(capture, size, deadline, operation)
            except BaseException:
                _stop_git_process(process, subprocess, observed_descendants)
                raise
    except OSError as exc:
        raise GitCommandError("git_capture_failed") from exc


def _verify_private_capture(handle: BinaryIO) -> None:
    details = os.fstat(handle.fileno())
    if (not stat.S_ISREG(details.st_mode) or _is_reparse_point(details)
            or (os.name == "posix" and
                (details.st_mode & 0o077 or details.st_uid != os.geteuid()))):
        raise GitCommandError("git_capture_failed")


class VerifiedCapture:
    """A completed private capture, lent only while its owner is open."""

    def __init__(self, handle: BinaryIO, size: int, deadline: float | None, operation: str):
        self.handle = handle
        self.size = size
        self.deadline = deadline
        self.operation = operation

    def chunks(self, offset: int = 0, length: int | None = None, chunk_bytes: int = 65536) -> Iterator[bytes]:
        length = self.size - offset if length is None else length
        if offset < 0 or length < 0 or offset + length > self.size or chunk_bytes <= 0:
            raise GitCommandError("git_output_invalid", self.operation)
        enforce_deadline(self.deadline)
        if os.fstat(self.handle.fileno()).st_size != self.size:
            raise GitCommandError("git_output_invalid", self.operation)
        self.handle.seek(offset)
        remaining = length
        while remaining:
            enforce_deadline(self.deadline)
            chunk = self.handle.read(min(remaining, chunk_bytes, 65536))
            if not chunk:
                raise GitCommandError("git_output_invalid", self.operation)
            remaining -= len(chunk)
            yield chunk
        enforce_deadline(self.deadline)
        if os.fstat(self.handle.fileno()).st_size != self.size:
            raise GitCommandError("git_output_invalid", self.operation)

    def records(self, separator: bytes, *, maximum: int = MAX_GIT_OUTPUT_BYTES) -> Iterator[bytes]:
        pending = bytearray()
        for chunk in self.chunks():
            start = 0
            while True:
                end = chunk.find(separator, start)
                if end < 0:
                    pending.extend(chunk[start:])
                    if len(pending) > maximum:
                        raise GitCommandError("git_output_invalid", self.operation)
                    break
                pending.extend(chunk[start:end])
                if len(pending) > maximum:
                    raise GitCommandError("git_output_invalid", self.operation)
                yield bytes(pending)
                pending.clear()
                start = end + 1
        if pending:
            raise GitCommandError("git_output_invalid", self.operation)


def run_git(args: list[str], *, cwd: Path, text: bool = True,
            allow_nonzero: bool = False, deadline: float | None = None,
            input_bytes: bytes | None = None) -> str | bytes | None:
    # Small control output compatibility. Bodies use capture ranges directly.
    with capture_git(args, cwd=cwd, allow_nonzero=allow_nonzero,
                     deadline=deadline, input_bytes=input_bytes) as capture:
        if capture is None:
            return None
        output = b"".join(capture.chunks())
        return os.fsdecode(output) if text else output


def _windows_git_descendants(
    parent_pid: int, ancestor_pids: set[int] | None = None,
) -> list[int]:
    import ctypes
    from ctypes import wintypes

    class ProcessEntry(ctypes.Structure):
        _fields_ = [
            ("size", wintypes.DWORD), ("usage", wintypes.DWORD),
            ("pid", wintypes.DWORD), ("default_heap", ctypes.c_void_p),
            ("module", wintypes.DWORD), ("threads", wintypes.DWORD),
            ("parent_pid", wintypes.DWORD), ("priority", ctypes.c_long),
            ("flags", wintypes.DWORD), ("name", ctypes.c_wchar * 260),
        ]

    kernel = ctypes.windll.kernel32
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry)]
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        return []
    parents: dict[int, int] = {}
    try:
        entry = ProcessEntry()
        entry.size = ctypes.sizeof(entry)
        if kernel.Process32FirstW(snapshot, ctypes.byref(entry)):
            while True:
                parents[int(entry.pid)] = int(entry.parent_pid)
                if not kernel.Process32NextW(snapshot, ctypes.byref(entry)):
                    break
    finally:
        kernel.CloseHandle(snapshot)
    descendants: set[int] = set()
    frontier = {parent_pid}
    if ancestor_pids:
        frontier.update(ancestor_pids)
    while frontier:
        children = {pid for pid, parent in parents.items() if parent in frontier}
        children -= descendants
        descendants.update(children)
        frontier = children
    return list(descendants)


def _stop_git_process(
    process: object, subprocess_module: object,
    observed_descendants: list[int] | None = None,
) -> None:
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.windll.kernel32
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        cleanup_deadline = time.monotonic() + 0.75
        known_descendants = set(observed_descendants or [])
        quiet_scans = 0
        while time.monotonic() < cleanup_deadline:
            known_descendants.update(_windows_git_descendants(process.pid, known_descendants))
            handles = []
            for pid in [process.pid, *sorted(known_descendants)]:
                handle = kernel.OpenProcess(0x00100001, False, pid)
                if not handle:
                    continue
                if kernel.WaitForSingleObject(handle, 0) == 0x102:
                    handles.append(handle)
                else:
                    kernel.CloseHandle(handle)
            try:
                if not handles:
                    quiet_scans += 1
                    if quiet_scans >= 2:
                        break
                    time.sleep(min(0.01, max(0.0, cleanup_deadline - time.monotonic())))
                    continue
                quiet_scans = 0
                for handle in handles:
                    kernel.TerminateProcess(handle, 1)
                for handle in handles:
                    remaining_ms = max(0, min(50, int((cleanup_deadline - time.monotonic()) * 1000)))
                    kernel.WaitForSingleObject(handle, remaining_ms)
            finally:
                for handle in handles:
                    kernel.CloseHandle(handle)
        if process.poll() is None:
            process.kill()
        try:
            process.wait(timeout=max(0.0, cleanup_deadline - time.monotonic()))
        except subprocess_module.TimeoutExpired:
            pass
        return
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGTERM)
        elif process.poll() is None:
            process.terminate()
    except (OSError, ProcessLookupError):
        if process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass
    cleanup_deadline = time.monotonic() + 0.25
    group_alive = True
    while time.monotonic() < cleanup_deadline:
        if os.name == "posix":
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                group_alive = False
                break
            except OSError:
                break
        elif process.poll() is not None:
            group_alive = False
            break
        time.sleep(0.01)
    if group_alive:
        try:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            elif process.poll() is None:
                process.kill()
        except (OSError, ProcessLookupError):
            if process.poll() is None:
                try:
                    process.kill()
                except OSError:
                    pass
    try:
        process.wait(timeout=0.25)
    except subprocess_module.TimeoutExpired:
        pass


def repo_root(work_dir: Path, *, deadline: float | None = None) -> Path:
    output = run_git(["rev-parse", "--show-toplevel"], cwd=work_dir, deadline=deadline)
    if isinstance(output, str):
        root = output.strip()
        if root:
            return Path(root)
    return work_dir


def repository_marker_exists(work_dir: Path) -> bool:
    try:
        current = work_dir.resolve(strict=False)
    except OSError as exc:
        raise ScanSecurityError("repository_unavailable", "repository") from exc

    for directory in (current, *current.parents):
        try:
            (directory / ".git").lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ScanSecurityError("repository_unavailable", "repository") from exc
        return True
    return False


def is_inside_git_repo(work_dir: Path, *, deadline: float | None = None) -> bool:
    try:
        output = run_git(
            ["rev-parse", "--is-inside-work-tree"],
            cwd=work_dir,
            deadline=deadline,
        )
    except GitCommandError:
        if repository_marker_exists(work_dir):
            raise
        return False
    return isinstance(output, str) and output.strip() == "true"


def has_head(root: Path, *, deadline: float | None = None) -> bool:
    head = run_git(
        ["rev-parse", "--verify", "HEAD"],
        cwd=root,
        allow_nonzero=True,
        deadline=deadline,
    )
    if head is not None:
        return True
    branch = run_git(["symbolic-ref", "--quiet", "HEAD"], cwd=root, deadline=deadline)
    if not isinstance(branch, str) or not branch.startswith("refs/heads/") or branch.count("\n") != 1:
        raise GitCommandError("git_head_invalid", "git_head")
    branch_exists = run_git(
        ["show-ref", "--verify", "--quiet", branch.rstrip("\n")],
        cwd=root,
        allow_nonzero=True,
        deadline=deadline,
    )
    if branch_exists is not None:
        raise GitCommandError("git_head_invalid", "git_head")
    return False


def collect_unmerged_files(
    root: Path, *, deadline: float | None = None,
) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    with capture_git(["ls-files", "--unmerged", "-z", "--"], cwd=root,
                     deadline=deadline) as capture:
        for record in capture.records(b"\0"):
            header, separator, raw_path = record.partition(b"\t")
            match = re.fullmatch(rb"[0-7]{6} (?:[0-9a-f]{40}|[0-9a-f]{64}) ([123])", header)
            if not separator or not raw_path or match is None:
                raise GitCommandError("git_output_invalid", "git_candidates")
            path = os.fsdecode(raw_path)
            _validate_candidate_parts(path)
            source = CANDIDATE_UNMERGED_STAGES[int(match.group(1)) - 1]
            candidate = (source, path)
            if candidate in seen:
                raise GitCommandError("git_output_invalid", "git_candidates")
            seen.add(candidate)
            candidates.append(candidate)
            if len(candidates) > MAX_FILES:
                raise ScanLimitExceeded("snapshot_count_limit", "git_candidates",
                                        measured=len(candidates), limit=MAX_FILES)
    return candidates


def collect_files(
    root: Path, scope: str, root_has_head: bool, *, deadline: float | None = None,
) -> list[tuple[str, str]]:
    candidates = set(collect_unmerged_files(root, deadline=deadline))
    unmerged_paths = {path for _, path in candidates}
    diff_options = ["--name-only", "-z", "--no-ext-diff", "--no-color",
                    "--no-textconv", "--diff-filter=ACMRTUXB"]

    def add_paths(args: list[str], source: str) -> None:
        with capture_git(args, cwd=root, deadline=deadline) as capture:
            for raw_path in capture.records(b"\0"):
                if not raw_path:
                    continue
                path = os.fsdecode(raw_path)
                if source == CANDIDATE_STAGED and path in unmerged_paths:
                    continue
                actual_source = (CANDIDATE_UNMERGED_WORKTREE
                                 if source == CANDIDATE_WORKTREE and path in unmerged_paths
                                 else source)
                candidates.add((actual_source, path))
                if len(candidates) > MAX_FILES:
                    raise ScanLimitExceeded("snapshot_count_limit", "git_candidates",
                                            measured=len(candidates), limit=MAX_FILES)

    if scope in {"staged", "diff"}:
        add_paths(["diff", "--cached", *diff_options,
                   *(["HEAD"] if root_has_head else []), "--"], CANDIDATE_STAGED)
    if scope == "diff":
        add_paths(["diff", *diff_options, "--"], CANDIDATE_WORKTREE)
        add_paths(["ls-files", "-z", "--others", "--exclude-standard"], CANDIDATE_UNTRACKED)
    return sorted(candidates, key=lambda candidate: (candidate[1], candidate[0]))


def _is_reparse_point(details: os.stat_result) -> bool:
    attributes = getattr(details, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & flag)


def _validate_candidate_parts(path: str) -> tuple[str, ...]:
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or not parsed.parts or any(part in {"", ".", ".."} for part in parsed.parts):
        raise ScanSecurityError("candidate_unsafe", "candidate_read")
    return parsed.parts


@contextlib.contextmanager
def _worktree_descriptor(root: Path, path: str, *, allow_missing: bool = False) -> Iterator[int | None]:
    parts = _validate_candidate_parts(path)
    try:
        root_path = root.resolve(strict=True)
    except OSError as exc:
        raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    nonblocking = getattr(os, "O_NONBLOCK", 0)
    directory_flag = getattr(os, "O_DIRECTORY", 0)

    if os.open in os.supports_dir_fd and directory_flag:
        descriptors: list[int] = []
        opened = False
        try:
            current = os.open(root_path, os.O_RDONLY | directory_flag)
            descriptors.append(current)
            for component in parts[:-1]:
                details = os.stat(component, dir_fd=current, follow_symlinks=False)
                if stat.S_ISLNK(details.st_mode) or _is_reparse_point(details):
                    raise ScanSecurityError("candidate_unsafe", "candidate_read")
                current = os.open(
                    component,
                    os.O_RDONLY | directory_flag | no_follow,
                    dir_fd=current,
                )
                descriptors.append(current)
            details = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
            if stat.S_ISLNK(details.st_mode) or _is_reparse_point(details):
                raise ScanSecurityError("candidate_unsafe", "candidate_read")
            descriptor = os.open(parts[-1], os.O_RDONLY | no_follow | nonblocking, dir_fd=current)
            descriptors.append(descriptor)
            opened = True
            yield descriptor
            return
        except (OSError, ValueError) as exc:
            if allow_missing and not opened and isinstance(exc, FileNotFoundError):
                yield None
                return
            raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
        finally:
            for descriptor in reversed(descriptors):
                try:
                    os.close(descriptor)
                except OSError:
                    pass

    candidate = root_path.joinpath(*parts)
    current = root_path
    try:
        for component in parts:
            current = current / component
            details = current.lstat()
            if stat.S_ISLNK(details.st_mode) or _is_reparse_point(details):
                raise ScanSecurityError("candidate_unsafe", "candidate_read")
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root_path)
        descriptor = os.open(candidate, os.O_RDONLY | no_follow | nonblocking)
    except (OSError, ValueError) as exc:
        if allow_missing and isinstance(exc, FileNotFoundError):
            yield None
            return
        raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
    try:
        yield descriptor
    except OSError as exc:
        raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
    finally:
        os.close(descriptor)


class ScanBudget:
    def __init__(self, deadline: float):
        self.deadline = deadline
        self.used_bytes = 0
        self.index_reserved: set[tuple[str, str]] = set()

    def remaining(self) -> int:
        enforce_deadline(self.deadline)
        return MAX_TOTAL_BYTES - self.used_bytes

    def charge(self, size: int, operation: str = "candidate_read") -> None:
        enforce_deadline(self.deadline)
        if size > self.remaining():
            raise ScanLimitExceeded("total_bytes_limit", operation,
                                    measured=self.used_bytes + size, limit=MAX_TOTAL_BYTES)
        self.used_bytes += size

    def reserve_index(self, candidate: tuple[str, str], size: int) -> None:
        if candidate not in self.index_reserved:
            self.charge(size, "git_index")
            self.index_reserved.add(candidate)


class Snapshot:
    def __init__(self, candidate: tuple[str, str], capture: VerifiedCapture,
                 offset: int, byte_count: int):
        self.candidate = candidate
        self.capture = capture
        self.offset = offset
        self.byte_count = byte_count
        self.active = True
        self.classification = "binary"

    def chunks(self, chunk_bytes: int = 65536) -> Iterator[bytes]:
        if not self.active:
            raise ScanSecurityError("candidate_read_failed", "candidate_read")
        for chunk in self.capture.chunks(self.offset, self.byte_count, chunk_bytes):
            if not self.active:
                raise ScanSecurityError("candidate_read_failed", "candidate_read")
            yield chunk

    def classify(self) -> None:
        decoder = codecs.getincrementaldecoder("utf-8")("strict")
        valid = True
        nul = False
        for chunk in self.chunks():
            nul = nul or b"\0" in chunk
            if valid:
                try:
                    decoder.decode(chunk, final=False)
                except UnicodeDecodeError:
                    valid = False
        if valid:
            try:
                decoder.decode(b"", final=True)
            except UnicodeDecodeError:
                valid = False
        self.classification = ("text" if not nul and
                               (valid or Path(self.candidate[1]).suffix.lower() in TEXT_EXTENSIONS)
                               else "binary")


def resolve_index_candidates(root: Path, index_candidates: list[tuple[str, str]],
                             *, deadline: float | None = None) -> dict[tuple[str, str], bytes]:
    paths: list[str] = []
    for _, path in index_candidates:
        _validate_candidate_parts(path)
        if path not in paths:
            paths.append(path)
    resolved: dict[tuple[str, str], bytes] = {}
    expected_candidates = set(index_candidates)
    cursor = 0
    while cursor < len(paths):
        start = cursor
        argument_bytes = 0
        while cursor < len(paths):
            path_bytes = len(os.fsencode(paths[cursor])) * 2 + 3
            if cursor > start and argument_bytes + path_bytes > 8192:
                break
            argument_bytes += path_bytes
            cursor += 1
        batch_paths = paths[start:cursor]
        with capture_git(
            ["--literal-pathspecs", "ls-files", "--stage", "-z", "--", *batch_paths],
            cwd=root, deadline=deadline,
        ) as capture:
            if capture is None or not capture.size:
                raise GitCommandError("git_output_invalid", "git_index")
            for record in capture.records(b"\0"):
                header, separator, raw_path = record.partition(b"\t")
                match = re.fullmatch(rb"[0-7]{6} ([0-9a-f]{40}|[0-9a-f]{64}) ([0-3])", header)
                if not separator or not raw_path or match is None:
                    raise GitCommandError("git_output_invalid", "git_index")
                path = os.fsdecode(raw_path)
                if "/".join(_validate_candidate_parts(path)) != path:
                    raise GitCommandError("git_output_invalid", "git_index")
                if path not in batch_paths:
                    # Literal pathspecs still expand directory descendants.
                    if any(path.startswith(parent + "/") for parent in batch_paths):
                        continue
                    raise GitCommandError("git_output_invalid", "git_index")
                stage = int(match.group(2))
                source = CANDIDATE_STAGED if stage == 0 else CANDIDATE_UNMERGED_STAGES[stage - 1]
                candidate = (source, path)
                if candidate not in expected_candidates or candidate in resolved:
                    raise GitCommandError("git_output_invalid", "git_index")
                resolved[candidate] = match.group(1)
    if len(resolved) != len(index_candidates):
        raise GitCommandError("git_output_invalid", "git_index")
    return resolved


class SnapshotSource:
    """Own one index capture and one worktree spool in candidate order."""

    def __init__(self, root: Path, candidates: list[tuple[str, str]], budget: ScanBudget):
        self.root = root
        self.budget = budget
        self.objects: list[tuple[tuple[str, str], bytes, int, bytes]] = []
        self.cursor = 0
        self.batch_owner = contextlib.ExitStack()
        self.ranges: dict[tuple[str, str], tuple[VerifiedCapture, int, int]] = {}
        index_candidates = [candidate for candidate in candidates
                            if candidate[0] == CANDIDATE_STAGED
                            or candidate[0] in CANDIDATE_UNMERGED_STAGES]
        if not index_candidates:
            return
        resolved = resolve_index_candidates(root, index_candidates, deadline=budget.deadline)
        with capture_git(["cat-file", "--batch-check"], cwd=root,
                         input_bytes=b"".join(resolved[c] + b"\n" for c in index_candidates),
                         deadline=budget.deadline) as capture:
            records = iter(capture.records(b"\n", maximum=96))
            for candidate in index_candidates:
                header = next(records, None)
                match = (re.fullmatch(rb"([0-9a-f]{40}|[0-9a-f]{64}) blob ([0-9]{1,20})", header)
                         if header is not None else None)
                if match is None or match.group(1) != resolved[candidate]:
                    raise GitCommandError("git_output_invalid", "git_index")
                size = int(match.group(2))
                budget.reserve_index(candidate, size)
                self.objects.append((candidate, match.group(1), size, header + b"\n"))
            if next(records, None) is not None:
                raise GitCommandError("git_output_invalid", "git_index")

    def close(self) -> None:
        self.batch_owner.close()
        self.ranges.clear()

    def _next_batch(self) -> None:
        self.close()
        start = self.cursor
        capture_bytes = 0
        while self.cursor < len(self.objects):
            _, _, size, header = self.objects[self.cursor]
            framed_size = len(header) + size + 1
            if capture_bytes + framed_size > MAX_GIT_OUTPUT_BYTES:
                break
            capture_bytes += framed_size
            self.cursor += 1
        batch = self.objects[start:self.cursor]
        if not batch:
            candidate, oid, size, _ = self.objects[self.cursor]
            self.cursor += 1
            capture = self.batch_owner.enter_context(capture_git(
                ["cat-file", "blob", oid.decode("ascii")], cwd=self.root, deadline=self.budget.deadline))
            if capture.size != size:
                raise GitCommandError("git_output_invalid", "git_index")
            self.ranges[candidate] = (capture, 0, size)
            return
        capture = self.batch_owner.enter_context(capture_git(
            ["cat-file", "--batch"], cwd=self.root,
            input_bytes=b"".join(oid + b"\n" for _, oid, _, _ in batch),
            deadline=self.budget.deadline))
        if capture.size != capture_bytes:
            raise GitCommandError("git_output_invalid", "git_index")
        offset = 0
        for candidate, _, size, header in batch:
            if b"".join(capture.chunks(offset, len(header))) != header:
                raise GitCommandError("git_output_invalid", "git_index")
            offset += len(header)
            if b"".join(capture.chunks(offset + size, 1)) != b"\n":
                raise GitCommandError("git_output_invalid", "git_index")
            self.ranges[candidate] = (capture, offset, size)
            offset += size + 1
        if offset != capture.size:
            raise GitCommandError("git_output_invalid", "git_index")

    @contextlib.contextmanager
    def acquire(self, candidate: tuple[str, str]) -> Iterator[Snapshot | None]:
        source, path = candidate
        snapshot = None
        try:
            if source == CANDIDATE_STAGED or source in CANDIDATE_UNMERGED_STAGES:
                if candidate not in self.ranges:
                    self._next_batch()
                snapshot = Snapshot(candidate, *self.ranges[candidate])
                snapshot.classify()
                yield snapshot
            else:
                with _worktree_descriptor(self.root, path,
                        allow_missing=source == CANDIDATE_UNMERGED_WORKTREE) as descriptor:
                    if descriptor is None:
                        yield None
                        return
                    details = os.fstat(descriptor)
                    if not stat.S_ISREG(details.st_mode) or _is_reparse_point(details):
                        raise ScanSecurityError("candidate_unsafe", "candidate_read")
                    remaining = self.budget.remaining()
                    if details.st_size > remaining:
                        raise ScanLimitExceeded("total_bytes_limit", "candidate_read",
                                                measured=self.budget.used_bytes + details.st_size,
                                                limit=MAX_TOTAL_BYTES)
                    with tempfile.TemporaryFile(mode="w+b") as spool:
                        _verify_private_capture(spool)
                        size = 0
                        ceiling = remaining
                        while True:
                            enforce_deadline(self.budget.deadline)
                            chunk = os.read(descriptor, min(65536, ceiling + 1 - size))
                            if not chunk:
                                break
                            size += len(chunk)
                            if size > ceiling:
                                raise ScanLimitExceeded("total_bytes_limit", "candidate_read",
                                                        measured=self.budget.used_bytes + len(chunk),
                                                        limit=MAX_TOTAL_BYTES)
                            self.budget.charge(len(chunk))
                            spool.write(chunk)
                        spool.flush()
                        capture = VerifiedCapture(spool, size, self.budget.deadline, "candidate_read")
                        snapshot = Snapshot(candidate, capture, 0, size)
                        snapshot.classify()
                        yield snapshot
        except OSError as exc:
            raise ScanSecurityError("candidate_read_failed", "candidate_read") from exc
        finally:
            if snapshot is not None:
                snapshot.active = False
            if candidate in self.ranges:
                del self.ranges[candidate]
                if not self.ranges:
                    self.close()


@contextlib.contextmanager
def snapshot_source(root: Path, candidates: list[tuple[str, str]],
                    budget: ScanBudget) -> Iterator[SnapshotSource]:
    source = SnapshotSource(root, candidates, budget)
    try:
        yield source
    finally:
        source.close()


def is_env_path(path: str) -> bool:
    return bool(re.search(r"(^|/)\.env($|[.])", path.lower()))


def is_credential_path(path: str) -> bool:
    lowered = path.lower()
    base_name = lowered.rsplit("/", 1)[-1]
    if base_name in {"credentials", ".git-credentials"}:
        return True
    if base_name.startswith("credentials."):
        return True

    return any(
        re.search(pattern, lowered)
        for pattern in (
            r"(^|/)\.ssh(/|$)",
            r"(^|/)\.aws(/|$)",
            r"(^|/)\.gnupg(/|$)",
            r"(^|/)\.?credentials(/|$)",
            r"(^|/)\.?secrets(/|$)",
        )
    )


def scan_diff_added_lines(
    root: Path,
    path: str,
    source: str,
    report: StreamReport,
    is_allowlisted,
    *,
    root_has_head: bool,
    deadline: float | None = None,
) -> None:
    if source not in {CANDIDATE_STAGED, CANDIDATE_WORKTREE}:
        raise ScanSecurityError("candidate_unsafe", "git_diff")
    cached_options = ["--cached"] if source == CANDIDATE_STAGED else []
    cached_revision = ["HEAD"] if source == CANDIDATE_STAGED and root_has_head else []
    with capture_git(
        [
            "diff",
            *cached_options,
            "--no-ext-diff",
            "--no-color",
            "--no-textconv",
            "--unified=0",
            "--src-prefix=a/",
            "--dst-prefix=b/",
            "--output-indicator-new=+",
            "--output-indicator-old=-",
            "--output-indicator-context= ",
            *cached_revision,
            "--",
            path,
        ],
        cwd=root,
        deadline=deadline,
    ) as capture:
        check_budget = lambda: enforce_deadline(deadline)
        try:
            scan_line_events(path, diff_added_line_events(capture.chunks(), check_budget),
                             report, is_allowlisted, redact_match, check_budget)
        except StreamDiffError as exc:
            raise GitCommandError("git_output_invalid", "git_diff") from exc


def redact_match(match: str) -> str:
    if len(match) <= 8:
        return "[REDACTED]"
    return f"{match[:4]}...{match[-4:]}"


def _normalize_allowlist_value(value: str) -> str:
    return value.strip(" ")


def _has_forbidden_allowlist_separator(value: str) -> bool:
    return any(unicodedata.category(character) == "Cc" for character in value) or bool(
        re.search(r"\\(?:n|r|t|x0[9ad]|u000[9ad])", value, re.IGNORECASE)
    )


def parse_allowlist(raw_allowlist: str | None) -> list[dict[str, str]]:
    if not raw_allowlist:
        return []
    try:
        decoded = json.loads(raw_allowlist)
    except (TypeError, ValueError):
        return []
    if not isinstance(decoded, list) or len(decoded) > 64:
        return []

    entries: list[dict[str, str]] = []
    for raw_entry in decoded:
        if not isinstance(raw_entry, dict) or set(raw_entry) != {"tool", "input"}:
            return []
        tool = raw_entry.get("tool")
        tool_input = raw_entry.get("input")
        if not isinstance(tool, str) or not isinstance(tool_input, str):
            return []
        if _has_forbidden_allowlist_separator(tool) or _has_forbidden_allowlist_separator(tool_input):
            return []
        normalized_tool = _normalize_allowlist_value(tool).casefold()
        normalized_input = _normalize_allowlist_value(tool_input)
        if not normalized_tool or not normalized_input or len(normalized_tool) > 128 or len(normalized_input) > 8192:
            return []
        entries.append({"tool": normalized_tool, "input": normalized_input})
    return entries


def allowlist_contains(tool_name: str, tool_input: str, entries: list[dict[str, str]]) -> bool:
    if _has_forbidden_allowlist_separator(tool_name) or _has_forbidden_allowlist_separator(tool_input):
        return False
    normalized_tool = _normalize_allowlist_value(tool_name).casefold()
    normalized_input = _normalize_allowlist_value(tool_input)
    return any(
        entry["tool"] == normalized_tool and entry["input"] == normalized_input
        for entry in entries
    )


def _assert_safe_log_path(path: Path, *, allow_missing: bool = True) -> os.stat_result | None:
    try:
        details = path.lstat()
    except FileNotFoundError:
        if allow_missing:
            return None
        raise ScanSecurityError("log_unavailable", "scan_log") from None
    except OSError as exc:
        raise ScanSecurityError("log_unavailable", "scan_log") from exc
    if stat.S_ISLNK(details.st_mode) or _is_reparse_point(details):
        raise ScanSecurityError("log_unsafe", "scan_log")
    return details


def _ensure_secure_log_directory(directory: Path) -> None:
    try:
        directory.mkdir(parents=True, mode=0o700, exist_ok=True)
        details = _assert_safe_log_path(directory, allow_missing=False)
        if details is None or not stat.S_ISDIR(details.st_mode):
            raise ScanSecurityError("log_unsafe", "scan_log")
        os.chmod(directory, 0o700)
    except ScanSecurityError:
        raise
    except OSError as exc:
        raise ScanSecurityError("log_unavailable", "scan_log") from exc


def _open_secure_regular(path: Path, flags: int) -> int:
    _assert_safe_log_path(path)
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    binary = getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags | no_follow | binary, 0o600)
    except OSError as exc:
        raise ScanSecurityError("log_unavailable", "scan_log") from exc
    try:
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode) or _is_reparse_point(details):
            raise ScanSecurityError("log_unsafe", "scan_log")
        try:
            os.fchmod(descriptor, 0o600)
        except (AttributeError, OSError):
            os.chmod(path, 0o600)
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def rotate_scan_log(
    log_path: Path,
    incoming_bytes: int,
    max_bytes: int = 1048576,
    backups: int = 3,
) -> None:
    if max_bytes < 1 or backups < 1 or backups > 100:
        raise ScanSecurityError("log_configuration_invalid", "scan_log")
    if incoming_bytes < 1 or incoming_bytes > MAX_LOG_RECORD_BYTES:
        raise ScanLimitExceeded("log_record_limit", "scan_log", measured=incoming_bytes, limit=MAX_LOG_RECORD_BYTES)
    if incoming_bytes > max_bytes:
        raise ScanLimitExceeded("log_record_limit", "scan_log", measured=incoming_bytes, limit=max_bytes)
    details = _assert_safe_log_path(log_path)
    if details is None:
        return
    if not stat.S_ISREG(details.st_mode):
        raise ScanSecurityError("log_unsafe", "scan_log")
    if details.st_size + incoming_bytes <= max_bytes:
        return

    paths = [log_path.with_name(f"{log_path.name}.{index}") for index in range(1, backups + 2)]
    for path in paths:
        details = _assert_safe_log_path(path)
        if details is not None and not stat.S_ISREG(details.st_mode):
            raise ScanSecurityError("log_unsafe", "scan_log")

    try:
        for index in range(backups, 0, -1):
            current = log_path.with_name(f"{log_path.name}.{index}")
            next_path = log_path.with_name(f"{log_path.name}.{index + 1}")
            if not current.exists():
                continue
            if index == backups:
                os.remove(current)
            else:
                os.replace(current, next_path)
                os.chmod(next_path, 0o600)
        first_backup = log_path.with_name(f"{log_path.name}.1")
        os.replace(log_path, first_backup)
        os.chmod(first_backup, 0o600)
    except OSError as exc:
        raise ScanSecurityError("log_unavailable", "scan_log") from exc


def enforce_log_lock_deadline(lock_deadline: float, deadline: float | None) -> None:
    enforce_deadline(deadline)
    if time.monotonic() >= lock_deadline:
        raise ScanLimitExceeded("log_lock_timeout", "scan_log", seconds=int(LOG_LOCK_TIMEOUT_SECONDS))


def _acquire_log_lock(
    lock_fd: int,
    fcntl_module: object | None,
    msvcrt_module: object | None,
    *,
    deadline: float | None = None,
) -> str:
    lock_deadline = time.monotonic() + LOG_LOCK_TIMEOUT_SECONDS
    if deadline is not None:
        lock_deadline = min(lock_deadline, deadline)
    enforce_log_lock_deadline(lock_deadline, deadline)
    if fcntl_module is not None:
        while True:
            enforce_log_lock_deadline(lock_deadline, deadline)
            try:
                fcntl_module.flock(lock_fd, fcntl_module.LOCK_EX | fcntl_module.LOCK_NB)
                return "posix"
            except (BlockingIOError, OSError) as exc:
                if time.monotonic() >= lock_deadline:
                    raise ScanLimitExceeded("log_lock_timeout", "scan_log", seconds=int(LOG_LOCK_TIMEOUT_SECONDS)) from exc
                time.sleep(LOG_LOCK_POLL_SECONDS)
    if msvcrt_module is not None:
        if os.fstat(lock_fd).st_size == 0:
            os.write(lock_fd, b"\0")
        while True:
            enforce_log_lock_deadline(lock_deadline, deadline)
            try:
                os.lseek(lock_fd, 0, os.SEEK_SET)
                msvcrt_module.locking(lock_fd, msvcrt_module.LK_NBLCK, 1)
                return "windows"
            except OSError as exc:
                if time.monotonic() >= lock_deadline:
                    raise ScanLimitExceeded("log_lock_timeout", "scan_log", seconds=int(LOG_LOCK_TIMEOUT_SECONDS)) from exc
                time.sleep(LOG_LOCK_POLL_SECONDS)
    raise ScanSecurityError("log_unavailable", "scan_log")


def _release_log_lock(
    lock_fd: int,
    lock_kind: str,
    fcntl_module: object | None,
    msvcrt_module: object | None,
) -> None:
    if lock_kind == "posix" and fcntl_module is not None:
        fcntl_module.flock(lock_fd, fcntl_module.LOCK_UN)
    elif lock_kind == "windows" and msvcrt_module is not None:
        os.lseek(lock_fd, 0, os.SEEK_SET)
        msvcrt_module.locking(lock_fd, msvcrt_module.LK_UNLCK, 1)


def append_scan_log(**kwargs: object) -> None:
    global SCAN_PHASE, SCAN_SECURITY_OUTCOME
    if kwargs.get("status") != "incomplete":
        SCAN_SECURITY_OUTCOME = kwargs.get("status", "incomplete")
    SCAN_PHASE = "scan_log"
    try:
        _append_scan_log(**kwargs)
    except ScanFailure:
        raise
    except OSError as exc:
        raise ScanSecurityError("log_unavailable", "scan_log") from exc


def _append_scan_log(
    *,
    log_path: Path,
    status: str,
    session_id: str,
    timestamp: str,
    mode: str,
    scope: str,
    repo_root_path: Path,
    env_files: list[str],
    findings: list[dict[str, object]],
    omitted_findings: int = 0,
    findings_truncated: bool = False,
    note: str = "",
    deadline: float | None = None,
    diagnostic: dict[str, object] | None = None,
    security_outcome: str | None = None,
    audit_outcome: str = "written",
) -> None:
    enforce_deadline(deadline)
    _ensure_secure_log_directory(log_path.parent)
    payload: dict[str, object] = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sessionId": report_label(session_id),
        "repoRoot": report_label(str(repo_root_path)),
        "mode": mode,
        "scope": scope,
        "status": status,
    }
    if status == "incomplete":
        # Incomplete records cannot carry payload-derived identifiers or paths.
        payload = {"timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "mode": mode, "scope": scope, "status": status, "action": SCAN_ACTION}
        if diagnostic is not None:
            payload["diagnostic"] = diagnostic
    if note:
        payload["note"] = report_text(note, 512)
    payload.update(build=REPORT_BUILD, provider=REPORT_PROVIDER,
                   profile="pending_snapshots_v1", route="pending_scan", action=SCAN_ACTION,
                   cause=diagnostic["cause"] if diagnostic else status,
                   security_outcome=security_outcome or status, audit_outcome=audit_outcome,
                   inspection_outcome="incomplete" if status == "incomplete" else "complete",
                   enforcement="deny" if mode == "block" and status in {"findings", "incomplete"} else "allow")
    if findings:
        payload["findings"] = findings[:MAX_RETAINED_FINDINGS]
    # Reserve structural/count metadata before retaining optional path labels.
    payload["omittedFindings"] = omitted_findings + max(0, len(findings) - MAX_RETAINED_FINDINGS)
    payload["findingsTruncated"] = findings_truncated
    payload["envFiles"] = []
    payload["omittedEnvFiles"] = len(env_files)
    retained_bytes = report_json_bytes(payload)
    for path in env_files[:MAX_FILES]:
        label = report_label(path)
        label_bytes = report_json_bytes(label) + 1
        if retained_bytes + label_bytes >= MAX_LOG_RECORD_BYTES - 128:
            break
        payload["envFiles"].append(label)
        payload["omittedEnvFiles"] -= 1
        retained_bytes += label_bytes
    while report_json_bytes(payload) >= MAX_LOG_RECORD_BYTES and payload.get("findings"):
        payload["findings"].pop()
        payload["omittedFindings"] += 1
        payload["findingsTruncated"] = True

    record = (json.dumps(payload, ensure_ascii=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    if len(record) > MAX_LOG_RECORD_BYTES:
        raise ScanLimitExceeded("log_record_limit", "scan_log", measured=len(record), limit=MAX_LOG_RECORD_BYTES)

    try:
        import fcntl
    except ImportError:
        fcntl = None

    try:
        import msvcrt
    except ImportError:
        msvcrt = None

    lock_path = log_path.with_name(f"{log_path.name}.lock")
    lock_fd = _open_secure_regular(lock_path, os.O_CREAT | os.O_RDWR)
    lock_kind = ""
    try:
        lock_kind = _acquire_log_lock(lock_fd, fcntl, msvcrt, deadline=deadline)
        enforce_deadline(deadline)
        try:
            max_bytes = int(os.environ.get("AUDIT_LOG_MAX_BYTES", "1048576"))
            backups = int(os.environ.get("AUDIT_LOG_MAX_BACKUPS", "3"))
        except ValueError as exc:
            raise ScanSecurityError("log_configuration_invalid", "scan_log") from exc
        rotate_scan_log(log_path, len(record), max_bytes, backups)
        enforce_deadline(deadline)
        log_fd = _open_secure_regular(log_path, os.O_APPEND | os.O_CREAT | os.O_WRONLY)
        with os.fdopen(log_fd, "ab") as handle:
            handle.write(record)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        if lock_kind:
            try:
                _release_log_lock(lock_fd, lock_kind, fcntl, msvcrt)
            except OSError:
                pass
        os.close(lock_fd)


def build_findings_json(findings: list[tuple[str, str, str, int, str]]) -> list[dict[str, object]]:
    return [
        {
            "pattern": pattern_name,
            "severity": severity,
            "path": report_label(path),
            "line": line_number,
            "redactedMatch": redacted,
        }
        for pattern_name, severity, path, line_number, redacted in findings
    ]


class RetainedFindings(list):
    """Only display-safe, bounded fields enter the retained report model."""

    def append(self, finding):
        pattern, severity, path, line, redacted = finding
        if len(self) < MAX_RETAINED_FINDINGS:
            super().append((pattern, severity, report_label(path), line, redacted))


def record_finding(
    findings: list[tuple[str, str, str, int, str]],
    finding: tuple[str, str, str, int, str],
    processed_findings: int,
) -> tuple[int, bool]:
    processed_findings += 1
    if len(findings) < MAX_RETAINED_FINDINGS:
        findings.append(finding)
    return processed_findings, processed_findings >= MAX_PROCESSED_FINDINGS


def emit_output(findings_count: int, log_path: Path, checked_files: int = 0, skipped: bool = False) -> None:
    if findings_count > 0:
        emit_json({"systemMessage": f"scan-secrets warning: {SCAN_ACTION}; potential secrets detected. "
                   f"security_outcome=findings; audit_outcome=written; enforcement=allow; build={REPORT_BUILD}; "
                   "profile=pending_snapshots_v1; route=pending_scan; cause=findings."})
        return
    if HOOK_EVENT == "Stop":
        if skipped:
            emit_json({"systemMessage": "scan-secrets: skipped"})
        else:
            emit_json({"systemMessage": f"scan-secrets: pass; {checked_files} modified {'file' if checked_files == 1 else 'files'}"})
        return
    emit_json({})


def normalized_mode_from_env() -> str:
    mode = os.environ.get("SCAN_MODE", "block")
    if mode not in {"warn", "block"}:
        return "block"
    return mode


def enforce_scan_budget(scan_started: float, total_bytes: int, *, now: float | None = None) -> None:
    current_time = time.monotonic() if now is None else now
    if current_time - scan_started > MAX_SCAN_SECONDS:
        raise ScanLimitExceeded("scan_timeout", seconds=int(MAX_SCAN_SECONDS))
    if total_bytes > MAX_TOTAL_BYTES:
        raise ScanLimitExceeded("total_bytes_limit", measured=total_bytes, limit=MAX_TOTAL_BYTES)


def handle_unexpected_exception(exc: Exception) -> int:
    mode = normalized_mode_from_env()
    failure = exc if isinstance(exc, ScanFailure) else ScanFailure("internal_error")
    detail = failure.detail()
    outcome = "blocked" if mode == "block" else "warning"
    processed = SCAN_REPORT.processed if SCAN_REPORT is not None else 0
    security = "findings" if processed else SCAN_SECURITY_OUTCOME
    audit = "failed"
    if INCOMPLETE_LOG is not None:
        try:
            append_scan_log(**INCOMPLETE_LOG, status="incomplete", env_files=[],
                            findings=build_findings_json(SCAN_FINDINGS),
                            omitted_findings=max(0, processed - len(SCAN_FINDINGS)),
                            findings_truncated=bool(SCAN_REPORT and SCAN_REPORT.stopped),
                            note=detail, diagnostic=failure.diagnostic(), security_outcome=security)
            audit = "written"
        except Exception:
            # Reporting must preserve the first failure even if logging also fails.
            pass
    finding_message = "potential secrets detected; scan incomplete." if processed else "scan incomplete; potential secrets could not be checked."
    reason = (f"scan-secrets {outcome}: {SCAN_ACTION}; {finding_message} {detail} "
              f"security_outcome={security}; audit_outcome={audit}; enforcement={'deny' if mode == 'block' else 'allow'}; "
              f"build={REPORT_BUILD}; profile=pending_snapshots_v1; route=pending_scan; cause={failure.cause}.")
    print(reason, file=sys.stderr)
    if mode == "block":
        emit_block_denial(reason)
    else:
        emit_json({"systemMessage": reason})
    return 0
# BEGIN PROVIDER ADAPTER
SESSION_ID_KEYS = ("session_id",)
DEFAULT_SECRETS_LOG_PATH = Path.home() / ".gemini" / "hooks" / "secrets"
HOOK_EVENT = ""


def resolve_work_dir(payload: dict) -> Path:
    hook_cwd = str(payload.get("cwd") or "")
    return Path(hook_cwd or os.environ.get("GEMINI_PROJECT_DIR") or Path.cwd())
# END PROVIDER ADAPTER



def findings_denial_reason(scan_log: Path) -> str:
    return (f"scan-secrets blocked: {SCAN_ACTION}; potential secrets detected. "
            f"security_outcome=findings; audit_outcome=written; enforcement=deny; build={REPORT_BUILD}; "
            "profile=pending_snapshots_v1; route=pending_scan; cause=findings.")

def resolve_scan_log() -> Path:
    log_dir_str = os.environ.get("SECRETS_LOG_DIR", str(DEFAULT_SECRETS_LOG_PATH))
    log_path = Path(log_dir_str)
    if log_path.is_dir() or not log_path.suffix:
        scan_log = log_path / "scan.log"
    elif log_path.suffix.lower() == ".log":
        if log_path.parent.exists() and log_path.parent.is_file():
            scan_log = log_path.parent.parent / "secrets" / log_path.name
        else:
            scan_log = log_path
    else:
        scan_log = log_path / "scan.log"
    return scan_log


def main() -> int:
    global INCOMPLETE_LOG, SCAN_ACTION, SCAN_PHASE, SCAN_REPORT, SCAN_FINDINGS
    scan_started = _SCAN_STARTED if _SCAN_STARTED is not None else time.monotonic()
    scan_deadline = scan_started + MAX_SCAN_SECONDS
    mode = normalized_mode_from_env()

    # Prepare disposable-safe failure logging before initialization or input fails.
    scan_log = resolve_scan_log()
    INCOMPLETE_LOG = {
        "log_path": scan_log, "session_id": "", "timestamp": "", "mode": mode,
        "scope": "diff", "repo_root_path": Path.cwd(),
    }
    SCAN_PHASE = "input"
    payload = read_payload()
    # Read once in bootstrap, but ordinary scans retain the normal input failure path.
    global HOOK_EVENT
    HOOK_EVENT = payload.get("hook_event_name", "")
    if not git_available():
        raise GitCommandError("git_unavailable", "initialization")
    try:
        from helpers.audit import audit_init
    except Exception:
        emit_block_denial("scan-secrets blocked: tool scan; scan incomplete; audit helper unavailable. Use the standalone diagnostics CLI. "
                          f"security_outcome=incomplete; audit_outcome=not_attempted; enforcement=deny; build={REPORT_BUILD}; "
                          "profile=pending_snapshots_v1; route=initialization; cause=audit_unavailable.")
        return 0
    if not audit_init():
        raise ScanSecurityError("audit_unavailable", "initialization")

    SCAN_PHASE = "input"
    event = payload.get("hook_event_name")
    SCAN_ACTION = (
        "session-end scan"
        if event in {"Stop", "SessionEnd", "agentStop", "subagentStop"}
        or payload.get("reason") == "complete"
        else "tool scan"
    )
    session_id = ""
    for key in SESSION_ID_KEYS:
        value = payload.get(key)
        if value:
            session_id = str(value)
            break
    timestamp = str(payload.get("timestamp") or "")

    scope = os.environ.get("SCAN_SCOPE", "diff")
    if scope not in {"diff", "staged"}:
        scope = "diff"

    SCAN_PHASE = "repository"
    work_dir = resolve_work_dir(payload)

    if not timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    INCOMPLETE_LOG = {
        "log_path": scan_log,
        "session_id": session_id,
        "timestamp": timestamp,
        "mode": mode,
        "scope": scope,
        "repo_root_path": work_dir,
    }

    if os.environ.get("SKIP_SECRETS_SCAN") == "true":
        append_scan_log(
            log_path=scan_log,
            status="skipped",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=work_dir,
            env_files=[],
            findings=[],
            note="scan disabled by SKIP_SECRETS_SCAN",
            deadline=scan_deadline,
        )
        emit_output(0, scan_log, skipped=True)
        return 0

    if not is_inside_git_repo(work_dir, deadline=scan_deadline):
        append_scan_log(
            log_path=scan_log,
            status="skipped",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=work_dir,
            env_files=[],
            findings=[],
            note="not inside git repository",
            deadline=scan_deadline,
        )
        emit_output(0, scan_log, skipped=True)
        return 0

    root = repo_root(work_dir, deadline=scan_deadline)
    root_has_head = has_head(root, deadline=scan_deadline)
    candidates = collect_files(root, scope, root_has_head, deadline=scan_deadline)
    SCAN_PHASE = "candidate_scan"

    if not candidates:
        append_scan_log(
            log_path=scan_log,
            status="clean",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=root,
            env_files=[],
            findings=[],
            note="no modified files to scan",
            deadline=scan_deadline,
        )
        emit_output(0, scan_log)
        return 0

    allowlist = parse_allowlist(os.environ.get("SECRETS_ALLOWLIST"))
    env_files: list[str] = []
    findings = RetainedFindings()
    report = StreamReport(findings)
    SCAN_REPORT, SCAN_FINDINGS = report, findings
    budget = ScanBudget(scan_deadline)
    total_bytes = 0
    with snapshot_source(root, candidates, budget) as snapshots:
        for source, path in candidates:
            SCAN_PHASE = "candidate_read"
            with snapshots.acquire((source, path)) as snapshot:
                if snapshot is None:
                    continue
                SCAN_PHASE = "candidate_scan"
                total_bytes = budget.used_bytes
                enforce_scan_budget(scan_started, total_bytes)

                if is_env_path(path) and path not in env_files:
                    env_files.append(path)

                if is_credential_path(path):
                    allowlist_text = f"{path}:1:credential_path:[SENSITIVE PATH]"
                    if not allowlist_contains("scan_secrets", allowlist_text, allowlist):
                        report.processed, report.stopped = record_finding(
                            findings,
                            ("credential_path", "critical", path, 1, "[SENSITIVE PATH]"),
                            report.processed,
                        )

                if report.stopped:
                    break

                is_allowlisted = lambda key: allowlist_contains("scan_secrets", key, allowlist)
                check_budget = lambda: enforce_deadline(scan_deadline)
                if (snapshot.classification == "binary" or scope == "staged"
                      or not root_has_head or source == CANDIDATE_UNTRACKED
                      or source in CANDIDATE_UNMERGED_STAGES or source == CANDIDATE_UNMERGED_WORKTREE):
                    scan_line_events(path,
                        full_line_events(snapshot.chunks(), snapshot.classification, check_budget),
                        report, is_allowlisted, redact_match, check_budget)
                else:
                    scan_diff_added_lines(root, path, source, report, is_allowlisted,
                        root_has_head=root_has_head, deadline=scan_deadline)
                SCAN_PHASE = "candidate_scan"
                if report.stopped:
                    break

    enforce_scan_budget(scan_started, total_bytes)

    if not findings:
        append_scan_log(
            log_path=scan_log,
            status="clean",
            session_id=session_id,
            timestamp=timestamp,
            mode=mode,
            scope=scope,
            repo_root_path=root,
            env_files=env_files,
            findings=[],
            deadline=scan_deadline,
        )
        emit_output(0, scan_log, checked_files=len(candidates))
        return 0

    findings_json = build_findings_json(findings)
    omitted_findings = report.processed - len(findings)
    enforce_scan_budget(scan_started, total_bytes)
    append_scan_log(
        log_path=scan_log,
        status="findings",
        session_id=session_id,
        timestamp=timestamp,
        mode=mode,
        scope=scope,
        repo_root_path=root,
        env_files=env_files,
        findings=findings_json,
        omitted_findings=omitted_findings,
        findings_truncated=report.stopped or omitted_findings > 0,
        deadline=scan_deadline,
    )
    if mode == "block":
        emit_block_denial(findings_denial_reason(scan_log))
        return 0

    emit_output(report.processed, scan_log)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(handle_unexpected_exception(exc))

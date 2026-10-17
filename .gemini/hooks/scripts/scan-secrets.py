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

# BEGIN PROVIDER ADAPTER
def block_denial_payload(reason: str, hook_event: str) -> dict:
    return {"decision": "deny", "reason": reason}


def emit_block_denial(reason: str) -> None:
    emit_json(block_denial_payload(reason, HOOK_EVENT))
# END PROVIDER ADAPTER

import re as _label_re


def credential_label(text):
    """Recognize credentials in caller-normalized labels before display clipping."""
    return bool(_label_re.search(r"(?i)(?:gh[pousr]_|github_pat_|akia|sk-|sk_live_|xox[baprs]-|bearer\s|(?:token|secret|password|passwd|api[_-]?key|authorization)\s*[:=]|https?://[^/\s]*@)", text))
SECURITY_HOOK_FILES = ('scan-secrets.py', 'tool-guard.py', 'scan-status.py')
def serialize_trusted_launch(python: str, script: str, shell: str, *, windows: bool = False) -> str:
    """Quote an already validated five-operand security-hook launch."""
    import shlex

    arguments = [python, "-I", "-S", "-B", script]
    if shell == "powershell":
        return "& " + " ".join("'" + item.replace("'", "''") + "'" for item in arguments)
    if shell == "windows" or (shell == "native" and windows):
        return f'"{arguments[0]}" -I -S -B "{arguments[-1]}"'
    return shlex.join(arguments)

def trusted_posix_arguments(command: str) -> list[str] | None:
    """Recognize only the shared POSIX isolated-interpreter argument shape."""
    from pathlib import Path
    import shlex

    try:
        arguments = shlex.split(command)
    except ValueError:
        return None
    if (len(arguments) != 5 or arguments[1:4] != ["-I", "-S", "-B"]
            or not Path(arguments[0]).is_absolute()):
        return None
    return arguments

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


def _diag_owner_or_mode_unsafe(info):
    return _diag_os.name != "nt" and bool(info.st_mode & 0o022 or info.st_uid != _diag_os.getuid())


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
    normalized = _diag_unicode.normalize("NFKC", value)
    if credential_label(normalized) or _diag_re.search(r"(?i)(sk_test_|rk_live_|ASIA|https?[:/]|auth|password|passwd|secret|token|bearer)", normalized):
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
            if _diag_owner_or_mode_unsafe(info):
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


def _diag_installed_expected(script, registrations=None, executable=None):
    registrations = DIAG_REGISTRATIONS if registrations is None else registrations
    expected = set(registrations)
    for serialized in registrations:
        event, matcher, handler = _diag_json.loads(serialized)
        keys = ("bash", "powershell") if DIAG_PROVIDER == "copilot" else ("command", "commandWindows") if DIAG_PROVIDER == "codex" else ("command",)
        for filename in SECURITY_HOOK_FILES:
            if not any(filename in handler.get(key, "") for key in keys):
                continue
            python = executable or _diag_sys.executable
            path = str(_DiagPath(script).absolute().parent / filename)
            for key in keys:
                shell = "powershell" if key == "powershell" else "windows" if key == "commandWindows" else "native" if key == "command" else "posix"
                handler[key] = serialize_trusted_launch(python, path, shell, windows=_diag_os.name == "nt")
            expected.discard(serialized)
            expected.add(_diag_fingerprint(event, matcher, handler))
    return expected


def _diag_registered_python(handler):
    command = handler.get("bash" if DIAG_PROVIDER == "copilot" else "command")
    if not isinstance(command, str):
        return None
    try:
        if DIAG_PROVIDER == "gemini" and _diag_os.name == "nt":
            prefix, separator, remainder = command.partition(" -I -S -B ")
            executable = prefix[1:-1] if prefix.startswith('"') and prefix.endswith('"') else prefix
            if not separator:
                return None
        else:
            arguments = trusted_posix_arguments(command)
            if arguments is None:
                return None
            executable = arguments[0]
        return executable if _DiagPath(executable).is_absolute() else None
    except ValueError:
        return None


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
        expected = _diag_installed_expected(script)
        # Source/copy fixtures retain canonical registrations; installed commands
        # must match an exact launch, including every interpreter operand.
        source_expected = set(DIAG_REGISTRATIONS)
        seen = set()
        matched = set()
        events = set()
        for event, groups in config["hooks"].items():
            if DIAG_PROVIDER == "gemini" and event == "disabled":
                if not isinstance(groups, list) or not all(isinstance(name, str) for name in groups):
                    raise _DiagnosticsUnavailable("malformed")
                continue
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
                    executable = _diag_registered_python(handler)
                    selected_expected = _diag_installed_expected(script, executable=executable) if executable else expected
                    commands = {field: handler[field] for field in ("bash", "powershell", "command", "commandWindows") if field in handler}
                    duplicate_key = _diag_fingerprint(event, None, commands or handler)
                    if duplicate_key in seen:
                        result["duplicates"] += 1
                    seen.add(duplicate_key)
                    if key in selected_expected or key in source_expected:
                        result["owned"] += 1
                        if key in source_expected:
                            matched.update(_diag_installed_expected(script, [key]))
                        else:
                            # Retain one stable identity when doctor uses another
                            # trusted interpreter than the one selected at install.
                            for canonical in DIAG_REGISTRATIONS:
                                if key in _diag_installed_expected(script, [canonical], executable):
                                    matched.update(_diag_installed_expected(script, [canonical]))
                    else:
                        result["unowned"] += 1
        result["missing"] = len(expected - matched)
        result["events"] = sorted(events)
        result["cause"] = "observed"
        if _diag_owner_or_mode_unsafe(info):
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
DIAG_BUILD = '24107b4728788a54ac6db20b97f27b3cad2f2ce1f2bd7dcfa4c3dc4b1a65f0b0'
DIAG_ASSETS = [('helpers/common.py', 'f8f2bf01352288c56a763f178359c0a57f958c2f047a2e2b9a81c7f6853bd169'), ('helpers/audit.py', '0a41a58053222793ff30388309ccd0196a1e85603d003f7965ff340d2d8a5661'), ('tool-guard.py', None), ('helpers/tool_guard_policy.py', 'c3ee195c5bd9eb51c35c799f3d41cf39440d1ec7771917df5411aeecb07a60fe'), ('helpers/scan_types.py', '19f69ccb6d3268d9c43c353b86c0898d75994c1bf1279a544eed52dbac2bfe59'), ('helpers/scan_reporting.py', '0b3d355f49f49d22ac8340e644635c7ad7306af59c22215ace7e42c5b94e1c28'), ('helpers/scan_allowlist.py', '370485db39a1ceccee1bfdf078ef21b490f778b5e5e8644dab644c2984fcbe43'), ('helpers/scan_stream.py', '631b9d0b3f3b9389be6de37843f941c35950256f0c7b9c55fd5a874fbd4abf31'), ('helpers/scan_git.py', '5f40f7158fb649f23056da9a20d2c7239786f6b82493403fb9e0f31d4ebd7809'), ('helpers/scan_audit.py', '501f7dc6d5705538672642061835f9d1b95a35b2c69f1b73ba29d9934bc15450'), ('helpers/scan_native_file.py', '1c07697a5020bed461b41f3c0015c7dc798fc8f5c62941af60947c003ea4adf8'), ('helpers/scan_native_process.py', 'ed68b76b0021e2514ffd0822eba2a463e1bfb459ab707d47a4161c42e909bbc1'), ('helpers/scan_engine.py', '2f75e639211905e25650af46959512e49ac2abb338aa248ffeb74b81d43570d1'), ('scan-status.py', None), ('scan-secrets.py', None), ('hooks-diagnostics.py', None)]
DIAG_POLICY_LIMITS = {'scope': 'canonical scanner constants and Guardian input-bound subset', 'scanner': {'MAX_FILES': 256, 'MAX_FILE_BYTES': 'not_defined', 'MAX_TOTAL_BYTES': 8388608, 'MAX_SCAN_SECONDS': 8.0}, 'guardian': {'MAX_SCAN_TEXT': 32768, 'MAX_NATIVE_DATA_BYTES': 65536, 'MAX_NATIVE_PATCH_BYTES': 262144, 'MAX_COMMAND_SEGMENTS': 128, 'MAX_COMMAND_TOKENS': 256, 'MAX_STRUCTURED_DEPTH': 32, 'MAX_STRUCTURED_NODES': 256, 'MAX_STRUCTURED_STRINGS': 128}}
DIAG_EVENTS = ['AfterAgent', 'AfterModel', 'AfterTool', 'BeforeAgent', 'BeforeModel', 'BeforeTool', 'BeforeToolSelection', 'Notification', 'PreCompress', 'SessionEnd', 'SessionStart']
DIAG_REGISTRATIONS = ['["SessionStart",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"SessionStart"},"type":"command"}]', '["SessionStart",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/skill-context-injector.py\\"","description":"Loads required skill files and injects them as context before each agent turn.","env":{"AGENTS_REQUIRED_SKILL_FILES":"caveman/SKILL.md"},"name":"skill-context-injector","type":"command"}]', '["AfterAgent",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"AfterAgent"},"type":"command"}]', '["AfterAgent",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/scan-status.py\\"","description":"Reports historical secret-scan status without scanning or blocking turn completion.","name":"scan-secrets","timeout":2000,"type":"command"}]', '["BeforeAgent",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"BeforeAgent"},"type":"command"}]', '["BeforeModel",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"BeforeModel"},"type":"command"}]', '["AfterModel",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"AfterModel"},"type":"command"}]', '["BeforeToolSelection",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"BeforeToolSelection"},"type":"command"}]', '["BeforeTool","*",{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"BeforeTool"},"type":"command"}]', '["BeforeTool","*",{"command":"python \\"$HOME/.gemini/hooks/scripts/tool-guard.py\\"","description":"Blocks dangerous Gemini tool invocations using same policy patterns as Copilot tool-guard.","name":"tool-guard","type":"command"}]', '["BeforeTool","run_shell_command",{"command":"python \\"$HOME/.gemini/hooks/scripts/rtk-hook-gemini.py\\"","timeout":5000,"type":"command"}]', '["AfterTool",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"AfterTool"},"type":"command"}]', '["PreCompress",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"PreCompress"},"type":"command"}]', '["Notification",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"Notification"},"type":"command"}]', '["SessionEnd",null,{"command":"python \\"$HOME/.gemini/hooks/scripts/send-event.py\\"","env":{"OBSERVABILITY_CAPTURE_EVENT":"true","OBSERVABILITY_SOURCE_EVENT_NAME":"SessionEnd"},"type":"command"}]']
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
    if DIAG_PROVIDER == "codex":
        metadata.update(model=256, turn_id=256)
        if "permission_mode" in payload and (type(payload["permission_mode"]) is not str or payload["permission_mode"] not in {"default", "acceptEdits", "plan", "dontAsk", "bypassPermissions"}):
            return False
    extra_metadata = {"permission_mode"} if DIAG_PROVIDER == "codex" else set()
    if not set(payload) <= {"hook_event_name", tool_key, args_key, "timestamp", *metadata, *extra_metadata}:
        return False
    if any((type(payload[key]) is not str or len(payload[key]) > limit)
           and not (DIAG_PROVIDER == "codex" and key == "transcript_path" and payload[key] is None)
           for key, limit in metadata.items() if key in payload):
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
    return block_denial_payload(reason, "PreToolUse")
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
MAX_FILES = 256
MAX_TOTAL_BYTES = 8388608
MAX_GIT_OUTPUT_BYTES = 8388608
MAX_SCAN_SECONDS = 8.0
INCOMPLETE_LOG = None
SCAN_ACTION = "scan"
SCAN_RESULT = None
SCAN_SECURITY_OUTCOME = "incomplete"
REPORT_BUILD = "e7a03131aa64264b"
REPORT_PROVIDER = DIAG_PROVIDER

# Optional detector assets load only after exact diagnostics recovery routing.
_SCAN_RUNTIME_ERROR = None
try:
    from helpers.scan_native_file import WindowsDirectoryHandles
    from helpers.scan_native_process import NativeProcess
    from helpers.scan_types import ScanLimits, ScanFailure, ScanSecurityError, GitCommandError
    from helpers.scan_engine import ScanPolicy, scan
    from helpers.scan_allowlist import parse_allowlist
    from helpers.scan_audit import AuditPolicy, append_scan_log as _write_scan_log
except Exception:
    _SCAN_RUNTIME_ERROR = True


def noop():
    emit_json({})
    raise SystemExit(0)
def scanner_attribution(security: str, audit: str, enforcement: str, route: str, cause: str) -> str:
    return (f"security_outcome={security}; audit_outcome={audit}; enforcement={enforcement}; build={REPORT_BUILD}; "
            f"profile=pending_snapshots_v1; route={route}; cause={cause}.")


def emit_output(findings_count: int, log_path: Path, checked_files: int = 0, skipped: bool = False) -> None:
    if findings_count > 0:
        emit_json({"systemMessage": f"scan-secrets warning: {SCAN_ACTION}; potential secrets detected. "
                   + scanner_attribution("findings", "written", "allow", "pending_scan", "findings")})
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


def append_scan_log(**kwargs):
    global SCAN_SECURITY_OUTCOME
    if kwargs.get("status") != "incomplete":
        SCAN_SECURITY_OUTCOME = kwargs.get("status", "incomplete")
    result = SCAN_RESULT
    if result is not None:
        result.audit_outcome = "written"
        kwargs["scan_result"] = result.summary()
    try:
        _write_scan_log(AuditPolicy(REPORT_BUILD, REPORT_PROVIDER, SCAN_ACTION, MAX_FILES,
                        os.environ.get("AUDIT_LOG_MAX_BYTES", "1048576"),
                        os.environ.get("AUDIT_LOG_MAX_BACKUPS", "3")), **kwargs)
    except BaseException:
        if result is not None:
            result.audit_outcome = "failed"
            result.outcome = "incomplete"
            if result.failure is None:
                result.reason = "audit_unavailable"
        raise


def handle_unexpected_exception(exc):
    mode = normalized_mode_from_env()
    failure = exc if isinstance(exc, ScanFailure) else ScanFailure("internal_error")
    detail = failure.detail()
    outcome = "blocked" if mode == "block" else "warning"
    result = SCAN_RESULT
    processed = result.counts["processed_findings"] if result else 0
    security = "findings" if processed else SCAN_SECURITY_OUTCOME
    audit = "failed"
    if INCOMPLETE_LOG is not None:
        try:
            append_scan_log(**INCOMPLETE_LOG, status="incomplete", env_files=result.env_files if result else [],
                            findings=result.findings if result else [],
                            omitted_findings=max(0, processed - len(result.findings)) if result else 0,
                            findings_truncated=bool(result and (processed > len(result.findings))),
                            note=detail, diagnostic=failure.diagnostic(), security_outcome=security)
            audit = "written"
        except Exception:
            pass
    finding_message = "potential secrets detected; scan incomplete." if processed else "scan incomplete; potential secrets could not be checked."
    reason = (f"scan-secrets {outcome}: {SCAN_ACTION}; {finding_message} {detail} "
              + scanner_attribution(security, audit, "deny" if mode == "block" else "allow", "pending_scan", failure.cause))
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
            + scanner_attribution("findings", "written", "deny", "pending_scan", "findings"))

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
    global INCOMPLETE_LOG, SCAN_ACTION, SCAN_RESULT, HOOK_EVENT
    if isinstance(_SCAN_PAYLOAD, dict):
        HOOK_EVENT = _SCAN_PAYLOAD.get("hook_event_name", "")
    if _SCAN_RUNTIME_ERROR:
        emit_block_denial("scan-secrets blocked: tool scan; scan incomplete; scanner helper unavailable. Use the standalone diagnostics CLI. "
                          + scanner_attribution("incomplete", "not_attempted", "deny", "initialization", "internal_error"))
        return 0
    mode = normalized_mode_from_env()
    scan_started = _SCAN_STARTED if _SCAN_STARTED is not None else time.monotonic()
    scan_log = resolve_scan_log()
    INCOMPLETE_LOG = {"log_path": scan_log, "session_id": "", "timestamp": "", "mode": mode,
                      "scope": "diff", "repo_root_path": Path.cwd()}
    _load_scan_payload()
    if _SCAN_INPUT_ERROR:
        raise ScanSecurityError(_SCAN_INPUT_ERROR, "input")
    payload = _SCAN_PAYLOAD
    if not isinstance(payload, dict):
        raise ScanSecurityError("input_invalid", "input")
    HOOK_EVENT = payload.get("hook_event_name", "")
    if shutil.which("git") is None:
        raise GitCommandError("git_unavailable", "initialization")
    try:
        from helpers.audit import audit_init
    except Exception:
        emit_block_denial("scan-secrets blocked: tool scan; scan incomplete; audit helper unavailable. Use the standalone diagnostics CLI. "
                          + scanner_attribution("incomplete", "not_attempted", "deny", "initialization", "audit_unavailable"))
        return 0
    if not audit_init():
        raise ScanSecurityError("audit_unavailable", "initialization")
    event = payload.get("hook_event_name")
    SCAN_ACTION = ("session-end scan" if event in {"Stop", "SessionEnd", "agentStop", "subagentStop"}
                   or payload.get("reason") == "complete" else "tool scan")
    session_id = next((str(payload[key]) for key in SESSION_ID_KEYS if payload.get(key)), "")
    timestamp = str(payload.get("timestamp") or "")
    scope = os.environ.get("SCAN_SCOPE", "diff")
    if scope not in {"diff", "staged"}:
        scope = "diff"
    work_dir = resolve_work_dir(payload)
    INCOMPLETE_LOG = {"log_path": scan_log, "session_id": session_id, "timestamp": timestamp,
                      "mode": mode, "scope": scope, "repo_root_path": work_dir}
    log_context = {**INCOMPLETE_LOG, "deadline": scan_started + MAX_SCAN_SECONDS}
    if os.environ.get("SKIP_SECRETS_SCAN") == "true":
        append_scan_log(**log_context, status="skipped", env_files=[], findings=[],
                        note="scan disabled by SKIP_SECRETS_SCAN")
        emit_output(0, scan_log, skipped=True)
        return 0
    policy = ScanPolicy(REPORT_BUILD, scope, allowlist=tuple(parse_allowlist(os.environ.get("SECRETS_ALLOWLIST"))))
    result = scan(work_dir, policy,
                  ScanLimits(MAX_FILES, MAX_TOTAL_BYTES, MAX_SCAN_SECONDS, MAX_GIT_OUTPUT_BYTES),
                  started=scan_started)
    SCAN_RESULT = result
    if result.failure is not None:
        raise result.failure
    if result.skipped:
        append_scan_log(**log_context, status="skipped", env_files=[], findings=[], note="not inside git repository")
        emit_output(0, scan_log, skipped=True)
        return 0
    log_context["repo_root_path"] = result.root
    processed = result.counts["processed_findings"]
    append_scan_log(**log_context, status="findings" if processed else "clean", env_files=result.env_files,
                    findings=result.findings, omitted_findings=result.counts["omitted_findings"],
                    findings_truncated=result.counts["omitted_findings"] > 0,
                    note="no modified files to scan" if not result.counts["candidates"] else "")
    if processed and mode == "block":
        emit_block_denial(findings_denial_reason(scan_log))
    else:
        emit_output(processed, scan_log, checked_files=result.counts["candidates"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        if _SCAN_RUNTIME_ERROR:
            emit_block_denial("scan-secrets blocked: tool scan; scan incomplete; scanner helper unavailable.")
            raise SystemExit(0)
        raise SystemExit(handle_unexpected_exception(exc))

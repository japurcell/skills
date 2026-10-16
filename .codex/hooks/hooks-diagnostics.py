#!/usr/bin/env python3
# Generated from hooks/families/diagnostics.py by scripts/generate-hooks.py. Do not edit.
from __future__ import annotations


import re as _label_re


def credential_label(text):
    """Recognize credentials in caller-normalized labels before display clipping."""
    return bool(_label_re.search(r"(?i)(?:gh[pousr]_|github_pat_|akia|sk-|sk_live_|xox[baprs]-|bearer\s|(?:token|secret|password|passwd|api[_-]?key|authorization)\s*[:=]|https?://[^/\s]*@)", text))
SECURITY_HOOK_FILES = ('scan-secrets.py', 'tool-guard.py')
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
DIAG_PROVIDER = 'codex'
DIAG_LIMITS = {'directories': 1024, 'entries': 4096, 'records': 256, 'unsafe_records': 16, 'depth': 32, 'label_bytes': 160, 'seconds': 1.0, 'response_bytes': 16384, 'assets': 64, 'hash_bytes': 1048576, 'settings_bytes': 262144}
DIAG_BUILD = 'a313eff1bc12df4d53d490026ba6ee63443569740abb4422f9737fcaa7f5e164'
DIAG_ASSETS = [('helpers/common.py', '55be5cd5746e2674ab1e8446135d3da569c453ed43b5cdb78d0618ca6ba4a45b'), ('helpers/audit.py', 'ccc58956b61edb5e6bb4914ed90326c0fedc565fd3732d4c6edccac6136f9f87'), ('tool-guard.py', None), ('helpers/tool_guard_policy.py', 'c3ee195c5bd9eb51c35c799f3d41cf39440d1ec7771917df5411aeecb07a60fe'), ('helpers/scan_types.py', '19f69ccb6d3268d9c43c353b86c0898d75994c1bf1279a544eed52dbac2bfe59'), ('helpers/scan_reporting.py', '0b3d355f49f49d22ac8340e644635c7ad7306af59c22215ace7e42c5b94e1c28'), ('helpers/scan_allowlist.py', '370485db39a1ceccee1bfdf078ef21b490f778b5e5e8644dab644c2984fcbe43'), ('helpers/scan_stream.py', '631b9d0b3f3b9389be6de37843f941c35950256f0c7b9c55fd5a874fbd4abf31'), ('helpers/scan_git.py', 'c2dc79618e2fa3cf370052c77f630921e7e5b5d05770cacd3c6fb73ef57e0f0d'), ('helpers/scan_audit.py', '501f7dc6d5705538672642061835f9d1b95a35b2c69f1b73ba29d9934bc15450'), ('helpers/scan_native_file.py', '52dd7df2f11c151b65a22f2a52cb5f248f38eae552523cbbc01c4b8defd8d0e3'), ('helpers/scan_engine.py', '2f75e639211905e25650af46959512e49ac2abb338aa248ffeb74b81d43570d1'), ('scan-status.py', None), ('scan-secrets.py', None), ('hooks-diagnostics.py', None)]
DIAG_POLICY_LIMITS = {'scope': 'canonical scanner constants and Guardian input-bound subset', 'scanner': {'MAX_FILES': 256, 'MAX_FILE_BYTES': 'not_defined', 'MAX_TOTAL_BYTES': 8388608, 'MAX_SCAN_SECONDS': 8.0}, 'guardian': {'MAX_SCAN_TEXT': 32768, 'MAX_NATIVE_DATA_BYTES': 65536, 'MAX_NATIVE_PATCH_BYTES': 262144, 'MAX_COMMAND_SEGMENTS': 128, 'MAX_COMMAND_TOKENS': 256, 'MAX_STRUCTURED_DEPTH': 32, 'MAX_STRUCTURED_NODES': 256, 'MAX_STRUCTURED_STRINGS': 128}}
DIAG_EVENTS = ['PreToolUse', 'SessionStart', 'Stop']
DIAG_REGISTRATIONS = ['["SessionStart","startup|resume|clear|compact",{"additionalContextLimit":8000,"command":"python3 ~/.codex/hooks/load-required-skills.py","commandWindows":"py -3 \\"%USERPROFILE%\\\\.codex\\\\hooks\\\\load-required-skills.py\\"","statusMessage":"Loading required skill context","timeout":5,"type":"command"}]', '["PreToolUse","Bash|apply_patch|Edit|Write",{"command":"python3 ~/.codex/hooks/scan-secrets.py","commandWindows":"py -3 \\"%USERPROFILE%\\\\.codex\\\\hooks\\\\scan-secrets.py\\"","statusMessage":"Scanning modified files for secrets","timeout":10,"type":"command"}]', '["PreToolUse","Bash|apply_patch|Edit|Write",{"command":"python3 ~/.codex/hooks/tool-guard.py","commandWindows":"py -3 \\"%USERPROFILE%\\\\.codex\\\\hooks\\\\tool-guard.py\\"","statusMessage":"Checking dangerous tool actions","timeout":10,"type":"command"}]', '["Stop",null,{"command":"python3 ~/.codex/hooks/scan-secrets.py","commandWindows":"py -3 \\"%USERPROFILE%\\\\.codex\\\\hooks\\\\scan-secrets.py\\"","statusMessage":"Checking modified files for secrets","timeout":10,"type":"command"}]']
# END PROVIDER ADAPTER

def diagnostics_main(argv=None):
    arguments = list(_diag_sys.argv[1:] if argv is None else argv)
    if arguments not in ([], ["--doctor"], ["--help"]):
        _diag_sys.stderr.write("usage: hooks-diagnostics.py [--doctor | --help]\n")
        return 2
    if arguments == ["--help"]:
        _diag_sys.stdout.write("usage: hooks-diagnostics.py [--doctor | --help]\nNo operands: current-directory metadata plus fixed installation checks.\n--doctor: fixed installation checks only. No content scan or execution permission.\n")
        return 0
    _diag_sys.stdout.buffer.write(diagnostics_encode(diagnostics_collect(__file__, doctor=bool(arguments))))
    return 0


if __name__ == "__main__":
    raise SystemExit(diagnostics_main())

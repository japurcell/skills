"""Canonical stdlib-only diagnostics collector and generated CLI renderer."""
from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import json
from pathlib import Path

from hooks.manifest import GeneratedTarget, targets
from hooks.providers import Provider
from hooks.families.reporting import CREDENTIAL_LABEL_SOURCE
from scripts.trusted_hook_launch import (SECURITY_HOOK_FILES, BRAIN_HOOK_FILES, PINNED_HOOK_FILES,
                                         hook_arguments, serialize_trusted_launch, trusted_posix_arguments)

LIMITS = {"directories": 1024, "entries": 4096, "records": 256,
          "unsafe_records": 16, "depth": 32, "label_bytes": 160,
          "seconds": 1.0, "response_bytes": 16384, "assets": 64,
          "hash_bytes": 1048576, "settings_bytes": 262144}

POLICY_NAMES = {
    "scanner": ("families/scan_secrets.py", ("MAX_FILES", "MAX_FILE_BYTES", "MAX_TOTAL_BYTES", "MAX_SCAN_SECONDS")),
    "guardian": ("runtime/tool_guard_policy.py", ("MAX_SCAN_TEXT", "MAX_NATIVE_DATA_BYTES", "MAX_NATIVE_PATCH_BYTES", "MAX_COMMAND_SEGMENTS", "MAX_COMMAND_TOKENS", "MAX_STRUCTURED_DEPTH", "MAX_STRUCTURED_NODES", "MAX_STRUCTURED_STRINGS")),
}


def _policy_limits(repo: Path) -> dict:
    """Extract trusted canonical numeric assignments without importing runtime code."""
    result = {"scope": "canonical scanner constants and Guardian input-bound subset"}
    for label, (filename, names) in POLICY_NAMES.items():
        outer = ast.parse((repo / "hooks" / filename).read_text())
        trees = [outer]
        if label == "scanner":
            trees.append(ast.parse((repo / "hooks/runtime/scan_types.py").read_text()))
        for node in ast.walk(outer):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and "MAX_" in node.value:
                try:
                    trees.append(ast.parse(node.value))
                except SyntaxError:
                    continue
        assignments = {}
        for tree in trees:
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            assignments[target.id] = node.value

        def number(node, seen=()):
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return node.value
            if isinstance(node, ast.Name) and node.id in assignments and node.id not in seen:
                return number(assignments[node.id], (*seen, node.id))
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
                left, right = number(node.left, seen), number(node.right, seen)
                return left + right if isinstance(node.op, ast.Add) else (left - right if isinstance(node.op, ast.Sub) else left * right)
            raise ValueError(f"Unsupported canonical policy limit expression in {filename}")

        result[label] = {name: number(assignments[name]) if name in assignments else "not_defined" for name in names}
    return result

RUNTIME = r'''import hashlib as _diag_hashlib
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
        for filename in PINNED_HOOK_FILES:
            if not any(filename in handler.get(key, "") for key in keys):
                continue
            python = executable or _diag_sys.executable
            path = str(_DiagPath(script).absolute().parent / filename)
            for key in keys:
                shell = "powershell" if key == "powershell" else "windows" if key == "commandWindows" else "native" if key == "command" else "posix"
                handler[key] = serialize_trusted_launch(python, path, shell, windows=_diag_os.name == "nt", extra=hook_arguments(filename, DIAG_PROVIDER))
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
'''

CLI = r'''def diagnostics_main(argv=None):
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
'''


def collector_source(provider: Provider) -> str:
    """Self-contained source for embedding before optional scanner imports."""
    if provider.name not in {"codex", "copilot", "gemini"}:
        raise ValueError("Unsupported diagnostics provider")
    repo = Path(__file__).resolve().parents[2]
    template = {"codex": ".codex/global-hooks.json", "copilot": ".copilot/hooks/hooks.json", "gemini": ".gemini/global-settings.json"}[provider.name]
    config = json.loads((repo / template).read_bytes())
    registrations = []
    for event, groups in config.get("hooks", {}).items():
        if provider.name == "gemini" and event == "disabled":
            continue
        for group in groups:
            for handler in ([group] if provider.name == "copilot" else group["hooks"]):
                registrations.append(json.dumps([event, None if provider.name == "copilot" else group.get("matcher"), handler], sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    entryroot = provider.hook_root if provider.name == "codex" else provider.hook_root / "scripts"
    assets = []
    for target in targets():
        if target.provider == provider.name and target.family in {"scan_secrets", "scan_status", "scan_runtime", "common", "audit", "tool_guard"}:
            family = importlib.import_module("hooks.families." + target.family)
            # Entrypoints can embed this collector later: no self-render/hash cycle.
            expected = None if target.output_path.parent == entryroot else hashlib.sha256(family.render(provider, target).encode()).hexdigest()
            assets.append((target.output_path.relative_to(entryroot).as_posix(), expected))
    assets.append(("hooks-diagnostics.py", None))
    identity = hashlib.sha256()
    for path in sorted((repo / "hooks").rglob("*.py")):
        identity.update(path.relative_to(repo).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    launch_source = (f"SECURITY_HOOK_FILES = {SECURITY_HOOK_FILES!r}\n"
                     + f"BRAIN_HOOK_FILES = {BRAIN_HOOK_FILES!r}\nPINNED_HOOK_FILES = {PINNED_HOOK_FILES!r}\n"
                     + inspect.getsource(hook_arguments) + "\n"
                     + inspect.getsource(serialize_trusted_launch) + "\n"
                     + inspect.getsource(trusted_posix_arguments) + "\n")
    identity.update(launch_source.encode())
    identity.update((repo / template).read_bytes())
    identity.update(json.dumps([provider.name, LIMITS], sort_keys=True).encode())
    constants = (f"DIAG_PROVIDER = {provider.name!r}\nDIAG_LIMITS = {LIMITS!r}\n"
                 f"DIAG_BUILD = {identity.hexdigest()!r}\nDIAG_ASSETS = {assets!r}\n"
                 f"DIAG_POLICY_LIMITS = {_policy_limits(repo)!r}\n"
                 f"DIAG_EVENTS = {sorted(config.get('hooks', {}))!r}\nDIAG_REGISTRATIONS = {registrations!r}\n")
    return CREDENTIAL_LABEL_SOURCE + launch_source + RUNTIME + "\n# BEGIN PROVIDER ADAPTER\n" + constants + "# END PROVIDER ADAPTER\n"


def render(provider: Provider, target: GeneratedTarget) -> str:
    if target.provider != provider.name or target.output_path.name != "hooks-diagnostics.py":
        raise ValueError("Diagnostics target/provider mismatch")
    return "#!/usr/bin/env python3\n# Generated from hooks/families/diagnostics.py by scripts/generate-hooks.py. Do not edit.\nfrom __future__ import annotations\n\n" + collector_source(provider) + "\n" + CLI

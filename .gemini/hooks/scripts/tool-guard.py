#!/usr/bin/env python3
# Generated from hooks/families/tool_guard.py by scripts/generate-hooks.py. Do not edit.

from __future__ import annotations

# BEGIN PROVIDER ADAPTER
import json
import os
import stat
import sys
import time
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None

try:
    import msvcrt
except ImportError:
    msvcrt = None

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.common import emit_json, read_json_input  # noqa: E402


TOOL_NAME_KEYS = ("tool_name", "toolName")
TOOL_INPUT_KEYS = ("tool_input", "toolInput", "toolArgs")


def emit_skip_allow_response() -> None:
    emit_json({"decision": "allow"})
    raise SystemExit(0)


def emit_allow_response(system_message: str | None = None) -> None:
    payload: dict[str, str] = {"decision": "allow"}
    if system_message:
        payload["systemMessage"] = system_message
    emit_json(payload)
    raise SystemExit(0)


def emit_deny_response(reason: str) -> None:
    emit_json({"decision": "deny", "reason": reason, "systemMessage": reason})
    raise SystemExit(0)
# END PROVIDER ADAPTER


import re
import shlex
import unicodedata


MAX_SCAN_TEXT = 32768
MAX_COMMAND_SEGMENTS = 128
MAX_COMMAND_TOKENS = 256
MAX_EXCERPT_LENGTH = 160
REDACTED = "[REDACTED]"

def R(*codes: int) -> str:
    return "".join(chr(code) for code in codes)


def _is_word_char(char: str) -> bool:
    return char.isalnum() or char == "_"


def _find_word(lower_text: str, word: str, start: int = 0) -> int:
    index = lower_text.find(word, start)
    while index != -1:
        before = lower_text[index - 1] if index > 0 else ""
        after_index = index + len(word)
        after = lower_text[after_index] if after_index < len(lower_text) else ""
        if not _is_word_char(before) and not _is_word_char(after):
            return index
        index = lower_text.find(word, index + 1)
    return -1


def _simple_match(*codes: int):
    needle = R(*codes)

    def matcher(text: str, lower_text: str) -> str | None:
        index = lower_text.find(needle)
        if index == -1:
            return None
        return text[index : index + len(needle)]

    return matcher


def _command_segments(text: str) -> list[list[str]]:
    normalized = unicodedata.normalize("NFKC", text[:MAX_SCAN_TEXT])
    raw_segments = re.split(r"(?:\r?\n|\\[nr]|&&|\|\||;)", normalized)
    segments: list[list[str]] = []
    for raw_segment in raw_segments[:MAX_COMMAND_SEGMENTS]:
        token_source = re.sub(r'[{}\[\]",:]', " ", raw_segment)
        try:
            tokens = shlex.split(token_source, comments=False, posix=True)
        except ValueError:
            tokens = token_source.split()
        if tokens:
            segments.append(tokens[:MAX_COMMAND_TOKENS])
    return segments


def _matches_protected_remove_target(target: str, target_kind: str) -> bool:
    unquoted = target.rstrip("/") or "/"
    if target_kind == "/":
        return unquoted == "/"
    if target_kind == "~":
        return unquoted == "~" or unquoted.startswith("~/")
    if target_kind == ".":
        return unquoted == "." or unquoted.startswith("./")
    return unquoted == ".." or unquoted.startswith("../")


def _match_recursive_rm_target(*target_codes: int):
    target_kind = R(*target_codes)

    def matcher(text: str, lower_text: str) -> str | None:
        del lower_text
        for tokens in _command_segments(text):
            for index, token in enumerate(tokens):
                if token.casefold().rsplit("/", 1)[-1] != "rm":
                    continue
                recursive = False
                force = False
                target_index = index + 1
                while target_index < len(tokens):
                    option = tokens[target_index].casefold()
                    if option == "--":
                        target_index += 1
                        break
                    if not option.startswith("-") or option == "-":
                        break
                    if option in {"--recursive", "--dir"}:
                        recursive = True
                    elif option == "--force":
                        force = True
                    elif option.startswith("-") and not option.startswith("--"):
                        flags = option[1:]
                        recursive = recursive or "r" in flags or "R" in option[1:]
                        force = force or "f" in flags
                    target_index += 1
                if (
                    recursive
                    and force
                    and target_index < len(tokens)
                    and _matches_protected_remove_target(tokens[target_index], target_kind)
                ):
                    return " ".join(tokens[index : target_index + 1])
        return None

    return matcher


def _match_rm_env(text: str, lower_text: str) -> str | None:
    commands = (R(114, 109), R(100, 101, 108), R(117, 110, 108, 105, 110, 107))
    suffix = R(46, 101, 110, 118)
    for command in commands:
        start = 0
        while True:
            index = _find_word(lower_text, command, start)
            if index == -1:
                break
            max_search_index = index + len(command) + 100 + len(suffix)
            suffix_start = index + len(command)
            while True:
                end = lower_text.find(suffix, suffix_start, max_search_index)
                if end == -1:
                    break
                after = end + len(suffix)
                if after == len(lower_text) or not _is_word_char(lower_text[after]):
                    in_between = lower_text[index + len(command) : end]
                    if not any(nl in in_between for nl in ("\n", "\\n", "\r", "\\r")):
                        return text[index : end + len(suffix)]
                suffix_start = end + 1
            start = index + 1
    return None


def _match_rm_git(text: str, lower_text: str) -> str | None:
    commands = (R(114, 109), R(100, 101, 108), R(117, 110, 108, 105, 110, 107))
    suffix = R(46, 103, 105, 116)
    for command in commands:
        start = 0
        while True:
            index = _find_word(lower_text, command, start)
            if index == -1:
                break
            max_search_index = index + len(command) + 100 + len(suffix)
            suffix_start = index + len(command)
            while True:
                end = lower_text.find(suffix, suffix_start, max_search_index)
                if end == -1:
                    break
                after = end + len(suffix)
                if after == len(lower_text) or not _is_word_char(lower_text[after]):
                    in_between = lower_text[index + len(command) : end]
                    if not any(nl in in_between for nl in ("\n", "\\n", "\r", "\\r")):
                        return text[index:after]
                suffix_start = end + 1
            start = index + 1
    return None


def _match_git_push(*prefix_codes: int):
    prefix = R(*prefix_codes)
    force_option = prefix.split()[-1]
    protected = {R(109, 97, 105, 110), R(109, 97, 115, 116, 101, 114)}

    def matcher(text: str, lower_text: str) -> str | None:
        del lower_text
        for tokens in _command_segments(text):
            folded = [token.casefold() for token in tokens]
            for index in range(len(tokens) - 1):
                if folded[index : index + 2] != ["git", "push"]:
                    continue
                tail = folded[index + 2 :]
                force_indexes = [offset for offset, token in enumerate(tail) if token == force_option]
                branch_indexes = [
                    offset for offset, token in enumerate(tail)
                    if token.lstrip("+").split(":")[-1] in protected
                ]
                forced_refspecs = [
                    offset for offset in branch_indexes if tail[offset].startswith("+")
                ]
                if force_indexes and branch_indexes:
                    end = max(force_indexes[0], branch_indexes[0]) + index + 3
                    return " ".join(tokens[index:end])
                if force_option == "--force" and forced_refspecs:
                    end = forced_refspecs[0] + index + 3
                    return " ".join(tokens[index:end])
        return None

    return matcher


def _match_delete_from(text: str, lower_text: str) -> str | None:
    del lower_text
    normalized = unicodedata.normalize("NFKC", text[:MAX_SCAN_TEXT])
    statement_pattern = re.compile(
        R(92, 98, 100, 101, 108, 101, 116, 101, 92, 115, 43, 102, 114, 111, 109, 92, 115, 43)
        + r"[^\s;]+(?P<tail>.*?)(?:;|$)",
        re.IGNORECASE | re.DOTALL,
    )
    for statement in statement_pattern.finditer(normalized):
        tail = statement.group("tail")
        if re.search(R(92, 98, 119, 104, 101, 114, 101, 92, 98), tail, re.IGNORECASE):
            continue
        return statement.group(0).strip()
    return None


def _match_pipe_chain(*codes: int):
    first, second = (R(*codes[0]), R(*codes[1]))

    def matcher(text: str, lower_text: str) -> str | None:
        index = lower_text.find(first)
        if index == -1:
            return None
        pipe = lower_text.find(R(124), index + len(first))
        if pipe == -1:
            return None
        tail = lower_text.find(second, pipe + 1)
        if tail == -1:
            return None
        return text[index : tail + len(second)]

    return matcher


def _match_data_upload(text: str, lower_text: str) -> str | None:
    curl = R(99, 117, 114, 108)
    data = R(45, 45, 100, 97, 116, 97)
    at_sign = R(64)
    index = lower_text.find(curl)
    if index == -1:
        return None
    marker = lower_text.find(data, index + len(curl))
    if marker == -1:
        return None
    end = lower_text.find(at_sign, marker + len(data))
    if end == -1:
        return None
    return text[index : end + 1]


PATTERNS = [
    ("destructive_file_ops", "critical", _match_recursive_rm_target(47), "Use targeted removals."),
    ("destructive_file_ops", "critical", _match_recursive_rm_target(126), "Use targeted removals."),
    ("destructive_file_ops", "critical", _match_recursive_rm_target(46), "Use targeted removals."),
    ("destructive_file_ops", "critical", _match_recursive_rm_target(46, 46), "Avoid recursive parent removal."),
    ("destructive_file_ops", "critical", _match_rm_env, "Back up sensitive files first."),
    ("destructive_file_ops", "critical", _match_rm_git, "Never delete repository metadata."),
    ("destructive_git_ops", "critical", _match_git_push(103, 105, 116, 32, 112, 117, 115, 104, 32, 45, 45, 102, 111, 114, 99, 101), "Use a safer push strategy."),
    ("destructive_git_ops", "critical", _match_git_push(103, 105, 116, 32, 112, 117, 115, 104, 32, 45, 102), "Use a safer push strategy."),
    ("destructive_git_ops", "high", _simple_match(103, 105, 116, 32, 114, 101, 115, 101, 116, 32, 45, 45, 104, 97, 114, 100), "Prefer a softer reset path."),
    ("destructive_git_ops", "high", _simple_match(103, 105, 116, 32, 99, 108, 101, 97, 110, 32, 45, 102, 100), "Preview deletions first."),
    ("database_destruction", "critical", _simple_match(100, 114, 111, 112, 32, 116, 97, 98, 108, 101), "Preserve the schema instead."),
    ("database_destruction", "critical", _simple_match(100, 114, 111, 112, 32, 100, 97, 116, 97, 98, 97, 115, 101), "Back up before removing."),
    ("database_destruction", "critical", _simple_match(116, 114, 117, 110, 99, 97, 116, 101), "Preserve the schema instead."),
    ("database_destruction", "high", _match_delete_from, "Add a filter clause."),
    ("permission_abuse", "high", _simple_match(99, 104, 109, 111, 100, 32, 45, 114, 32, 55, 55, 55), "Use narrower permissions."),
    ("permission_abuse", "high", _simple_match(99, 104, 109, 111, 100, 32, 55, 55, 55), "Use narrower permissions."),
    ("network_exfiltration", "critical", _match_pipe_chain((99, 117, 114, 108), (98, 97, 115, 104)), "Review downloads before execution."),
    ("network_exfiltration", "critical", _match_pipe_chain((119, 103, 101, 116), (115, 104)), "Review downloads before execution."),
    ("network_exfiltration", "high", _match_data_upload, "Review outbound data before sending."),
    ("system_danger", "high", _simple_match(115, 117, 100, 111, 32), "Use least privilege."),
    ("system_danger", "high", _simple_match(110, 112, 109, 32, 112, 117, 98, 108, 105, 115, 104), "Dry-run publication first."),
]


def _normalize_allowlist_value(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).strip().split())


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
        normalized_tool = _normalize_allowlist_value(tool).casefold()
        normalized_input = _normalize_allowlist_value(tool_input)
        if not normalized_tool or not normalized_input or len(normalized_tool) > 128 or len(normalized_input) > 8192:
            return []
        entries.append({"tool": normalized_tool, "input": normalized_input})
    return entries


def allowlist_contains(tool_name: str, tool_input: str, entries: list[dict[str, str]]) -> bool:
    normalized_tool = _normalize_allowlist_value(tool_name).casefold()
    normalized_input = _normalize_allowlist_value(tool_input)
    return any(
        entry["tool"] == normalized_tool and entry["input"] == normalized_input
        for entry in entries
    )


def read_tool_name(payload: dict) -> str:
    for key in TOOL_NAME_KEYS:
        value = payload.get(key)
        if value is not None:
            return str(value)
    return ""


def read_tool_input(payload: dict) -> str:
    for key in TOOL_INPUT_KEYS:
        if key not in payload:
            continue
        value = payload.get(key)
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return ""


def redact_excerpt(value: str) -> str:
    excerpt = unicodedata.normalize("NFKC", value[:4096])
    excerpt = re.sub(
        r"(?i)\b(https?://)([^/\s@]+)@",
        lambda match: f"{match.group(1)}{REDACTED}@",
        excerpt,
    )
    excerpt = re.sub(
        r"(?i)(//\S+\s+)[^\s@]+@",
        lambda match: f"//{REDACTED}@",
        excerpt,
    )
    excerpt = re.sub(
        r"(?i)([?&](?:access[_-]?token|api[_-]?key|token|secret|password|passwd|auth)=)[^&#\s]+",
        lambda match: f"{match.group(1)}{REDACTED}",
        excerpt,
    )
    excerpt = re.sub(
        r"(?i)\b(authorization|proxy-authorization|x-api-key|api-key|cookie|set-cookie)\s*:\s*(?:(?:bearer|basic)\s+)?[^\s,;]+",
        lambda match: f"{match.group(1)}: {REDACTED}",
        excerpt,
    )
    excerpt = re.sub(
        r"(?i)\b([A-Z0-9_]*(?:TOKEN|KEY|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH)[A-Z0-9_]*)\s*=\s*[^\s,;&]+",
        lambda match: f"{match.group(1)}={REDACTED}",
        excerpt,
    )
    excerpt = re.sub(
        r"(?i)(--(?:token|api-key|secret|password|passwd|authorization)(?:=|\s+))[^\s,;&]+",
        lambda match: f"{match.group(1)}{REDACTED}",
        excerpt,
    )
    excerpt = re.sub(
        r"(?i)\b(?:gh[pousr]_[A-Za-z0-9_]{8,}|sk-[A-Za-z0-9_-]{8,}|AKIA[A-Z0-9]{8,})\b",
        REDACTED,
        excerpt,
    )
    excerpt = " ".join(excerpt.split())
    if len(excerpt) > MAX_EXCERPT_LENGTH:
        excerpt = excerpt[: MAX_EXCERPT_LENGTH - 3] + "..."
    return excerpt


def build_threats(tool_text: str) -> list[dict[str, str]]:
    lower_tool_text = tool_text.lower()
    threats: list[dict[str, str]] = []
    for category, severity, matcher, _suggestion in PATTERNS:
        match = matcher(tool_text, lower_tool_text)
        if match:
            threats.append(
                {
                    "category": category,
                    "severity": severity,
                    "excerpt": redact_excerpt(match),
                }
            )
    return threats


def build_block_reason(tool_name: str, threats: list[dict[str, str]]) -> str:
    summary = [f"{threat['category']}/{threat['severity']} near '{threat['excerpt']}'" for threat in threats[:3]]
    joined = "; ".join(summary)
    safe_tool_name = redact_excerpt(tool_name) if tool_name else "tool invocation"
    return (
        f"Tool Guardian blocked {safe_tool_name}. {joined}. "
        "Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."
    )

# BEGIN PROVIDER ADAPTER

LOG_LOCK_TIMEOUT_SECONDS = 1.0


def format_error(error: Exception) -> str:
    return str(error)


def configure_log() -> None:
    global TIMESTAMP, LOG_FILE
    log_dir = os.environ.get("TOOL_GUARD_LOG_DIR", os.path.expanduser("~/.gemini/hooks/tool-guardian"))
    LOG_FILE = f"{log_dir}/guard.log"
    TIMESTAMP = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _open_owner_only_no_follow(path: str, flags: int) -> int:
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags | no_follow, 0o600)
    try:
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode):
            raise OSError(f"Log path is not a regular file: {path}")
        if not no_follow:
            path_details = os.stat(path, follow_symlinks=False)
            if not stat.S_ISREG(path_details.st_mode) or (
                path_details.st_dev,
                path_details.st_ino,
            ) != (details.st_dev, details.st_ino):
                raise OSError(f"Refusing linked or replaced log path: {path}")
        if hasattr(os, "fchmod"):
            os.fchmod(descriptor, 0o600)
        else:
            os.chmod(path, 0o600, follow_symlinks=False)
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _acquire_log_lock(lock_path: str) -> int:
    descriptor = _open_owner_only_no_follow(lock_path, os.O_CREAT | os.O_RDWR)
    deadline = time.monotonic() + LOG_LOCK_TIMEOUT_SECONDS
    if fcntl is not None:
        while True:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return descriptor
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    os.close(descriptor)
                    raise TimeoutError(f"Timed out waiting for Tool Guardian log lock: {lock_path}") from None
                time.sleep(0.01)
    if msvcrt is not None:
        if os.fstat(descriptor).st_size == 0:
            os.write(descriptor, b"0")
            os.fsync(descriptor)
        while True:
            try:
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                return descriptor
            except OSError:
                if time.monotonic() >= deadline:
                    os.close(descriptor)
                    raise TimeoutError(f"Timed out waiting for Tool Guardian log lock: {lock_path}") from None
                time.sleep(0.01)
    os.close(descriptor)
    raise OSError("No supported Tool Guardian log locking primitive is available")


def _release_log_lock(descriptor: int) -> None:
    try:
        if fcntl is not None:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        elif msvcrt is not None:
            os.lseek(descriptor, 0, os.SEEK_SET)
            msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
    finally:
        os.close(descriptor)


def append_log(
    log_file: str,
    event: str,
    mode: str,
    tool_name: str,
    timestamp: str,
    threat_count: int = 0,
    threats: list[dict[str, str]] | None = None,
) -> None:
    parent = os.path.dirname(log_file)
    if parent:
        os.makedirs(parent, mode=0o700, exist_ok=True)

    payload: dict[str, object] = {
        "timestamp": timestamp,
        "event": event,
        "mode": mode,
        "tool": redact_excerpt(tool_name),
    }
    if event == "threats_detected":
        payload["threat_count"] = threat_count
        payload["threats"] = threats or []

    lock_descriptor = _acquire_log_lock(f"{log_file}.lock")
    try:
        descriptor = _open_owner_only_no_follow(log_file, os.O_APPEND | os.O_CREAT | os.O_WRONLY)
        try:
            handle = os.fdopen(descriptor, "a", encoding="utf-8")
        except BaseException:
            os.close(descriptor)
            raise
        with handle:
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        _release_log_lock(lock_descriptor)


def log_payload(event: str, mode: str, tool_name: str, threat_count: int = 0, threats: list[dict[str, str]] | None = None) -> None:
    append_log(LOG_FILE, event, mode, tool_name, TIMESTAMP, threat_count, threats)
# END PROVIDER ADAPTER


def main() -> int:
    if os.environ.get("SKIP_TOOL_GUARD") == "true":
        emit_skip_allow_response()

    configure_log()
    mode = os.environ.get("GUARD_MODE", "block")
    if mode not in {"warn", "block"}:
        mode = "block"

    try:
        payload = read_json_input()
    except ValueError:
        emit_deny_response("Tool Guardian skipped: invalid hook input JSON.")
    except Exception as exc:  # noqa: BLE001 - intentional top-level fallback
        print(f"Tool Guardian failed to read input: {format_error(exc)}", file=sys.stderr)
        emit_deny_response("Tool Guardian skipped: unexpected exception.")

    if not isinstance(payload, dict):
        emit_deny_response("Tool Guardian skipped: invalid hook input JSON.")

    tool_name = read_tool_name(payload)
    tool_input = read_tool_input(payload)
    tool_text = f"{tool_name} {tool_input}"
    allowlist = parse_allowlist(os.environ.get("TOOL_GUARD_ALLOWLIST"))

    if allowlist and allowlist_contains(tool_name, tool_input, allowlist):
        log_payload("guard_skipped", mode, tool_name)
        emit_allow_response()

    threats = build_threats(tool_text)
    if not threats:
        log_payload("guard_passed", mode, tool_name)
        emit_allow_response()

    log_payload("threats_detected", mode, tool_name, len(threats), threats)
    if mode == "warn":
        emit_allow_response(f"⚠️ Tool Guardian warning: {build_block_reason(tool_name, threats)}")

    emit_deny_response(build_block_reason(tool_name, threats))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - intentional fail-closed safety net
        print(f"Tool Guardian failed unexpectedly: {format_error(exc)}", file=sys.stderr)
        emit_deny_response("Tool Guardian blocked execution due to an internal error.")

#!/usr/bin/env python3
# Generated from hooks/families/tool_guard.py by scripts/generate-hooks.py. Do not edit.

from __future__ import annotations

# BEGIN PROVIDER ADAPTER
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_log_event  # noqa: E402
from helpers.common import emit_json, read_json_input  # noqa: E402


SCRIPT_NAME = Path(__file__).name
TOOL_NAME_KEYS = ("toolName", "tool_name")
TOOL_INPUT_KEYS = ("toolArgs", "toolInput", "tool_input")
TOOL_PROVIDER = "copilot"


def emit_skip_allow_response() -> None:
    emit_json(
        {
            "continue": True,
            "permissionDecision": "allow",
            "hookSpecificOutput": {"permissionDecision": "allow"},
        }
    )
    raise SystemExit(0)


def emit_allow_response(system_message: str | None = None) -> None:
    payload = {
        "continue": True,
        "permissionDecision": "allow",
        "hookSpecificOutput": {"permissionDecision": "allow"},
    }
    if system_message:
        payload["systemMessage"] = system_message
    emit_json(payload)
    raise SystemExit(0)


def emit_deny_response(reason: str) -> None:
    emit_json(
        {
            "continue": True,
            "permissionDecision": "deny",
            "hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": reason},
            "permissionDecisionReason": reason,
        }
    )
    raise SystemExit(0)
# END PROVIDER ADAPTER


import re
import shlex
import unicodedata


MAX_SCAN_TEXT = 32768
MAX_NATIVE_DATA_BYTES = 65536
MAX_COMMAND_SEGMENTS = 128
MAX_COMMAND_TOKENS = 256
MAX_STRUCTURED_DEPTH = 32
MAX_STRUCTURED_NODES = 256
MAX_STRUCTURED_STRINGS = 128
MAX_TOOL_NAME_LENGTH = 160
MAX_EXCERPT_LENGTH = 160
REDACTED = "[REDACTED]"
KNOWN_TOOL_FIELDS = {
    "write_file": frozenset({"content"}),
    "run_shell_command": frozenset({"command"}),
    "bash": frozenset({"command"}),
    "apply_patch": frozenset({"command"}),
}


class ScanLimitExceeded(ValueError):
    def __init__(self, rule_id: str, limit: int, measured: int, unit: str, field: str = "tool input") -> None:
        self.rule_id = rule_id
        self.limit = limit
        self.measured = measured
        self.unit = unit
        self.field = field
        super().__init__(rule_id)

    def threat(self) -> dict[str, str]:
        cause = f"{self.field}: {self.measured} {self.unit} exceeds limit {self.limit} {self.unit}"
        return {
            "category": "input_limits",
            "severity": "critical",
            "rule_id": self.rule_id,
            "cause": cause,
        }

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


def _bounded_normalized_text(text: str) -> str:
    if len(text) > MAX_SCAN_TEXT:
        raise ScanLimitExceeded("scan_text_characters", MAX_SCAN_TEXT, len(text), "characters")
    text_bytes = len(text.encode("utf-8"))
    if text_bytes > MAX_SCAN_TEXT:
        raise ScanLimitExceeded("scan_text_bytes", MAX_SCAN_TEXT, text_bytes, "bytes")
    normalized = unicodedata.normalize("NFKC", text)
    if len(normalized) > MAX_SCAN_TEXT:
        raise ScanLimitExceeded("normalized_scan_text_characters", MAX_SCAN_TEXT, len(normalized), "characters")
    normalized_bytes = len(normalized.encode("utf-8"))
    if normalized_bytes > MAX_SCAN_TEXT:
        raise ScanLimitExceeded("normalized_scan_text_bytes", MAX_SCAN_TEXT, normalized_bytes, "bytes")
    return normalized


def _command_segments(text: str) -> list[list[str]]:
    normalized = _bounded_normalized_text(text)
    raw_segments = re.split(
        r"(?:\r?\n|\\[nr]|&&|\|\||;)",
        normalized,
        maxsplit=MAX_COMMAND_SEGMENTS,
    )
    if len(raw_segments) > MAX_COMMAND_SEGMENTS:
        raise ScanLimitExceeded("command_segments", MAX_COMMAND_SEGMENTS, len(raw_segments), "segments")
    segments: list[list[str]] = []
    for raw_segment in raw_segments:
        token_source = re.sub(r'[",]', " ", raw_segment)
        try:
            tokens = shlex.split(token_source, comments=False, posix=True)
        except ValueError:
            tokens = token_source.split()
        if len(tokens) > MAX_COMMAND_TOKENS:
            raise ScanLimitExceeded("command_tokens", MAX_COMMAND_TOKENS, len(tokens), "tokens")
        if tokens:
            segments.append(tokens)
    return segments


def _executable_basename(token: str) -> str:
    basename = token.replace("\\", "/").rsplit("/", 1)[-1].casefold()
    for suffix in (".exe", ".cmd", ".bat"):
        if basename.endswith(suffix):
            return basename[: -len(suffix)]
    return basename


def _matches_protected_remove_target(target: str, target_kind: str) -> bool:
    unquoted = target.rstrip("/\\") or "/"
    if target_kind == "/":
        return unquoted == "/"
    if target_kind == "~":
        folded = unquoted.casefold()
        home_prefixes = (
            "~",
            "$home",
            "${home}",
            "$userprofile",
            "${userprofile}",
            "$env:home",
            "${env:home}",
            "$env:userprofile",
            "${env:userprofile}",
            "%userprofile%",
            "%homepath%",
            "%homedrive%%homepath%",
        )
        return any(
            folded == prefix or folded.startswith((f"{prefix}/", f"{prefix}\\"))
            for prefix in home_prefixes
        )
    if target_kind == ".":
        return unquoted == "." or unquoted.startswith("./")
    return unquoted == ".." or unquoted.startswith("../")


def _match_recursive_rm_target(*target_codes: int):
    target_kind = R(*target_codes)

    def matcher(text: str, lower_text: str) -> str | None:
        del lower_text
        for tokens in _command_segments(text):
            for index, token in enumerate(tokens):
                if _executable_basename(token) != "rm":
                    continue
                recursive = False
                force = False
                operands: list[tuple[int, str]] = []
                options_done = False
                for target_index in range(index + 1, len(tokens)):
                    option = tokens[target_index].casefold()
                    if option == "--":
                        options_done = True
                    elif not options_done and option in {"--recursive", "--dir"}:
                        recursive = True
                    elif not options_done and option == "--force":
                        force = True
                    elif not options_done and option.startswith("-") and not option.startswith("--"):
                        flags = option[1:]
                        recursive = recursive or "r" in flags or "R" in option[1:]
                        force = force or "f" in flags
                    else:
                        operands.append((target_index, tokens[target_index]))
                if recursive and force:
                    for target_index, operand in operands:
                        if _matches_protected_remove_target(operand, target_kind):
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

    options_with_values = {
        "-C",
        "-c",
        "--config-env",
        "--exec-path",
        "--git-dir",
        "--namespace",
        "--super-prefix",
        "--work-tree",
    }
    options_without_values = {
        "--bare",
        "--glob-pathspecs",
        "--html-path",
        "--icase-pathspecs",
        "--info-path",
        "--literal-pathspecs",
        "--man-path",
        "--no-advice",
        "--no-optional-locks",
        "--no-pager",
        "--no-replace-objects",
        "--noglob-pathspecs",
        "--paginate",
        "-P",
        "-p",
    }

    def push_index(tokens: list[str], git_index: int) -> int | None:
        index = git_index + 1
        while index < len(tokens):
            token = tokens[index]
            if token.casefold() == "push":
                return index
            if token in options_with_values:
                if index + 1 >= len(tokens):
                    return None
                index += 2
                continue
            if (
                (token.startswith("-C") and token != "-C")
                or (token.startswith("-c") and token != "-c")
                or any(token.startswith(f"{option}=") for option in options_with_values if option.startswith("--"))
            ):
                index += 1
                continue
            if token in options_without_values:
                index += 1
                continue
            return None
        return None

    def matcher(text: str, lower_text: str) -> str | None:
        del lower_text
        for tokens in _command_segments(text):
            folded = [token.casefold() for token in tokens]
            for index in range(len(tokens)):
                if _executable_basename(tokens[index]) != "git":
                    continue
                command_index = push_index(tokens, index)
                if command_index is None:
                    continue
                tail = folded[command_index + 1 :]
                force_indexes = [offset for offset, token in enumerate(tail) if token == force_option]
                branch_indexes = [
                    offset for offset, token in enumerate(tail)
                    if token.lstrip("+").split(":")[-1].removeprefix("refs/heads/") in protected
                ]
                forced_refspecs = [
                    offset for offset in branch_indexes if tail[offset].startswith("+")
                ]
                if force_indexes and branch_indexes:
                    end = max(force_indexes[0], branch_indexes[0]) + command_index + 2
                    return " ".join(tokens[index:end])
                if force_option == "--force" and forced_refspecs:
                    end = forced_refspecs[0] + command_index + 2
                    return " ".join(tokens[index:end])
        return None

    return matcher


def _sql_code_without_comments_or_literals(text: str) -> str:
    output: list[str] = []
    index = 0
    state = "code"
    while index < len(text):
        character = text[index]
        next_character = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if character == "-" and next_character == "-":
                output.extend((" ", " "))
                index += 2
                state = "line_comment"
                continue
            if character == "#":
                output.append(" ")
                index += 1
                state = "line_comment"
                continue
            if character == "/" and next_character == "*":
                output.extend((" ", " "))
                index += 2
                state = "block_comment"
                continue
            if character in {"'", '"', "`"}:
                output.append("_")
                state = character
            else:
                output.append(character)
        elif state == "line_comment":
            output.append(character if character in "\r\n" else " ")
            if character in "\r\n":
                state = "code"
        elif state == "block_comment":
            if character == "*" and next_character == "/":
                output.extend((" ", " "))
                index += 2
                state = "code"
                continue
            output.append(character if character in "\r\n" else " ")
        else:
            output.append("_")
            if character == state:
                if next_character == state:
                    output.append("_")
                    index += 2
                    continue
                state = "code"
        index += 1
    return "".join(output)


def _match_delete_from(text: str, lower_text: str) -> str | None:
    del lower_text
    normalized = _sql_code_without_comments_or_literals(_bounded_normalized_text(text))
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

RULE_DETAILS = (
    ("recursive_remove_root", "recursive forced removal targets the filesystem root"),
    ("recursive_remove_home", "recursive forced removal targets the home directory"),
    ("recursive_remove_current", "recursive forced removal targets the current directory"),
    ("recursive_remove_parent", "recursive forced removal targets a parent directory"),
    ("remove_env_file", "removal targets an environment file"),
    ("remove_git_metadata", "removal targets Git metadata"),
    ("force_push_protected_branch", "forced push targets a protected branch"),
    ("force_push_protected_branch", "forced push targets a protected branch"),
    ("hard_reset", "hard reset can discard local work"),
    ("forced_git_clean", "forced Git clean can delete untracked work"),
    ("drop_table", "SQL drops a table"),
    ("drop_database", "SQL drops a database"),
    ("truncate_table", "SQL truncates a table"),
    ("delete_without_where", "SQL DELETE has no WHERE clause"),
    ("recursive_world_writable", "recursive permissions grant write access to everyone"),
    ("world_writable", "permissions grant write access to everyone"),
    ("download_execute_bash", "download output is piped to bash"),
    ("download_execute_sh", "download output is piped to sh"),
    ("upload_local_data", "curl uploads local data"),
    ("privileged_command", "command requests elevated privileges"),
    ("publish_package", "command publishes a package"),
)


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


def read_tool_name(payload: dict) -> str:
    for key in TOOL_NAME_KEYS:
        value = payload.get(key)
        if value is not None:
            return str(value)
    return ""


def _read_tool_input_value(payload: dict) -> object:
    for key in TOOL_INPUT_KEYS:
        if key not in payload:
            continue
        value = payload.get(key)
        if value is None:
            return ""
        return value
    return ""


def read_tool_input(payload: dict) -> str:
    value = _read_tool_input_value(payload)
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class NativeToolInput:
    """Validated native arguments, with file operations separate from inert data."""
    def __init__(self, kind: str, metadata: tuple[str, ...], data: tuple[str, ...], operations: tuple[tuple[str, str], ...] = ()) -> None:
        self.kind = kind
        self.metadata = metadata
        self.data = data
        self.operations = operations


def _matches_native_schema(value: dict, required: dict[str, type], optional: dict[str, type] | None = None) -> bool:
    fields = {**required, **(optional or {})}
    return required.keys() <= value.keys() <= fields.keys() and all(type(child) is fields[key] for key, child in value.items())


def _native_tool_shape(tool_name: str, value: object) -> NativeToolInput | None:
    if not isinstance(value, dict):
        return None
    if TOOL_PROVIDER == "codex" and tool_name == "apply_patch" and _matches_native_schema(value, {"command": str}):
        return NativeToolInput("patch", (), (value["command"],))
    if TOOL_PROVIDER == "gemini":
        if tool_name == "write_file" and _matches_native_schema(value, {"file_path": str, "content": str}):
            return NativeToolInput("write", (value["file_path"],), (value["content"],))
        if tool_name == "replace" and _matches_native_schema(value, {"file_path": str, "instruction": str, "old_string": str, "new_string": str}, {"allow_multiple": bool}):
            return NativeToolInput("edit", (value["file_path"], value["instruction"]), (value["old_string"], value["new_string"]))
        if tool_name == "grep_search" and _matches_native_schema(value, {"pattern": str}, {"path": str, "include": str}):
            return NativeToolInput("search", tuple(value.get(key, "") for key in ("path", "include")), (value["pattern"],))
    if TOOL_PROVIDER == "copilot":
        if tool_name == "create" and _matches_native_schema(value, {"path": str, "file_text": str}):
            return NativeToolInput("write", (value["path"],), (value["file_text"],))
        if tool_name == "edit" and _matches_native_schema(value, {"path": str, "old_str": str, "new_str": str}):
            return NativeToolInput("edit", (value["path"],), (value["old_str"], value["new_str"]))
        if tool_name in {"grep", "rg"}:
            # Observed CLI arguments, not a guessed complete provider schema.
            pattern_keys = value.keys() & {"pattern", "query"}
            if len(pattern_keys) != 1 or (tool_name == "rg" and "query" in value):
                return None
            pattern_key = next(iter(pattern_keys))
            fields = {"path": str, "paths": (str, list), "output_mode": str, "head_limit": int,
                      "n": (bool, int), "C": int, "case_sensitive": bool} if tool_name == "grep" else {
                          "paths": (str, list), "output_mode": str, "head_limit": int, "glob": str,
                          "-n": bool, "-i": bool, "-A": int, "-C": int, "n": int}
            if not value.keys() <= fields.keys() | {pattern_key} or type(value[pattern_key]) is not str:
                return None
            if "path" in value and "paths" in value:
                return None
            for key, child in value.items():
                if key == pattern_key:
                    continue
                allowed_types = fields[key] if isinstance(fields[key], tuple) else (fields[key],)
                if type(child) not in allowed_types or (type(child) is list and any(type(item) is not str for item in child)):
                    return None
            return NativeToolInput("search", (), tuple(child for child in value.values() if isinstance(child, str)))
    return None


def _parse_native_patch(patch: str) -> NativeToolInput | None:
    lines = patch.splitlines()
    if len(lines) < 3 or lines[0] != "*** Begin Patch" or lines[-1] != "*** End Patch":
        return None
    operations: list[tuple[str, str]] = []
    metadata: list[str] = []
    kind = ""
    body_seen = False
    moved = False
    for line in lines[1:-1]:
        header = next((prefix for prefix in ("*** Add File: ", "*** Update File: ", "*** Delete File: ") if line.startswith(prefix)), None)
        if header:
            if kind in {"add", "update"} and not body_seen:
                return None
            path = line[len(header):]
            if not path or "\x00" in path:
                return None
            kind = {"*** Add File: ": "add", "*** Update File: ": "update", "*** Delete File: ": "delete"}[header]
            metadata.append(path)
            if kind == "delete":
                operations.append(("delete", path))
            body_seen = moved = False
        elif line.startswith("*** Move to: "):
            if kind != "update" or body_seen or moved:
                return None
            destination = line[len("*** Move to: "):]
            if not destination or "\x00" in destination:
                return None
            operations.append(("move", metadata[-1]))
            metadata.append(destination)
            moved = True
        elif kind == "add" and line.startswith("+"):
            body_seen = True
        elif kind == "update" and (line.startswith((" ", "+", "-", "@@ ")) or line in {"@@", "*** End of File"}):
            body_seen = True
        else:
            return None
    if not kind or (kind in {"add", "update"} and not body_seen):
        return None
    return NativeToolInput("patch", tuple(metadata), (patch,), tuple(operations))


def _native_operation_threats(native: NativeToolInput) -> list[dict[str, str]]:
    threats: list[dict[str, str]] = []
    seen: set[str] = set()
    for operation, path in native.operations:
        # Move removes its source. Apply the existing environment/Git removal
        # rules to that operation without treating a filename as shell code.
        normalized = unicodedata.normalize("NFKC", path).casefold().replace("\\", "/")
        for suffix, rule_id, cause in ((".env", "remove_env_file", "removal targets an environment file"),
                                     (".git", "remove_git_metadata", "removal targets Git metadata")):
            start = 0
            protected = False
            while (index := normalized.find(suffix, start)) != -1:
                after = index + len(suffix)
                if after == len(normalized) or not _is_word_char(normalized[after]):
                    protected = True
                    break
                start = after
            if protected and rule_id not in seen:
                seen.add(rule_id)
                threats.append({"category": "destructive_file_ops", "severity": "critical", "rule_id": rule_id,
                                "cause": cause, "matched": f"patch {operation} {suffix}"})
    return threats


def read_tool_scan_inputs(payload: dict) -> tuple[str, ...] | NativeToolInput:
    value = _read_tool_input_value(payload)
    if isinstance(value, str):
        return (value,)

    tool_name = read_tool_name(payload)
    native = _native_tool_shape(tool_name, value)
    byte_limit = MAX_NATIVE_DATA_BYTES if native else MAX_SCAN_TEXT
    known_fields = KNOWN_TOOL_FIELDS.get(tool_name.casefold(), frozenset())
    stack: list[tuple[object, int, str]] = [(value, 0, "tool input")]
    strings: list[str] = []
    node_count = 0
    total_string_bytes = 0
    keys: list[str] = []
    while stack:
        current, depth, field = stack.pop()
        node_count += 1
        if node_count > MAX_STRUCTURED_NODES:
            raise ScanLimitExceeded("structured_nodes", MAX_STRUCTURED_NODES, node_count, "nodes")
        if depth > MAX_STRUCTURED_DEPTH:
            raise ScanLimitExceeded("structured_depth", MAX_STRUCTURED_DEPTH, depth, "levels")
        if isinstance(current, str):
            strings.append(current)
            current_bytes = len(current.encode("utf-8"))
            total_string_bytes += current_bytes
            if len(strings) > MAX_STRUCTURED_STRINGS:
                raise ScanLimitExceeded("structured_strings", MAX_STRUCTURED_STRINGS, len(strings), "strings")
            if total_string_bytes > byte_limit:
                source = field if current_bytes > byte_limit else "tool input"
                raise ScanLimitExceeded("structured_bytes", byte_limit, total_string_bytes, "bytes", source)
        elif isinstance(current, dict):
            keys.extend(current)
            stack.extend(
                (child, depth + 1, f"{tool_name.casefold()}.{key}" if depth == 0 and key in known_fields and isinstance(child, str) else "tool input")
                for key, child in reversed(tuple(current.items()))
            )
        elif isinstance(current, (list, tuple)):
            stack.extend((child, depth + 1, "tool input") for child in reversed(current))

    key_bytes = sum(len(key.encode("utf-8")) for key in keys)
    if native:
        aggregate_bytes = total_string_bytes + key_bytes
        if aggregate_bytes > byte_limit:
            raise ScanLimitExceeded("structured_bytes", byte_limit, aggregate_bytes, "bytes")
        if native.kind == "patch":
            native = _parse_native_patch(native.data[0])
        if native is not None:
            return native
        if total_string_bytes > MAX_SCAN_TEXT:
            raise ScanLimitExceeded("structured_bytes", MAX_SCAN_TEXT, total_string_bytes, "bytes")
    elif key_bytes > MAX_SCAN_TEXT:
        raise ScanLimitExceeded("structured_bytes", MAX_SCAN_TEXT, key_bytes, "bytes")
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return tuple(strings) + tuple(keys) + (serialized,)


def sanitize_tool_name(value: str) -> str:
    sanitized = unicodedata.normalize("NFKC", value[:4096])
    sanitized = re.sub(
        r"(?i)\b(https?://)([^/\s@]+)@",
        lambda match: f"{match.group(1)}{REDACTED}@",
        sanitized,
    )
    sanitized = re.sub(
        r"(?i)(//\S+\s+)[^\s@]+@",
        lambda match: f"//{REDACTED}@",
        sanitized,
    )
    sanitized = re.sub(
        r"(?i)([?&](?:access[_-]?token|api[_-]?key|token|secret|password|passwd|auth)=)[^&#\s]+",
        lambda match: f"{match.group(1)}{REDACTED}",
        sanitized,
    )
    sanitized = re.sub(
        r"(?i)\b(authorization|proxy-authorization|x-api-key|api-key|cookie|set-cookie)\s*:\s*(?:(?:bearer|basic)\s+)?[^\s,;]+",
        lambda match: f"{match.group(1)}: {REDACTED}",
        sanitized,
    )
    sanitized = re.sub(
        r"(?i)\b([A-Z0-9_]*(?:TOKEN|KEY|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH)[A-Z0-9_]*)\s*=\s*[^\s,;&]+",
        lambda match: f"{match.group(1)}={REDACTED}",
        sanitized,
    )
    sanitized = re.sub(
        r"(?i)(--(?:token|api-key|secret|password|passwd|authorization)(?:=|\s+))[^\s,;&]+",
        lambda match: f"{match.group(1)}{REDACTED}",
        sanitized,
    )
    sanitized = re.sub(
        r"(?i)\b(?:gh[pousr]_[A-Za-z0-9_]{8,}|sk-[A-Za-z0-9_-]{8,}|AKIA[A-Z0-9]{8,})\b",
        REDACTED,
        sanitized,
    )
    sanitized = " ".join(sanitized.split())
    if len(sanitized) > MAX_TOOL_NAME_LENGTH:
        sanitized = sanitized[: MAX_TOOL_NAME_LENGTH - 3] + "..."
    return sanitized


def build_threats(tool_text: str) -> list[dict[str, str]]:
    try:
        _command_segments(tool_text)
    except ScanLimitExceeded as limit:
        return [limit.threat()]
    lower_tool_text = tool_text.lower()
    threats: list[dict[str, str]] = []
    for (category, severity, matcher, _suggestion), (rule_id, cause) in zip(PATTERNS, RULE_DETAILS, strict=True):
        match = matcher(tool_text, lower_tool_text)
        if match:
            threats.append(
                {
                    "category": category,
                    "severity": severity,
                    "rule_id": rule_id,
                    "cause": cause,
                    "matched": match,
                }
            )
    return threats


def build_input_threats(tool_name: str, tool_inputs: tuple[str, ...] | NativeToolInput) -> list[dict[str, str]]:
    if isinstance(tool_inputs, NativeToolInput):
        return _native_operation_threats(tool_inputs)
    threats: list[dict[str, str]] = []
    seen: set[str] = set()
    for tool_input in tool_inputs:
        for threat in build_threats(f"{tool_name} {tool_input}"):
            identity = threat["rule_id"]
            if identity not in seen:
                seen.add(identity)
                threats.append(threat)
    return threats


def sanitize_excerpt(value: str) -> str:
    normalized = " ".join(unicodedata.normalize("NFKC", value[:4096]).split())
    normalized = re.sub(r"(?i)\b(https?://)[^/\s@]+@", r"\1[REDACTED]@", normalized)
    normalized = re.sub(
        r'(?i)("[A-Z0-9_-]*(?:TOKEN|KEY|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH)[A-Z0-9_-]*"\s*:\s*)"(?:\\.|[^"\\])*(?:"|$)',
        r'\1"[REDACTED]"', normalized,
    )
    credential_value = r""""(?:\\.|[^"\\])*(?:"|$)|'(?:\\.|[^'\\])*(?:'|$)|[^\s,;&]+"""
    normalized = re.sub(
        r"(?i)(--(?:token|api-key|secret|password|passwd|authorization)(?:=|\s+))(?:" + credential_value + ")",
        r"\1[REDACTED]", normalized,
    )
    normalized = re.sub(
        r"(?i)\b([A-Z0-9_]*(?:TOKEN|KEY|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH)[A-Z0-9_]*)\s*=\s*(?:" + credential_value + ")",
        r"\1=[REDACTED]", normalized,
    )
    normalized = re.sub(r"(?i)\b(authorization|proxy-authorization|x-api-key|api-key|cookie|set-cookie)\s*:\s*(?:(?:bearer|basic)\s+)?[^\s,;]+", r"\1: [REDACTED]", normalized)
    normalized = re.sub(r"(?i)\b(?:gh[pousr]_[A-Za-z0-9_]{8,}|github_pat_[A-Za-z0-9_]{8,}|sk[-_](?:live_)?[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9-]{8,}|AKIA[A-Z0-9]{8,})\b", REDACTED, normalized)
    normalized = re.sub(r"(?<![A-Za-z0-9])(?=[A-Za-z0-9_/-]{24,}(?![A-Za-z0-9_/-]))(?=[A-Za-z0-9_/-]*[A-Za-z])(?=[A-Za-z0-9_/-]*[0-9])[A-Za-z0-9_/-]+", REDACTED, normalized)
    return normalized


def safe_excerpt_context(tool_input: str, matched: str) -> str:
    """Keep context only when every part outside the match is known safe."""
    normalized = " ".join(unicodedata.normalize("NFKC", tool_input[:4096]).split())
    if matched not in normalized:
        return ""
    context = sanitize_excerpt(tool_input)
    if matched.casefold() == "drop" + " table" and re.fullmatch(
        r'(?i)\{"command":"DROP' + r' TABLE [A-Z_][A-Z0-9_]*;"\}', context
    ):
        return context
    remainder = context.replace(sanitize_excerpt(matched), "", 1)
    remainder = re.sub(
        r'(?i)(?:"(?:[A-Z0-9_-]*(?:TOKEN|KEY|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH)[A-Z0-9_-]*)"\s*:\s*"\[REDACTED\]"|'
        r'(?:--(?:token|api-key|secret|password|passwd|authorization)(?:=|\s+)|'
        r'[A-Z0-9_]*(?:TOKEN|KEY|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH)[A-Z0-9_]*\s*=)\[REDACTED\])',
        "",
        remainder,
    )
    remainder = re.sub(r'(?i)"command"\s*:', "", remainder)
    remainder = re.sub(r'([A-Za-z])\1{31,}', "", remainder)
    if re.fullmatch(r'[\s,;:{}"\']*', remainder):
        return context
    return ""


def safe_git_push_match(matched: str) -> str:
    """Describe a protected push using only known flags, remotes, and branches."""
    tokens = matched.split()
    try:
        push_index = next(index for index, token in enumerate(tokens) if token.casefold() == "push")
    except StopIteration:
        return " ".join(("git", "push"))
    tail = tokens[push_index + 1 :]
    folded = [token.casefold() for token in tail]
    force = "--force" if "--force" in folded else "-f" if "-f" in folded else ""
    remote = next((token for token in folded if token in {"origin", "upstream"}), "")
    branch = ""
    for token in folded:
        destination = token.lstrip("+").split(":")[-1].removeprefix("refs/heads/")
        if destination in {"main", "master"}:
            branch = ("+" if token.startswith("+") and not force else "") + destination
            break
    summary = ["git", "push"]
    if force:
        summary.append(force)
    if remote:
        summary.append(remote)
    if branch:
        summary.append(branch)
    return " ".join(summary)


def build_action_excerpt(tool_input: str, threats: list[dict[str, str]]) -> str:
    matched_threat = next((threat for threat in threats if threat.get("matched")), None)
    if not matched_threat:
        return "command omitted"
    try:
        matched = matched_threat["matched"]
        safe_match = sanitize_excerpt(matched)
        if matched_threat["category"] == "destructive_git_ops" and "push" in matched.casefold().split():
            safe_match = safe_git_push_match(matched)
        elif matched_threat["category"] == "network_exfiltration":
            folded = matched.casefold()
            if "curl" in folded and "bash" in folded and chr(124) in matched:
                safe_match = "curl " + chr(124) + " bash"
            elif "wget" in folded and "sh" in folded and chr(124) in matched:
                safe_match = "wget " + chr(124) + " sh"
            elif "curl" in folded and "--" + "data" in folded:
                safe_match = "curl --" + "data " + chr(64)
        elif re.search(r"\b[A-Za-z][A-Za-z0-9_-]*:\s+\S", matched):
            return "command omitted"
        safe_context = (
            "" if matched_threat["category"] == "network_exfiltration" or safe_match != sanitize_excerpt(matched)
            else safe_excerpt_context(tool_input, matched)
        )
        if not safe_match or "\n" in safe_match or "\r" in safe_match:
            return "command omitted"
        excerpt = safe_match if not safe_context or safe_context == safe_match else f"{safe_match}; {safe_context}"
        return excerpt[:MAX_EXCERPT_LENGTH]
    except (TypeError, ValueError, UnicodeError):
        return "command omitted"


def log_threat_metadata(threats: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {key: threat[key] for key in ("category", "severity", "rule_id", "cause") if key in threat}
        for threat in threats
    ]


def build_block_reason(tool_name: str, threats: list[dict[str, str]], excerpt: str, mode: str) -> str:
    summary = [
        f"{threat['category']}/{threat['severity']} [{threat['rule_id']}]: {threat['cause']}"
        if "rule_id" in threat else f"{threat['category']}/{threat['severity']}"
        for threat in threats[:3]
    ]
    joined = "; ".join(summary)
    omitted = max(0, len(threats) - 3)
    if omitted:
        joined += f"; {omitted} more finding{'s' if omitted != 1 else ''} omitted"
    safe_tool_name = sanitize_tool_name(tool_name) if tool_name else "tool invocation"
    message = f"Tool Guardian {mode} {safe_tool_name}. {joined}. Action: {excerpt}."
    if not any(threat["category"] in {"input_limits", "inspection_failure"} for threat in threats):
        message += " Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional."
    return message

# BEGIN PROVIDER ADAPTER

def format_error(error: Exception) -> str:
    return type(error).__name__


def configure_log() -> None:
    global TIMESTAMP, LOG_FILE, LOCK_FILE
    TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    LOG_FILE = os.environ.get(
        "TOOL_GUARD_LOG_DIR",
        str(Path.home() / ".copilot" / "hooks" / "tool-guardian" / "guard.log"),
    )
    LOCK_FILE = f"{LOG_FILE}.lock"


def log_payload(event: str, mode: str, tool_name: str, threat_count: int = 0, threats: list[dict[str, str]] | None = None, excerpt: str | None = None) -> None:
    payload: dict[str, object] = {
        "timestamp": TIMESTAMP,
        "event": event,
        "mode": mode,
        "tool": sanitize_tool_name(tool_name),
    }
    if event == "threats_detected":
        payload["threat_count"] = threat_count
        payload["threats"] = threats or []
        payload["excerpt"] = excerpt or "command omitted"

    old_audit_log = os.environ.get("AUDIT_LOG")
    old_audit_lock = os.environ.get("AUDIT_LOCK")
    try:
        os.environ["AUDIT_LOG"] = LOG_FILE
        os.environ["AUDIT_LOCK"] = LOCK_FILE
        audit_log_event(SCRIPT_NAME, json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    finally:
        if old_audit_log is None:
            os.environ.pop("AUDIT_LOG", None)
        else:
            os.environ["AUDIT_LOG"] = old_audit_log
        if old_audit_lock is None:
            os.environ.pop("AUDIT_LOCK", None)
        else:
            os.environ["AUDIT_LOCK"] = old_audit_lock
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
    try:
        tool_scan_inputs = read_tool_scan_inputs(payload)
        threats = build_input_threats(tool_name, tool_scan_inputs)
    except ScanLimitExceeded as limit:
        threats = [limit.threat()]
    except UnicodeError:
        threats = [{"category": "inspection_failure", "severity": "critical", "rule_id": "inspection_failure", "cause": "tool input cannot be encoded as UTF-8 for inspection"}]
    if any(threat["category"] in {"input_limits", "inspection_failure"} for threat in threats):
        excerpt = "command omitted"
        log_payload("threats_detected", mode, tool_name, len(threats), log_threat_metadata(threats), excerpt)
        emit_deny_response(build_block_reason(tool_name, threats, excerpt, "blocked"))

    tool_input = read_tool_input(payload)
    allowlist = parse_allowlist(os.environ.get("TOOL_GUARD_ALLOWLIST"))

    if allowlist and allowlist_contains(tool_name, tool_input, allowlist):
        log_payload("guard_skipped", mode, tool_name)
        emit_allow_response()

    if not threats:
        log_payload("guard_passed", mode, tool_name)
        emit_allow_response()

    excerpt = build_action_excerpt(tool_input, threats)
    log_payload("threats_detected", mode, tool_name, len(threats), log_threat_metadata(threats), excerpt)
    if mode == "warn":
        emit_allow_response(build_block_reason(tool_name, threats, excerpt, "warning"))

    emit_deny_response(build_block_reason(tool_name, threats, excerpt, "blocked"))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - intentional fail-closed safety net
        print(f"Tool Guardian failed unexpectedly: {format_error(exc)}", file=sys.stderr)
        emit_deny_response("Tool Guardian blocked execution due to an internal error.")

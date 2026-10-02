"""Render Tool Guardian from one policy and explicit provider adapters."""

from __future__ import annotations

from hooks.families.allowlist import ALLOWLIST_SOURCE
from hooks.manifest import GeneratedTarget
from hooks.providers import Provider


SHEBANG = "#!/usr/bin/env python3\n"
HEADER = "# Generated from hooks/families/tool_guard.py by scripts/generate-hooks.py. Do not edit.\n"
ADAPTER_START = "# BEGIN PROVIDER ADAPTER\n"
ADAPTER_END = "# END PROVIDER ADAPTER\n"


_COPILOT_IMPORT_AND_RESPONSE_ADAPTER = r'''import json
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
'''


_GEMINI_IMPORT_AND_RESPONSE_ADAPTER = r'''import json
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
TOOL_PROVIDER = "gemini"


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
    emit_json({"decision": "deny", "reason": reason})
    raise SystemExit(0)
'''


_CODEX_IMPORT_AND_RESPONSE_ADAPTER = r'''import json
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
TOOL_NAME_KEYS = ("tool_name", "toolName")
TOOL_INPUT_KEYS = ("tool_input", "toolInput", "toolArgs")
TOOL_PROVIDER = "codex"


def emit_skip_allow_response() -> None:
    emit_json({})
    raise SystemExit(0)


def emit_allow_response(system_message: str | None = None) -> None:
    emit_json({"systemMessage": system_message} if system_message else {})
    raise SystemExit(0)


def emit_deny_response(reason: str) -> None:
    emit_json({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }})
    raise SystemExit(0)
'''


_POLICY_SOURCE = r'''

import re
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
    if isinstance(text, _ScanText):
        return text.segments
    import shlex
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


class _ScanText(str):
    def __new__(cls, text: str, segments: list[list[str]]):
        value = str.__new__(cls, text)
        value.segments = segments
        return value


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
            recursive = force = False
            protected_index = None
            summaries = [(False, False, None)] * (len(tokens) + 1)
            for offset in range(len(tokens) - 1, -1, -1):
                option = tokens[offset].casefold()
                if _matches_protected_remove_target(tokens[offset], target_kind):
                    protected_index = offset
                if option == "--":
                    recursive = force = False
                elif option in {"--recursive", "--dir"}:
                    recursive = True
                elif option == "--force":
                    force = True
                elif option.startswith("-") and not option.startswith("--"):
                    recursive = recursive or "r" in option[1:]
                    force = force or "f" in option[1:]
                summaries[offset] = (recursive, force, protected_index)
            for index, token in enumerate(tokens):
                if _executable_basename(token) == "rm":
                    recursive, force, target_index = summaries[index + 1]
                    if recursive and force and target_index is not None:
                        return " ".join(tokens[index:target_index + 1])
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
            suffix = [(None, None, None)] * (len(tokens) + 1)
            force_index = branch_index = forced_index = None
            for offset in range(len(tokens) - 1, -1, -1):
                token = folded[offset]
                if token == force_option:
                    force_index = offset
                if token.lstrip("+").split(":")[-1].removeprefix("refs/heads/") in protected:
                    branch_index = offset
                    if token.startswith("+"):
                        forced_index = offset
                suffix[offset] = (force_index, branch_index, forced_index)
            for index in range(len(tokens)):
                if _executable_basename(tokens[index]) != "git":
                    continue
                command_index = push_index(tokens, index)
                if command_index is None:
                    continue
                force_index, branch_index, forced_index = suffix[command_index + 1]
                if force_index is not None and branch_index is not None:
                    return " ".join(tokens[index:max(force_index, branch_index) + 1])
                if force_option == "--force" and forced_index is not None:
                    return " ".join(tokens[index:forced_index + 1])
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
    if _find_word(lower_text, R(100, 101, 108, 101, 116, 101)) == -1:
        return None
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

    matcher.pipe_names = (first, second)
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


# __ALLOWLIST_SOURCE__






class NativeToolInput:
    """Validated native arguments, with file operations separate from inert data."""
    def __init__(self, kind: str, metadata: tuple[str, ...], data: tuple[str, ...], operations: tuple[tuple[str, str], ...] = ()) -> None:
        self.kind = kind
        self.metadata = metadata
        self.data = data
        self.operations = operations


def _matches_native_schema(value: dict, required: dict[str, type], optional: dict[str, type] | None = None) -> bool:
    fields = {**required, **(optional or {})}
    if not len(required) <= len(value) <= len(fields):
        return False
    return required.keys() <= value.keys() <= fields.keys() and all(type(child) is fields[key] for key, child in value.items())




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
    normalized_bytes = 0
    for operation, path in native.operations:
        # Move removes its source. Apply the existing environment/Git removal
        # rules to that operation without treating a filename as shell code.
        normalized = unicodedata.normalize("NFKC", path).casefold().replace("\\", "/")
        normalized_bytes += len(normalized.encode("utf-8"))
        if normalized_bytes > MAX_SCAN_TEXT:
            raise ScanLimitExceeded("normalized_operation_bytes", MAX_SCAN_TEXT, normalized_bytes, "bytes")
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




class InspectionFailure(ValueError):
    pass


class _ShellWord:
    def __init__(self, value: str, literal: bool = True, quoted: bool = False) -> None:
        self.value, self.literal, self.quoted = value, literal, quoted


class _ShellCommand:
    def __init__(self) -> None:
        self.words = []
        self.heredocs = []
        self.redirects = []
        self.pipe = False


class _InspectionBudget:
    def __init__(self) -> None:
        self.bytes = self.commands = self.tokens = 0

    def source(self, source: str, depth: int) -> str:
        if depth > 16:
            raise ScanLimitExceeded("executable_depth", 16, depth, "levels")
        _bounded_normalized_text(source)
        self.bytes += len(source.encode("utf-8"))
        if self.bytes > MAX_SCAN_TEXT:
            raise ScanLimitExceeded("executable_bytes", MAX_SCAN_TEXT, self.bytes, "bytes")
        return source

    def matcher_tokens(self, segments, charged=0):
        self.tokens += max(0, sum(len(segment) for segment in segments) - charged)
        if self.tokens > MAX_COMMAND_TOKENS:
            raise ScanLimitExceeded("command_tokens", MAX_COMMAND_TOKENS, self.tokens, "tokens")


def _shell_representation(source: str, budget: _InspectionBudget):
    commands, nested, pending = [], [], []
    command = _ShellCommand()
    pieces = []
    active = quoted = False
    literal = True
    quote = redirect = ""
    strict = False
    index = 0

    def word():
        nonlocal pieces, active, quoted, literal, redirect
        if not active:
            return
        value = _ShellWord("".join(pieces), literal, quoted)
        if redirect:
            command.redirects.append((redirect, value))
            if redirect in {"<<", "<<-"}:
                pending.append((command, value, redirect == "<<-"))
            redirect = ""
        else:
            command.words.append(value)
        pieces = []
        active = quoted = False
        literal = True

    def finish(pipe=False):
        nonlocal command
        word()
        if redirect:
            raise InspectionFailure("missing redirection operand")
        if command.words or command.redirects:
            budget.commands += 1
            budget.tokens += len(command.words) + len(command.redirects)
            if budget.commands > MAX_COMMAND_SEGMENTS:
                raise ScanLimitExceeded("command_segments", MAX_COMMAND_SEGMENTS, budget.commands, "segments")
            if budget.tokens > MAX_COMMAND_TOKENS:
                raise ScanLimitExceeded("command_tokens", MAX_COMMAND_TOKENS, budget.tokens, "tokens")
            command.pipe = pipe
            commands.append(command)
        command = _ShellCommand()

    def substitution(start, backtick=False):
        cursor = start + (1 if backtick else 2)
        body_start, nesting, state = cursor, 1, ""
        while cursor < len(source):
            ch = source[cursor]
            if ch == "\\" and state != "'":
                cursor += 2
                continue
            if backtick:
                if ch == chr(96):
                    nested.append(source[body_start:cursor])
                    return cursor + 1
            elif state:
                if ch == state:
                    state = ""
            elif ch in "'\"":
                state = ch
            elif ch == "(":
                nesting += 1
                if nesting > 16:
                    raise ScanLimitExceeded("executable_depth", 16, nesting, "levels")
            elif ch == ")":
                nesting -= 1
                if nesting == 0:
                    nested.append(source[body_start:cursor])
                    return cursor + 1
            cursor += 1
        raise InspectionFailure("unterminated shell substitution")

    while index < len(source):
        ch = source[index]
        if quote == "'":
            if ch == "'":
                quote = ""
            else:
                pieces.append(ch)
            index += 1
            continue
        if ch == "\\":
            if index + 1 >= len(source):
                raise InspectionFailure("unfinished shell escape")
            following = source[index + 1]
            if following == "\n":
                index += 2
                continue
            if quote == '"' and following not in '$\"\\' + chr(96):
                pieces.append("\\")
                index += 1
                continue
            active = True
            pieces.append(following)
            index += 2
            continue
        if ch == chr(96) or source.startswith("$(", index):
            active, literal = True, False
            strict = strict or source.startswith("$((", index)
            end = substitution(index, ch == chr(96))
            pieces.append(source[index:end])
            index = end
            continue
        if ch == "$":
            active, literal = True, False
            strict = strict or source.startswith("${", index)
        if quote == '"':
            if ch == '"':
                quote = ""
            else:
                pieces.append(ch)
            index += 1
            continue
        if ch in "'\"":
            active = quoted = True
            quote = ch
            index += 1
            continue
        if ch == "#" and not active:
            end = source.find("\n", index)
            index = len(source) if end < 0 else end
            continue
        if ch in " \t\r":
            word()
            index += 1
            continue
        if ch in ";|&\n":
            finish(ch == "|" and not source.startswith("||", index))
            index += 2 if source[index:index + 2] in {"&&", "||"} else 1
            if ch == "\n" and pending:
                for owner, delimiter, strip_tabs in pending:
                    body_start, body_lines = index, []
                    while index < len(source):
                        end = source.find("\n", index)
                        end = len(source) if end < 0 else end
                        line = source[index:end]
                        compared = line.lstrip("\t") if strip_tabs else line
                        index = end + 1 if end < len(source) else end
                        if compared == delimiter.value:
                            break
                        body_lines.append(compared)
                    else:
                        raise InspectionFailure("unterminated heredoc")
                    strict = strict or not delimiter.literal
                    owner.heredocs.append(("\n".join(body_lines), delimiter.quoted))
                    if not delimiter.quoted:
                        cursor = body_start
                        body_end = index - len(delimiter.value) - 1
                        while cursor < body_end:
                            if source[cursor] == "\\":
                                cursor += 2
                            elif source[cursor] == chr(96) or source.startswith("$(", cursor):
                                cursor = substitution(cursor, source[cursor] == chr(96))
                            else:
                                cursor += 1
                pending.clear()
            continue
        if ch in "<>":
            if source[index:index + 2] in {"<(", ">("}:
                strict = True
                end = substitution(index)
                active, literal = True, False
                pieces.append(source[index:end])
                index = end
                continue
            descriptor = ""
            if active and pieces and all(c.isdecimal() for c in pieces):
                descriptor, pieces, active = "".join(pieces), [], False
            else:
                word()
            operator = source[index:index + 2] if source[index:index + 2] in {"<<", ">>", "<&", ">&"} else ch
            if source.startswith("<<-", index):
                operator = "<<-"
            strict = strict or operator in {"<&", ">&"} or descriptor not in {"", "0", "1", "2"}
            strict = strict or operator.startswith("<<") and descriptor not in {"", "0"}
            redirect = operator
            index += len(operator)
            continue
        strict = strict or ch in "(){}" or ch == "\x00"
        active = True
        pieces.append(ch)
        index += 1
    if quote or pending:
        raise InspectionFailure("unterminated shell quote or heredoc")
    finish()
    return commands, nested, strict


_GUARD_TARGETS = frozenset({".codex/hooks/tool-guard.py", ".copilot/hooks/scripts/tool-guard.py", ".gemini/hooks/scripts/tool-guard.py"})


def _literal_search(command):
    words = command.words
    if not words or words[0].value != "rg" or not all(word.literal for word in words):
        return False
    pattern_seen = positional = needs_pattern = False
    for word in words[1:]:
        value = word.value
        if needs_pattern:
            pattern_seen, needs_pattern = True, False
        elif value == "--" and not positional:
            positional = True
        elif not positional and value == "-n":
            continue
        elif not positional and value in {"-e", "--regexp"}:
            needs_pattern = True
        elif not positional and value.startswith("--regexp="):
            pattern_seen = True
        elif not positional and value.startswith("-"):
            return False
        elif not pattern_seen:
            pattern_seen = True
    return pattern_seen and not needs_pattern
def _python_preflight(source):
    """Bound parser work before ast.parse without importing another lexer."""
    index = depth = tokens = 0
    while index < len(source):
        char = source[index]
        if char == "#":
            end = source.find("\n", index)
            index = len(source) if end < 0 else end
            continue
        if char in "'\"":
            delimiter = char * 3 if source.startswith(char * 3, index) else char
            index += len(delimiter)
            while index < len(source) and not source.startswith(delimiter, index):
                index += 2 if source[index] == "\\" else 1
            if index >= len(source):
                raise InspectionFailure("unterminated Python literal")
            index += len(delimiter)
            tokens += 1
            if tokens > 1024:
                raise ScanLimitExceeded("python_syntax_tokens", 1024, tokens, "tokens")
            continue
        if char in "([{":
            depth += 1
            if depth > 32:
                raise ScanLimitExceeded("python_syntax_depth", 32, depth, "levels")
        elif char in ")]}":
            depth -= 1
        if not char.isspace():
            tokens += 1
            if char.isalnum() or char == "_":
                while index + 1 < len(source) and (source[index + 1].isalnum() or source[index + 1] == "_"):
                    index += 1
        if tokens > 1024:
            raise ScanLimitExceeded("python_syntax_tokens", 1024, tokens, "tokens")
        index += 1


def _python_inspection(source):
    """Prove whole writers/surveys, discovering execution sinks independently."""
    _python_preflight(source)
    import ast
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, RecursionError) as error:
        raise InspectionFailure("Python parse failed") from error
    stack, nodes, constant_bytes = [(tree, 0)], [], 0
    while stack:
        node, depth = stack.pop()
        nodes.append(node)
        if len(nodes) > 2048:
            raise ScanLimitExceeded("python_ast_nodes", 2048, len(nodes), "nodes")
        if depth > 32:
            raise ScanLimitExceeded("python_ast_depth", 32, depth, "levels")
        if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
            constant_bytes += len(node.value.encode("utf-8") if isinstance(node.value, str) else node.value)
            if constant_bytes > MAX_SCAN_TEXT:
                raise ScanLimitExceeded("python_constant_bytes", MAX_SCAN_TEXT, constant_bytes, "bytes")
        stack.extend((child, depth + 1) for child in ast.iter_child_nodes(node))
    symbols = {}
    sink_aliases = {}
    for node in nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in {"os", "subprocess"}:
                    sink_aliases[alias.asname or alias.name] = ("module", alias.name)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module in {"os", "subprocess"}:
            for alias in node.names:
                sink_aliases[alias.asname or alias.name] = ("function", node.module + "." + alias.name)
    supported = True
    wrote = surveyed = False
    sinks, inspected = [], set()

    def resolve(node):
        if isinstance(node, ast.Constant) and type(node.value) in {str, int, bool, type(None)}:
            return ("literal", node.value)
        if isinstance(node, ast.Name):
            return symbols.get(node.id)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left, right = resolve(node.left), resolve(node.right)
            if left and right and left[0] == right[0] == "literal" and isinstance(left[1], str) and isinstance(right[1], str):
                value = left[1] + right[1]
                if len(value.encode("utf-8")) > MAX_SCAN_TEXT:
                    raise ScanLimitExceeded("python_resolved_bytes", MAX_SCAN_TEXT, len(value.encode("utf-8")), "bytes")
                return ("literal", value)
        if isinstance(node, (ast.List, ast.Tuple)):
            values = [resolve(item) for item in node.elts]
            return ("sequence", values) if all(values) else None
        if isinstance(node, ast.Dict) and all(key is not None for key in node.keys):
            values = [(resolve(key), resolve(value)) for key, value in zip(node.keys, node.values)]
            return ("json", values) if all(key and value and key[0] == "literal" and value[0] in {"literal", "json", "sequence"} for key, value in values) else None
        if isinstance(node, ast.Attribute):
            base = resolve(node.value)
            if base == ("module", "sys") and node.attr == "executable":
                return ("python", None)
            if base and base[0] == "survey_result" and node.attr == "stdout":
                return ("survey_output", None)
            if base and base[0] == "module":
                return ("function", base[1] + "." + node.attr)
        if isinstance(node, ast.Call):
            function = resolve(node.func)
            args = [resolve(argument) for argument in node.args]
            kwargs = {keyword.arg: resolve(keyword.value) for keyword in node.keywords}
            if None in kwargs or any(value is None for value in args) or any(value is None for value in kwargs.values()):
                return None
            if function == ("function", "pathlib.Path") and len(args) == 1 and args[0][0] == "literal" and isinstance(args[0][1], str) and not kwargs:
                return ("path", args[0][1])
            if isinstance(node.func, ast.Attribute):
                base = resolve(node.func.value)
                if base and base[0] == "path" and node.func.attr == "read_text" and not args and not kwargs:
                    return ("data", base[1])
                if base and base[0] == "data" and node.func.attr == "replace" and len(args) == 2 and all(arg[0] == "literal" and isinstance(arg[1], str) for arg in args) and not kwargs:
                    return base
                if base and base[0] == "path" and node.func.attr == "write_text" and len(args) == 1 and not kwargs and (args[0][0] == "literal" and isinstance(args[0][1], str) or args[0] == ("data", base[1])):
                    return ("write", base[1])
            if function == ("function", "json.dumps") and len(args) == 1 and args[0][0] == "json" and not kwargs:
                return ("json_input", None)
            if function == ("function", "subprocess.run") and len(args) == 1 and args[0][0] == "sequence" and len(args[0][1]) == 2 and args[0][1][0] == ("python", None) and args[0][1][1][0] == "literal" and args[0][1][1][1] in _GUARD_TARGETS and kwargs == {"input": ("json_input", None), "capture_output": ("literal", True), "text": ("literal", True)}:
                return ("survey_result", None)
            if function == ("function", "json.loads") and args == [("survey_output", None)] and not kwargs:
                return ("survey_display", None)
            if isinstance(node.func, ast.Name) and node.func.id == "print" and node.func.id not in symbols and args == [("survey_display", None)] and not kwargs:
                return ("survey_print", None)
        return None

    def inspect_sink(node):
        if not isinstance(node, ast.Call) or id(node) in inspected:
            return
        inspected.add(id(node))
        function = resolve(node.func)
        name = function[1] if function and function[0] == "function" else None
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            root = node.func.value.id
            alias = sink_aliases.get(root, ("module", root) if root in {"os", "subprocess"} else None)
            if alias and alias[0] == "module" and name is None:
                name = alias[1] + "." + node.func.attr
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Call):
            call = node.func.value
            if isinstance(call.func, ast.Name) and call.func.id == "__import__" and call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value in {"os", "subprocess"}:
                name = call.args[0].value + "." + node.func.attr
        elif isinstance(node.func, ast.Name) and name is None:
            alias = sink_aliases.get(node.func.id)
            if alias and alias[0] == "function":
                name = alias[1]
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"} and node.func.id not in symbols:
            name = node.func.id
        if name in {"os.system", "os.popen", "eval", "exec", "subprocess.run", "subprocess.call", "subprocess.Popen", "subprocess.check_call", "subprocess.check_output"}:
            if resolve(node) == ("survey_result", None):
                return
            first = node.args[0] if node.args else next((keyword.value for keyword in node.keywords if keyword.arg in {"args", "command", "object"}), None)
            value = resolve(first) if first is not None else None
            if value and value[0] == "literal" and isinstance(value[1], str):
                sinks.append(("python" if name in {"eval", "exec"} else "shell", value[1]))
            elif value and value[0] == "sequence" and all(item and item[0] == "literal" and isinstance(item[1], str) for item in value[1]):
                import shlex
                sinks.append(("shell", " ".join(shlex.quote(item[1]) for item in value[1])))
            else:
                raise InspectionFailure("unresolved Python execution sink")

    for statement in tree.body:
        for node in ast.walk(statement):
            inspect_sink(node)
        if isinstance(statement, ast.Import) and all(alias.name in {"os", "subprocess", "json", "sys"} for alias in statement.names):
            for alias in statement.names:
                key = alias.asname or alias.name
                if key in symbols:
                    supported = False
                symbols[key] = ("module", alias.name)
            supported = supported and all(alias.name in {"subprocess", "json", "sys"} for alias in statement.names)
        elif isinstance(statement, ast.ImportFrom) and statement.level == 0 and statement.module in {"os", "subprocess"}:
            supported = False
            for alias in statement.names:
                symbols[alias.asname or alias.name] = ("function", statement.module + "." + alias.name)
        elif isinstance(statement, ast.ImportFrom) and statement.module == "pathlib" and statement.level == 0 and len(statement.names) == 1 and statement.names[0].name == "Path":
            key = statement.names[0].asname or "Path"
            if key in symbols:
                supported = False
            symbols[key] = ("function", "pathlib.Path")
        elif isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
            name, value = statement.targets[0].id, resolve(statement.value)
            if name in symbols or value is None:
                supported = False
            symbols[name] = value or ("unknown", None)
            surveyed = surveyed or value == ("survey_result", None)
        elif isinstance(statement, ast.Expr):
            value = resolve(statement.value)
            wrote = wrote or bool(value and value[0] == "write")
            if not value or value[0] not in {"write", "survey_print"}:
                supported = False
        else:
            supported = False
            for node in ast.walk(statement):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    symbols[node.id] = ("unknown", None)
    return supported and (wrote or surveyed), sinks, [node.value for node in nodes if isinstance(node, ast.Constant) and isinstance(node.value, str)]


def _strict_threats(text, segments=None, pipelines=None):
    normalized = _bounded_normalized_text(text)
    tokens = [[unicodedata.normalize("NFKC", token) for token in segment] for segment in segments] if segments is not None else _command_segments(normalized)
    scanned = _ScanText(normalized, tokens)
    lower, threats = normalized.lower(), []
    for (category, severity, matcher, _suggestion), (rule_id, cause) in zip(PATTERNS, RULE_DETAILS, strict=True):
        match = pipelines.get(matcher.pipe_names) if pipelines is not None and hasattr(matcher, "pipe_names") else matcher(scanned, lower)
        if match:
            threats.append({"category": category, "severity": severity, "rule_id": rule_id, "cause": cause, "matched": match})
    return threats


def _python_threats(source, budget, depth, permit_data=True):
    source = budget.source(source, depth)
    proven, sinks, constants = _python_inspection(source)
    proven = proven and permit_data
    threats = []
    if not proven:
        segments = _command_segments(source)
        budget.matcher_tokens(segments, 1)
        threats.extend(_strict_threats(source, segments))
        for constant in constants:
            segments = _command_segments(constant)
            budget.matcher_tokens(segments)
            threats.extend(_strict_threats(constant, segments))
    for language, sink in sinks:
        if language == "python":
            threats.extend(_python_threats(sink, budget, depth + 1))
        else:
            threats.extend(_shell_threats(sink, budget, depth + 1))
    return threats


def _inline_operand(words, offset):
    launcher = _executable_basename(words[offset].value)
    python = re.fullmatch(r"python(?:[23](?:\.[0-9]{1,2})?)?", launcher) is not None
    if not python and launcher not in {"sh", "bash"}:
        return None
    index = offset + 1
    while index < len(words):
        word = words[index]
        option = word.value
        if not word.literal:
            if any(later.value == "-c" for later in words[index + 1:]):
                raise InspectionFailure("unresolved interpreter option prefix")
            return None
        if option == "-c" or not python and option.startswith("-") and not option.startswith("--") and "c" in option[1:]:
            if index + 1 >= len(words):
                raise InspectionFailure("missing interpreter operand")
            operand = words[index + 1]
            if not operand.literal:
                raise InspectionFailure("unresolved interpreter operand")
            return ("python" if python else "shell", operand.value, index)
        if python and option.startswith("-c") and len(option) > 2:
            return ("python", option[2:], index)
        if python and option in {"-W", "-X"} or not python and option in {"--rcfile", "--init-file", "-o", "-O", "+o", "+O"}:
            index += 2
        elif option.startswith("-") and option != "-m":
            index += 1
        else:
            return None
    return None


def _shell_threats(source, budget, depth=0):
    source = budget.source(source, depth)
    commands, nested, strict = _shell_representation(source, budget)
    windows = any(command.words and (
        "\\" in command.words[0].value or command.words[0].value.casefold().endswith((".exe", ".cmd", ".bat"))
        or _executable_basename(command.words[0].value) in {"pwsh", "powershell", "cmd"}
    ) for command in commands)
    strict = strict or windows
    threats = []
    for fragment in nested:
        threats.extend(_shell_threats(fragment, budget, depth + 1))
    if strict:
        if windows:
            segments = [[token for word in command.words for token in word.value.split()] for command in commands]
        else:
            segments = _command_segments(source)
        budget.matcher_tokens(segments, sum(len(command.words) + len(command.redirects) for command in commands))
        threats.extend(_strict_threats(source, segments))
        # Unsupported surrounding syntax cannot hide established interpreter operands.
        for command in commands:
            for offset in range(len(command.words)):
                inline = _inline_operand(command.words, offset)
                if inline:
                    language, operand, _index = inline
                    threats.extend(_python_threats(operand, budget, depth + 1, False) if language == "python" else _shell_threats(operand, budget, depth + 1))
        return threats
    rendered, segments, pipelines = [], [], {}
    pipeline_commands = {"curl", "wget", "bash", "sh", "python", "python3", "rg", "cat", "echo", "printf", "tee", "head", "tail", "sort", "uniq", "wc"}
    for offset, command in enumerate(commands[:-1]):
        if command.pipe and command.words and commands[offset + 1].words:
            before = _executable_basename(command.words[0].value)
            after = _executable_basename(commands[offset + 1].words[0].value)
            if before not in pipeline_commands or after not in pipeline_commands:
                pipelines = None
                break
            if (before, after) in {(R(99, 117, 114, 108), "bash"), (R(119, 103, 101, 116), "sh")}:
                pipelines.setdefault((before, after), before + " | " + after)
    unsafe_pipeline = set()
    output_is_code = False
    for offset in range(len(commands) - 1, -1, -1):
        command = commands[offset]
        if not command.pipe:
            output_is_code = False
        if command.pipe and output_is_code:
            unsafe_pipeline.add(id(command))
        if command.words:
            consumer = _executable_basename(command.words[0].value)
            if consumer in {"sh", "bash", "python", "python3"} or consumer not in pipeline_commands:
                output_is_code = True
    for command in commands:
        words = [word.value for word in command.words]
        if not words:
            continue
        executable = _executable_basename(words[0])
        # Wrappers never obtain a data proof, but established interpreter operands
        # still require their language inspection, including execution sinks.
        for offset in range(len(command.words)):
            inline = _inline_operand(command.words, offset)
            if inline:
                language, operand, argument = inline
                exact = offset == 0 and argument == 1 and len(words) == 3 and words[0] in {"python", "python3", sys.executable, "sh", "bash"}
                if not exact:
                    threats.extend(_python_threats(operand, budget, depth + 1, False) if language == "python" else _shell_threats(operand, budget, depth + 1))
        stdin = [(operator, operand) for operator, operand in command.redirects if operator in {"<", "<<", "<<-"}]
        body = command.heredocs[-1] if command.heredocs and stdin and stdin[-1][0] in {"<<", "<<-"} else None
        python_code = shell_code = None
        proven = False
        shell_inline = executable in {"sh", "bash"} and len(words) >= 3 and words[1].startswith("-") and "c" in words[1][1:]
        if (executable in {"python", "python3"} and words[1:2] == ["-c"] or shell_inline) and len(words) >= 3 and not command.words[2].literal:
            raise InspectionFailure("unresolved interpreter operand")
        if words[0] in {"python", "python3", sys.executable} and all(word.literal for word in command.words):
            if len(words) == 3 and words[1] == "-c":
                python_code = words[2]
            elif words == [words[0], "-"] and body and len(stdin) == 1 and body[1]:
                python_code = body[0]
            elif len(words) == 2 and words[1] in _GUARD_TARGETS and body and body[1] and len(stdin) == 1:
                try:
                    proven = isinstance(json.loads(body[0]), dict)
                except (ValueError, RecursionError) as error:
                    raise InspectionFailure("invalid guardian survey JSON") from error
        elif executable in {"sh", "bash"}:
            if shell_inline and command.words[2].literal:
                shell_code = words[2]
            elif len(words) == 1 and body:
                shell_code = body[0]
        elif executable == "eval":
            if not all(word.literal for word in command.words[1:]):
                raise InspectionFailure("unresolved shell evaluation operand")
            shell_code = " ".join(words[1:])
        elif executable in {"psql", "mysql", "sqlite3"}:
            for offset, word in enumerate(command.words[1:], 1):
                operand = None
                if word.value in {"-c", "-e", "--command", "--execute"}:
                    if offset + 1 >= len(command.words):
                        raise InspectionFailure("missing SQL interpreter operand")
                    operand = command.words[offset + 1]
                elif word.value.startswith(("--command=", "--execute=")):
                    operand = _ShellWord(word.value.split("=", 1)[1], word.literal)
                elif executable == "sqlite3" and offset == 2:
                    operand = word
                if operand is not None:
                    if not operand.literal:
                        raise InspectionFailure("unresolved SQL interpreter operand")
                    sql_segments = _command_segments(operand.value)
                    budget.matcher_tokens(sql_segments, 1)
                    threats.extend(_strict_threats(operand.value, sql_segments))
        if python_code is not None:
            threats.extend(_python_threats(python_code, budget, depth + 1))
            proven = True
        elif shell_code is not None:
            threats.extend(_shell_threats(shell_code, budget, depth + 1))
            proven = True
        if python_code is None and shell_code is None and not proven and (id(command) in unsafe_pipeline or not _literal_search(command)):
            rendered.append(" ".join(words) + (" |" if command.pipe else ""))
            # Unproved consumers retain strict inspection of complete literal values.
            flattened = [token for value in words for token in value.split()]
            budget.matcher_tokens([flattened], len(words))
            segments.append(flattened)
        for operator, operand in command.redirects:
            if operator not in {"<<", "<<-"}:
                operand_segments = _command_segments(operand.value)
                budget.matcher_tokens(operand_segments, 1)
                threats.extend(_strict_threats(operand.value, operand_segments))
        if command.heredocs and (python_code is None and shell_code is None and not proven or len(stdin) != 1 or words[1:2] == ["-c"]):
            for heredoc, _quoted in command.heredocs:
                heredoc_segments = _command_segments(heredoc)
                budget.matcher_tokens(heredoc_segments)
                threats.extend(_strict_threats(heredoc, heredoc_segments))
    if rendered:
        threats.extend(_strict_threats("\n".join(rendered), segments, pipelines))
    order = {rule: index for index, (rule, _cause) in enumerate(RULE_DETAILS)}
    ordered, seen = [], set()
    for threat in sorted(threats, key=lambda threat: order.get(threat["rule_id"], -1)):
        if threat["rule_id"] not in seen:
            seen.add(threat["rule_id"])
            ordered.append(threat)
    return ordered



def sanitize_tool_name(value: str) -> str:
    sanitized = unicodedata.normalize("NFKC", value[:4096])
    # ASCII identifiers have no credential separators; token matches can only
    # start at their first character because every character is a word character.
    if (sanitized.isascii() and sanitized.replace("_", "").isalnum()
            and not sanitized.lower().startswith(("ghp_", "gho_", "ghu_", "ghs_", "ghr_", "akia"))):
        return sanitized if len(sanitized) <= MAX_TOOL_NAME_LENGTH else sanitized[:MAX_TOOL_NAME_LENGTH - 3] + "..."
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
        return _strict_threats(tool_text)
    except ScanLimitExceeded as limit:
        return [limit.threat()]


def build_input_threats(tool_name: str, tool_inputs: tuple[str, ...] | NativeToolInput) -> list[dict[str, str]]:
    if isinstance(tool_inputs, NativeToolInput):
        if tool_inputs.kind == "shell":
            try:
                return _shell_threats(tool_inputs.data[0], _InspectionBudget())
            except InspectionFailure:
                return [{"category": "inspection_failure", "severity": "critical", "rule_id": "inspection_failure", "cause": "executable input could not be completely inspected"}]
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
'''


_PROVIDER_POLICY_SOURCE = r'''
try:
    from helpers.tool_guard_policy import (
        MAX_SCAN_TEXT,
        MAX_NATIVE_DATA_BYTES,
        MAX_COMMAND_SEGMENTS,
        MAX_COMMAND_TOKENS,
        MAX_STRUCTURED_DEPTH,
        MAX_STRUCTURED_NODES,
        MAX_STRUCTURED_STRINGS,
        MAX_TOOL_NAME_LENGTH,
        MAX_EXCERPT_LENGTH,
        REDACTED,
        KNOWN_TOOL_FIELDS,
        ScanLimitExceeded,
        R,
        _is_word_char,
        _find_word,
        _simple_match,
        _bounded_normalized_text,
        _command_segments,
        _ScanText,
        _executable_basename,
        _matches_protected_remove_target,
        _match_recursive_rm_target,
        _match_rm_env,
        _match_rm_git,
        _match_git_push,
        _sql_code_without_comments_or_literals,
        _match_delete_from,
        _match_pipe_chain,
        _match_data_upload,
        PATTERNS,
        RULE_DETAILS,
        NativeToolInput,
        _matches_native_schema,
        _parse_native_patch,
        _native_operation_threats,
        InspectionFailure,
        _ShellWord,
        _ShellCommand,
        _InspectionBudget,
        _shell_representation,
        _GUARD_TARGETS,
        _literal_search,
        _python_preflight,
        _python_inspection,
        _strict_threats,
        _python_threats,
        _inline_operand,
        _shell_threats,
        sanitize_tool_name,
        build_threats,
        build_input_threats,
        sanitize_excerpt,
        safe_excerpt_context,
        safe_git_push_match,
        build_action_excerpt,
        log_threat_metadata,
        build_block_reason,
        _normalize_allowlist_value,
        _has_forbidden_allowlist_separator,
        parse_allowlist,
        allowlist_contains,
    )
except Exception:
    emit_deny_response("Tool Guardian blocked execution due to an internal error.")


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



def _native_tool_shape(tool_name: str, value: object) -> NativeToolInput | None:
    if not isinstance(value, dict) or len(value) > MAX_STRUCTURED_NODES:
        return None
    shell_tools = {"codex": {"Bash", "exec_command", "functions.exec_command"}, "copilot": {"bash"}, "gemini": {"run_shell_command"}}
    if tool_name in shell_tools.get(TOOL_PROVIDER, set()):
        key = "cmd" if tool_name in {"exec_command", "functions.exec_command"} else "command"
        if _matches_native_schema(value, {key: str}):
            return NativeToolInput("shell", (), (value[key],))
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
                if type(child) not in allowed_types or (type(child) is list and (
                    len(child) > MAX_STRUCTURED_NODES or any(type(item) is not str for item in child)
                )):
                    return None
            return NativeToolInput("search", (), tuple(child for child in value.values() if isinstance(child, str)))
    return None



def read_tool_scan_inputs(payload: dict) -> tuple[str, ...] | NativeToolInput:
    value = _read_tool_input_value(payload)
    if isinstance(value, str):
        return (value,)

    tool_name = read_tool_name(payload)
    native = _native_tool_shape(tool_name, value)
    byte_limit = MAX_NATIVE_DATA_BYTES if native and native.kind != "shell" else MAX_SCAN_TEXT
    known_fields = KNOWN_TOOL_FIELDS.get(tool_name.casefold(), frozenset())
    stack = [iter(((value, 0, "tool input"),))]
    strings: list[str] = []
    node_count = 0
    total_string_bytes = 0
    keys: list[str] = []

    def dictionary_children(mapping, depth):
        for key, child in mapping.items():
            keys.append(key)
            field = f"{tool_name.casefold()}.{key}" if depth == 0 and key in known_fields and isinstance(child, str) else "tool input"
            yield child, depth + 1, field

    def sequence_children(sequence, depth):
        for child in sequence:
            yield child, depth + 1, "tool input"

    while stack:
        try:
            current, depth, field = next(stack[-1])
        except StopIteration:
            stack.pop()
            continue
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
            stack.append(dictionary_children(current, depth))
        elif isinstance(current, (list, tuple)):
            stack.append(sequence_children(current, depth))

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

'''


_COPILOT_LOGGING_ADAPTER = r'''
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
'''


_CODEX_LOGGING_ADAPTER = _COPILOT_LOGGING_ADAPTER.replace(
    'Path.home() / ".copilot"', 'Path.home() / ".codex"'
)


_GEMINI_LOGGING_ADAPTER = r'''
LOG_LOCK_TIMEOUT_SECONDS = 1.0


def format_error(error: Exception) -> str:
    return type(error).__name__


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
    excerpt: str | None = None,
) -> None:
    parent = os.path.dirname(log_file)
    if parent:
        os.makedirs(parent, mode=0o700, exist_ok=True)

    payload: dict[str, object] = {
        "timestamp": timestamp,
        "event": event,
        "mode": mode,
        "tool": sanitize_tool_name(tool_name),
    }
    if event == "threats_detected":
        payload["threat_count"] = threat_count
        payload["threats"] = threats or []
        payload["excerpt"] = excerpt or "command omitted"

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


def log_payload(event: str, mode: str, tool_name: str, threat_count: int = 0, threats: list[dict[str, str]] | None = None, excerpt: str | None = None) -> None:
    append_log(LOG_FILE, event, mode, tool_name, TIMESTAMP, threat_count, threats, excerpt)
'''


_MAIN_SOURCE = r'''

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
'''


def _adapter_sources(provider: Provider) -> tuple[str, str]:
    if provider.name == "copilot":
        return _COPILOT_IMPORT_AND_RESPONSE_ADAPTER, _COPILOT_LOGGING_ADAPTER
    if provider.name == "gemini":
        return _GEMINI_IMPORT_AND_RESPONSE_ADAPTER, _GEMINI_LOGGING_ADAPTER
    if provider.name == "codex":
        return _CODEX_IMPORT_AND_RESPONSE_ADAPTER, _CODEX_LOGGING_ADAPTER
    raise ValueError(f"Unsupported Tool Guardian provider: {provider.name}")


def render(provider: Provider, target: GeneratedTarget) -> str:
    """Render a provider entrypoint or its local, provider-neutral policy helper."""
    if target.provider != provider.name or provider.name not in {"copilot", "gemini", "codex"}:
        raise ValueError(f"Unsupported Tool Guardian target/provider: {target.output_path}")
    if target.output_path.name == "tool_guard_policy.py":
        return SHEBANG + HEADER + "\nfrom __future__ import annotations\n\nimport json\nimport sys\n" + _POLICY_SOURCE.replace("# __ALLOWLIST_SOURCE__\n", ALLOWLIST_SOURCE)
    import_adapter, logging_adapter = _adapter_sources(provider)
    return (
        SHEBANG
        + HEADER
        + "\nfrom __future__ import annotations\n\n"
        + ADAPTER_START
        + import_adapter
        + ADAPTER_END
        + _PROVIDER_POLICY_SOURCE
        + "\n"
        + ADAPTER_START
        + logging_adapter
        + ADAPTER_END
        + _MAIN_SOURCE
    )

#!/usr/bin/env python3
# Generated from hooks/families/repository_state.py by scripts/generate-hooks.py. Do not edit.
from __future__ import annotations

import json
import ntpath
import os
from pathlib import Path
import re
import shlex
import stat
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from helpers.common import emit_json, read_json_input

PROVIDER = "codex"
SHELL_TOOLS = {"bash", "shell", "run_shell_command", "powershell", "pwsh", "exec_command"}
EDITOR_TOOLS = {"create", "edit", "write", "write_file", "replace", "apply_patch", "multiedit"}
PATH_KEYS = {"file_path", "filepath", "path", "target_file", "filename", "old_path", "new_path", "destination"}
COMMAND_KEYS = ("command", "cmd", "script")
REVIEW = ("Show git status, unstaged git diff for affected paths, git diff --cached for affected paths, "
          "and untracked files or a dry-run deletion list. If local work would be lost, ask user to "
          "approve this exact command, then have user run it directly. Prior approval does not carry forward.")


def deny(reason):
    if PROVIDER == "copilot":
        return {"continue": True, "permissionDecision": "deny",
                "hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": reason},
                "permissionDecisionReason": reason}
    if PROVIDER == "gemini":
        return {"decision": "deny", "reason": reason}
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def _linked(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _safe_layout_path(path):
    # Normalize the platform root alias (for example macOS /var -> /private/var).
    anchor = Path(path.anchor)
    parts = path.relative_to(anchor).parts
    if parts:
        path = (anchor / parts[0]).resolve(strict=False).joinpath(*parts[1:])
    for part in (path, *path.parents):
        if _linked(part):
            raise ValueError("linked Git metadata layout")
    return path.resolve(strict=False)


def git_layout(cwd):
    current = cwd.resolve(strict=True)
    for root in (current, *current.parents):
        dotgit = root / ".git"
        if not dotgit.exists() and not dotgit.is_symlink():
            continue
        _safe_layout_path(dotgit)
        if dotgit.is_dir():
            gitdir = dotgit
        elif dotgit.is_file():
            raw = dotgit.read_bytes()
            if len(raw) > 4096:
                raise ValueError("oversized .git pointer")
            match = re.fullmatch(rb"gitdir: ([^\r\n]+)\r?\n?", raw)
            if not match:
                raise ValueError("malformed .git pointer")
            value = os.fsdecode(match.group(1))
            gitdir = Path(value)
            if not gitdir.is_absolute():
                gitdir = root / gitdir
        else:
            raise ValueError("unsupported .git pointer")
        gitdir = _safe_layout_path(gitdir)
        if not gitdir.is_dir():
            raise ValueError("missing Git directory")
        common_file = gitdir / "commondir"
        _safe_layout_path(common_file)
        if common_file.exists():
            raw = common_file.read_bytes()
            if len(raw) > 4096 or not raw.strip() or b"\n" in raw.strip():
                raise ValueError("malformed common directory pointer")
            common = Path(os.fsdecode(raw.strip()))
            if not common.is_absolute():
                common = gitdir / common
            common = _safe_layout_path(common)
            if not common.is_dir():
                raise ValueError("missing common Git directory")
        else:
            common = gitdir
        return (dotgit, gitdir, common)
    return ()


def _norm(path):
    string = os.fspath(path).replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", string):
        return ntpath.normcase(ntpath.normpath(string)).replace("\\", "/")
    return os.path.normcase(os.path.normpath(string)).replace("\\", "/")


def _inside(path, root):
    name, parent = _norm(path).rstrip("/"), _norm(root).rstrip("/")
    return name == parent or name.startswith(parent + "/")


def _mentions_dotgit(text):
    return bool(re.search(r"(?i)(?:^|[^\w.-])(?:\.\/)*\.git(?:[\\/]|(?=$|[^\w.-]))", text))


def metadata_path(path, cwd, layout):
    if not isinstance(path, str) or not path.strip():
        raise ValueError("missing editor path")
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = cwd / candidate
    # Resolve existing aliases without opening the metadata target.
    resolved = candidate.resolve(strict=False)
    if _mentions_dotgit(path):
        return True
    return any(_inside(candidate, root) or _inside(resolved, root) for root in layout)


def _shell_segments(command):
    lexer = shlex.shlex(command, posix=False, punctuation_chars=";&|<>\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    segments = [[]]
    for token in lexer:
        if token in (";", "&&", "||", "|", "&", "\n"):
            segments.append([])
        else:
            segments[-1].append(token)
    return segments


def _unquote(token):
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return token[1:-1]
    return token


def _command_start(tokens):
    index = 0
    while index < len(tokens) and re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*=.*", tokens[index]):
        index += 1
    while index < len(tokens) and _unquote(tokens[index]).lower() in ("command", "env", "sudo", "rtk"):
        index += 1
        if index < len(tokens) and _unquote(tokens[index]).lower() == "proxy":
            index += 1
    return index


def _git_action(command, depth=0):
    if depth > 3:
        return "uncertain nested command"
    try:
        segments = _shell_segments(command)
    except ValueError:
        return "uncertain Git command"
    for tokens in segments:
        start = _command_start(tokens)
        if start >= len(tokens):
            continue
        name = _unquote(tokens[start]).lower()
        if name in ("bash", "sh", "zsh", "pwsh", "powershell"):
            for option in range(start + 1, len(tokens) - 1):
                if _unquote(tokens[option]).lower() in ("-c", "-command"):
                    nested = _git_action(_unquote(tokens[option + 1]), depth + 1)
                    if nested:
                        return nested
                    break
        if name not in ("git", "git.exe"):
            continue
        tokens = [_unquote(token) for token in tokens[start:]]
        index = 1
        while index < len(tokens):
            token = tokens[index]
            if token in ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"):
                index += 2
            elif token.startswith("-"):
                index += 1
            else:
                break
        if index >= len(tokens):
            continue
        operation = tokens[index].lower()
        arguments = [part.lower() for part in tokens[index + 1:]]
        if operation == "clean" and any(part in ("-n", "--dry-run") or
                                        (part.startswith("-") and "n" in part[1:]) for part in arguments):
            continue
        if operation in ("checkout", "restore", "reset", "clean", "switch"):
            return f"git {operation}"
        if operation == "stash" and any(part in ("drop", "clear") for part in arguments):
            return "git stash"
        if operation == "checkout-index" and any(part in ("-f", "--force", "-a", "--all") for part in arguments):
            return "git checkout-index"
        if operation == "read-tree" and any(part in ("--reset", "-u") for part in arguments):
            return "git read-tree"
        if operation == "worktree" and "remove" in arguments and any(part in ("-f", "--force") for part in arguments):
            return "git worktree remove"
        if operation == "branch" and any(part in ("-D", "--delete", "-d") for part in tokens[index + 1:]):
            return "git branch delete"
    return ""


def _metadata_token(token, layout):
    path = _unquote(token).replace("\\", "/")
    if _mentions_dotgit(path):
        return True
    if not (path.startswith("/") or re.match(r"^[A-Za-z]:/", path)):
        return False
    candidate = Path(path).resolve(strict=False)
    return any(_inside(candidate, root) for root in layout)


def _writes_metadata(command, layout, script_source=False, depth=0):
    if depth > 3:
        return True
    if script_source:
        command = re.sub(r'(?ms)@(?P<quote>["\'])\r?\n.*?^[ \t]*(?P=quote)@(?=\r?$)',
                         "'literal'", command)
    # Inspect shell tokens. Quoted prose is data, not a write operation.
    try:
        segments = _shell_segments(command)
    except ValueError:
        return True
    writer_commands = {"tee", "touch", "rm", "mv", "cp", "chmod", "set-content", "add-content",
                       "out-file", "remove-item", "copy-item", "move-item", "new-item", "truncate", "install"}
    script_write = re.compile(r"(?i)\b(?:write_text|write_bytes|unlink|remove|rmtree|mkdir|makedirs)\s*\(|\bopen\s*\([^)]*,\s*['\"]?[wax+]")
    for tokens in segments:
        start = _command_start(tokens)
        if start >= len(tokens):
            continue
        command_name = ntpath.basename(_unquote(tokens[start]).lower()).removesuffix(".exe")
        if command_name in ("bash", "sh", "zsh", "pwsh", "powershell"):
            for option in range(start + 1, len(tokens) - 1):
                if _unquote(tokens[option]).lower() in ("-c", "-command"):
                    if _writes_metadata(_unquote(tokens[option + 1]), layout, depth=depth + 1):
                        return True
                    break
        for index, token in enumerate(tokens):
            if token in (">", ">>") and index + 1 < len(tokens) and _metadata_token(tokens[index + 1], layout):
                return True
        target_is_metadata = any(_metadata_token(token, layout) for token in tokens[start + 1:])
        if command_name in writer_commands and target_is_metadata:
            return True
        if command_name == "sed" and target_is_metadata:
            options = (_unquote(token) for token in tokens[start + 1:])
            if any(option.startswith("--in-place") or
                   (option.startswith("-") and not option.startswith("--") and "i" in option[1:])
                   for option in options):
                return True
        if command_name == "perl" and target_is_metadata:
            options = (_unquote(token) for token in tokens[start + 1:])
            if any(option.startswith("-") and not option.startswith("--") and "i" in option[1:]
                   for option in options):
                return True
        if script_source or command_name in ("python", "python3", "py", "pwsh", "powershell", "bash", "sh", "zsh"):
            if any(script_write.search(_unquote(token)) and _metadata_token(token, layout) for token in tokens[start:]):
                return True
    return False


def _editor_paths(tool_input):
    if isinstance(tool_input, str):
        return re.findall(r"(?m)^\*\*\* (?:Add|Update|Delete|Move to) File: (.+)$", tool_input)
    if not isinstance(tool_input, dict):
        raise ValueError("malformed editor input")
    paths = []
    for key, value in tool_input.items():
        if key.lower() in PATH_KEYS:
            if not isinstance(value, str):
                raise ValueError("malformed editor path")
            paths.append(value)
    patch = tool_input.get("patch", tool_input.get("command"))
    if isinstance(patch, str):
        paths.extend(_editor_paths(patch))
    if not paths:
        raise ValueError("missing editor path")
    return paths


def inspect(payload):
    if not isinstance(payload, dict):
        return "Malformed tool payload; Git state protection blocked this action."
    tool = payload.get("toolName", payload.get("tool_name")) if PROVIDER == "copilot" else payload.get("tool_name")
    args = payload.get("toolArgs", payload.get("tool_input")) if PROVIDER == "copilot" else payload.get("tool_input")
    if not isinstance(tool, str) or not tool.strip() or not isinstance(args, (dict, str)):
        return "Malformed tool payload; Git state protection blocked this action."
    cwd_text = payload.get("cwd")
    if not isinstance(cwd_text, str) or not Path(cwd_text).is_absolute():
        return "Malformed workspace path; Git state protection blocked this action."
    cwd = Path(cwd_text)
    if not cwd.is_dir():
        return "Workspace path unavailable; Git state protection blocked this action."
    tool = tool.lower()
    command = None
    if tool in SHELL_TOOLS:
        command = args if isinstance(args, str) else next((args[key] for key in COMMAND_KEYS if key in args), None)
        if not isinstance(command, str):
            return "Malformed shell command; Git state protection blocked this action."
        action = _git_action(command)
        if action:
            return f"Work-discarding {action} blocked. {REVIEW}"
    try:
        layout = git_layout(cwd)
    except (OSError, ValueError):
        if tool in EDITOR_TOOLS or (command is not None and _writes_metadata(command, ())):
            return "Git metadata layout could not be verified. Run a read-only layout probe before writing."
        return ""
    if tool in EDITOR_TOOLS:
        try:
            paths = _editor_paths(args)
            if any(metadata_path(path, cwd, layout) for path in paths):
                return "Git metadata write blocked. Use Git commands for repository state."
            content = args.get("content", "") if isinstance(args, dict) else ""
            script_path = any(Path(path).suffix.lower() in (".py", ".ps1", ".sh", ".bash", ".cmd", ".bat") for path in paths)
            if script_path and isinstance(content, str) and _writes_metadata(content, layout, script_source=True):
                return "Git metadata write in script text blocked. Use Git commands for repository state."
        except (OSError, ValueError):
            return "Editor path could not be verified; Git metadata write blocked."
        return ""
    if tool in SHELL_TOOLS:
        if _writes_metadata(command, layout):
            return "Git metadata write blocked. Use Git commands for repository state."
    return ""


def main():
    try:
        payload = read_json_input()
        reason = inspect(payload)
    except Exception:
        reason = "Git state protection could not inspect the tool call; action blocked."
    response = deny(reason) if reason else {}
    emit_json(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

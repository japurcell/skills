"""Exact provider registration identities, including explicitly retired events.

This installer-only registry never runs inside provider hooks. Unknown commands
are retained; an owned path combined with an unrecognized launch is ambiguous.
"""
from __future__ import annotations

import copy
from contextlib import contextmanager
import os
from pathlib import Path
import stat
import shlex

from scripts.trusted_hook_launch import serialize_trusted_launch, trusted_posix_arguments

DESIRED = {
    "codex": {"SessionStart": ("load-required-skills.py",), "PreToolUse": ("tool-guard.py",), "Stop": ("scan-status.py",)},
    "copilot": {
        **{event: ("send-event.py",) for event in ("agentStop", "errorOccurred", "notification", "permissionRequest", "postToolUse", "preCompact", "postToolUseFailure", "subagentStart", "subagentStop", "userPromptSubmitted", "userPromptTransformed")},
        "agentStop": ("send-event.py", "scan-status.py"),
        "preToolUse": ("send-event.py", "tool-guard.py"),
        "sessionEnd": ("send-event.py", "bell.py"),
        "sessionStart": ("send-event.py", "load-required-skills.py"),
    },
    "gemini": {
        **{event: ("send-event.py",) for event in ("AfterAgent", "BeforeAgent", "BeforeModel", "AfterModel", "BeforeToolSelection", "AfterTool", "PreCompress", "Notification", "SessionEnd")},
        "SessionStart": ("send-event.py", "skill-context-injector.py"),
        "BeforeTool": ("send-event.py", "tool-guard.py", "rtk-hook-gemini.py"),
        "AfterAgent": ("send-event.py", "scan-status.py"),
    },
}
# These identities do not depend on events present in the replacement template.
RETIRED = {
    "codex": {"PreToolUse": ("scan-secrets.py", "rtk-explicit-codex.py"), "PostToolUse": ("rtk-explicit-codex.py", "rtk-agent-launcher.py"), "Stop": ("scan-secrets.py",)},
    "copilot": {"preToolUse": ("scan-secrets.py",), "sessionEnd": ("scan-secrets.py",)},
    "gemini": {"BeforeTool": ("scan-secrets.py",), "SessionEnd": ("scan-secrets.py",)},
}


def legacy_commands(provider, filename):
    if provider == "codex":
        return {"command": f"python3 ~/.codex/hooks/{filename}", "commandWindows": f'py -3 "%USERPROFILE%\\.codex\\hooks\\{filename}"'}
    path = f"$HOME/.{provider}/hooks/scripts/{filename}"
    return {"bash": path, "powershell": f'python "{path}"'} if provider == "copilot" else {"command": f'python "{path}"'}


def literal_output_command(command, provider, field):
    """Recognize only known POSIX output fields without evaluation/sinks."""
    posix_field = field == "bash" or (field == "command" and (provider == "codex" or os.name == "posix"))
    if not posix_field:
        return False
    if any(character in command for character in "$`;&|<>(){}\r\n"):
        return False
    try:
        arguments = shlex.split(command)
    except ValueError:
        return False
    return bool(arguments) and arguments[0] in {"echo", "printf"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def classify(handler, provider, event, directory):
    """Return an exact owned filename, None for unowned, or refuse ambiguity."""
    names = set(DESIRED[provider].get(event, ())) | set(RETIRED[provider].get(event, ()))
    keys = ("command", "commandWindows") if provider == "codex" else ("bash", "powershell") if provider == "copilot" else ("command",)
    for key in keys:
        if key in handler and not isinstance(handler[key], str):
            raise ValueError("Hook command must be a string")
    def admit(filename):
        executable_fields = {"command", "commandWindows", "bash", "powershell"}
        if set(handler) & (executable_fields - set(keys)) or handler.get("type", "command") != "command":
            raise ValueError(f"Ambiguous {provider} hook ownership at {event}; unsupported executable override")
        return filename

    for filename in names:
        legacy = legacy_commands(provider, filename)
        if all(handler.get(key) == value for key, value in legacy.items()):
            return admit(filename)
        # A bash-only old provider config is an explicitly maintained fixture
        # shape, provided it has no alternate executable override.
        if provider == "copilot" and handler.get("bash") == legacy["bash"] and "powershell" not in handler and "command" not in handler:
            return admit(filename)
        script = str(directory / filename)
        command = handler.get(keys[0], "")
        arguments = trusted_posix_arguments(command)
        python = arguments[0] if arguments and arguments[4] == script else None
        if provider == "gemini" and os.name == "nt":
            prefix, separator, suffix = command.partition(" -I -S -B ")
            if separator and suffix == f'"{script}"' and prefix.startswith('"') and prefix.endswith('"'):
                python = prefix[1:-1]
        if python:
            shells = ("posix", "windows") if provider == "codex" else ("posix", "powershell") if provider == "copilot" else ("native",)
            if all(handler.get(key) == serialize_trusted_launch(python, script, shell, windows=os.name == "nt") for key, shell in zip(keys, shells)):
                return admit(filename)
        # Mentioning our exact home path with unknown executable behavior is
        # neither ownership proof nor permission to delete that behavior.
        markers = (script, f"~/.{provider}/hooks/{filename}", f"$HOME/.{provider}/hooks/scripts/{filename}", f"%USERPROFILE%\\.{provider}\\hooks\\{filename}")
        if any(marker in handler.get(key, "") and not literal_output_command(handler.get(key, ""), provider, key) for key in keys for marker in markers):
            raise ValueError(f"Ambiguous {provider} hook ownership at {event}; review commands before retrying")
    return None


def reconcile(current, maintained, provider, directory):
    result = copy.deepcopy(current)
    disabled = {}
    # Collect disable intent before moving scanner registration to End Turn.
    for event in set(DESIRED[provider]) | set(RETIRED[provider]):
        entries = current.get(event, [])
        for entry in entries:
            for handler in ([entry] if provider == "copilot" else entry["hooks"]):
                name = classify(handler, provider, event, directory)
                if name:
                    intent = {key: value for obj in (entry, handler) for key, value in obj.items() if (key == "enabled" and value is False) or (key == "disabled" and value is True)}
                    disabled.setdefault("scan-status.py" if name == "scan-secrets.py" else name, {}).update(intent)
    for event in dict.fromkeys((*maintained, *RETIRED[provider])):
        if provider == "gemini" and event == "disabled":
            result.setdefault(event, copy.deepcopy(maintained[event]))
            continue
        entries = current.get(event, [])
        preserved = []
        for entry in entries:
            if provider == "copilot":
                if classify(entry, provider, event, directory) is None:
                    preserved.append(copy.deepcopy(entry))
            else:
                remaining = [copy.deepcopy(handler) for handler in entry["hooks"] if classify(handler, provider, event, directory) is None]
                if remaining or not entry["hooks"]:
                    preserved.append({**copy.deepcopy(entry), "hooks": remaining})
        replacements = copy.deepcopy(maintained.get(event, []))
        for entry in replacements:
            for handler in ([entry] if provider == "copilot" else entry["hooks"]):
                name = classify(handler, provider, event, directory)
                if name:
                    handler.update(disabled.get(name, {}))
        if event in current or replacements:
            result[event] = [*preserved, *replacements]
    return result


def has_status_registration(provider, maintained, directory):
    for event, entries in maintained.items():
        if "scan-status.py" not in DESIRED[provider].get(event, ()):
            continue
        for entry in entries:
            for handler in ([entry] if provider == "copilot" else entry["hooks"]):
                if classify(handler, provider, event, directory) == "scan-status.py":
                    return True
    return False


def validate_status_asset(provider, maintained, directory):
    """Activation requires the exact deployed self-contained replacement asset."""
    if not has_status_registration(provider, maintained, directory):
        return
    source = Path(__file__).resolve().parents[1] / f".{provider}/hooks"
    if provider != "codex":
        source /= "scripts"
    source /= "scan-status.py"
    target = directory / "scan-status.py"
    info = target.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size != source.stat().st_size or target.read_bytes() != source.read_bytes():
        raise ValueError("Replacement status asset is missing, linked or invalid; deploy assets before activation")


def check_parent_directories(home: Path, destination: Path) -> None:
    home = Path(os.path.abspath(home))
    destination = Path(os.path.abspath(destination))
    try:
        relative = destination.relative_to(home)
    except ValueError as exc:
        raise ValueError(f"Destination is outside the install home: {destination}") from exc
    if not relative.parts:
        raise ValueError(f"Destination must be a file below the install home: {destination}")

    ancestor = home
    while ancestor != ancestor.parent:
        system_alias = os.name == "posix" and str(ancestor) in {"/var", "/tmp"} and str(ancestor.resolve()) == "/private" + str(ancestor)
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            ancestor = ancestor.parent
            continue
        reparse = getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        if (stat.S_ISLNK(info.st_mode) and not system_alias) or reparse:
            raise ValueError("Refusing linked configuration ancestor")
        ancestor = ancestor.parent

    current = home
    for part in ("", *relative.parts[:-1]):
        if part:
            current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        ):
            raise ValueError(f"Refusing linked configuration directory: {current}")
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError(f"Configuration parent must be a directory: {current}")



def preflight_status_path(provider, maintained, directory):
    if not has_status_registration(provider, maintained, directory):
        return
    current = directory
    while current != current.parent:
        system_alias = os.name == "posix" and str(current) in {"/var", "/tmp"} and str(current.resolve()) == "/private" + str(current)
        try:
            info = current.lstat()
        except FileNotFoundError:
            current = current.parent
            continue
        reparse = getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        if (stat.S_ISLNK(info.st_mode) and not system_alias) or reparse:
            raise ValueError("Refusing linked status asset directory")
        current = current.parent
    target = directory / "scan-status.py"
    try:
        info = target.lstat()
    except FileNotFoundError:
        return
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError("Refusing linked status asset; restore a private regular file before retrying")


@contextmanager
def configuration_lock(destination, check=False):
    """A stable kernel-released lock for cooperating writers, never a CAS."""
    if check:
        yield
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    path = destination.with_name(destination.name + ".install-lock")
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    locked = False
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or (hasattr(os, "getuid") and (info.st_uid != os.getuid() or info.st_mode & 0o077)):
            raise ValueError("Unsafe provider migration lock")
        try:
            if os.name == "nt":
                import msvcrt
                if info.st_size == 0:
                    os.write(descriptor, b"0")
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise ValueError("Provider migration is busy; retry after the cooperating writer finishes") from None
        locked = True
        yield
    finally:
        if locked:
            if os.name == "nt":
                import msvcrt
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def verify_unchanged(destination, existed, content):
    if destination.is_symlink() or destination.exists() != existed:
        raise ValueError("Provider configuration changed during migration; review and retry")
    if existed and destination.read_bytes() != content:
        raise ValueError("Provider configuration changed during migration; review and retry")

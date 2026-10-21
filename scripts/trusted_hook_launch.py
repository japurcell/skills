"""Render installed security and brain launches without runtime interpreter lookup."""

from __future__ import annotations

from collections.abc import Iterable
import os
from pathlib import Path
import sys

SECURITY_HOOK_FILES = ("scan-secrets.py", "tool-guard.py", "scan-status.py")
BRAIN_HOOK_FILES = ("auto-index-brain.py", "inject-brain.py")
PINNED_HOOK_FILES = SECURITY_HOOK_FILES + BRAIN_HOOK_FILES


def hook_arguments(filename: str, provider: str) -> tuple[str, ...]:
    return ("--provider", provider) if filename in BRAIN_HOOK_FILES else ()


def template_commands(provider: str, filename: str) -> dict[str, str]:
    extra = hook_arguments(filename, provider)
    suffix = " " + " ".join(extra) if extra else ""
    if provider == "codex":
        return {"command": f"python3 ~/.codex/hooks/{filename}" + suffix,
                "commandWindows": f'py -3 "%USERPROFILE%\\.codex\\hooks\\{filename}"' + suffix}
    path = f"$HOME/.{provider}/hooks/scripts/{filename}"
    if provider == "copilot":
        bash = f'python3 "{path}"' if filename in BRAIN_HOOK_FILES else path
        return {"bash": bash + suffix, "powershell": f'python "{path}"' + suffix}
    return {"command": f'python "{path}"' + suffix}



def serialize_trusted_launch(python: str, script: str, shell: str, *, windows: bool = False, extra: tuple[str, ...] = ()) -> str:
    """Quote a validated isolated-interpreter launch and constant hook arguments."""
    import shlex

    arguments = [python, "-I", "-S", "-B", script, *extra]
    if shell == "powershell":
        return "& " + " ".join("'" + item.replace("'", "''") + "'" for item in arguments)
    if shell == "windows" or (shell == "native" and windows):
        return f'"{python}" -I -S -B "{script}"' + (" " + " ".join(extra) if extra else "")
    return shlex.join(arguments)


def trusted_posix_arguments(command: str) -> list[str] | None:
    """Recognize only the shared POSIX isolated-interpreter argument shape."""
    from pathlib import Path
    import shlex

    try:
        arguments = shlex.split(command)
    except ValueError:
        return None
    if ((len(arguments) != 5 and not (len(arguments) == 7 and arguments[5] == "--provider" and arguments[6] in {"codex", "copilot", "gemini"})) or arguments[1:4] != ["-I", "-S", "-B"]
            or not Path(arguments[0]).is_absolute()):
        return None
    return arguments


def trusted_command(script: Path, shell: str = "native", executable: str | None = None, *, extra: tuple[str, ...] = ()) -> str:
    python = Path(executable or sys.executable)
    if not python.is_absolute() or (executable is None and not python.is_file()):
        raise ValueError("Trusted Python must be an absolute executable file")
    script_text = str(script.absolute())
    if shell == "windows" or (shell == "native" and os.name == "nt"):
        # cmd.exe metacharacters must remain inside quotes even without spaces.
        # Percent/delayed expansion cannot be made literal across host shells.
        if any(any(character in item for character in ('"', '%', '!', '\r', '\n')) for item in (str(python), script_text)):
            raise ValueError("Trusted hook paths contain unsupported Windows shell characters")
    return serialize_trusted_launch(str(python), script_text, shell, windows=os.name == "nt", extra=extra)


def is_trusted_pair(handler: dict, script: Path) -> bool:
    arguments = trusted_posix_arguments(handler.get("command", ""))
    if arguments is None or arguments[4] != str(script):
        return False
    try:
        return (handler.get("command") == trusted_command(script, "posix", arguments[0])
                and handler.get("commandWindows") == trusted_command(script, "windows", arguments[0]))
    except ValueError:
        return False


def _pin_hook_commands(
    entries: Iterable[dict], provider: str, hook_directory: Path, fields: tuple[tuple[str, str], ...]
) -> None:
    for entry in entries:
        for handler in ([entry] if provider == "copilot" else entry["hooks"]):
            for filename in PINNED_HOOK_FILES:
                legacy = template_commands(provider, filename)
                if provider == "copilot":
                    matches = handler.get("bash") == legacy["bash"] and ("powershell" not in handler or handler["powershell"] == legacy["powershell"])
                else:
                    matches = handler.get("command") == legacy["command"]
                if not matches:
                    continue
                script = hook_directory / filename
                for key, shell in fields:
                    handler[key] = trusted_command(script, shell, extra=hook_arguments(filename, provider))


def pin_provider_commands(template: dict, provider: str, home: Path) -> None:
    fields = (("bash", "posix"), ("powershell", "powershell")) if provider == "copilot" else (("command", "native"),)
    entries = (
        entry for event, groups in template.get("hooks", {}).items()
        if not (provider == "gemini" and event == "disabled")
        for entry in groups
    )
    _pin_hook_commands(entries, provider, home / f".{provider}/hooks/scripts", fields)

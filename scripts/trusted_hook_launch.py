"""Render installed security-hook launches without runtime interpreter lookup."""

from __future__ import annotations

import os
from pathlib import Path
import sys

SECURITY_HOOK_FILES = ("scan-secrets.py", "tool-guard.py")


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


def trusted_command(script: Path, shell: str = "native", executable: str | None = None) -> str:
    python = Path(executable or sys.executable)
    if not python.is_absolute() or (executable is None and not python.is_file()):
        raise ValueError("Trusted Python must be an absolute executable file")
    script_text = str(script.absolute())
    if shell == "windows" or (shell == "native" and os.name == "nt"):
        # cmd.exe metacharacters must remain inside quotes even without spaces.
        # Percent/delayed expansion cannot be made literal across host shells.
        if any(any(character in item for character in ('"', '%', '!', '\r', '\n')) for item in (str(python), script_text)):
            raise ValueError("Trusted hook paths contain unsupported Windows shell characters")
    return serialize_trusted_launch(str(python), script_text, shell, windows=os.name == "nt")


def is_trusted_pair(handler: dict, script: Path) -> bool:
    arguments = trusted_posix_arguments(handler.get("command", ""))
    if arguments is None or arguments[4] != str(script):
        return False
    try:
        return (handler.get("command") == trusted_command(script, "posix", arguments[0])
                and handler.get("commandWindows") == trusted_command(script, "windows", arguments[0]))
    except ValueError:
        return False


def pin_provider_commands(template: dict, provider: str, home: Path) -> None:
    for entries in template.get("hooks", {}).values():
        for entry in entries:
            for handler in ([entry] if provider == "copilot" else entry["hooks"]):
                for filename in SECURITY_HOOK_FILES:
                    keys = ("bash", "powershell") if provider == "copilot" else ("command",)
                    if not any(filename in handler.get(key, "") for key in keys):
                        continue
                    script = home / f".{provider}/hooks/scripts" / filename
                    for key in keys:
                        handler[key] = trusted_command(script, "powershell" if key == "powershell" else ("posix" if key == "bash" else "native"))

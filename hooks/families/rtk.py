"""Render the RTK forwarders with their explicit provider adapters."""

from __future__ import annotations

from hooks.manifest import GeneratedTarget
from hooks.providers import Provider


SHEBANG = "#!/usr/bin/env python3\n"
HEADER = "# Generated from hooks/families/rtk.py by scripts/generate-hooks.py. Do not edit.\n"
ADAPTER_START = "# BEGIN PROVIDER ADAPTER\n"
ADAPTER_END = "# END PROVIDER ADAPTER\n"
_TARGET_PATHS = {
    "copilot": ".copilot/hooks/scripts/rtk-hook-copilot.py",
    "gemini": ".gemini/hooks/scripts/rtk-hook-gemini.py",
}
_EXPLICIT_PATHS = {
    "copilot": ".copilot/hooks/scripts/rtk-explicit-copilot.py",
    "gemini": ".gemini/hooks/scripts/rtk-explicit-gemini.py",
    "codex": ".codex/hooks/rtk-explicit-codex.py",
}
_LAUNCHER_PATHS = {
    "copilot": ".copilot/hooks/scripts/rtk-agent-launcher.py",
    "gemini": ".gemini/hooks/scripts/rtk-agent-launcher.py",
    "codex": ".codex/hooks/rtk-agent-launcher.py",
}


_COPILOT_ADAPTER = r'''RTK_PROVIDER = "copilot"


def normalize_rewritten(rewritten: dict) -> dict:
    top_decision = rewritten.get("permissionDecision")
    if isinstance(top_decision, str) and top_decision.strip().lower() == "ask":
        audit_log_event(SCRIPT_NAME, "Overriding top-level 'ask' decision to 'allow' for silent execution")
        rewritten["permissionDecision"] = "allow"

    hook_out = rewritten.get("hookSpecificOutput")
    if isinstance(hook_out, dict):
        nested_decision = hook_out.get("permissionDecision")
        if isinstance(nested_decision, str) and nested_decision.strip().lower() == "ask":
            audit_log_event(SCRIPT_NAME, "Overriding nested hookSpecificOutput 'ask' decision to 'allow' for silent execution")
            hook_out["permissionDecision"] = "allow"

    return rewritten


'''


_GEMINI_ADAPTER = r'''RTK_PROVIDER = "gemini"


def normalize_rewritten(rewritten: dict) -> dict:
    return rewritten


'''


_RUNTIME_SOURCE = r'''from __future__ import annotations

import codecs
import io
import json
import os
import select
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.audit import audit_log_event
from helpers.common import emit_json, sanitize_log_field
from helpers.observability import begin_hook_capture


SCRIPT_NAME = Path(__file__).name
RTK_TIMEOUT_SECONDS = 1.0
INPUT_COMPLETION_IDLE_SECONDS = 0.5


def emit_noop() -> None:
    emit_json({})


def log_failure(reason: str) -> None:
    audit_log_event(SCRIPT_NAME, f"RTK rewrite fallback: {sanitize_log_field(reason)}")


def windows_pipe_bytes_available(file_descriptor: int) -> int | None:
    """Return queued pipe bytes, or None when the pipe is closed."""
    import ctypes
    import ctypes.wintypes
    import msvcrt

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.PeekNamedPipe.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.c_void_p,
        ctypes.wintypes.DWORD,
        ctypes.POINTER(ctypes.wintypes.DWORD),
        ctypes.POINTER(ctypes.wintypes.DWORD),
        ctypes.POINTER(ctypes.wintypes.DWORD),
    ]
    kernel32.PeekNamedPipe.restype = ctypes.wintypes.BOOL
    available = ctypes.wintypes.DWORD()
    handle = msvcrt.get_osfhandle(file_descriptor)
    if kernel32.PeekNamedPipe(handle, None, 0, None, ctypes.byref(available), None):
        return available.value
    return None


def wait_for_stdin(file_descriptor: int, timeout: float) -> bool:
    if os.name != "nt":
        return bool(select.select([file_descriptor], [], [], timeout)[0])

    deadline = time.monotonic() + timeout
    while True:
        available = windows_pipe_bytes_available(file_descriptor)
        if available is None or available:
            return True
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(remaining, 0.01))


def read_stdin_bytes(file_descriptor: int) -> bytes:
    if os.name == "nt":
        available = windows_pipe_bytes_available(file_descriptor)
        return os.read(file_descriptor, available or 1)
    return os.read(file_descriptor, io.DEFAULT_BUFFER_SIZE)


def read_hook_input() -> tuple[bytes | None, dict | None, str | None]:
    file_descriptor = sys.stdin.fileno()
    raw_input = bytearray()
    decoded_input = ""
    utf8_decoder = codecs.getincrementaldecoder("utf-8")()
    json_decoder = json.JSONDecoder()
    idle_deadline = time.monotonic() + INPUT_COMPLETION_IDLE_SECONDS

    while True:
        timeout = max(0.0, idle_deadline - time.monotonic())
        if not wait_for_stdin(file_descriptor, timeout):
            return None, None, "invalid hook input JSON"

        try:
            chunk = read_stdin_bytes(file_descriptor)
        except OSError:
            return None, None, "invalid hook input JSON"

        if not chunk:
            return None, None, "invalid hook input JSON"

        raw_input.extend(chunk)
        try:
            decoded_input += utf8_decoder.decode(chunk, final=False)
        except UnicodeDecodeError:
            return None, None, "invalid hook input JSON"

        try:
            start = len(decoded_input) - len(decoded_input.lstrip())
            payload, end = json_decoder.raw_decode(decoded_input, start)
        except json.JSONDecodeError:
            idle_deadline = time.monotonic() + INPUT_COMPLETION_IDLE_SECONDS
            continue

        if not isinstance(payload, dict):
            return None, None, "invalid hook input JSON"

        while wait_for_stdin(file_descriptor, 0.0):
            try:
                buffered = read_stdin_bytes(file_descriptor)
            except OSError:
                return None, None, "invalid hook input JSON"
            if not buffered:
                break
            raw_input.extend(buffered)
            try:
                decoded_input += utf8_decoder.decode(buffered, final=False)
            except UnicodeDecodeError:
                return None, None, "invalid hook input JSON"

        trailing_input = decoded_input[end:]
        if utf8_decoder.getstate()[0] or (trailing_input and not trailing_input.isspace()):
            return None, None, "invalid hook input JSON"
        return bytes(raw_input), payload, None


def forward_to_rtk(raw_input: bytes) -> tuple[dict | None, str | None]:
    rtk_bin = shutil.which("rtk") or "rtk"

    try:
        result = subprocess.run(
            [rtk_bin, "hook", RTK_PROVIDER],
            input=raw_input,
            capture_output=True,
            shell=False,
            timeout=RTK_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return None, "rtk command not found"
    except subprocess.TimeoutExpired:
        return None, f"rtk hook {RTK_PROVIDER} timed out after {RTK_TIMEOUT_SECONDS:.1f}s"
    except Exception as exc:  # noqa: BLE001 - safe fallback path
        return None, f"rtk hook invocation failed: {exc}"

    if result.returncode != 0:
        return None, f"rtk exited {result.returncode}"

    stdout_stripped = (result.stdout or b"").strip()
    if not stdout_stripped:
        return {}, None

    try:
        rewritten = json.loads(stdout_stripped.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "rtk returned invalid JSON"

    if not isinstance(rewritten, dict):
        return None, "rtk returned non-object JSON"

    return normalize_rewritten(rewritten), None


def main() -> int:
    raw_input, payload, input_failure = read_hook_input()
    begin_hook_capture(payload or {})

    if input_failure is not None or raw_input is None:
        log_failure(input_failure or "invalid hook input JSON")
        emit_noop()
        return 0

    rewritten, failure_reason = forward_to_rtk(raw_input)
    if failure_reason is not None:
        log_failure(failure_reason)
        emit_noop()
        return 0

    emit_json(rewritten)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _adapter_source(provider: Provider) -> str:
    if provider.name == "copilot":
        return _COPILOT_ADAPTER
    if provider.name == "gemini":
        return _GEMINI_ADAPTER
    raise ValueError(f"Unsupported RTK provider: {provider.name}")


def render(provider: Provider, target: GeneratedTarget) -> str:
    """Render one self-contained RTK provider forwarder."""
    if target.family == "rtk" and target.provider == provider.name:
        if target.output_path.as_posix() == _EXPLICIT_PATHS.get(provider.name):
            return SHEBANG + HEADER + _EXPLICIT_SOURCE.replace(
                "PROVIDER_NAME", provider.name
            ).replace("RTK_VERIFICATION_SOURCE", _VERIFICATION_SOURCE.rstrip("\n"))
        if target.output_path.as_posix() == _LAUNCHER_PATHS.get(provider.name):
            return SHEBANG + HEADER + _LAUNCHER_SOURCE.replace(
                "RTK_VERIFICATION_SOURCE", _VERIFICATION_SOURCE.rstrip("\n")
            )
    if (
        target.family != "rtk"
        or target.provider != provider.name
        or target.output_path.as_posix() != _TARGET_PATHS.get(provider.name)
    ):
        raise ValueError(f"Unsupported RTK target/provider: {target.output_path}")
    future_import, runtime_body = _RUNTIME_SOURCE.split("\n", 1)
    return (
        SHEBANG
        + HEADER
        + future_import
        + "\n"
        + ADAPTER_START
        + _adapter_source(provider)
        + ADAPTER_END
        + runtime_body
    )


_VERIFICATION_SOURCE = r'''APPROVED_ASSET_DIGESTS = {
    "05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321",
    "10345f57214b2f9a14f3de1ae1f4235f6eef0669dfed9ab1758a94601b7b829a",
    "4993afdf43a93d09dcce1bef0b0167464f96aa9e973fa5644ca244604a1846b8",
    "bf8a1d0e44afb28db9e88859e1f7668c56ecd074264f0c36637c4e07a0c2f1db",
    "636262ec8341455c09a3826329f90c92a57e2ef64d8761511eb123f1b84642d7",
}


def verified(binary: Path) -> bool:
    try:
        receipt = json.loads((binary.parent / "receipt.json").read_text(encoding="utf-8"))
        return (receipt.get("tag") == "dev-0.50.0-rc.451"
                and receipt.get("asset_sha256") in APPROVED_ASSET_DIGESTS
                and hashlib.sha256(binary.read_bytes()).hexdigest() == receipt.get("binary_sha256"))
    except (OSError, ValueError):
        return False
'''


_LAUNCHER_SOURCE = r'''"""Launch the verified side-by-side RTK with child-only warning suppression."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


RTK_VERIFICATION_SOURCE


def main() -> int:
    binary = Path.home() / ".agents/rtk/dev-0.50.0-rc.451" / ("rtk.exe" if os.name == "nt" else "rtk")
    if not binary.is_file() or not verified(binary):
        print("Verified RTK prerelease is not installed", file=sys.stderr)
        return 127
    environment = os.environ.copy()
    environment["RTK_SUPPRESS_HOOK_WARNING"] = "1"
    try:
        return subprocess.call([str(binary), *sys.argv[1:]], env=environment)
    except OSError as error:
        print(f"Unable to start verified RTK prerelease: {error}", file=sys.stderr)
        return 127


if __name__ == "__main__":
    raise SystemExit(main())
'''


_EXPLICIT_SOURCE = r'''"""Rewrite explicit RTK shell invocations only when a verified prerelease is installed."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from helpers.common import emit_json, read_json_input

PROVIDER = "PROVIDER_NAME"
RTK_VERIFICATION_SOURCE


def split_segments(command: str, powershell: bool) -> list[tuple[int, int]] | None:
    if "`" in command or "$(" in command or "\n" in command or "\r" in command:
        return None
    segments = []
    quote = None
    escaped = False
    start = 0
    index = 0
    while index < len(command):
        char = command[index]
        if escaped:
            escaped = False
        elif char == "\\" and quote != "'":
            escaped = True
        elif quote:
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char in ";&|":
            if command.startswith("&&", index) or command.startswith("||", index):
                segments.append((start, index))
                index += 1
                start = index + 1
            elif char == ";":
                segments.append((start, index))
                start = index + 1
            elif powershell and char == "&" and not command[start:index].strip():
                pass
            else:
                return None
        index += 1
    if quote or escaped:
        return None
    segments.append((start, len(command)))
    return segments


def command_token(command: str, start: int, end: int, powershell: bool) -> tuple[int, int, str, bool] | None:
    while start < end and command[start].isspace():
        start += 1
    called = False
    if powershell and command[start:start + 1] == "&":
        called = True
        start += 1
        while start < end and command[start].isspace():
            start += 1
    if start >= end:
        return None
    token_start = start
    quote = None
    escaped = False
    while start < end:
        char = command[start]
        if escaped:
            escaped = False
        elif char == "\\" and not powershell and quote != "'":
            escaped = True
        elif quote:
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char.isspace():
            break
        start += 1
    token = command[token_start:start]
    if token.startswith(("'", '"')) and token[-1:] == token[:1]:
        token = token[1:-1]
    return token_start, start, token, called


def rewrite(command: str, powershell: bool) -> str | None:
    segments = split_segments(command, powershell)
    if segments is None:
        return None
    launcher = SCRIPT_DIR / "rtk-agent-launcher.py"
    if powershell:
        quoted = "'" + str(launcher).replace("'", "''") + "'"
        replacement = f"python {quoted}"
    else:
        import shlex
        replacement = "python3 " + shlex.quote(str(launcher))
    changes = []
    for start, end in segments:
        found = command_token(command, start, end, powershell)
        if found is None:
            continue
        token_start, token_end, token, called = found
        basename = re.split(r"[/\\]", token)[-1]
        if basename != "rtk" and not (powershell and basename.lower() == "rtk.exe"):
            continue
        changes.append((token_start, token_end, ("" if called or not powershell else "& ") + replacement))
    if not changes:
        return None
    for start, end, replacement in reversed(changes):
        command = command[:start] + replacement + command[end:]
    return command


def main() -> int:
    try:
        payload = read_json_input()
        if PROVIDER == "copilot":
            tool = payload.get("toolName") or payload.get("tool_name")
            args = payload.get("toolArgs") if "toolArgs" in payload else payload.get("tool_input")
            if isinstance(args, str):
                args = json.loads(args)
            powershell = tool == "powershell" or (tool == "Bash" and os.name == "nt")
            supported = tool in ("bash", "powershell", "Bash")
        else:
            tool = payload.get("tool_name")
            args = payload.get("tool_input")
            powershell = os.name == "nt"
            supported = tool == ("run_shell_command" if PROVIDER == "gemini" else "Bash")
        if not supported or not isinstance(args, dict) or not isinstance(args.get("command"), str):
            emit_json({})
            return 0
        binary = Path.home() / ".agents/rtk/dev-0.50.0-rc.451" / ("rtk.exe" if powershell else "rtk")
        if not binary.is_file() or not verified(binary):
            emit_json({})
            return 0
        updated = rewrite(args["command"], powershell)
        if updated is None:
            emit_json({})
            return 0
        new_args = args | {"command": updated}
        if PROVIDER == "copilot" and "toolArgs" in payload:
            output = {"modifiedArgs": new_args}
        elif PROVIDER == "gemini":
            output = {"hookSpecificOutput": {"tool_input": new_args}}
        else:
            output = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", "updatedInput": new_args}}
        emit_json(output)
    except Exception:
        emit_json({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

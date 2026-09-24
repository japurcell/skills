#!/usr/bin/env python3
"""Temporarily measure installed provider hook delivery with owner-only evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import sys
import tempfile
import uuid


EVENTS = {
    "codex": {"cli": ("PreToolUse", "Stop")},
    "gemini": {"cli": ("BeforeTool", "AfterTool", "AfterAgent")},
    "copilot": {
        "cli": ("preToolUse", "postToolUse", "agentStop"),
        "vscode": ("PreToolUse", "PostToolUse", "Stop"),
    },
}
CONFIG_PATHS = {
    "codex": Path(".codex/hooks.json"),
    "gemini": Path(".gemini/settings.json"),
    "copilot": Path(".copilot/hooks/hooks.json"),
}
PROBE_PREFIX = "ready-ideas-hook-"
ID_PATTERN = re.compile(r"[0-9a-f]{32}\Z")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="action", required=True)
    for action in ("prepare", "verify", "cleanup"):
        command = commands.add_parser(action)
        command.add_argument("--provider", required=True, choices=EVENTS)
        if action == "prepare":
            command.add_argument("--surface", choices=("cli", "vscode"), default="cli")
            command.add_argument("--mode", choices=("normal", "timeout"), default="normal")
            command.add_argument("--timeout-seconds", type=int, default=1)
            command.add_argument("--delay-seconds", type=int, default=3)
        else:
            command.add_argument("--id", required=True)
        if action == "verify":
            command.add_argument("--transcript", required=True, type=Path)
            command.add_argument("--mode", choices=("normal", "timeout"), default="normal")
    return result


def probe_dir(identifier: str) -> Path:
    if not ID_PATTERN.fullmatch(identifier):
        raise ValueError("Invalid probe ID")
    return Path(tempfile.gettempdir()) / f"{PROBE_PREFIX}{identifier}"


def check_regular_path(path: Path) -> None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return
    if not stat.S_ISREG(mode):
        raise ValueError(f"Refusing linked or non-file hook settings: {path}")


def write_private(path: Path, content: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def replace_file(path: Path, content: bytes, mode: int = 0o600) -> None:
    check_regular_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def command_for(provider: str, surface: str, event: str, handler: Path) -> dict[str, str]:
    posix = f"python3 {shlex.quote(str(handler))} {event}"
    windows = f'py -3 "{handler}" {event}'
    if provider == "codex":
        return {"command": posix, "commandWindows": windows}
    if provider == "copilot" and surface == "vscode":
        return {"command": posix, "windows": windows}
    if provider == "copilot":
        return {"bash": posix, "powershell": windows}
    return {"command": posix}


def probe_handler(provider: str, surface: str, event: str, handler: Path, timeout: int) -> dict:
    command = command_for(provider, surface, event, handler)
    if provider == "copilot" and surface == "vscode":
        return {"type": "command", **command, "timeout": timeout}
    if provider == "copilot":
        return {"type": "command", **command, "timeoutSec": timeout}
    if provider == "gemini":
        return {"name": f"ready-ideas-probe-{handler.parent.name}-{event}", "type": "command",
                **command, "timeout": timeout * 1000}
    return {"type": "command", **command, "timeout": timeout}


def add_handlers(config: dict, provider: str, surface: str,
                 events: tuple[str, ...], handler: Path, timeout: int) -> dict:
    hooks = config.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("Existing hooks must be an object")
    if provider == "copilot":
        if config.get("disableAllHooks") is True:
            raise ValueError("Copilot hooks are disabled; trust/settings were not changed")
        config.setdefault("version", 1)
    for event in events:
        groups = hooks.setdefault(event, [])
        if not isinstance(groups, list):
            raise ValueError(f"Existing hooks.{event} must be a list")
        entry = probe_handler(provider, surface, event, handler, timeout)
        if provider == "copilot":
            groups.append(entry)
        else:
            group = {"hooks": [entry]}
            if event in {"BeforeTool", "AfterTool"}:
                group["matcher"] = "run_shell_command"
            groups.append(group)
    return config


def handler_source() -> bytes:
    source = r'''#!/usr/bin/env python3
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import time
import uuid

directory = Path(__file__).resolve().parent
state = json.loads((directory / "state.json").read_text(encoding="utf-8"))
event = sys.argv[1]
if event not in state["events"]:
    raise SystemExit(1)
buffer = bytearray()
payload = None
while len(buffer) < 1_048_576:
    chunk = os.read(0, 65536)
    if not chunk:
        break
    buffer.extend(chunk)
    try:
        payload = json.loads(buffer.decode("utf-8"))
        break
    except (UnicodeDecodeError, json.JSONDecodeError):
        continue
if not isinstance(payload, dict):
    raise SystemExit(1)
provider = state["provider"]
surface = state["surface"]
if provider == "copilot" and surface == "cli":
    required = {"sessionId", "cwd"}
    if event in {"preToolUse", "postToolUse"}:
        required.update({"toolName", "toolArgs"})
    if event == "postToolUse":
        required.add("toolResult")
else:
    required = {"hook_event_name"} if provider == "copilot" else {"session_id", "cwd", "hook_event_name"}
    if event in {"PreToolUse", "PostToolUse", "BeforeTool", "AfterTool"}:
        required.update({"tool_name", "tool_input"})
    if event == "AfterTool":
        required.add("tool_response")
    if event in {"Stop", "AfterAgent"}:
        required.add("stop_hook_active")
    if event == "AfterAgent":
        required.add("prompt_response")
missing = sorted(required - payload.keys())
token = f"READY_IDEAS_HOOK_{state['nonce']}_{event}"
response = {} if provider == "copilot" and surface == "cli" else {"systemMessage": token}
if provider == "copilot" and event in {"postToolUse", "PostToolUse"}:
    response["additionalContext"] = token
if provider == "copilot" and event in {"agentStop", "Stop"}:
    response["decision"] = "allow"

def append(name, record):
    path = directory / name
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as output:
        output.write(json.dumps(record, separators=(",", ":")) + "\n")
        output.flush()
        os.fsync(output.fileno())

invocation_id = str(payload.get("tool_use_id") or payload.get("toolUseId") or uuid.uuid4().hex)
append("marker.jsonl", {"provider": provider, "event": event, "invocation_id": invocation_id,
                        "missing_keys": missing, "response_keys": sorted(response)})
if state["mode"] == "timeout":
    time.sleep(state["delay_seconds"])
if provider == "copilot" and surface == "cli":
    sys.stdout.write(json.dumps({"type": "progress", "message": token}, separators=(",", ":")) + "\n")
    sys.stdout.flush()
sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
sys.stdout.flush()
append("completed.jsonl", {"event": event, "invocation_id": invocation_id})
'''
    return source.encode("utf-8")


def prepare(args: argparse.Namespace) -> int:
    if args.surface not in EVENTS[args.provider]:
        raise ValueError(f"{args.provider} does not have a {args.surface} probe surface")
    if args.timeout_seconds < 1 or args.delay_seconds < 1:
        raise ValueError("Probe timing must be positive whole seconds")
    if args.mode == "timeout" and args.delay_seconds <= args.timeout_seconds:
        raise ValueError("Probe delay must exceed its hook timeout")
    codex_home = os.environ.get("CODEX_HOME")
    config_path = (Path(codex_home) / "hooks.json" if args.provider == "codex" and codex_home
                   else Path.home() / CONFIG_PATHS[args.provider])
    if config_path.parent.is_symlink():
        raise ValueError(f"Refusing linked settings directory: {config_path.parent}")
    check_regular_path(config_path)
    original_exists = config_path.exists()
    original = config_path.read_bytes() if original_exists else b""
    original_mode = stat.S_IMODE(config_path.stat().st_mode) if original_exists else 0o600
    config = json.loads(original.decode("utf-8")) if original_exists else {}
    if not isinstance(config, dict):
        raise ValueError("Hook settings must be a JSON object")
    identifier = uuid.uuid4().hex
    directory = probe_dir(identifier)
    directory.mkdir(mode=0o700)
    events = EVENTS[args.provider][args.surface]
    handler = directory / "handler.py"
    marker = directory / "marker.jsonl"
    transcript = directory / "transcript.txt"
    try:
        write_private(directory / "backup", original)
        write_private(handler, handler_source())
        write_private(marker, b"")
        write_private(directory / "completed.jsonl", b"")
        write_private(transcript, b"")
        state = {
            "id": identifier, "provider": args.provider, "surface": args.surface, "mode": args.mode,
            "events": events, "nonce": uuid.uuid4().hex, "config": str(config_path),
            "delay_seconds": args.delay_seconds,
            "original_exists": original_exists, "original_mode": original_mode,
            "before_hash": digest(original),
        }
        add_handlers(config, args.provider, args.surface, events, handler,
                     args.timeout_seconds if args.mode == "timeout" else 10)
        installed = (json.dumps(config, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        state["after_hash"] = digest(installed)
        write_private(directory / "state.json", json.dumps(state).encode("utf-8"))
        replace_file(config_path, installed)
    except BaseException:
        if state.get("after_hash") and config_path.exists() and digest(config_path.read_bytes()) == state["after_hash"]:
            print(f"Settings changed; recover with cleanup --provider {args.provider} --id {identifier}",
                  file=sys.stderr)
        else:
            shutil.rmtree(directory)
        raise
    try:
        print(json.dumps({"id": identifier, "config": str(config_path), "backup": str(directory / "backup"),
                          "marker": str(marker), "handler": str(handler), "transcript": str(transcript)}),
              flush=True)
    except OSError:
        print(f"Settings changed; recover with cleanup --provider {args.provider} --id {identifier}",
              file=sys.stderr)
        return 1
    return 0


def load_state(provider: str, identifier: str) -> tuple[Path, dict]:
    directory = probe_dir(identifier)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Probe state directory is missing or linked")
    state = json.loads((directory / "state.json").read_text(encoding="utf-8"))
    if state.get("id") != identifier or state.get("provider") != provider:
        raise ValueError("Probe ID/provider mismatch")
    return directory, state


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def verify(args: argparse.Namespace) -> int:
    directory, state = load_state(args.provider, args.id)
    if args.mode != state["mode"]:
        raise ValueError("Verify mode does not match prepared probe")
    transcript = args.transcript.resolve()
    if transcript != (directory / "transcript.txt").resolve():
        raise ValueError("Transcript must be the exact probe-owned path")
    output = transcript.read_text(encoding="utf-8", errors="replace")
    markers = read_jsonl(directory / "marker.jsonl")
    completed = read_jsonl(directory / "completed.jsonl")
    for event in state["events"]:
        entries = [entry for entry in markers if entry.get("provider") == args.provider and entry.get("event") == event]
        if not entries:
            raise ValueError(f"No invocation marker for {event}")
        if any(entry.get("missing_keys") for entry in entries):
            raise ValueError(f"Unexpected payload keys for {event}")
        if not (args.provider == "copilot" and state["surface"] == "cli") and any(
            "systemMessage" not in entry.get("response_keys", []) for entry in entries
        ):
            raise ValueError(f"Invalid response shape for {event}")
        token = f"READY_IDEAS_HOOK_{state['nonce']}_{event}"
        event_completions = [entry for entry in completed if entry.get("event") == event]
        if args.mode == "normal":
            if not event_completions or token not in output:
                raise ValueError(f"No completed visible response for {event}")
        elif event_completions or token in output:
            raise ValueError(f"Timeout probe completed unexpectedly for {event}")
    if args.mode == "timeout" and not re.search(r"timed? ?out|timeout", output, re.IGNORECASE):
        raise ValueError("Provider timeout indication was absent")
    print(f"PASS: {args.provider} {state['surface']} {args.mode} hook delivery")
    return 0


def remove_owned_handlers(config: dict, original: dict, provider: str, surface: str,
                          events: tuple[str, ...], handler: Path) -> dict:
    hooks = config.get("hooks")
    if not isinstance(hooks, dict):
        raise ValueError("Current hooks are not an object; manual restoration required")
    original_hooks = original.get("hooks", {})
    for event in events:
        groups = hooks.get(event)
        if not isinstance(groups, list):
            continue
        owned = command_for(provider, surface, event, handler)
        if provider == "copilot":
            hooks[event] = [entry for entry in groups if not (
                isinstance(entry, dict) and all(entry.get(key) == value for key, value in owned.items())
            )]
        else:
            kept = []
            for group in groups:
                if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                    kept.append(group)
                    continue
                entries = [entry for entry in group["hooks"] if not (
                    isinstance(entry, dict) and all(entry.get(key) == value for key, value in owned.items())
                )]
                if entries:
                    group["hooks"] = entries
                    kept.append(group)
            hooks[event] = kept
        if not hooks[event] and event not in original_hooks:
            del hooks[event]
    if provider == "copilot" and "version" not in original and config.get("version") == 1:
        del config["version"]
    if not hooks and "hooks" not in original:
        del config["hooks"]
    return config


def cleanup(args: argparse.Namespace) -> int:
    directory, state = load_state(args.provider, args.id)
    config_path = Path(state["config"])
    check_regular_path(config_path)
    current_exists = config_path.exists()
    current = config_path.read_bytes() if current_exists else b""
    original = (directory / "backup").read_bytes()
    if digest(original) != state["before_hash"]:
        raise ValueError("Probe backup changed; refusing restoration")
    if current_exists and digest(current) == state["after_hash"]:
        if state["original_exists"]:
            replace_file(config_path, original, state["original_mode"])
        else:
            config_path.unlink()
    elif current_exists:
        config = json.loads(current.decode("utf-8"))
        if not isinstance(config, dict):
            raise ValueError("Current settings are malformed; manual restoration required")
        original_config = json.loads(original.decode("utf-8")) if state["original_exists"] else {}
        remove_owned_handlers(config, original_config, args.provider, state["surface"],
                              tuple(state["events"]), directory / "handler.py")
        replace_file(config_path, (json.dumps(config, indent=2, ensure_ascii=False) + "\n").encode())
    elif state["original_exists"]:
        raise ValueError("Original settings disappeared; manual restoration required")
    for name in ("backup", "handler.py", "marker.jsonl", "completed.jsonl", "transcript.txt", "state.json"):
        (directory / name).unlink(missing_ok=True)
    directory.rmdir()
    print(f"Cleaned probe {args.id}")
    return 0


def main() -> int:
    args = parser().parse_args()
    try:
        return {"prepare": prepare, "verify": verify, "cleanup": cleanup}[args.action](args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"probe-provider-hook-delivery: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# Generated from hooks/families/agent_brain.py by scripts/generate-hooks.py. Do not edit.
PROVIDER = 'gemini'

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import select
import signal
import stat
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ADAPTER_VERSION = "native-1"
MAX_BYTES = 1024 * 1024
DEADLINE = float("inf")


def tick():
    if time.monotonic() >= DEADLINE:
        raise TimeoutError()


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def finite(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite number")
    return number


def constant(value):
    raise ValueError("nonfinite number")


DECODER = json.JSONDecoder(object_pairs_hook=pairs, parse_float=finite, parse_constant=constant)


def decode(raw):
    value = DECODER.decode(raw.decode("utf-8", errors="strict"))
    if not isinstance(value, dict):
        raise ValueError("object required")
    return value


def ready(fd, wait):
    if os.name != "nt":
        return bool(select.select([fd], [], [], max(0, wait))[0])
    import ctypes
    import msvcrt
    end = time.monotonic() + max(0, wait)
    handle = ctypes.c_void_p(msvcrt.get_osfhandle(fd))
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    while True:
        available = ctypes.c_ulong()
        if not kernel.PeekNamedPipe(handle, None, 0, None, ctypes.byref(available), None):
            return True
        if available.value:
            return True
        if time.monotonic() >= end:
            return False
        time.sleep(min(0.005, max(0, end - time.monotonic())))


def read_input(deadline):
    raw = b""
    fd = sys.stdin.fileno()
    while time.monotonic() < deadline:
        if not ready(fd, min(0.25, deadline - time.monotonic())):
            continue
        chunk = os.read(fd, 65536)
        raw += chunk
        if len(raw) > MAX_BYTES:
            raise ValueError("oversized input")
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            if error.reason == "unexpected end of data" and chunk:
                continue
            raise
        try:
            value, end = DECODER.raw_decode(text.lstrip())
        except json.JSONDecodeError:
            if chunk:
                continue
            raise ValueError("incomplete input") from None
        if not isinstance(value, dict):
            raise ValueError("object required")
        if text.lstrip()[end:].strip():
            raise ValueError("trailing input")
        # Drain data already available, without waiting for pipe EOF. A bounded
        # quiet window also rejects immediately arriving trailing fragments.
        while ready(fd, min(0.01, max(0, deadline - time.monotonic()))):
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            raw += chunk
            if len(raw) > MAX_BYTES:
                raise ValueError("oversized input")
            decode(raw)
        return decode(raw)
    raise TimeoutError()


def local(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("invalid local path")
    path = root
    for part in Path(relative).parts:
        tick()
        path /= part
        info = path.lstat()
        if path.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400 or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
            raise ValueError("linked path")
    return path


def read_file(path):
    tick()
    if not stat.S_ISREG(path.lstat().st_mode) or path.stat().st_size > MAX_BYTES:
        raise ValueError("invalid pinned file")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    tick()
    if len(raw) > MAX_BYTES:
        raise ValueError("oversized pinned file")
    return raw


def sha(path):
    return hashlib.sha256(read_file(path)).hexdigest()


def bundle_revision(path):
    scripts = local(path, "scripts")
    inventory = []
    for item in scripts.rglob("*"):
        tick()
        if len(inventory) >= 2000:
            raise ValueError("oversized runnable inventory")
        local(path, item.relative_to(path).as_posix())
        inventory.append(item)
    files = []
    for item in sorted(inventory):
        relative = item.relative_to(path).as_posix()
        if item.is_file() and item.suffix == ".py":
            files.append((relative, sha(item)))
    return hashlib.sha256(json.dumps(files, separators=(",", ":")).encode()).hexdigest()


def registration(root, path):
    global DEADLINE
    record = decode(read_file(local(root, path)))
    if set(record) != {"schema_version", "integration_id", "config_path", "bundle_path", "provider", "provider_version", "entry_mode"} or type(record["schema_version"]) is not int or record["schema_version"] != 1:
        raise ValueError("invalid registration")
    config = decode(read_file(local(root, record["config_path"])))
    provider = config["providers"][record["integration_id"]]
    if provider["enabled"] is not True or provider["kind"] != "native" or provider["adapter_version"] != ADAPTER_VERSION:
        raise ValueError("disabled registration")
    support = decode(read_file(local(root, provider["support_record"])))
    seconds = support["native_deadline_seconds"]
    if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0.1:
        raise ValueError("invalid deadline")
    DEADLINE = min(DEADLINE, STARTED + seconds * 0.8)
    if os.name != "nt":
        signal.setitimer(signal.ITIMER_REAL, max(0.001, DEADLINE - time.monotonic()))
    for key in ("bundle_path", "provider", "provider_version", "entry_mode"):
        if support[key] != record[key]:
            raise ValueError("unmatched binding")
    if record["provider"] != PROVIDER or support["adapter_revision"] != sha(Path(__file__)):
        raise ValueError("unmatched adapter")
    bundle = local(root, record["bundle_path"])
    if bundle_revision(bundle) != support["bundle_revision"]:
        raise ValueError("unmatched bundle")
    return record, support, bundle


def failure(event, code, payload=None):
    reason = "agent-brain: " + code
    if PROVIDER == "codex":
        if event == "PreToolUse":
            return {"hookSpecificOutput": {"hookEventName": event, "permissionDecision": "deny", "permissionDecisionReason": reason}}
        if event in ("Stop", "SubagentStop", "UserPromptSubmit", "PreCompact"):
            return {"decision": "block", "reason": reason}
        return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": reason + ". This path is unsupported; restore configured foreground context before dependent work."}}
    if PROVIDER == "copilot":
        if event == "preToolUse":
            return {"permissionDecision": "deny", "permissionDecisionReason": reason}
        if event in ("agentStop", "subagentStop"):
            return {"decision": "block", "reason": reason}
        if event == "userPromptTransformed":
            original = (payload or {}).get("transformedPrompt", "")
            return {"modifiedTransformedPrompt": (original if isinstance(original, str) else "") + "\n\n" + reason + ". This path is unsupported; restore foreground context."}
        if event in ("sessionStart", "subagentStart"):
            return {"additionalContext": reason + ". This path is unsupported; restore foreground context."}
        return {}
    if event in ("BeforeAgent", "BeforeTool", "BeforeModel", "AfterAgent"):
        return {"decision": "deny", "reason": reason}
    if event == "PreCompress":
        return {"systemMessage": reason + ". Compression is advisory; restore at the validated next boundary."}
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": reason + ". This path is unsupported; restore foreground context."}}


def child(bundle, record, payload, deadline, action):
    # File capture has no descendant-held pipe EOF dependency and has an output
    # size bound. The entire process group is cleaned up on timeout on POSIX.
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as source:
        source.write(json.dumps({"registration": record, "payload": payload}, ensure_ascii=False).encode("utf-8"))
        source.seek(0)
        process = subprocess.Popen([sys.executable, str(bundle / "scripts/native-integration.py"), action],
            stdin=source, stdout=output, stderr=subprocess.DEVNULL, start_new_session=os.name != "nt")
        try:
            while process.poll() is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or os.fstat(output.fileno()).st_size > MAX_BYTES:
                    raise TimeoutError()
                try:
                    process.wait(timeout=min(0.02, remaining))
                except subprocess.TimeoutExpired:
                    pass
            if os.fstat(output.fileno()).st_size > MAX_BYTES:
                raise ValueError("oversized output")
            output.seek(0)
            result = decode(output.read(MAX_BYTES + 1))
            if process.returncode != 0:
                raise ValueError("core incomplete")
            return result
        finally:
            if os.name != "nt":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            elif process.poll() is None:
                process.kill()
            process.wait(timeout=0.1)


def main():
    global DEADLINE, STARTED
    started = time.monotonic()
    STARTED = started
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--registration", default=".agents/context/native-registration.json")
    parser.add_argument("--event", required=True)
    args = parser.parse_args()
    event = args.event
    emitted = False
    payload = None
    deadline = started + 3.8  # four seconds includes interpreter/cleanup reserve
    DEADLINE = deadline
    if os.name != "nt":
        def expired(signum, frame):
            raise TimeoutError()
        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, max(0.001, deadline - time.monotonic()))
    try:
        try:
            record, support, bundle = registration(Path.cwd().resolve(), args.registration)
        except (OSError, ValueError, TypeError, KeyError):
            if event == "userPromptTransformed":
                payload = read_input(deadline)
            raise
        seconds = support["native_deadline_seconds"]
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0.1:
            raise ValueError("invalid deadline")
        deadline = min(deadline, started + seconds * 0.8)
        DEADLINE = deadline
        if os.name != "nt":
            signal.setitimer(signal.ITIMER_REAL, max(0.001, deadline - time.monotonic()))
        payload = read_input(deadline)
        observed = payload.get("hook_event_name", payload.get("hookEventName", event))
        if observed != event:
            raise ValueError("unmatched event")
        payload["_native_event"] = event
        result = child(bundle, record, payload, deadline, "callback")
        emitted = True
        emit(result["envelope"], deadline)
        if result.get("settlement"):
            child(bundle, record, result["settlement"], deadline, "settle")
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError, TimeoutError, subprocess.SubprocessError) as error:
        # A readiness timeout can precede the alarm by a fraction of a second.
        # Reserve bounded output time without that alarm interrupting denial.
        if os.name != "nt":
            signal.setitimer(signal.ITIMER_REAL, 0)
        code = "INTERNAL_WATCHDOG_INCOMPLETE" if isinstance(error, TimeoutError) or time.monotonic() >= deadline else "NATIVE_UNSUPPORTED"
        print("agent-brain adapter: " + code + "; native consumption and provider timeout behavior remain unverified.", file=sys.stderr)
        if not emitted:
            emit(failure(event, code, payload), time.monotonic() + 0.05)
        return 0
    finally:
        if os.name != "nt":
            signal.setitimer(signal.ITIMER_REAL, 0)


def emit(value, deadline):
    """Bound final stdout work; partial or unavailable output never settles."""
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise ValueError("oversized envelope")
    fd = sys.stdout.fileno()
    if os.name == "nt":
        # Native Windows output cancellation still needs build certification.
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return
    was_blocking = os.get_blocking(fd)
    os.set_blocking(fd, False)
    try:
        while raw:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError()
            if not select.select([], [fd], [], min(0.02, remaining))[1]:
                continue
            try:
                raw = raw[os.write(fd, raw):]
            except BlockingIOError:
                continue
    finally:
        os.set_blocking(fd, was_blocking)


if __name__ == "__main__":
    raise SystemExit(main())

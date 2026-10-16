#!/usr/bin/env python3
# Generated from hooks/families/scan_status.py by scripts/generate-hooks.py. Do not edit.

from __future__ import annotations

PROVIDER = 'copilot'

import json
import os
from pathlib import Path
import re
import select
import signal
import subprocess
import sys
import tempfile
import time

# Reserve time for startup, unconditional child cleanup and native output.
STARTED = time.monotonic()
INPUT_SECONDS = 0.12
CHILD_SECONDS = 0.70
CLEANUP_SECONDS = 0.10
MAX_INPUT = 65536
MAX_OUTPUT = 65536
UNAVAILABLE = "unavailable; saved scope/time unavailable"


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError
        value[key] = item
    return value


def read_input():
    # Native Windows has no contained status child yet. Never start one there.
    if os.name != "posix":
        return None
    raw = bytearray()
    deadline = min(STARTED + INPUT_SECONDS, time.monotonic() + INPUT_SECONDS)
    fd = sys.stdin.fileno()
    while time.monotonic() < deadline:
        ready, _, _ = select.select([fd], [], [], max(0, deadline - time.monotonic()))
        if not ready:
            return None
        chunk = os.read(fd, min(4096, MAX_INPUT + 1 - len(raw)))
        raw.extend(chunk)
        if len(raw) > MAX_INPUT:
            return None
        try:
            text = raw.decode("utf-8")
            decoder = json.JSONDecoder(object_pairs_hook=unique_object)
            value, end = decoder.raw_decode(text.lstrip())
            if text.lstrip()[end:].strip():
                return None
            # Drain bytes already delivered before accepting an open pipe.
            if select.select([fd], [], [], 0)[0] and chunk:
                continue
            return value if type(value) is dict else None
        except (ValueError, UnicodeError):
            if not chunk:
                return None
    return None


def entrypoint():
    # Same fixed default bundle location as install-scan-secrets.platform_roots.
    # No environment command override or executable lookup is accepted.
    return Path.home() / ".local/lib/scan-secrets/scripts/scan-secrets.py"


# The isolated bridge sets the kernel output limit after exec, then replaces
# itself with the exact neutral CLI in the same private process group. Python
# never runs in a multithreaded parent's fork/exec gap.
CHILD_BRIDGE = """import os,resource,sys
_,hard=resource.getrlimit(resource.RLIMIT_FSIZE)
limit=65536 if hard==resource.RLIM_INFINITY else min(65536,hard)
resource.setrlimit(resource.RLIMIT_FSIZE,(limit,limit))
os.execv(sys.executable,[sys.executable,'-I','-S','-B',*sys.argv[1:]])
"""


def child_status(repo):
    if os.name != "posix":
        return None
    process = None
    deadline = STARTED + CHILD_SECONDS
    with tempfile.TemporaryFile(mode="w+b") as output:
        try:
            process = subprocess.Popen([sys.executable, "-I", "-S", "-B", "-c", CHILD_BRIDGE, str(entrypoint()),
                "status", "--json", "--no-input", "--repo", repo], stdin=subprocess.DEVNULL,
                stdout=output, stderr=subprocess.DEVNULL, start_new_session=True)
            while time.monotonic() < deadline:
                if os.fstat(output.fileno()).st_size > MAX_OUTPUT:
                    return None
                try:
                    process.wait(timeout=min(0.01, max(0.001, deadline - time.monotonic())))
                    break
                except subprocess.TimeoutExpired:
                    pass
            else:
                return None
            if process.returncode != 0 or os.fstat(output.fileno()).st_size > MAX_OUTPUT:
                return None
            output.seek(0)
            return json.loads(output.read(MAX_OUTPUT + 1), object_pairs_hook=unique_object)
        except (OSError, ValueError, subprocess.SubprocessError):
            return None
        finally:
            if process is not None:
                # A finished root may leave live descendants and held handles.
                # Kill the whole private process group before waiting on root.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=CLEANUP_SECONDS)
                except subprocess.TimeoutExpired:
                    pass


def display(value):
    if type(value) is not dict or value.get("schema") != "scan_secrets_status_v1" or value.get("historical") is not True or value.get("authorizes_publication") is not False:
        return UNAVAILABLE
    if value.get("outcome") == "not_scanned" and value.get("last_scan") is None:
        return "not scanned; saved scope/time unavailable"
    if value.get("outcome") != "last_scan" or type(value.get("last_scan")) is not dict:
        return UNAVAILABLE
    last = value["last_scan"]
    result = {"complete_clean": "clean", "complete_findings": "findings", "incomplete": "incomplete"}.get(last.get("outcome"))
    scope = last.get("scope")
    completed = last.get("completed_at")
    if result is None or type(scope) is not str or scope not in {"worktree", "index", "outgoing"} or type(completed) is not str or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z", completed) is None:
        return UNAVAILABLE
    return f"last {result}; scope {scope}; time {completed}"


def main():
    payload = None
    summary = UNAVAILABLE
    try:
        payload = read_input()
        if payload is not None:
            repo = payload.get("cwd", os.getcwd())
            if type(repo) is str and len(repo) <= 8192 and "\0" not in repo and Path(repo).is_absolute():
                summary = display(child_status(repo))
    except Exception:
        pass
    message = "scan-secrets status: " + summary + ". Historical only; never authorizes publication."
    # Progress framing is CLI-only. Unknown/error input may be VS Code, whose
    # parser requires one final JSON document. Native camelCase identifies CLI.
    copilot_cli = payload is not None and (payload.get("hook_event_name") == "agentStop" or (
        "hook_event_name" not in payload and type(payload.get("sessionId")) is str
        and type(payload.get("timestamp")) is int and type(payload.get("cwd")) is str
        and type(payload.get("transcriptPath")) is str and payload.get("stopReason") == "end_turn"
        and type(payload.get("stop_hook_active")) is bool))
    if PROVIDER == "copilot" and copilot_cli:
        rows = [{"type": "progress", "message": message}, {}]
    else:
        rows = [{"systemMessage": message}]
    try:
        for row in rows:
            sys.stdout.buffer.write((json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8"))
        sys.stdout.buffer.flush()
    except OSError:
        # The host may stop consuming after its turn completes. Cleanup has
        # already finished; prevent a second flush failure at interpreter exit.
        descriptor = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(descriptor, sys.stdout.fileno())
        finally:
            os.close(descriptor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

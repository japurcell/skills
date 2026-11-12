#!/usr/bin/env python3
"""Private scheduler-pilot PreToolUse policy (stdlib).

--manifest PATH --cell ID: read one bounded native hook JSON object on stdin.
Emit documented native JSON on stdout; diagnostics on stderr. Exit 0 permits
normal processing; 2 explicitly denies. --help performs no I/O. This process's
fail-closed output does not establish host trust, hook-error handling or coverage.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical(path, root):
    path = Path(path)
    if not path.is_absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("path outside frozen root")
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError("linked policy/output path")
        current = current.parent
    return path


def load(manifest_path, cell_id):
    path = Path(manifest_path)
    if path.is_symlink():
        raise ValueError("linked manifest")
    path = path.resolve()
    if path.is_symlink() or path.parent.resolve() != path.parent or path.parent.stat().st_mode & 0o077:
        raise ValueError("private physical manifest required")
    root = path.parent
    if json.loads((root / "manifest.sha256.json").read_text()) != {"sha256": sha(path)}:
        raise ValueError("manifest hash drift")
    manifest = json.loads(path.read_text())
    if manifest.get("root") != str(root) or manifest.get("version") != 3:
        raise ValueError("unsupported control manifest")
    for relative, expected in manifest["hashes"].items():
        target = physical(root / relative, root)
        if not target.is_file() or sha(target) != expected:
            raise ValueError("immutable policy/config/input drift")
    cell = manifest["cells"][cell_id]
    physical(Path(cell["repo"]), root)
    control = cell["control"]
    hook = physical(Path(control["script"]), root)
    if sha(Path(__file__)) != sha(hook):
        raise ValueError("invoked policy differs from frozen policy")
    return manifest, cell, sha(hook)


def shell_allowed(command, tool_input, cell):
    if not isinstance(command, str) or not command or any(c in command for c in "\n\r;|&<>$`\x00"):
        return False
    if set(tool_input) - {"command", "cwd", "login", "tty", "yield_time_ms", "max_output_tokens", "timeout_ms"}:
        return False
    if tool_input.get("login", False) is not False or tool_input.get("tty", False) is not False:
        return False
    if "cwd" in tool_input and Path(tool_input["cwd"]).resolve() != Path(cell["repo"]):
        return False
    argv = shlex.split(command)
    if argv[:2] != cell["helper_prefix"] or shlex.join(argv) != command:
        return False
    arguments = argv[2:]
    if arguments == ["smoke-write"]:
        return True
    if len(arguments) == 4 and arguments[0] == "parent-update":
        return all(value.strip() and len(value) <= 128 for value in arguments[1:3]) and math.isfinite(float(arguments[3]))
    if len(arguments) < 3 or arguments[0] != "--state":
        return False
    output = Path(cell["repo"]) / "outputs"
    state = physical(Path(arguments[1]), output)
    if state.parent != output or state.name not in ("smoke-state.json", "scenario-state.json"):
        return False
    return arguments[2] in ("register", "tick", "checkpoint", "extend", "complete", "cancel", "confirm-stopped", "transfer", "confirm-transfer", "list")


def patch_allowed(command, cell):
    if not isinstance(command, str):
        return False
    lines = command.splitlines()
    if not lines or lines[0] != "*** Begin Patch" or lines[-1] != "*** End Patch":
        return False
    output = Path(cell["repo"]) / "outputs"
    targets = []
    for line in lines[1:-1]:
        if line.startswith(("*** Add File: ", "*** Update File: ")):
            raw = line.split(": ", 1)[1]
            path = Path(raw)
            if ".." in path.parts:
                return False
            if not path.is_absolute():
                path = Path(cell["repo"]) / path
            target = physical(path, output)
            if target == output or target.is_dir() or (target.exists() and target.stat().st_nlink != 1):
                return False
            targets.append(target)
        elif line.startswith("*** ") and line != "*** End of File":
            return False
    return bool(targets)


def audit(manifest, cell, policy_hash, event, decision):
    path = physical(Path(cell["control"]["audit"]), Path(manifest["root"]))
    record = {"policy_sha256": policy_hash, "decision": decision,
              "tool_name": event.get("tool_name"), "tool_use_id": event.get("tool_use_id"),
              "command_sha256": hashlib.sha256(str(event.get("tool_input", {}).get("command", "")).encode()).hexdigest()}
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "a") as stream:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        stream.write(json.dumps(record) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--cell", required=True)
    args = parser.parse_args()
    try:
        raw = sys.stdin.read(65537)
        if len(raw) > 65536:
            raise ValueError("hook input exceeds 64KiB")
        event = json.loads(raw)
        if not isinstance(event, dict) or event.get("hook_event_name") != "PreToolUse" or not isinstance(event.get("tool_input"), dict) or not isinstance(event.get("tool_use_id"), str) or not event["tool_use_id"]:
            raise ValueError("malformed native PreToolUse event")
        manifest, cell, policy_hash = load(args.manifest, args.cell)
        if Path(event.get("cwd", "")).resolve() != Path(cell["repo"]):
            raise ValueError("wrong native cwd")
        tool, data = event.get("tool_name"), event["tool_input"]
        allowed = shell_allowed(data.get("command"), data, cell) if tool == "Bash" else (patch_allowed(data.get("command"), cell) if tool == "apply_patch" and set(data) == {"command"} else False)
        audit(manifest, cell, policy_hash, event, "allow" if allowed else "deny")
        if not allowed:
            raise ValueError("not an exact frozen helper invocation or confined neutral output write")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "Private scheduler policy loaded: " + policy_hash}}))
        return 0
    except Exception as error:
        reason = "scheduler-pilot policy denied: " + str(error)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))
        print(reason, file=sys.stderr)
        return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "policy interrupted"}}))
        sys.exit(2)

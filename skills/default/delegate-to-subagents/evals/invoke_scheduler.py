#!/usr/bin/env python3
"""Execute only the frozen scheduler or fixed disposable fixture I/O.

Read sibling invocation.json; stdin unused. JSON receipts go to stdout;
diagnostics to stderr. Exit 0 success, 2 invalid input/child rejection,
124 child timeout, 130 interruption. The native provider event must retain
this exact helper command and its receipt; authored files alone are not proof.
"""
import json
from pathlib import Path
import subprocess
import os
import signal
import time
import sys


def load(path):
    return json.loads(path.read_text()) if path.exists() else None


def capture(argv, timeout, *, cwd=None, env=None, text_input=None):
    child = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE if text_input is not None else subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    code = None
    try:
        stdout, stderr = child.communicate(text_input, timeout=timeout)
        code = child.returncode
    except subprocess.TimeoutExpired:
        code = 124
    except KeyboardInterrupt:
        code = 130
    finally:
        try:
            os.killpg(child.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + .2
        while time.monotonic() < deadline:
            child.poll()
            try:
                os.killpg(child.pid, 0)
            except ProcessLookupError:
                break
            time.sleep(.01)
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        remaining_out, remaining_err = child.communicate(timeout=2)
        if code in (124, 130):
            stdout, stderr = remaining_out, remaining_err
    return code, stdout, stderr


def main():
    if sys.argv[1:] in (["--help"], ["-h"]):
        print(__doc__)
        return 0
    spec = load(Path(__file__).with_name("invocation.json"))
    repo = Path(spec["repo"])
    if repo.resolve() != repo or repo.is_symlink():
        raise ValueError("physical repo path required")
    output = repo / "outputs"
    arguments = sys.argv[1:]
    if arguments == ["smoke-write"]:
        path = output / "smoke.json"
        if path.is_symlink() or path.parent.is_symlink():
            raise ValueError("linked output prohibited")
        path.write_text(json.dumps({"smoke": True}))
        receipt = {"kind": "smoke-write", "readback": load(path), "path": str(path)}
        code = 0
    elif len(arguments) == 4 and arguments[0] == "parent-update":
        path = output / "ownership.json"
        if path.is_symlink() or path.parent.is_symlink():
            raise ValueError("linked output prohibited")
        before = load(path)
        after = {"previous_owner": arguments[1], "owner": arguments[2], "updated_at": float(arguments[3])}
        path.write_text(json.dumps(after))
        receipt = {"kind": "parent-update", "before": before, "after": load(path), "at": float(arguments[3])}
        code = 0
    else:
        if len(arguments) < 3 or arguments[0] != "--state":
            raise ValueError("use --state OUTPUT_STATE COMMAND [ARGS]")
        state = Path(arguments[1])
        if state.name not in ("smoke-state.json", "scenario-state.json") or state.parent.resolve() != output.resolve() or state.is_symlink() or output.is_symlink():
            raise ValueError("state must be an exact outputs smoke/scenario state path")
        if arguments[2] not in ("register", "tick", "checkpoint", "extend", "complete", "cancel", "confirm-stopped", "transfer", "confirm-transfer", "list"):
            raise ValueError("unsupported scheduler command")
        before = load(state)
        parent_before = load(output / "ownership.json")
        argv = ["python3", spec["scheduler"], *arguments]
        code, stdout, stderr = capture(argv, spec.get("timeout_seconds", 10))
        receipt = {"kind": "scheduler", "argv": argv, "exit_code": code, "stdout": stdout, "stderr": stderr, "before": before, "after": load(state), "parent_before": parent_before, "parent_after": load(output / "ownership.json")}
    print(json.dumps({"pilot_child": receipt}), flush=True)
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.stdout = open(os.devnull, "w")
        sys.exit(1)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
    except subprocess.TimeoutExpired:
        print("scheduler child timed out", file=sys.stderr)
        sys.exit(124)
    except KeyboardInterrupt:
        sys.exit(130)

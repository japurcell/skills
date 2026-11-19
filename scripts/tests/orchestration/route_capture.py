"""Invoke the pinned route38 executable and retain its JSON decision safely."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def _timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _request(argv, stdin_text):
    if argv != ["--input", "route-request.json"] or stdin_text:
        return None
    try:
        source = (Path.cwd() / "route-request.json").resolve(strict=True)
        source.relative_to(Path.cwd().resolve())
        value = json.loads(source.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def _append(path, value):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    real = os.environ.get("P0_REAL_ROUTER_SCRIPT")
    router_log = os.environ.get("P0_ROUTER_LOG")
    if not all((real, router_log)):
        print("route wrapper: missing private setup", file=sys.stderr)
        return 2
    stdin_text = sys.stdin.read()
    request = _request(args, stdin_text)
    if request is None:
        print("route wrapper: only the bounded route-request.json invocation is enabled", file=sys.stderr)
        return 2
    result = subprocess.run([sys.executable, real, *args], input=stdin_text,
                            capture_output=True, text=True, check=False)
    try:
        output = json.loads(result.stdout) if result.stdout.strip() else None
    except json.JSONDecodeError:
        output = None
    row = {"timestamp": _timestamp(), "argv": args, "request": request,
           "exit_code": result.returncode, "output": output,
           "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest()}
    _append(router_log, row)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

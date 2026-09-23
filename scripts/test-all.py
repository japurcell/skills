#!/usr/bin/env python3
"""Run the maintained repository test suites on macOS and Linux."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import BinaryIO


# Register maintained suites explicitly; never discover fixture or archived tests.
SUITES = (
    ("bash", "scripts/test-addy-install.sh"),
    ("bash", "scripts/test-cleanup-skill-workspaces.sh"),
    ("bash", "scripts/test-codex-hooks-startup.sh"),
    ("bash", "scripts/test-codex-hooks-secrets-scanner.sh"),
    ("bash", "scripts/test-gemini-hooks-auto-ingest.sh"),
    ("bash", "scripts/test-gemini-hooks-observability.sh"),
    ("bash", "scripts/test-gemini-hooks-okf-lint.sh"),
    ("bash", "scripts/test-gemini-hooks-rtk.sh"),
    ("bash", "scripts/test-gemini-hooks-secrets-scanner.sh"),
    ("bash", "scripts/test-gemini-hooks-startup.sh"),
    ("bash", "scripts/test-gemini-hooks-tool-guard.sh"),
    ("bash", "scripts/test-hooks-auto-ingest.sh"),
    ("bash", "scripts/test-hooks-observability.sh"),
    ("bash", "scripts/test-hooks-okf-lint.sh"),
    ("bash", "scripts/test-hooks-rtk.sh"),
    ("bash", "scripts/test-hooks-secrets-scanner.sh"),
    ("bash", "scripts/test-hooks-startup.sh"),
    ("bash", "scripts/test-hooks-tool-guard.sh"),
    ("python3", "scripts/test-codex-agents.py"),
    ("python3", "scripts/test-install-codex-hooks.py"),
    ("python3", "scripts/test-generate-hooks.py"),
    ("pwsh", "-NoProfile", "-File", "scripts/test-install.ps1"),
    ("pwsh", "-NoProfile", "-File", "scripts/test-codex-hooks-windows.ps1"),
    ("bash", "scripts/test-install.sh"),
    ("bash", "scripts/test-okf-lint.sh"),
    ("bash", "scripts/test-repo-root.sh"),
    ("python3", "scripts/test_helpers.py"),
    ("python3", "scripts/test_test_all.py"),
    ("python3", "-m", "unittest", "discover", "-s",
     "skills/subagent-model-router/evals", "-p", "test_*.py"),
)


class Cancelled(Exception):
    def __init__(self, signum: int):
        self.signum = signum


class Processes:
    """Own child process groups so cancellation never signals the caller."""

    def __init__(self):
        self.active: subprocess.Popen | None = None
        self.cancelled = 0
        self.force = False

    def __enter__(self):
        self.handlers = {
            signum: signal.signal(signum, self.on_signal)
            for signum in (signal.SIGINT, signal.SIGTERM)
        }
        return self

    def on_signal(self, signum, frame):
        # Record intent instead of raising during Popen before its PID is assigned.
        if self.cancelled:
            self.force = True
        else:
            self.cancelled = signum

    def check_cancelled(self):
        if self.cancelled:
            raise Cancelled(self.cancelled)

    def __exit__(self, exc_type, exc, traceback):
        try:
            try:
                if self.cancelled:
                    print(
                        f"test-all: received {signal.Signals(self.cancelled).name}; "
                        "stopping children (up to 5s; Ctrl-C again forces termination).",
                        file=sys.stderr, flush=True,
                    )
            finally:
                if self.active is not None:
                    self.stop()
        finally:
            for signum, handler in self.handlers.items():
                signal.signal(signum, handler)
        if exc_type is None:
            self.check_cancelled()

    def send_group(self, signum):
        try:
            os.killpg(self.active.pid, signum)
            return True
        except ProcessLookupError:
            return False

    def stop(self):
        self.send_group(self.cancelled or signal.SIGTERM)
        deadline = time.monotonic() + 5
        while not self.force and time.monotonic() < deadline:
            self.active.poll()  # Reap the leader, but still check surviving descendants.
            if not self.send_group(0):
                break
            time.sleep(0.05)
        self.send_group(signal.SIGKILL)
        try:
            self.active.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass  # SIGKILL is pending; do not let uninterruptible I/O hang the runner.
        self.active = None

    def run(
        self, command: tuple[str, ...], root: Path,
        stdout: BinaryIO | None = None, timeout: float | None = None,
    ) -> int:
        self.check_cancelled()
        self.active = subprocess.Popen(
            command, cwd=root, stdin=subprocess.DEVNULL, stdout=stdout,
            start_new_session=True,
        )
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            self.check_cancelled()
            try:
                code = self.active.wait(timeout=0.05)
                self.check_cancelled()
                self.active = None
                return 128 - code if code < 0 else code
            except subprocess.TimeoutExpired:
                if deadline is not None and time.monotonic() >= deadline:
                    raise OSError(f"dependency check timed out: {shlex.join(command)}")


def main(processes: Processes) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        allow_abbrev=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  ./scripts/test-all.py          Run every suite, continuing after failures.
  ./scripts/test-all.py --list   List suite commands without running them.

Requires Python 3, bash, git, jq, flock, sqlite3, and PowerShell 7+ (pwsh).
Install missing tools with your system package manager and add them to PATH.
Help and listing do not check suite dependencies. No dependencies are installed.

Child stdout/stderr are inherited; progress and the summary go to stderr.
Stdin is not read; suites receive EOF. There are no prompts or suite timeouts.
Host-specific skips remain visible in suite output.
Ctrl-C or SIGTERM stops the active suite and its descendants, with up to five
seconds for cleanup. A second Ctrl-C forces termination immediately.

Exit codes: 0 success, 1 suite failures, 2 usage/dependency/runner errors,
130 Ctrl-C, 143 SIGTERM, 141 runner broken pipe. Child failures, including
broken pipes, do not prevent later suites from running.
""",
    )
    parser.add_argument("--list", action="store_true", help="list suite commands and exit")
    args = parser.parse_args()
    if args.list:
        for command in SUITES:
            print(shlex.join(command))
        return 0
    if sys.platform not in ("linux", "darwin"):
        print("test-all: run this command on macOS or Linux; native Windows is not supported.",
              file=sys.stderr)
        return 2
    missing = [
        tool for tool in ("bash", "python3", "git", "jq", "flock", "sqlite3", "pwsh")
        if shutil.which(tool) is None
    ]
    if missing:
        print(
            f"test-all: missing dependencies: {', '.join(missing)}.\n"
            "Install them with your system package manager and add them to PATH.\n"
            "PowerShell requires version 7 or newer. See README.md, Validation.",
            file=sys.stderr,
        )
        return 2
    root = Path(__file__).resolve().parent.parent
    missing_suites = [
        part for command in SUITES for part in command
        if (part.startswith("scripts/") and not (root / part).is_file())
        or (part.startswith("skills/") and not (root / part).is_dir())
    ]
    if missing_suites:
        print(
            f"test-all: missing suite paths: {', '.join(missing_suites)}.\n"
            "Restore the complete checkout or update the suite registry after moving tests.",
            file=sys.stderr,
        )
        return 2
    print(f"Checking prerequisites for {len(SUITES)} suites...", file=sys.stderr, flush=True)
    with tempfile.TemporaryFile() as output:
        code = processes.run(
            ("pwsh", "-NoProfile", "-NonInteractive", "-Command",
             "$PSVersionTable.PSVersion.Major"),
            root, stdout=output, timeout=5,
        )
        output.seek(0)
        major = output.read(100).strip()
    if code or not major.isdigit() or int(major) < 7:
        print("test-all: PowerShell 7+ is required. Install a current pwsh on PATH.", file=sys.stderr)
        return 2
    return run_suites(processes, root)


def run_suites(processes: Processes, root: Path) -> int:
    failures = []
    started = time.monotonic()
    for index, command in enumerate(SUITES, 1):
        label = shlex.join(command)
        print(f"[{index}/{len(SUITES)}] RUN {label}", file=sys.stderr, flush=True)
        code = processes.run(command, root)
        if code:
            failures.append((label, code))
        print(
            f"{'FAIL' if code else 'PASS'} {label} (exit {code})",
            file=sys.stderr, flush=True,
        )
    print(
        f"Suites: {len(SUITES) - len(failures)} passed, {len(failures)} failed "
        f"in {time.monotonic() - started:.1f}s. "
        "Host-specific skips, if any, are shown in suite output.",
        file=sys.stderr, flush=True,
    )
    for label, code in failures:
        print(f"  FAIL {label} (exit {code})", file=sys.stderr, flush=True)
    return 1 if failures else 0


def entrypoint():
    try:
        try:
            with Processes() as processes:
                code = main(processes)
        except Cancelled as error:
            code = 128 + error.signum
        except SystemExit as error:
            code = error.code
        except BrokenPipeError:
            raise
        except OSError as error:
            print(f"test-all: runner error: {error}. Check tool access and checkout permissions.",
                  file=sys.stderr, flush=True)
            code = 2
        sys.stdout.flush()
        sys.stderr.flush()
        return code
    except BrokenPipeError:
        # Prevent buffered output from changing exit 141 to 120 at interpreter shutdown.
        with open(os.devnull, "w") as sink:
            os.dup2(sink.fileno(), sys.stdout.fileno())
            os.dup2(sink.fileno(), sys.stderr.fileno())
        return 141


if __name__ == "__main__":
    raise SystemExit(entrypoint())

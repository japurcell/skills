"""Bounded POSIX subprocess groups and incremental Gemini JSONL decoding."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time
from dataclasses import dataclass

from contracts import LIMIT, Stop, decode, require


@dataclass
class Outcome:
    code: int
    stdout: bytes
    stderr: bytes
    duration: float
    timed_out: bool
    stdout_truncated: bool
    stderr_truncated: bool


class Supervisor:
    def __init__(self, deadline):
        self.deadline = deadline
        self.signal = 0
        self.force = False
        self.active = None
        self.inspection = False
        self.cleanup_failure = None

    def __enter__(self):
        self.handlers = {s: signal.signal(s, self.on_signal) for s in (signal.SIGINT, signal.SIGTERM)}
        return self

    def __exit__(self, error_type, error, traceback):
        try:
            if self.active:
                failure = self.finalize_child(self.active)
                if failure and error is None:
                    raise failure
        finally:
            for s, handler in self.handlers.items():
                signal.signal(s, handler)

    def on_signal(self, signum, frame):
        if self.signal:
            self.force = True
        else:
            self.signal = signum

    def check(self):
        if self.cleanup_failure:
            raise self.cleanup_failure
        if self.inspection:
            return
        if self.signal:
            raise Stop('interrupted', signal.Signals(self.signal).name, 128 + self.signal)
        if time.monotonic() >= self.deadline:
            raise Stop('total_deadline', 'Total runtime exhausted', 124)

    @staticmethod
    def kill_group(pid, signum):
        try:
            os.killpg(pid, signum)
        except ProcessLookupError:
            pass
        except PermissionError:
            # The group may have disappeared while a short-lived leader exited.
            # A denied signal is harmless only after independent group inspection
            # proves that no live member remains. Real denial stays a blocker.
            if Supervisor.living_group(pid):
                raise

    @staticmethod
    def living_group(pid):
        # killpg(0) also sees reparented zombies. Zombies cannot write or hold pipes.
        try:
            os.killpg(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            # A denied kernel probe cannot establish whether members still live.
            # Use the bounded process inventory below rather than guessing.
            pass
        result = subprocess.run(['/bin/ps', '-eo', 'pgid=,stat='], stdin=subprocess.DEVNULL,
                                capture_output=True, timeout=1)
        if result.returncode:
            raise Stop('cleanup_unconfirmed', 'Unable to inspect remaining child group', 3)
        return any(parts[0] == str(pid) and not parts[1].startswith('Z')
                   for line in result.stdout.decode().splitlines() if len(parts := line.split()) >= 2)

    def finalize_child(self, child, cleanup_confirmed=False):
        """Always release local resources, retaining a barrier on uncertain cleanup."""
        failure = None
        try:
            if not cleanup_confirmed:
                try:
                    self.kill_group(child.pid, signal.SIGKILL)
                except OSError as error:
                    failure = Stop('cleanup_unconfirmed', f'Cannot terminate owned child group {child.pid}: {error}', 3)
            try:
                child.wait(timeout=1)
            except (OSError, subprocess.TimeoutExpired) as error:
                failure = failure or Stop('cleanup_unconfirmed', f'Child leader termination is unconfirmed: {error}', 3)
            if not cleanup_confirmed and failure is None:
                try:
                    limit = time.monotonic() + .5
                    while self.living_group(child.pid) and time.monotonic() < limit:
                        time.sleep(.02)
                    if self.living_group(child.pid):
                        failure = Stop('cleanup_unconfirmed', 'Owned descendants remain alive', 3)
                except (OSError, Stop, subprocess.SubprocessError) as error:
                    failure = Stop('cleanup_unconfirmed', f'Child group cleanup is unconfirmed: {error}', 3)
        finally:
            for pipe in (child.stdout, child.stderr):
                try:
                    pipe.close()
                except OSError as error:
                    failure = failure or Stop('cleanup_unconfirmed', f'Cannot close owned child stream: {error}', 3)
            self.active = None
        if failure:
            self.cleanup_failure = failure
        return failure

    def run(self, argv, cwd: Path, timeout, consume=None, spawned=None):
        self.check()
        started = time.monotonic()
        end = min(self.deadline, started + timeout)
        output, errors = bytearray(), bytearray()
        timed_out, failure = False, None
        sizes = [0, 0]
        try:
            child = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, start_new_session=True)
        except (OSError, ValueError) as error:
            raise Stop('spawn_error', f'Cannot start {argv[0]}: {error}', 3) from error
        self.active = child
        stop_at = None
        cleanup_confirmed = False
        try:
            if spawned:
                spawned(child.pid)
            with selectors.DefaultSelector() as poller:
                for pipe in (child.stdout, child.stderr):
                    os.set_blocking(pipe.fileno(), False)
                    poller.register(pipe, selectors.EVENT_READ)
                while poller.get_map() or child.poll() is None:
                    now = time.monotonic()
                    child.poll()
                    stopping = (self.signal and not self.inspection) or failure or now >= end
                    # Descendants holding inherited streams are still owned after leader exit.
                    if stopping and stop_at is None:
                        timed_out = now >= end and not self.signal and failure is None
                        self.kill_group(child.pid, (self.signal if not self.inspection else 0) or signal.SIGTERM)
                        stop_at = min(self.deadline, now + min(5, max(.02, timeout * .1)))
                    if stop_at is not None and (self.force or now >= stop_at):
                        self.kill_group(child.pid, signal.SIGKILL)
                    if stop_at is not None and now >= stop_at + 1:
                        raise Stop('cleanup_unconfirmed', 'Child streams did not close after SIGKILL', 3)
                    for key, _ in poller.select(.02):
                        chunk = os.read(key.fileobj.fileno(), 65536)
                        if not chunk:
                            poller.unregister(key.fileobj)
                            continue
                        buffer = output if key.fileobj is child.stdout else errors
                        sizes[0 if key.fileobj is child.stdout else 1] += len(chunk)
                        buffer.extend(chunk)
                        if len(buffer) > LIMIT:
                            del buffer[:-LIMIT]
                        if key.fileobj is child.stdout and consume and failure is None:
                            try:
                                consume(chunk)
                            except Stop as error:
                                failure = error
                child.wait(timeout=1)
            # A detached-from-pipes descendant must also be stopped before replacement.
            if self.living_group(child.pid):
                self.kill_group(child.pid, signal.SIGKILL)
                limit = time.monotonic() + .5
                while self.living_group(child.pid) and time.monotonic() < limit:
                    time.sleep(.02)
                if self.living_group(child.pid):
                    raise Stop('cleanup_unconfirmed', 'Owned descendants remain alive', 3)
            cleanup_confirmed = True
            if failure:
                raise Stop('protocol', failure.detail, 1)
            return Outcome(child.returncode, bytes(output), bytes(errors), time.monotonic() - started, timed_out,
                           sizes[0] > LIMIT, sizes[1] > LIMIT)
        except OSError as error:
            raise Stop('cleanup_unconfirmed', f'Owned child I/O or cleanup failed: {error}', 3) from error
        finally:
            cleanup_error = self.finalize_child(child, cleanup_confirmed)
            if cleanup_error:
                raise cleanup_error


class GeminiStream:
    def __init__(self):
        self.pending = bytearray()
        self.answer = ''
        self.terminal = None
        self.session_id = None
        self.model = None
        self.usage = None
        self.error = None
        self.seen_init = False

    def feed(self, chunk):
        self.pending.extend(chunk)
        while b'\n' in self.pending:
            line, _, rest = self.pending.partition(b'\n')
            self.pending = bytearray(rest)
            self.line(line)
        require(len(self.pending) <= LIMIT, 'Provider event exceeds 1 MiB')

    def line(self, raw):
        require(0 < len(raw) <= LIMIT, 'Empty or oversized provider event')
        try:
            event = decode(raw.decode('utf-8'))
        except UnicodeError as error:
            raise Stop('protocol', 'Provider output is not UTF-8', 1) from error
        require(isinstance(event, dict) and isinstance(event.get('type'), str), 'Invalid provider event')
        kind = event['type']
        require(self.terminal is None, 'Provider data after terminal result')
        if kind == 'init':
            require(not self.seen_init and isinstance(event.get('session_id'), str) and
                    isinstance(event.get('model'), str), 'Invalid or duplicate init')
            self.seen_init = True
            self.session_id, self.model = event['session_id'], event['model']
        elif kind == 'message' and event.get('role') == 'assistant':
            require(self.seen_init and isinstance(event.get('content'), str), 'Invalid assistant event')
            self.answer += event['content']
            require(len(self.answer.encode()) <= LIMIT, 'Assistant payload exceeds 1 MiB')
        elif kind == 'tool_use':
            # Provider tool turns may contain narration. Only the assistant turn
            # after the last tool call is the proposed structured result.
            self.answer = ''
        elif kind == 'error' and event.get('severity') == 'error':
            require(isinstance(event.get('message'), str), 'Invalid provider error')
            self.error = event['message'][:4096]
        elif kind == 'result':
            require(self.seen_init and event.get('status') in ('success', 'error'), 'Invalid terminal result')
            self.terminal = event
            stats = event.get('stats')
            if isinstance(stats, dict):
                self.usage = {key: stats.get(key) if type(stats.get(key)) in (int, float) and math.isfinite(stats[key]) and stats[key] >= 0 else None
                              for key in ('total_tokens', 'input_tokens', 'output_tokens', 'duration_ms', 'tool_calls')}

    def finish(self):
        if self.pending:
            self.line(self.pending)
            self.pending.clear()
        require(self.terminal is not None, 'Missing terminal provider result')
        if self.error or self.terminal['status'] != 'success':
            error = self.terminal.get('error', {})
            kind = error.get('type', '') if isinstance(error, dict) else ''
            # Only explicit rate-limit/service-unavailable types permit paid retry.
            if kind in ('RATE_LIMIT', 'RESOURCE_EXHAUSTED', 'UNAVAILABLE', 'rate_limit', 'service_unavailable'):
                raise Stop('transient_infrastructure', 'Provider temporarily unavailable', 1)
            raise Stop('provider_blocked', 'Provider error; inspect its session log', 3)
        return self.answer

#!/usr/bin/env python3
"""Persistent assignment scheduler. Emits host actions; controls no workers."""
import argparse
import contextlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time

VERSION = 2


@contextlib.contextmanager
def locked(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path) + '.lock', 'a+b') as lock:
        if os.name == 'nt':
            import msvcrt
            lock.seek(0)
            if not lock.read(1):
                lock.write(b'0')
                lock.flush()
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == 'nt':
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock, fcntl.LOCK_UN)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def load(path):
    if not path.exists():
        return {'version': VERSION, 'assignments': {}}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or data.get('version') != VERSION or not isinstance(data.get('assignments'), dict):
            raise ValueError('unsupported schema')
        for key, a in data['assignments'].items():
            if not isinstance(a, dict) or not isinstance(key, str) or not key or a.get('id') != key:
                raise ValueError('invalid assignment identity')
            if any(not isinstance(a.get(k), str) for k in ('agent', 'task', 'route')):
                raise ValueError('invalid assignment metadata')
            if a.get('status') not in ('active', 'completed', 'cancelled') or a.get('phase') not in ('running', 'checkpoint', 'decision', 'extended', 'stop'):
                raise ValueError('invalid assignment status or phase')
            if any(not finite(a.get(k)) for k in ('deadline', 'checkpoint_interval', 'checkpoint_grace', 'next_checkpoint')) or a['checkpoint_interval'] <= 0 or a['checkpoint_grace'] < 0:
                raise ValueError('invalid assignment timing')
            if 'eta' in a and not finite(a['eta']):
                raise ValueError('invalid assignment ETA')
            if a.get('phase') in ('checkpoint', 'decision') and not finite(a.get('phase_deadline')):
                raise ValueError('invalid phase deadline')
            if any(not isinstance(a.get(k), bool) for k in ('extension_used', 'stop_confirmed', 'transferred')):
                raise ValueError('invalid assignment flags')
        return data
    except (OSError, ValueError, TypeError) as exc:
        raise ValueError(f'malformed state at {path}: {exc}') from exc


def save(path, data):
    fd, tmp = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, sort_keys=True, indent=2, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def add_time(start, duration):
    result = start + duration
    if not finite(result):
        raise ValueError('time calculation exceeds finite range')
    return result


def advance(a, now):
    if a['status'] != 'active':
        return None
    phase = a['phase']
    event = None
    if phase == 'running' and now >= a['deadline']:
        a['phase'] = 'checkpoint'
        a['phase_deadline'] = add_time(now, a['checkpoint_grace'])
        event = ('deadline_expired', 'request status by the checkpoint deadline')
    elif phase in ('checkpoint', 'decision') and now >= a['phase_deadline']:
        a['phase'] = 'stop'
        event = ('checkpoint_expired', 'request stop; confirm worker and writes stopped before ownership transfer')
    elif phase == 'extended' and now >= a['deadline']:
        a['phase'] = 'stop'
        event = ('extension_expired', 'request stop; confirm worker and writes stopped before ownership transfer')
    elif phase in ('running', 'extended') and now >= a['next_checkpoint']:
        a['next_checkpoint'] = add_time(now, a['checkpoint_interval'])
        event = ('progress_reminder', 'request concise progress update')
    if event:
        return {'type': event[0], 'assignment': a['id'], 'host_action': event[1]}
    return None


def events(assignments, now):
    return [event for a in assignments.values() if (event := advance(a, now))]


class StrictParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs['allow_abbrev'] = False
        super().__init__(*args, **kwargs)


def parser():
    contract = ("Times are seconds: deadlines and ETAs are Unix timestamps; intervals "
                "and grace are durations. Successful operations write JSON to stdout; help writes text; "
                "errors go to stderr with exit 2, interruption exits 130, and a closed "
                "stdout exits 1. No command reads stdin. The host carries out actions. "
                "Example: scheduler.py --state work.json wait --max-wait 60")
    p = StrictParser(description=__doc__, epilog=contract)
    p.add_argument('--state', type=Path, required=True, help='session-specific state file')
    sub = p.add_subparsers(dest='cmd', required=True)
    purposes = {
        'register': 'Register an assignment with a future deadline.',
        'checkpoint': 'Record timely worker status.',
        'extend': 'Grant the one allowed ETA-based extension.',
        'complete': 'Mark an assignment complete.',
        'cancel': 'Cancel an assignment.',
        'confirm-stopped': 'Record verified worker and write shutdown.',
        'transfer': 'Emit permission for the host to transfer ownership.',
        'tick': 'Persist and emit currently due actions.',
        'wait': 'Wait for a due action or a bounded timeout.',
        'list': 'List stored assignments.',
    }
    def command(name):
        return sub.add_parser(name, help=purposes[name], description=purposes[name], epilog=contract)
    r = command('register')
    for name in ('id', 'agent', 'task'):
        r.add_argument(name)
    r.add_argument('--deadline', type=float, required=True, help='future Unix timestamp in seconds')
    r.add_argument('--checkpoint', type=float, required=True, help='progress reminder interval in seconds')
    r.add_argument('--grace', type=float, default=60, help='status and decision grace in seconds (default: 60)')
    r.add_argument('--route', default='', help='coordination metadata')
    r.add_argument('--now', type=float, help='override current Unix timestamp in seconds for testing')
    for name in ('checkpoint', 'extend', 'complete', 'cancel', 'confirm-stopped', 'transfer'):
        q = command(name)
        q.add_argument('id')
        q.add_argument('--now', type=float, help='override current Unix timestamp in seconds for testing')
        if name in ('checkpoint', 'extend'):
            q.add_argument('--eta', type=float, required=name == 'extend', help='estimated completion Unix timestamp in seconds')
        if name == 'confirm-stopped':
            q.add_argument('--confirmation', required=True, help='literal worker-and-writes-stopped')
    for name in ('tick', 'wait'):
        q = command(name)
        q.add_argument('--now', type=float, help='override current Unix timestamp in seconds for testing')
        if name == 'wait':
            q.add_argument('--max-wait', type=float, required=True, help='maximum wait in seconds')
    command('list')
    return p


def main():
    args = parser().parse_args()
    supplied_now = getattr(args, 'now', None)
    try:
        for name in ('now', 'deadline', 'checkpoint', 'grace', 'eta', 'max_wait'):
            value = getattr(args, name, None)
            if value is not None and not finite(value):
                raise ValueError(f'{name} must be finite')
        if args.cmd == 'wait' and args.max_wait < 0:
            raise ValueError('max-wait must be nonnegative')
        started = time.monotonic()
        while True:
            now = time.time() if supplied_now is None else supplied_now + (time.monotonic() - started if args.cmd == 'wait' else 0)
            with locked(args.state):
                # Refresh real time after lock acquisition.
                if supplied_now is None:
                    now = time.time()
                data = load(args.state)
                assignments = data['assignments']
                if args.cmd in ('tick', 'wait'):
                    found = events(assignments, now)
                    elapsed = time.monotonic() - started
                    if args.cmd == 'tick' or found or elapsed >= args.max_wait:
                        save(args.state, data)
                        out = {'events': found}
                        if args.cmd == 'wait':
                            out['wait_seconds'] = min(elapsed, args.max_wait)
                        break
                elif args.cmd == 'register':
                    if not args.id or args.id in assignments or args.deadline <= now or args.checkpoint <= 0 or args.grace < 0:
                        raise ValueError('duplicate ID or invalid deadline/checkpoint/grace')
                    assignments[args.id] = dict(id=args.id, agent=args.agent, task=args.task, route=args.route, status='active', phase='running', deadline=args.deadline, checkpoint_interval=args.checkpoint, checkpoint_grace=args.grace, next_checkpoint=add_time(now, args.checkpoint), extension_used=False, stop_confirmed=False, transferred=False)
                    out = {'registered': args.id}
                elif args.cmd == 'list':
                    out = {'assignments': list(assignments.values())}
                else:
                    if args.id not in assignments:
                        raise ValueError('unknown assignment')
                    a = assignments[args.id]
                    if args.cmd in ('checkpoint', 'extend'):
                        if a['status'] != 'active':
                            raise ValueError('assignment is not active')
                        # Refuse late actions even if no tick has processed the expiry.
                        if (a['phase'] in ('checkpoint', 'decision') and now >= a['phase_deadline']) or (a['phase'] == 'extended' and now >= a['deadline']) or (a['phase'] == 'running' and now >= a['deadline']):
                            raise ValueError('deadline expired; run tick for host action')
                    if args.cmd == 'checkpoint':
                        if a['phase'] not in ('running', 'checkpoint', 'extended'):
                            raise ValueError('checkpoint unavailable')
                        if args.eta is not None:
                            a['eta'] = args.eta
                        a['next_checkpoint'] = add_time(now, a['checkpoint_interval'])
                        if a['phase'] == 'checkpoint':
                            a['phase'] = 'decision'
                            a['phase_deadline'] = add_time(now, a['checkpoint_grace'])
                        out = {'checkpointed': args.id}
                    elif args.cmd == 'extend':
                        if a['phase'] != 'decision' or a['extension_used'] or args.eta <= max(a['deadline'], now):
                            raise ValueError('extension unavailable or ETA must exceed current deadline and time')
                        a.update(deadline=args.eta, extension_used=True, phase='extended')
                        a.pop('phase_deadline', None)
                        out = {'extended_to': args.eta}
                    elif args.cmd in ('complete', 'cancel'):
                        if a['status'] != 'active':
                            raise ValueError('assignment is not active')
                        a['status'] = 'completed' if args.cmd == 'complete' else 'cancelled'
                        out = {'status': a['status']}
                    elif args.cmd == 'confirm-stopped':
                        if args.confirmation != 'worker-and-writes-stopped' or a['stop_confirmed']:
                            raise ValueError('explicit worker and write shutdown confirmation required')
                        a['stop_confirmed'] = True
                        a['phase'] = 'stop'
                        out = {'stop_confirmed': True}
                    elif args.cmd == 'transfer':
                        if not a['stop_confirmed'] or a['transferred']:
                            raise ValueError('ownership transfer requires confirmed shutdown and must be new')
                        a['transferred'] = True
                        out = {'host_action': 'ownership transfer may now be performed by host'}
                if args.cmd not in ('tick', 'wait'):
                    save(args.state, data)
                    break
            time.sleep(min(.1, max(0, args.max_wait - (time.monotonic() - started))))
        print(json.dumps(out, sort_keys=True), flush=True)
        return 0
    except BrokenPipeError:
        raise
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    try:
        try:
            code = main()
        except SystemExit as exc:
            code = exc.code
        sys.stdout.flush()
        raise SystemExit(code)
    except BrokenPipeError:
        # Prevent a second flush error during interpreter shutdown.
        sys.stdout = open(os.devnull, 'w')
        raise SystemExit(1)
    except KeyboardInterrupt:
        print('interrupted', file=sys.stderr)
        raise SystemExit(130)

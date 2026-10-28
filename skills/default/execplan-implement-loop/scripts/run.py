#!/usr/bin/env python3
"""Execute a canonical ExecPlan through bounded Gemini iterations."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
import os
import time

from contracts import Plan, Stop
from reporting import make_blocker, readiness_blockers


def seconds(value):
    try:
        number = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError('Expected positive finite seconds') from error
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError('Expected positive finite seconds')
    return number


def arguments():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog='JSON summary on stdout; progress JSON events on stderr. Exit: 0 completed/valid, '
               '1 failed, 2 invalid, 3 blocked, 124 deadline, 130 SIGINT, 143 SIGTERM, 141 broken pipe. '
               'Resume preserves work and gives this invocation a fresh runtime budget.')
    parser.add_argument('plan', type=Path, help='canonical ExecPlan Markdown file')
    parser.add_argument('--max-runtime', type=seconds, default=3600, help='total runtime in seconds')
    parser.add_argument('--iteration-timeout', type=seconds, default=1200, help='maximum Gemini iteration seconds')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--resume', type=Path, help='recorded run directory to reconcile and continue')
    group.add_argument('--run-dir', type=Path, help='new state directory outside the worktree')
    parser.add_argument('--acknowledge-unclean-stop', action='store_true', help='operator confirms old children stopped and state inspected')
    parser.add_argument('--model', help='explicit Gemini model override; otherwise inherited')
    parser.add_argument('--approval-mode', choices=['default', 'auto_edit', 'yolo'], help='explicit Gemini permission policy; otherwise inherited')
    parser.add_argument('--gemini', default='gemini', help='Gemini executable path or name')
    validation = parser.add_mutually_exclusive_group()
    validation.add_argument('--validate-only', action='store_true', help='validate static contracts without executing commands')
    validation.add_argument('--doctor', action='store_true', help='diagnose local prerequisites without a provider prompt')
    parser.add_argument('--policy', type=Path, help='reviewed single-file Gemini policy TOML')
    args = parser.parse_args()
    if args.doctor and args.run_dir:
        parser.error('--doctor cannot be combined with --run-dir')
    if args.doctor and args.acknowledge_unclean_stop:
        parser.error('--doctor cannot acknowledge an unclean stop')
    if args.validate_only and args.policy is not None:
        parser.error('--policy is not used with --validate-only')
    return args


def main():
    started = time.monotonic()
    args = arguments()
    engine = None
    try:
        if args.doctor:
            from processes import Supervisor
            from readiness import collect_readiness
            with Supervisor(started + args.max_runtime) as supervisor:
                result = collect_readiness(plan_path=args.plan.resolve(), workspace=None,
                                           gemini=args.gemini, policy=args.policy,
                                           model=args.model, approval_mode=args.approval_mode,
                                           resume=args.resume, supervisor=supervisor)
            report = dict(schema_version=1, status='diagnosed', reason_code=result.reason_code,
                          readiness=result.readiness,
                          blockers=readiness_blockers(result.blockers, run_directory=args.resume,
                                                      plan_path=args.plan.resolve(),
                                                      run_script=Path(__file__).resolve()))
            print(json.dumps(report), flush=True)
            return result.exit_code
        if sys.version_info < (3, 12) or sys.platform not in ('darwin', 'linux'):
            raise Stop('unsupported_platform', 'Python 3.12+ on macOS or Linux required')
        plan = Plan(args.plan.resolve())
        if args.validate_only:
            result = dict(schema_version=1, status='valid', reason_code='valid_contract',
                          plan_id=plan.data['plan_id'], immutable_hash=plan.immutable_hash(),
                          blockers=[],
                          task_counts=dict(total=len(plan.tasks), done=sum(t['state'] == 'done' for t in plan.tasks.values())))
            print(json.dumps(result))
            return 0
        from engine import Engine
        from processes import Supervisor
        with Supervisor(started + args.max_runtime) as supervisor:
            engine = Engine(args, plan, supervisor, started)
            try:
                status, reason, code = engine.execute()
                report = engine.report(status, reason)
            except BrokenPipeError:
                raise
            except (OSError, Stop, ValueError) as error:
                code = error.code if isinstance(error, Stop) else 2
                reason = error.reason if isinstance(error, Stop) else 'io_or_state_error'
                status = {2: 'invalid', 3: 'blocked', 124: 'deadline', 130: 'interrupted', 143: 'interrupted'}.get(code, 'failed')
                engine.event(status, reason_code=reason)
                report = engine.report(status, reason, str(error))
            finally:
                engine.close()
            print(json.dumps(report), flush=True)
            return code
    except BrokenPipeError:
        raise
    except (OSError, Stop, ValueError) as error:
        code = error.code if isinstance(error, Stop) else 2
        reason = error.reason if isinstance(error, Stop) else 'io_error'
        plan_path = args.plan.resolve()
        print(json.dumps(dict(schema_version=1, status='blocked' if code == 3 else 'invalid',
                              reason_code=reason, detail=str(error),
                              blockers=[make_blocker(reason, run_directory=args.resume,
                                                     plan_path=plan_path, run_script=Path(__file__).resolve(),
                                                     fallback_source='preflight')])))
        return code


def entrypoint():
    try:
        return main()
    except BrokenPipeError:
        with open(os.devnull, 'w') as sink:
            os.dup2(sink.fileno(), sys.stdout.fileno())
            os.dup2(sink.fileno(), sys.stderr.fileno())
        return 141


if __name__ == '__main__':
    raise SystemExit(entrypoint())

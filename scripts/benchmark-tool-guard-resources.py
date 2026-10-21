#!/usr/bin/env python3
"""Collect macOS full-process elapsed samples and separate peak-RSS evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

from tool_guard_corpus import PROVIDERS, script_path
from hook_benchmark_support import (
    collect_macos_rss, disposable_environment, guardian_runtime_footprint,
    prepare_failure, verify_audit, guardian_decision, guardian_canonical_paths,
    guardian_benchmark_environment, guardian_response_matches,
)
from fixtures.tool_guard_resource_cases import (
    FIXTURE_SETS, DEFAULT_EXPECTATIONS, resource_cases,
    validate_response, ResourceCase, historical_fixtures as fixtures, payload,
)


ROOT = Path(__file__).resolve().parents[1]


def checked_run(command: list[str], data: bytes, env: dict[str, str], provider: str, expected: str, *, cwd: Path | None = None, contract: dict | None = None) -> subprocess.CompletedProcess:
    start = time.perf_counter_ns()
    result = subprocess.run(command, input=data, capture_output=True, env=env, cwd=cwd, timeout=5)
    result.elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
    try:
        output = json.loads(result.stdout)
        if not guardian_response_matches(provider, result.returncode, output, expected, contract=contract):
            raise RuntimeError(f'{provider}: expected {expected}, exit {result.returncode}, output {result.stdout[:1024]!r}, collector stderr {result.stderr[:1024]!r}')
    except (RuntimeError, ValueError, UnicodeDecodeError) as exc:
        exc.invocation = {"elapsed_ms": result.elapsed_ms, "exit_code": result.returncode,
                          "stdout": result.stdout[:1024].decode("utf-8", errors="replace"),
                          "stderr": result.stderr[:1024].decode("utf-8", errors="replace")}
        raise
    return result


def fingerprints(root: Path) -> dict[str, str]:
    scripts, helpers, _canonical = guardian_runtime_footprint()
    paths = {root / path for path in scripts}
    for helper in helpers:
        paths.update((root / helper).rglob('*.py'))
    for source in [*(root / name for name in guardian_canonical_paths()), *(root / "hooks/runtime").rglob("*.py")]:
        if source.is_file():
            paths.add(source)
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def selected_cases(root: Path, fixture_set: str, expectations: Path | None, condition: str):
    return resource_cases(root, fixture_set, expectations, condition)


def harness_fingerprints(expectations: Path | None) -> dict:
    names = ("benchmark-tool-guard-resources.py", "hook_benchmark_support.py", "tool_guard_corpus.py",
             "fixtures/tool_guard_resource_cases.py", "fixtures/tool_guard_vectors.py")
    result = {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest() for name in names}
    result["reviewed_expectations"] = hashlib.sha256((expectations or DEFAULT_EXPECTATIONS).read_bytes()).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--script-root', type=Path, default=ROOT)
    parser.add_argument('--fixture-set', choices=FIXTURE_SETS, default='historical-v1')
    parser.add_argument('--expectations', type=Path)
    parser.add_argument('--condition', choices=('baseline', 'candidate'), default='candidate')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--samples', type=int, default=25)
    parser.add_argument('--warmups', type=int, default=3)
    parser.add_argument('--ceiling-ms', type=float, default=500, help='accepted finite-case latency ceiling')
    args = parser.parse_args()
    if args.fixture_set != 'historical-v1' and args.expectations is None:
        parser.error('--expectations is required for an explicit new fixture set')
    root = args.script_root.resolve()
    try:
        cases = selected_cases(root, args.fixture_set, args.expectations, args.condition)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    if args.list:
        print(json.dumps([{'case': case.name, 'input_sha256': hashlib.sha256(case.payload).hexdigest(),
                           **case.fixture_metadata['contract']} for case in cases], indent=2))
        return 0
    if args.output is None:
        parser.error('--output is required')
    if args.output.exists():
        parser.error('--output already exists; retain original evidence and choose a new path')
    if platform.system() != 'Darwin':
        parser.error('peak-RSS collector requires native macOS /usr/bin/time -l')
    if args.samples < 5 or args.warmups < 0 or args.ceiling_ms <= 0:
        parser.error('samples must be at least 5; warmups nonnegative; ceiling positive')
    missing = [str(script_path(root, provider)) for provider in PROVIDERS if not script_path(root, provider).is_file()]
    if missing:
        parser.error('missing hook entrypoints: ' + ', '.join(missing))
    before = fingerprints(root)
    harness = harness_fingerprints(args.expectations)
    report = {'environment': {'platform': platform.platform(), 'python': platform.python_version(),
                              'python_executable': sys.executable, 'machine': platform.machine()},
              'method': {'script_root': str(root), 'samples': args.samples, 'warmups': args.warmups,
                         'fixture_set': args.fixture_set, 'condition': args.condition,
                         'latency_command': 'direct Python launch; audit verification outside elapsed',
                         'memory_command': 'separate /usr/bin/time -l Python launch; macOS RSS in bytes',
                         'first_run': 'fresh log home; operating-system caches uncleared'},
              'script_sha256': before, 'harness_sha256': harness, 'results': [], 'errors': []}
    try:
        with tempfile.TemporaryDirectory(prefix='tool-guard-resources-') as temporary:
            for case in cases:
                provider = case.name.split('.')[0]
                home = Path(temporary) / case.name
                home.mkdir(parents=True)
                current = prepare_failure(case, home)
                env = disposable_environment(home, provider)
                env.update({**guardian_benchmark_environment(),
                            'COPILOT_OBSERVABILITY_LOG_PATH': str(home / 'copilot-observability.ndjson'),
                            'GEMINI_OBSERVABILITY_LOG_PATH': str(home / 'gemini-observability.ndjson'),
                            **current.environment})
                command = [sys.executable, str(current.script)]
                contract = case.fixture_metadata['contract']
                row = {'case': case.name, 'input_bytes': len(case.payload),
                       'input_sha256': hashlib.sha256(case.payload).hexdigest(),
                       'contract': contract, 'fixture_metadata': case.fixture_metadata, 'expected_decision': case.expected_decision,
                       'samples_ms': [], 'outputs': [], 'ceiling_ms': args.ceiling_ms}
                report['results'].append(row)
                calls = 0
                def launch(argv):
                    nonlocal calls
                    output = checked_run(argv, case.payload, env, provider, case.expected_decision, contract=contract)
                    calls += 1
                    return output
                for index in range(1 + args.warmups + args.samples):
                    output = launch(command)
                    elapsed = output.elapsed_ms
                    if index == 0:
                        row['first_run_ms'] = elapsed
                        row['first_output'] = json.loads(output.stdout)
                    elif index > args.warmups:
                        row['samples_ms'].append(elapsed)
                        row['outputs'].append(json.loads(output.stdout))
                memory, rss = collect_macos_rss(command, launch)
                if rss is None:
                    row['rss_collector_stderr'] = memory.stderr.decode('utf-8', errors='replace')[:1024]
                    raise RuntimeError('macOS time did not report peak resident set size')
                proof = verify_audit(home, current, calls)
                row['logging'] = proof
                if proof['records'] != proof['required_records']:
                    raise ValueError('unexpected completed audit record count')
                timings = row['samples_ms']
                median = statistics.median(timings)
                row.update({'actual_decision': guardian_decision(provider, json.loads(output.stdout), contract=contract),
                            'median_ms': median, 'p95_ms': sorted(timings)[max(0, math.ceil(len(timings) * .95) - 1)],
                            'mad_ms': statistics.median(abs(sample - median) for sample in timings),
                            'peak_rss_bytes': rss, 'ceiling_met': max(row['first_run_ms'], *timings) <= args.ceiling_ms})
    except (Exception, KeyboardInterrupt) as exc:
        report['errors'].append(f'{type(exc).__name__}: {exc}')
        if hasattr(exc, 'invocation'):
            report['failed_invocation'] = {'case': case.name, **exc.invocation}
    finally:
        try:
            report['sources_unchanged'] = before == fingerprints(root) and harness == harness_fingerprints(args.expectations)
            if not report['sources_unchanged']:
                report['errors'].append('hook or harness sources changed during resource measurement')
        except OSError as exc:
            report['sources_unchanged'] = False
            report['errors'].append(str(exc))
        report['gates_met'] = not report['errors'] and len(report['results']) == len(cases) and all(row.get('ceiling_met', False) for row in report['results'])
        with args.output.open('x', encoding='utf-8') as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write('\n')
    return 0 if report['gates_met'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

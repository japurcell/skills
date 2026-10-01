#!/usr/bin/env python3
"""Collect macOS full-process elapsed samples and separate peak-RSS evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shlex
import statistics
import subprocess
import sys
import tempfile
import time

from tool_guard_corpus import PROVIDERS, decision, script_path

ROOT = Path(__file__).resolve().parents[1]
SHELL_TOOLS = {'copilot': 'bash', 'gemini': 'run_shell_command', 'codex': 'Bash'}


def fixtures(provider: str) -> list[tuple[str, str, object, str]]:
    shell = SHELL_TOOLS[provider]
    cases = [
        ('strict-max', 'X', 'x' * 32766, 'allow'),
        ('strict-overflow', 'X', 'x' * 32767, 'deny'),
        ('strict-utf8-max', 'X', '界' * 10922, 'allow'),
        ('normalized-max', 'X', "'" + '\u0958' * 5460 + 'xxxx' + "'", 'allow'),
        ('normalized-overflow', 'X', "'" + '\u0958' * 5460 + 'xxxxx' + "'", 'deny'),
        ('quoted-max', shell, {'command': "echo '" + 'x' * 32754 + "'"}, 'allow'),
        ('tokens-max', shell, {'command': ' '.join(['x'] * 256)}, 'allow'),
        ('tokens-overflow', shell, {'command': ' '.join(['x'] * 257)}, 'deny'),
        ('commands-max', shell, {'command': ';'.join(['x'] * 128)}, 'allow'),
        ('commands-overflow', shell, {'command': ';'.join(['x'] * 129)}, 'deny'),
        ('quoted-tokens-max', shell, {'command': "echo '" + 'x ' * 255 + "'"}, 'allow'),
        ('quoted-tokens-overflow', shell, {'command': "echo '" + 'x ' * 256 + "'"}, 'deny'),
        ('heredoc-tokens-max', shell, {'command': "cat <<'EOF'\n" + 'x ' * 254 + '\nEOF'}, 'allow'),
        ('heredoc-tokens-overflow', shell, {'command': "cat <<'EOF'\n" + 'x ' * 255 + '\nEOF'}, 'deny'),
        ('structure-nodes-max', 'unknown_tool', [0] * 255, 'allow'),
        ('structure-wide-overflow', 'unknown_tool', [0] * 30000, 'deny'),
        ('substitution-depth-max', shell, {'command': 'echo $(' * 16 + 'x' + ')' * 16}, 'allow'),
        ('substitution-depth-overflow', shell, {'command': 'echo $(' * 17 + 'x' + ')' * 17}, 'deny'),
    ]
    writer = 'from pathlib import Path;Path("x").write_text('
    assignment = 'from pathlib import Path;Path("x").write_text("safe");a='
    for name, source, expected in (
        ('python-syntax-max', writer + '"x"' * 1011 + ')', 'allow'),
        ('python-syntax-overflow', writer + '"x"' * 1012 + ')', 'deny'),
        ('python-literal-token-max', assignment + '"x"' * 1007, 'allow'),
        ('python-literal-token-overflow', assignment + '"x"' * 1008, 'deny'),
        ('python-ast-depth-max', 'x+' * 29 + 'x', 'allow'),
        ('python-ast-depth-overflow', 'x+' * 30 + 'x', 'deny'),
        ('python-decoded-literal', "x='" + '\\u754c' * 2000 + "'", 'allow')):
        cases.append((name, shell, {'command': 'python3 -c ' + shlex.quote(source)}, expected))
    resolved = "a='" + 'x' * 1024 + "';b=a+a;c=b+b;d=c+c;e=d+d;f=e+e"
    cases.extend((('python-resolved-max', shell, {'command': 'python3 -c ' + shlex.quote(resolved)}, 'allow'),
                  ('python-resolved-overflow', shell, {'command': 'python3 -c ' + shlex.quote(resolved + ';g=f+"x"')}, 'deny')))
    if provider in {'copilot', 'gemini'}:
        tool, path_key, body_key = ('create', 'path', 'file_text') if provider == 'copilot' else ('write_file', 'file_path', 'content')
        available = 65536 - len(path_key + body_key + 'example.txt')
        body = '界' * (available // 3) + 'x' * (available % 3)
        cases.extend((('native-max', tool, {path_key: 'example.txt', body_key: body}, 'allow'),
                      ('native-overflow', tool, {path_key: 'example.txt', body_key: body + 'x'}, 'deny')))
    if provider == 'codex':
        prefix, suffix = '*** Begin Patch\n*** Add File: example.txt\n+', '\n*** End Patch'
        patch = prefix + 'x' * (65536 - len('command' + prefix + suffix)) + suffix
        path = '\ufdfa' * 496 + 'x' * 16
        operations = '*** Begin Patch\n*** Delete File: ' + path + '\n*** Delete File: ' + path + '\n*** End Patch'
        cases.extend((('native-max', 'apply_patch', {'command': patch}, 'allow'),
                      ('native-overflow', 'apply_patch', {'command': patch.replace('+x', '+xx', 1)}, 'deny'),
                      ('operation-normalized-max', 'apply_patch', {'command': operations}, 'allow'),
                      ('operation-normalized-overflow', 'apply_patch', {'command': operations.replace(path + '\n*** End', path + 'x\n*** End')}, 'deny')))
    if provider == 'copilot':
        cases.append(('native-wide-paths-overflow', 'grep', {'pattern': 'safe', 'paths': ['docs'] * 30000}, 'deny'))
    return cases


def payload(provider: str, tool: str, value: object) -> bytes:
    event = {'toolName': tool, 'toolArgs': value} if provider == 'copilot' else {'tool_name': tool, 'tool_input': value}
    event['hook_event_name'] = 'BeforeTool' if provider == 'gemini' else 'PreToolUse'
    return json.dumps(event, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def checked_run(command: list[str], data: bytes, env: dict[str, str], provider: str, expected: str) -> subprocess.CompletedProcess:
    result = subprocess.run(command, input=data, capture_output=True, env=env, timeout=5)
    if result.returncode or decision(provider, json.loads(result.stdout)) != expected:
        raise RuntimeError(f'{provider}: expected {expected}, exit {result.returncode}, output {result.stdout[:1024]!r}')
    return result


def fingerprints(root: Path) -> dict[str, str]:
    paths = {script_path(root, provider) for provider in PROVIDERS}
    for script in tuple(paths):
        paths.update((script.parent / 'helpers').rglob('*.py'))
    source = root / 'hooks/families/tool_guard.py'
    if source.is_file():
        paths.add(source)
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--script-root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--samples', type=int, default=25)
    parser.add_argument('--warmups', type=int, default=3)
    parser.add_argument('--ceiling-ms', type=float, required=True, help='documented ceiling derived from retained existing workloads')
    args = parser.parse_args()
    if platform.system() != 'Darwin':
        parser.error('peak-RSS collector requires native macOS /usr/bin/time -l')
    if args.samples < 5 or args.warmups < 0 or args.ceiling_ms <= 0:
        parser.error('samples must be at least 5; warmups nonnegative; ceiling positive')
    root = args.script_root.resolve()
    missing = [str(script_path(root, provider)) for provider in PROVIDERS if not script_path(root, provider).is_file()]
    if missing:
        parser.error('missing hook entrypoints: ' + ', '.join(missing))
    before = fingerprints(root)
    results = []
    with tempfile.TemporaryDirectory(prefix='tool-guard-resources-') as temporary:
        for provider in PROVIDERS:
            for name, tool, value, expected in fixtures(provider):
                home = Path(temporary) / provider / name
                home.mkdir(parents=True)
                env = {**os.environ, 'HOME': str(home), 'XDG_CONFIG_HOME': str(home / '.config'),
                       'XDG_CACHE_HOME': str(home / '.cache'), 'XDG_DATA_HOME': str(home / '.local/share'),
                       'AUDIT_LOG': str(home / 'audit.log'), 'AUDIT_LOCK': str(home / 'audit.lock'),
                       'GUARD_MODE': 'block', 'TOOL_GUARD_LOG_DIR': str(home / 'guard' if provider == 'gemini' else home / 'guard.log')}
                env.pop('SKIP_TOOL_GUARD', None)
                env.pop('TOOL_GUARD_ALLOWLIST', None)
                command = [sys.executable, str(script_path(root, provider))]
                data, timings, first = payload(provider, tool, value), [], None
                for index in range(1 + args.warmups + args.samples):
                    start = time.perf_counter_ns()
                    output = checked_run(command, data, env, provider, expected)
                    elapsed = (time.perf_counter_ns() - start) / 1_000_000
                    if index == 0:
                        first = elapsed
                    elif index > args.warmups:
                        timings.append(elapsed)
                memory = checked_run(['/usr/bin/time', '-l', *command], data, env, provider, expected)
                match = re.search(rb'([0-9]+)\s+maximum resident set size', memory.stderr)
                if match is None:
                    raise RuntimeError('macOS time did not report peak resident set size')
                median = statistics.median(timings)
                results.append({'case': f'{provider}.resources.{name}', 'input_bytes': len(data),
                                'expected_decision': expected, 'actual_decision': decision(provider, json.loads(output.stdout)),
                                'first_run_ms': first, 'samples_ms': timings, 'median_ms': median,
                                'p95_ms': sorted(timings)[max(0, math.ceil(len(timings) * .95) - 1)],
                                'mad_ms': statistics.median(abs(sample - median) for sample in timings),
                                'peak_rss_bytes': int(match.group(1)), 'ceiling_ms': args.ceiling_ms,
                                'ceiling_met': max([first, *timings]) <= args.ceiling_ms})
    after = fingerprints(root)
    if before != after:
        raise RuntimeError('hook source changed during resource measurement')
    report = {'environment': {'platform': platform.platform(), 'python': platform.python_version(),
                              'python_executable': sys.executable, 'machine': platform.machine()},
              'method': {'script_root': str(root), 'samples': args.samples, 'warmups': args.warmups,
                         'latency_command': 'same direct Python launch as fixed corpus runner',
                         'memory_command': 'separate /usr/bin/time -l Python launch; macOS RSS in bytes',
                         'first_run': 'fresh log home; operating-system caches uncleared',
                         'ceiling_basis': 'caller-supplied and documented against retained existing workload'},
              'script_sha256': before, 'results': results}
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return 0 if all(result['ceiling_met'] for result in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())

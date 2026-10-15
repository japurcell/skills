import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys
import time
from unittest import mock

ROOT = Path(sys.argv[1]).resolve()
OUTPUT = Path(sys.argv[2])
spec = importlib.util.spec_from_file_location('scanner_fixture', ROOT / 'scripts/test-scan-secrets-merge.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
REAL_RUN = subprocess.run
SIZE = 8 * 1024 * 1024

def fingerprints():
    paths = set(ROOT.joinpath('hooks').rglob('*.py'))
    for script in fixture.HOOKS.values():
        paths.add(script)
        paths.update(script.parent.joinpath('helpers').rglob('*.py'))
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths)}

def setup_case(name):
    case = fixture.MergeScannerTests()
    case.setUp()
    case.env.update({'HOME': str(case.root), 'XDG_CONFIG_HOME': str(case.root / 'config'),
                     'XDG_CACHE_HOME': str(case.root / 'cache'), 'XDG_DATA_HOME': str(case.root / 'data'),
                     'AUDIT_LOCK': str(case.root / 'audit.lock'),
                     'AUDIT_LOG_MAX_BYTES': '1048576', 'AUDIT_LOG_MAX_BACKUPS': '3'})
    path = case.repo / 'safe.txt'
    if name == 'long-line-8MiB':
        path.write_bytes(b'q' * SIZE)
    elif name == 'empty-lines-8MiB':
        path.write_bytes(b'\n' * SIZE)
    elif name in ('short-lines-8MiB', 'short-lines-2030848'):
        path.write_bytes(b'x\n' * ((SIZE if name.endswith('8MiB') else 2030848) // 2))
    elif name == 'binary-8MiB':
        path.write_bytes(b'\0' + b'q' * (SIZE - 1))
    elif name == 'greedy-token-8MiB':
        path.write_bytes(b'github_pat_' + b'A' * (SIZE - 11))
    elif name == 'snapshots-256-8MiB':
        for index in range(256):
            (case.repo / f'safe-{index:03}.txt').write_bytes(b'q' * (SIZE // 256))
    elif name == 'tracked-tiny-edit-2030848':
        path.write_bytes(b'q' * 2030847 + b'\n')
        case.git('add', '--all')
        case.git('commit', '-qm', 'safe baseline')
        with path.open('ab') as handle:
            handle.write(b'tiny change\n')
    return case

def invoke(case, provider, memory=False):
    measurement = {}
    def measured(command, **kwargs):
        payload = json.loads(kwargs['input'])
        if provider == 'codex':
            payload['tool_input'] = {'cmd': 'git status', 'login': False}
            kwargs['input'] = json.dumps(payload)
        started = time.perf_counter_ns()
        result = REAL_RUN((['/usr/bin/time', '-l'] if memory else []) + command, **kwargs)
        measurement['elapsed_ms'] = (time.perf_counter_ns() - started) / 1_000_000
        if memory:
            found = re.search(r'(\d+)\s+maximum resident set size', result.stderr)
            if not found:
                raise RuntimeError('native macOS RSS unavailable: ' + result.stderr[:200])
            measurement['peak_rss_bytes'] = int(found.group(1))
        return result
    with mock.patch.object(fixture.subprocess, 'run', measured):
        response, record = case.scan(provider)
    expected = 'findings' if current_name == 'greedy-token-8MiB' else 'clean'
    assert record['status'] == expected, (provider, current_name, record['status'], record.get('diagnostic'))
    if expected == 'clean':
        assert response == {}, response
    else:
        assert 'deny' in json.dumps(response), response
        assert record['findings'][0]['pattern'] == 'github_fine_grained_pat'
    measurement['security_status'] = record['status']
    return measurement

before = fingerprints()
report = {'environment': {'platform': platform.platform(), 'python': sys.version,
          'python_executable': sys.executable},
          'commit': REAL_RUN(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True,
                             capture_output=True, check=True).stdout.strip(),
          'source_fingerprints': before,
          'method': {'samples_per_case': 3, 'command_flags': ['-I', '-S', '-B'],
          'elapsed': 'complete scanner subprocess only; fixture setup and log verification excluded',
          'memory': 'separate native /usr/bin/time -l invocation; RSS bytes; wrapper latency excluded',
          'cache': 'OS and standard-library caches uncleared; provider bytecode disabled',
          'logging': 'disposable provider log, checked after every call',
          'limits': '8 MiB logical candidate bytes, 256 snapshots, 8 second shared work/input budget'},
          'cases': [], 'failures': []}
names = ['long-line-8MiB', 'empty-lines-8MiB', 'short-lines-8MiB', 'short-lines-2030848',
         'binary-8MiB', 'greedy-token-8MiB', 'snapshots-256-8MiB', 'tracked-tiny-edit-2030848']
for current_name in names:
    case = setup_case(current_name)
    try:
        for provider in fixture.PROVIDERS:
            try:
                samples = [invoke(case, provider) for _ in range(3)]
                memory = invoke(case, provider, memory=True)
                durations = [sample['elapsed_ms'] for sample in samples]
                row = {'case': current_name, 'provider': provider, 'samples_ms': durations,
                       'first_ms': durations[0], 'median_ms': statistics.median(durations),
                       'maximum_ms': max(durations), 'peak_rss_bytes': memory['peak_rss_bytes'],
                       'security_status': memory['security_status']}
                report['cases'].append(row)
                print(json.dumps({key: row[key] for key in ('case', 'provider', 'maximum_ms', 'peak_rss_bytes')}), flush=True)
            except Exception as error:
                report['failures'].append({'case': current_name, 'provider': provider,
                                           'error': str(error)[:500]})
    finally:
        case.doCleanups()
report['concurrency'] = []
current_name = 'short-lines-2030848'
case = setup_case(current_name)
try:
    for provider in fixture.PROVIDERS:
        logs = case.root / ('concurrency-' + provider)
        logs.mkdir(mode=0o700)
        env = {**case.env, 'SCAN_MODE': 'block', 'SCAN_SCOPE': 'diff',
               'SECRETS_LOG_DIR': str(logs), 'AUDIT_LOG': str(logs / 'audit.log'),
               'AUDIT_LOCK': str(logs / 'audit.lock'), 'OBSERVABILITY_TESTING': '1',
               'OBSERVABILITY_LOG_PATH': str(logs / 'observability.jsonl'), 'TMPDIR': str(case.root)}
        if provider == 'copilot':
            payload = {'sessionId': 'resource-concurrency', 'hook_event_name': 'preToolUse',
                       'toolName': 'bash', 'toolArgs': {'command': 'git status'}}
        else:
            payload = {'session_id': 'resource-concurrency', 'cwd': str(case.repo),
                       'hook_event_name': 'BeforeTool' if provider == 'gemini' else 'PreToolUse',
                       'tool_name': 'run_shell_command' if provider == 'gemini' else 'exec_command',
                       'tool_input': {'command': 'git status'} if provider == 'gemini'
                                     else {'cmd': 'git status', 'login': False}}
        def concurrent_call(_):
            start = time.perf_counter_ns()
            result = REAL_RUN([sys.executable, '-I', '-S', '-B', str(fixture.HOOKS[provider])],
                              input=json.dumps(payload), text=True, capture_output=True,
                              cwd=case.repo, env=env, timeout=12)
            elapsed = (time.perf_counter_ns() - start) / 1_000_000
            assert result.returncode == 0 and json.loads(result.stdout) == {}, provider
            return elapsed
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                durations = list(pool.map(concurrent_call, range(2)))
            records = [json.loads(line) for line in (logs / 'scan.log').read_text().splitlines()]
            assert len(records) == 2 and all(row['status'] == 'clean' for row in records), provider
            report['concurrency'].append({'provider': provider, 'case': current_name,
                                          'calls': 2, 'samples_ms': durations, 'logged_clean': 2})
        except Exception as error:
            report['failures'].append({'case': 'concurrent-' + current_name,
                                       'provider': provider, 'error': str(error)[:500]})
finally:
    case.doCleanups()
report['fingerprints_unchanged'] = before == fingerprints()
assert report['fingerprints_unchanged'], 'source changed during measurement'
OUTPUT.write_text(json.dumps(report, indent=2) + '\n')
raise SystemExit(bool(report['failures']))

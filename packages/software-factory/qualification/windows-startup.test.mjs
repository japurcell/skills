import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { gitModes, includedConfigQuery, parseTrace, selectLaunchMode, validateModules, validateStopTrace, validateTrace } from './windows-startup.mjs';

test('qualification accepts only the two fixed native launch modes', () => {
  assert.equal(selectLaunchMode(), 'no-window');
  assert.equal(selectLaunchMode('no-window'), 'no-window');
  assert.equal(selectLaunchMode('detached-process'), 'detached-process');
  for (const value of ['', 'debug-only-this-process', 'detached-process+no-window', 'DETACHED_PROCESS'])
    assert.throws(() => selectLaunchMode(value), /unsupported qualification launch mode/);
});

test('PowerShell bridge refuses an unknown launch mode before native interop', (t) => {
  const base = mkdtempSync(join(tmpdir(), 'windows-startup-mode-'));
  t.after(() => rmSync(base, { recursive: true, force: true }));
  const powershell = process.platform === 'win32'
    ? join(process.env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe')
    : 'pwsh';
  const specPath = join(base, 'spec.json');
  const script = fileURLToPath(new URL('./windows-startup-trace.ps1', import.meta.url));
  for (const [index, launchMode] of ['debug-only-this-process', 'NO-WINDOW'].entries()) {
    const stagePath = join(base, `stages-${index}.tsv`);
    writeFileSync(specPath, JSON.stringify({ launchMode }));
    const invocation = spawnSync(powershell, ['-NoProfile', '-NonInteractive', '-File', script,
      '-SpecPath', specPath, '-StagePath', stagePath],
    { encoding: 'utf8', timeout: 15000, maxBuffer: 8192 });
    if (process.platform !== 'win32' && invocation.error?.code === 'ENOENT') {
      t.skip('PowerShell is unavailable on this non-Windows host');
      return;
    }
    assert.ifError(invocation.error);
    assert.equal(invocation.status, 4);
    assert.deepEqual(readFileSync(stagePath, 'utf8').trim().split('\n').map((row) => row.split('\t')[1]),
      ['ps-entry', 'spec-read', 'ps-error']);
    assert.match(invocation.stderr, /unsupported qualification launch mode/);
  }
});

test('PowerShell launcher retains an entry marker and bounded failure when spec loading fails', (t) => {
  const base = mkdtempSync(join(tmpdir(), 'windows-startup-entry-'));
  t.after(() => rmSync(base, { recursive: true, force: true }));
  const powershell = process.platform === 'win32'
    ? join(process.env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe')
    : 'pwsh';
  const stagePath = join(base, 'stages.tsv');
  const script = fileURLToPath(new URL('./windows-startup-trace.ps1', import.meta.url));
  const invocation = spawnSync(powershell, ['-NoProfile', '-NonInteractive', '-File', script,
    '-SpecPath', join(base, 'missing.json'), '-StagePath', stagePath],
  { encoding: 'utf8', timeout: 15000, maxBuffer: 8192 });
  if (process.platform !== 'win32' && invocation.error?.code === 'ENOENT') {
    t.skip('PowerShell is unavailable on this non-Windows host');
    return;
  }
  assert.ifError(invocation.error);
  assert.equal(invocation.status, 4);
  const stages = readFileSync(stagePath, 'utf8').trim().split('\n')
    .map((row) => row.split('\t')[1]);
  assert.deepEqual(stages, ['ps-entry', 'ps-error']);
  assert.ok(invocation.stderr.length > 0 && invocation.stderr.length < 8192);
});

test('closed Git modes have exact native argv and no caller flags', () => {
  assert.deepEqual(gitModes, [
    ['--no-pager', '--no-lazy-fetch', 'rev-parse', '--show-toplevel'],
    ['--no-pager', '--no-lazy-fetch', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
    ['--no-pager', '--no-lazy-fetch', 'rev-parse', '--path-format=absolute', '--git-dir'],
    ['--no-pager', '--no-lazy-fetch', 'worktree', 'list', '--porcelain', '-z'],
  ]);
});

test('trace requires a positive child control and complete direct exit', () => {
  const b64 = (text) => Buffer.from(text).toString('base64');
  const root = `ROOT\t10\t${b64('C:\\root.exe')}`;
  const created = `CREATE\t10\t${b64('C:\\root.exe')}`;
  const child = `CREATE\t11\t${b64('C:\\child.exe')}`;
  const exit = `EXIT\t10\t${b64('0')}`;
  const done = `DONE\t10\t${b64('0')}`;
  assert.equal(validateTrace(parseTrace([root, created, exit, done].join('\n')), 10, false).ok, true);
  assert.equal(validateTrace(parseTrace([root, created, child, exit, done].join('\n')), 10, false).ok, false);
  assert.equal(validateTrace(parseTrace([root, created, child, `EXIT\t11\t${b64('0')}`, exit, done].join('\n')), 10, true).ok, true);
  assert.equal(validateTrace(parseTrace([root, created, exit].join('\n')), 10, false).ok, false);
});

test('positive control requires the intended child image, not an incidental console host', () => {
  const b64 = (text) => Buffer.from(text).toString('base64');
  const rows = (childImage) => parseTrace([
    `ROOT\t10\t${b64('C:\\Windows\\System32\\cmd.exe')}`,
    `CREATE\t10\t${b64('\\\\?\\C:\\Windows\\System32\\cmd.exe')}`,
    `CREATE\t11\t${b64(childImage)}`,
    `EXIT\t11\t${b64('0')}`,
    `EXIT\t10\t${b64('0')}`,
    `DONE\t10\t${b64('0')}`,
  ].join('\n'));
  const intended = 'C:\\Windows\\System32\\cmd.exe';
  assert.equal(validateTrace(rows('\\\\?\\C:\\Windows\\System32\\conhost.exe'), 10, true, intended).ok, false);
  assert.equal(validateTrace(rows('\\\\?\\C:\\Windows\\System32\\cmd.exe'), 10, true, intended).ok, true);
});

test('stop control requires a complete termination sequence for every observed process', () => {
  const b64 = (value) => Buffer.from(value).toString('base64');
  const row = (kind, pid, value) => `${kind}\t${pid}\t${b64(value)}`;
  const records = [
    row('ROOT', 10, 'C:\\control.exe'),
    row('CREATE', 10, 'C:\\control.exe'),
    row('CREATE', 11, 'C:\\Windows\\System32\\conhost.exe'),
    row('STOP_REQUESTED', 10, 'deadline'),
    row('EXIT', 11, '124'),
    row('EXIT', 10, '124'),
    row('STOP_OBSERVED', 10, '124'),
    row('DONE', 10, 'stopped:124'),
  ];
  const check = (rows) => validateStopTrace(parseTrace(rows.join('\n')), 10, 'deadline');
  assert.equal(check(records).ok, true);
  assert.match(check(records.filter((record) => !record.startsWith('EXIT\t11\t'))).reasons.join('; '),
    /child exit unobserved/);
  assert.match(check(records.filter((record) => !record.startsWith('STOP_OBSERVED\t'))).reasons.join('; '),
    /stop completion unobserved/);
  assert.match(check(records.filter((record) => !record.startsWith('STOP_REQUESTED\t'))).reasons.join('; '),
    /missing stop request/);
  assert.match(check(records.slice(0, -1).concat(row('DONE', 10, '0'))).reasons.join('; '),
    /inconsistent completed debug loop/);
  assert.match(validateStopTrace(parseTrace(records.join('\n')), 10, 'output-limit').reasons.join('; '),
    /wrong stop reason/);
  assert.match(check(records.map((record) => record.startsWith('EXIT\t10\t')
    ? row('EXIT', 10, '0') : record)).reasons.join('; '), /root was not terminated with code 124/);
  assert.match(validateStopTrace(parseTrace(records.join('\n')), 10, 'deadline', 'C:\\other.exe').reasons.join('; '),
    /root image differs from control executable/);
});

test('each fixed helper needs resolved module evidence and each Git case needs its imported DLLs', (t) => {
  const base = mkdtempSync(join(tmpdir(), 'windows-startup-modules-'));
  t.after(() => rmSync(base, { recursive: true, force: true }));
  const packageRoot = join(base, 'package');
  const systemRoot = join(base, 'windows');
  const executable = join(packageRoot, 'mingw64', 'bin', 'git.exe');
  const systemDll = join(systemRoot, 'System32', 'kernel32.dll');
  mkdirSync(join(packageRoot, 'mingw64', 'bin'), { recursive: true });
  mkdirSync(join(systemRoot, 'System32'), { recursive: true });
  writeFileSync(executable, 'pinned executable');
  writeFileSync(systemDll, 'system module');
  const imported = ['libiconv-2.dll', 'libintl-8.dll', 'libpcre2-8-0.dll',
    'libwinpthread-1.dll', 'zlib1.dll'];
  const files = {};
  const modulePaths = imported.map((name) => {
    const member = `mingw64/bin/${name}`;
    const path = join(packageRoot, 'mingw64', 'bin', name);
    writeFileSync(path, name);
    files[member] = createHash('sha256').update(name).digest('hex');
    return path;
  });
  const archive = { root: packageRoot, files };
  const created = [{ kind: 'CREATE', pid: 10, value: executable }];
  const dll = (path) => ({ kind: 'DLL', pid: 10, value: path });

  assert.throws(() => validateModules(created, executable, archive, systemRoot),
    /no loaded module events/);
  assert.throws(() => validateModules([...created, { kind: 'DLL', pid: 99, value: systemDll }],
    executable, archive, systemRoot), /loaded module event belongs to unknown process/);
  assert.throws(() => validateModules([...created, dll(systemDll)], executable, archive, systemRoot, imported),
    /expected pinned Git dependency was not observed: libiconv-2\.dll/);
  assert.doesNotThrow(() => validateModules([...created, dll(systemDll), ...modulePaths.map(dll)],
    executable, archive, systemRoot, imported));
  assert.throws(() => validateModules([...created, dll('')], executable, archive, systemRoot),
    /unresolved loaded module path/);
  const unlisted = join(packageRoot, 'mingw64', 'bin', 'unlisted.dll');
  writeFileSync(unlisted, 'unlisted module');
  assert.throws(() => validateModules([...created, dll(unlisted)], executable, archive, systemRoot),
    /loaded module absent from pinned archive/);
  const unknown = join(base, 'unknown.dll');
  writeFileSync(unknown, 'unknown module');
  assert.throws(() => validateModules([...created, dll(unknown)],
    executable, archive, systemRoot), /loaded module outside pinned archive and Windows root/);
});

test('the private global config control reads an included value explicitly', (t) => {
  const base = mkdtempSync(join(tmpdir(), 'windows-startup-config-'));
  t.after(() => rmSync(base, { recursive: true, force: true }));
  const included = join(base, 'included config');
  const config = join(base, 'global config');
  writeFileSync(included, '[core]\n\tfsmonitor = owned-fixture-value\n');
  writeFileSync(config, `[include]\n\tpath = ${JSON.stringify(included.replaceAll('\\', '/'))}\n`);
  const result = spawnSync('git', includedConfigQuery, {
    cwd: base, env: { ...process.env, GIT_CONFIG_GLOBAL: config },
    encoding: 'utf8', timeout: 5000, maxBuffer: 8192,
  });
  assert.ifError(result.error);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), 'owned-fixture-value');
});

import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const entry = fileURLToPath(new URL('./windows-storage-loader-metadata-bootstrap.mjs', import.meta.url));
test('bootstrap fixed CLI refuses candidate arguments without echoing them', () => {
  const result = spawnSync(process.execPath, [entry, '--metadata-only', 'private-command-canary'], {
    encoding: 'utf8', timeout: 2000, maxBuffer: 4096, env: {},
  });
  assert.equal(result.error, undefined);
  assert.equal(result.status, 1);
  assert.equal(result.stderr, '');
  assert.deepEqual(JSON.parse(result.stdout), {
    scope: 'windows-storage-loader-metadata-bootstrap', schema: 1, state: 'blocked', reason: 'arguments',
    selectionAuthority: false, buildAuthority: false, nativeAuthority: false,
  });
  assert.doesNotMatch(result.stdout, /private-command-canary/);
});

const observed = () => ({ scope: 'windows-storage-loader-metadata-bootstrap', schema: 1,
  state: 'observed', reason: 'none', selectionAuthority: false, buildAuthority: false, nativeAuthority: false,
  windowsRoot: 'C:\\Windows', windowsVersion: '10.0.26100.1', powershellVersion: '5.1.26100.1',
  architecture: 'x64', powershellSha256: 'a'.repeat(64), powershellBytes: 123456, stability: 'observed-equal' });
const wire = value => Buffer.from(`${JSON.stringify(value)}\n`);
const inert = script => spawn(process.execPath, ['--input-type=module', '-e', script], {
  stdio: ['ignore', 'pipe', 'pipe'], env: {},
});

test('bootstrap CLI refuses host/context before considering private environment paths', () => {
  const result = spawnSync(process.execPath, [entry, '--bootstrap-only'], {
    encoding: 'utf8', timeout: 2000, maxBuffer: 4096,
    env: { FACTORY_WINDOWS_LOADER_METADATA_SELECTION: 'private-path-canary' },
  });
  assert.equal(result.status, 1);
  assert.equal(result.stderr, '');
  assert.equal(JSON.parse(result.stdout).reason, process.platform === 'win32' ? 'controller-prerequisite' : 'platform');
  assert.doesNotMatch(result.stdout, /private-path-canary/);
});

test('bootstrap closed wire records observations with no selection, build or native authority', async () => {
  const { validateBootstrapWire } = await import(entry);
  assert.deepEqual(validateBootstrapWire(wire(observed())), observed());
  const refusal = { scope: 'windows-storage-loader-metadata-bootstrap', schema: 1, state: 'blocked', reason: 'host',
    selectionAuthority: false, buildAuthority: false, nativeAuthority: false };
  assert.deepEqual(validateBootstrapWire(wire(refusal)), refusal);
});

test('bootstrap wire refuses forged authority, coercion, extra fields and noncanonical or oversized bytes', async () => {
  const { validateBootstrapWire } = await import(entry);
  for (const mutate of [
    v => { v.selectionAuthority = true; }, v => { v.buildAuthority = true; }, v => { v.nativeAuthority = true; },
    v => { v.trusted = true; }, v => { v.command = 'private-canary'; }, v => { v.schema = 2; },
    v => { v.windowsRoot = 'C:\\Users\\private'; }, v => { v.windowsVersion = ['10.0.26100.1']; },
    v => { v.windowsVersion = '10.0.26100'; }, v => { v.powershellVersion = ['5.1.26100.1']; },
    v => { v.powershellVersion = '7.5.0'; }, v => { v.architecture = 'arm64'; },
    v => { v.powershellSha256 = ['a'.repeat(64)]; }, v => { v.powershellSha256 = 'unknown'; },
    v => { v.powershellBytes = 134217729; }, v => { v.powershellBytes = 0; },
    v => { v.stability = 'assumed'; }, v => { v.state = 'blocked'; },
  ]) {
    const value = observed(); mutate(value);
    assert.throws(() => validateBootstrapWire(wire(value)), /bootstrap/);
  }
  for (const bytes of [Buffer.alloc(4097), Buffer.from([0xff]), Buffer.from('{}\n{}\n'),
    Buffer.from(`${JSON.stringify(observed())} \n`), Buffer.from('{"schema":1,"schema":1}\n')]) {
    assert.throws(() => validateBootstrapWire(bytes), /bootstrap/);
  }
});

test('bootstrap consumer accepts an inert zero-exit observation only after both real EOF', async () => {
  const { observeBootstrapProcess } = await import(entry);
  const value = observed();
  const result = await observeBootstrapProcess(inert(`process.stdout.write(${JSON.stringify(wire(value).toString())})`), { deadlineMs: 2000 });
  assert.deepEqual(result, value);
});

test('bootstrap consumer refuses process failures and wire overflow without returning child bytes', async () => {
  const { observeBootstrapProcess } = await import(entry);
  for (const [script, deadlineMs] of [
    ['process.stderr.write("private-canary")', 2000],
    ['process.stdout.write("private-canary");process.exitCode=1', 2000],
    ['process.stdout.write(Buffer.alloc(1048577,65))', 2000],
    ['process.stderr.write(Buffer.alloc(8193,65))', 2000],
    ['process.stdout.write(Buffer.alloc(4097,65))', 2000],
    ['setInterval(()=>{},1000)', 150],
    [`process.stdout.write(${JSON.stringify(wire({ scope: 'windows-storage-loader-metadata-bootstrap', schema: 1,
      state: 'blocked', reason: 'host', selectionAuthority: false, buildAuthority: false, nativeAuthority: false }).toString())})`, 2000],
    [`process.stdout.write(${JSON.stringify(wire({ scope: 'windows-storage-loader-metadata-bootstrap', schema: 1,
      state: 'blocked', reason: 'host', selectionAuthority: false, buildAuthority: false, nativeAuthority: false }).toString())});process.exitCode=1`, 2000],
  ]) {
    await assert.rejects(observeBootstrapProcess(inert(script), { deadlineMs }), /^Error: bootstrap-(?:process|wire)$/);
  }
});

test('Phase A workflow has a fixed bootstrap-only route and bounded artifact whitelist', () => {
  const yaml = readFileSync(new URL('../../../.github/workflows/windows-storage-loader-metadata.yml', import.meta.url), 'utf8');
  assert.match(yaml, /windows-2025/);
  assert.match(yaml, /timeout-minutes: 10/);
  assert.match(yaml, /persist-credentials: false/);
  assert.match(yaml, /codex\/research-agentic-workflow-prototypes/);
  assert.match(yaml, /workflow_dispatch:\s*\n/);
  assert.match(yaml, /windows-storage-loader-metadata-bootstrap\.mjs --bootstrap-only/);
  assert.match(yaml, /d2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5/);
  assert.match(yaml, /d702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5/);
  assert.match(yaml, /bootstrap\.json/);
  assert.match(yaml, /control\.json/);
  assert.doesNotMatch(yaml, /--metadata-only|--build-only|workflow_call:|inputs:|secrets:|npm |vswhere|cl\.exe|link\.exe|dumpbin\.exe|lib\.exe/);
  assert.doesNotMatch(yaml, /setup-node|qualification-bootstrap\.mjs|FACTORY_WINDOWS_LOADER_METADATA_SELECTION/);
});

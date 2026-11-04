import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { appendFileSync, copyFileSync, mkdtempSync, readFileSync, readdirSync, mkdirSync, rmSync, realpathSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import test from 'node:test';
import { EventEmitter } from 'node:events';
import { PassThrough } from 'node:stream';

const entry = fileURLToPath(new URL('./windows-storage-loader-metadata-collect-result.mjs', import.meta.url));
const cli = fileURLToPath(new URL('./windows-storage-loader-metadata.mjs', import.meta.url));
const digest = '10f2bd54b5e47122e4d5283ba83a72e776ba3b87fdf74d8eb68d02908257bf98';
const commit = '1234567890123456789012345678901234567890';
const wire = value => Buffer.from(`${JSON.stringify(value)}\n`);
const metadata = () => ({ scope: 'windows-storage-loader-metadata', schema: 2, state: 'blocked',
  reason: 'sdk-provenance-unproven', selectionAuthority: false, buildAuthority: false, nativeAuthority: false,
  sourceSelectionSha256: digest,
  host: { powershellVersion: '5.1.26100.33648', windowsVersion: '10.0.26100.0', architecture: 'x64',
    profile: 'winps-inbox-only', securityCommand: 'captured-inbox-Get-AuthenticodeSignature' },
  installations: [], sdkVersions: [], files: [], sdkCoverage: 'prerequisite-samples-not-consumed-closure',
  sdkRegistration: { version: 1, status: 'single-candidate', reason: 'none', records: [{
    view: 'x64', productCode: '{01234567-89AB-CDEF-0123-456789ABCDEF}',
    displayName: 'Windows Software Development Kit - Windows 10.0.26100.0',
    displayVersion: '10.1.26100.1', publisher: 'Microsoft Corporation',
  }] } });
const refusal = () => ({ scope: 'windows-storage-loader-metadata', state: 'blocked', reason: 'host-profile',
  selectionAuthority: false, buildAuthority: false, nativeAuthority: false });
const inert = script => spawn(process.execPath, ['--input-type=module', '-e', script], {
  stdio: ['ignore', 'pipe', 'pipe'], env: {},
});

function fakeChild() {
  const child = new EventEmitter();
  child.stdout = new PassThrough(); child.stderr = new PassThrough();
  child.kill = () => queueMicrotask(() => { child.stdout.end(); child.stderr.end(); child.emit('exit', null, 'SIGKILL'); child.emit('close'); });
  child.unref = () => {};
  return child;
}

test('a timed out inert collection yields only the fixed outer deadline marker', async () => {
  const { classifyCollectionProcess } = await import(entry);
  const result = await classifyCollectionProcess(fakeChild(), { deadlineMs: 10 });
  assert.deepEqual(result, { diagnostic: 'metadata-refused-outer-deadline' });
});

function completeFake(child, bytes, code = 1, { stderr = '', stdoutEOF = true, stderrEOF = true, signal = null } = {}) {
  setImmediate(() => {
    if (bytes) child.stdout.write(bytes);
    if (stderr) child.stderr.write(stderr);
    if (stdoutEOF) child.stdout.end();
    if (stderrEOF) child.stderr.end();
    child.emit('exit', code, signal);
    setImmediate(() => child.emit('close'));
  });
  return child;
}

test('diagnostic classification accepts only closed inner refusals and valid full wire', async () => {
  const { classifyCollectionProcess } = await import(entry);
  for (const reason of ['deadline', 'exit', 'eof', 'stderr', 'bounds', 'process', 'protocol', 'changed']) {
    const value = { ...refusal(), reason };
    assert.deepEqual(await classifyCollectionProcess(completeFake(fakeChild(), wire(value))),
      { diagnostic: `metadata-refused-inner-${reason}` });
  }
  const bytes = wire(metadata());
  assert.deepEqual(await classifyCollectionProcess(completeFake(fakeChild(), bytes)), { bytes, exitCode: 1 });
  const observedBytes = wire(observed());
  assert.deepEqual(await classifyCollectionProcess(completeFake(fakeChild(), observedBytes, 0)), { bytes: observedBytes, exitCode: 0 });
  const forged = { ...refusal(), reason: 'deadline', selectionAuthority: true };
  for (const [input, code] of [[wire(forged), 1], [wire({ ...refusal(), reason: 'deadline', extra: 'secret' }), 1],
    [wire({ ...refusal(), reason: ['deadline'] }), 1], [wire({ ...refusal(), reason: {} }), 1],
    [wire({ ...refusal(), reason: 'unknown' }), 1],
    [Buffer.from(`${JSON.stringify({ ...refusal(), reason: 'deadline' })}\n\n`), 1],
    [Buffer.from('{"state":"blocked","scope":"windows-storage-loader-metadata","reason":"deadline","selectionAuthority":false,"buildAuthority":false,"nativeAuthority":false}\n'), 1],
    [wire({ ...refusal(), reason: 'deadline' }), 0], [Buffer.from('C:\\private\\secret'), 1], [bytes, 0]]) {
    assert.deepEqual(await classifyCollectionProcess(completeFake(fakeChild(), input, code)), { diagnostic: 'metadata-refused-wire' });
  }
});

test('diagnostic classification reports fixed outer capture failures without child data', async () => {
  const { classifyCollectionProcess } = await import(entry);
  for (const [child, expected] of [
    [completeFake(fakeChild(), Buffer.from('secret'), 2), 'exit'],
    [completeFake(fakeChild(), Buffer.from('secret'), 1, { stdoutEOF: false }), 'eof'],
    [completeFake(fakeChild(), Buffer.from('secret'), 1, { stderr: 'private-stderr' }), 'stderr'],
    [completeFake(fakeChild(), Buffer.alloc(1048577, 65)), 'bounds'],
    [completeFake(fakeChild(), null, 1, { stderr: 'x'.repeat(8193) }), 'bounds'],
  ]) assert.deepEqual(await classifyCollectionProcess(child), { diagnostic: `metadata-refused-outer-${expected}` });
  const broken = fakeChild();
  setImmediate(() => broken.emit('error', new Error('private-error')));
  assert.deepEqual(await classifyCollectionProcess(broken), { diagnostic: 'metadata-refused-outer-process' });
});

test('collection entry refuses arguments and unsupported host without exposing environment values', () => {
  for (const args of [['private-argument-canary'], []]) {
    const result = spawnSync(process.execPath, [entry, ...args], { encoding: 'utf8', timeout: 2000,
      maxBuffer: 4096, env: { FACTORY_PRIVATE_ROOT: 'private-path-canary' } });
    assert.equal(result.error, undefined);
    assert.equal(result.status, 1);
    assert.equal(result.stderr, '');
    assert.equal(result.stdout, 'metadata-refused-prerequisite\n');
  }
});

test('existing real metadata CLI refuses this unsupported host before using candidate paths', () => {
  const result = spawnSync(process.execPath, [cli, '--metadata-only'], { encoding: 'utf8', timeout: 2000,
    maxBuffer: 4096, env: { FACTORY_WINDOWS_LOADER_METADATA_SELECTION: 'private-path-canary' } });
  assert.equal(result.status, 1);
  assert.equal(result.stderr, '');
  assert.equal(JSON.parse(result.stdout).reason, process.platform === 'win32' ? 'controller-prerequisite' : 'platform');
  assert.doesNotMatch(result.stdout, /private-path-canary/);
});

test('inert blocked collection is retained only after accepted exit and both actual EOF', async () => {
  const { observeCollectionProcess } = await import(entry);
  const bytes = wire(metadata());
  const captured = await observeCollectionProcess(inert(`process.stdout.write(${JSON.stringify(bytes.toString())});process.exitCode=1`), { deadlineMs: 2000 });
  assert.equal(captured.exitCode, 1);
  assert.deepEqual(captured.bytes, bytes);
});

// Synthetic signatures exercise parser controls only, never Microsoft authentication.
function observed() {
  const value = metadata();
  value.state = 'observed'; value.reason = 'none';
  const installation = 'C:\\Program Files\\Microsoft Visual Studio\\2022\\BuildTools';
  const toolset = '14.44.35207'; const sdkVersion = '10.0.26100.0';
  value.installations = [installation]; value.sdkVersions = [sdkVersion];
  const row = (role, target, path, tool = true) => ({ role, target,
    installation: tool ? installation : '', toolset: tool ? toolset : '', sdkVersion: tool ? '' : sdkVersion,
    path, bytes: 1, sha256: 'a'.repeat(64), fileVersion: '1.0', regular: true, reparse: false,
    stability: 'observed-equal', signature: { path, status: 'Valid', type: 'Authenticode', condition: 'none',
      subject: 'CN=Synthetic parser control, O=Microsoft Corporation, C=US', issuer: 'CN=Synthetic parser control',
      thumbprint: 'b'.repeat(40), certificateSha256: 'c'.repeat(64) } });
  for (const target of ['x64', 'x86']) {
    const prefix = `${installation}\\VC\\Tools\\MSVC\\${toolset}\\bin\\Hostx64\\${target}\\`;
    for (const [role, leaf] of [['compiler', 'cl.exe'], ['linker', 'link.exe'],
      [target === 'x64' ? 'inspector' : 'library-tool', target === 'x64' ? 'dumpbin.exe' : 'lib.exe'],
      ['compiler-companion', 'c1.dll'], ['compiler-companion', 'c1xx.dll'], ['compiler-companion', 'c2.dll']]) {
      value.files.push(row(role, target, `${prefix}${leaf}`));
    }
  }
  const kit = 'C:\\Program Files (x86)\\Windows Kits\\10';
  for (const suffix of ['ucrt\\stdio.h', 'shared\\sdkddkver.h', 'um\\Windows.h']) {
    value.files.push(row('sdk-header', 'none', `${kit}\\Include\\${sdkVersion}\\${suffix}`, false));
  }
  for (const target of ['x64', 'x86']) for (const [directory, leaf] of [['ucrt', 'ucrt.lib'], ['um', 'kernel32.lib']]) {
    value.files.push(row('sdk-library', target, `${kit}\\Lib\\${sdkVersion}\\${directory}\\${target}\\${leaf}`, false));
  }
  return value;
}

test('root selection uses its independently frozen exact bytes and source commit', async () => {
  const { validateCollectionSelection } = await import(entry);
  const bytes = readFileSync(new URL('./windows-storage-loader-metadata-controller-selection.json', import.meta.url));
  const historical = readFileSync(new URL('./windows-storage-loader-metadata-controller-selection-2229249.json', import.meta.url));
  assert.throws(() => validateCollectionSelection(historical), /metadata-collection/);
  assert.equal(validateCollectionSelection(bytes).sourceCommit, '5405a163b4e591705f9888440ec5cb8933c48d2c');
  for (const mutate of [v => { v.sourceCommit = commit; }, v => { v.windowsVersion = '10.0.26100.1'; },
    v => { v.sourceSha256['qualification/windows-storage-loader-metadata.mjs'] = 'd'.repeat(64); },
    v => { v.powershellSha256 = 'e'.repeat(64); }, v => { v.trusted = true; }]) {
    const value = JSON.parse(bytes); mutate(value);
    assert.throws(() => validateCollectionSelection(wire(value)), /metadata-collection/);
  }
  assert.throws(() => validateCollectionSelection(Buffer.concat([bytes, Buffer.from('\n')])), /metadata-collection/);
});

test('fixed context checks actual selected source bytes and refuses a changed disposable source', async () => {
  const originalPackage = fileURLToPath(new URL('../', import.meta.url));
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'metadata-context-')));
  try {
    const selectedPath = 'qualification/windows-storage-loader-metadata-controller-selection.json';
    const selected = JSON.parse(readFileSync(join(originalPackage, selectedPath)));
    const resultPath = 'qualification/windows-storage-loader-metadata-collect-result.mjs';
    for (const path of [...Object.keys(selected.sourceSha256), selectedPath, resultPath]) {
      mkdirSync(dirname(join(root, path)), { recursive: true });
      copyFileSync(join(originalPackage, path), join(root, path));
    }
    const { verifyCollectionSources } = await import(pathToFileURL(join(root, resultPath)).href);
    assert.equal(verifyCollectionSources().selected.sourceCommit, '5405a163b4e591705f9888440ec5cb8933c48d2c');
    appendFileSync(join(root, 'qualification/windows-storage-loader-fixture.py'), '\n# changed disposable control\n');
    assert.throws(() => verifyCollectionSources(), /metadata-collection/);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('fully closed synthetic observed wire couples exclusively to exit zero', async () => {
  const { observeCollectionProcess } = await import(entry);
  const bytes = wire(observed());
  const captured = await observeCollectionProcess(inert(`process.stdout.write(${JSON.stringify(bytes.toString())})`), { deadlineMs: 2000 });
  assert.equal(captured.exitCode, 0);
  assert.deepEqual(captured.bytes, bytes);
});

test('collection refuses exit/state mismatch, early refusal, host drift and forged authority', async () => {
  const { observeCollectionProcess } = await import(entry);
  const drift = metadata(); drift.host.windowsVersion = '10.0.26100.1';
  const psDrift = metadata(); psDrift.host.powershellVersion = '5.1.26100.1';
  const forged = metadata(); forged.selectionAuthority = true;
  const source = metadata(); source.sourceSelectionSha256 = 'd'.repeat(64);
  for (const [value, code] of [[metadata(), 0], [observed(), 1], [metadata(), 2], [refusal(), 1],
    [drift, 1], [psDrift, 1], [forged, 1], [source, 1]]) {
    await assert.rejects(observeCollectionProcess(inert(`process.stdout.write(${JSON.stringify(wire(value).toString())});process.exitCode=${code}`),
      { deadlineMs: 2000 }));
  }
});

test('real failed captures suppress stderr, overflow, deadline and inherited-pipe incomplete EOF', async () => {
  const { observeCollectionProcess } = await import(entry);
  for (const [script, deadlineMs] of [
    ['process.stderr.write("private-stderr-canary")', 2000],
    ['process.stdout.write(Buffer.alloc(1048577,65))', 2000],
    ['process.stderr.write(Buffer.alloc(8193,65))', 2000],
    ['setInterval(()=>{},1000)', 100],
    [`import {spawn} from 'node:child_process';spawn(process.execPath,['-e','setTimeout(()=>{},400)'],{stdio:['ignore','inherit','inherit'],env:{}}).unref()`, 100],
  ]) await assert.rejects(observeCollectionProcess(inert(script), { deadlineMs }), /^Error: metadata-collection$/);
});

test('only two fresh artifact files preserve blocked failure and observed success without authority', async () => {
  const { prepareCollectionArtifacts } = await import(entry);
  for (const [value, code] of [[metadata(), 1], [observed(), 0]]) {
    const root = realpathSync(mkdtempSync(join(tmpdir(), 'metadata-artifacts-')));
    try {
      const result = prepareCollectionArtifacts(wire(value), code, root, commit);
      assert.equal(result.exitCode, code);
      assert.equal(result.state, value.state);
      assert.deepEqual(readdirSync(result.artifactDirectory).sort(), ['control.json', 'metadata.json']);
      assert.deepEqual(readFileSync(join(result.artifactDirectory, 'metadata.json')), wire(value));
      const control = JSON.parse(readFileSync(join(result.artifactDirectory, 'control.json')));
      assert.deepEqual(control, { scope: 'windows-storage-loader-metadata-execution-control', schema: 1,
        phase: 'metadata-only', sourceCommit: '5405a163b4e591705f9888440ec5cb8933c48d2c', collectionSourceCommit: commit,
        sourceSelectionSha256: digest, state: value.state, collectorExitCode: code,
        selectionAuthority: false, buildAuthority: false, nativeAuthority: false });
      assert.throws(() => prepareCollectionArtifacts(wire(value), code, root, commit));
    } finally { rmSync(root, { recursive: true, force: true }); }
  }
});

test('invalid wire, raw data, early refusals and existing destinations never create an export', async () => {
  const { prepareCollectionArtifacts } = await import(entry);
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'metadata-artifacts-')));
  try {
    for (const [bytes, code, sourceCommit] of [[wire(metadata()), 0, commit], [wire(refusal()), 1, commit],
      [Buffer.from('private-raw-canary'), 1, commit], [Buffer.alloc(1048577), 1, commit],
      [wire(metadata()), 1, 'private-source-canary']]) {
      assert.throws(() => prepareCollectionArtifacts(bytes, code, root, sourceCommit));
      assert.deepEqual(readdirSync(root), []);
    }
    mkdirSync(join(root, 'factory-metadata-collect-upload'));
    assert.throws(() => prepareCollectionArtifacts(wire(metadata()), 1, root, commit));
    assert.deepEqual(readdirSync(join(root, 'factory-metadata-collect-upload')), []);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('separate workflow fixes its route, Node bootstrap and exact two-file artifact allowlist', () => {
  const yaml = readFileSync(new URL('../../../.github/workflows/windows-storage-loader-metadata-collect.yml', import.meta.url), 'utf8');
  const bootstrap = readFileSync(new URL('./windows-storage-loader-node-bootstrap.ps1', import.meta.url), 'utf8');
  assert.match(yaml, /windows-2025/);
  assert.match(yaml, /timeout-minutes: 10/);
  assert.match(yaml, /persist-credentials: false/);
  assert.match(yaml, /codex\/research-agentic-workflow-prototypes/);
  assert.match(yaml, /workflow_dispatch:\s*\n/);
  assert.match(yaml, /windows-storage-loader-node-bootstrap\.ps1/);
  assert.match(yaml, /windows-storage-loader-metadata-collect-result\.mjs/);
  assert.match(yaml, /if: \$\{\{ !cancelled\(\) && steps\.collect\.outputs\.artifacts_ready == 'true' \}\}/);
  assert.match(yaml, /factory-metadata-collect-upload\/metadata\.json/);
  assert.match(yaml, /factory-metadata-collect-upload\/control\.json/);
  assert.doesNotMatch(yaml, /continue-on-error|workflow_call:|inputs:|secrets:|setup-node|npm |npx |--build-only|--bootstrap-only|vswhere/);
  assert.match(bootstrap, /https:\/\/nodejs\.org\/download\/release\/v24\.22\.1\/node-v24\.22\.1-win-x64\.zip/);
  assert.match(bootstrap, /d2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5/);
  assert.match(bootstrap, /d702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5/);
  assert.match(bootstrap, /AllowAutoRedirect = \$false/);
  assert.match(bootstrap, /150000000/);
  assert.match(bootstrap, /120000/);
  assert.doesNotMatch(bootstrap, /Expand-Archive|Start-Process|Invoke-Expression|npm |npx |--version|--help/);
});

// Root-selected literals are independent protocol prerequisites, never candidate-derived.
test('new SDK live context requires exact Root selection and matching digest sidecar', async () => {
  const { createHash } = await import('node:crypto');
  const { validateCollectionSelection } = await import(entry);
  const bytes = readFileSync(new URL('./windows-storage-loader-metadata-controller-selection.json', import.meta.url));
  const sidecar = readFileSync(new URL('./windows-storage-loader-metadata-controller-selection.sha256', import.meta.url), 'utf8');
  const approved = '10f2bd54b5e47122e4d5283ba83a72e776ba3b87fdf74d8eb68d02908257bf98';
  assert.equal(createHash('sha256').update(bytes).digest('hex'), approved);
  assert.equal(sidecar, `${approved}  windows-storage-loader-metadata-controller-selection.json\n`);
  assert.equal(validateCollectionSelection(bytes).sourceCommit, '5405a163b4e591705f9888440ec5cb8933c48d2c');
  for (const name of ['4b311737', '2229249']) {
    const historical = readFileSync(new URL(`./windows-storage-loader-metadata-controller-selection-${name}.json`, import.meta.url));
    assert.throws(() => validateCollectionSelection(historical), /metadata-collection/);
  }
});

test('new SDK live context admits v2 and refuses historical v1 without exporting artifacts', async () => {
  const { observeCollectionProcess, classifyCollectionProcess, prepareCollectionArtifacts } = await import(entry);
  const { validateMetadataWire, validateSdkRegistrationMetadataWire } = await import(cli);
  const approved = '10f2bd54b5e47122e4d5283ba83a72e776ba3b87fdf74d8eb68d02908257bf98';
  const value = { ...metadata(), schema: 2, sourceSelectionSha256: approved,
    sdkRegistration: { version: 1, status: 'single-candidate', reason: 'none', records: [{
      view: 'x64', productCode: '{01234567-89AB-CDEF-0123-456789ABCDEF}',
      displayName: 'Windows Software Development Kit - Windows 10.0.26100.0',
      displayVersion: '10.1.26100.1', publisher: 'Microsoft Corporation',
    }] } };
  const bytes = wire(value);
  assert.deepEqual(validateSdkRegistrationMetadataWire(bytes, approved), value);
  assert.deepEqual(await observeCollectionProcess(completeFake(fakeChild(), bytes)), { bytes, exitCode: 1 });
  const old = structuredClone(value); old.schema = 1; delete old.sdkRegistration;
  assert.deepEqual(validateMetadataWire(wire(old), approved), old);
  const malformed = structuredClone(value); malformed.sdkRegistration.records[0].view = 'foreign';
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'metadata-v2-rejection-')));
  try {
    for (const rejected of [old, malformed]) {
      await assert.rejects(observeCollectionProcess(completeFake(fakeChild(), wire(rejected))));
      assert.deepEqual(await classifyCollectionProcess(completeFake(fakeChild(), wire(rejected))), { diagnostic: 'metadata-refused-wire' });
      assert.throws(() => prepareCollectionArtifacts(wire(rejected), 1, root, commit));
      assert.deepEqual(readdirSync(root), []);
    }
  } finally { rmSync(root, { recursive: true, force: true }); }
});

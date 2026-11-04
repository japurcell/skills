import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { appendFileSync, copyFileSync, mkdtempSync, readFileSync, readdirSync, mkdirSync, rmSync, realpathSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import test from 'node:test';

const entry = fileURLToPath(new URL('./windows-storage-loader-metadata-collect-result.mjs', import.meta.url));
const cli = fileURLToPath(new URL('./windows-storage-loader-metadata.mjs', import.meta.url));
const digest = '719d27ea0ed7cb4e554adf02e0384c8a67a50bae61c6cdb80f832f4991335650';
const commit = '1234567890123456789012345678901234567890';
const wire = value => Buffer.from(`${JSON.stringify(value)}\n`);
const metadata = () => ({ scope: 'windows-storage-loader-metadata', schema: 1, state: 'blocked',
  reason: 'sdk-provenance-unproven', selectionAuthority: false, buildAuthority: false, nativeAuthority: false,
  sourceSelectionSha256: digest,
  host: { powershellVersion: '5.1.26100.33648', windowsVersion: '10.0.26100.0', architecture: 'x64',
    profile: 'winps-inbox-only', securityCommand: 'captured-inbox-Get-AuthenticodeSignature' },
  installations: [], sdkVersions: [], files: [], sdkCoverage: 'prerequisite-samples-not-consumed-closure' });
const refusal = () => ({ scope: 'windows-storage-loader-metadata', state: 'blocked', reason: 'host-profile',
  selectionAuthority: false, buildAuthority: false, nativeAuthority: false });
const inert = script => spawn(process.execPath, ['--input-type=module', '-e', script], {
  stdio: ['ignore', 'pipe', 'pipe'], env: {},
});

test('collection entry refuses arguments and unsupported host without exposing environment values', () => {
  for (const args of [['private-argument-canary'], []]) {
    const result = spawnSync(process.execPath, [entry, ...args], { encoding: 'utf8', timeout: 2000,
      maxBuffer: 4096, env: { FACTORY_PRIVATE_ROOT: 'private-path-canary' } });
    assert.equal(result.error, undefined);
    assert.equal(result.status, 1);
    assert.equal(result.stderr, '');
    assert.equal(result.stdout, '');
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
  assert.equal(validateCollectionSelection(bytes).sourceCommit, '222924947e2a9b4c24a1d7c3eddaa426b0d15403');
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
    assert.equal(verifyCollectionSources().selected.sourceCommit, '222924947e2a9b4c24a1d7c3eddaa426b0d15403');
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
        phase: 'metadata-only', sourceCommit: '222924947e2a9b4c24a1d7c3eddaa426b0d15403', collectionSourceCommit: commit,
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

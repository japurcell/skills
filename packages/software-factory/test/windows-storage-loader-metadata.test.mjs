import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const entry = fileURLToPath(new URL('../qualification/windows-storage-loader-metadata.mjs', import.meta.url));
test('fixed metadata CLI refuses unsupported argv without echoing candidate commands', () => {
  const result = spawnSync(process.execPath, [entry, '--build-only', 'private-command-canary'], {
    encoding: 'utf8', timeout: 2000, maxBuffer: 4096, env: {},
  });
  assert.equal(result.error, undefined);
  assert.equal(result.status, 1);
  assert.equal(result.stderr, '');
  assert.deepEqual(JSON.parse(result.stdout), {
    scope: 'windows-storage-loader-metadata', state: 'blocked', reason: 'arguments',
    selectionAuthority: false, buildAuthority: false, nativeAuthority: false,
  });
  assert.doesNotMatch(result.stdout, /private-command-canary/);
});

test('fixed metadata CLI blocks unsupported host before looking at candidate environment', () => {
  const result = spawnSync(process.execPath, [entry, '--metadata-only'], {
    encoding: 'utf8', timeout: 2000, maxBuffer: 4096,
    env: { FACTORY_WINDOWS_LOADER_METADATA_SELECTION: 'private-path-canary' },
  });
  assert.equal(result.status, 1);
  assert.equal(result.stderr, '');
  assert.equal(JSON.parse(result.stdout).reason, process.platform === 'win32' ? 'controller-prerequisite' : 'platform');
  assert.doesNotMatch(result.stdout, /private-path-canary/);
});

const digest = 'a'.repeat(64);
const metadata = () => ({ scope: 'windows-storage-loader-metadata', schema: 1, state: 'blocked',
  reason: 'sdk-provenance-unproven', selectionAuthority: false, buildAuthority: false, nativeAuthority: false,
  sourceSelectionSha256: digest,
  host: { powershellVersion: '5.1.26100.1', windowsVersion: '10.0.26100.1', architecture: 'x64',
    profile: 'winps-inbox-only', securityCommand: 'captured-inbox-Get-AuthenticodeSignature' },
  installations: [], sdkVersions: [], files: [], sdkCoverage: 'prerequisite-samples-not-consumed-closure',
});
const wire = value => Buffer.from(`${JSON.stringify(value)}\n`);

test('closed wire accepts only the compatible release folders under fixed roots and editions', async () => {
  const { validateMetadataWire } = await import(entry);
  for (const root of ['Program Files', 'Program Files (x86)']) {
    for (const edition of ['BuildTools', 'Community', 'Professional', 'Enterprise']) {
      for (const release of ['18', '2022']) {
        const value = metadata();
        value.installations = [`C:\\${root}\\Microsoft Visual Studio\\${release}\\${edition}`];
        assert.deepEqual(validateMetadataWire(wire(value), digest), value);
      }
    }
  }
  for (const release of ['17', '19', '018', '18x', '202', '20222', 'Insiders', '..\\18']) {
    const value = metadata();
    value.installations = [`C:\\Program Files\\Microsoft Visual Studio\\${release}\\Enterprise`];
    assert.throws(() => validateMetadataWire(wire(value), digest), /metadata/);
  }
  for (const path of ['C:\\Other\\Microsoft Visual Studio\\18\\Enterprise',
    'C:\\Program Files\\Microsoft Visual Studio\\18\\Insiders']) {
    const value = metadata(); value.installations = [path];
    assert.throws(() => validateMetadataWire(wire(value), digest), /metadata/);
  }
});

test('closed wire parser preserves blocked observations without granting authority', async () => {
  const { validateMetadataWire } = await import(entry);
  const parsed = validateMetadataWire(wire(metadata()), digest);
  assert.equal(parsed.reason, 'sdk-provenance-unproven');
  assert.equal(parsed.selectionAuthority, false);
  assert.equal(parsed.buildAuthority, false);
  assert.equal(parsed.nativeAuthority, false);
});

test('closed metadata wire refuses authority forgery, unknown schema, private paths and record overflow', async () => {
  const { validateMetadataWire } = await import(entry);
  const cases = [
    value => { value.trusted = true; }, value => { value.selectionAuthority = true; },
    value => { value.buildAuthority = true; }, value => { value.nativeAuthority = true; },
    value => { value.schema = 2; }, value => { value.sourceSelectionSha256 = 'b'.repeat(64); },
    value => { value.host.profile = 'ambient'; }, value => { value.reason = 'arbitrary-private-canary'; },
    value => { value.host.powershellVersion = ['5.1.26100.1']; },
    value => { value.host.windowsVersion = ['10.0.26100.1']; },
    value => { value.installations = ['C:\\Users\\someone\\MSVC']; },
    value => { value.files = Array(257).fill({}); },
    value => { value.state = 'observed'; value.reason = 'none'; },
  ];
  for (const mutate of cases) {
    const value = metadata(); mutate(value);
    assert.throws(() => validateMetadataWire(wire(value), digest), /metadata/);
  }
  for (const bytes of [Buffer.from('{}\n{}\n'), Buffer.from('{"schema":1,"schema":1}\n'),
    Buffer.from(`${JSON.stringify(metadata())} \n`), Buffer.alloc(1048577), Buffer.from([0xff])]) {
    assert.throws(() => validateMetadataWire(bytes, digest), /metadata/);
  }
});

test('actual source-selection schema binds fixed controller sources without accepting candidate authority', async () => {
  const { validateControllerSelection } = await import(entry);
  const paths = ['qualification/windows-storage-loader-fixture.py', 'qualification/windows-storage-loader-canary.c',
    'qualification/windows-storage-loader-child.mjs', 'qualification/windows-storage-loader.qualification.mjs',
    'test/windows-storage-loader-contract.test.mjs', 'qualification/windows-storage-loader.md',
    'qualification/windows-storage-loader-metadata.mjs', 'qualification/windows-storage-loader-metadata.ps1',
    'qualification/windows-owned-image-host-profile.ps1', 'qualification/windows-owned-image-diagnostics.ps1'];
  const selected = { scope: 'windows-storage-loader-metadata-controller', schema: 1, sourceCommit: 'b'.repeat(40),
    sourceSha256: Object.fromEntries(paths.map(path => [path, digest])),
    nodeSha256: 'd702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5',
    powershellSha256: 'c'.repeat(64), windowsRoot: 'C:\\Windows', windowsVersion: '10.0.26100.1' };
  assert.equal(validateControllerSelection(wire(selected)).powershellSha256, 'c'.repeat(64));
  for (const change of [
    value => { value.trusted = true; }, value => { value.command = 'cl.exe'; },
    value => { value.nodeSha256 = digest; }, value => { value.windowsRoot = 'C:\\Users\\someone'; },
    value => { value.sourceSha256['qualification/private.ps1'] = digest; },
    value => { delete value.sourceSha256[paths[0]]; }, value => { value.powershellSha256 = 'unknown'; },
    value => { value.windowsVersion = ['10.0.26100.1']; },
  ]) {
    const value = structuredClone(selected); change(value);
    assert.throws(() => validateControllerSelection(wire(value)), /metadata/);
  }
});

test('synthetic Microsoft-shaped signature is only a blocked fact and tool roles cannot hide in SDK rows', async () => {
  const { validateMetadataWire } = await import(entry);
  const path = 'C:\\Program Files\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Tools\\MSVC\\14.44.35207\\bin\\Hostx64\\x86\\lib.exe';
  const value = metadata();
  value.installations = ['C:\\Program Files\\Microsoft Visual Studio\\2022\\BuildTools'];
  value.files = [{ role: 'library-tool', target: 'x86', installation: value.installations[0], toolset: '14.44.35207',
    sdkVersion: '', path, bytes: 123, sha256: digest, fileVersion: '14.44.35207.0', regular: true,
    reparse: false, stability: 'observed-equal', signature: { path, status: 'Valid', type: 'Authenticode', condition: 'none',
      subject: 'CN=Synthetic test only, O=Microsoft Corporation, C=US', issuer: 'CN=Synthetic test only',
      thumbprint: 'd'.repeat(40), certificateSha256: 'e'.repeat(64) } }];
  const parsed = validateMetadataWire(wire(value), digest);
  assert.equal(parsed.state, 'blocked');
  assert.equal(parsed.buildAuthority, false);
  for (const change of [
    row => { row.role = 'sdk-library'; }, row => { row.role = 'sdk-header'; },
    row => { row.path = 'C:\\Users\\someone\\lib.exe'; row.signature.path = row.path; },
    row => { row.signature.trusted = true; }, row => { row.signature.status = 'NotSigned'; },
    row => { row.toolset = ['14.44.35207']; },
    row => { row.stability = 'assumed'; }, row => { row.reparse = true; }, row => { row.bytes = 134217729; },
  ]) {
    const bad = structuredClone(value); change(bad.files[0]);
    assert.throws(() => validateMetadataWire(wire(bad), digest), /metadata/);
  }
});

test('discovered 18 tools do not promote unknown SDK signatures or ambiguous observations', async () => {
  const { validateMetadataWire } = await import(entry);
  const value = metadata();
  const installation = 'C:\\Program Files\\Microsoft Visual Studio\\18\\Enterprise';
  const sdkVersion = '10.0.26100.0';
  const sdkPath = `C:\\Program Files (x86)\\Windows Kits\\10\\Include\\${sdkVersion}\\ucrt\\stdio.h`;
  value.installations = [installation]; value.sdkVersions = [sdkVersion];
  value.files = [{ role: 'sdk-header', target: 'none', installation: '', toolset: '', sdkVersion,
    path: sdkPath, bytes: 123, sha256: digest, fileVersion: '', regular: true, reparse: false,
    stability: 'observed-equal', signature: { path: sdkPath, status: 'UnknownError', type: 'None',
      condition: 'status-not-valid', subject: '', issuer: '', thumbprint: '', certificateSha256: '' } }];
  const toolPath = `${installation}\\VC\\Tools\\MSVC\\14.44.35207\\bin\\Hostx64\\x86\\lib.exe`;
  value.files.push({ role: 'library-tool', target: 'x86', installation, toolset: '14.44.35207', sdkVersion: '',
    path: toolPath, bytes: 123, sha256: digest, fileVersion: '14.44.35207.0', regular: true, reparse: false,
    stability: 'observed-equal', signature: { path: toolPath, status: 'Valid', type: 'Authenticode', condition: 'none',
      subject: 'CN=Synthetic test only, O=Microsoft Corporation, C=US', issuer: 'CN=Synthetic test only',
      thumbprint: 'd'.repeat(40), certificateSha256: 'e'.repeat(64) } });
  const parsed = validateMetadataWire(wire(value), digest);
  assert.equal(parsed.reason, 'sdk-provenance-unproven');
  assert.equal(parsed.selectionAuthority, false);
  assert.equal(parsed.buildAuthority, false);
  assert.equal(parsed.nativeAuthority, false);
  const forged = structuredClone(value); forged.state = 'observed'; forged.reason = 'none';
  assert.throws(() => validateMetadataWire(wire(forged), digest), /metadata/);
  const ambiguous = structuredClone(value);
  ambiguous.reason = 'ambiguous-tools';
  ambiguous.installations.push('C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools');
  assert.equal(validateMetadataWire(wire(ambiguous), digest).reason, 'ambiguous-tools');
  ambiguous.state = 'observed'; ambiguous.reason = 'none';
  assert.throws(() => validateMetadataWire(wire(ambiguous), digest), /metadata/);
});

test('observed synthetic 18 record requires exactly one toolset', async () => {
  const { validateMetadataWire } = await import(entry);
  const value = metadata();
  const installation = 'C:\\Program Files\\Microsoft Visual Studio\\18\\Enterprise';
  const sdkVersion = '10.0.26100.0';
  const toolset = '14.44.35207';
  value.state = 'observed'; value.reason = 'none';
  value.installations = [installation]; value.sdkVersions = [sdkVersion];
  // Synthetic signature fields exercise wire validation only; they authenticate no file.
  const file = (role, target, path, sourceInstallation, sourceToolset, sourceSdk) => ({
    role, target, installation: sourceInstallation, toolset: sourceToolset, sdkVersion: sourceSdk,
    path, bytes: 123, sha256: digest, fileVersion: '1.0', regular: true, reparse: false,
    stability: 'observed-equal', signature: { path, status: 'Valid', type: 'Authenticode', condition: 'none',
      subject: 'CN=Synthetic test only, O=Microsoft Corporation, C=US', issuer: 'CN=Synthetic test only',
      thumbprint: 'd'.repeat(40), certificateSha256: 'e'.repeat(64) },
  });
  for (const [role, target, leaf] of [['compiler', 'x64', 'cl.exe'], ['linker', 'x64', 'link.exe'],
    ['inspector', 'x64', 'dumpbin.exe'], ['compiler', 'x86', 'cl.exe'], ['linker', 'x86', 'link.exe'],
    ['library-tool', 'x86', 'lib.exe'], ...['x64', 'x86'].flatMap(target =>
      ['c1.dll', 'c1xx.dll', 'c2.dll'].map(leaf => ['compiler-companion', target, leaf]))]) {
    const path = `${installation}\\VC\\Tools\\MSVC\\${toolset}\\bin\\Hostx64\\${target}\\${leaf}`;
    value.files.push(file(role, target, path, installation, toolset, ''));
  }
  const sdkRoot = 'C:\\Program Files (x86)\\Windows Kits\\10';
  for (const [role, target, suffix] of [['sdk-header', 'none', `Include\\${sdkVersion}\\ucrt\\stdio.h`],
    ['sdk-header', 'none', `Include\\${sdkVersion}\\shared\\sdkddkver.h`],
    ['sdk-header', 'none', `Include\\${sdkVersion}\\um\\Windows.h`],
    ...['x64', 'x86'].flatMap(target => [['sdk-library', target, `Lib\\${sdkVersion}\\ucrt\\${target}\\ucrt.lib`],
      ['sdk-library', target, `Lib\\${sdkVersion}\\um\\${target}\\kernel32.lib`]])]) {
    value.files.push(file(role, target, `${sdkRoot}\\${suffix}`, '', '', sdkVersion));
  }
  assert.equal(validateMetadataWire(wire(value), digest).state, 'observed');
  const ambiguous = structuredClone(value);
  const changed = ambiguous.files.find(row => row.role === 'library-tool');
  changed.toolset = '14.45.12345';
  changed.path = changed.path.replace(toolset, changed.toolset); changed.signature.path = changed.path;
  assert.throws(() => validateMetadataWire(wire(ambiguous), digest), /metadata/);
  ambiguous.state = 'blocked'; ambiguous.reason = 'ambiguous-tools';
  assert.equal(validateMetadataWire(wire(ambiguous), digest).reason, 'ambiguous-tools');
});

test('real inert process capture requires zero exit and both EOF before returning bytes', async () => {
  const { captureMetadataProcess } = await import(entry);
  const child = spawn(process.execPath, ['--input-type=module', '-e', 'process.stdout.write("fixed\\n")'], {
    stdio: ['ignore', 'pipe', 'pipe'], env: {},
  });
  const result = await captureMetadataProcess(child, { deadlineMs: 2000 });
  assert.equal(result.state, 'captured');
  assert.equal(result.reason, 'none');
  assert.equal(result.bytes.toString(), 'fixed\n');
  assert.equal(result.exitObserved, true);
  assert.equal(result.stdoutEOF, true);
  assert.equal(result.stderrEOF, true);
});

test('fixed metadata blocked-exit policy retains exit1 observations with both EOF', async () => {
  const { captureMetadataProcess } = await import(entry);
  const child = spawn(process.execPath, ['--input-type=module', '-e', 'process.stdout.write("blocked\\n");process.exitCode=1'], {
    stdio: ['ignore', 'pipe', 'pipe'], env: {},
  });
  const result = await captureMetadataProcess(child, { deadlineMs: 2000, exitCodes: [0, 1] });
  assert.equal(result.state, 'captured');
  assert.equal(result.exitCode, 1);
  assert.equal(result.bytes.toString(), 'blocked\n');
  assert.equal(result.stdoutEOF, true);
  assert.equal(result.stderrEOF, true);
});

test('real process refusal suppresses stderr, nonzero exit, output overflow and deadline bytes', async () => {
  const { captureMetadataProcess } = await import(entry);
  const controls = [
    ['process.stderr.write("private-output-canary")', 'stderr', 2000],
    ['process.exitCode=7;process.stdout.write("private-output-canary")', 'exit', 2000],
    ['process.stdout.write(Buffer.alloc(1048577,65))', 'bounds', 2000],
    ['process.stderr.write(Buffer.alloc(8193,65))', 'bounds', 2000],
    ['setInterval(()=>{},1000)', 'deadline', 150],
  ];
  for (const [script, reason, deadlineMs] of controls) {
    const child = spawn(process.execPath, ['--input-type=module', '-e', script], {
      stdio: ['ignore', 'pipe', 'pipe'], env: {},
    });
    const result = await captureMetadataProcess(child, { deadlineMs });
    assert.equal(result.state, 'blocked');
    assert.equal(result.reason, reason);
    assert.equal(result.bytes, null);
  }
});

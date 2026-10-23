import { pythonSourcePaths } from './fixtures/python-source-paths.mjs';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash, randomUUID } from 'node:crypto';
import { existsSync, linkSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, statSync, symlinkSync, truncateSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { createRepository } from './fixtures/repository.mjs';

const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const owner = { host: 'fixture-host', pid: process.pid, start: 'fixture-start' };
const selection = { release: '1.2.3', selectionDigest: 'a'.repeat(64), targetReleaseSha256: 'b'.repeat(64),
  artifactDigests: { bundle: 'b'.repeat(64), node: 'c'.repeat(64) }, targetSchema: 7 };
const { scanOwnedTree, directoryIdentity, writeCandidateReceipt, verifyBoundInstallCandidate } = await import('../dist/install-candidate.js');
const { runManagedInstallCommand } = await import('../dist/install.js');
const bootstrapScript = fileURLToPath(new URL('../../../skills/software-factory/scripts/install.py', import.meta.url));
const packageRoot = join(import.meta.dirname, '..');
const canonical = value => Array.isArray(value) ? `[${value.map(canonical).join(',')}]`
  : value && typeof value === 'object' ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`
    : JSON.stringify(value);

function candidateFixture() {
  const repository = createRepository();
  const source = realpathSync(repository.path);
  const dispose = () => repository.dispose();
  return { repository, source, dispose };
}

test('a bound candidate receipt rejects changed bytes, extra empty directories and receipt edits', async () => {
  const { beginRepositoryBootstrap, inspectMaintenance, measureMaintenanceStage, prepareMaintenanceHandoff } = await import('../dist/maintenance.js');
  const { openMaintenanceStore } = await import('../dist/store.js');
  const fixture = candidateFixture();
  try {
    const handle = await beginRepositoryBootstrap(fixture.source, selection, owner);
    const candidate = join(handle.commonDir, 'factory', `install-candidate-${handle.operationId}`);
    mkdirSync(candidate, { mode: 0o700 });
    mkdirSync(join(candidate, 'install'), { mode: 0o700 });
    mkdirSync(join(candidate, 'toolchain'), { mode: 0o700 });
    writeFileSync(join(candidate, 'install/payload.txt'), 'known payload', { mode: 0o600, flag: 'wx' });
    const tree = scanOwnedTree(candidate, 'candidate');
    const receiptId = randomUUID(), identity = directoryIdentity(candidate);
    const receipt = { schema: 1, receiptId, operationId: handle.operationId, repositoryId: handle.repositoryId,
      claimId: handle.claimId, selectionDigest: selection.selectionDigest, manifestSha256: selection.targetReleaseSha256,
      nodeArchiveSha256: selection.artifactDigests.node, toolchainLockSha256: 'd'.repeat(64), omittedLinks: [],
      providers: {}, rootIdentity: identity, treeDigest: tree.digest, entries: tree.rows };
    const receiptPath = join(candidate, 'candidate-receipt.json');
    const receiptSha256 = writeCandidateReceipt(receiptPath, receipt);
    const binding = { path: candidate, identity, treeDigest: tree.digest, receiptId, receiptSha256 };
    const stage = join(handle.commonDir, 'factory', 'controller-staging', handle.operationId);
    mkdirSync(join(handle.commonDir, 'factory', 'controller-staging'), { mode: 0o700 });
    mkdirSync(stage, { mode: 0o700 });
    mkdirSync(join(stage, 'payload'), { mode: 0o700 });
    writeFileSync(join(stage, 'payload/controller.js'), 'approved stage', { mode: 0o600 });
    const stageEvidence = measureMaintenanceStage(stage);
    const expected = { operationId: handle.operationId, repositoryId: handle.repositoryId,
      claimId: handle.claimId, selectionDigest: selection.selectionDigest, manifestSha256: selection.targetReleaseSha256 };
    assert.equal(verifyBoundInstallCandidate(binding, expected).treeDigest, tree.digest);
    const store = openMaintenanceStore(handle.commonDir);
    try {
      await store.bindInstallCandidate({ handle, candidate: binding, ...stageEvidence });
      await assert.rejects(store.bindInstallCandidate({ handle, candidate: binding, ...stageEvidence }), /claim\/token\/phase/);
      await assert.rejects(store.bindInstallCandidate({ handle: { ...handle, token: randomUUID() }, candidate: binding, ...stageEvidence }), /claim\/token\/phase/);
    } finally { store.close(); }
    writeFileSync(join(stage, 'payload/controller.js'), 'changed stage');
    await assert.rejects(prepareMaintenanceHandoff(fixture.source, handle), /stage changed/);
    writeFileSync(join(stage, 'payload/controller.js'), 'approved stage');
    const inspection = await inspectMaintenance(fixture.source);
    assert.equal(inspection.status, 'incomplete');
    assert.equal(inspection.intent.candidate.treeDigest, tree.digest);
    assert.equal(inspection.intent.token, undefined);
    writeFileSync(join(candidate, 'install/payload.txt'), 'changed payload');
    assert.throws(() => verifyBoundInstallCandidate(binding, expected), /tree differs/);
    writeFileSync(join(candidate, 'install/payload.txt'), 'known payload');
    mkdirSync(join(candidate, 'install/extra-empty'), { mode: 0o700 });
    assert.throws(() => verifyBoundInstallCandidate(binding, expected), /tree differs/);
    rmSync(join(candidate, 'install/extra-empty'), { recursive: true });
    writeFileSync(receiptPath, `${readFileSync(receiptPath, 'utf8')} `);
    assert.throws(() => verifyBoundInstallCandidate(binding, expected), /receipt hash changed/);
    const forged = { ...receipt, entries: [...receipt.entries, { ...receipt.entries.find(row => row.type === 'file'), path: 'install/PAYLOAD.TXT' }] };
    const forgedBytes = `${JSON.stringify(forged)}\n`;
    writeFileSync(receiptPath, forgedBytes);
    assert.throws(() => verifyBoundInstallCandidate({ ...binding, receiptSha256: sha(forgedBytes) }, expected), /tree differs/);
  } finally { fixture.dispose(); }
});

test('unbound partial candidates cannot be reclaimed and install handoff refuses missing binding', async () => {
  const { beginRepositoryBootstrap, reclaimMaintenance, prepareMaintenanceHandoff } = await import('../dist/maintenance.js');
  const fixture = candidateFixture();
  try {
    const handle = await beginRepositoryBootstrap(fixture.source, selection, owner);
    await assert.rejects(prepareMaintenanceHandoff(fixture.source, handle), /candidate absent or unbound/);
    mkdirSync(join(handle.commonDir, 'factory', `install-candidate-${handle.operationId}`), { mode: 0o700 });
    await assert.rejects(reclaimMaintenance(fixture.source, handle.operationId, owner,
      { operatorConfirmed: true, note: 'inspected disposable fixture' }), /candidate absent or unbound/);
  } finally { fixture.dispose(); }
});

test('candidate scanner refuses links, unsafe paths and oversized files', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-candidate-scan-')));
  try {
    mkdirSync(join(root, 'install'), { mode: 0o700 });
    writeFileSync(join(root, 'install/a'), 'x', { mode: 0o600 });
    assert.equal(scanOwnedTree(root, 'candidate').entries, 2);
    symlinkSync(join(root, 'install/a'), join(root, 'install/link'));
    assert.throws(() => scanOwnedTree(root, 'candidate'), /linked/);
    rmSync(join(root, 'install/link'));
    linkSync(join(root, 'install/a'), join(root, 'install/hard'));
    assert.throws(() => scanOwnedTree(root, 'candidate'), /hard-linked/);
    rmSync(join(root, 'install/hard'));
    writeFileSync(join(root, 'install/CON'), 'z', { mode: 0o600 });
    assert.throws(() => scanOwnedTree(root, 'candidate'), /unsafe/);
    rmSync(join(root, 'install/CON'));
    truncateSync(join(root, 'install/a'), 128 * 1024 * 1024 + 1);
    assert.throws(() => scanOwnedTree(root, 'candidate'), /file exceeds bound/);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('managed preparation refuses a child group that retains a pipe-free descendant', async () => {
  const script = `const {spawn}=require('node:child_process');
    spawn(process.execPath,['-e','setTimeout(()=>{},15000)'],{stdio:'ignore',detached:false}).unref();`;
  if (process.platform === 'win32') {
    await assert.rejects(runManagedInstallCommand(process.execPath, ['-e', script], packageRoot, {}), /Windows preparer closure/);
    return;
  }
  await assert.rejects(runManagedInstallCommand(process.execPath, ['-e', script], packageRoot, {}),
    /managed process group remains/);
});

test('private Node entry rejects altered, escaping, missing and oversized requests before bootstrap', () => {
  const fixture = candidateFixture();
  const stage = realpathSync(mkdtempSync(join(tmpdir(), 'factory-private-request-')));
  try {
    for (const name of ['bundle', 'node', 'npm', 'npm/cache', 'npm/home']) mkdirSync(join(stage, name), { mode: 0o700 });
    writeFileSync(join(stage, 'selected-node-archive'), 'invalid archive', { mode: 0o600 });
    for (const name of ['user', 'global']) writeFileSync(join(stage, `npm/${name}.npmrc`), '', { mode: 0o600 });
    const requestPath = join(stage, 'preparer-request.json');
    const request = { schema: 1, requestId: randomUUID(), repository: fixture.source,
      npm: { offline: true }, stageRoot: stage, stageIdentity: `${statSync(stage).dev}:${statSync(stage).ino}`,
      source: { bundleRoot: join(stage, 'bundle'), manifestSha256: 'a'.repeat(64), nodeArchivePath: join(stage, 'selected-node-archive') },
      snapshot: { bundleRoot: join(stage, 'bundle'), nodeArchivePath: join(stage, 'selected-node-archive'),
        extractedNodeRoot: join(stage, 'node'), nodeTree: { schema: 1, digest: 'b'.repeat(64), entries: 1,
          regularBytes: 1, omittedLinks: ['bin/corepack', 'bin/npm', 'bin/npx'] } } };
    const run = (value, raw) => {
      writeFileSync(requestPath, raw ?? `${canonical(value)}\n`, { mode: 0o600 });
      const outcome = spawnSync(process.execPath, ['dist/install-entry.js', '--request', requestPath],
        { cwd: join(import.meta.dirname, '..'), encoding: 'utf8' });
      assert.equal(outcome.status, 1, outcome.stdout + outcome.stderr);
      assert.equal(outcome.stdout, '');
      assert.equal(existsSync(join(fixture.source, '.git/factory')), false);
      return outcome.stderr;
    };
    assert.match(run({ ...request, npm: { offline: 'true' } }), /invalid private npm mode/);
    assert.match(run({ ...request, snapshot: { ...request.snapshot, extractedNodeRoot: fixture.source } }), /private snapshot path differs/);
    assert.match(run(request, `${canonical(request).replace('"schema":1', '"schema":1,"schema":1')}\n`), /noncanonical or duplicate/);
    assert.match(run(request, `${canonical(request)}${' '.repeat(64 * 1024)}\n`), /size refused/);
    assert.match(run({ ...request, stageIdentity: '0:0' }), /private stage identity differs/);
    assert.match(run(request), /release manifest|ENOENT|install selection/);
  } finally { rmSync(stage, { recursive: true, force: true }); fixture.dispose(); }
});

test('public Python inventory rejects a changed new import, missing map and stale fixed module table before JS', () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-new-inventory-')));
  try {
    const bundle = join(root, 'bundle'), selectionFile = join(root, 'selection.json'), archive = join(root, 'node.tar.xz');
    const node = { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
      sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' };
    writeFileSync(selectionFile, JSON.stringify({ version: '1.2.3', platform: 'darwin-arm64', node }));
    writeFileSync(archive, 'unqualified archive');
    const packageResult = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', selectionFile,
      '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
    assert.equal(packageResult.status, 0, packageResult.stderr);
    const manifestSha256 = JSON.parse(packageResult.stdout).manifestSha256;
    const python = process.env.FACTORY_TEST_PYTHON ?? 'python3';
    const { pythonBundle, pythonArchive } = pythonSourcePaths(python, bundle, archive);
    const verify = script => spawnSync(python, [script, 'verify', '--bundle-root', pythonBundle,
      '--manifest-sha256', manifestSha256, '--node-archive', pythonArchive], { encoding: 'utf8' });
    const imported = join(bundle, 'dist/install-candidate.js'), original = readFileSync(imported);
    writeFileSync(imported, `process.stderr.write('EXECUTED');\n${original}`);
    const changed = verify(bootstrapScript);
    assert.equal(changed.status, 1);
    assert.match(changed.stderr, /changed file|size mismatch/i);
    assert.doesNotMatch(changed.stderr + changed.stdout, /EXECUTED/);
    writeFileSync(imported, original);
    const map = join(bundle, 'dist/install-entry.js.map'), mapBytes = readFileSync(map);
    rmSync(map);
    const absentMap = verify(bootstrapScript);
    assert.equal(absentMap.status, 1);
    assert.match(absentMap.stderr, /missing|source|unowned/i);
    writeFileSync(map, mapBytes);
    const staleScript = join(root, 'stale-install.py');
    const current = readFileSync(bootstrapScript, 'utf8');
    const stale = current.replace('"install", "install-candidate", "install-entry", ', '').replace(', "maintenance-entry"', '');
    assert.notEqual(stale, current);
    writeFileSync(staleScript, stale);
    const staleResult = verify(staleScript);
    assert.equal(staleResult.status, 1);
    assert.match(staleResult.stderr, /incomplete or unsorted release payload/);
    assert.equal(staleResult.stdout, '');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

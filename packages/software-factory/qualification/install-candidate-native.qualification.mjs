import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdtempSync, readFileSync, realpathSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { createRepository } from '../test/fixtures/repository.mjs';

const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const script = resolve(packageRoot, '../../skills/software-factory/scripts/install.py');
const archive = '/private/tmp/factory-node-v24.22.1-darwin-arm64-selection.tar.xz';
const cache = '/tmp/software-factory-npm-cache';
const python = process.env.FACTORY_TEST_PYTHON ?? '/Users/adam/.pyenv/versions/3.13.14/bin/python3.13';
const nodeAsset = { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
  sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' };
function fingerprint(root) {
  const digest = createHash('sha256');
  const visit = (directory, prefix = '') => {
    for (const name of readdirSync(directory).sort()) {
      const relative = prefix ? `${prefix}/${name}` : name, path = join(directory, name), info = lstatSync(path);
      digest.update(relative).update('\0').update(String(info.mode & 0o777)).update('\0');
      if (info.isDirectory()) visit(path, relative);
      else if (info.isFile()) digest.update(createHash('sha256').update(readFileSync(path)).digest());
      else throw new Error(`unexpected seed entry: ${relative}`);
    }
  };
  visit(root);
  return digest.digest('hex');
}
function fileMeasure(root) {
  let files = 0, bytes = 0;
  const visit = directory => {
    for (const name of readdirSync(directory)) {
      const path = join(directory, name), info = lstatSync(path);
      if (info.isDirectory()) visit(path);
      else if (info.isFile()) { files++; bytes += info.size; }
      else throw new Error(`unexpected stage entry: ${path}`);
    }
  };
  visit(root);
  return { files, bytes };
}

test('explicit native offline prepare binds an incomplete candidate and self-sufficient stage', async () => {
  assert.equal(process.platform, 'darwin', 'native Darwin qualification required');
  assert.equal(process.arch, 'arm64', 'native arm64 qualification required');
  assert.ok(existsSync(archive), `exact pinned Node archive prerequisite missing: ${archive}`);
  assert.ok(existsSync(join(cache, '_cacache')), `offline cache prerequisite missing: ${cache}`);
  const version = spawnSync(python, ['-c', 'import sys; print(".".join(map(str, sys.version_info[:3])))'], { encoding: 'utf8' });
  assert.equal(version.status, 0, version.stderr);
  assert.equal(version.stdout.trim(), '3.13.14', 'exact Python 3.13.14 qualification required');

  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-candidate-native-')));
  const repository = createRepository();
  const repositoryPath = realpathSync(repository.path);
  const seedPath = realpathSync(cache);
  try {
    const selection = join(container, 'selection.json'), bundle = join(container, 'bundle');
    writeFileSync(selection, JSON.stringify({ version: '1.2.3', platform: 'darwin-arm64', node: nodeAsset }));
    const packaged = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', selection,
      '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
    assert.equal(packaged.status, 0, packaged.stderr);
    const manifestSha256 = JSON.parse(packaged.stdout).manifestSha256;
    const beforeSource = readFileSync(join(repositoryPath, 'tracked.txt'));
    const beforeIndex = createHash('sha256').update(readFileSync(join(repositoryPath, '.git/index'))).digest('hex');
    const beforeGit = repository.git(['status', '--porcelain=v1']);
    const beforeSeed = fingerprint(join(seedPath, '_cacache'));
    const invocation = [script, 'prepare', '--repository', repositoryPath, '--bundle-root', bundle,
      '--manifest-sha256', manifestSha256, '--node-archive', archive, '--offline', '--offline-cache-seed', seedPath];
    const run = () => spawnSync(python, invocation,
      { encoding: 'utf8', timeout: 300_000, maxBuffer: 2 * 1024 * 1024,
        env: { ...process.env, TMPDIR: container, TMP: container, TEMP: container } });
    const beforePrivate = readdirSync(container).sort();
    const result = run();
    assert.equal(result.status, 0, `native prepare failed; fixture ${container}; stderr=${result.stderr}; stdout=${result.stdout}`);
    assert.deepEqual(readdirSync(container).sort(), beforePrivate, 'successful Python preparation must remove its exact private stage');
    assert.equal(fingerprint(join(seedPath, '_cacache')), beforeSeed, 'read-only offline seed changed');
    const receipt = JSON.parse(result.stdout);
    assert.deepEqual(Object.keys(receipt).sort(), ['candidateDigest', 'claimId', 'operationId', 'repositoryId', 'stagePath']);
    assert.match(receipt.candidateDigest, /^[a-f0-9]{64}$/);
    const factory = join(repositoryPath, '.git/factory');
    const candidate = join(factory, `install-candidate-${receipt.operationId}`);
    assert.deepEqual(readdirSync(candidate).sort(), ['candidate-receipt.json', 'install', 'toolchain']);
    const ownedReceipt = JSON.parse(readFileSync(join(candidate, 'candidate-receipt.json'), 'utf8'));
    const candidateBytes = ownedReceipt.entries.reduce((sum, entry) => sum + (entry.bytes ?? 0), 0);
    assert.ok(ownedReceipt.entries.length > 6_500 && ownedReceipt.entries.length <= 8_192,
      `measured candidate entries: ${ownedReceipt.entries.length}`);
    assert.ok(candidateBytes > 225_000_000 && candidateBytes <= 512 * 1024 * 1024,
      `measured candidate bytes: ${candidateBytes}`);
    assert.ok(readFileSync(join(candidate, 'candidate-receipt.json')).length <= 8 * 1024 * 1024);
    assert.ok(existsSync(join(candidate, 'install/node/bin/node')));
    assert.ok(existsSync(join(candidate, 'toolchain/node_modules/typescript/bin/tsc')));
    assert.ok(existsSync(join(receipt.stagePath, 'payload/node')));
    assert.ok(existsSync(join(receipt.stagePath, 'payload/dist/maintenance-entry.js')));
    const stageMeasure = fileMeasure(join(receipt.stagePath, 'payload'));
    assert.ok(stageMeasure.files <= 512 && stageMeasure.bytes <= 256 * 1024 * 1024);
    process.stdout.write(`candidate inventory: ${ownedReceipt.entries.length} entries, ${candidateBytes} bytes; `
      + `controller payload: ${stageMeasure.files} files, ${stageMeasure.bytes} bytes\n`);
    assert.ok(existsSync(join(factory, 'bootstrap-incomplete')));
    assert.ok(!existsSync(join(factory, 'install')));
    assert.ok(!existsSync(join(factory, 'toolchain')));
    const { inspectMaintenance } = await import('../dist/maintenance.js');
    const inspection = await inspectMaintenance(repositoryPath);
    assert.equal(inspection.status, 'incomplete');
    assert.equal(inspection.intent?.phase, 'preparing');
    assert.equal(inspection.intent?.candidate?.treeDigest, receipt.candidateDigest);
    assert.equal(inspection.claims, 1);
    const staged = spawnSync(join(receipt.stagePath, 'payload/node'), [join(receipt.stagePath, 'payload/dist/maintenance-entry.js'), '--self-check'],
      { encoding: 'utf8' });
    assert.equal(staged.status, 0, staged.stderr);
    assert.match(staged.stdout, /selfCheck/);
    const unavailable = spawnSync(join(receipt.stagePath, 'payload/node'),
      [join(receipt.stagePath, 'payload/dist/maintenance-entry.js'), '--publish'], { encoding: 'utf8' });
    assert.equal(unavailable.status, 1);
    assert.equal(unavailable.stdout, '');
    assert.match(unavailable.stderr, /publication unavailable/);
    assert.deepEqual(readFileSync(join(repositoryPath, 'tracked.txt')), beforeSource);
    assert.equal(createHash('sha256').update(readFileSync(join(repositoryPath, '.git/index'))).digest('hex'), beforeIndex);
    assert.equal(repository.git(['status', '--porcelain=v1']), beforeGit);
    const markerBytes = readFileSync(join(factory, 'bootstrap-incomplete'));
    const candidateReceiptBytes = readFileSync(join(candidate, 'candidate-receipt.json'));
    const second = run();
    assert.equal(second.status, 1, `second installer unexpectedly succeeded: ${second.stdout}`);
    assert.equal(second.stdout, '');
    assert.deepEqual(readFileSync(join(factory, 'bootstrap-incomplete')), markerBytes);
    assert.deepEqual(readFileSync(join(candidate, 'candidate-receipt.json')), candidateReceiptBytes);

    const target = join(candidate, 'install/runtime/dist/install.js'), original = readFileSync(target);
    writeFileSync(target, `${original}\nchanged`);
    assert.equal((await inspectMaintenance(repositoryPath)).status, 'blocked');
    const { reclaimMaintenance, prepareMaintenanceHandoff } = await import('../dist/maintenance.js');
    await assert.rejects(reclaimMaintenance(repositoryPath, receipt.operationId,
      { host: 'fixture-host', pid: process.pid, start: 'fixture' },
      { operatorConfirmed: true, note: 'inspected disposable candidate' }), /candidate tree differs/);
    writeFileSync(target, original);
    const { openMaintenanceStore } = await import('../dist/store.js');
    const store = openMaintenanceStore(join(repositoryPath, '.git'));
    let claim;
    try { claim = store.readMaintenanceClaim(receipt.operationId); } finally { store.close(); }
    const handle = { operationId: receipt.operationId, repositoryId: receipt.repositoryId, claimId: receipt.claimId,
      token: claim.token, commonDir: join(repositoryPath, '.git') };
    const stagedFile = join(receipt.stagePath, 'payload/dist/maintenance-entry.js'), stagedBytes = readFileSync(stagedFile);
    writeFileSync(stagedFile, `${stagedBytes}\nchanged`);
    await assert.rejects(prepareMaintenanceHandoff(repositoryPath, handle), /prepared install stage changed/);
    writeFileSync(stagedFile, stagedBytes);
    const selectedModule = join(bundle, 'dist/install-entry.js');
    writeFileSync(selectedModule, `${readFileSync(selectedModule)}\nchanged`);
    const changedSource = run();
    assert.equal(changedSource.status, 1);
    assert.match(changedSource.stderr, /changed file|size mismatch/i);
    assert.equal(changedSource.stdout, '');
    assert.deepEqual(readFileSync(join(factory, 'bootstrap-incomplete')), markerBytes);
  } finally {
    repository.dispose();
    rmSync(container, { recursive: true, force: true });
  }
});

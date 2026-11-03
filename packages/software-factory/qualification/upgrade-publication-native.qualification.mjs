import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRepository } from '../test/fixtures/repository.mjs';

const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const script = resolve(packageRoot, '../../skills/default/software-factory/scripts/install.py');
const archiveInput = process.env.FACTORY_TEST_NODE_ARCHIVE;
const cacheInput = process.env.FACTORY_TEST_NPM_CACHE_SEED;
const python = process.env.FACTORY_TEST_PYTHON ?? '/Users/adam/.pyenv/versions/3.13.14/bin/python3.13';
const node = { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
  sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' };
function hashFile(path) { return createHash('sha256').update(readFileSync(path)).digest('hex'); }
function fingerprint(root) {
  const digest = createHash('sha256');
  const visit = (directory, prefix = '') => {
    for (const name of readdirSync(directory).sort()) {
      const relative = prefix ? `${prefix}/${name}` : name, path = join(directory, name), info = lstatSync(path);
      digest.update(relative).update('\0').update(String(info.mode & 0o777)).update('\0');
      if (info.isDirectory()) visit(path, relative);
      else if (info.isFile()) digest.update(createHash('sha256').update(readFileSync(path)).digest());
      else throw new Error(`unexpected cache entry: ${relative}`);
    }
  };
  visit(root);
  return digest.digest('hex');
}

test('public authenticated upgrade publishes a new installed release from an owned v7 baseline', async () => {
  assert.equal(process.platform, 'darwin', 'native Darwin qualification required');
  assert.equal(process.arch, 'arm64', 'native arm64 qualification required');
  assert.ok(archiveInput && existsSync(archiveInput), 'exact pinned Node archive is required');
  assert.ok(cacheInput && existsSync(join(cacheInput, '_cacache')), 'offline cache seed is required');
  const archive = realpathSync(archiveInput), cache = realpathSync(cacheInput);
  assert.equal(hashFile(archive), node.sha256, 'selected Node archive differs from pin');
  const version = spawnSync(python, ['-c', 'import sys; print(".".join(map(str, sys.version_info[:3])))'], { encoding: 'utf8' });
  assert.equal(version.status, 0, version.stderr);
  assert.equal(version.stdout.trim(), '3.13.14');
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-install-native-')));
  const repository = createRepository();
  const root = realpathSync(repository.path);
  try {
    const authoring = join(root, '.factory');
    mkdirSync(authoring);
    const customPackage = Buffer.from('{"name":"my-custom-authoring","type":"module","description":"keep user bytes"}\n');
    const customAgents = Buffer.from('{"agents":["my-custom-agent"]}\n');
    writeFileSync(join(authoring, 'package.json'), customPackage);
    writeFileSync(join(authoring, 'agents.json'), customAgents);
    const descriptor = join(container, 'selection.json'), bundle = join(container, 'bundle');
    writeFileSync(descriptor, JSON.stringify({ version: '1.2.3', platform: 'darwin-arm64', node }));
    const packaged = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
      '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
    assert.equal(packaged.status, 0, packaged.stderr);
    const manifestSha256 = JSON.parse(packaged.stdout).manifestSha256;
    const source = readFileSync(join(root, 'tracked.txt'));
    const index = createHash('sha256').update(readFileSync(join(root, '.git/index'))).digest('hex');
    const status = repository.git(['status', '--porcelain=v1']);
    const cacheDigest = fingerprint(join(cache, '_cacache'));
    const outcome = spawnSync(python, [script, 'install', '--repository', root, '--bundle-root', bundle,
      '--manifest-sha256', manifestSha256, '--node-archive', archive, '--offline', '--offline-cache-seed', realpathSync(cache)],
    { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024,
      env: { ...process.env, TMPDIR: container, TMP: container, TEMP: container } });
    assert.equal(outcome.status, 0, `public install failed: ${outcome.stderr}`);
    const first = JSON.parse(outcome.stdout);
    assert.equal(first.state, 'ready');
    const factory = join(root, '.git/factory');
    const originalReceipt = readFileSync(join(factory, 'installed-receipt.json'));
    const baselineCli = spawnSync(join(factory, 'install/node/bin/node'), [join(factory, 'install/runtime/dist/cli.js'), '--help'],
      { encoding: 'utf8', timeout: 30000 });
    assert.equal(baselineCli.status, 0, baselineCli.stderr);
    const targetDescriptor = join(container, 'target-selection.json'), targetBundle = join(container, 'target-bundle');
    writeFileSync(targetDescriptor, JSON.stringify({ version: '1.2.4', platform: 'darwin-arm64', node }));
    const targetPackage = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', targetDescriptor,
      '--source-root', packageRoot, '--destination', targetBundle], { encoding: 'utf8' });
    assert.equal(targetPackage.status, 0, targetPackage.stderr);
    const targetSha = JSON.parse(targetPackage.stdout).manifestSha256;
    const upgraded = spawnSync(python, [script, 'upgrade', '--repository', root, '--bundle-root', targetBundle,
      '--manifest-sha256', targetSha, '--node-archive', archive, '--offline', '--offline-cache-seed', realpathSync(cache)],
    { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024,
      env: { ...process.env, TMPDIR: container, TMP: container, TEMP: container } });
    assert.equal(upgraded.status, 0, `public upgrade failed: ${upgraded.stderr}`);
    const result = JSON.parse(upgraded.stdout);
    assert.equal(result.state, 'ready');
    assert.notEqual(result.operationId, first.operationId);
    assert.deepEqual(readFileSync(join(factory, 'installed-receipt.json')), originalReceipt);
    const manifest = JSON.parse(readFileSync(join(factory, 'install/runtime/release-manifest.json'), 'utf8'));
    assert.equal(manifest.version, '1.2.4');
    assert.ok(!existsSync(join(factory, 'upgrade-incomplete')));
    assert.ok(!existsSync(join(factory, 'controller-staging', result.operationId)));
    const backupRoot = join(factory, 'maintenance-backups', result.operationId), backups = readdirSync(backupRoot);
    assert.equal(backups.length, 1);
    const backupPath = join(backupRoot, backups[0], 'history.sqlite');
    const backupUrl = pathToFileURL(backupPath); backupUrl.searchParams.set('mode', 'ro'); backupUrl.searchParams.set('immutable', '1');
    const backup = new DatabaseSync(backupUrl, { readOnly: true });
    try {
      assert.equal(backup.prepare('PRAGMA integrity_check').get().integrity_check, 'ok');
      assert.equal(backup.prepare('SELECT release FROM repository').get().release, '1.2.3');
      assert.equal(backup.prepare('SELECT count(*) AS count FROM owner_claims').get().count, 1);
    } finally { backup.close(); }
    const { inspectMaintenance } = await import('../dist/maintenance.js');
    assert.equal((await inspectMaintenance(root)).status, 'ready');
    const cli = spawnSync(join(factory, 'install/node/bin/node'), [join(factory, 'install/runtime/dist/cli.js'), '--help'],
      { encoding: 'utf8', timeout: 30000 });
    assert.equal(cli.status, 0, cli.stderr);
    assert.deepEqual(readFileSync(join(authoring, 'package.json')), customPackage);
    assert.deepEqual(readFileSync(join(authoring, 'agents.json')), customAgents);
    assert.deepEqual(readFileSync(join(root, 'tracked.txt')), source);
    assert.equal(createHash('sha256').update(readFileSync(join(root, '.git/index'))).digest('hex'), index);
    assert.equal(fingerprint(join(cache, '_cacache')), cacheDigest);
  } finally { repository.dispose(); rmSync(container, { recursive: true, force: true }); }
});

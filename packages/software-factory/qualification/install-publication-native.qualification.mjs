import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
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
const node = { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
  sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' };
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

test('public pinned offline install reaches ready through the foreground staged controller', async () => {
  assert.equal(process.platform, 'darwin', 'native Darwin qualification required');
  assert.equal(process.arch, 'arm64', 'native arm64 qualification required');
  assert.ok(existsSync(archive), `exact pinned Node archive missing: ${archive}`);
  assert.ok(existsSync(join(cache, '_cacache')), `offline cache missing: ${cache}`);
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
    const result = JSON.parse(outcome.stdout);
    assert.equal(result.state, 'ready');
    const factory = join(root, '.git/factory');
    assert.ok(existsSync(join(factory, 'install/runtime/dist/cli.js')));
    assert.ok(existsSync(join(factory, 'install/node/bin/node')));
    assert.ok(existsSync(join(factory, 'toolchain/node_modules/typescript/bin/tsc')));
    const owned = JSON.parse(readFileSync(join(factory, 'installed-receipt.json'), 'utf8'));
    assert.equal(owned.version, 1);
    assert.equal(owned.release, '1.2.3');
    assert.equal(owned.targetSchema, 7);
    assert.equal(owned.operationId, result.operationId);
    assert.equal(owned.authoring.length, 9);
    assert.ok(owned.authoring.every(file => file.path !== 'package.json' && file.path !== 'agents.json'));
    assert.deepEqual(readFileSync(join(authoring, 'package.json')), customPackage);
    assert.deepEqual(readFileSync(join(authoring, 'agents.json')), customAgents);
    assert.ok(existsSync(join(authoring, 'prompts/implementation.md')));
    assert.ok(existsSync(join(authoring, 'workflows/change.ts')));
    assert.ok(!existsSync(join(factory, 'controller-staging', result.operationId)));
    assert.ok(!existsSync(join(factory, 'bootstrap-incomplete')));
    const installedNode = join(factory, 'install/node/bin/node');
    const npmCli = join(factory, 'install/node/lib/node_modules/npm/bin/npm-cli.js');
    const tscCli = join(factory, 'toolchain/node_modules/typescript/bin/tsc');
    for (const [entry, expected] of [
      [['--version'], 'v24.22.1'], [[npmCli, '--version'], '11.19.1'], [[tscCli, '--version'], 'Version 7.0.2'],
    ]) {
      const direct = spawnSync(installedNode, entry, { encoding: 'utf8', timeout: 30000 });
      assert.equal(direct.status, 0, direct.stderr);
      assert.equal(direct.stdout.trim(), expected);
    }
    const { inspectMaintenance } = await import('../dist/maintenance.js');
    const inspected = await inspectMaintenance(root);
    assert.equal(inspected.status, 'ready');
    assert.equal(inspected.claims, 0);
    assert.deepEqual(readFileSync(join(root, 'tracked.txt')), source);
    assert.equal(createHash('sha256').update(readFileSync(join(root, '.git/index'))).digest('hex'), index);
    assert.equal(fingerprint(join(cache, '_cacache')), cacheDigest);
    assert.deepEqual(repository.git(['status', '--porcelain=v1']).split('\n').filter(Boolean).sort(),
      [...new Set([...status.split('\n').filter(Boolean), '?? .factory/'])].sort());
    const installedDigest = createHash('sha256').update(readFileSync(join(factory, 'install/runtime/release-manifest.json'))).digest('hex');
    const second = spawnSync(python, [script, 'install', '--repository', root, '--bundle-root', bundle,
      '--manifest-sha256', manifestSha256, '--node-archive', archive, '--offline', '--offline-cache-seed', realpathSync(cache)],
    { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024,
      env: { ...process.env, TMPDIR: container, TMP: container, TEMP: container } });
    assert.equal(second.status, 1, 'second installer must refuse the occupied factory root');
    assert.equal(createHash('sha256').update(readFileSync(join(factory, 'install/runtime/release-manifest.json'))).digest('hex'), installedDigest);
    assert.equal((await inspectMaintenance(root)).status, 'ready');
  } finally { repository.dispose(); rmSync(container, { recursive: true, force: true }); }
});

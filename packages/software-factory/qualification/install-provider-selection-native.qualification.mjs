import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { copyFileSync, existsSync, lstatSync, mkdtempSync, readFileSync, realpathSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import test from 'node:test';
import { createRepository } from '../test/fixtures/repository.mjs';

const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const script = resolve(packageRoot, '../../skills/software-factory/scripts/install.py');
const archive = '/private/tmp/factory-node-v24.22.1-darwin-arm64-selection.tar.xz';
const cache = '/tmp/software-factory-npm-cache';
const codex = '/Users/adam/homebrew/Caskroom/codex/0.163.0/bin/codex';
const copilot = '/Users/adam/Library/Caches/copilot/pkg/darwin-arm64/1.0.101';
const copilotManifest = '/private/tmp/factory-copilot-1.0.101-package-manifest.json';
const python = process.env.FACTORY_TEST_PYTHON ?? '/Users/adam/.pyenv/versions/3.13.14/bin/python3.13';
const node = { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
  sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' };
function sha(bytes) { return createHash('sha256').update(bytes).digest('hex'); }
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
function publicInstall(root, bundle, digest, providers, temp) {
  return spawnSync(python, [script, 'install', '--repository', root, '--bundle-root', bundle,
    '--manifest-sha256', digest, '--node-archive', archive, '--providers', providers,
    '--offline', '--offline-cache-seed', realpathSync(cache)],
  { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024,
    env: { ...process.env, TMPDIR: temp, TMP: temp, TEMP: temp } });
}

test('public selected-provider install binds exact external Codex and Copilot without launching either', async () => {
  assert.equal(process.platform, 'darwin', 'native Darwin qualification required');
  assert.equal(process.arch, 'arm64', 'native arm64 qualification required');
  for (const path of [archive, join(cache, '_cacache'), codex, copilot, copilotManifest])
    assert.ok(existsSync(path), `exact prerequisite missing: ${path}`);
  const version = spawnSync(python, ['-c', 'import sys; print(".".join(map(str, sys.version_info[:3])))'], { encoding: 'utf8' });
  assert.equal(version.status, 0, version.stderr);
  assert.equal(version.stdout.trim(), '3.13.14');
  const temp = realpathSync(mkdtempSync(join(tmpdir(), 'factory-selected-native-')));
  const repository = createRepository();
  const root = realpathSync(repository.path);
  try {
    const manifestCopy = join(temp, 'copilot-manifest.json');
    copyFileSync(copilotManifest, manifestCopy);
    const providers = join(temp, 'providers.json');
    const selected = { codex: { executable: codex, modes: ['read-only', 'workspace-write'] },
      copilot: { packageRoot: copilot, manifestFile: manifestCopy, modes: ['read-only'] } };
    writeFileSync(providers, JSON.stringify(selected));
    const descriptor = join(temp, 'selection.json'), bundle = join(temp, 'bundle');
    writeFileSync(descriptor, JSON.stringify({ version: '1.2.3', platform: 'darwin-arm64', node }));
    const packaged = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
      '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
    assert.equal(packaged.status, 0, packaged.stderr);
    const digest = JSON.parse(packaged.stdout).manifestSha256;
    const source = readFileSync(join(root, 'tracked.txt'));
    const index = sha(readFileSync(join(root, '.git/index')));
    const status = repository.git(['status', '--porcelain=v1']);
    const cacheDigest = fingerprint(join(cache, '_cacache'));
    const manifestBytes = readFileSync(manifestCopy);
    writeFileSync(manifestCopy, Buffer.concat([manifestBytes, Buffer.from('\n')]));
    const unqualified = spawnSync(python, [script, 'verify', '--bundle-root', bundle,
      '--manifest-sha256', digest, '--node-archive', archive, '--providers', providers],
    { encoding: 'utf8', timeout: 120_000, maxBuffer: 2 * 1024 * 1024,
      env: { ...process.env, TMPDIR: temp, TMP: temp, TEMP: temp } });
    assert.equal(unqualified.status, 1, 'changed selected artifact must refuse the public verifier');
    assert.match(unqualified.stderr, /semantic selection validation refused/i);
    assert.ok(!existsSync(join(root, '.git/factory')));
    writeFileSync(manifestCopy, manifestBytes);
    const outcome = publicInstall(root, bundle, digest, providers, temp);
    assert.equal(outcome.status, 0, `selected public install failed: ${outcome.stderr}`);
    assert.doesNotMatch(outcome.stdout + outcome.stderr, /token|nonce|manifestCopy|Caskroom|Library\/Caches/);
    const ready = JSON.parse(outcome.stdout);
    assert.equal(ready.state, 'ready');
    const factory = join(root, '.git/factory');
    const installedNode = join(factory, 'install/node/bin/node');
    const cli = join(factory, 'install/runtime/dist/cli.js');
    const bound = spawnSync(installedNode, ['--input-type=module', '-e',
      `const {loadInstalledBindings}=await import(process.argv[1]);
const selected=await loadInstalledBindings(process.argv[2],process.argv[3]);
process.stdout.write(JSON.stringify(Object.fromEntries(Object.entries(selected.adapters).map(([name,adapter])=>[name,adapter.capabilities]))));`,
      pathToFileURL(join(factory, 'install/runtime/dist/installed-bindings.js')).href, cli, root],
    { encoding: 'utf8', timeout: 30_000 });
    assert.equal(bound.status, 0, bound.stderr);
    const adapters = JSON.parse(bound.stdout);
    assert.deepEqual(Object.keys(adapters).sort(), ['codex', 'copilot']);
    assert.ok(adapters.codex.includes('read-only'));
    assert.ok(adapters.codex.includes('workspace-write'));
    assert.ok(adapters.copilot.includes('read-only'));
    assert.ok(!adapters.copilot.includes('workspace-write'));
    const { openRepositoryStore } = await import('../dist/store.js');
    const store = openRepositoryStore(join(root, '.git'));
    try { assert.deepEqual([store.readNotificationPreferences().successNotices,
      store.readNotificationPreferences().reminders], [false, false]); }
    finally { store.close(); }
    assert.deepEqual(readFileSync(join(root, 'tracked.txt')), source);
    assert.equal(sha(readFileSync(join(root, '.git/index'))), index);
    assert.equal(fingerprint(join(cache, '_cacache')), cacheDigest);
    assert.deepEqual(repository.git(['status', '--porcelain=v1']).split('\n').filter(Boolean).sort(),
      [...new Set([...status.split('\n').filter(Boolean), '?? .factory/'])].sort());
    assert.ok(!existsSync(join(factory, 'install/runtime/copilot')));
    assert.ok(!existsSync(join(factory, 'install/runtime/codex')));
    const receipt = join(factory, `install-candidate-${ready.operationId}`, 'candidate-receipt.json');
    const originalReceipt = readFileSync(receipt);
    const modified = JSON.parse(originalReceipt);
    modified.providers.codex.modes = ['read-only'];
    writeFileSync(receipt, JSON.stringify(modified));
    const changedDescriptor = spawnSync(installedNode, [cli, 'history', '--repository', root, '--invocation', '00000000-0000-4000-8000-000000000000', '--json'],
      { encoding: 'utf8', timeout: 30_000 });
    assert.equal(changedDescriptor.status, 3, 'changed durable provider descriptor must refuse at startup');
    writeFileSync(receipt, originalReceipt);
    writeFileSync(manifestCopy, Buffer.concat([readFileSync(manifestCopy), Buffer.from('\n')]));
    const changedArtifact = spawnSync(installedNode, [cli, 'history', '--repository', root, '--invocation', '00000000-0000-4000-8000-000000000000', '--json'],
      { encoding: 'utf8', timeout: 30_000 });
    assert.equal(changedArtifact.status, 3, 'changed external manifest must refuse at startup');
    assert.doesNotMatch(changedArtifact.stderr, /Caskroom|Library\/Caches|copilot-manifest\.json/);
  } finally { repository.dispose(); rmSync(temp, { recursive: true, force: true }); }
});

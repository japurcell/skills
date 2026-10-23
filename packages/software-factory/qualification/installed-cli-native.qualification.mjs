import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { createRepository } from '../test/fixtures/repository.mjs';

const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const script = resolve(packageRoot, '../../skills/software-factory/scripts/install.py');
const platform = `${process.platform}-${process.arch}`;
const assets = {
  'darwin-arm64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
    sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' },
  'linux-x64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz',
    sha256: '6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6' },
};
const archive = process.env.FACTORY_TEST_NODE_ARCHIVE ?? (platform === 'darwin-arm64'
  ? '/private/tmp/factory-node-v24.22.1-darwin-arm64-selection.tar.xz'
  : '/tmp/factory-node-v24.22.1-linux-x64-install-selection.tar.xz');
const cache = process.env.FACTORY_TEST_NPM_CACHE_SEED ?? '/tmp/software-factory-npm-cache';
const python = process.env.FACTORY_TEST_PYTHON ?? '/Users/adam/.pyenv/versions/3.13.14/bin/python3.13';
const node = assets[platform];
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

test('installed CLI runs a command-only workflow and refuses changed published bytes', async () => {
  assert.ok(node, 'native POSIX qualification requires darwin-arm64 or linux-x64');
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
    writeFileSync(descriptor, JSON.stringify({ version: '1.2.3', platform, node }));
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
    const workflow = join(authoring, 'workflows/command-only.ts');
    writeFileSync(workflow, `import type { WorkflowContext } from '@local/software-factory';
export async function run(context: WorkflowContext) {
  const command = await context.command('pinned-node', { argv: [process.execPath, '-e', 'process.stdout.write(process.version)'] });
  if (command.exitCode !== 0 || command.cleanup !== 'complete') throw new Error('pinned command failed');
  return { kind: 'installed-command', attemptId: command.attemptId };
}
`);
    const input = join(container, 'input.json');
    writeFileSync(input, '{}\n');
    const cli = join(factory, 'install/runtime/dist/cli.js');
    const help = spawnSync(installedNode, [cli, '--help'], { encoding: 'utf8', timeout: 30_000 });
    assert.equal(help.status, 0, help.stderr);
    assert.match(help.stdout, /^software-factory\n/);
    assert.doesNotMatch(help.stdout, /development/);
    const invoked = spawnSync(installedNode, [cli, 'invoke', '--repository', root,
      '--workflow', '.factory/workflows/command-only.ts', '--input', input, '--worktree', root, '--json'],
    { encoding: 'utf8', timeout: 120_000, maxBuffer: 2 * 1024 * 1024 });
    assert.equal(invoked.status, 0, `installed invoke failed: ${invoked.stderr}`);
    const invocation = JSON.parse(invoked.stdout);
    assert.equal(invocation.outcome, 'succeeded');
    const history = spawnSync(installedNode, [cli, 'history', '--repository', root,
      '--invocation', invocation.invocationId, '--json'], { encoding: 'utf8', timeout: 30_000 });
    assert.equal(history.status, 0, history.stderr);
    assert.ok(JSON.parse(history.stdout).invocation);
    const bound = spawnSync(installedNode, ['--input-type=module', '-e',
      `const { loadInstalledBindings } = await import(process.argv[1]);
const { sendDesktopNotification } = await import(process.argv[4]);
const selected = await loadInstalledBindings(process.argv[2], process.argv[3]);
process.stdout.write(JSON.stringify({ adapters: Object.keys(selected.adapters), senderBound: selected.notificationSender === sendDesktopNotification }));`,
      pathToFileURL(join(factory, 'install/runtime/dist/installed-bindings.js')).href, cli, root,
      pathToFileURL(join(factory, 'install/runtime/dist/native/notifications.js')).href],
    { encoding: 'utf8', timeout: 30_000 });
    assert.equal(bound.status, 0, bound.stderr);
    assert.deepEqual(JSON.parse(bound.stdout), { adapters: [], senderBound: true },
      'only the installed sender is bound; no unselected provider is bound');
    const { openRepositoryStore } = await import('../dist/store.js');
    const store = openRepositoryStore(join(root, '.git'));
    try { assert.deepEqual([store.readNotificationPreferences().successNotices,
      store.readNotificationPreferences().reminders], [false, false]); }
    finally { store.close(); }
    const authoredPrompt = join(authoring, 'prompts/implementation.md');
    writeFileSync(authoredPrompt, Buffer.concat([readFileSync(authoredPrompt), Buffer.from('\nUser customization.\n')]));
    const customized = spawnSync(installedNode, [cli, 'history', '--repository', root,
      '--invocation', invocation.invocationId, '--json'], { encoding: 'utf8', timeout: 30_000 });
    assert.equal(customized.status, 0, 'editable authoring files must not be frozen at startup');
    writeFileSync(join(authoring, 'workflows/unselected-agent.ts'), `import type { WorkflowContext } from '@local/software-factory';
export async function run(context: WorkflowContext) {
  await context.agent('unselected', { harness: 'codex', model: 'gpt-6-luna', reasoning: 'low', permissions: 'read-only', prompt: 'Do not launch' });
}
`);
    const noProvider = spawnSync(installedNode, [cli, 'invoke', '--repository', root,
      '--workflow', '.factory/workflows/unselected-agent.ts', '--input', input, '--worktree', root, '--json'],
    { encoding: 'utf8', timeout: 120_000, maxBuffer: 2 * 1024 * 1024 });
    assert.equal(noProvider.status, 1, noProvider.stderr);
    assert.match(JSON.parse(noProvider.stdout).diagnostic, /agent adapters unavailable/);
    const changedModule = join(factory, 'install/runtime/dist/accounting.js');
    writeFileSync(changedModule, Buffer.concat([readFileSync(changedModule), Buffer.from('\n// changed after publication\n')]));
    const changed = spawnSync(installedNode, [cli, 'history', '--repository', root,
      '--invocation', invocation.invocationId, '--json'], { encoding: 'utf8', timeout: 30_000 });
    assert.equal(changed.status, 3, 'changed installed code must refuse before CLI dispatch');
    assert.match(changed.stderr, /installed|inventory|release/i);
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

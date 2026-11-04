import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { chmodSync, existsSync, linkSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, renameSync, rmdirSync, rmSync, symlinkSync, unlinkSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:net';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { DatabaseSync } from 'node:sqlite';
import { createRepository } from '../test/fixtures/repository.mjs';

const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const platform = `${process.platform}-${process.arch}`;
const nodes = {
  'darwin-arm64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz',
    sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' },
  'linux-x64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz',
    sha256: '6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6' },
};
const hash = value => createHash('sha256').update(value).digest('hex');

test('native installed dependency ownership separates selected file damage and preserves strict startup and upgrade', async t => {
  const node = nodes[platform];
  assert.ok(node, 'native dependency ownership qualification requires Darwin arm64 or Linux x64');
  assert.equal(process.version, node.version, 'exact pinned Node required');
  const archive = process.env.FACTORY_TEST_NODE_ARCHIVE, cache = process.env.FACTORY_TEST_NPM_CACHE_SEED;
  const python = process.env.FACTORY_TEST_PYTHON;
  assert.ok(archive && existsSync(archive), 'exact pinned Node archive required');
  assert.ok(cache && existsSync(join(cache, '_cacache')), 'offline npm cache seed required');
  assert.ok(python && existsSync(python), 'selected Python required');
  assert.equal(hash(readFileSync(archive)), node.sha256);
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-dependency-state-native-')));
  const repository = createRepository(), root = realpathSync(repository.path), common = join(root, '.git');
  try {
    const descriptor = join(container, 'selection.json'), bundle = join(container, 'bundle');
    writeFileSync(descriptor, JSON.stringify({ version: '1.2.3', platform, node }));
    const packaged = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
      '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
    assert.equal(packaged.status, 0, packaged.stderr);
    const manifestSha256 = JSON.parse(packaged.stdout).manifestSha256;
    const home = join(container, 'home'); mkdirSync(home, { mode: 0o700 });
    const env = { PATH: process.env.PATH, HOME: home, TMPDIR: container, TMP: container, TEMP: container };
    const installed = spawnSync(python, [resolve(packageRoot, '../../skills/default/software-factory/scripts/install.py'),
      'install', '--repository', root, '--bundle-root', bundle, '--manifest-sha256', manifestSha256,
      '--node-archive', realpathSync(archive), '--offline', '--offline-cache-seed', realpathSync(cache)],
    { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024, env });
    assert.equal(installed.status, 0, `public install failed: ${installed.stderr}`);
    assert.equal(JSON.parse(installed.stdout).state, 'ready');
    const factory = join(common, 'factory'), compiler = join(factory, 'toolchain/node_modules/typescript/bin/tsc');
    const compilerBytes = readFileSync(compiler), compilerMode = lstatSync(compiler).mode & 0o777;
    unlinkSync(compiler);
    const strict = await import('../dist/installed-bindings.js');
    await assert.rejects(strict.inspectInstalledOwnership(common, root), /installed binding refused/);
    const { captureOriginalInstallation } = await import('../dist/upgrade-original.js');
    const { currentOwner } = await import('../dist/native/process.js');
    await assert.rejects(captureOriginalInstallation(common, root, currentOwner()), /installed binding refused/);
    const cli = spawnSync(join(factory, 'install/node/bin/node'), [join(factory, 'install/runtime/dist/cli.js'), '--help'],
      { encoding: 'utf8', timeout: 30_000, env });
    assert.equal(cli.status, 3, 'ordinary installed startup must refuse missing owned compiler');
    const before = readFileSync(join(factory, 'history.sqlite'));
    const { inspectInstalledDependencyState } = await import('../dist/dependency-state.js');
    const damaged = await inspectInstalledDependencyState(common, root);
    assert.deepEqual(damaged.toolchain.missing, ['node_modules/typescript/bin/tsc']);
    assert.deepEqual(damaged.toolchain.changed, []);
    assert.ok(damaged.toolchain.expected.rows.some(row => row.path === 'node_modules/typescript/bin/tsc'));
    assert.ok(!damaged.toolchain.observed.rows.some(row => row.path === 'node_modules/typescript/bin/tsc'));
    assert.deepEqual(readFileSync(join(factory, 'history.sqlite')), before, 'inspection must not write history or claims');
    writeFileSync(compiler, compilerBytes, { mode: compilerMode });
    await strict.inspectInstalledOwnership(common, root);
    const toolchain = join(factory, 'toolchain');
    const unchanged = { runtime: readFileSync(join(factory, 'install/runtime/release-manifest.json')),
      node: hash(readFileSync(join(factory, 'install/node/bin/node'))), source: readFileSync(join(root, 'tracked.txt')),
      index: readFileSync(join(common, 'index')), receipt: readFileSync(join(factory, 'installed-receipt.json')) };
    const selectedFile = async name => {
      const path = join(toolchain, name), bytes = readFileSync(path), mode = lstatSync(path).mode & 0o777;
      try {
        writeFileSync(path, 'process.exit(99); // damaged compiler must never execute\n');
        const inspected = await inspectInstalledDependencyState(common, root);
        assert.deepEqual(inspected.toolchain.changed, [name]);
        assert.deepEqual(inspected.toolchain.missing, []);
        assert.notEqual(inspected.toolchain.observed.rows.find(row => row.path === name).sha256,
          inspected.toolchain.expected.rows.find(row => row.path === name).sha256);
        await assert.rejects(strict.inspectInstalledOwnership(common, root), /installed binding refused/);
        await assert.rejects(captureOriginalInstallation(common, root, currentOwner()), /installed binding refused/);
      } finally { writeFileSync(path, bytes, { mode }); chmodSync(path, mode); }
    };
    await t.test('changed owned compiler is recorded without executing it', async () => {
      await selectedFile('node_modules/typescript/bin/tsc');
      assert.deepEqual(readFileSync(join(factory, 'history.sqlite')), before);
    });
    await t.test('missing owned lock is evidence rather than a replacement selection', async () => {
      const path = join(toolchain, 'package-lock.json'), bytes = readFileSync(path);
      try {
        unlinkSync(path);
        assert.deepEqual((await inspectInstalledDependencyState(common, root)).toolchain.missing, ['package-lock.json']);
        await assert.rejects(strict.inspectInstalledOwnership(common, root), /installed binding refused/);
      } finally { writeFileSync(path, bytes, { mode: 0o600 }); }
    });
    await t.test('unowned extra entry refuses instead of being selected', async () => {
      const path = join(toolchain, 'foreign'); writeFileSync(path, 'foreign', { mode: 0o600 });
      try { await assert.rejects(inspectInstalledDependencyState(common, root), /installed binding refused/); }
      finally { unlinkSync(path); }
    });
    await t.test('owned file mode changes refuse rather than broadening byte repair', async () => {
      chmodSync(compiler, compilerMode === 0o700 ? 0o600 : 0o700);
      try { await assert.rejects(inspectInstalledDependencyState(common, root), /installed binding refused/); }
      finally { chmodSync(compiler, compilerMode); }
    });
    for (const [name, make] of [['symlink', symlinkSync], ['hardlink', linkSync]]) {
      await t.test(`${name} at an owned selected path refuses`, async () => {
        const outside = join(container, `${name}-target`); writeFileSync(outside, compilerBytes, { mode: compilerMode });
        unlinkSync(compiler); make(outside, compiler);
        try { await assert.rejects(inspectInstalledDependencyState(common, root), /installed binding refused/); }
        finally { unlinkSync(compiler); writeFileSync(compiler, compilerBytes, { mode: compilerMode }); }
      });
    }
    await t.test('special entry refuses', async () => {
      const cwd = process.cwd(), server = createServer();
      process.chdir(toolchain);
      try {
        await new Promise((resolve, reject) => { server.once('error', reject); server.listen('foreign.socket', resolve); });
        await assert.rejects(inspectInstalledDependencyState(common, root), /installed binding refused/);
      } finally {
        await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
        process.chdir(cwd);
      }
    });
    await t.test('selected directory loss and changed root identity refuse', async () => {
      const directory = join(toolchain, 'node_modules/typescript/bin'), saved = join(container, 'saved-bin');
      renameSync(directory, saved);
      try { await assert.rejects(inspectInstalledDependencyState(common, root), /installed binding refused/); }
      finally { renameSync(saved, directory); }
      const savedRoot = join(factory, 'saved-toolchain'); renameSync(toolchain, savedRoot);
      try {
        await assert.rejects(inspectInstalledDependencyState(common, root), /installed binding refused/);
        mkdirSync(toolchain, { mode: 0o700 });
        await assert.rejects(inspectInstalledDependencyState(common, root), /installed binding refused/);
      }
      finally { rmdirSync(toolchain); renameSync(savedRoot, toolchain); }
    });
    await t.test('unrelated runtime damage refuses alongside selected damage', async () => {
      const path = join(factory, 'install/runtime/dist/accounting.js'), bytes = readFileSync(path);
      try {
        writeFileSync(path, Buffer.concat([bytes, Buffer.from('\n// changed\n')]));
        unlinkSync(compiler);
        await assert.rejects(inspectInstalledDependencyState(common, root), /installed binding refused/);
      } finally { writeFileSync(path, bytes); writeFileSync(compiler, compilerBytes, { mode: compilerMode }); }
    });
    await t.test('future dependency completion is refused rather than falling back to install ownership', async () => {
      const database = new DatabaseSync(join(factory, 'history.sqlite'));
      try {
        database.exec('BEGIN IMMEDIATE');
        database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)').run('dependencies.completed', JSON.stringify(damaged.active.completion));
        database.exec('COMMIT');
        await assert.rejects(inspectInstalledDependencyState(common, root), /installed binding refused/);
        await assert.rejects(strict.inspectInstalledOwnership(common, root), /installed binding refused/);
      } finally {
        database.prepare("DELETE FROM observation_events WHERE kind='dependencies.completed'").run(); database.close();
      }
    });
    assert.deepEqual(readFileSync(join(factory, 'install/runtime/release-manifest.json')), unchanged.runtime);
    assert.equal(hash(readFileSync(join(factory, 'install/node/bin/node'))), unchanged.node);
    assert.deepEqual(readFileSync(join(root, 'tracked.txt')), unchanged.source);
    assert.deepEqual(readFileSync(join(common, 'index')), unchanged.index);
    assert.deepEqual(readFileSync(join(factory, 'installed-receipt.json')), unchanged.receipt);
    await strict.inspectInstalledOwnership(common, root);
    await t.test('genuine public upgrade retains strict old trees while only its current toolchain is inspectable', async () => {
      const upgradedBundle = join(container, 'upgrade-bundle');
      writeFileSync(descriptor, JSON.stringify({ version: '1.2.4', platform, node }));
      const packagedUpgrade = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
        '--source-root', packageRoot, '--destination', upgradedBundle], { encoding: 'utf8' });
      assert.equal(packagedUpgrade.status, 0, packagedUpgrade.stderr);
      const upgraded = spawnSync(python, [resolve(packageRoot, '../../skills/default/software-factory/scripts/install.py'),
        'upgrade', '--repository', root, '--bundle-root', upgradedBundle,
        '--manifest-sha256', JSON.parse(packagedUpgrade.stdout).manifestSha256,
        '--node-archive', realpathSync(archive), '--offline', '--offline-cache-seed', realpathSync(cache)],
      { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024, env });
      assert.equal(upgraded.status, 0, `public upgrade failed: ${upgraded.stderr}`);
      const completion = JSON.parse(upgraded.stdout);
      assert.equal(completion.state, 'ready');
      const active = await inspectInstalledDependencyState(common, root);
      assert.equal(active.active.kind, 'upgrade.completed');
      assert.equal(active.release, '1.2.4');
      const currentCompiler = readFileSync(compiler), currentMode = lstatSync(compiler).mode & 0o777;
      try {
        unlinkSync(compiler);
        assert.deepEqual((await inspectInstalledDependencyState(common, root)).toolchain.missing, ['node_modules/typescript/bin/tsc']);
        await assert.rejects(strict.inspectInstalledOwnership(common, root), /installed binding refused/);
        await assert.rejects(captureOriginalInstallation(common, root, currentOwner()), /installed binding refused/);
      } finally { writeFileSync(compiler, currentCompiler, { mode: currentMode }); }
      await selectedFile('node_modules/typescript/bin/tsc');
      const oldFile = join(factory, `upgrade-${completion.operationId}/old/toolchain/node_modules/typescript/bin/tsc`);
      const oldBytes = readFileSync(oldFile);
      try {
        writeFileSync(oldFile, 'changed retained original');
        await assert.rejects(inspectInstalledDependencyState(common, root), /installed binding refused/);
      } finally { writeFileSync(oldFile, oldBytes); }
      await strict.inspectInstalledOwnership(common, root);
      const database = new DatabaseSync(join(factory, 'history.sqlite'), { readOnly: true });
      try {
        assert.equal(database.prepare('SELECT count(*) AS n FROM owner_claims').get().n, 0);
        assert.equal(database.prepare("SELECT count(*) AS n FROM attempts WHERE kind='agent'").get().n, 0);
        assert.equal(database.prepare('SELECT count(*) AS n FROM sessions').get().n, 0);
      } finally { database.close(); }
    });
  } finally { repository.dispose(); rmSync(container, { recursive: true, force: true }); }
});

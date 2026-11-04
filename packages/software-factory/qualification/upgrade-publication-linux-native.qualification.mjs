import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, readlinkSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
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
const pythonInput = process.env.FACTORY_TEST_PYTHON;
let python;
const node = { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz',
  sha256: '6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6' };
// Qualification-only observation of children created by this test. No global process scan.
function linuxProcess(pid) {
  try {
    const path = `/proc/${pid}`;
    const before = readFileSync(`${path}/stat`, 'utf8');
    const fields = before.slice(before.lastIndexOf(') ') + 2).trim().split(/\s+/);
    const executable = readlinkSync(`${path}/exe`);
    const after = readFileSync(`${path}/stat`, 'utf8');
    const later = after.slice(after.lastIndexOf(') ') + 2).trim().split(/\s+/);
    assert.equal(fields[19], later[19], 'fixture process changed during observation');
    assert.equal(fields[1], later[1], 'fixture parent changed during observation');
    assert.match(fields[19], /^\d+$/);
    return { pid, parent: Number(fields[1]), start: fields[19], executable, state: later[0] };
  } catch (error) {
    if (error.code === 'ENOENT' || error.code === 'ESRCH') return undefined;
    throw error;
  }
}
function sameProcess(expected) {
  const current = linuxProcess(expected.pid);
  assert.ok(current, 'owned fixture process disappeared before signal');
  for (const key of ['pid', 'parent', 'start', 'executable'])
    assert.equal(current[key], expected[key], `owned fixture ${key} changed`);
  return current;
}
function ownedChildren(parent) {
  sameProcess(parent);
  const text = readFileSync(`/proc/${parent.pid}/task/${parent.pid}/children`, 'utf8').trim();
  const children = text ? text.split(/\s+/).map(Number).map(linuxProcess).filter(Boolean) : [];
  assert.ok(children.every(child => child.parent === parent.pid), 'fixture child changed parent');
  sameProcess(parent);
  return children;
}
function stagedController(launcher, executable) {
  const children = ownedChildren(launcher).filter(child => child.executable === executable);
  assert.ok(children.length <= 1, 'multiple staged fixture controllers');
  return children[0];
}
async function stopOwned(expected) {
  sameProcess(expected);
  process.kill(expected.pid, 'SIGSTOP');
  const deadline = Date.now() + 3000;
  while (sameProcess(expected).state !== 'T') {
    assert.ok(Date.now() < deadline, 'owned fixture process did not stop');
    await new Promise(resolve => setTimeout(resolve, 5));
  }
}
function signalOwned(expected, signal) {
  sameProcess(expected);
  process.kill(expected.pid, signal);
}
async function launcherIdentity(child) {
  await new Promise((resolve, reject) => { child.once('spawn', resolve); child.once('error', reject); });
  const identity = linuxProcess(child.pid);
  assert.ok(identity, 'fixture launcher exited before identity observation');
  assert.equal(identity.parent, process.pid);
  assert.equal(identity.executable, python, 'fixture launcher must be the selected interpreter');
  return identity;
}
async function closeHelpers(controller) {
  const deadline = Date.now() + 15000;
  while (ownedChildren(controller).length) {
    assert.ok(Date.now() < deadline, 'owned publication helper did not close');
    await new Promise(resolve => setTimeout(resolve, 50));
  }
}
function hashFile(path) { return createHash('sha256').update(readFileSync(path)).digest('hex'); }
function directoryIdentity(path) { const info = lstatSync(path, { bigint: true }); return `${info.dev}:${info.ino}`; }
function databaseSnapshot(factory) {
  const database = new DatabaseSync(join(factory, 'history.sqlite'), { readOnly: true, timeout: 100 });
  try {
    database.exec('BEGIN');
    return { repository: database.prepare('SELECT state,release FROM repository').get(),
      claims: database.prepare('SELECT count(*) AS count FROM owner_claims').get().count,
      agentAttempts: database.prepare("SELECT count(*) AS count FROM attempts WHERE kind='agent'").get().count,
      sessions: database.prepare('SELECT count(*) AS count FROM sessions').get().count,
      completions: database.prepare("SELECT cursor,kind,data FROM observation_events WHERE kind IN ('install.completed','upgrade.completed') ORDER BY cursor").all() };
  } finally { database.close(); }
}
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

test('Linux x64 public install and upgrade retain ownership through all four receipt crashes and ready-marker recovery', async () => {
  assert.equal(process.platform, 'linux', 'native Linux qualification required');
  assert.equal(process.arch, 'x64', 'native x64 qualification required');
  assert.equal(process.version, node.version, 'exact pinned Node must run the qualification');
  assert.ok(pythonInput && existsSync(pythonInput), 'FACTORY_TEST_PYTHON must select Python 3.13.14');
  python = realpathSync(pythonInput);
  assert.ok(process.env.FACTORY_ATOMIC_PYTHON, 'FACTORY_ATOMIC_PYTHON is required');
  assert.equal(realpathSync(process.env.FACTORY_ATOMIC_PYTHON), python, 'atomic helper interpreter must match selected Python');
  assert.ok(archiveInput && existsSync(archiveInput), 'exact pinned Node archive is required');
  assert.ok(cacheInput && existsSync(join(cacheInput, '_cacache')), 'offline cache seed is required');
  const archive = realpathSync(archiveInput), cache = realpathSync(cacheInput);
  assert.equal(hashFile(archive), node.sha256, 'selected Node archive differs from pin');
  const version = spawnSync(python, ['-I', '-c', 'import sys; print(".".join(map(str, sys.version_info[:3])))'],
    { encoding: 'utf8', env: { PATH: process.env.PATH } });
  assert.equal(version.status, 0, version.stderr);
  assert.equal(version.stdout.trim(), '3.13.14');
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-linux-upgrade-native-')));
  const repository = createRepository();
  const root = realpathSync(repository.path);
  try {
    const home = join(container, 'home'); mkdirSync(home, { mode: 0o700 });
    const environment = { PATH: process.env.PATH, HOME: home, XDG_CONFIG_HOME: join(home, '.config'),
      XDG_CACHE_HOME: join(home, '.cache'), TMPDIR: container, TMP: container, TEMP: container,
      FACTORY_ATOMIC_PYTHON: python };
    const pathNode = spawnSync('node', ['--version'], { encoding: 'utf8', env: environment });
    assert.equal(pathNode.status, 0, pathNode.stderr);
    assert.equal(pathNode.stdout.trim(), node.version, 'PATH must select the pinned Node');
    const authoring = join(root, '.factory');
    mkdirSync(authoring);
    const customPackage = Buffer.from('{"name":"my-custom-authoring","type":"module","description":"keep user bytes"}\n');
    const customAgents = Buffer.from('{"agents":["my-custom-agent"]}\n');
    writeFileSync(join(authoring, 'package.json'), customPackage);
    writeFileSync(join(authoring, 'agents.json'), customAgents);
    const descriptor = join(container, 'selection.json'), bundle = join(container, 'bundle');
    writeFileSync(descriptor, JSON.stringify({ version: '1.2.3', platform: 'linux-x64', node }));
    const packaged = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
      '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8', env: environment });
    assert.equal(packaged.status, 0, packaged.stderr);
    const manifestSha256 = JSON.parse(packaged.stdout).manifestSha256;
    const source = readFileSync(join(root, 'tracked.txt'));
    const index = createHash('sha256').update(readFileSync(join(root, '.git/index'))).digest('hex');
    const status = repository.git(['status', '--porcelain=v1']);
    const cacheDigest = fingerprint(join(cache, '_cacache'));
    const outcome = spawnSync(python, [script, 'install', '--repository', root, '--bundle-root', bundle,
      '--manifest-sha256', manifestSha256, '--node-archive', archive, '--offline', '--offline-cache-seed', realpathSync(cache)],
    { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024,
      env: environment });
    assert.equal(outcome.status, 0, `public install failed: ${outcome.stderr}`);
    const first = JSON.parse(outcome.stdout);
    assert.equal(first.state, 'ready');
    const factory = join(root, '.git/factory');
    const originalReceipt = readFileSync(join(factory, 'installed-receipt.json'));
    const owned = JSON.parse(originalReceipt);
    assert.equal(owned.release, '1.2.3');
    assert.equal(owned.targetSchema, 7);
    assert.equal(owned.operationId, first.operationId);
    const baseline = databaseSnapshot(factory);
    assert.deepEqual({ ...baseline.repository }, { state: 'ready', release: '1.2.3' });
    assert.equal(baseline.claims, 0);
    assert.equal(baseline.agentAttempts, 0);
    assert.equal(baseline.sessions, 0);
    assert.equal(baseline.completions.length, 1);
    assert.equal(baseline.completions[0].kind, 'install.completed');
    const originalInstall = directoryIdentity(join(factory, 'install'));
    const originalToolchain = directoryIdentity(join(factory, 'toolchain'));
    assert.ok(!existsSync(join(factory, 'bootstrap-incomplete')));
    assert.ok(!existsSync(join(factory, 'controller-staging', first.operationId)));
    const baselineCli = spawnSync(join(factory, 'install/node/bin/node'), [join(factory, 'install/runtime/dist/cli.js'), '--help'],
      { encoding: 'utf8', timeout: 30000, env: environment });
    assert.equal(baselineCli.status, 0, baselineCli.stderr);
    for (const [arguments_, expected] of [
      [['--version'], 'v24.22.1'],
      [[join(factory, 'install/node/lib/node_modules/npm/bin/npm-cli.js'), '--version'], '11.19.1'],
      [[join(factory, 'toolchain/node_modules/typescript/bin/tsc'), '--version'], 'Version 7.0.2'],
    ]) {
      const tool = spawnSync(join(factory, 'install/node/bin/node'), arguments_,
        { encoding: 'utf8', timeout: 30000, env: environment });
      assert.equal(tool.status, 0, tool.stderr);
      assert.equal(tool.stdout.trim(), expected);
    }
    const targetDescriptor = join(container, 'target-selection.json'), targetBundle = join(container, 'target-bundle');
    writeFileSync(targetDescriptor, JSON.stringify({ version: '1.2.4', platform: 'linux-x64', node }));
    const targetPackage = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', targetDescriptor,
      '--source-root', packageRoot, '--destination', targetBundle], { encoding: 'utf8', env: environment });
    assert.equal(targetPackage.status, 0, targetPackage.stderr);
    const targetSha = JSON.parse(targetPackage.stdout).manifestSha256;
    const emptyCache = join(container, 'empty-cache'); mkdirSync(join(emptyCache, '_cacache'), { recursive: true });
    const failed = spawnSync(python, [script, 'upgrade', '--repository', root, '--bundle-root', targetBundle,
      '--manifest-sha256', targetSha, '--node-archive', archive, '--offline', '--offline-cache-seed', emptyCache],
    { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024,
      env: environment });
    assert.equal(failed.status, 1, 'offline preparation must fail with an empty cache');
    const maintenance = await import('../dist/maintenance.js');
    const pending = await maintenance.inspectMaintenance(root);
    assert.equal(pending.status, 'incomplete');
    assert.equal(pending.intent.phase, 'preparing');
    const inspect = spawnSync(python, [script, 'inspect-upgrade', '--repository', root, '--bundle-root', targetBundle,
      '--manifest-sha256', targetSha, '--node-archive', archive],
    { encoding: 'utf8', timeout: 120000, env: environment });
    assert.equal(inspect.status, 0, inspect.stderr);
    const publicStatus = JSON.parse(inspect.stdout);
    assert.equal(publicStatus.status, 'incomplete');
    assert.equal(publicStatus.intent.operationId, pending.intent.operationId);
    assert.ok(['not_live', 'unknown'].includes(publicStatus.owner.state));
    assert.ok(!existsSync(join(factory, 'upgrade-incomplete')));
    await assert.rejects(maintenance.abandonUpgradePreparation(root, pending.intent.operationId,
      { operatorConfirmed: false, note: 'Unconfirmed.' }), /clearance/);
    writeFileSync(join(factory, 'installed-receipt.json'), Buffer.concat([originalReceipt, Buffer.from(' ')]));
    try {
      await assert.rejects(maintenance.abandonUpgradePreparation(root, pending.intent.operationId,
        { operatorConfirmed: true, note: 'Original receipt was altered.' }), /original|ownership|receipt/i);
    } finally { writeFileSync(join(factory, 'installed-receipt.json'), originalReceipt); }
    const controllerModule = new URL('../dist/maintenance.js', import.meta.url).href;
    const processModule = new URL('../dist/native/process.js', import.meta.url).href;
    const holdProgram = `import {reclaimMaintenance} from ${JSON.stringify(controllerModule)};import {currentOwner} from ${JSON.stringify(processModule)};await reclaimMaintenance(process.argv[1],process.argv[2],currentOwner(),{operatorConfirmed:true,note:'Inspected expired fixture owner.'});process.stdout.write('ready\\n');await new Promise(resolve=>process.stdin.once('data',resolve));`;
    const holder = spawn(process.execPath, ['--input-type=module', '-e', holdProgram, root, pending.intent.operationId],
      { stdio: ['pipe', 'pipe', 'pipe'], env: environment });
    const holderExit = new Promise(resolve => holder.once('close', resolve));
    try {
      const ready = await Promise.race([new Promise(resolve => holder.stdout.once('data', data => resolve(String(data)))),
        holderExit.then(code => { throw new Error(`fixture owner exited before readiness: ${code}`); }),
        new Promise((_, reject) => setTimeout(() => reject(new Error('fixture owner readiness timeout')), 15000))]);
      assert.equal(ready, 'ready\n');
      await assert.rejects(maintenance.abandonUpgradePreparation(root, pending.intent.operationId,
        { operatorConfirmed: true, note: 'Attempted clearance of a positively live owner.' }), /known-live/);
    } finally { holder.stdin.end('release'); assert.equal(await holderExit, 0); }
    const wrongRelease = spawnSync(python, [script, 'abandon-upgrade', '--repository', root, '--bundle-root', bundle,
      '--manifest-sha256', manifestSha256, '--node-archive', archive, '--operation', pending.intent.operationId,
      '--operator-confirmed', '--note', 'Attempted abandonment with the wrong authenticated release.'],
    { encoding: 'utf8', timeout: 120000, env: environment });
    assert.equal(wrongRelease.status, 1);
    assert.equal((await maintenance.inspectMaintenance(root)).status, 'incomplete');
    const abandon = spawnSync(python, [script, 'abandon-upgrade', '--repository', root, '--bundle-root', targetBundle,
      '--manifest-sha256', targetSha, '--node-archive', archive, '--operation', pending.intent.operationId,
      '--operator-confirmed', '--note', 'Inspected the exited disposable preparer and retained its partial evidence.'],
    { encoding: 'utf8', timeout: 120000, env: environment });
    assert.equal(abandon.status, 0, abandon.stderr);
    assert.equal(JSON.parse(abandon.stdout).operationId, pending.intent.operationId);
    assert.equal((await maintenance.inspectMaintenance(root)).status, 'ready');
    assert.ok(existsSync(join(factory, `install-candidate-${pending.intent.operationId}`)));
    assert.ok(existsSync(join(factory, 'maintenance-backups', pending.intent.operationId)));
    assert.deepEqual(readFileSync(join(factory, 'installed-receipt.json')), originalReceipt);
    const upgraded = spawnSync(python, [script, 'upgrade', '--repository', root, '--bundle-root', targetBundle,
      '--manifest-sha256', targetSha, '--node-archive', archive, '--offline', '--offline-cache-seed', realpathSync(cache)],
    { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024,
      env: environment });
    assert.equal(upgraded.status, 0, `public upgrade failed: ${upgraded.stderr}`);
    const result = JSON.parse(upgraded.stdout);
    assert.equal(result.state, 'ready');
    assert.notEqual(result.operationId, first.operationId);
    assert.deepEqual(readFileSync(join(factory, 'installed-receipt.json')), originalReceipt);
    const manifest = JSON.parse(readFileSync(join(factory, 'install/runtime/release-manifest.json'), 'utf8'));
    assert.equal(manifest.version, '1.2.4');
    assert.ok(!existsSync(join(factory, 'upgrade-incomplete')));
    assert.ok(!existsSync(join(factory, 'controller-staging', result.operationId)));
    assert.equal(directoryIdentity(join(factory, `upgrade-${result.operationId}`, 'old/install')), originalInstall);
    assert.equal(directoryIdentity(join(factory, `upgrade-${result.operationId}`, 'old/toolchain')), originalToolchain);
    const afterUpgrade = databaseSnapshot(factory);
    assert.deepEqual({ ...afterUpgrade.repository }, { state: 'ready', release: '1.2.4' });
    assert.equal(afterUpgrade.claims, 0);
    assert.deepEqual(afterUpgrade.completions.slice(0, 1), baseline.completions);
    assert.equal(afterUpgrade.completions.length, 2);
    assert.equal(afterUpgrade.completions[1].kind, 'upgrade.completed');
    assert.equal(JSON.parse(afterUpgrade.completions[1].data).operationId, result.operationId);
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
      { encoding: 'utf8', timeout: 30000, env: environment });
    assert.equal(cli.status, 0, cli.stderr);
    assert.deepEqual(readFileSync(join(authoring, 'package.json')), customPackage);
    assert.deepEqual(readFileSync(join(authoring, 'agents.json')), customAgents);
    assert.deepEqual(readFileSync(join(root, 'tracked.txt')), source);
    assert.equal(createHash('sha256').update(readFileSync(join(root, '.git/index'))).digest('hex'), index);
    assert.equal(fingerprint(join(cache, '_cacache')), cacheDigest);

    const nextDescriptor = join(container, 'next-selection.json'), nextBundle = join(container, 'next-bundle');
    writeFileSync(nextDescriptor, JSON.stringify({ version: '1.2.5', platform: 'linux-x64', node }));
    const nextPackage = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', nextDescriptor,
      '--source-root', packageRoot, '--destination', nextBundle], { encoding: 'utf8', env: environment });
    assert.equal(nextPackage.status, 0, nextPackage.stderr);
    const nextSha = JSON.parse(nextPackage.stdout).manifestSha256;
    const receiptBytes = new Map();
    async function interruptAtReceipt(command, receiptName, expectedId) {
      const child = spawn(python, command, { stdio: ['ignore', 'pipe', 'pipe'], env: environment });
      let output = '';
      child.stdout.on('data', data => { output = (output + String(data)).slice(0, 8192); });
      child.stderr.on('data', data => { output = (output + String(data)).slice(0, 8192); });
      const exited = new Promise(resolve => child.once('close', resolve));
      const launcher = await launcherIdentity(child);
      const until = Date.now() + 180000;
      let operationId, controller;
      while (Date.now() < until && child.exitCode === null) {
        const markerPath = join(factory, 'upgrade-incomplete');
        if (existsSync(markerPath)) {
          const candidateId = JSON.parse(readFileSync(markerPath, 'utf8')).operationId;
          const step = join(factory, `upgrade-${candidateId}`, `${receiptName}.json`);
          if ((!expectedId || candidateId === expectedId) && existsSync(step)) {
            const expected = join(factory, 'controller-staging', candidateId, 'payload/node');
            controller = stagedController(launcher, expected);
            if (controller) { operationId = candidateId; break; }
          }
        }
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      if (!controller || !operationId) {
        await exited;
        assert.fail(`failed to observe owned staged controller at ${receiptName}: ${output}`);
      }
      let stopped = true, launcherStopped = false;
      try {
        await stopOwned(controller);
        await closeHelpers(controller);
        const receipts = ['01-old-install', '02-new-install', '03-old-toolchain', '04-new-toolchain'];
        const currentIndex = receipts.indexOf(receiptName), operationRoot = join(factory, `upgrade-${operationId}`);
        for (const previous of receipts.slice(0, currentIndex + 1)) {
          const bytes = readFileSync(join(operationRoot, `${previous}.json`));
          if (receiptBytes.has(previous)) assert.deepEqual(bytes, receiptBytes.get(previous), 'earlier receipt changed during resume');
          else receiptBytes.set(previous, bytes);
          const record = JSON.parse(bytes);
          assert.equal(record.operationId, operationId);
          assert.equal(record.step, previous);
        }
        for (const later of receipts.slice(receipts.indexOf(receiptName) + 1))
          assert.ok(!existsSync(join(factory, `upgrade-${operationId}`, `${later}.json`)),
            `controller passed the selected ${receiptName} boundary`);
        if (receiptName === '01-old-install') { launcherStopped = true; await stopOwned(launcher); }
        signalOwned(controller, 'SIGKILL'); stopped = false;
        if (launcherStopped) {
          const blocked = spawnSync(python, [script, 'resume-upgrade', '--repository', root, '--bundle-root', nextBundle,
            '--manifest-sha256', nextSha, '--node-archive', archive, '--operation', operationId,
            '--operator-confirmed', '--note', 'Attempted recovery while the original launcher was live.'],
          { encoding: 'utf8', timeout: 120000, env: environment });
          assert.equal(blocked.status, 1, 'a live original launcher must block recovery');
          assert.ok(existsSync(join(factory, 'upgrade-incomplete')));
          signalOwned(launcher, 'SIGCONT'); launcherStopped = false;
        }
        assert.notEqual(await exited, 0, 'interrupted controller must not report success');
      } finally {
        if (launcherStopped) signalOwned(launcher, 'SIGCONT');
        if (stopped) signalOwned(controller, 'SIGCONT');
        if (launcherStopped || stopped) await exited;
      }
      const status = await maintenance.inspectMaintenance(root);
      assert.equal(status.status, 'incomplete');
      assert.equal(status.intent.operationId, operationId);
      const interrupted = databaseSnapshot(factory);
      assert.deepEqual({ ...interrupted.repository }, { state: 'incomplete', release: '1.2.4' });
      assert.equal(interrupted.claims, 1);
      assert.deepEqual(interrupted.completions, afterUpgrade.completions);
      assert.ok(existsSync(join(factory, 'maintenance-backups', operationId)));
      return operationId;
    }
    const targetArgs = ['--repository', root, '--bundle-root', nextBundle, '--manifest-sha256', nextSha, '--node-archive', archive];
    const interruptedId = await interruptAtReceipt([script, 'upgrade', ...targetArgs, '--offline', '--offline-cache-seed', cache], '01-old-install');
    for (const receiptName of ['02-new-install', '03-old-toolchain', '04-new-toolchain']) {
      const operation = await interruptAtReceipt([script, 'resume-upgrade', ...targetArgs, '--operation', interruptedId,
        '--operator-confirmed', '--note', 'Inspected the terminated disposable staged controller and helper closure.'], receiptName, interruptedId);
      assert.equal(operation, interruptedId);
    }
    const finalArgs = [script, 'resume-upgrade', ...targetArgs, '--operation', interruptedId,
      '--operator-confirmed', '--note', 'Inspected the terminated disposable staged controller and helper closure.'];
    const finalAttempt = spawn(python, finalArgs, { stdio: ['ignore', 'pipe', 'pipe'], env: environment });
    let finalOutput = '';
    finalAttempt.stdout.on('data', data => { finalOutput = (finalOutput + String(data)).slice(0, 8192); });
    finalAttempt.stderr.on('data', data => { finalOutput = (finalOutput + String(data)).slice(0, 8192); });
    const finalExit = new Promise(resolve => finalAttempt.once('close', resolve));
    const finalLauncher = await launcherIdentity(finalAttempt);
    try {
      const readyDeadline = Date.now() + 180000;
      let readyController;
      while (Date.now() < readyDeadline && finalAttempt.exitCode === null) {
        const markerPath = join(factory, 'upgrade-incomplete');
        if (existsSync(markerPath)) {
          let live, ready = false;
          try {
            live = new DatabaseSync(join(factory, 'history.sqlite'), { readOnly: true, timeout: 100 });
            ready = live.prepare('SELECT state FROM repository').get().state === 'ready';
          } catch (error) {
            if (error?.errcode !== 5 && error?.errcode !== 6) throw error;
          } finally { live?.close(); }
          if (ready) {
            const expected = join(factory, 'controller-staging', interruptedId, 'payload/node');
            readyController = stagedController(finalLauncher, expected);
            if (readyController) break;
          }
        }
        await new Promise(resolve => setTimeout(resolve, 25));
      }
      if (!readyController) { await finalExit; assert.fail(`failed to observe ready-before-marker controller: ${finalOutput}`); }
      let readyStopped = true, completingLauncherStopped = false;
      try {
        await stopOwned(readyController);
        await closeHelpers(readyController);
        const committed = databaseSnapshot(factory);
        assert.deepEqual({ ...committed.repository }, { state: 'ready', release: '1.2.5' });
        assert.equal(committed.claims, 0);
        assert.equal(committed.completions.length, 3);
        assert.equal(JSON.parse(committed.completions[2].data).operationId, interruptedId);
        const blocked = spawnSync(python, finalArgs, { encoding: 'utf8', timeout: 120000, env: environment });
        assert.equal(blocked.status, 1, 'a live completed controller must block marker recovery');
        assert.ok(existsSync(join(factory, 'upgrade-incomplete')));
        completingLauncherStopped = true; await stopOwned(finalLauncher);
        signalOwned(readyController, 'SIGKILL'); readyStopped = false;
        const launcherBlocked = spawnSync(python, finalArgs, { encoding: 'utf8', timeout: 120000, env: environment });
        assert.equal(launcherBlocked.status, 1, 'a live completing launcher must block marker recovery');
        assert.ok(existsSync(join(factory, 'upgrade-incomplete')));
        assert.deepEqual(databaseSnapshot(factory), committed, 'refused recovery must preserve committed ownership');
        signalOwned(finalLauncher, 'SIGCONT'); completingLauncherStopped = false;
        assert.notEqual(await finalExit, 0, 'interrupted ready controller must not report success');
      } finally {
        if (completingLauncherStopped) signalOwned(finalLauncher, 'SIGCONT');
        if (readyStopped) { signalOwned(readyController, 'SIGCONT'); await finalExit; }
      }
      const resumed = spawnSync(python, finalArgs, { encoding: 'utf8', timeout: 600000, maxBuffer: 2 * 1024 * 1024,
        env: environment });
      assert.equal(resumed.status, 0, `explicit committed upgrade recovery failed: ${resumed.stderr}`);
      assert.equal(JSON.parse(resumed.stdout).operationId, interruptedId);
    } finally { if (finalAttempt.exitCode === null) await finalExit; }
    assert.equal((await maintenance.inspectMaintenance(root)).status, 'ready');
    assert.equal(JSON.parse(readFileSync(join(factory, 'install/runtime/release-manifest.json'), 'utf8')).version, '1.2.5');
    assert.deepEqual(readFileSync(join(factory, 'installed-receipt.json')), originalReceipt);
    assert.ok(!existsSync(join(factory, 'upgrade-incomplete')));
    assert.ok(!existsSync(join(factory, 'controller-staging', interruptedId)));
    const recovered = databaseSnapshot(factory);
    assert.deepEqual({ ...recovered.repository }, { state: 'ready', release: '1.2.5' });
    assert.equal(recovered.claims, 0);
    assert.equal(recovered.agentAttempts, 0);
    assert.equal(recovered.sessions, 0);
    assert.deepEqual(recovered.completions.slice(0, 2), afterUpgrade.completions);
    assert.equal(recovered.completions.length, 3, 'recovery must not append a duplicate completion');
    for (const [receipt, bytes] of receiptBytes)
      assert.deepEqual(readFileSync(join(factory, `upgrade-${interruptedId}`, `${receipt}.json`)), bytes);
    const finalCli = spawnSync(join(factory, 'install/node/bin/node'), [join(factory, 'install/runtime/dist/cli.js'), '--help'],
      { encoding: 'utf8', timeout: 30000, env: environment });
    assert.equal(finalCli.status, 0, finalCli.stderr);
    assert.deepEqual(readFileSync(join(authoring, 'package.json')), customPackage);
    assert.deepEqual(readFileSync(join(authoring, 'agents.json')), customAgents);
    assert.deepEqual(readFileSync(join(root, 'tracked.txt')), source);
    assert.equal(hashFile(join(root, '.git/index')), index);
    assert.equal(fingerprint(join(cache, '_cacache')), cacheDigest);
    assert.deepEqual(repository.git(['status', '--porcelain=v1']).split('\n').filter(Boolean).sort(),
      status.split('\n').filter(Boolean).sort());
  } finally { repository.dispose(); rmSync(container, { recursive: true, force: true }); }
});

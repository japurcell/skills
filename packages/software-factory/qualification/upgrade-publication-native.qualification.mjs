import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
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
    const emptyCache = join(container, 'empty-cache'); mkdirSync(join(emptyCache, '_cacache'), { recursive: true });
    const failed = spawnSync(python, [script, 'upgrade', '--repository', root, '--bundle-root', targetBundle,
      '--manifest-sha256', targetSha, '--node-archive', archive, '--offline', '--offline-cache-seed', emptyCache],
    { encoding: 'utf8', timeout: 600_000, maxBuffer: 2 * 1024 * 1024,
      env: { ...process.env, TMPDIR: container, TMP: container, TEMP: container } });
    assert.equal(failed.status, 1, 'offline preparation must fail with an empty cache');
    const maintenance = await import('../dist/maintenance.js');
    const pending = await maintenance.inspectMaintenance(root);
    assert.equal(pending.status, 'incomplete');
    assert.equal(pending.intent.phase, 'preparing');
    const inspect = spawnSync(python, [script, 'inspect-upgrade', '--repository', root, '--bundle-root', targetBundle,
      '--manifest-sha256', targetSha, '--node-archive', archive],
    { encoding: 'utf8', timeout: 120000, env: { ...process.env, TMPDIR: container, TMP: container, TEMP: container } });
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
      { stdio: ['pipe', 'pipe', 'pipe'] });
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
    { encoding: 'utf8', timeout: 120000, env: { ...process.env, TMPDIR: container, TMP: container, TEMP: container } });
    assert.equal(wrongRelease.status, 1);
    assert.equal((await maintenance.inspectMaintenance(root)).status, 'incomplete');
    const abandon = spawnSync(python, [script, 'abandon-upgrade', '--repository', root, '--bundle-root', targetBundle,
      '--manifest-sha256', targetSha, '--node-archive', archive, '--operation', pending.intent.operationId,
      '--operator-confirmed', '--note', 'Inspected the exited disposable preparer and retained its partial evidence.'],
    { encoding: 'utf8', timeout: 120000, env: { ...process.env, TMPDIR: container, TMP: container, TEMP: container } });
    assert.equal(abandon.status, 0, abandon.stderr);
    assert.equal(JSON.parse(abandon.stdout).operationId, pending.intent.operationId);
    assert.equal((await maintenance.inspectMaintenance(root)).status, 'ready');
    assert.ok(existsSync(join(factory, `install-candidate-${pending.intent.operationId}`)));
    assert.ok(existsSync(join(factory, 'maintenance-backups', pending.intent.operationId)));
    assert.deepEqual(readFileSync(join(factory, 'installed-receipt.json')), originalReceipt);
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

    const nextDescriptor = join(container, 'next-selection.json'), nextBundle = join(container, 'next-bundle');
    writeFileSync(nextDescriptor, JSON.stringify({ version: '1.2.5', platform: 'darwin-arm64', node }));
    const nextPackage = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', nextDescriptor,
      '--source-root', packageRoot, '--destination', nextBundle], { encoding: 'utf8' });
    assert.equal(nextPackage.status, 0, nextPackage.stderr);
    const nextSha = JSON.parse(nextPackage.stdout).manifestSha256;
    const environment = { ...process.env, TMPDIR: container, TMP: container, TEMP: container };
    async function interruptAtReceipt(command, receiptName, expectedId) {
      const child = spawn(python, command, { stdio: ['ignore', 'pipe', 'pipe'], env: environment });
      let output = '';
      child.stdout.on('data', data => { output += String(data).slice(0, 4096); });
      child.stderr.on('data', data => { output += String(data).slice(0, 4096); });
      const exited = new Promise(resolve => child.once('close', resolve));
      const until = Date.now() + 180000;
      let operationId, stagePid;
      while (Date.now() < until && child.exitCode === null) {
        const markerPath = join(factory, 'upgrade-incomplete');
        if (existsSync(markerPath)) {
          const candidateId = JSON.parse(readFileSync(markerPath, 'utf8')).operationId;
          const step = join(factory, `upgrade-${candidateId}`, `${receiptName}.json`);
          if ((!expectedId || candidateId === expectedId) && existsSync(step)) {
            const expected = join(factory, 'controller-staging', candidateId, 'payload/node');
            const ps = spawnSync('/bin/ps', ['-ww', '-axo', 'pid=,ppid=,comm='], { encoding: 'utf8' });
            assert.equal(ps.status, 0, ps.stderr);
            for (const line of ps.stdout.split('\n')) {
              const row = /^\s*(\d+)\s+(\d+)\s+(.+)$/.exec(line);
              if (row && Number(row[2]) === child.pid && row[3] === expected) {
                stagePid = Number(row[1]); operationId = candidateId; break;
              }
            }
            if (stagePid) break;
          }
        }
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      if (!stagePid || !operationId) {
        await exited;
        assert.fail(`failed to observe owned staged controller at ${receiptName}: ${output}`);
      }
      process.kill(stagePid, 'SIGSTOP');
      let stopped = true, launcherStopped = false;
      try {
        const deadline = Date.now() + 15000;
        for (;;) {
          const ps = spawnSync('/bin/ps', ['-axo', 'pid=,ppid='], { encoding: 'utf8' });
          assert.equal(ps.status, 0, ps.stderr);
          const children = ps.stdout.split('\n').map(line => /^\s*(\d+)\s+(\d+)/.exec(line))
            .filter(row => row && Number(row[2]) === stagePid);
          if (!children.length) break;
          assert.ok(Date.now() < deadline, 'owned publication helper did not close');
          await new Promise(resolve => setTimeout(resolve, 50));
        }
        if (receiptName === '01-old-install') { process.kill(child.pid, 'SIGSTOP'); launcherStopped = true; }
        process.kill(stagePid, 'SIGKILL'); stopped = false;
        if (launcherStopped) {
          const blocked = spawnSync(python, [script, 'resume-upgrade', '--repository', root, '--bundle-root', nextBundle,
            '--manifest-sha256', nextSha, '--node-archive', archive, '--operation', operationId,
            '--operator-confirmed', '--note', 'Attempted recovery while the original launcher was live.'],
          { encoding: 'utf8', timeout: 120000, env: environment });
          assert.equal(blocked.status, 1, 'a live original launcher must block recovery');
          assert.ok(existsSync(join(factory, 'upgrade-incomplete')));
          process.kill(child.pid, 'SIGCONT'); launcherStopped = false;
        }
        assert.notEqual(await exited, 0, 'interrupted controller must not report success');
      } finally {
        if (launcherStopped) process.kill(child.pid, 'SIGCONT');
        if (stopped) process.kill(stagePid, 'SIGCONT');
        if (launcherStopped || stopped) await exited;
      }
      const status = await maintenance.inspectMaintenance(root);
      assert.equal(status.status, 'incomplete');
      assert.equal(status.intent.operationId, operationId);
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
    finalAttempt.stdout.on('data', data => { finalOutput += String(data).slice(0, 4096); });
    finalAttempt.stderr.on('data', data => { finalOutput += String(data).slice(0, 4096); });
    const finalExit = new Promise(resolve => finalAttempt.once('close', resolve));
    try {
    const readyDeadline = Date.now() + 180000;
    let readyStagePid;
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
          const ps = spawnSync('/bin/ps', ['-ww', '-axo', 'pid=,ppid=,comm='], { encoding: 'utf8' });
          assert.equal(ps.status, 0, ps.stderr);
          for (const line of ps.stdout.split('\n')) {
            const row = /^\s*(\d+)\s+(\d+)\s+(.+)$/.exec(line);
            if (row && Number(row[2]) === finalAttempt.pid && row[3] === expected) { readyStagePid = Number(row[1]); break; }
          }
          if (readyStagePid) break;
        }
      }
      await new Promise(resolve => setTimeout(resolve, 25));
    }
    if (!readyStagePid) { await finalExit; assert.fail(`failed to observe ready-before-marker controller: ${finalOutput}`); }
    process.kill(readyStagePid, 'SIGSTOP');
    let readyStopped = true;
    try {
      const helperDeadline = Date.now() + 15000;
      for (;;) {
        const ps = spawnSync('/bin/ps', ['-axo', 'pid=,ppid='], { encoding: 'utf8' });
        assert.equal(ps.status, 0, ps.stderr);
        const children = ps.stdout.split('\n').map(line => /^\s*(\d+)\s+(\d+)/.exec(line))
          .filter(row => row && Number(row[2]) === readyStagePid);
        if (!children.length) break;
        assert.ok(Date.now() < helperDeadline, 'owned validation child did not close');
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      const blocked = spawnSync(python, finalArgs, { encoding: 'utf8', timeout: 120000, env: environment });
      assert.equal(blocked.status, 1, 'a live completed controller must block marker recovery');
      assert.ok(existsSync(join(factory, 'upgrade-incomplete')));
      process.kill(readyStagePid, 'SIGKILL'); readyStopped = false;
      assert.notEqual(await finalExit, 0, 'interrupted ready controller must not report success');
    } finally {
      if (readyStopped) { process.kill(readyStagePid, 'SIGCONT'); await finalExit; }
    }
    const resumed = spawnSync(python, finalArgs, { encoding: 'utf8', timeout: 600000, maxBuffer: 2 * 1024 * 1024,
      env: environment });
    assert.equal(resumed.status, 0, `explicit committed upgrade recovery failed: ${resumed.stderr}`);
    assert.equal(JSON.parse(resumed.stdout).operationId, interruptedId);
    } finally { if (finalAttempt.exitCode === null) await finalExit; }
    assert.equal((await maintenance.inspectMaintenance(root)).status, 'ready');
    assert.equal(JSON.parse(readFileSync(join(factory, 'install/runtime/release-manifest.json'), 'utf8')).version, '1.2.5');
    assert.deepEqual(readFileSync(join(factory, 'installed-receipt.json')), originalReceipt);
  } finally { repository.dispose(); rmSync(container, { recursive: true, force: true }); }
});

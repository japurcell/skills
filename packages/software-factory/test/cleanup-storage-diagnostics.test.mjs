import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

// This fixed grammar is the entire diagnostic export. Permission bits are not ACL authority.
const recordPattern = /^cleanup-sidecar-v1 role=(wal|shm|journal) regular=(true|false) symbolicLink=(true|false) singleLink=(true|false) groupOtherBitsClear=(true|false)$(?![\s\S])/;
const fixtureProgram = String.raw`
  import assert from 'node:assert/strict';
  import childProcess from 'node:child_process';
  import fs from 'node:fs';
  import { join } from 'node:path';
  import { syncBuiltinESMExports } from 'node:module';
  import { createRepository } from ${JSON.stringify(new URL('./fixtures/repository.mjs', import.meta.url).href)};
  import { initializeRepositoryStore, openCleanupReadStore } from ${JSON.stringify(new URL('../dist/store.js', import.meta.url).href)};

  function observe(database) {
    const original = fs.lstatSync;
    let first;
    fs.lstatSync = (path, options) => {
      const stats = original(path, options);
      const role = ['wal', 'shm', 'journal'].find(role => path === database + '-' + role);
      if (first === undefined && role !== undefined && options?.bigint === true) {
        // All facts come from the very object returned to the production guard.
        const regular = stats.isFile();
        const symbolicLink = stats.isSymbolicLink();
        const singleLink = stats.nlink === 1n;
        const groupOtherBitsClear = (stats.mode & 0o077n) === 0n;
        if (!regular || symbolicLink || !singleLink || !groupOtherBitsClear)
          first = 'cleanup-sidecar-v1 role=' + role + ' regular=' + regular
            + ' symbolicLink=' + symbolicLink + ' singleLink=' + singleLink
            + ' groupOtherBitsClear=' + groupOtherBitsClear;
      }
      return stats;
    };
    syncBuiltinESMExports();
    return () => {
      fs.lstatSync = original;
      syncBuiltinESMExports();
      return first;
    };
  }

  const repository = createRepository();
  const common = fs.realpathSync(join(repository.path, '.git'));
  const database = join(common, 'factory/history.sqlite');
  let store;
  try {
    store = await initializeRepositoryStore(common, { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id,
      owner: { host: 'fixture', pid: process.pid, start: 'cleanup-storage-diagnostics' } });
    await store.activateInvocation(invocation.id);
    const input = await store.createCapture({ invocationId: invocation.id, channel: 'context' });
    await store.appendCapture({ id: input.id, chunks: [{ sequence: 1, text: 'saved input 🌍' }], state: 'complete' });
    await store.saveInvocationMetadata(invocation.id, { settings: {}, workflow: 'workflow.ts', selectedCommit: null,
      inputCaptureId: input.id, question: null, contexts: [] });
    FIXTURE_ACTION
  } finally { store?.close(); repository.dispose(); }
`;

function run(action) {
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_SELECTOR_TIMING_ROOT;
  const child = spawnSync(process.execPath, ['--input-type=module', '-e', fixtureProgram.replace('FIXTURE_ACTION', action)], {
    encoding: 'utf8', timeout: 10_000, maxBuffer: 8192, env,
  });
  assert.ok(!child.error, 'diagnostic child did not complete within its bound');
  assert.equal(child.signal, null, 'diagnostic child was interrupted');
  // Retain no child error text: even an unexpected fixture failure may name paths.
  const failure = child.stderr.includes('ERR_MODULE_NOT_FOUND') ? 'module-unavailable'
    : child.stderr.includes('PRIVATE_DIAGNOSTIC_CANARY') ? 'forbidden-stat-field'
    : child.stderr.includes('undefined') ? 'missing-observation'
    : child.stderr.includes('AssertionError') ? 'assertion' : 'other';
  const lines = child.stdout === '' ? [] : child.stdout.slice(0, -1).split('\n');
  assert.ok(child.stdout === '' || child.stdout.endsWith('\n'), 'diagnostic export omitted its record terminator');
  assert.ok(lines.length <= 1 && lines.every(line => recordPattern.test(line)), 'diagnostic export violated the closed grammar');
  return { status: child.status, lines, failure };
}

test('cleanup sidecar diagnostic grammar rejects extra, path-bearing and arbitrary fields', () => {
  const valid = 'cleanup-sidecar-v1 role=wal regular=true symbolicLink=false singleLink=true groupOtherBitsClear=false';
  assert.match(valid, recordPattern);
  for (const invalid of [valid + ' path=/private/canary', valid + ' uid=501', valid + ' mode=438',
    valid.replace('wal', '/private/canary'), valid.replace('false', 'canary'), valid + '\ncanary', valid + '\n', valid + ' ',
    valid.replace('v1', 'v2'), valid + ' SID=canary', valid + ' env=canary']) assert.doesNotMatch(invalid, recordPattern);
});

test('cleanup sidecar observation preserves each original refusal and exports only the same four predicates', () => {
  const result = run(String.raw`
    const realLstat = fs.lstatSync;
    const realSpawn = childProcess.spawnSync;
    const base = realLstat(database + '-wal', { bigint: true });
    const canary = 'PRIVATE_DIAGNOSTIC_CANARY';
    let placementCalls = 0;
    // Synthetic predicate contracts replace only the existing Windows placement
    // child boundary. The separate native positive case retains actual placement.
    if (process.platform === 'win32') childProcess.spawnSync = (command, args, options) => {
      placementCalls++;
      assert.equal(command, join(process.env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'));
      assert.equal(args.length, 5);
      assert.deepEqual(args.slice(0, 4), ['-NoLogo', '-NoProfile', '-NonInteractive', '-Command']);
      assert.equal(typeof args[4], 'string');
      assert.ok(args[4].length > 0);
      assert.deepEqual(options, { encoding: 'utf8', timeout: 10_000, maxBuffer: 8192, windowsHide: true,
        env: { ...process.env, FACTORY_PLACEMENT_PATH: join(common, 'factory') } });
      return { status: 0, signal: null, stdout: '{"driveType":3,"filesystem":"NTFS"}' };
    };
    syncBuiltinESMExports();
    try {
    for (const role of ['wal', 'shm', 'journal']) {
      for (const failed of ['regular', 'symbolicLink', 'singleLink', 'groupOtherBitsClear', 'all']) {
        let observations = 0;
        const target = database + '-' + role;
        const selected = {
          isFile() { assert.equal(this, selected); return failed !== 'regular' && failed !== 'all'; },
          isSymbolicLink() { assert.equal(this, selected); return failed === 'symbolicLink' || failed === 'all'; },
          nlink: failed === 'singleLink' || failed === 'all' ? 2n : 1n,
          mode: failed === 'groupOtherBitsClear' || failed === 'all' ? 0o644n : 0o600n,
          get uid() { throw new Error(canary); }, get ino() { throw new Error(canary); },
          get dev() { throw new Error(canary); }, get size() { throw new Error(canary); },
          get SID() { throw new Error(canary); }, toJSON() { throw new Error(canary); },
        };
        const safe = new Proxy(base, { get(object, key) {
          if (key === 'isFile') return () => true;
          if (key === 'isSymbolicLink') return () => false;
          if (key === 'nlink') return 1n;
          if (key === 'mode') return 0o600n;
          return Reflect.get(object, key);
        } });
        fs.lstatSync = (path, options) => {
          if (['-wal', '-shm', '-journal'].some(suffix => path === database + suffix)) {
            if (path === target && options?.bigint) { observations++; return selected; }
            return path === target ? selected : safe;
          }
          return realLstat(path, options);
        };
        syncBuiltinESMExports();
        const finish = observe(database);
        assert.throws(() => openCleanupReadStore(common), { message: 'forward store sidecar is not private regular storage' });
        const record = finish();
        assert.equal(observations, 1);
        assert.equal(record, 'cleanup-sidecar-v1 role=' + role
          + ' regular=' + (failed !== 'regular' && failed !== 'all')
          + ' symbolicLink=' + (failed === 'symbolicLink' || failed === 'all')
          + ' singleLink=' + (failed !== 'singleLink' && failed !== 'all')
          + ' groupOtherBitsClear=' + (failed !== 'groupOtherBitsClear' && failed !== 'all'));
        assert.ok(!record.includes(canary));
        fs.lstatSync = realLstat;
        syncBuiltinESMExports();
      }
    }
    assert.equal(placementCalls, process.platform === 'win32' ? 15 : 0);
    } finally {
      fs.lstatSync = realLstat;
      childProcess.spawnSync = realSpawn;
      syncBuiltinESMExports();
    }
  `);
  assert.equal(result.status, 0, 'controlled predicate observation failed: ' + result.failure);
  assert.deepEqual(result.lines, []);
});

test('cleanup native read-only admission reports a bounded sidecar tuple while retaining its positive expectation', t => {
  const result = run(String.raw`
    const before = [fs.readFileSync(database), fs.readFileSync(database + '-wal')];
    const finish = observe(database);
    let reader;
    try {
      reader = openCleanupReadStore(common);
      const snapshot = reader.readCleanupSnapshot();
      assert.equal(snapshot.recovery.authority, 'unassessed');
      assert.deepEqual([fs.readFileSync(database), fs.readFileSync(database + '-wal')], before);
      const later = await store.createCapture({ invocationId: invocation.id, channel: 'stdout' });
      await store.saveInvocationMetadata(invocation.id, { futureReference: later.id });
      const committed = [fs.readFileSync(database), fs.readFileSync(database + '-wal')];
      assert.deepEqual(reader.readCleanupSnapshot(), snapshot);
      assert.equal(reader.pageCleanupCaptureHeaders().records.length, 1);
      assert.deepEqual([fs.readFileSync(database), fs.readFileSync(database + '-wal')], committed);
    } catch {
      process.exitCode = 1;
    } finally {
      reader?.close();
      const record = finish();
      if (record !== undefined) process.stdout.write(record + '\n');
    }
  `);
  for (const record of result.lines) t.diagnostic(record);
  assert.equal(result.status, 0, 'native cleanup read-only admission did not satisfy the positive snapshot contract');
  assert.deepEqual(result.lines, []);
});

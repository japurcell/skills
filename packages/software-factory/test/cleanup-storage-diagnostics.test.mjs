import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

// Only these fixed grammars may be exported. Permission bits are not ACL authority.
const recordPattern = /^cleanup-sidecar-v1 role=(wal|shm|journal) regular=(true|false) symbolicLink=(true|false) singleLink=(true|false) groupOtherBitsClear=(true|false)$(?![\s\S])/;
const failurePattern = /^cleanup-fixture-v1 stage=(repository|initialize|seed|action|base|placement-command|placement-flags|placement-options|admission|observation|count|restore|cleanup|other) role=(none|wal|shm|journal|other) vector=(none|regular|symbolicLink|singleLink|groupOtherBitsClear|all|other) code=(assertion|stat-canary|ENOENT|EACCES|EPERM|other)$(?![\s\S])/;
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

  let diagnosticStage = 'repository', diagnosticRole = 'none', diagnosticVector = 'none';
  FIXTURE_BEGIN
  const repository = createRepository();
  const common = fs.realpathSync(join(repository.path, '.git'));
  const database = join(common, 'factory/history.sqlite');
  let store;
  try {
    diagnosticStage = 'initialize';
    store = await initializeRepositoryStore(common, { release: 'fixture' });
    diagnosticStage = 'seed';
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id,
      owner: { host: 'fixture', pid: process.pid, start: 'cleanup-storage-diagnostics' } });
    await store.activateInvocation(invocation.id);
    const input = await store.createCapture({ invocationId: invocation.id, channel: 'context' });
    await store.appendCapture({ id: input.id, chunks: [{ sequence: 1, text: 'saved input 🌍' }], state: 'complete' });
    await store.saveInvocationMetadata(invocation.id, { settings: {}, workflow: 'workflow.ts', selectedCommit: null,
      inputCaptureId: input.id, question: null, contexts: [] });
    diagnosticStage = 'action';
    FIXTURE_ACTION
  } FIXTURE_BODY_CATCH finally { diagnosticStage = 'cleanup'; store?.close(); repository.dispose(); }
  FIXTURE_END
`;

const boundedFailureReporter = String.raw`
  let failureReported = false;
  function reportFixtureFailure(error) {
    if (failureReported) return;
    failureReported = true;
    const stage = ['repository', 'initialize', 'seed', 'action', 'base', 'placement-command', 'placement-flags',
      'placement-options', 'admission', 'observation', 'count', 'restore', 'cleanup'].includes(diagnosticStage) ? diagnosticStage : 'other';
    const role = ['none', 'wal', 'shm', 'journal'].includes(diagnosticRole) ? diagnosticRole : 'other';
    const vector = ['none', 'regular', 'symbolicLink', 'singleLink', 'groupOtherBitsClear', 'all'].includes(diagnosticVector) ? diagnosticVector : 'other';
    const code = error?.code === 'ERR_ASSERTION' ? 'assertion'
      : error?.message === 'PRIVATE_DIAGNOSTIC_CANARY' ? 'stat-canary'
      : ['ENOENT', 'EACCES', 'EPERM'].includes(error?.code) ? error.code : 'other';
    fs.writeSync(2, 'cleanup-fixture-v1 stage=' + stage + ' role=' + role + ' vector=' + vector + ' code=' + code + '\n');
  }
  try {
`;

function runProgram(program) {
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_SELECTOR_TIMING_ROOT;
  const child = spawnSync(process.execPath, ['--input-type=module', '-e', program], {
    encoding: 'utf8', timeout: 10_000, maxBuffer: 8192, env,
  });
  if (child.error || child.signal !== null) {
    // Child output and Error text can contain private paths or environment values.
    const code = child.error?.code;
    const error = !child.error ? 'none'
      : ['ETIMEDOUT', 'ENOBUFS', 'E2BIG', 'ENOENT', 'EACCES', 'EPERM', 'EAGAIN', 'ENOMEM', 'EMFILE', 'ENFILE'].includes(code) ? code : 'other';
    const status = child.status === null ? 'none' : child.status === 0 ? 'zero'
      : Number.isInteger(child.status) ? 'nonzero' : 'other';
    const signal = child.signal === null ? 'none'
      : ['SIGTERM', 'SIGKILL', 'SIGINT', 'SIGBREAK', 'SIGABRT'].includes(child.signal) ? child.signal : 'other';
    assert.fail('diagnostic child failed (error=' + error + '; status=' + status + '; signal=' + signal + ')');
  }
  // Retain no child error text: even an unexpected fixture failure may name paths.
  const records = child.stderr.split('\n').filter(line => failurePattern.test(line));
  const failure = records.length === 1 ? records[0] : child.stderr.includes('ERR_MODULE_NOT_FOUND') ? 'module-unavailable'
    : child.stderr.includes('PRIVATE_DIAGNOSTIC_CANARY') ? 'forbidden-stat-field'
    : child.stderr.includes('undefined') ? 'missing-observation'
    : child.stderr.includes('AssertionError') ? 'assertion' : 'other';
  const lines = child.stdout === '' ? [] : child.stdout.slice(0, -1).split('\n');
  assert.ok(child.stdout === '' || child.stdout.endsWith('\n'), 'diagnostic export omitted its record terminator');
  assert.ok(lines.length <= 1 && lines.every(line => recordPattern.test(line)), 'diagnostic export violated the closed grammar');
  return { status: child.status, lines, failure };
}

function run(action, diagnose = false) {
  return runProgram(fixtureProgram.replace('FIXTURE_ACTION', action)
    .replace('FIXTURE_BEGIN', diagnose ? boundedFailureReporter : '')
    .replace('FIXTURE_BODY_CATCH', diagnose ? 'catch (error) { reportFixtureFailure(error); throw error; }' : '')
    .replace('FIXTURE_END', diagnose ? '} catch (error) { reportFixtureFailure(error); process.exitCode = 1; }' : ''));
}

test('cleanup diagnostic child buffer refusal exports only closed process facts', () => {
  assert.throws(() => runProgram(String.raw`
    process.stderr.write('PRIVATE_DIAGNOSTIC_CANARY /private/canary S-1-canary '.repeat(8192));
  `), { message: /^diagnostic child failed \(error=ENOBUFS; status=(none|zero|nonzero|other); signal=(none|SIGTERM|SIGKILL|SIGINT|SIGBREAK|SIGABRT|other)\)$/ });
});

test('cleanup synthetic fixture preserves a large assertion failure as one closed nonzero record', () => {
  const result = run(String.raw`
    const dispose = repository.dispose;
    repository.dispose = () => {
      dispose();
      throw new Error('PRIVATE_DIAGNOSTIC_CANARY cleanup /private/canary');
    };
    throw new assert.AssertionError({ actual: 'PRIVATE_DIAGNOSTIC_CANARY /private/canary S-1-canary '.repeat(8192), expected: 'fixture' });
  `, true);
  assert.equal(result.status, 1);
  assert.deepEqual(result.lines, []);
  assert.equal(result.failure, 'cleanup-fixture-v1 stage=action role=none vector=none code=assertion');
});

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
    diagnosticStage = 'base';
    const base = realLstat(database + '-wal', { bigint: true });
    const canary = 'PRIVATE_DIAGNOSTIC_CANARY';
    let placementCalls = 0;
    // Synthetic predicate contracts replace only the existing Windows placement
    // child boundary. The separate native positive case retains actual placement.
    if (process.platform === 'win32') childProcess.spawnSync = (command, args, options) => {
      placementCalls++;
      diagnosticStage = 'placement-command';
      assert.equal(command, join(process.env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'));
      diagnosticStage = 'placement-flags';
      assert.equal(args.length, 5);
      assert.deepEqual(args.slice(0, 4), ['-NoLogo', '-NoProfile', '-NonInteractive', '-Command']);
      assert.equal(typeof args[4], 'string');
      assert.ok(args[4].length > 0);
      diagnosticStage = 'placement-options';
      assert.deepEqual(options, { encoding: 'utf8', timeout: 10_000, maxBuffer: 8192, windowsHide: true,
        env: { ...process.env, FACTORY_PLACEMENT_PATH: join(common, 'factory') } });
      diagnosticStage = 'admission';
      return { status: 0, signal: null, stdout: '{"driveType":3,"filesystem":"NTFS"}' };
    };
    syncBuiltinESMExports();
    try {
    for (const role of ['wal', 'shm', 'journal']) {
      for (const failed of ['regular', 'symbolicLink', 'singleLink', 'groupOtherBitsClear', 'all']) {
        diagnosticRole = role;
        diagnosticVector = failed;
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
        diagnosticStage = 'admission';
        assert.throws(() => openCleanupReadStore(common), { message: 'forward store sidecar is not private regular storage' });
        diagnosticStage = 'observation';
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
    diagnosticStage = 'count';
    assert.equal(placementCalls, process.platform === 'win32' ? 15 : 0);
    } catch (error) {
      reportFixtureFailure(error);
      throw error;
    } finally {
      diagnosticStage = 'restore';
      fs.lstatSync = realLstat;
      childProcess.spawnSync = realSpawn;
      syncBuiltinESMExports();
    }
  `, true);
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

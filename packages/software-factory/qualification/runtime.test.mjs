import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { once } from 'node:events';
import { existsSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { setTimeout as delay } from 'node:timers/promises';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

test('pinned native runtime proves SQLite transaction, backup, contention and process-loss behavior', () => {
  const probe = fileURLToPath(new URL('./runtime.ts', import.meta.url));
  const result = spawnSync(process.execPath, [probe], { encoding: 'utf8', timeout: 30000 });
  assert.equal(result.status, 0, result.stderr);
  const report = JSON.parse(result.stdout);
  assert.equal(report.node, 'v24.22.1');
  assert.equal(report.sqlite, '3.53.4');
  assert.equal(report.journal, 'wal');
  assert.equal(report.synchronous, 2);
  assert.equal(report.foreignKeys, true);
  assert.equal(report.rollback, true);
  assert.equal(report.backupIntegrity, 'ok');
  assert.equal(report.committedAfterLoss, 1);
  assert.equal(report.uncommittedAfterLoss, 0);
  assert.equal(report.concurrentRows, 80);
  assert.equal(report.contention, 'busy');
  assert.ok(report.busyMs >= 30 && report.busyMs < 1000, JSON.stringify(report));
  assert.ok(report.commitP95Ms < 100, JSON.stringify(report));
  assert.ok(report.maxCommitMs < 1000, JSON.stringify(report));
});

test('handled qualification cancellation closes owned workers and removes only its disposable directory', async () => {
  const probe = fileURLToPath(new URL('./runtime.ts', import.meta.url));
  for (const [signal, expected] of [['SIGINT', 130], ['SIGTERM', 143]]) {
    const child = spawn(process.execPath, [probe, '--pause-before-loss', '5000'], { stdio: ['ignore', 'pipe', 'pipe', 'ipc'] });
    const closed = once(child, 'close');
    let diagnostic = '';
    child.stdout.resume();
    const ready = new Promise((resolve, reject) => {
      child.stderr.on('data', (chunk) => {
        diagnostic += chunk;
        const line = diagnostic.split('\n').find((value) => value.startsWith('probe-owned:'));
        if (line) resolve(JSON.parse(line.slice('probe-owned:'.length)));
      });
      child.on('close', () => reject(new Error(`qualifier exited before cancellable worker: ${diagnostic}`)));
    });
    try {
      const owned = await ready;
      if (process.platform === 'win32') child.send({ type: 'qualifier-stop', signal });
      else child.kill(signal);
      const [status] = await closed;
      assert.equal(status, expected, diagnostic);
      assert.throws(() => process.kill(owned.pid, 0), { code: 'ESRCH' });
      assert.equal(existsSync(owned.directory), false);
    } finally {
      if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
      await closed;
    }
  }
});

for (const releaseLock of [true, false]) test(releaseLock
  ? 'qualifier writer survives a real held SQLite lock beyond its initial busy timeout without losing rows'
  : 'qualifier writer fails within its bounded deadline when another SQLite writer never releases', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-runtime-contention-'));
  const path = join(directory, 'facts.sqlite');
  const database = new DatabaseSync(path);
  let child, closed;
  try {
    database.exec('PRAGMA journal_mode=WAL; CREATE TABLE facts(id TEXT PRIMARY KEY); BEGIN IMMEDIATE');
    const worker = fileURLToPath(new URL('./sqlite-worker.mjs', import.meta.url));
    child = spawn(process.execPath, [worker, path, 'write', 'held'], { stdio: ['ignore', 'pipe', 'pipe', 'ipc'] });
    closed = once(child, 'close');
    child.stdout.resume();
    let diagnostic = '';
    child.stderr.on('data', chunk => { diagnostic += chunk; });
    const timer = setTimeout(() => child.kill('SIGKILL'), 9000);
    try {
      const [ready] = await Promise.race([
        once(child, 'message'),
        closed.then(() => { throw new Error(`worker exited before contention handshake: ${diagnostic}`); }),
      ]);
      assert.deepEqual(ready, { ready: 'write' });
      const start = performance.now();
      await delay(350);
      assert.equal(child.exitCode, null, `writer did not retry beyond 100ms: ${diagnostic}`);
      assert.equal(database.prepare('SELECT count(*) AS n FROM facts').get().n, 0);
      if (releaseLock) database.exec('ROLLBACK');
      const [status, signal] = await closed;
      assert.equal(signal, null, diagnostic);
      assert.equal(status, releaseLock ? 0 : 1, diagnostic);
      if (!releaseLock) {
        assert.match(diagnostic, /database is locked/);
        assert.ok(performance.now() - start >= 4500, diagnostic);
        assert.ok(performance.now() - start < 8000, diagnostic);
      }
      assert.equal(database.prepare('SELECT count(*) AS n FROM facts').get().n, releaseLock ? 40 : 0);
    } finally { clearTimeout(timer); }
  } finally {
    if (child && child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
    if (closed) await closed;
    if (database.isTransaction) database.exec('ROLLBACK');
    database.close();
    rmSync(directory, { recursive: true, force: true });
  }
});

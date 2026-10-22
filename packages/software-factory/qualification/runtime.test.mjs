import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { once } from 'node:events';
import { existsSync } from 'node:fs';
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

test('cancelling qualification closes owned workers and removes only its disposable directory', async () => {
  const probe = fileURLToPath(new URL('./runtime.ts', import.meta.url));
  for (const [signal, expected] of [['SIGINT', 130], ['SIGTERM', 143]]) {
    const child = spawn(process.execPath, [probe, '--pause-before-loss', '5000'], { stdio: ['ignore', 'pipe', 'pipe'] });
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
      child.kill(signal);
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

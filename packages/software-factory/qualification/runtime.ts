import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { once } from 'node:events';
import { mkdtempSync, readFileSync, rmSync, statfsSync } from 'node:fs';
import { tmpdir, release } from 'node:os';
import { join } from 'node:path';
import { performance } from 'node:perf_hooks';
import { DatabaseSync, backup } from 'node:sqlite';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { setTimeout as delay } from 'node:timers/promises';

let stopSignal: 'SIGINT' | 'SIGTERM' | undefined;
const cancellation = new AbortController();
const ownedWorkers: ReturnType<typeof spawn>[] = [];
for (const signal of ['SIGINT', 'SIGTERM'] as const) process.on(signal, () => {
  stopSignal ??= signal;
  cancellation.abort();
  for (const child of ownedWorkers) if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
});
function checkStopped() {
  if (stopSignal) throw new Error(`cancelled by ${stopSignal}`);
}

// Run directly with the pinned runtime. This command never installs or downloads anything.
async function qualify() {
  const { values } = parseArgs({ options: { 'pause-before-loss': { type: 'string' } } });
  const pause = Number(values['pause-before-loss'] ?? 0);
  assert.ok(Number.isInteger(pause) && pause >= 0 && pause <= 5000, 'pause-before-loss must be 0-5000 milliseconds');
  checkStopped();
  const manifest = JSON.parse(readFileSync(new URL('./runtime-manifest.json', import.meta.url), 'utf8'));
  assert.equal(process.version, manifest.node, 'runtime mismatch; explicitly obtain the manifest-pinned Node before qualification');
  assert.equal(process.versions.sqlite, manifest.sqlite, 'bundled SQLite differs from the reviewed WAL-fixed version');
  const directory = mkdtempSync(join(tmpdir(), 'factory-sqlite-probe-'));
  const filesystem = statfsSync(directory).type;
  // APFS/HFS, Linux ext/btrfs/xfs/tmpfs. Windows placement needs its own native qualification.
  const localTypes = process.platform === 'darwin' ? [26, 17] : process.platform === 'linux'
    ? [0xef53, 0x9123683e, 0x58465342, 0x01021994] : [];
  const path = join(directory, 'history.sqlite');
  let database: DatabaseSync | undefined;
  const completions: Promise<unknown>[] = [];
  const worker = fileURLToPath(new URL('./sqlite-worker.mjs', import.meta.url));
  function start(mode: string, prefix = '') {
    checkStopped();
    const child = spawn(process.execPath, [worker, path, mode, prefix], { stdio: ['ignore', 'pipe', 'pipe', 'ipc'] });
    ownedWorkers.push(child);
    let diagnostic = '';
    child.stdout?.resume();
    child.stderr?.on('data', (chunk: Buffer) => { diagnostic = (diagnostic + chunk.toString()).slice(-8192); });
    const timer = setTimeout(() => child.kill('SIGKILL'), 10_000);
    const completion = once(child, 'close').then(([code, signal]) => {
      clearTimeout(timer);
      return { code, signal, diagnostic };
    });
    completions.push(completion);
    return { child, completion };
  }
  try {
    assert.ok(localTypes.includes(filesystem), `unsupported or unqualified local filesystem: ${filesystem} (${process.platform})`);
    database = new DatabaseSync(path, { timeout: 100 });
    database.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON');
    const journal = database.prepare('PRAGMA journal_mode').get()?.['journal_mode'];
    const synchronous = database.prepare('PRAGMA synchronous').get()?.['synchronous'];
    const foreignKeys = database.prepare('PRAGMA foreign_keys').get()?.['foreign_keys'] === 1;
    assert.equal(journal, 'wal');
    assert.equal(synchronous, 2);
    assert.equal(foreignKeys, true);
    database.exec('CREATE TABLE facts(id TEXT PRIMARY KEY); CREATE TABLE children(parent TEXT REFERENCES facts(id))');
    assert.throws(() => database!.prepare('INSERT INTO children(parent) VALUES (?)').run('missing'), /FOREIGN KEY/);
    database.exec("BEGIN IMMEDIATE; INSERT INTO facts VALUES ('rollback'); ROLLBACK");
    assert.equal(database.prepare("SELECT count(*) AS n FROM facts WHERE id='rollback'").get()?.['n'], 0);

    database.exec('BEGIN IMMEDIATE');
    const blocked = spawnSync(process.execPath, [worker, path, 'busy'], { encoding: 'utf8', timeout: 5000 });
    database.exec('ROLLBACK');
    assert.equal(blocked.status, 0, blocked.stderr);
    const contention = JSON.parse(blocked.stdout);
    assert.equal(contention.contention, 'busy');
    assert.ok(contention.busyMs >= 30 && contention.busyMs < 1000);

    const writers = [start('write', 'first'), start('write', 'second')];
    for (const writer of writers) {
      const result = await writer.completion;
      checkStopped();
      assert.equal(result.code, 0, result.diagnostic);
    }
    const concurrentRows = database.prepare('SELECT count(*) AS n FROM facts').get()?.['n'];
    assert.equal(concurrentRows, 80);
    for (const mode of ['committed', 'uncommitted']) {
      const owned = start(mode);
      const ready = await Promise.race([
        once(owned.child, 'message'), owned.completion.then((result) => { throw new Error(`probe exited before ready: ${result.diagnostic}`); }),
      ]);
      assert.deepEqual(ready[0], { ready: true });
      checkStopped();
      if (pause) {
        process.stderr.write(`probe-owned:${JSON.stringify({ pid: owned.child.pid, directory })}\n`);
        await delay(pause, undefined, { signal: cancellation.signal });
      }
      checkStopped();
      owned.child.kill('SIGKILL');
      await owned.completion;
    }
    // Reopen after losing the worker's process while a transaction was active.
    database.close();
    database = new DatabaseSync(path, { timeout: 100 });
    const committedAfterLoss = database.prepare("SELECT count(*) AS n FROM facts WHERE id='committed'").get()?.['n'];
    const uncommittedAfterLoss = database.prepare("SELECT count(*) AS n FROM facts WHERE id='uncommitted'").get()?.['n'];
    assert.equal(committedAfterLoss, 1);
    assert.equal(uncommittedAfterLoss, 0);
    const backupPath = join(directory, 'verified-backup.sqlite');
    await backup(database, backupPath, { rate: 1 });
    checkStopped();
    const copy = new DatabaseSync(backupPath, { readOnly: true });
    let backupIntegrity;
    try {
      backupIntegrity = copy.prepare('PRAGMA integrity_check').get()?.['integrity_check'];
      assert.equal(backupIntegrity, 'ok');
      assert.equal(copy.prepare('SELECT count(*) AS n FROM facts').get()?.['n'], 81);
    } finally { copy.close(); }
    const timings: number[] = [];
    for (let index = 0; index < 100; index++) {
      const begin = performance.now();
      database.exec('BEGIN IMMEDIATE');
      database.prepare('INSERT INTO facts(id) VALUES (?)').run(`latency-${index}`);
      database.exec('COMMIT');
      timings.push(performance.now() - begin);
    }
    timings.sort((a, b) => a - b);
    const commitP95Ms = timings[94]!;
    const maxCommitMs = timings[99]!;
    assert.ok(commitP95Ms < 100, `p95 small transaction exceeded 100ms: ${commitP95Ms}`);
    assert.ok(maxCommitMs < 1000, `small transaction exceeded 1s: ${maxCommitMs}`);
    return { node: process.version, sqlite: process.versions.sqlite, platform: process.platform, arch: process.arch,
      os: release(), filesystem, journal, synchronous, foreignKeys, rollback: true, ...contention,
      concurrentRows, committedAfterLoss, uncommittedAfterLoss, backupIntegrity, commitP95Ms, maxCommitMs };
  } finally {
    for (const child of ownedWorkers) if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
    await Promise.allSettled(completions);
    database?.close();
    rmSync(directory, { recursive: true, force: true });
  }
}

try {
  process.stdout.write(`${JSON.stringify(await qualify())}\n`);
} catch (error) {
  process.stderr.write(`runtime qualification ${stopSignal ? `cancelled by ${stopSignal}` : `failed: ${error instanceof Error ? error.message : String(error)}`}\n`);
  process.exitCode = stopSignal === 'SIGINT' ? 130 : stopSignal === 'SIGTERM' ? 143 : 1;
}

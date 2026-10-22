// Disposable storage probes only. Each worker operates on its parent's fixture DB.
import { DatabaseSync } from 'node:sqlite';
import { performance } from 'node:perf_hooks';
import { setTimeout as delay } from 'node:timers/promises';

const [path, mode, prefix] = process.argv.slice(2);
const database = new DatabaseSync(path, { timeout: mode === 'busy' ? 40 : 100 });
database.exec('PRAGMA foreign_keys=ON; PRAGMA synchronous=FULL');
if (mode === 'busy') {
  const start = performance.now();
  try {
    database.exec('BEGIN IMMEDIATE; ROLLBACK');
    process.stdout.write(JSON.stringify({ contention: 'unexpected success', busyMs: performance.now() - start }));
    process.exitCode = 1;
  } catch (error) {
    if (error.errcode !== 5) throw error;
    process.stdout.write(JSON.stringify({ contention: 'busy', busyMs: performance.now() - start }));
  }
  database.close();
} else if (mode === 'write') {
  process.send?.({ ready: 'write' });
  for (let index = 0; index < 40; index++) {
    const deadline = performance.now() + 5000;
    while (true) {
      try { database.exec('BEGIN IMMEDIATE'); break; }
      catch (error) {
        // Only retry confirmed contention before acquiring a transaction. Never replay writes or commits.
        if (error.errcode !== 5 || database.isTransaction || performance.now() >= deadline) throw error;
        await delay(20);
      }
    }
    database.prepare('INSERT INTO facts(id) VALUES (?)').run(`${prefix}-${index}`);
    database.exec('COMMIT');
  }
  database.close();
} else if (mode === 'committed' || mode === 'uncommitted') {
  database.exec('BEGIN IMMEDIATE');
  database.prepare('INSERT INTO facts(id) VALUES (?)').run(mode);
  if (mode === 'committed') database.exec('COMMIT');
  process.send({ ready: true });
  const hold = setInterval(() => {}, 1000);
  // Parent death must not leave a qualification-only process holding fixture storage forever.
  process.on('disconnect', () => {
    clearInterval(hold);
    database.close();
  });
} else {
  database.close();
  throw new Error('Unknown storage probe mode');
}

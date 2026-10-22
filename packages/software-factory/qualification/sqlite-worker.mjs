// Disposable storage probes only. Each worker operates on its parent's fixture DB.
import { DatabaseSync } from 'node:sqlite';
import { performance } from 'node:perf_hooks';

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
  for (let index = 0; index < 40; index++) {
    database.exec('BEGIN IMMEDIATE');
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

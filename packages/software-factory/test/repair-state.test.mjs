import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';
import { inspectRepairSelection } from '../dist/repair.js';
import { createRepository } from './fixtures/repository.mjs';

test('repair inspection refuses an unowned repository without creating installation state', async () => {
  const fixture = createRepository();
  try {
    const result = await inspectRepairSelection(fixture.path, { bundleRoot: fixture.path,
      manifestSha256: '0'.repeat(64), nodeArchivePath: join(fixture.path, 'untracked.txt') });
    assert.equal(result.action, 'refused');
    assert.equal(existsSync(join(fixture.path, '.git/factory')), false);
  } finally { fixture.dispose(); }
});

test('pinned read-only SQLite includes committed WAL and holds one endmark across concurrent commit', () => {
  const fixture = createRepository(), path = join(fixture.path, 'readonly.sqlite');
  const hash = file => createHash('sha256').update(readFileSync(file)).digest('hex');
  const writer = new DatabaseSync(path);
  let reader;
  try {
    writer.exec('PRAGMA journal_mode=WAL; PRAGMA wal_autocheckpoint=0; CREATE TABLE facts(value); INSERT INTO facts VALUES (42)');
    const before = { database: hash(path), wal: hash(`${path}-wal`) };
    reader = new DatabaseSync(path, { readOnly: true }); reader.exec('BEGIN');
    assert.deepEqual(reader.prepare('SELECT value FROM facts ORDER BY value').all().map(row => row.value), [42]);
    assert.deepEqual({ database: hash(path), wal: hash(`${path}-wal`) }, before);
    writer.exec('INSERT INTO facts VALUES (43)');
    const committed = { database: hash(path), wal: hash(`${path}-wal`) };
    assert.deepEqual(reader.prepare('SELECT value FROM facts ORDER BY value').all().map(row => row.value), [42]);
    assert.deepEqual({ database: hash(path), wal: hash(`${path}-wal`) }, committed);
    reader.exec('COMMIT');
    assert.deepEqual(reader.prepare('SELECT value FROM facts ORDER BY value').all().map(row => row.value), [42, 43]);
    reader.close(); reader = null;
    assert.deepEqual({ database: hash(path), wal: hash(`${path}-wal`) }, committed);
    const shm = lstatSync(`${path}-shm`);
    assert.ok(shm.isFile() && !shm.isSymbolicLink() && shm.nlink === 1);
  } finally { reader?.close(); writer.close(); fixture.dispose(); }
});

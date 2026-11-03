import { createHash } from 'node:crypto';
import type { DatabaseSync } from 'node:sqlite';

export type ForwardShape = 'v3' | 'v4-base' | 'v4-plus' | 'v5' | 'v6' | 'v7';
const SHAPES: Readonly<Record<ForwardShape, { version: number; digest: string }>> = {
  v3: { version: 3, digest: '8e1cb7eca1ecc7ac6f373d7df6bc9110e7951937f5f2075193ac952d06bd69ce' },
  'v4-base': { version: 4, digest: '49449d80b69df7c8ae32c02c512a70db40c590b07ae7b82d091443ed46d1de74' },
  'v4-plus': { version: 4, digest: 'bf8f1ac5dfecf49a497b207359555f41be9b392a97cc482fff45d194f3d80cde' },
  v5: { version: 5, digest: 'a882a6b6a38b21eba59aa0df7bd0afc45e38e53cfd96b1ed95b7ed0d12ddfb5b' },
  v6: { version: 6, digest: '6eb9f73cef58a08c00648284790d87288a62eb9aab1465c3b02f62880067e2fd' },
  v7: { version: 7, digest: '145da70ebe06f5e21bc9cbbcd3e3727c86f3febf95d3c452e9f29f3ee2d987d2' },
};
const ORDER: readonly ForwardShape[] = ['v3', 'v4-base', 'v4-plus', 'v5', 'v6', 'v7'];
const DDL: Readonly<Record<Exclude<ForwardShape, 'v7'>, string>> = {
  v3: `CREATE INDEX invocation_run_page ON invocations(run_id);
    CREATE INDEX observation_invocation_page ON observation_events(json_extract(data,'$.invocationId'),cursor);
    CREATE INDEX clearance_invocation_page ON clearances(json_extract(data,'$.invocationId'),id);
    PRAGMA user_version=4;`,
  'v4-base': `CREATE INDEX attempt_operation_target ON attempts(operation_id,invocation_id);
    CREATE INDEX capture_question_target ON captures(invocation_id,channel);`,
  'v4-plus': `CREATE TABLE notification_deliveries(id TEXT PRIMARY KEY, invocation_id TEXT NOT NULL REFERENCES invocations(id), kind TEXT NOT NULL CHECK(kind='initial'), data TEXT NOT NULL CHECK(json_valid(data)), UNIQUE(invocation_id,kind));
    CREATE INDEX notification_invocation ON notification_deliveries(invocation_id);
    PRAGMA user_version=5;`,
  v5: `CREATE TABLE notification_preferences(id INTEGER PRIMARY KEY CHECK(id=1), success_notices INTEGER NOT NULL CHECK(success_notices IN (0,1)), reminders INTEGER NOT NULL CHECK(reminders IN (0,1)), updated_at TEXT NOT NULL);
    CREATE TABLE notification_acknowledgments(invocation_id TEXT PRIMARY KEY REFERENCES invocations(id), acknowledged_at TEXT NOT NULL);
    PRAGMA user_version=6;`,
  v6: `CREATE TABLE notification_attention(invocation_id TEXT PRIMARY KEY REFERENCES invocations(id));
    CREATE TABLE notification_reminder_groups(id TEXT PRIMARY KEY, claim_id TEXT NOT NULL, unsettled INTEGER NOT NULL CHECK(unsettled IN (0,1)), data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE INDEX notification_reminder_unsettled ON notification_reminder_groups(claim_id,unsettled);
    PRAGMA user_version=7;`,
};
export function assertForwardRuntime() {
  if (process.versions.node !== '24.22.1' || process.versions.sqlite !== '3.53.4')
    throw new Error('forward schema runtime differs from qualified Node and SQLite');
}
function hash(value: string | Buffer): string { return createHash('sha256').update(value).digest('hex'); }

/** Exact historical sqlite_schema shape, including automatic indexes and constraints. */
export function knownForwardShape(database: DatabaseSync): ForwardShape {
  const version = database.prepare('PRAGMA user_version').get()?.['user_version'];
  const objects = [];
  let bytes = 0;
  for (const row of database.prepare('SELECT type,name,tbl_name,sql FROM sqlite_schema ORDER BY type,name').iterate()) {
    const size = Buffer.byteLength(JSON.stringify(row));
    if (objects.length >= 64 || size > 8192 || (bytes += size) > 256 * 1024)
      throw new Error('forward schema inventory exceeds bound');
    objects.push(row);
  }
  const signature = hash(JSON.stringify(objects));
  const found = ORDER.find(name => SHAPES[name].version === version && SHAPES[name].digest === signature);
  if (!found) throw new Error('unsupported or changed forward schema; preserving store');
  return found;
}

export function assertForwardIntegrity(database: DatabaseSync): void {
  const result = database.prepare('PRAGMA integrity_check').iterate();
  if (result.next().value?.['integrity_check'] !== 'ok' || !result.next().done
    || database.prepare('PRAGMA foreign_key_check').get())
    throw new Error('forward store integrity or foreign keys differ');
}

/** Stable essential counts from an already authenticated schema; no caller-provided table names. */
export function forwardCounts(database: DatabaseSync): { digest: string; rows: Record<string, string> } {
  const shape = knownForwardShape(database);
  const names: string[] = [];
  for (const row of database.prepare("SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name").iterate()) {
    if (names.length >= 32) throw new Error('forward table inventory exceeds bound');
    names.push(String(row['name']));
  }
  const rows: Record<string, string> = {};
  for (const name of names) {
    if (!/^[a-z_]+$/.test(name)) throw new Error('unsafe forward table name');
    const query = database.prepare(`SELECT count(*) AS total FROM "${name}"`);
    query.setReadBigInts(true);
    rows[name] = String(query.get()?.['total']);
  }
  return { rows, digest: hash(JSON.stringify(rows)) };
}

/** Caller owns the immediate transaction and exact claim/backup CAS. */
export function applyForwardStep(database: DatabaseSync, expected: ForwardShape): ForwardShape {
  if (knownForwardShape(database) !== expected || expected === 'v7') throw new Error('forward step precondition differs');
  database.exec(DDL[expected]);
  const next = ORDER[ORDER.indexOf(expected) + 1]!;
  if (knownForwardShape(database) !== next) throw new Error('forward step postcondition differs');
  return next;
}

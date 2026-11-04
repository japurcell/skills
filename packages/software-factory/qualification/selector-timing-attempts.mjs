import { randomUUID } from 'node:crypto';
import { lstatSync, realpathSync } from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { fixtureIdentity, limits, telemetry, timingSync } from './selector-timing.mjs';

// Receives only the disposable repository just created by the selected fixture helper.
// No history/capture API is called, and no raw database identity leaves this adapter.
export function fixtureAttemptTiming(repository) {
  if (!telemetry()) return Object.assign(() => {}, { invocationId: () => '' });
  const path = realpathSync(repository), container = dirname(path);
  if (basename(path) !== 'repository' || !basename(container).startsWith('factory-repository-')) throw new Error('invalid qualification fixture ownership');
  const identity = fixtureIdentity(path), ids = new Map(); let cursor = 0, count = 0;
  const opaque = (value, kind) => {
    if (typeof value !== 'string' || value.length < 1 || value.length > 100) throw new Error('invalid qualification attempt metadata');
    const key = kind + '/' + value;
    if (!ids.has(key)) ids.set(key, randomUUID());
    return ids.get(key);
  };
  const read = () => { try { timingSync('export', () => {
    const current = lstatSync(path);
    if (current.isSymbolicLink() || current.ino !== identity.ino || current.dev !== identity.dev || realpathSync(path) !== path) throw new Error('invalid qualification fixture ownership');
    const file = join(path, '.git/factory/history.sqlite');
    if (realpathSync(dirname(file)) !== dirname(file)) throw new Error('invalid qualification fixture ownership');
    const stat = lstatSync(file);
    if (!stat.isFile() || stat.isSymbolicLink() || stat.nlink !== 1) throw new Error('invalid qualification fixture ownership');
    const database = new DatabaseSync(file, { readOnly: true, timeout: 0 });
    try {
      const query = database.prepare(`SELECT e.cursor, e.kind, json_extract(e.data,'$.at') AS at,
        a.id AS attempt, a.invocation_id AS invocation,
        CASE WHEN o.operation_key LIKE 'startup/git/%' THEN 'startup/git'
          WHEN o.operation_key LIKE 'startup/build/%' THEN 'startup/build'
          WHEN a.kind='agent' THEN 'fake-agent' WHEN a.kind='command' THEN 'fixture-command' ELSE 'unknown' END AS class
        FROM observation_events e LEFT JOIN attempts a ON a.id=json_extract(e.data,'$.attemptId')
        LEFT JOIN operations o ON o.id=a.operation_id
        WHERE e.cursor>? AND e.kind IN ('attempt.started','attempt.settled') ORDER BY e.cursor LIMIT 128`);
      for (;;) {
        const rows = query.all(cursor);
        for (const row of rows) {
          if (++count > limits.databaseRows) throw new Error('qualification attempt row bound exceeded');
          telemetry().mark('attempt', { phase: row.kind, at: row.at, invocationId: opaque(row.invocation, 'invocation'), attemptId: opaque(row.attempt, 'attempt'), operationClass: row.class });
          cursor = Number(row.cursor);
        }
        if (rows.length < 128) break;
      }
    } finally { database.close(); }
  }); } catch { telemetry().mark('export', { disposition: 'incomplete' }); } };
  read.invocationId = value => value === undefined ? '' : opaque(value, 'invocation');
  return read;
}

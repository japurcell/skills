import type { DatabaseSync } from 'node:sqlite';

export const schemaVersion = 6;

export function initializeSchema(database: DatabaseSync) {
  database.exec(`
    BEGIN IMMEDIATE;
    CREATE TABLE repository(id TEXT PRIMARY KEY, release TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('ready','incomplete','absent')),
      agent_limit INTEGER NOT NULL DEFAULT 2, command_limit INTEGER NOT NULL DEFAULT 2);
    CREATE TABLE runs(id TEXT PRIMARY KEY, data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE TABLE worktrees(id TEXT PRIMARY KEY, path TEXT UNIQUE NOT NULL, data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE TABLE invocations(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), worktree_id TEXT NOT NULL REFERENCES worktrees(id), data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE INDEX invocation_history ON invocations(run_id, id);
    CREATE INDEX invocation_run_page ON invocations(run_id);
    CREATE TABLE operations(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), operation_key TEXT NOT NULL, data TEXT NOT NULL CHECK(json_valid(data)), UNIQUE(run_id, operation_key));
    CREATE TABLE attempts(id TEXT PRIMARY KEY, invocation_id TEXT NOT NULL REFERENCES invocations(id), operation_id TEXT NOT NULL REFERENCES operations(id), kind TEXT NOT NULL CHECK(kind IN ('agent','command')),
      occupied INTEGER NOT NULL CHECK(occupied IN (0,1)), data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE INDEX attempt_capacity ON attempts(kind,occupied);
    CREATE INDEX attempt_operation_target ON attempts(operation_id,invocation_id);
    CREATE TABLE allowance_ledger(id TEXT PRIMARY KEY, attempt_id TEXT NOT NULL REFERENCES attempts(id), run_id TEXT NOT NULL REFERENCES runs(id), scope TEXT NOT NULL, category TEXT NOT NULL, delta INTEGER NOT NULL CHECK(delta IN (-1,1)), UNIQUE(attempt_id,category,delta));
    CREATE TABLE owner_claims(id TEXT PRIMARY KEY, token TEXT UNIQUE NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('worktree','dashboard','maintenance')),
      resource_key TEXT NOT NULL, invocation_id TEXT REFERENCES invocations(id), data TEXT NOT NULL CHECK(json_valid(data)), UNIQUE(kind, resource_key));
    CREATE TABLE observation_events(cursor INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE INDEX observation_invocation_page ON observation_events(json_extract(data,'$.invocationId'),cursor);
    CREATE TABLE clearances(id TEXT PRIMARY KEY, claim_id TEXT NOT NULL, data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE INDEX clearance_history ON clearances(claim_id,id);
    CREATE INDEX clearance_invocation_page ON clearances(json_extract(data,'$.invocationId'),id);
    CREATE TABLE captures(id TEXT PRIMARY KEY, invocation_id TEXT NOT NULL REFERENCES invocations(id), attempt_id TEXT REFERENCES attempts(id),
      channel TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('open','complete','partial','unknown','pruned')), sequence INTEGER NOT NULL DEFAULT 0);
    CREATE INDEX capture_history ON captures(invocation_id,id);
    CREATE INDEX capture_question_target ON captures(invocation_id,channel);
    CREATE TABLE capture_chunks(capture_id TEXT NOT NULL REFERENCES captures(id), sequence INTEGER NOT NULL CHECK(sequence>0), text TEXT NOT NULL,
      PRIMARY KEY(capture_id,sequence), CHECK(length(CAST(text AS BLOB))<=65536));
    CREATE TABLE sessions(id TEXT PRIMARY KEY, invocation_id TEXT NOT NULL REFERENCES invocations(id), attempt_id TEXT NOT NULL REFERENCES attempts(id), native_id TEXT NOT NULL, data TEXT NOT NULL CHECK(json_valid(data)), UNIQUE(attempt_id,native_id));
    CREATE INDEX session_history ON sessions(invocation_id,attempt_id);
    CREATE TABLE notification_deliveries(id TEXT PRIMARY KEY, invocation_id TEXT NOT NULL REFERENCES invocations(id), kind TEXT NOT NULL CHECK(kind='initial'), data TEXT NOT NULL CHECK(json_valid(data)), UNIQUE(invocation_id,kind));
    CREATE INDEX notification_invocation ON notification_deliveries(invocation_id);
    CREATE TABLE notification_preferences(id INTEGER PRIMARY KEY CHECK(id=1), success_notices INTEGER NOT NULL CHECK(success_notices IN (0,1)), reminders INTEGER NOT NULL CHECK(reminders IN (0,1)), updated_at TEXT NOT NULL);
    CREATE TABLE notification_acknowledgments(invocation_id TEXT PRIMARY KEY REFERENCES invocations(id), acknowledged_at TEXT NOT NULL);
    PRAGMA user_version=6;
    COMMIT;
  `);
}

import type { DatabaseSync } from 'node:sqlite';

export const schemaVersion = 1;

export function initializeSchema(database: DatabaseSync) {
  database.exec(`
    BEGIN IMMEDIATE;
    CREATE TABLE repository(id TEXT PRIMARY KEY, release TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('ready','incomplete','absent')),
      agent_limit INTEGER NOT NULL DEFAULT 2, command_limit INTEGER NOT NULL DEFAULT 2);
    CREATE TABLE runs(id TEXT PRIMARY KEY, data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE TABLE worktrees(id TEXT PRIMARY KEY, path TEXT UNIQUE NOT NULL, data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE TABLE invocations(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), worktree_id TEXT NOT NULL REFERENCES worktrees(id), data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE INDEX invocation_history ON invocations(run_id, id);
    CREATE TABLE operations(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), operation_key TEXT NOT NULL, data TEXT NOT NULL CHECK(json_valid(data)), UNIQUE(run_id, operation_key));
    CREATE TABLE attempts(id TEXT PRIMARY KEY, invocation_id TEXT NOT NULL REFERENCES invocations(id), operation_id TEXT NOT NULL REFERENCES operations(id), kind TEXT NOT NULL CHECK(kind IN ('agent','command')),
      occupied INTEGER NOT NULL CHECK(occupied IN (0,1)), data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE INDEX attempt_capacity ON attempts(kind,occupied);
    CREATE TABLE allowance_ledger(id TEXT PRIMARY KEY, attempt_id TEXT NOT NULL REFERENCES attempts(id), run_id TEXT NOT NULL REFERENCES runs(id), scope TEXT NOT NULL, category TEXT NOT NULL, delta INTEGER NOT NULL CHECK(delta IN (-1,1)), UNIQUE(attempt_id,category,delta));
    CREATE TABLE owner_claims(id TEXT PRIMARY KEY, token TEXT UNIQUE NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('worktree','dashboard','maintenance')),
      resource_key TEXT NOT NULL, invocation_id TEXT REFERENCES invocations(id), data TEXT NOT NULL CHECK(json_valid(data)), UNIQUE(kind, resource_key));
    CREATE TABLE observation_events(cursor INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE TABLE clearances(id TEXT PRIMARY KEY, claim_id TEXT NOT NULL, data TEXT NOT NULL CHECK(json_valid(data)));
    CREATE INDEX clearance_history ON clearances(claim_id,id);
    PRAGMA user_version=1;
    COMMIT;
  `);
}

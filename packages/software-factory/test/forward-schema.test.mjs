import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { readFileSync, lstatSync, mkdirSync, chmodSync, writeFileSync, renameSync, symlinkSync, copyFileSync } from 'node:fs';
import { hostname } from 'node:os';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { createRepository } from './fixtures/repository.mjs';
import { currentOwner } from '../dist/native/process.js';
import { advanceForwardSchema, consumeMaintenanceHandoff, inspectMaintenance, prepareForwardSchema,
  prepareMaintenanceHandoff, resumeForwardSchema, inspectForwardSchema } from '../dist/maintenance.js';
import { openForwardMaintenanceStore, openRepositoryStore } from '../dist/store.js';
import { repositoryIdentity } from '../dist/workspace.js';
import { pathToFileURL } from 'node:url';

const fixture = name => readFileSync(fileURLToPath(new URL(`./fixtures/forward-schema/${name}.sql`, import.meta.url)), 'utf8');
const selection = { release: '1.2.3', selectionDigest: 'a'.repeat(64), targetReleaseSha256: 'b'.repeat(64),
  artifactDigests: { node: 'c'.repeat(64) }, targetSchema: 7 };

function oldRepository(version) {
  const repository = createRepository();
  const root = repository.path, common = join(root, '.git');
  mkdirSync(join(common, 'factory'), { mode: 0o700 });
  const path = join(common, 'factory/history.sqlite');
  const db = new DatabaseSync(path);
  db.exec(`PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; ${fixture(version)}`);
  db.prepare("INSERT INTO repository(id,release,state) VALUES (?,?, 'ready')")
    .run('01234567-89ab-4cde-8fab-0123456789ab', 'old-release');
  db.prepare('INSERT INTO runs(id,data) VALUES (?,?)').run('run-1', JSON.stringify({ id: 'run-1' }));
  db.prepare('INSERT INTO worktrees(id,path,data) VALUES (?,?,?)').run('worktree-1', root, '{}');
  db.prepare('INSERT INTO invocations(id,run_id,worktree_id,data) VALUES (?,?,?,?)').run('invocation-1', 'run-1', 'worktree-1', '{}');
  db.prepare('INSERT INTO operations(id,run_id,operation_key,data) VALUES (?,?,?,?)').run('operation-1', 'run-1', 'key', '{}');
  db.prepare('INSERT INTO attempts(id,invocation_id,operation_id,kind,occupied,data) VALUES (?,?,?,?,?,?)')
    .run('attempt-1', 'invocation-1', 'operation-1', 'command', 0, '{}');
  db.prepare('INSERT INTO captures(id,invocation_id,attempt_id,channel,state,sequence) VALUES (?,?,?,?,?,?)')
    .run('capture-1', 'invocation-1', 'attempt-1', 'output', 'complete', 1);
  db.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,?,?)').run('capture-1', 1, 'kept');
  db.close();
  chmodSync(path, 0o600);
  return { repository, root, common, path };
}

for (const version of ['v3', 'v4-base', 'v4-plus', 'v5', 'v6', 'v7']) test(`forward preparation and staged one-step migration preserve real ${version} history`, async () => {
  const owned = oldRepository(version);
  try {
    const before = readFileSync(owned.path);
    if (version !== 'v7') assert.throws(() => openRepositoryStore(owned.common), /incompatible schema/);
    assert.deepEqual(readFileSync(owned.path), before, 'normal old-schema refusal must not mutate storage');
    const handle = await prepareForwardSchema(owned.root, selection, currentOwner());
    assert.equal(handle.repositoryId, '01234567-89ab-4cde-8fab-0123456789ab');
    const live = new DatabaseSync(owned.path, { readOnly: true });
    try {
      assert.equal(live.prepare('PRAGMA user_version').get().user_version, Number(version.slice(1, 2)));
      assert.equal(live.prepare('SELECT count(*) n FROM owner_claims').get().n, 1);
      assert.equal(live.prepare('SELECT state FROM repository').get().state, 'ready');
    } finally { live.close(); }
    const backup = join(owned.common, 'factory/maintenance-backups', handle.operationId, handle.backupId, 'history.sqlite');
    assert.ok(lstatSync(backup).isFile());
    const backupUrl = pathToFileURL(backup); backupUrl.searchParams.set('mode', 'ro'); backupUrl.searchParams.set('immutable', '1');
    const copied = new DatabaseSync(backupUrl, { readOnly: true });
    try {
      assert.equal(copied.prepare('PRAGMA user_version').get().user_version, Number(version.slice(1, 2)));
      assert.equal(copied.prepare('SELECT text FROM capture_chunks').get().text, 'kept');
      assert.equal(copied.prepare('PRAGMA integrity_check').get().integrity_check, 'ok');
    } finally { copied.close(); }
    const inspection = await inspectForwardSchema(owned.root, handle.operationId);
    assert.equal(inspection.intent.forward.backupBound, true);
    assert.ok(!JSON.stringify(inspection).includes(handle.token));
    const excluded = openForwardMaintenanceStore(owned.common);
    try {
      await assert.rejects(excluded.createRun(), /maintenance claimed/);
      await assert.rejects(excluded.claimResource({ kind: 'dashboard', owner: currentOwner() }), /maintenance claimed/);
    } finally { excluded.close(); }
    await assert.rejects(prepareForwardSchema(owned.root, selection, currentOwner()), /forward admission requires exact ready idle repository/);
    await assert.rejects(resumeForwardSchema(owned.root, handle.operationId, selection, currentOwner(),
      { operatorConfirmed: true, note: 'Known live original owner.' }), /known-live/);
    await assert.rejects(resumeForwardSchema(owned.root, handle.operationId,
      { ...selection, selectionDigest: 'e'.repeat(64) }, currentOwner(),
      { operatorConfirmed: true, note: 'Wrong target.' }), /selection differs/);
    const stagePath = (await inspectMaintenance(owned.root)).intent.stagePath;
    mkdirSync(join(stagePath, 'payload'), { recursive: true, mode: 0o700 });
    writeFileSync(join(stagePath, 'payload', 'node'), 'controlled staged node');
    const handoff = await prepareMaintenanceHandoff(owned.root, handle);
    const ticket = JSON.parse(readFileSync(handoff.ticketPath, 'utf8'));
    writeFileSync(ticket.exitReceiptPath, JSON.stringify({ version: 1, operationId: handle.operationId,
      claimId: handle.claimId, stageDigest: handoff.stageDigest, nonce: ticket.nonce }), { flag: 'wx', mode: 0o600 });
    assert.equal((await consumeMaintenanceHandoff(handoff.ticketPath)).phase, 'modifying');
    await assert.rejects(advanceForwardSchema({ ...handle, token: '00000000-0000-4000-8000-000000000001' }), /token/);
    let shape;
    do { ({ shape } = await advanceForwardSchema(handle)); } while (shape !== 'v7');
    const final = openForwardMaintenanceStore(owned.common);
    try {
      assert.equal(final.forwardShape(), 'v7');
      assert.equal(final.readMaintenanceClaim(handle.operationId).maintenance.forward.currentShape, 'v7');
      await assert.rejects(final.createRun(), /installation not ready|maintenance claimed/);
    } finally { final.close(); }
    const result = new DatabaseSync(owned.path, { readOnly: true });
    try {
      assert.equal(result.prepare('SELECT text FROM capture_chunks').get().text, 'kept');
      assert.equal(result.prepare('SELECT state FROM repository').get().state, 'incomplete');
      assert.equal(result.prepare('SELECT count(*) n FROM owner_claims').get().n, 1);
    } finally { result.close(); }
  } finally { owned.repository.dispose(); }
});

test('marker, changed schema, unsupported version, linked store and linked WAL refuse before admission', async () => {
  for (const change of ['marker', 'schema', 'version', 'link', 'sidecar']) {
    const owned = oldRepository('v3');
    try {
      if (change === 'marker') writeFileSync(join(owned.common, 'factory/bootstrap-incomplete'), 'foreign');
      if (change === 'schema' || change === 'version') {
        const db = new DatabaseSync(owned.path);
        try { db.exec(change === 'schema' ? 'CREATE INDEX foreign_history ON runs(id)' : 'PRAGMA user_version=99'); }
        finally { db.close(); }
      }
      if (change === 'link') {
        const original = `${owned.path}.original`; renameSync(owned.path, original); symlinkSync(original, owned.path);
      }
      if (change === 'sidecar') {
        const foreign = join(owned.common, 'factory', 'foreign-wal');
        writeFileSync(foreign, 'foreign', { mode: 0o600 }); symlinkSync(foreign, `${owned.path}-wal`);
      }
      const before = readFileSync(change === 'link' ? `${owned.path}.original` : owned.path);
      await assert.rejects(prepareForwardSchema(owned.root, selection, currentOwner()),
        /marker|schema|store file|sidecar|incompatible|invalid/i);
      assert.deepEqual(readFileSync(change === 'link' ? `${owned.path}.original` : owned.path), before);
    } finally { owned.repository.dispose(); }
  }
});

test('bound backup identity, bytes and receipt must survive before handoff', async () => {
  for (const change of ['same-bytes-new-inode', 'linked', 'altered', 'receipt', 'extra']) {
    const owned = oldRepository('v3');
    try {
      const handle = await prepareForwardSchema(owned.root, selection, currentOwner());
      const backup = join(owned.common, 'factory/maintenance-backups', handle.operationId, handle.backupId, 'history.sqlite');
      if (change === 'extra') {
        writeFileSync(join(backup, '..', 'foreign'), 'foreign', { mode: 0o600 });
      } else if (change === 'receipt') {
        const receiptPath = join(backup, '..', 'backup-receipt.json');
        const receipt = JSON.parse(readFileSync(receiptPath, 'utf8'));
        writeFileSync(receiptPath, JSON.stringify({ ...receipt, sourceRelease: 'changed' }), { mode: 0o600 });
      } else if (change === 'altered') {
        const db = new DatabaseSync(backup);
        try { db.prepare('INSERT INTO runs(id,data) VALUES (?,?)').run('foreign', '{}'); }
        finally { db.close(); }
      } else {
        const retained = `${backup}.retained`; renameSync(backup, retained);
        if (change === 'linked') symlinkSync(retained, backup);
        else copyFileSync(retained, backup);
      }
      mkdirSync(join(owned.common, 'factory/controller-staging', handle.operationId, 'payload'), { recursive: true });
      await assert.rejects(prepareMaintenanceHandoff(owned.root, handle), /backup/);
      const live = openForwardMaintenanceStore(owned.common);
      try {
        assert.equal(live.readMaintenanceClaim(handle.operationId).maintenance.phase, 'preparing');
        assert.equal(live.forwardShape(), 'v3');
      } finally { live.close(); }
    } finally { owned.repository.dispose(); }
  }
});

test('explicit inspected prebind recovery rotates token and backup identity, preserving partial evidence', async () => {
  const owned = oldRepository('v4-base');
  try {
    const common = (await repositoryIdentity(owned.root)).common;
    const store = openForwardMaintenanceStore(common);
    const operationId = randomUUID(), originalBackupId = randomUUID();
    const absentOwner = { host: hostname(), pid: 99999999, start: null };
    let claim;
    try {
      const intent = { operationId, repositoryId: store.repositoryId(), kind: 'upgrade', release: selection.release,
        targetReleaseSha256: selection.targetReleaseSha256, selectionDigest: selection.selectionDigest,
        artifactDigests: selection.artifactDigests, targetSchema: 7,
        stagePath: join(common, 'factory/controller-staging', operationId), stageDigest: null,
        stageIdentity: null, phase: 'preparing', ownedReceiptId: null, backupId: originalBackupId,
        ticketNonceHash: null, ticketConsumed: false, candidate: null,
        forward: { sourceShape: store.forwardShape(), currentShape: store.forwardShape(),
          sourceRelease: store.repositoryRelease(), sourceIdentity: store.forwardIdentity(), backup: null } };
      claim = await store.beginForwardMaintenance(intent, absentOwner);
    } finally { store.close(); }
    const partial = join(common, 'factory/maintenance-backups', operationId, originalBackupId, 'history.sqlite');
    mkdirSync(join(partial, '..'), { recursive: true, mode: 0o700 });
    writeFileSync(partial, 'partial old backup', { mode: 0o600 });
    await assert.rejects(resumeForwardSchema(owned.root, operationId, selection, currentOwner(),
      { operatorConfirmed: false, note: 'No clearance.' }), /operator clearance/);
    const recovered = await resumeForwardSchema(owned.root, operationId, selection, currentOwner(),
      { operatorConfirmed: true, note: 'Inspected absent preparer and retained partial backup.' });
    assert.equal(recovered.operationId, operationId);
    assert.equal(recovered.claimId, claim.id);
    assert.notEqual(recovered.token, claim.token);
    assert.notEqual(recovered.backupId, originalBackupId);
    assert.equal(readFileSync(partial, 'utf8'), 'partial old backup');
    const live = openForwardMaintenanceStore(common);
    try {
      const current = live.readMaintenanceClaim(operationId);
      assert.equal(current.maintenance.forward.backup.id, recovered.backupId);
      assert.equal(current.maintenance.forward.currentShape, 'v4-base');
      assert.equal(live.forwardShape(), 'v4-base');
    } finally { live.close(); }
  } finally { owned.repository.dispose(); }
});

test('existing dashboard claim blocks forward admission without DDL', async () => {
  const owned = oldRepository('v3');
  try {
    const store = openForwardMaintenanceStore(owned.common);
    try { await store.claimResource({ kind: 'dashboard', owner: currentOwner() }); }
    finally { store.close(); }
    await assert.rejects(prepareForwardSchema(owned.root, selection, currentOwner()), /forward admission requires/);
    const live = new DatabaseSync(owned.path);
    try {
      assert.equal(live.prepare('PRAGMA user_version').get().user_version, 3);
      assert.equal(live.prepare('SELECT kind FROM owner_claims').get().kind, 'dashboard');
    } finally { live.close(); }
  } finally { owned.repository.dispose(); }
});

test('a concurrent SQLite writer prevents forward admission and leaves the old schema unchanged', async () => {
  const owned = oldRepository('v3');
  const writer = new DatabaseSync(owned.path);
  try {
    writer.exec('BEGIN IMMEDIATE');
    await assert.rejects(prepareForwardSchema(owned.root, selection, currentOwner()), /locked|busy/i);
    assert.equal(writer.prepare('SELECT count(*) n FROM owner_claims').get().n, 0);
    assert.equal(writer.prepare('PRAGMA user_version').get().user_version, 3);
  } finally { if (writer.isTransaction) writer.exec('ROLLBACK'); writer.close(); owned.repository.dispose(); }
});

test('foreign-key inconsistency and corrupt bytes refuse without adding a claim', async () => {
  for (const damage of ['foreign-key', 'bytes']) {
    const owned = oldRepository('v3');
    try {
      if (damage === 'foreign-key') {
        const db = new DatabaseSync(owned.path);
        try { db.exec('PRAGMA foreign_keys=OFF'); db.prepare('INSERT INTO invocations(id,run_id,worktree_id,data) VALUES (?,?,?,?)')
          .run('orphan', 'absent-run', 'worktree-1', '{}'); }
        finally { db.close(); }
      } else writeFileSync(owned.path, 'corrupt SQLite bytes');
      const before = readFileSync(owned.path);
      await assert.rejects(prepareForwardSchema(owned.root, selection, currentOwner()), /integrity|foreign|schema|file|database/i);
      assert.deepEqual(readFileSync(owned.path), before);
    } finally { owned.repository.dispose(); }
  }
});

import assert from 'node:assert/strict';
import { lstatSync, readdirSync, readFileSync, readlinkSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { DatabaseSync } from 'node:sqlite';
import { actionClosureFixture } from './cleanup-actions-public.qualification.mjs';

export async function exceptionalClosure(t, options = {}) {
  await actionClosureFixture(t, { ...options, probe: async (_child, context) => {
    const { inspectCleanupSelection } = await import('../dist/cleanup.js');
    const database = new DatabaseSync(join(context.common, 'factory/history.sqlite'), { readOnly: true });
    try {
    const rows = () => {
      const result = {};
      for (const { name } of database.prepare("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").all()) {
        const statement = database.prepare(`SELECT * FROM "${name.replaceAll('"', '""')}" ORDER BY rowid`);
        statement.setReadBigInts(true); result[name] = statement.all();
      }
      return result;
    };
    const factoryFiles = () => {
      const result = {};
      const walk = (path, relative) => {
        const info = lstatSync(path);
        if (info.isSymbolicLink()) result[relative] = ['link', readlinkSync(path)];
        else if (info.isDirectory()) for (const name of readdirSync(path).sort()) walk(join(path, name), `${relative}/${name}`);
        else result[relative] = ['file', readFileSync(path)];
      };
      walk(join(context.root, '.factory'), '.factory'); return result;
    };
    const inspect = async (selection, bounds = {}) => {
      const before = rows(), files = factoryFiles(), bytes = context.immutablePaths.map(path => [path, readFileSync(path)]);
      const result = await inspectCleanupSelection(context.root, selection, bounds);
      assert.deepEqual(rows(), before);
      assert.deepEqual(factoryFiles(), files);
      for (const [path, value] of bytes) assert.deepEqual(readFileSync(path), value);
      return result;
    };
    const select = (key, exceptional = [], reviewNonOutput = []) =>
      ({ kind: 'captures', captures: [key], exceptional, reviewNonOutput });
    const ordinary = await context.inspect();
    assert.equal(ordinary.status, 'inspectable', JSON.stringify(ordinary.blockers));
    assert.deepEqual(ordinary.blockers, []);
    assert.equal(ordinary.captures[0].disposition, 'eligible');
    const candidate = context.actionReports[0].value.approval.candidate;
    const key = { invocationId: candidate.invocationId, captureId: candidate.captureId };
    const selection = select(key, [key]);
    const result = await inspect(selection);
    assert.equal(result.status, 'inspectable', JSON.stringify(result.blockers));
    assert.equal(result.captures[0].disposition, 'exceptional-impact');
    assert.equal(result.captures[0].verificationWillFail, true);
    assert.equal(result.captures[0].requiresExplicitConfirmation, true);
    const expected = context.closure.headers.filter(row => row.channel === 'report')
      .map(row => ({ invocationId: row.invocationId, captureId: row.id }))
      .sort((a, b) => JSON.stringify([a.invocationId, a.captureId]).localeCompare(JSON.stringify([b.invocationId, b.captureId])));
    assert.equal(expected.length, 12);
    const actual = [...result.captures[0].affectedReports]
      .sort((a, b) => JSON.stringify([a.invocationId, a.captureId]).localeCompare(JSON.stringify([b.invocationId, b.captureId])));
    assert.deepEqual(actual, expected);
    assert.deepEqual(result.captures[0].affectedAttempts, []);
    const evaluations = context.closure.headers.filter(row => row.channel === 'report')
      .map(row => context.closure.payloads.get(row.id)).map(text => JSON.parse(text))
      .filter(value => Object.hasOwn(value, 'assessment')).map(value => value.assessment).sort();
    assert.deepEqual(evaluations, ['inconclusive', 'supported', 'unsupported']);

    const command = context.closure.attempts.find(row => row.operationKey === 'variants');
    assert.ok(command);
    const commandHeader = context.closure.headers.find(row => row.attemptId === command.id && row.channel === 'stderr');
    assert.ok(commandHeader);
    const commandKey = { invocationId: command.invocationId, captureId: commandHeader.id };
    const commandImpact = await inspect(select(commandKey, [commandKey]));
    assert.equal(commandImpact.status, 'inspectable', JSON.stringify(commandImpact.blockers));
    assert.equal(commandImpact.captures[0].disposition, 'exceptional-impact');
    assert.deepEqual(commandImpact.captures[0].affectedReports, expected);
    assert.deepEqual(commandImpact.captures[0].affectedAttempts,
      [{ invocationId: command.invocationId, attemptId: command.id }]);
    assert.equal(commandImpact.captures[0].verificationWillFail, true);
    assert.equal(commandImpact.captures[0].requiresExplicitConfirmation, true);

    const report = expected[0];
    const rootInput = context.closure.headers.find(row => row.channel === 'context' && row.attemptId === null);
    assert.ok(rootInput);
    for (const permanent of [report, { invocationId: rootInput.invocationId, captureId: rootInput.id }]) {
      const protectedResult = await inspect(select(permanent, [permanent]));
      assert.equal(protectedResult.captures[0].disposition, 'protected');
      assert.deepEqual(protectedResult.captures[0].affectedReports, []);
      assert.equal(protectedResult.captures[0].verificationWillFail, false);
    }
    for (const invalid of [
      select(key, [key], [key]),
      select(key, [commandKey]),
      select(key, [key, key]),
    ]) {
      const blocked = await inspect(invalid);
      assert.equal(blocked.status, 'blocked');
      assert.ok(blocked.blockers.some(row => row.code === 'malformed'));
    }
    const ordinaryExceptional = await inspect(select(context.selected, [context.selected]));
    assert.equal(ordinaryExceptional.status, 'blocked');
    assert.ok(ordinaryExceptional.blockers.some(row => row.code === 'opaque'));
    for (const bounds of [{ stateBytes: 1 }, { pages: 1 }, { sourceRows: 1 }, { payloadBytes: 1 }, { nodes: 1 }, { edges: 1 }, { reports: 1 }]) {
      const blocked = await inspect(selection, bounds);
      assert.equal(blocked.status, 'blocked');
      assert.ok(blocked.blockers.some(row => row.code === 'limit'), JSON.stringify(blocked.blockers));
      assert.ok(blocked.captures.every(row => row.disposition !== 'exceptional-impact'));
    }

    const { openRepositoryStore } = await import('../dist/store.js');
    const { currentOwner } = await import('../dist/native/process.js');
    const recorder = openRepositoryStore(context.common);
    let looseKey;
    try {
      const run = await recorder.createRun();
      const worktree = await recorder.registerWorktree({ path: context.root, registration: 'action-fixture' });
      const invocation = await recorder.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: currentOwner() });
      const input = await recorder.createCapture({ invocationId: invocation.id, channel: 'context' });
      await recorder.appendCapture({ id: input.id, chunks: [{ sequence: 1, text: '{"inputs":{},"question":null,"contexts":[]}' }], state: 'complete' });
      await recorder.saveInvocationMetadata(invocation.id, { settings: {}, workflow: '.factory/workflows/unreferenced-event.ts', selectedCommit: null,
        inputCaptureId: input.id, question: null, contexts: [] });
      await recorder.activateInvocation(invocation.id);
      const event = await recorder.createCapture({ invocationId: invocation.id, channel: 'event' });
      await recorder.appendCapture({ id: event.id, chunks: [{ sequence: 1, text: 'unreferenced event payload' }], state: 'complete' });
      await recorder.stopAdmissions(invocation.id);
      await recorder.finalizeInvocation({ id: invocation.id, outcome: 'succeeded', cleanup: 'complete', claimId: invocation.claim.id, token: invocation.claim.token });
      looseKey = { invocationId: invocation.id, captureId: event.id };
    } finally { recorder.close(); }
    const unreviewed = await inspect(select(looseKey));
    assert.equal(unreviewed.status, 'inspectable', JSON.stringify(unreviewed.blockers));
    assert.equal(unreviewed.captures[0].disposition, 'protected');
    const reviewed = await inspect(select(looseKey, [], [looseKey]));
    assert.equal(reviewed.status, 'inspectable', JSON.stringify(reviewed.blockers));
    assert.equal(reviewed.captures[0].disposition, 'eligible');
    assert.equal(reviewed.captures[0].requiresExplicitConfirmation, true);
    assert.deepEqual(reviewed.captures[0].affectedReports, []);

    const writable = new DatabaseSync(join(context.common, 'factory/history.sqlite'));
    const preparation = context.actionReports.find(row => row.value.kind === 'adoption-preparation');
    const applied = context.actionReports.find(row => row.value.kind === 'adoption' && row.value.status === 'applied');
    assert.ok(preparation && applied);
    const edit = (id, transform) => {
      const original = writable.prepare('SELECT sequence FROM captures WHERE id=?').get(id).sequence;
      const chunks = writable.prepare('SELECT rowid,sequence,text FROM capture_chunks WHERE capture_id=? ORDER BY sequence').all(id);
      const changed = JSON.stringify(transform(JSON.parse(chunks.map(row => row.text).join(''))));
      const parts = []; let part = '', bytes = 0;
      for (const character of changed) { const size = Buffer.byteLength(character);
        if (bytes + size > 4096) { parts.push(part); part = ''; bytes = 0; }
        part += character; bytes += size; }
      if (part) parts.push(part);
      writable.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(id);
      parts.forEach((text, index) => writable.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,?,?)').run(id, index + 1, text));
      writable.prepare('UPDATE captures SET sequence=? WHERE id=?').run(parts.length, id);
      return () => {
        writable.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(id);
        for (const row of chunks) writable.prepare('INSERT INTO capture_chunks(rowid,capture_id,sequence,text) VALUES (?,?,?,?)').run(row.rowid, id, row.sequence, row.text);
        writable.prepare('UPDATE captures SET sequence=? WHERE id=?').run(original, id);
        assert.deepEqual(writable.prepare('SELECT rowid,sequence,text FROM capture_chunks WHERE capture_id=? ORDER BY sequence').all(id), chunks);
      };
    };
    try {
      for (const [parent, transform, code] of [
        [preparation, value => { value.approval.extra = true; return value; }, 'opaque'],
        [applied, value => { value.preparationReference.captureId = 'absent-preparation'; return value; }, 'missing'],
        [applied, value => { value.preparationReference.invocationId = value.approval.extraction.invocationId; return value; }, 'foreign'],
        [applied, value => { value.preparationReference = applied.reference; return value; }, 'cycle'],
      ]) {
        const restore = edit(parent.reference.captureId, transform);
        try { const blocked = await inspect(selection);
          assert.equal(blocked.status, 'blocked');
          assert.ok(blocked.blockers.some(row => row.code === code), JSON.stringify(blocked.blockers));
          assert.ok(blocked.captures.every(row => row.disposition !== 'exceptional-impact'));
        } finally { restore(); }
      }
      for (const state of ['partial', 'pruned']) {
        writable.prepare('UPDATE captures SET state=? WHERE id=?').run(state, preparation.reference.captureId);
        try { const blocked = await inspect(selection);
          assert.equal(blocked.status, 'blocked');
          assert.ok(blocked.blockers.some(row => row.code === (state === 'pruned' ? 'pruned' : 'partial')));
          assert.ok(blocked.captures.every(row => row.disposition !== 'exceptional-impact'));
        } finally { writable.prepare("UPDATE captures SET state='complete' WHERE id=?").run(preparation.reference.captureId); }
      }
    } finally { writable.close(); }
    } finally { database.close(); }
  } });
}

if (process.argv[1] === fileURLToPath(import.meta.url)) test('exceptional selection reports the genuine action chain', t => exceptionalClosure(t));

import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lstatSync, readdirSync, readFileSync, readlinkSync } from 'node:fs';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';
import { actionClosureFixture } from '../qualification/cleanup-actions-public.qualification.mjs';
import { inspectCleanupSelection } from '../dist/cleanup.js';

function retainedBytes(context) {
  const database = new DatabaseSync(join(context.common, 'factory/history.sqlite'), { readOnly: true });
  const rows = {};
  try {
    for (const { name } of database.prepare("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").all()) {
      const statement = database.prepare(`SELECT * FROM "${name.replaceAll('"', '""')}" ORDER BY rowid`);
      statement.setReadBigInts(true); rows[name] = statement.all();
    }
  } finally { database.close(); }
  const files = {};
  function walk(path, relative) {
    const info = lstatSync(path);
    if (info.isSymbolicLink()) files[relative] = ['link', readlinkSync(path)];
    else if (info.isDirectory()) for (const name of readdirSync(path).sort()) walk(join(path, name), `${relative}/${name}`);
    else files[relative] = ['file', readFileSync(path)];
  }
  walk(join(context.root, '.factory'), '.factory');
  for (const path of context.immutablePaths) files[path] = ['file', readFileSync(path)];
  return { rows, files };
}

test('uninstalled genuine action history cannot acquire cleanup authority', t => actionClosureFixture(t, {
  installed: false,
  probe: async (_child, context) => {
    assert.equal(context.closure.graph.status, 'complete', JSON.stringify(context.closure.graph.blockers));
    const candidate = context.actionReports[0].value.approval.candidate;
    const selections = [
      { kind: 'captures', captures: [context.selected], exceptional: [], reviewNonOutput: [] },
      { kind: 'captures', captures: [{ invocationId: candidate.invocationId, captureId: candidate.captureId }],
        exceptional: [{ invocationId: candidate.invocationId, captureId: candidate.captureId }], reviewNonOutput: [] },
    ];
    for (const selection of selections) {
      const before = retainedBytes(context);
      const result = await inspectCleanupSelection(context.root, selection);
      assert.deepEqual(retainedBytes(context), before);
      assert.equal(result.status, 'blocked');
      assert.equal(result.snapshotSha256, null);
      assert.equal(result.impactSha256, null);
      assert.ok(result.blockers.some(blocker => blocker.code === 'unassessed-recovery' && blocker.node === null), JSON.stringify(result.blockers));
      assert.equal(result.captures.length, 1);
      const row = result.captures[0], key = selection.captures[0];
      const payload = context.closure.payloads.get(key.captureId);
      assert.deepEqual(row.key, key);
      assert.equal(row.logicalBytes, String(Buffer.byteLength(payload)));
      assert.equal(row.payloadSha256, createHash('sha256').update(payload).digest('hex'));
      assert.notEqual(row.disposition, 'eligible');
      assert.notEqual(row.disposition, 'exceptional-impact');
      assert.deepEqual(row.affectedReports, []);
      assert.deepEqual(row.affectedAttempts, []);
      assert.equal(row.verificationWillFail, false);
      assert.equal(row.requiresExplicitConfirmation, false);
    }
    assert.ok(context.closure.graph.protected.some(node => node.kind === 'capture' && node.captureId === candidate.captureId));
    for (const report of context.closure.headers.filter(header => header.channel === 'report'))
      assert.ok(context.closure.graph.protected.some(node => node.kind === 'capture' && node.captureId === report.id));
  },
}));

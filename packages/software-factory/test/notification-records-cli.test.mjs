import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { DatabaseSync } from 'node:sqlite';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { sendInitialNotification } from '../dist/notifications.js';
import { openRepositoryStore } from '../dist/store.js';
import { createNotificationFixture as fixture } from './notification-repository-fixture.mjs';

test('ordinary success stays quiet and an unbound development sender is explicitly unavailable', async () => {
  const success = await fixture(`export async function run(context) { await context.progress('complete'); }`);
  const issue = await fixture(`export async function run(context) { await context.needsInput('Choose', 'A choice is required'); }`);
  try {
    let sends = 0;
    const quiet = await success.run({ notificationSender: async () => { sends++; return { state: 'submitted', cleanup: 'complete' }; } });
    assert.equal(quiet.exitCode, 0);
    assert.equal(quiet.notification, null);
    assert.equal(sends, 0);
    const unavailable = await issue.run();
    assert.equal(unavailable.exitCode, 2);
    assert.equal(unavailable.notification.state, 'failed');
    assert.equal(unavailable.notification.reason, 'unbound_sender');
    const reopened = openRepositoryStore(issue.common);
    try {
      assert.deepEqual(reopened.readHistory(unavailable.invocationId).notifications, [unavailable.notification]);
      const maintenance = await reopened.claimResource({ kind: 'maintenance', owner: { host: 'fixture', pid: process.pid, start: null } });
      await reopened.releaseClaim({ claimId: maintenance.id, token: maintenance.token, basis: 'quiescent' });
    }
    finally { reopened.close(); }
    const cli = fileURLToPath(new URL('../dist/cli.js', import.meta.url));
    const cliResult = spawnSync(process.execPath, [cli, 'invoke', '--repository', issue.path, '--workflow', '.factory/workflows/notice.ts', '--input', issue.input, '--new-worktree', '--json'], { encoding: 'utf8', timeout: 10000 });
    assert.equal(cliResult.status, 2, cliResult.stderr);
    const summary = JSON.parse(cliResult.stdout);
    assert.equal(summary.notification.reason, 'unbound_sender');
    const cliHistory = spawnSync(process.execPath, [cli, 'history', '--repository', issue.path, '--invocation', summary.invocationId, '--json'], { encoding: 'utf8', timeout: 10000 });
    assert.equal(cliHistory.status, 0, cliHistory.stderr);
    assert.deepEqual(JSON.parse(cliHistory.stdout).notifications, [summary.notification]);
    assert.equal(sends, 0, 'opening saved history must never replay a notice');
  } finally { success.dispose(); issue.dispose(); }
});

test('a failed result write preserves the reservation and owner for explicit recovery', async () => {
  const repo = await fixture(`export async function run(context) { await context.needsInput('Choose', 'A choice is required'); }`);
  try {
    const result = await repo.run({ notificationSender: async () => {
      const database = new DatabaseSync(join(repo.common, 'factory/history.sqlite'));
      try { database.exec("CREATE TRIGGER refuse_notification_result BEFORE UPDATE ON notification_deliveries BEGIN SELECT RAISE(FAIL, 'result write refused'); END"); }
      finally { database.close(); }
      return { state: 'submitted', cleanup: 'complete' };
    } });
    assert.equal(result.outcome, 'needs_input');
    assert.equal(result.cleanup, 'complete');
    assert.equal(result.exitCode, 2);
    assert.equal(result.notification.state, 'unknown');
    assert.equal(result.notification.reason, 'submission_unconfirmed');
    const store = openRepositoryStore(repo.common);
    try {
      const history = store.readHistory(result.invocationId);
      assert.equal(history.captures.filter(capture => capture.channel === 'request').length, 1);
      assert.deepEqual(history.notifications, [result.notification]);
      const [claim] = store.inspectOwners().filter(owner => owner.invocationId === result.invocationId);
      assert.ok(claim);
      await assert.rejects(store.claimResource({ kind: 'maintenance', owner: { host: 'fixture', pid: process.pid, start: null } }), /active or uncertain owner blocks maintenance/);
      let duplicateSends = 0;
      assert.deepEqual(await sendInitialNotification(store, result.invocationId, async () => { duplicateSends++; return { state: 'submitted', cleanup: 'complete' }; }), result.notification);
      assert.equal(duplicateSends, 0);
      await store.clearOwner({ claimId: claim.id, token: claim.token, operatorConfirmed: true, note: 'Fixture inspected sender and result write', inspection: 'not_live' });
      const maintenance = await store.claimResource({ kind: 'maintenance', owner: { host: 'fixture', pid: process.pid, start: null } });
      await store.releaseClaim({ claimId: maintenance.id, token: maintenance.token, basis: 'quiescent' });
    } finally { store.close(); }
  } finally { repo.dispose(); }
});

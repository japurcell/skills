import test from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { join } from 'node:path';
import { sendInitialNotification } from '../dist/notifications.js';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';
import { createNotificationFixture as fixture } from './notification-repository-fixture.mjs';

test('one initial combined issue is saved after finalization and submitted only once', async () => {
  const repo = await fixture(`export async function run(context) { await context.needsInput('Choose target', 'A target is required'); }`);
  const calls = [];
  try {
    const result = await repo.run({ notificationSender: async message => {
      calls.push(message);
      const saved = openRepositoryStore(repo.common);
      try {
        const invocation = saved.readNotificationDeliveries(saved.readInvocations().invocations[0].id)[0];
        assert.equal(saved.readInvocation(invocation.invocationId).stage, 'finalized');
        assert.equal(invocation.state, 'unknown', 'submission must follow the durable reservation');
        await assert.rejects(saved.claimResource({ kind: 'maintenance', owner: { host: 'fixture', pid: process.pid, start: null } }), /active or uncertain owner blocks maintenance/);
      } finally { saved.close(); }
      return { state: 'submitted', cleanup: 'complete' };
    } });
    assert.equal(result.outcome, 'needs_input');
    assert.equal(result.exitCode, 2);
    assert.equal(calls.length, 1);
    assert.match(calls[0].body, /1 question needs input; run needs input/);
    assert.doesNotMatch(JSON.stringify(calls[0]), /Choose target|A target is required/);
    const store = openRepositoryStore(repo.common);
    try {
      const history = store.readHistory(result.invocationId);
      assert.equal(history.invocation.stage, 'finalized');
      assert.equal(history.captures.filter(capture => capture.channel === 'request').length, 1);
      assert.equal(history.notifications.length, 1);
      assert.equal(history.notifications[0].id, `${result.invocationId}:initial`);
      assert.equal(history.notifications[0].state, 'submitted');
      assert.equal(history.notifications[0].issues.questions, 1);
      assert.equal(history.notifications[0].issues.outcome, 'needs_input');
      assert.equal(history.notifications[0].visibleDelivery, false);
      assert.deepEqual(result.notification, history.notifications[0]);
      const duplicate = await sendInitialNotification(store, result.invocationId, async () => { calls.push('duplicate'); return { state: 'submitted', cleanup: 'complete' }; });
      assert.deepEqual(duplicate, result.notification);
      assert.equal(calls.length, 1, 'the same delivery identity must never submit twice');
      const maintenance = await store.claimResource({ kind: 'maintenance', owner: { host: 'fixture', pid: process.pid, start: null } });
      await store.releaseClaim({ claimId: maintenance.id, token: maintenance.token, basis: 'quiescent' });
    } finally { store.close(); }
  } finally { repo.dispose(); }
});

test('sender rejection and bounded uncertainty keep the workflow result and saved question', async () => {
  const repo = await fixture(`export async function run(context) { await context.needsInput('Choose', 'A choice is required'); }`);
  try {
    const rejected = await repo.run({ notificationSender: async () => { throw new Error('maybe sent'); } });
    assert.equal(rejected.exitCode, 2);
    assert.equal(rejected.notification.state, 'unknown');
    assert.equal(rejected.notification.cleanup, 'unknown');
    const uncertain = openRepositoryStore(repo.common);
    try {
      assert.equal(uncertain.inspectOwners().filter(claim => claim.invocationId === rejected.invocationId).length, 1);
      await assert.rejects(uncertain.claimResource({ kind: 'maintenance', owner: { host: 'fixture', pid: process.pid, start: null } }), /active or uncertain owner blocks maintenance/);
    } finally { uncertain.close(); }
    const timeout = await repo.run({ notificationSender: async () => ({ state: 'timed_out', reason: 'deadline_exceeded', cleanup: 'complete' }) });
    assert.equal(timeout.exitCode, 2);
    assert.equal(timeout.notification.state, 'timed_out');
    assert.equal(timeout.notification.reason, 'deadline_exceeded');
    const reportedUnknown = await repo.run({ notificationSender: async () => ({ state: 'unknown', reason: 'cleanup_unconfirmed', cleanup: 'unknown' }) });
    assert.equal(reportedUnknown.exitCode, 2);
    assert.equal(reportedUnknown.notification.cleanup, 'unknown');
    const store = openRepositoryStore(repo.common);
    try {
      for (const result of [rejected, timeout, reportedUnknown]) {
        const history = store.readHistory(result.invocationId);
        assert.equal(history.invocation.outcome, 'needs_input');
        assert.equal(history.captures.filter(capture => capture.channel === 'request').length, 1);
        assert.deepEqual(history.notifications, [result.notification]);
      }
      assert.equal(store.readNotificationDeliveries(rejected.invocationId)[0].id, `${rejected.invocationId}:initial`);
      assert.equal(store.inspectOwners().filter(claim => claim.invocationId === reportedUnknown.invocationId).length, 1);
      assert.equal(store.inspectOwners().filter(claim => claim.invocationId === timeout.invocationId).length, 0, 'a known-clean sender releases its claim');
      await assert.rejects(store.claimResource({ kind: 'maintenance', owner: { host: 'fixture', pid: process.pid, start: null } }), /active or uncertain owner blocks maintenance/);
    } finally { store.close(); }
  } finally { repo.dispose(); }
});

test('a version 4 store is refused without mutation or automatic migration', async () => {
  const repo = createRepository();
  try {
    const common = join(repo.path, '.git');
    const initialized = await initializeRepositoryStore(common, { release: 'fixture' }); initialized.close();
    const database = new DatabaseSync(join(common, 'factory/history.sqlite'));
    database.exec('PRAGMA user_version=4');
    const before = database.prepare("SELECT name,sql FROM sqlite_master WHERE type='table' ORDER BY name").all();
    database.close();
    assert.throws(() => openRepositoryStore(common), /incompatible schema; explicit forward maintenance required/);
    const after = new DatabaseSync(join(common, 'factory/history.sqlite'));
    try {
      assert.equal(after.prepare('PRAGMA user_version').get().user_version, 4);
      assert.deepEqual(after.prepare("SELECT name,sql FROM sqlite_master WHERE type='table' ORDER BY name").all(), before);
    } finally { after.close(); }
  } finally { repo.dispose(); }
});

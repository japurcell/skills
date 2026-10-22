import assert from 'node:assert/strict';
import test from 'node:test';
import { sendInitialNotification } from '../dist/notifications.js';
import { openRepositoryStore } from '../dist/store.js';
import { createNotificationFixture as fixture } from './notification-repository-fixture.mjs';

test('a sender that never settles is bounded and remains unknown without changing exit status', async () => {
  const repo = await fixture(`export async function run(context) { await context.needsInput('Choose', 'A choice is required'); }`);
  try {
    let settleSender;
    const started = performance.now();
    const result = await repo.run({ notificationSender: () => new Promise(resolve => { settleSender = resolve; }) });
    const elapsed = performance.now() - started;
    assert.equal(result.exitCode, 2);
    assert.equal(result.notification.state, 'unknown');
    assert.equal(result.notification.reason, 'cleanup_unconfirmed');
    assert.equal(result.notification.cleanup, 'unknown');
    assert.ok(elapsed >= 5000 && elapsed < 9000, `sender bound took ${elapsed}ms`);
    const store = openRepositoryStore(repo.common);
    try {
      assert.deepEqual(store.readHistory(result.invocationId).notifications, [result.notification]);
      assert.equal(store.inspectOwners().filter(claim => claim.invocationId === result.invocationId).length, 1);
      await assert.rejects(store.claimResource({ kind: 'maintenance', owner: { host: 'fixture', pid: process.pid, start: null } }), /active or uncertain owner blocks maintenance/);
      settleSender({ state: 'submitted', cleanup: 'complete' });
      await new Promise(resolve => setImmediate(resolve));
      assert.deepEqual(store.readHistory(result.invocationId).notifications, [result.notification], 'late sender completion must not rewrite the record');
      assert.equal(store.inspectOwners().filter(claim => claim.invocationId === result.invocationId).length, 1, 'late sender completion must not release ownership');
      let duplicateSends = 0;
      assert.deepEqual(await sendInitialNotification(store, result.invocationId, async () => { duplicateSends++; return { state: 'submitted', cleanup: 'complete' }; }), result.notification);
      assert.equal(duplicateSends, 0, 'reading an uncertain reservation must not replay it');
    }
    finally { store.close(); }
  } finally { repo.dispose(); }
});

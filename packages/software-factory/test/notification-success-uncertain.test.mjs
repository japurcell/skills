import assert from 'node:assert/strict';
import test from 'node:test';
import { sendInitialNotification } from '../dist/notifications.js';
import { openRepositoryStore } from '../dist/store.js';
import { createNotificationFixture as fixture } from './notification-repository-fixture.mjs';

test('uncertain opt-in success notice retains its original owner and saved success', async () => {
  const repo = await fixture(`export async function run(context) { await context.progress('complete'); }`);
  try {
    const store = openRepositoryStore(repo.common);
    await store.saveNotificationPreferences({ successNotices: true, reminders: false }); store.close();
    let settleSender;
    const result = await repo.run({ notificationSender: () => new Promise(resolve => { settleSender = resolve; }) });
    assert.equal(result.outcome, 'succeeded'); assert.equal(result.exitCode, 0);
    assert.equal(result.notification.state, 'unknown'); assert.equal(result.notification.cleanup, 'unknown');
    const saved = openRepositoryStore(repo.common);
    try {
      assert.equal(saved.readInvocation(result.invocationId).outcome, 'succeeded');
      assert.equal(saved.inspectOwners().filter(claim => claim.invocationId === result.invocationId).length, 1);
      await saved.saveNotificationPreferences({ successNotices: false, reminders: false });
      assert.deepEqual(await sendInitialNotification(saved, result.invocationId, async () => { throw new Error('resent'); }), result.notification);
      settleSender({ state: 'submitted', cleanup: 'complete' });
      await new Promise(resolve => setImmediate(resolve));
      assert.deepEqual(saved.readHistory(result.invocationId).notifications, [result.notification]);
    } finally { saved.close(); }
  } finally { repo.dispose(); }
});

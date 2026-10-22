import test from 'node:test';
import assert from 'node:assert/strict';
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { sendInitialNotification } from '../dist/notifications.js';
import { openRepositoryStore } from '../dist/store.js';
import { createNotificationFixture as fixture } from './notification-repository-fixture.mjs';

test('opted-in successful invocation saves one bounded notice without changing its outcome', async () => {
  const repo = await fixture(`export async function run(context) { await context.progress('complete'); }`);
  try {
    const store = openRepositoryStore(repo.common);
    await store.saveNotificationPreferences({ successNotices: true, reminders: false }); store.close();
    let sends = 0;
    const result = await repo.run({ notificationSender: async message => {
      sends++;
      assert.deepEqual(message, { title: 'Software Factory completed', body: '1 run succeeded' });
      const saved = openRepositoryStore(repo.common);
      try {
        const invocationId = saved.readInvocations().invocations[0].id;
        assert.equal(saved.readInvocation(invocationId).outcome, 'succeeded');
        assert.equal(saved.inspectOwners().filter(claim => claim.invocationId === invocationId).length, 1);
        await saved.saveNotificationPreferences({ successNotices: false, reminders: false });
      } finally { saved.close(); }
      return { state: 'failed', reason: 'delivery_refused', cleanup: 'complete' };
    } });
    assert.equal(result.outcome, 'succeeded'); assert.equal(result.exitCode, 0);
    assert.equal(result.notification.state, 'failed'); assert.equal(sends, 1);
    const reopened = openRepositoryStore(repo.common);
    try {
      assert.deepEqual(reopened.readHistory(result.invocationId).notifications, [result.notification]);
      assert.equal(reopened.inspectOwners().filter(claim => claim.invocationId === result.invocationId).length, 0);
      assert.deepEqual(await sendInitialNotification(reopened, result.invocationId, async () => { sends++; return { state: 'submitted', cleanup: 'complete' }; }), result.notification);
      assert.equal(sends, 1);
    } finally { reopened.close(); }
    const quiet = await repo.run({ notificationSender: async () => { sends++; return { state: 'submitted', cleanup: 'complete' }; } });
    assert.equal(quiet.outcome, 'succeeded'); assert.equal(quiet.notification, null); assert.equal(sends, 1);
    const quietStore = openRepositoryStore(repo.common);
    try {
      assert.equal(quietStore.inspectOwners().filter(claim => claim.invocationId === quiet.invocationId).length, 0);
      await quietStore.saveNotificationPreferences({ successNotices: true, reminders: false });
    } finally { quietStore.close(); }
    const submitted = await repo.run({ notificationSender: async () => { sends++; return { state: 'submitted', cleanup: 'complete' }; } });
    assert.equal(submitted.outcome, 'succeeded'); assert.equal(submitted.notification.state, 'submitted'); assert.equal(sends, 2);
  } finally { repo.dispose(); }
});

test('question, independent failure and unknown cleanup survive unavailable delivery', async () => {
  const repo = await fixture(`import { existsSync } from 'node:fs';
  export async function run(context, inputs) {
    const launched = async () => { for (let n=0;n<300;n++) { if (existsSync(inputs.marker)) return; await new Promise(resolve => setTimeout(resolve,10)); } throw new Error('peer did not launch'); };
    void context.command('orphan-peer', { argv: [process.execPath, '-e', 'const {spawn}=require("node:child_process");spawn(process.execPath,["-e","setInterval(()=>{},1000)"],{stdio:"ignore"});require("node:fs").writeFileSync(process.argv[1],"ready");process.exit(0)', inputs.marker], env: {} });
    void context.scope('independent-failure', async () => { await launched(); await new Promise(resolve => setTimeout(resolve, 120)); throw new Error('independent failure'); });
    await launched(); await new Promise(resolve => setTimeout(resolve, 30));
    await context.needsInput('Choose', 'Question must survive');
  }`);
  writeFileSync(repo.input, JSON.stringify({ marker: join(repo.common, 'peer-launched') }));
  let group;
  try {
    const result = await repo.run({ shutdownGraceMs: 100 });
    assert.equal(result.outcome, 'failed');
    assert.equal(result.cleanup, 'unknown');
    assert.equal(result.exitCode, 1);
    assert.equal(result.notification.state, 'failed');
    assert.equal(result.notification.reason, 'unbound_sender');
    const store = openRepositoryStore(repo.common);
    try {
      const history = store.readHistory(result.invocationId);
      group = history.attempts.find(attempt => attempt.operationKey === 'orphan-peer')?.owner?.pid;
      assert.equal(history.captures.filter(capture => capture.channel === 'request').length, 1);
      assert.equal(history.invocation.cleanup, 'unknown');
      assert.deepEqual(history.notifications[0].issues, { outcome: 'failed', cleanup: 'unknown', questions: 1 });
    } finally { store.close(); }
  } finally {
    if (group) { try { process.kill(-group, 'SIGKILL'); } catch {} }
    repo.dispose();
  }
});

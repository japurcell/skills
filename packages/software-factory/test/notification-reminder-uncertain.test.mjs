import assert from 'node:assert/strict';
import test from 'node:test';
import { join } from 'node:path';
import { createRepository } from './fixtures/repository.mjs';
import { initializeRepositoryStore } from '../dist/store.js';
import { startObservationHost } from '../dist/dashboard.js';

test('a five-second nonsettling sender retains the group and ignores late acceptance', async () => {
  const repo = createRepository();
  const store = await initializeRepositoryStore(join(repo.path, '.git'), { release: 'fixture' });
  let host, callback, finish;
  const pending = new Promise(resolve => { finish = resolve; });
  const scheduler = { setTimeout(task, milliseconds) { assert.equal(milliseconds, 15 * 60 * 1000); callback = task; return 1; }, clearTimeout() { callback = undefined; } };
  try {
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repo.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: null } });
    await store.activateInvocation(invocation.id);
    await store.finalizeInvocation({ id: invocation.id, outcome: 'failed', cleanup: 'complete', claimId: invocation.claim.id, token: invocation.claim.token });
    host = await startObservationHost({ store, reminderScheduler: scheduler, reminderSender: async () => pending });
    const response = await fetch(host.url + '/api/notifications/preferences', { method: 'POST',
      headers: { Authorization: 'Bearer ' + host.sessionToken, Origin: host.url, 'Content-Type': 'application/json' },
      body: JSON.stringify({ successNotices: false, reminders: true }) });
    assert.equal(response.status, 200);
    await callback();
    const saved = store.readReminderGroups().groups[0];
    assert.equal(saved.state, 'unknown');
    assert.equal(saved.cleanup, 'unknown');
    assert.equal(saved.reason, 'cleanup_unconfirmed');
    finish({ state: 'submitted', cleanup: 'complete' });
    await Promise.resolve();
    assert.deepEqual(store.readReminderGroups().groups[0], saved);
    await assert.rejects(host.close(), /reminder cleanup or recording unknown/);
    assert.ok(store.readDashboardClaim()); host = undefined;
  } finally { finish?.({ state: 'submitted', cleanup: 'complete' }); store.close(); repo.dispose(); }
});

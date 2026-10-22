import assert from 'node:assert/strict';
import test from 'node:test';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { randomUUID } from 'node:crypto';
import { createRepository } from './fixtures/repository.mjs';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { startObservationHost } from '../dist/dashboard.js';

function clock() {
  const jobs = new Map(); let next = 0;
  return {
    jobs,
    setTimeout(callback, milliseconds) { const id = ++next; jobs.set(id, { callback, milliseconds }); return id; },
    clearTimeout(id) { jobs.delete(id); },
    async tick() { const [id, job] = jobs.entries().next().value ?? []; assert.ok(job, 'a reminder tick is scheduled'); jobs.delete(id); await job.callback(); },
  };
}

async function fixture() {
  const repo = createRepository();
  const store = await initializeRepositoryStore(join(repo.path, '.git'), { release: 'fixture' });
  const run = await store.createRun();
  const worktree = await store.registerWorktree({ path: repo.path, registration: 'fixture' });
  async function finalize(outcome) {
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: null } });
    await store.activateInvocation(invocation.id);
    await store.finalizeInvocation({ id: invocation.id, outcome, cleanup: 'complete', claimId: invocation.claim.id, token: invocation.claim.token });
    return invocation.id;
  }
  return { repo, store, finalize, dispose() { store.close(); repo.dispose(); } };
}

async function write(host, body) {
  const response = await fetch(host.url + '/api/notifications/preferences', { method: 'POST', headers: { Authorization: 'Bearer ' + host.sessionToken, Origin: host.url, 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  assert.equal(response.status, 200);
  return response.json();
}

test('overlapping preference saves follow request order and leave the final timer consistent', async () => {
  for (const [heldValue, followingValue] of [[true, false], [false, true]]) {
    const f = await fixture(); const scheduler = clock(); let host, entered, release;
    const started = new Promise(resolve => { entered = resolve; });
    const gate = new Promise(resolve => { release = resolve; });
    let holdNext = false;
    try {
      host = await startObservationHost({ store: f.store, reminderScheduler: scheduler,
        notificationWrite: async (operation, body) => {
          if (operation !== 'preferences') return f.store.acknowledgeNotification(body);
          if (holdNext && body.reminders === heldValue) { holdNext = false; entered(); await gate; }
          return f.store.saveNotificationPreferences(body);
        },
      });
      await write(host, { successNotices: false, reminders: true });
      holdNext = true;
      const first = write(host, { successNotices: false, reminders: heldValue });
      await started;
      const second = write(host, { successNotices: false, reminders: followingValue });
      await Promise.race([second, new Promise(resolve => setTimeout(resolve, 100))]);
      release();
      await Promise.all([first, second]);
      assert.equal(f.store.readNotificationPreferences().reminders, followingValue);
      assert.equal(scheduler.jobs.size, followingValue ? 1 : 0);
      if (followingValue) assert.equal([...scheduler.jobs.values()][0].milliseconds, 15 * 60 * 1000);
    } finally { release?.(); await host?.close(); f.dispose(); }
  }
});

test('reminders stay off until enabled and wait a full host interval before one grouped send', async () => {
  const f = await fixture(); const scheduler = clock(); const sent = []; let host;
  try {
    await f.finalize('failed');
    host = await startObservationHost({ store: f.store, reminderScheduler: scheduler, reminderSender: async message => { sent.push(message); return { state: 'submitted', cleanup: 'complete' }; } });
    assert.equal(scheduler.jobs.size, 0);
    await write(host, { successNotices: false, reminders: true });
    assert.equal([...scheduler.jobs.values()][0].milliseconds, 15 * 60 * 1000);
    await write(host, { successNotices: true, reminders: true });
    assert.equal(scheduler.jobs.size, 1);
    await scheduler.tick();
    assert.deepEqual(sent, [{ title: 'Software Factory needs attention', body: '1 run needs attention' }]);
    assert.equal(f.store.readReminderGroups({ limit: 20 }).groups[0].state, 'submitted');
  } finally { await host?.close(); f.dispose(); }
});

test('restart waits a fresh interval and does not replay the reserved group', async () => {
  const f = await fixture(); const scheduler = clock(); let host;
  try {
    await f.finalize('failed');
    await f.store.saveNotificationPreferences({ successNotices: false, reminders: true });
    host = await startObservationHost({ store: f.store, reminderScheduler: scheduler });
    assert.equal(scheduler.jobs.size, 1);
    assert.equal([...scheduler.jobs.values()][0].milliseconds, 15 * 60 * 1000);
    await host.close(); host = undefined;
    assert.equal(scheduler.jobs.size, 0);
    const next = clock();
    host = await startObservationHost({ store: f.store, reminderScheduler: next });
    assert.equal([...next.jobs.values()][0].milliseconds, 15 * 60 * 1000);
    await next.tick();
    assert.equal(f.store.readReminderGroups({ limit: 20 }).groups[0].reason, 'unbound_sender');
  } finally { await host?.close(); f.dispose(); }
});

test('one group selects at most 100 unacknowledged finalized issues and reports truncation', async () => {
  const f = await fixture(); const scheduler = clock(); const sent = []; let host;
  try {
    const ignored = await f.finalize('succeeded');
    const acknowledged = await f.finalize('failed');
    const expected = [];
    for (let index = 0; index < 101; index++) expected.push(await f.finalize('failed'));
    await f.store.acknowledgeNotification({ invocationId: acknowledged });
    host = await startObservationHost({ store: f.store, reminderScheduler: scheduler, reminderSender: async message => { sent.push(message); return { state: 'submitted', cleanup: 'complete' }; } });
    await write(host, { successNotices: false, reminders: true });
    await scheduler.tick();
    const group = f.store.readReminderGroups().groups[0];
    assert.equal(group.count, 100);
    assert.equal(group.hasMore, true);
    assert.deepEqual(group.invocationIds, expected.slice(0, 100));
    assert.ok(!group.invocationIds.includes(ignored));
    assert.ok(!group.invocationIds.includes(acknowledged));
    assert.deepEqual(sent, [{ title: 'Software Factory needs attention', body: '100 or more runs need attention' }]);
    const unauthenticated = await fetch(host.url + '/api/notifications/reminders');
    assert.equal(unauthenticated.status, 403);
    const authenticated = await fetch(host.url + '/api/notifications/reminders?limit=1', { headers: { Authorization: 'Bearer ' + host.sessionToken } });
    assert.equal(authenticated.status, 200);
    assert.deepEqual((await authenticated.json()).groups[0].invocationIds, expected.slice(0, 100));
  } finally { await host?.close(); f.dispose(); }
});

test('disabling reminders cancels the scheduled tick and no host reuse adds a sender', async () => {
  const f = await fixture(); const scheduler = clock(); const sent = []; let host;
  try {
    await f.finalize('failed');
    host = await startObservationHost({ store: f.store, reminderScheduler: scheduler, reminderSender: async message => { sent.push(message); return { state: 'submitted', cleanup: 'complete' }; } });
    await write(host, { successNotices: false, reminders: true });
    const reused = await startObservationHost({ store: f.store, reminderScheduler: clock(), reminderSender: async () => { throw new Error('replacement sender must not run'); } });
    assert.equal(reused.reused, true);
    assert.equal(scheduler.jobs.size, 1);
    const staleTick = [...scheduler.jobs.values()][0].callback;
    await write(host, { successNotices: false, reminders: false });
    assert.equal(scheduler.jobs.size, 0);
    assert.deepEqual(sent, []);
    await write(host, { successNotices: false, reminders: true });
    assert.equal(scheduler.jobs.size, 1);
    await staleTick();
    assert.equal(sent.length, 0);
    assert.equal(scheduler.jobs.size, 1);
    await scheduler.tick();
    assert.equal(sent.length, 1);
  } finally { await host?.close(); f.dispose(); }
});

test('host close waits for an in-flight submission and then releases a clean claim', async () => {
  const f = await fixture(); const scheduler = clock(); let host, entered, finish;
  const started = new Promise(resolve => { entered = resolve; });
  const pending = new Promise(resolve => { finish = resolve; });
  try {
    await f.finalize('failed');
    host = await startObservationHost({ store: f.store, reminderScheduler: scheduler, reminderSender: async () => { entered(); return pending; } });
    await write(host, { successNotices: false, reminders: true });
    const tick = scheduler.tick(); await started;
    const closing = host.close();
    assert.ok(f.store.readDashboardClaim());
    finish({ state: 'submitted', cleanup: 'complete' });
    await tick; await closing; host = undefined;
    assert.equal(f.store.readDashboardClaim(), undefined);
    assert.equal(f.store.readReminderGroups().groups[0].state, 'submitted');
  } finally { finish?.({ state: 'submitted', cleanup: 'complete' }); await host?.close(); f.dispose(); }
});

test('rejected and malformed sender results retain the dashboard claim as unknown', async () => {
  for (const sender of [async () => { throw new Error('may have submitted'); }, async () => ({ state: 'submitted', cleanup: 'unknown' })]) {
    const f = await fixture(); const scheduler = clock(); let host;
    try {
      await f.finalize('failed');
      host = await startObservationHost({ store: f.store, reminderScheduler: scheduler, reminderSender: sender });
      await write(host, { successNotices: false, reminders: true });
      await scheduler.tick();
      const group = f.store.readReminderGroups().groups[0];
      assert.equal(group.state, 'unknown');
      assert.equal(group.cleanup, 'unknown');
      const claim = f.store.readDashboardClaim();
      await assert.rejects(f.store.releaseClaim({ claimId: claim.id, token: claim.token, basis: 'quiescent' }), /reminder cleanup or recording/);
      await assert.rejects(host.close(), /reminder cleanup or recording unknown/);
      assert.ok(f.store.readDashboardClaim()); host = undefined;
    } finally { f.dispose(); }
  }
});

test('failed result persistence retains the reserved identity and dashboard claim', async () => {
  const f = await fixture(); const scheduler = clock(); let host;
  try {
    await f.finalize('failed');
    const save = f.store.saveReminderGroupResult.bind(f.store);
    f.store.saveReminderGroupResult = async () => { throw new Error('uncertain write'); };
    host = await startObservationHost({ store: f.store, reminderScheduler: scheduler, reminderSender: async () => ({ state: 'submitted', cleanup: 'complete' }) });
    await write(host, { successNotices: false, reminders: true });
    await scheduler.tick();
    assert.equal(f.store.readReminderGroups().groups[0].state, 'reserved');
    await assert.rejects(host.close(), /reminder cleanup or recording unknown/);
    assert.ok(f.store.readDashboardClaim()); host = undefined;
    f.store.saveReminderGroupResult = save;
  } finally { f.dispose(); }
});

test('host close waits for an unsettled reminder result write', async () => {
  const f = await fixture(); const scheduler = clock(); let host, entered, release;
  const started = new Promise(resolve => { entered = resolve; });
  const gate = new Promise(resolve => { release = resolve; });
  try {
    await f.finalize('failed');
    const save = f.store.saveReminderGroupResult.bind(f.store);
    f.store.saveReminderGroupResult = async (...args) => { entered(); await gate; return save(...args); };
    host = await startObservationHost({ store: f.store, reminderScheduler: scheduler, reminderSender: async () => ({ state: 'submitted', cleanup: 'complete' }) });
    await write(host, { successNotices: false, reminders: true });
    const tick = scheduler.tick(); await started;
    const closing = host.close();
    assert.ok(f.store.readDashboardClaim());
    release(); await tick; await closing; host = undefined;
    assert.equal(f.store.readDashboardClaim(), undefined);
    assert.equal(f.store.readReminderGroups().groups[0].state, 'submitted');
  } finally { release?.(); await host?.close(); f.dispose(); }
});

test('closing while reservation is unsettled prevents submission and waits for its result write', async () => {
  const f = await fixture(); const scheduler = clock(); let host, entered, release;
  const started = new Promise(resolve => { entered = resolve; });
  const gate = new Promise(resolve => { release = resolve; });
  try {
    await f.finalize('failed');
    const reserve = f.store.reserveReminderGroup.bind(f.store);
    f.store.reserveReminderGroup = async claim => { entered(); await gate; return reserve(claim); };
    host = await startObservationHost({ store: f.store, reminderScheduler: scheduler, reminderSender: async () => { throw new Error('sender launched after close'); } });
    await write(host, { successNotices: false, reminders: true });
    const tick = scheduler.tick(); await started;
    const closing = host.close();
    assert.ok(f.store.readDashboardClaim());
    release(); await tick;
    await closing;
    assert.equal(f.store.readReminderGroups().groups[0].reason, 'stopped_before_submit');
    assert.equal(f.store.readDashboardClaim(), undefined); host = undefined;
  } finally { release?.(); f.dispose(); }
});

test('a late result cannot mutate a replacement dashboard claim', async () => {
  const f = await fixture(); const scheduler = clock(); let host, entered, finish;
  const started = new Promise(resolve => { entered = resolve; });
  const pending = new Promise(resolve => { finish = resolve; });
  try {
    await f.finalize('failed');
    host = await startObservationHost({ store: f.store, reminderScheduler: scheduler, reminderSender: async () => { entered(); return pending; } });
    await write(host, { successNotices: false, reminders: true });
    const tick = scheduler.tick(); await started;
    const original = f.store.readDashboardClaim();
    const replacement = { ...original, id: randomUUID(), token: randomUUID() };
    const database = new DatabaseSync(join(f.repo.path, '.git/factory/history.sqlite'));
    try { database.prepare('UPDATE owner_claims SET id=?,token=?,data=? WHERE id=?').run(replacement.id, replacement.token, JSON.stringify(replacement), original.id); }
    finally { database.close(); }
    finish({ state: 'submitted', cleanup: 'complete' }); await tick;
    assert.equal(f.store.readReminderGroups().groups[0].state, 'reserved');
    assert.equal(f.store.readDashboardClaim().id, replacement.id);
    await assert.rejects(host.close(), /reminder cleanup or recording unknown/);
    assert.equal(f.store.readDashboardClaim().id, replacement.id); host = undefined;
  } finally { finish?.({ state: 'submitted', cleanup: 'complete' }); f.dispose(); }
});

test('normal opening refuses a version 6 store without changing it', async () => {
  const repo = createRepository();
  const path = join(repo.path, '.git/factory/history.sqlite');
  const store = await initializeRepositoryStore(join(repo.path, '.git'), { release: 'fixture' });
  store.close();
  try {
    const database = new DatabaseSync(path);
    database.exec('PRAGMA user_version=6'); database.close();
    assert.throws(() => openRepositoryStore(join(repo.path, '.git')), /incompatible schema/);
    const observed = new DatabaseSync(path);
    try { assert.equal(observed.prepare('PRAGMA user_version').get().user_version, 6); }
    finally { observed.close(); }
  } finally { repo.dispose(); }
});

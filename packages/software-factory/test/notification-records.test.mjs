import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { fileURLToPath } from 'node:url';
import { invoke } from '../dist/lifecycle.js';
import { sendInitialNotification } from '../dist/notifications.js';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';

async function fixture(source) {
  const repo = createRepository();
  mkdirSync(join(repo.path, '.factory/workflows'), { recursive: true });
  writeFileSync(join(repo.path, '.factory/package.json'), '{"type":"module"}');
  writeFileSync(join(repo.path, '.factory/workflows/notice.ts'), source);
  repo.git(['add', '.factory']); repo.git(['commit', '-m', 'Commit notification fixture', '--only', '.factory']);
  const common = join(repo.path, '.git');
  const store = await initializeRepositoryStore(common, { release: 'fixture' }); store.close();
  const toolchain = join(common, 'factory/toolchain'); mkdirSync(toolchain);
  cpSync(new URL('../node_modules', import.meta.url), join(toolchain, 'node_modules'), { recursive: true });
  writeFileSync(join(toolchain, 'manifest.json'), JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2', dependencies: { '@types/node': '24.19.2' } }));
  const input = join(common, 'input.json'); writeFileSync(input, '{}');
  const run = (extra = {}) => invoke({ repository: repo.path, workflow: '.factory/workflows/notice.ts', input, newWorktree: true, ...extra });
  return { ...repo, common, input, run };
}

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

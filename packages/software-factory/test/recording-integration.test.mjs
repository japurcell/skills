import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { setTimeout as delay } from 'node:timers/promises';
import test from 'node:test';
import { InvocationRecorder } from '../dist/capture.js';
import { initializeRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';

test('recorder failure stops pending admission while preserving charged work and committed stream evidence', async () => {
  const repository = createRepository();
  let store, competitor;
  let locked = false;
  try {
    const common = join(repository.path, '.git');
    store = await initializeRepositoryStore(common, { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const owner = { host: 'fixture', pid: process.pid, start: 'integration' };
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    const base = { invocationId: invocation.id, operationKey: 'implement', kind: 'agent' };
    const initial = await store.admitAttempt({ ...base, id: randomUUID(), intent: 'initial' });
    await store.markStarted({ id: initial.id, owner });
    await store.settleAttempt({ id: initial.id, launch: 'started', outcome: 'failed', quiescent: true, evidence: 'fixture quality result' });
    const request = { ...base, id: randomUUID(), intent: 'code_correction', priorAttemptId: initial.id };
    const correction = await store.admitAttempt(request);
    await store.admitAttempt(request);
    await store.markStarted({ id: correction.id, owner });
    let notify;
    const shutdown = new Promise(resolve => { notify = resolve; });
    let notices = 0;
    const recorder = new InvocationRecorder({ store, invocationId: invocation.id,
      secrets: ['fixture-sensitive-value'], requestShutdown: notify, fallback: () => { notices++; } });
    const stdout = await recorder.openCapture({ channel: 'stdout', attemptId: correction.id });
    const stderr = await recorder.openCapture({ channel: 'stderr', attemptId: correction.id });
    await Promise.all([
      stdout.write('committed prefix fixture-sensitive-value ' + 'a'.repeat(65536)),
      stderr.consume((async function* () { for (let i = 0; i < 20; i++) yield Buffer.from('diagnostic\n'.repeat(4096)); })()),
    ]);
    await recorder.barrier();
    const committedCursor = store.readEvents({ after: '0' }).nextCursor;
    competitor = new DatabaseSync(join(common, 'factory', 'history.sqlite'));
    competitor.exec('BEGIN IMMEDIATE'); locked = true;
    const lateId = randomUUID();
    const pendingAdmission = store.admitAttempt({ id: lateId, invocationId: invocation.id, operationKey: 'late-command', kind: 'command', intent: 'initial' });
    const pendingResult = pendingAdmission.then(() => 'admitted', error => error.message);
    const failedWrite = stdout.write(Uint8Array.of(255));
    const failedResult = failedWrite.then(() => 'saved', error => error.message);
    await Promise.race([shutdown, delay(1500, undefined, { ref: false }).then(() => { throw new Error('shutdown waited for locked persistence'); })]);
    assert.equal(recorder.failed, true);
    assert.equal(notices, 1);
    assert.equal(store.readEvents({ after: committedCursor }).events.length, 0);
    competitor.exec('ROLLBACK'); locked = false;
    assert.match(await pendingResult, /admission|eligible/);
    assert.match(await failedResult, /recording failed/);
    assert.throws(() => store.readAttempt(lateId), /not found/);
    assert.equal(store.readAccounting(run.id).additionalUsed, 1);
    assert.equal(store.readAccounting(run.id).occupiedAgents, 1);
    assert.equal(store.readAttempt(correction.id).outcome, null);
    const saved = store.readCapture({ id: stdout.id });
    assert.equal(saved.state, 'partial');
    assert.match(saved.chunks[0].text, /^committed prefix \[REDACTED\]/);
    assert.equal(store.readCapture({ id: stderr.id }).state, 'complete');
    assert.ok(recorder.peakBufferedBytes <= 4194304);
    assert.equal(store.inspectOwners().length, 1);
  } finally {
    if (locked) competitor.exec('ROLLBACK');
    competitor?.close(); store?.close(); repository.dispose();
  }
});

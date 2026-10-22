import assert from 'node:assert/strict';
import { join } from 'node:path';
import test from 'node:test';
import { randomUUID } from 'node:crypto';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { createRepository } from './fixtures/repository.mjs';

const owner = { host: 'fixture-host', pid: process.pid, start: 'fixture-process-start' };

async function race(common, requests) {
  const children = [];
  try {
    const ready = [];
    for (const request of requests) {
      const child = spawn(process.execPath, [fileURLToPath(new URL('./fixtures/store-contender.mjs', import.meta.url)), common], {
        stdio: ['ignore', 'pipe', 'pipe', 'ipc'],
      });
      child.stdout.resume(); child.stderr.resume();
      const closed = once(child, 'close');
      const timer = setTimeout(() => child.kill('SIGKILL'), 5000);
      closed.finally(() => clearTimeout(timer));
      children.push({ child, closed, request });
      ready.push(Promise.race([once(child, 'message'), closed.then(() => { throw new Error('contender exited before ready'); })]));
    }
    await Promise.all(ready);
    const results = children.map(({ child }) => Promise.race([once(child, 'message'), once(child, 'close').then(() => { throw new Error('contender exited before result'); })]));
    for (const { child, request } of children) child.send(request);
    const messages = await Promise.all(results);
    await Promise.all(children.map(({ closed }) => closed));
    return messages.map(([message]) => message);
  } finally {
    for (const { child } of children) if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
    await Promise.allSettled(children.map(({ closed }) => closed));
  }
}

test('store preserves history and exclusive worktree claims across connections without stale-token release', async () => {
  const { initializeRepositoryStore, openRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let first, second;
  try {
    const common = join(repository.path, '.git');
    first = await initializeRepositoryStore(common, { release: 'fixture' });
    const run = await first.createRun();
    const worktree = await first.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await first.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    second = openRepositoryStore(common);
    assert.equal(second.readInvocation(invocation.id).runId, run.id);
    await assert.rejects(second.startInvocation({ runId: run.id, worktreeId: worktree.id, owner }), /claimed/);
    await assert.rejects(second.releaseClaim({ claimId: invocation.claim.id, token: 'stale', basis: 'quiescent' }), /token/);
    assert.equal(second.inspectOwners().length, 1);
    await first.releaseClaim({ claimId: invocation.claim.id, token: invocation.claim.token, basis: 'quiescent' });
    assert.equal(second.inspectOwners().length, 0);
    assert.equal(second.readInvocation(invocation.id).outcome, null);
    assert.ok(second.readEvents({ after: '0', limit: 200 }).events.length >= 4);
  } finally {
    second?.close(); first?.close(); repository.dispose();
  }
});

test('explicit clearance permits fresh follow-up with unknown prior outcome and rejects stale occupancy resurrection', async () => {
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const firstInvocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(firstInvocation.id);
    const old = await store.admitAttempt({ id: randomUUID(), invocationId: firstInvocation.id, operationKey: 'implement', kind: 'agent', intent: 'initial' });
    await store.clearOwner({ claimId: firstInvocation.claim.id, token: firstInvocation.claim.token, operatorConfirmed: true,
      inspection: 'unknown', note: 'Operator stopped and inspected the entire uncertain fixture scope.' });
    const fresh = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(fresh.id);
    const followup = await store.admitAttempt({ id: randomUUID(), invocationId: fresh.id, operationKey: 'implement', kind: 'agent', intent: 'followup', priorAttemptId: old.id });
    assert.notEqual(followup.invocationId, old.invocationId);
    assert.equal(store.readAttempt(old.id).outcome, null);
    assert.equal(store.readAccounting(run.id).additionalUsed, 1);
    await assert.rejects(store.settleAttempt({ id: old.id, launch: 'unknown', outcome: 'interrupted', quiescent: false, evidence: 'delayed stale settlement' }), /clearance/);
    await assert.rejects(store.markStarted({ id: old.id, owner }), /cleared/);
    assert.equal(store.readAttempt(old.id).quiescent, true);
    assert.equal(store.readAttempt(old.id).outcome, null);
    assert.equal(store.readAccounting(run.id).occupiedAgents, 1);
  } finally { store?.close(); repository.dispose(); }
});

test('invalid operation, settlement and lineage inputs cannot mutate existing facts', async () => {
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    const input = { id: randomUUID(), invocationId: invocation.id, operationKey: 'implement', kind: 'agent', intent: 'initial' };
    for (const operationKey of ['', 'x'.repeat(257), 'é'.repeat(129), 'bad\0key']) {
      await assert.rejects(store.admitAttempt({ ...input, operationKey }), /operation key/);
    }
    await store.admitAttempt(input);
    await assert.rejects(store.admitAttempt({ ...input, operationKey: 'changed' }), /identity/);
    await assert.rejects(store.settleAttempt({ id: input.id, launch: 'invented', outcome: 'succeeded', quiescent: true, evidence: 'invalid enum' }), /invalid/);
    assert.equal(store.readAttempt(input.id).outcome, null);
    await store.markStarted({ id: input.id, owner });
    await assert.rejects(store.settleAttempt({ id: input.id, launch: 'unknown', outcome: 'succeeded', quiescent: true, evidence: 'cannot erase known launch' }), /confirmed launch/);
    await assert.rejects(store.settleAttempt({ id: input.id, launch: 'not_started', outcome: 'failed', quiescent: true, evidence: 'cannot refund known launch' }), /confirmed launch/);
    assert.equal(store.readAccounting(run.id).occupiedAgents, 1);
  } finally { store?.close(); repository.dispose(); }
});

test('normal open refuses corrupt storage without creating or replacing history', async () => {
  const { initializeRepositoryStore, openRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  try {
    const common = join(repository.path, '.git');
    const store = await initializeRepositoryStore(common, { release: 'fixture' });
    await store.createRun();
    store.close();
    const databasePath = join(common, 'factory', 'history.sqlite');
    writeFileSync(databasePath, 'fixture-corrupt-database');
    assert.throws(() => openRepositoryStore(common));
    await assert.rejects(initializeRepositoryStore(common, { release: 'fixture' }), /already exists/);
    assert.equal(readFileSync(databasePath, 'utf8'), 'fixture-corrupt-database');
  } finally { repository.dispose(); }
});

test('explicit increases are recorded and shutdown rejects new admission without changing existing attempts', async () => {
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const run = await store.createRun();
    await store.increaseAllowances({ runId: run.id, additionalLimit: 21, codeLimit: 3, reason: 'Explicit fixture increase' });
    await assert.rejects(store.increaseAllowances({ runId: run.id, additionalLimit: 20, reason: 'Decrease' }), /increase/);
    await store.increaseCapacity({ agentLimit: 3, reason: 'Explicit fixture capacity increase' });
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    for (let index = 0; index < 3; index++) {
      await store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: `agent-${index}`, kind: 'agent', intent: 'initial' });
    }
    assert.equal(store.readAccounting(run.id).occupiedAgents, 3);
    await store.stopAdmissions(invocation.id);
    await assert.rejects(store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'late-command', kind: 'command', intent: 'initial' }), /eligible/);
    assert.equal(store.readAccounting(run.id).occupiedAgents, 3);
    const events = store.readEvents({ after: '0' }).events;
    assert.ok(events.some((event) => event.kind === 'allowances.increased' && event.data.reason === 'Explicit fixture increase'));
    assert.ok(events.some((event) => event.kind === 'capacity.increased'));
    assert.throws(() => store.readEvents({ after: '-1' }), /cursor/);
    assert.throws(() => store.readEvents({ after: '0', limit: 201 }), /limit/);
  } finally { store?.close(); repository.dispose(); }
});

test('contenders cannot spend the final additional allowance twice', async () => {
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    const common = join(repository.path, '.git');
    store = await initializeRepositoryStore(common, { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    const base = { invocationId: invocation.id, operationKey: 'review', kind: 'agent' };
    let previous;
    for (let index = 0; index < 20; index++) {
      previous = await store.admitAttempt({ ...base, id: randomUUID(), intent: index === 0 ? 'initial' : 'repeat', ...(previous ? { priorAttemptId: previous.id } : {}) });
      await store.markStarted({ id: previous.id, owner });
      await store.settleAttempt({ id: previous.id, launch: 'started', outcome: 'succeeded', quiescent: true, evidence: 'fixture review stopped' });
    }
    assert.equal(store.readAccounting(run.id).additionalUsed, 19);
    const results = await race(common, [0, 1].map(() => ({ action: 'admit', input: {
      ...base, id: randomUUID(), intent: 'repeat', priorAttemptId: previous.id,
    } })));
    assert.equal(results.filter((result) => result.ok).length, 1);
    assert.match(results.find((result) => !result.ok).error, /additional agent allowance/);
    assert.equal(store.readAccounting(run.id).additionalUsed, 20);
  } finally { store?.close(); repository.dispose(); }
});

test('process loss before or after admission preserves charges and an identity retry never double debits', async () => {
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    const common = join(repository.path, '.git');
    store = await initializeRepositoryStore(common, { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    const first = await store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'implement', kind: 'agent', intent: 'initial' });
    await store.markStarted({ id: first.id, owner });
    await store.settleAttempt({ id: first.id, launch: 'started', outcome: 'failed', quiescent: true, evidence: 'fixture quality result' });
    for (const point of ['before', 'after']) {
      const input = { id: randomUUID(), invocationId: invocation.id, operationKey: 'implement', kind: 'agent', intent: 'repeat', priorAttemptId: first.id };
      const child = spawn(process.execPath, [fileURLToPath(new URL('./fixtures/store-contender.mjs', import.meta.url)), common], { stdio: ['ignore', 'pipe', 'pipe', 'ipc'] });
      child.stdout.resume(); child.stderr.resume();
      const closed = once(child, 'close');
      const timer = setTimeout(() => child.kill('SIGKILL'), 5000);
      try {
        await Promise.race([once(child, 'message'), closed.then(() => { throw new Error('crash fixture failed to start'); })]);
        const checkpoint = Promise.race([once(child, 'message'), closed.then(() => { throw new Error('crash fixture ended before checkpoint'); })]);
        child.send({ action: `crash-${point}`, input });
        assert.equal((await checkpoint)[0].point, point);
        child.kill('SIGKILL');
        await closed;
        if (point === 'before') {
          assert.throws(() => store.readAttempt(input.id), /not found/);
          assert.equal(store.readAccounting(run.id).additionalUsed, 0);
        } else {
          assert.equal(store.readAttempt(input.id).launch, 'admitted');
          assert.equal(store.readAccounting(run.id).additionalUsed, 1);
          const recovered = await store.admitAttempt(input);
          assert.equal(recovered.id, input.id);
          assert.equal(store.readAccounting(run.id).additionalUsed, 1);
          assert.equal(store.readAccounting(run.id).occupiedAgents, 1);
        }
      } finally {
        clearTimeout(timer);
        if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
        await closed;
      }
    }
  } finally { store?.close(); repository.dispose(); }
});

test('separate processes contend atomically for the last capacity slot and exclusive owners', async () => {
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    const common = join(repository.path, '.git');
    store = await initializeRepositoryStore(common, { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const request = { action: 'invocation', input: { runId: run.id, worktreeId: worktree.id, owner } };
    const claims = await race(common, [request, request]);
    assert.equal(claims.filter((result) => result.ok).length, 1);
    assert.match(claims.find((result) => !result.ok).error, /claimed/);
    const invocation = claims.find((result) => result.ok).value;
    await store.activateInvocation(invocation.id);
    await store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'reserved', kind: 'agent', intent: 'initial' });
    const admissions = await race(common, [0, 1, 2].map((index) => ({ action: 'admit', input: {
      id: randomUUID(), invocationId: invocation.id, operationKey: `contender-${index}`, kind: 'agent', intent: 'initial',
    } })));
    assert.equal(admissions.filter((result) => result.ok).length, 1);
    for (const rejected of admissions.filter((result) => !result.ok)) assert.match(rejected.error, /capacity/);
    assert.equal(store.readAccounting(run.id).occupiedAgents, 2);
    await store.clearOwner({ claimId: invocation.claim.id, token: invocation.claim.token, operatorConfirmed: true,
      note: 'Fixture contenders exited; no provider launched.', inspection: 'not_live' });
    for (const kinds of [['dashboard', 'dashboard'], ['maintenance', 'maintenance'], ['maintenance', 'dashboard']]) {
      const results = await race(common, kinds.map((kind) => ({ action: 'claim', input: { kind, owner } })));
      assert.equal(results.filter((result) => result.ok).length, 1);
      const claim = results.find((result) => result.ok).value;
      await store.releaseClaim({ claimId: claim.id, token: claim.token, basis: 'quiescent' });
    }
    const other = await store.registerWorktree({ path: mkdtempSync(join(repository.path, 'other-')), registration: 'other-fixture' });
    const excluded = await race(common, [{ action: 'claim', input: { kind: 'maintenance', owner } },
      { action: 'invocation', input: { runId: run.id, worktreeId: other.id, owner } }]);
    assert.equal(excluded.filter((result) => result.ok).length, 1);
  } finally { store?.close(); repository.dispose(); }
});

test('maintenance excludes all owners and manual clearance saves basis without refunding uncertain launches', async () => {
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    const first = await store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'check', kind: 'agent', intent: 'initial' });
    await store.markStarted({ id: first.id, owner });
    await store.settleAttempt({ id: first.id, launch: 'started', outcome: 'failed', quiescent: true, evidence: 'stopped fixture' });
    const repeated = await store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'check', kind: 'agent', intent: 'repeat', priorAttemptId: first.id });
    await store.settleAttempt({ id: repeated.id, launch: 'unknown', outcome: 'interrupted', quiescent: false, evidence: 'launch acknowledgement lost' });
    const dashboard = await store.claimResource({ kind: 'dashboard', owner });
    await assert.rejects(store.claimResource({ kind: 'dashboard', owner }), /claimed/);
    await assert.rejects(store.claimResource({ kind: 'maintenance', owner }), /owner/);
    const clearance = { claimId: invocation.claim.id, token: invocation.claim.token, operatorConfirmed: true,
      note: 'Operator stopped and inspected the complete fixture scope.', inspection: 'known_live' };
    await assert.rejects(store.clearOwner(clearance), /known.live/);
    await assert.rejects(store.clearOwner({ ...clearance, inspection: 'unknown', operatorConfirmed: false }), /confirmation/);
    await store.clearOwner({ ...clearance, inspection: 'unknown' });
    assert.equal(store.readAccounting(run.id).additionalUsed, 1);
    assert.equal(store.readAccounting(run.id).occupiedAgents, 0);
    assert.equal(store.readAttempt(repeated.id).launch, 'unknown');
    assert.equal(store.readInvocation(invocation.id).outcome, null);
    assert.match(store.readClearances({ claimId: invocation.claim.id })[0].note, /inspected/);
    await assert.rejects(store.claimResource({ kind: 'maintenance', owner }), /owner/);
    await store.releaseClaim({ claimId: dashboard.id, token: dashboard.token, basis: 'quiescent' });
    const maintenance = await store.claimResource({ kind: 'maintenance', owner });
    await assert.rejects(store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner }), /maintenance/);
    await store.releaseClaim({ claimId: maintenance.id, token: maintenance.token, basis: 'quiescent' });
    await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await assert.rejects(store.clearOwner({ ...clearance, inspection: 'unknown' }), /token/);
    assert.equal(store.inspectOwners().length, 1);
  } finally { store?.close(); repository.dispose(); }
});

test('joined invocations retain correction and additional budgets, with refunds only for confirmed non-launch', async () => {
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    let invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    const request = { invocationId: invocation.id, operationKey: 'implement', kind: 'agent', intent: 'initial', loopKey: 'change' };
    let previous = await store.admitAttempt({ ...request, id: randomUUID() });
    const finish = async (attempt) => {
      await store.markStarted({ id: attempt.id, owner });
      await store.settleAttempt({ id: attempt.id, launch: 'started', outcome: 'failed', quiescent: true, evidence: 'fixture quality failure, stopped process' });
    };
    await finish(previous);
    previous = await store.admitAttempt({ ...request, id: randomUUID(), intent: 'code_correction', priorAttemptId: previous.id });
    await finish(previous);
    await store.releaseClaim({ claimId: invocation.claim.id, token: invocation.claim.token, basis: 'quiescent' });
    invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    request.invocationId = invocation.id;
    previous = await store.admitAttempt({ ...request, id: randomUUID(), intent: 'code_correction', priorAttemptId: previous.id });
    await finish(previous);
    await assert.rejects(store.admitAttempt({ ...request, id: randomUUID(), operationKey: 'renamed-correction', intent: 'code_correction', priorAttemptId: previous.id }), /code correction allowance/);
    const invalid = previous;
    previous = await store.admitAttempt({ ...request, id: randomUUID(), intent: 'format_correction', priorAttemptId: invalid.id });
    await finish(previous);
    await assert.rejects(store.admitAttempt({ ...request, id: randomUUID(), intent: 'format_correction', priorAttemptId: invalid.id }), /format correction allowance/);
    const unlaunched = await store.admitAttempt({ ...request, id: randomUUID(), intent: 'repeat', priorAttemptId: previous.id });
    assert.equal(store.readAccounting(run.id).additionalUsed, 4);
    const failure = { id: unlaunched.id, launch: 'not_started', outcome: 'failed', quiescent: true, evidence: 'spawn ENOENT' };
    await store.settleAttempt(failure);
    await store.settleAttempt(failure);
    assert.equal(store.readAccounting(run.id).additionalUsed, 3);
    for (let index = 0; index < 17; index++) {
      previous = await store.admitAttempt({ ...request, id: randomUUID(), intent: 'repeat', priorAttemptId: previous.id });
      await finish(previous);
    }
    assert.equal(store.readAccounting(run.id).additionalUsed, 20);
    await assert.rejects(store.admitAttempt({ ...request, id: randomUUID(), intent: 'followup', priorAttemptId: previous.id }), /additional agent allowance/);
  } finally { store?.close(); repository.dispose(); }
});

test('admission is idempotent, capacity is reserved before launch and uncertain children retain occupancy', async () => {
  const { initializeRepositoryStore } = await import('../dist/store.js');
  const repository = createRepository();
  let store;
  try {
    store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    const first = { id: randomUUID(), invocationId: invocation.id, operationKey: 'first', kind: 'agent', intent: 'initial' };
    await assert.rejects(store.admitAttempt(first), /eligible/);
    await store.activateInvocation(invocation.id);
    await store.admitAttempt(first);
    await store.admitAttempt(first);
    assert.equal(store.readAccounting(run.id).occupiedAgents, 1);
    const second = await store.admitAttempt({ ...first, id: randomUUID(), operationKey: 'second' });
    const third = { ...first, id: randomUUID(), operationKey: 'third' };
    await assert.rejects(store.admitAttempt(third), /capacity/);
    await store.settleAttempt({ id: first.id, launch: 'not_started', outcome: 'failed', quiescent: true, evidence: 'spawn returned ENOENT' });
    await store.admitAttempt(third);
    await store.markStarted({ id: second.id, owner });
    await store.settleAttempt({ id: second.id, launch: 'started', outcome: 'succeeded', quiescent: false, evidence: 'parent exited; child control unknown' });
    assert.equal(store.readAccounting(run.id).occupiedAgents, 2);
    await assert.rejects(store.releaseClaim({ claimId: invocation.claim.id, token: invocation.claim.token, basis: 'quiescent' }), /activity/);
    assert.equal(store.readAttempt(second.id).quiescent, false);
    assert.equal(store.readAttempt(first.id).launch, 'not_started');
    assert.equal(store.readAccounting(run.id).additionalUsed, 0);
  } finally {
    store?.close(); repository.dispose();
  }
});

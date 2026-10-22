import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { fixture } from './fixtures/learning-extraction-fixture.mjs';

test('explicit workspace-write override cannot make a modifying extraction succeed', async () => {
  const repo = await fixture();
  try {
    const source = repo.invoke('source', { mode: 'command' }).saved;
    const active = readFileSync(join(repo.path, '.factory/agents.json'), 'utf8');
    const result = repo.invoke('learn', { version: 1, sources: [{ invocationId: source.invocationId }] },
      { kind: 'mutate', payload: { proposals: [], noProposalReason: 'No justified change.' } },
      { agentOverrides: { 'learn/extract': { permissions: 'workspace-write' } } });
    assert.equal(JSON.parse(readFileSync(repo.launchLog, 'utf8').trim()).permissions, 'workspace-write');
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.saved.diagnostic, /candidate changed/);
    assert.equal(readFileSync(join(result.saved.worktree, '.factory/agents.json'), 'utf8'), '{"changed":"by fake extraction agent"}');
    assert.equal(readFileSync(join(repo.path, '.factory/agents.json'), 'utf8'), active);
    assert.equal(repo.history(source.invocationId).invocation.outcome, 'succeeded');
  } finally { repo.dispose(); }
});

test('malformed, unknown, unended and foreign source references fail before agent extraction', async () => {
  const repo = await fixture();
  try {
    const first = repo.invoke('source', { mode: 'command' }).saved;
    const second = repo.invoke('source', { mode: 'command' }).saved;
    const foreignAttempt = repo.history(second.invocationId).attempts.find(item => item.operationKey === 'observed').id;
    const foreignEvent = repo.events().find(item => item.kind === 'invocation.finalized' && item.data.invocationId === second.invocationId).cursor;
    const unended = await repo.seedHistory({ finalize: false });
    const cases = [
      [{ version: 2, sources: [{ invocationId: first.invocationId }] }, /version 1/],
      [{ version: 1, focus: 'x'.repeat(5000), sources: [{ invocationId: first.invocationId }] }, /focus exceeds/],
      [{ version: 1, sources: [{ invocationId: 'unknown-invocation' }] }, /invocation not found/],
      [{ version: 1, sources: [{ invocationId: unended }] }, /not an allowed ended invocation/],
      [{ version: 1, sources: [{ invocationId: first.invocationId, attemptIds: [foreignAttempt] }] }, /missing or foreign/],
      [{ version: 1, sources: [{ invocationId: first.invocationId, eventCursors: [foreignEvent] }] }, /another invocation/],
      [{ version: 1, sources: [{ invocationId: first.invocationId, eventCursors: ['9223372036854775807'] }] }, /missing or pruned/],
    ];
    for (const [input, diagnostic] of cases) {
      const result = repo.invoke('learn', input);
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.saved.diagnostic, diagnostic);
    }
  } finally { repo.dispose(); }
});

test('needs-input and infrastructure errors from extraction retain ordinary runner outcomes', async () => {
  const repo = await fixture();
  try {
    const source = repo.invoke('source', { mode: 'command' }).saved;
    const input = { version: 1, sources: [{ invocationId: source.invocationId }] };
    const question = repo.invoke('learn', input, { kind: 'needs_input' });
    assert.equal(question.status, 2, question.stdout + question.stderr);
    assert.equal(question.saved.outcome, 'needs_input');
    const failure = repo.invoke('learn', input, { kind: 'failure' });
    assert.equal(failure.status, 1, failure.stdout + failure.stderr);
    assert.equal(failure.saved.outcome, 'failed');
    assert.equal(repo.history(source.invocationId).invocation.outcome, 'succeeded');
  } finally { repo.dispose(); }
});

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { fixture } from './fixtures/learning-extraction-fixture.mjs';

test('explicit extraction saves examined ended sources and a justified empty result without changing active inputs', async () => {
  const repo = await fixture();
  try {
    const source = repo.invoke('source', { mode: 'command' });
    assert.equal(source.status, 0, source.stdout + source.stderr);
    const active = readFileSync(join(repo.path, '.factory/agents.json'), 'utf8');
    const extraction = repo.invoke('learn', { version: 1, sources: [{ invocationId: source.saved.invocationId }] });
    assert.equal(extraction.status, 0, extraction.stdout + extraction.stderr);
    const result = repo.report(extraction.saved.invocationId);
    assert.equal(result.version, 1);
    assert.deepEqual(result.proposals, []);
    assert.equal(result.noProposalReason, 'No justified change.');
    const extractionAttempt = repo.history(extraction.saved.invocationId).attempts.find(attempt => attempt.kind === 'agent');
    assert.equal(result.proposalResultCaptureId, extractionAttempt.agent.resultCaptureId);
    assert.equal(result.proposalValidatedResultCaptureId, extractionAttempt.agent.validatedResultCaptureId);
    assert.notEqual(result.proposalValidatedResultCaptureId, result.proposalResultCaptureId);
    assert.deepEqual(result.examinedSources.map(s => s.invocationId), [source.saved.invocationId]);
    assert.deepEqual(result.captureLimitations, []);
    assert.equal(repo.history(source.saved.invocationId).invocation.outcome, 'succeeded');
    assert.equal(readFileSync(join(repo.path, '.factory/agents.json'), 'utf8'), active);
    assert.equal(JSON.parse(readFileSync(repo.launchLog, 'utf8').trim()).permissions, 'read-only');
  } finally { repo.dispose(); }
});

test('failed, needs-input and interrupted invocations are valid explicit learning sources', async () => {
  const repo = await fixture();
  try {
    const failed = repo.invoke('source', { mode: 'failed' });
    const question = repo.invoke('source', { mode: 'needs_input' });
    const interrupted = await repo.interruptSource();
    assert.equal(failed.saved.outcome, 'failed');
    assert.equal(question.saved.outcome, 'needs_input');
    assert.equal(interrupted.outcome, 'interrupted');
    const result = repo.invoke('learn', { version: 1, sources: [failed.saved, question.saved, interrupted].map(item => ({ invocationId: item.invocationId })) });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.deepEqual(repo.report(result.saved.invocationId).examinedSources.map(item => item.outcome), ['failed', 'needs_input', 'interrupted']);
  } finally { repo.dispose(); }
});

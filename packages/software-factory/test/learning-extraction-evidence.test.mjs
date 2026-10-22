import assert from 'node:assert/strict';
import test from 'node:test';
import { fixture } from './fixtures/learning-extraction-fixture.mjs';

test('a proposal retains exact supporting and contrary references supplied to the agent', async () => {
  const repo = await fixture();
  try {
    const first = repo.invoke('source', { mode: 'command' }).saved;
    const second = repo.invoke('source', { mode: 'command' }).saved;
    const attemptId = repo.history(first.invocationId).attempts.find(item => item.operationKey === 'observed').id;
    const contraryId = repo.history(second.invocationId).attempts.find(item => item.operationKey === 'observed').id;
    const eventCursor = repo.events().find(item => item.kind === 'invocation.finalized' && item.data.invocationId === first.invocationId).cursor;
    const proposal = { key: 'clarify-check', summary: 'Clarify the selected check.', target: { scope: 'repository', path: '.factory/prompts/check.md' }, diff: '--- a/.factory/prompts/check.md\n+++ b/.factory/prompts/check.md\n@@ -1 +1 @@\n-Check\n+Run the selected check',
      supportingEvidence: [{ invocationId: first.invocationId, attemptId }, { invocationId: first.invocationId, eventCursor }],
      contraryEvidence: [{ invocationId: second.invocationId, attemptId: contraryId }], suggestedCases: ['Original failed check', 'Successful baseline check'] };
    const input = { version: 1, focus: 'Check discovery', sources: [{ invocationId: first.invocationId, attemptIds: [attemptId], eventCursors: [eventCursor] }, { invocationId: second.invocationId, attemptIds: [contraryId] }] };
    const result = repo.invoke('learn', input, { kind: 'result', payload: { proposals: [proposal] } });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const report = repo.report(result.saved.invocationId);
    assert.deepEqual(report.suppliedSources, input.sources);
    assert.deepEqual(report.proposals, [proposal]);
    assert.deepEqual(report.examinedSources[0].eventCursors, [eventCursor]);
    assert.deepEqual(report.examinedSources.map(item => item.attemptIds), [[attemptId], [contraryId]]);
  } finally { repo.dispose(); }
});

test('partial and pruned capture states and bounded history pages remain explicit in saved result', async () => {
  const repo = await fixture();
  try {
    const partial = await repo.seedHistory({ state: 'partial' });
    const pruned = await repo.seedHistory({ state: 'pruned' });
    const paged = await repo.seedHistory({ count: 65 });
    const result = repo.invoke('learn', { version: 1, sources: [partial, pruned, paged].map(invocationId => ({ invocationId })) });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const report = repo.report(result.saved.invocationId);
    assert.ok(report.captureLimitations.some(item => item.invocationId === partial && item.kind === 'capture_partial'));
    assert.ok(report.captureLimitations.some(item => item.invocationId === pruned && item.kind === 'capture_pruned'));
    assert.ok(report.captureLimitations.some(item => item.invocationId === paged && item.kind === 'capture_pages_unexamined'));
    assert.ok(report.examinedSources.find(item => item.invocationId === pruned).captureIds.length === 0);
    assert.deepEqual(report.proposals, []);
  } finally { repo.dispose(); }
});

test('a complete capture with an unreadable first text page is reported as unexamined', async () => {
  const repo = await fixture();
  try {
    const source = await repo.seedHistory({ text: 'x'.repeat(40000) });
    const result = repo.invoke('learn', { version: 1, sources: [{ invocationId: source }] });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const report = repo.report(result.saved.invocationId);
    assert.ok(report.captureLimitations.some(item => item.invocationId === source && item.kind === 'capture_text_unexamined'));
    assert.equal(report.examinedSources[0].captureIds.length, 0);
  } finally { repo.dispose(); }
});

test('unsupported proposed evidence cannot be reported as examined', async () => {
  const repo = await fixture();
  try {
    const source = repo.invoke('source', { mode: 'command' }).saved;
    const proposal = { key: 'invented', summary: 'Unjustified', target: { scope: 'repository', path: '.factory/prompts/check.md' }, diff: '+No',
      supportingEvidence: [{ invocationId: source.invocationId, attemptId: 'not-examined' }], contraryEvidence: [], suggestedCases: ['Case'] };
    const result = repo.invoke('learn', { version: 1, sources: [{ invocationId: source.invocationId }] }, { kind: 'result', payload: { proposals: [proposal] } });
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.saved.diagnostic, /result invalid|unresolved invalid/i);
    assert.equal(repo.history(source.invocationId).invocation.outcome, 'succeeded');
  } finally { repo.dispose(); }
});

test('a partial source capture cannot serve as an exact candidate reference', async () => {
  const repo = await fixture();
  try {
    const source = await repo.seedHistory({ state: 'partial' });
    const captureId = repo.history(source).captures[0].id;
    const proposal = { key: 'partial-candidate', summary: 'Candidate from incomplete bytes', target: { scope: 'repository', path: '.factory/prompts/check.md' },
      candidateCapture: { invocationId: source, captureId }, supportingEvidence: [{ invocationId: source, captureId }], contraryEvidence: [], suggestedCases: ['Review complete candidate'] };
    const result = repo.invoke('learn', { version: 1, sources: [{ invocationId: source }] }, { kind: 'result', payload: { proposals: [proposal] } });
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.saved.diagnostic, /result invalid/);
  } finally { repo.dispose(); }
});

test('a fully captured source can be cited as the proposed candidate', async () => {
  const repo = await fixture();
  try {
    const source = await repo.seedHistory({ text: 'Reviewable candidate bytes' });
    const captureId = repo.history(source).captures[0].id;
    const proposal = { key: 'captured-candidate', summary: 'Use retained candidate', target: { scope: 'repository', path: '.factory/prompts/check.md' },
      candidateCapture: { invocationId: source, captureId }, supportingEvidence: [{ invocationId: source, captureId }], contraryEvidence: [], suggestedCases: ['Check previous behavior'] };
    const result = repo.invoke('learn', { version: 1, sources: [{ invocationId: source }] }, { kind: 'result', payload: { proposals: [proposal] } });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.deepEqual(repo.report(result.saved.invocationId).proposals, [proposal]);
  } finally { repo.dispose(); }
});

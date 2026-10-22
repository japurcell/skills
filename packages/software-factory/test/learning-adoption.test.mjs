import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { sourceHistoryGateway, prepareAdoption, confirmAdoption, prepareRevert, confirmRevert } from '../dist/learning.js';
import { createRepository } from './fixtures/repository.mjs';

const sha = text => createHash('sha256').update(text).digest('hex');
const candidateText = 'candidate\n';
const originalText = 'baseline\n';
const path = '.factory/prompts/check.md';
const root = fileURLToPath(new URL('../', import.meta.url));

function fixture() {
  const repo = createRepository();
  mkdirSync(join(repo.path, '.factory/prompts'), { recursive: true });
  writeFileSync(join(repo.path, path), originalText);
  repo.git(['add', path]);
  repo.git(['commit', '-m', 'Add baseline']);
  const revision = repo.git(['rev-parse', 'HEAD']).trim();
  const extraction = { invocationId: 'extraction-1', proposalKey: 'improve' };
  const candidate = { invocationId: 'source-1', captureId: 'candidate-1', sha256: sha(candidateText) };
  const captures = new Map(), attempts = new Map();
  const put = (id, invocationId, channel, value, attemptId = null) => {
    const text = typeof value === 'string' ? value : JSON.stringify(value);
    captures.set(id, { invocationId, channel, text, attemptId, state: 'complete' }); return { captureId: id, sha256: sha(text) };
  };
  put('candidate-1', 'source-1', 'event', candidateText);
  put('baseline-1', 'source-1', 'event', originalText);
  const source = { invocationId: 'source-1', outcome: 'succeeded', attempts: [], events: [],
    captures: ['candidate-1', 'baseline-1'].map(id => ({ id, channel: 'event', state: 'complete', chunks: [{ sequence: 1, text: captures.get(id).text }] })) };
  const agent = (invocationId, attemptId, operationKey, validator, payload, context, purpose) => {
    const refs = { inputsCaptureId: `${attemptId}-inputs`, resultCaptureId: `${attemptId}-raw`, validatedResultCaptureId: `${attemptId}-validated`, validator };
    put(refs.inputsCaptureId, invocationId, 'context', { inputs: { permissions: 'read-only' }, purpose, context: JSON.stringify(context) }, attemptId);
    put(refs.resultCaptureId, invocationId, 'result', JSON.stringify(payload), attemptId);
    put(refs.validatedResultCaptureId, invocationId, 'validated-result', { kind: 'result', payload }, attemptId);
    attempts.set(attemptId, { id: attemptId, invocationId, kind: 'agent', outcome: 'succeeded', operationKey, agent: refs });
    return refs;
  };
  const proposals = [{ key: 'improve', target: { scope: 'repository', path }, candidateCapture: { invocationId: 'source-1', captureId: 'candidate-1' },
    suggestedCases: ['candidate check'], supportingEvidence: [{ invocationId: 'source-1', captureId: 'candidate-1' }], contraryEvidence: [] }];
  const extractionAgent = agent('extraction-1', 'extract-attempt-1', 'learn/extract', 'learning-extraction-v1', { proposals },
    { version: 1, evidence: [source], captureLimitations: [] }, 'report');
  const extractionReport = put('extraction-report-1', 'extraction-1', 'report', { version: 1,
    suppliedSources: [{ invocationId: 'source-1' }], examinedSources: [{ invocationId: 'source-1', outcome: 'succeeded', attemptIds: [], eventCursors: [], captureIds: ['candidate-1', 'baseline-1'] }],
    captureLimitations: [], proposals, proposalResultCaptureId: extractionAgent.resultCaptureId, proposalValidatedResultCaptureId: extractionAgent.validatedResultCaptureId });
  const cases = [{ key: 'check', criteria: 'candidate text', sourceSuggestion: 'candidate check', settings: { argv: ['/fixture/check'], cwd: '/fixture/case', timeoutMs: 5000, repetitions: 2 } }];
  for (const variant of ['baseline', 'candidate']) {
    const objective = [1, 2].map(index => ({ attemptId: `check-${variant}-${index}`, exitCode: variant === 'candidate' ? 0 : 1, cleanup: 'complete' }));
    for (const [index, entry] of objective.entries()) {
      attempts.set(entry.attemptId, { id: entry.attemptId, invocationId: 'evaluation-1', kind: 'command', outcome: entry.exitCode === 0 ? 'succeeded' : 'failed', operationKey: `evaluate/check/${variant}/objective/${index + 1}`, agent: null });
      put(`${entry.attemptId}-inputs`, 'evaluation-1', 'context', { ...cases[0].settings, required: false, shell: false }, entry.attemptId);
    }
    const payload = { judgment: variant === 'candidate' ? 'pass' : 'fail', reason: 'observed criterion' };
    const refs = agent('evaluation-1', `review-${variant}`, `evaluate/check/${variant}/review`, 'learning-evaluation-review-v1', payload,
      { variant, caseKey: 'check', criteria: 'candidate text', target: { scope: 'repository', path }, objective, text: variant === 'candidate' ? candidateText : originalText }, 'review');
    cases[0][variant] = { objective, review: { ...payload, attemptId: `review-${variant}`, resultCaptureId: refs.resultCaptureId,
      inputsCaptureId: refs.inputsCaptureId, effectivePermissions: 'read-only', effectiveProfile: null } };
  }
  const report = { version: 1, assessment: 'supported', limitations: [], target: { scope: 'repository', path },
    suppliedReferences: { extraction, baseline: { invocationId: 'source-1', captureId: 'baseline-1', sha256: sha(originalText) }, candidate },
    extractionReport, extractionResult: { attemptId: 'extract-attempt-1', rawCaptureId: extractionAgent.resultCaptureId, validatedCaptureId: extractionAgent.validatedResultCaptureId },
    resolved: { baselineSha256: sha(originalText), candidateSha256: sha(candidateText) }, proposalSuggestedCases: ['candidate check'], cases };
  const evaluations = new Map();
  const addEvaluation = (value, suffix) => {
    // Revised fixture reports share the same verified evidence-producing invocation.
    const reference = { invocationId: 'evaluation-1', reportCaptureId: `evaluation-report-${suffix}`, sha256: sha(JSON.stringify(value)) };
    put(reference.reportCaptureId, reference.invocationId, 'report', value);
    evaluations.set(reference.invocationId, reference.reportCaptureId); return reference;
  };
  const evaluation = addEvaluation(report, '1');
  const sourceHistory = {
    async read(id) {
      return { invocation: { id, stage: 'finalized', outcome: 'succeeded', workflow: id === 'extraction-1' ? '.factory/workflows/learn.ts' : id === 'evaluation-1' ? '.factory/workflows/evaluate.ts' : null },
        captures: [...captures].filter(([, capture]) => capture.invocationId === id).map(([id, capture]) => ({ id, ...capture })),
        attempts: [...attempts.values()].filter(item => item.invocationId === id),
        capturesNextCursor: 1, hasMoreCaptures: false, attemptsNextCursor: 1, hasMoreAttempts: false };
    },
    async attempt(id) { assert.ok(attempts.has(id)); return attempts.get(id); },
    async capture(invocationId, id) { const capture = captures.get(id); assert.ok(capture); assert.equal(capture.invocationId, invocationId); return {
      id, channel: capture.channel, state: capture.state, chunks: [{ sequence: 1, text: capture.text }], nextSequence: 1, hasMore: false,
    }; },
  };
  const approval = { reference: 'human-approval-1', extraction, evaluation, candidate,
    target: { repository: repo.path, scope: 'repository', path, expectedRevision: revision, expectedSha256: sha(originalText) } };
  let record = 0;
  const retain = value => ({ invocationId: 'approval-records', ...put(`record-${++record}`, 'approval-records', 'report', value) });
  return { repo, sourceHistory, approval, report, addEvaluation, captures, retain };
}

test('explicit approved action records actual committed candidate and actual revert', async () => {
  const f = fixture();
  try {
    const prepared = await prepareAdoption(f.sourceHistory, f.approval);
    assert.equal(prepared.approval.reference, 'human-approval-1');
    const unacted = await confirmAdoption(f.sourceHistory, f.retain(prepared), { reference: 'action-1', status: 'succeeded' });
    assert.equal(unacted.status, 'not_applied');
    assert.equal('applied' in unacted, false);

    writeFileSync(join(f.repo.path, path), candidateText);
    f.repo.git(['add', path]);
    f.repo.git(['commit', '-m', 'Adopt candidate']);
    const adopted = await confirmAdoption(f.sourceHistory, f.retain(prepared), { reference: 'action-2', status: 'succeeded' });
    assert.equal(adopted.status, 'applied');
    assert.equal(adopted.applied.revision, f.repo.git(['rev-parse', 'HEAD']).trim());
    assert.equal(adopted.applied.sha256, f.approval.candidate.sha256);
    assert.deepEqual(adopted.approval.evaluation, f.approval.evaluation);

    const reverting = await prepareRevert(f.sourceHistory, f.retain(adopted), { reference: 'human-revert-1' });
    writeFileSync(join(f.repo.path, path), originalText);
    f.repo.git(['add', path]);
    f.repo.git(['commit', '-m', 'Revert candidate']);
    const reverted = await confirmRevert(f.sourceHistory, f.retain(reverting), { reference: 'revert-action-1', status: 'succeeded' });
    assert.equal(reverted.status, 'reverted');
    assert.equal(reverted.reverted.revision, f.repo.git(['rev-parse', 'HEAD']).trim());
    assert.equal(reverted.originalAdoption.applied.revision, adopted.applied.revision);
    assert.equal(readFileSync(join(f.repo.path, path), 'utf8'), originalText);
  } finally { f.repo.dispose(); }
});

test('approval requires exact supported evaluation and candidate; changed scope or target requires renewed review', async () => {
  const f = fixture();
  try {
    const inconclusive = f.addEvaluation({ ...f.report, assessment: 'inconclusive', limitations: [{ kind: 'uncertain_review' }] }, 'uncertain');
    await assert.rejects(prepareAdoption(f.sourceHistory, { ...f.approval, evaluation: inconclusive }), /supported exact evaluation/);
    const revised = f.addEvaluation(f.report, 'revised');
    const approved = { ...f.approval, evaluation: revised };
    assert.equal((await prepareAdoption(f.sourceHistory, approved)).approval.evaluation.invocationId, revised.invocationId);
    const unrelatedBaseline = f.addEvaluation({ ...f.report,
      resolved: { ...f.report.resolved, baselineSha256: sha('unrelated evaluated baseline') } }, 'other-baseline');
    await assert.rejects(prepareAdoption(f.sourceHistory, { ...approved, evaluation: unrelatedBaseline }), /supported exact evaluation/);
    await assert.rejects(prepareAdoption(f.sourceHistory, { ...approved, candidate: { ...approved.candidate, sha256: sha('changed candidate') } }), /supported exact evaluation/);
    await assert.rejects(prepareAdoption(f.sourceHistory, { ...approved, target: { ...approved.target, path: 'tracked.txt' } }), /supported exact evaluation/);
    await assert.rejects(prepareAdoption(f.sourceHistory, { ...approved, target: { ...approved.target, scope: 'shared' } }), /exact human approval/);
    await assert.rejects(prepareAdoption(f.sourceHistory, { ...approved, reference: '' }), /exact human approval/);
    await assert.rejects(prepareAdoption(f.sourceHistory, { ...approved, target: { ...approved.target, expectedSha256: sha('stale') } }), /supported exact evaluation/);
    f.captures.set(approved.candidate.captureId, { ...f.captures.get(approved.candidate.captureId), text: 'changed captured candidate\n' });
    await assert.rejects(prepareAdoption(f.sourceHistory, approved), /approved candidate bytes changed|retained evidence/);
    f.captures.set(approved.candidate.captureId, { ...f.captures.get(approved.candidate.captureId), text: candidateText });
    writeFileSync(join(f.repo.path, path), 'changed target\n');
    f.repo.git(['add', path]);
    f.repo.git(['commit', '-m', 'Change target before approval']);
    await assert.rejects(prepareAdoption(f.sourceHistory, approved), /renewed review/);
  } finally { f.repo.dispose(); }
});

test('preparation retains approved identities when caller later mutates input objects', async () => {
  const f = fixture();
  try {
    const prepared = await prepareAdoption(f.sourceHistory, f.approval);
    f.approval.candidate.sha256 = sha('substituted');
    f.approval.target.path = 'tracked.txt';
    assert.equal(prepared.approval.candidate.sha256, sha(candidateText));
    assert.equal(prepared.approval.target.path, path);
  } finally { f.repo.dispose(); }
});

test('failed and uncertain action never claim applied even if candidate bytes appear', async () => {
  const f = fixture();
  try {
    const prepared = await prepareAdoption(f.sourceHistory, f.approval);
    assert.equal((await confirmAdoption(f.sourceHistory, f.retain(prepared), { reference: 'failure-1', status: 'failed' })).status, 'not_applied');
    assert.equal((await confirmAdoption(f.sourceHistory, f.retain(prepared), { reference: 'unknown-1', status: 'uncertain' })).status, 'not_applied');
    writeFileSync(join(f.repo.path, path), candidateText);
    f.repo.git(['add', path]);
    f.repo.git(['commit', '-m', 'Candidate after failed action']);
    for (const status of ['failed', 'uncertain']) {
      const result = await confirmAdoption(f.sourceHistory, f.retain(prepared), { reference: `action-${status}`, status });
      assert.equal(result.status, 'uncertain');
      assert.equal('applied' in result, false);
    }
  } finally { f.repo.dispose(); }
});

test('revert needs an applied record and fresh approval; failed or changed revert cannot claim restored revision', async () => {
  const f = fixture();
  try {
    const prepared = await prepareAdoption(f.sourceHistory, f.approval);
    const unacted = await confirmAdoption(f.sourceHistory, f.retain(prepared), { reference: 'unacted', status: 'succeeded' });
    await assert.rejects(prepareRevert(f.sourceHistory, f.retain(unacted), { reference: 'revert' }), /applied adoption/);
    writeFileSync(join(f.repo.path, path), candidateText);
    f.repo.git(['add', path]); f.repo.git(['commit', '-m', 'Apply candidate']);
    const adopted = await confirmAdoption(f.sourceHistory, f.retain(prepared), { reference: 'adopted', status: 'succeeded' });
    assert.equal(adopted.status, 'applied');
    await assert.rejects(prepareRevert(f.sourceHistory, f.retain(adopted), { reference: '' }), /explicit approval/);
    const reverting = await prepareRevert(f.sourceHistory, f.retain(adopted), { reference: 'revert-approval' });
    assert.equal((await confirmRevert(f.sourceHistory, f.retain(reverting), { reference: 'failed-revert', status: 'failed' })).status, 'not_reverted');
    writeFileSync(join(f.repo.path, path), 'another target\n');
    f.repo.git(['add', path]); f.repo.git(['commit', '-m', 'Change post-adoption target']);
    await assert.rejects(prepareRevert(f.sourceHistory, f.retain(adopted), { reference: 'stale-revert' }), /renewed review/);
    writeFileSync(join(f.repo.path, path), originalText);
    f.repo.git(['add', path]); f.repo.git(['commit', '-m', 'Restore after intervening change']);
    const result = await confirmRevert(f.sourceHistory, f.retain(reverting), { reference: 'late-revert', status: 'succeeded' });
    assert.equal(result.status, 'uncertain');
    assert.equal('reverted' in result, false);
  } finally { f.repo.dispose(); }
});

test('success claim with changed content or broader commit scope remains uncertain', async () => {
  const f = fixture();
  try {
    const prepared = await prepareAdoption(f.sourceHistory, f.approval);
    writeFileSync(join(f.repo.path, path), 'wrong candidate\n');
    f.repo.git(['add', path]);
    f.repo.git(['commit', '-m', 'Wrong candidate']);
    const wrong = await confirmAdoption(f.sourceHistory, f.retain(prepared), { reference: 'wrong-1', status: 'succeeded' });
    assert.equal(wrong.status, 'uncertain');
    assert.equal('applied' in wrong, false);
  } finally { f.repo.dispose(); }
  const broader = fixture();
  try {
    const prepared = await prepareAdoption(broader.sourceHistory, broader.approval);
    writeFileSync(join(broader.repo.path, path), candidateText);
    writeFileSync(join(broader.repo.path, 'tracked.txt'), 'unapproved scope\n');
    broader.repo.git(['add', path, 'tracked.txt']);
    broader.repo.git(['commit', '-m', 'Broader scope']);
    const result = await confirmAdoption(broader.sourceHistory, broader.retain(prepared), { reference: 'scope-1', status: 'succeeded' });
    assert.equal(result.status, 'uncertain');
    assert.equal('applied' in result, false);
  } finally { broader.repo.dispose(); }
  const intervening = fixture();
  try {
    const prepared = await prepareAdoption(intervening.sourceHistory, intervening.approval);
    writeFileSync(join(intervening.repo.path, path), 'changed first\n');
    intervening.repo.git(['add', path]);
    intervening.repo.git(['commit', '-m', 'Intervening target revision']);
    writeFileSync(join(intervening.repo.path, path), candidateText);
    intervening.repo.git(['add', path]);
    intervening.repo.git(['commit', '-m', 'Apply after changed target']);
    const result = await confirmAdoption(intervening.sourceHistory, intervening.retain(prepared), { reference: 'intervening-1', status: 'succeeded' });
    assert.equal(result.status, 'uncertain');
    assert.equal('applied' in result, false);
  } finally { intervening.repo.dispose(); }
});

test('saved preparations cannot replace approved adoption or revert parents', async () => {
  const f = fixture();
  try {
    const prepared = JSON.parse(JSON.stringify(await prepareAdoption(f.sourceHistory, f.approval)));
    writeFileSync(join(f.repo.path, path), 'intervening\n');
    f.repo.git(['add', path]); f.repo.git(['commit', '-m', 'Intervening']);
    prepared.expected = { revision: f.repo.git(['rev-parse', 'HEAD']).trim(), sha256: sha('intervening\n') };
    writeFileSync(join(f.repo.path, path), candidateText);
    f.repo.git(['add', path]); f.repo.git(['commit', '-m', 'Candidate']);
    await assert.rejects(confirmAdoption(f.sourceHistory, f.retain(prepared), { reference: 'action', status: 'succeeded' }), /preparation/);
    const forged = { kind: 'adoption', status: 'applied', approval: f.approval, evidence: prepared.evidence,
      action: { reference: 'action', status: 'succeeded' }, applied: { revision: f.repo.git(['rev-parse', 'HEAD']).trim(), sha256: sha(candidateText) } };
    await assert.rejects(prepareRevert(f.sourceHistory, f.retain(forged), { reference: 'revert' }), /retained report reference/);
  } finally { f.repo.dispose(); }
});

test('retained provenance rejects missing, foreign, partial, pruned and mismatched evidence', async () => {
  const f = fixture();
  try {
    for (const id of ['extraction-report-1', 'extract-attempt-1-raw', 'extract-attempt-1-validated', 'extract-attempt-1-inputs', 'review-candidate-validated', 'check-candidate-1-inputs']) {
      const original = f.captures.get(id);
      for (const state of ['partial', 'pruned']) {
        f.captures.set(id, { ...original, state });
        await assert.rejects(prepareAdoption(f.sourceHistory, f.approval));
      }
      f.captures.set(id, { ...original, invocationId: 'foreign' });
      await assert.rejects(prepareAdoption(f.sourceHistory, f.approval));
      f.captures.delete(id);
      await assert.rejects(prepareAdoption(f.sourceHistory, f.approval));
      f.captures.set(id, original);
    }
    const id = 'extract-attempt-1-validated', original = f.captures.get(id);
    const changed = JSON.parse(original.text); changed.payload.proposals[0].target.path = 'tracked.txt';
    f.captures.set(id, { ...original, text: JSON.stringify(changed) });
    await assert.rejects(prepareAdoption(f.sourceHistory, f.approval), /retained evidence/);
    f.captures.set(id, original);
    const lied = structuredClone(f.report); lied.cases[0].baseline.objective[0].exitCode = 0;
    await assert.rejects(prepareAdoption(f.sourceHistory, { ...f.approval, evaluation: f.addEvaluation(lied, 'lying-objective') }), /retained evidence/);
    assert.equal((await prepareAdoption(f.sourceHistory, f.approval)).kind, 'adoption-preparation');
  } finally { f.repo.dispose(); }
});

test('saved revert preparation and claimed historical adoption are revalidated', async () => {
  const f = fixture();
  try {
    const prepared = await prepareAdoption(f.sourceHistory, f.approval);
    writeFileSync(join(f.repo.path, path), candidateText);
    f.repo.git(['add', path]); f.repo.git(['commit', '-m', 'Candidate']);
    const applied = await confirmAdoption(f.sourceHistory, f.retain(prepared), { reference: 'apply', status: 'succeeded' });
    assert.equal(applied.status, 'applied');
    const invalidBaseline = structuredClone(applied); invalidBaseline.approval.target.expectedSha256 = sha('invented baseline');
    await assert.rejects(prepareRevert(f.sourceHistory, f.retain(invalidBaseline), { reference: 'revert' }), /retained evidence/);
    const revertApproval = { reference: 'revert' };
    const pending = prepareRevert(f.sourceHistory, f.retain(applied), revertApproval);
    revertApproval.reference = 'changed after call';
    const reverting = JSON.parse(JSON.stringify(await pending));
    assert.equal(reverting.approvalReference, 'revert');
    writeFileSync(join(f.repo.path, 'tracked.txt'), 'unapproved intervening scope\n');
    f.repo.git(['add', 'tracked.txt']); f.repo.git(['commit', '-m', 'Intervening']);
    reverting.expected.revision = f.repo.git(['rev-parse', 'HEAD']).trim();
    writeFileSync(join(f.repo.path, path), originalText);
    f.repo.git(['add', path]); f.repo.git(['commit', '-m', 'Restore']);
    await assert.rejects(confirmRevert(f.sourceHistory, f.retain(reverting), { reference: 'restore', status: 'succeeded' }), /revert preparation/);
    for (const malformed of [null, {}, { ...prepared, kind: 'revert-preparation' }, { ...prepared, evidence: {} }])
      await assert.rejects(confirmAdoption(f.sourceHistory, f.retain(malformed), { reference: 'action', status: 'succeeded' }));
  } finally { f.repo.dispose(); }
});

test('retained references anchor approval fields and reject forged or unavailable saved records at every boundary', async () => {
  const f = fixture();
  try {
    const prepared = await prepareAdoption(f.sourceHistory, f.approval);
    const reference = f.retain(prepared);
    const saved = JSON.parse(JSON.stringify(prepared));
    const mutations = [
      value => { value.approval.reference = 'different-human'; },
      value => { value.approval.candidate.sha256 = sha('unapproved'); },
      value => { value.approval.candidate.captureId = 'baseline-1'; },
      value => { value.approval.evaluation.reportCaptureId = 'different-evaluation'; },
      value => { value.approval.extraction.proposalKey = 'different-proposal'; },
      value => { value.approval.target.path = 'tracked.txt'; },
      value => { value.approval.target.repository = '/different-repository'; },
      value => { value.approval.target.expectedRevision = '1'.repeat(40); },
      value => { value.evidence.extractionReport.captureId = 'different-report'; },
    ];
    for (const mutate of mutations) {
      const changed = structuredClone(saved); mutate(changed);
      await assert.rejects(confirmAdoption(f.sourceHistory, changed, { reference: 'action', status: 'succeeded' }), /retained report reference/);
      await assert.rejects(confirmAdoption(f.sourceHistory, { ...reference, sha256: sha(JSON.stringify(changed)) },
        { reference: 'action', status: 'succeeded' }), /digest/);
    }
    const original = f.captures.get(reference.captureId);
    for (const replacement of [{ ...original, state: 'partial' }, { ...original, state: 'pruned' },
      { ...original, invocationId: 'foreign' }, { ...original, text: JSON.stringify({ ...saved, approval: { ...saved.approval, reference: 'edited' } }) }]) {
      f.captures.set(reference.captureId, replacement);
      await assert.rejects(confirmAdoption(f.sourceHistory, reference, { reference: 'action', status: 'succeeded' }));
    }
    f.captures.set(reference.captureId, original);
    writeFileSync(join(f.repo.path, path), candidateText);
    f.repo.git(['add', path]); f.repo.git(['commit', '-m', 'Approved target']);
    const applied = await confirmAdoption(f.sourceHistory, reference, { reference: 'apply', status: 'succeeded' });
    assert.equal(applied.status, 'applied');
    assert.deepEqual(applied.preparationReference, reference);
    const appliedRef = f.retain(applied);
    for (const mutate of mutations) {
      const forged = structuredClone(applied); mutate(forged);
      await assert.rejects(prepareRevert(f.sourceHistory, f.retain(forged), { reference: 'revert' }));
    }
    for (const status of ['failed', 'uncertain']) {
      await assert.rejects(prepareRevert(f.sourceHistory, f.retain({ ...applied, action: { reference: 'bad', status } }),
        { reference: 'revert' }), /observed adoption/);
    }
    for (const status of ['not_applied', 'uncertain'])
      await assert.rejects(prepareRevert(f.sourceHistory, f.retain({ ...applied, status }), { reference: 'revert' }), /applied adoption/);
    const reverting = await prepareRevert(f.sourceHistory, appliedRef, { reference: 'human-revert' });
    const revertRef = f.retain(reverting);
    const editedRevert = structuredClone(reverting); editedRevert.approvalReference = 'different-human';
    await assert.rejects(confirmRevert(f.sourceHistory, editedRevert, { reference: 'action', status: 'succeeded' }), /retained report reference/);
    await assert.rejects(confirmRevert(f.sourceHistory, { ...revertRef, sha256: sha(JSON.stringify(editedRevert)) },
      { reference: 'action', status: 'succeeded' }), /digest/);
    const forgedRevert = structuredClone(reverting);
    forgedRevert.originalAdoption.action.reference = 'forged-confirmation';
    await assert.rejects(confirmRevert(f.sourceHistory, f.retain(forgedRevert), { reference: 'action', status: 'succeeded' }), /retained evidence/);
    // Pruning previously accepted evaluation evidence invalidates both later saved-object boundaries.
    const review = f.captures.get('review-candidate-validated');
    f.captures.set('review-candidate-validated', { ...review, state: 'pruned' });
    await assert.rejects(confirmAdoption(f.sourceHistory, reference, { reference: 'action', status: 'succeeded' }));
    await assert.rejects(prepareRevert(f.sourceHistory, appliedRef, { reference: 'revert' }));
    await assert.rejects(confirmRevert(f.sourceHistory, revertRef, { reference: 'action', status: 'succeeded' }));
  } finally { f.repo.dispose(); }
});

test('extraction event ownership is resolved from retained history, including pages outside selected evidence', async () => {
  const f = fixture();
  try {
    const setEvent = event => {
      f.sourceHistory.event = async () => event;
      const input = f.captures.get('extract-attempt-1-inputs');
      const outer = JSON.parse(input.text), context = JSON.parse(outer.context);
      context.evidence[0].events = [event];
      outer.context = JSON.stringify(context);
      input.text = JSON.stringify(outer);
      const capture = f.captures.get('extraction-report-1'), report = JSON.parse(capture.text);
      report.examinedSources[0].eventCursors = [event.cursor];
      report.suppliedSources[0].eventCursors = [event.cursor];
      capture.text = JSON.stringify(report);
      f.report.extractionReport.sha256 = sha(capture.text);
      return { ...f.approval, evaluation: f.addEvaluation(f.report, 'events') };
    };
    for (const data of [{ invocationId: 'foreign-source' }, { invocationId: 'foreign-source', captureId: 'candidate-1' },
      { attemptId: 'extract-attempt-1' }, { captureId: 'extraction-report-1' }, {}]) {
      await assert.rejects(prepareAdoption(f.sourceHistory, setEvent({ cursor: '1', kind: 'event', data })), /retained evidence/);
    }
    for (const data of [{ invocationId: 'source-1' }, { captureId: 'candidate-1' }])
      assert.equal((await prepareAdoption(f.sourceHistory, setEvent({ cursor: '1', kind: 'event', data }))).kind, 'adoption-preparation');
    const read = f.sourceHistory.read;
    f.sourceHistory.read = async (id, afterAttempt = 0, afterCapture = 0) => {
      const page = await read(id);
      if (id !== 'source-1') return page;
      return { ...page, attempts: afterAttempt ? [{ id: 'owned-later', invocationId: id }] : [],
        attemptsNextCursor: afterAttempt ? 2 : 1, hasMoreAttempts: !afterAttempt };
    };
    assert.equal((await prepareAdoption(f.sourceHistory, setEvent({ cursor: '1', kind: 'event', data: { attemptId: 'owned-later' } }))).kind, 'adoption-preparation');
    f.sourceHistory.read = async (id, afterAttempt = 0) => {
      const page = await read(id);
      return id === 'source-1' ? { ...page, attempts: [], attemptsNextCursor: afterAttempt + 1, hasMoreAttempts: true } : page;
    };
    await assert.rejects(prepareAdoption(f.sourceHistory, setEvent({ cursor: '1', kind: 'event', data: { attemptId: 'owned-later' } })), /retained evidence/);
  } finally { f.repo.dispose(); }
});

test('real retained extraction, inconclusive evaluation, revised evaluation, approval, action and revert preserve lineage', async () => {
  const repo = createRepository();
  try {
    mkdirSync(join(repo.path, '.factory/workflows'), { recursive: true });
    mkdirSync(join(repo.path, '.factory/prompts'), { recursive: true });
    writeFileSync(join(repo.path, path), originalText);
    writeFileSync(join(repo.path, '.factory/package.json'), '{"type":"module"}');
    writeFileSync(join(repo.path, '.factory/agents.json'), JSON.stringify({ defaults: {
      harness: 'fake', permissions: 'read-only', skillDelivery: 'instructions', prompt: 'default', skills: [],
    } }));
    for (const name of ['learn', 'evaluate', 'change'])
      cpSync(join(root, `templates/workflows/${name}.ts`), join(repo.path, `.factory/workflows/${name}.ts`));
    repo.git(['add', '.factory']);
    repo.git(['commit', '-m', 'Create disposable learning target']);
    const originalRevision = repo.git(['rev-parse', 'HEAD']).trim();
    const common = join(repo.path, '.git');
    (await initializeRepositoryStore(common, { release: 'fixture' })).close();
    const toolchain = join(common, 'factory/toolchain');
    mkdirSync(toolchain);
    cpSync(join(root, 'node_modules'), join(toolchain, 'node_modules'), { recursive: true });
    writeFileSync(join(toolchain, 'manifest.json'), JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2',
      dependencies: { '@types/node': '24.19.2' } }));
    const host = join(common, 'adoption-host.mjs'), input = join(common, 'adoption-input.json');
    const launchLog = join(common, 'adoption-launches.jsonl');
    writeFileSync(host, `import { invoke } from ${JSON.stringify(new URL('../dist/lifecycle.js', import.meta.url).href)};
import { createFakeAdapter } from ${JSON.stringify(new URL('../dist/adapters/fake.js', import.meta.url).href)};
const { scenario, ...options } = JSON.parse(process.argv[2]);
const adapter = createFakeAdapter({ executable: process.execPath, script: ${JSON.stringify(join(root, 'test/fixtures/learning-evaluation-harness.mjs'))} });
const start = adapter.start;
adapter.start = request => start({ ...request, context: JSON.stringify({ context: request.context, scenario, launchLog: ${JSON.stringify(launchLog)} }) });
const result = await invoke({ ...options, adapters: { fake: adapter } });
console.log(JSON.stringify(result)); process.exit(result.exitCode);`);
    const store = openRepositoryStore(common);
    let sourceId, sourceWorktreeId, baselineId, candidateId;
    try {
      const run = await store.createRun();
      const worktree = await store.registerWorktree({ path: repo.path, registration: 'adoption-source' });
      sourceWorktreeId = worktree.id;
      const source = await store.startInvocation({ runId: run.id, worktreeId: worktree.id,
        owner: { host: 'fixture', pid: process.pid, start: null } });
      sourceId = source.id;
      const baseline = await store.createCapture({ invocationId: source.id, channel: 'event' });
      await store.appendCapture({ id: baseline.id, chunks: [{ sequence: 1, text: originalText }], state: 'complete' });
      baselineId = baseline.id;
      const candidate = await store.createCapture({ invocationId: source.id, channel: 'event' });
      await store.appendCapture({ id: candidate.id, chunks: [{ sequence: 1, text: candidateText }], state: 'complete' });
      candidateId = candidate.id;
      await store.finalizeInvocation({ id: source.id, outcome: 'succeeded', cleanup: 'complete',
        claimId: source.claim.id, token: source.claim.token });
    } finally { store.close(); }
    const invoke = (workflow, payload, scenario) => {
      writeFileSync(input, JSON.stringify(payload));
      const result = spawnSync(process.execPath, [host, JSON.stringify({ repository: repo.path,
        workflow: `.factory/workflows/${workflow}.ts`, input, newWorktree: true, shutdownGraceMs: 100, scenario })],
      { encoding: 'utf8', timeout: 60000 });
      assert.equal(result.error, undefined);
      assert.equal(result.status, 0, result.stdout + result.stderr);
      return JSON.parse(result.stdout.trim());
    };
    const retained = id => { const reader = openRepositoryStore(common); try {
      const capture = reader.readHistory(id, { limit: 100 }).captures.find(item => item.channel === 'report');
      assert.ok(capture);
      const text = capture.chunks.map(chunk => chunk.text).join('');
      return { captureId: capture.id, text, value: JSON.parse(text) };
    } finally { reader.close(); } };
    const saveOperation = async (name, value, workflow = `explicit-learning/${name}`) => {
      const recorder = openRepositoryStore(common);
      try {
        const run = await recorder.createRun();
        const invocation = await recorder.startInvocation({ runId: run.id, worktreeId: sourceWorktreeId,
          owner: { host: 'fixture', pid: process.pid, start: null } });
        await recorder.saveInvocationMetadata(invocation.id, { workflow });
        const capture = await recorder.createCapture({ invocationId: invocation.id, channel: 'report' });
        await recorder.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text: JSON.stringify(value) }], state: 'complete' });
        await recorder.finalizeInvocation({ id: invocation.id, outcome: 'succeeded', cleanup: 'complete',
          claimId: invocation.claim.id, token: invocation.claim.token });
        return { invocationId: invocation.id, captureId: capture.id, sha256: sha(JSON.stringify(value)) };
      } finally { recorder.close(); }
    };
    const extraction = invoke('learn', { version: 1, sources: [{ invocationId: sourceId }] },
      { kind: 'extract', proposalKind: 'capture', target: { scope: 'repository', path } });
    const extracted = retained(extraction.invocationId);
    assert.equal(extracted.value.proposals[0].candidateCapture.captureId, candidateId);
    const evaluationInput = { version: 1, extraction: { invocationId: extraction.invocationId, proposalKey: 'improve' },
      baseline: { invocationId: sourceId, captureId: baselineId, sha256: sha(originalText) },
      candidate: { invocationId: sourceId, captureId: candidateId, sha256: sha(candidateText) },
      cases: [{ key: 'candidate-check', criteria: 'candidate text', sourceSuggestion: 'candidate check',
        argv: [process.execPath, '-e', "process.exit(require('node:fs').readFileSync('.factory/prompts/check.md','utf8') === 'candidate\\n' ? 0 : 1)"],
        timeoutMs: 5000 }] };
    const inconclusiveRun = invoke('evaluate', evaluationInput, 'uncertain');
    const inconclusive = retained(inconclusiveRun.invocationId);
    assert.equal(inconclusive.value.assessment, 'inconclusive');
    const revisedRun = invoke('evaluate', evaluationInput, 'result');
    const revised = retained(revisedRun.invocationId);
    assert.equal(revised.value.assessment, 'supported');
    const approval = { reference: 'fixture-human-approval', extraction: evaluationInput.extraction,
      evaluation: { invocationId: revisedRun.invocationId, reportCaptureId: revised.captureId, sha256: sha(revised.text) },
      candidate: evaluationInput.candidate,
      target: { repository: repo.path, scope: 'repository', path, expectedRevision: originalRevision, expectedSha256: sha(originalText) } };
    const historyStore = openRepositoryStore(common);
    try {
      const history = sourceHistoryGateway(historyStore, action => action());
      await assert.rejects(prepareAdoption(history, { ...approval,
        evaluation: { invocationId: inconclusiveRun.invocationId, reportCaptureId: inconclusive.captureId, sha256: sha(inconclusive.text) } }),
      /supported exact evaluation/);
      // A successful report with matching claims is insufficient without its retained producer relationships.
      for (const workflow of ['unrelated-operation', '.factory/workflows/evaluate.ts']) {
        const forgedReport = structuredClone(revised.value);
        const recorded = await saveOperation('forged-evaluation', forgedReport, workflow);
        await assert.rejects(prepareAdoption(history, { ...approval, evaluation: {
          invocationId: recorded.invocationId, reportCaptureId: recorded.captureId, sha256: sha(JSON.stringify(forgedReport)) } }));
      }
      const missing = structuredClone(revised.value);
      missing.suppliedReferences.extraction.invocationId = 'nonexistent-extraction';
      const recorded = await saveOperation('missing-extraction', missing, '.factory/workflows/evaluate.ts');
      await assert.rejects(prepareAdoption(history, { ...approval, extraction: missing.suppliedReferences.extraction,
        evaluation: { invocationId: recorded.invocationId, reportCaptureId: recorded.captureId, sha256: sha(JSON.stringify(missing)) } }));
      const prepared = await prepareAdoption(history, approval);
      assert.deepEqual(prepared.evidence.extractionReport, revised.value.extractionReport);
      assert.deepEqual(prepared.evidence.extractionResult, revised.value.extractionResult);
      const approvalRecord = await saveOperation('adoption-approval', prepared);
      assert.equal(retained(approvalRecord.invocationId).value.kind, 'adoption-preparation');
      const editedPreparation = JSON.parse(JSON.stringify(prepared));
      editedPreparation.approval.candidate.sha256 = sha('unauthorized candidate\n');
      writeFileSync(join(repo.path, path), 'unauthorized candidate\n');
      repo.git(['add', path]); repo.git(['commit', '-m', 'Unapproved saved candidate']);
      await assert.rejects(confirmAdoption(history, editedPreparation, { reference: 'unapproved-action', status: 'succeeded' }));
      const rejectedCandidate = await confirmAdoption(history, approvalRecord, { reference: 'unapproved-action', status: 'succeeded' });
      assert.equal(rejectedCandidate.status, 'uncertain');
      assert.equal(rejectedCandidate.approval.candidate.sha256, sha(candidateText));
      await assert.rejects(prepareRevert(history, await saveOperation('unapproved-result', rejectedCandidate), { reference: 'revert' }));
      await assert.rejects(confirmAdoption(history, { ...approvalRecord, sha256: sha(JSON.stringify(editedPreparation)) },
        { reference: 'unapproved-action', status: 'succeeded' }), /digest/);
      repo.git(['reset', '--hard', originalRevision]);
      writeFileSync(join(repo.path, path), candidateText);
      repo.git(['add', path]); repo.git(['commit', '-m', 'Apply approved candidate']);
      const adopted = await confirmAdoption(history, approvalRecord, { reference: 'fixture-action', status: 'succeeded' });
      assert.equal(adopted.status, 'applied');
      const adoptedRecord = await saveOperation('adoption-result', adopted);
      const savedAdoption = retained(adoptedRecord.invocationId).value;
      assert.equal(savedAdoption.applied.revision, adopted.applied.revision);
      const preparedRevert = await prepareRevert(history, adoptedRecord, { reference: 'fixture-revert-approval' });
      const revertApprovalRecord = await saveOperation('revert-approval', preparedRevert);
      assert.equal(retained(revertApprovalRecord.invocationId).value.kind, 'revert-preparation');
      writeFileSync(join(repo.path, path), originalText);
      repo.git(['add', path]); repo.git(['commit', '-m', 'Revert approved candidate']);
      const reverted = await confirmRevert(history, revertApprovalRecord, { reference: 'fixture-revert-action', status: 'succeeded' });
      assert.equal(reverted.status, 'reverted');
      const revertRecord = await saveOperation('revert-result', reverted);
      assert.equal(retained(revertRecord.invocationId).value.reverted.revision, reverted.reverted.revision);
      assert.equal(reverted.originalAdoption.approval.extraction.invocationId, extraction.invocationId);
      assert.equal(reverted.originalAdoption.approval.evaluation.invocationId, revisedRun.invocationId);
      assert.equal(reverted.originalAdoption.approval.candidate.captureId, candidateId);
      assert.equal(reverted.reverted.revision, repo.git(['rev-parse', 'HEAD']).trim());
    } finally { historyStore.close(); }
    const check = openRepositoryStore(common);
    try { assert.equal(check.readHistory(inconclusiveRun.invocationId, { limit: 100 }).invocation.outcome, 'succeeded');
      assert.equal(check.readHistory(extraction.invocationId, { limit: 100 }).invocation.outcome, 'succeeded'); }
    finally { check.close(); }
  } finally { repo.dispose(); }
});

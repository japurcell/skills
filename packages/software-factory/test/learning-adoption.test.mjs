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
  const report = {
    version: 1, assessment: 'supported', limitations: [], target: { scope: 'repository', path },
    suppliedReferences: { extraction, baseline: { invocationId: 'source-1', captureId: 'baseline-1', sha256: sha(originalText) }, candidate },
    extractionReport: { captureId: 'extraction-report-1', sha256: sha('extraction report') },
    extractionResult: { attemptId: 'extract-attempt-1', rawCaptureId: 'raw-1', validatedCaptureId: 'validated-1' },
    resolved: { baselineSha256: sha(originalText), candidateSha256: sha(candidateText) },
    cases: [{ key: 'check' }],
  };
  const reportText = JSON.stringify(report);
  const evaluation = { invocationId: 'evaluation-1', reportCaptureId: 'evaluation-report-1', sha256: sha(reportText) };
  const captures = new Map([[evaluation.reportCaptureId, { channel: 'report', text: reportText }], [candidate.captureId, { channel: 'event', text: candidateText }]]);
  const evaluations = new Map([[evaluation.invocationId, evaluation.reportCaptureId]]);
  const addEvaluation = (value, suffix) => {
    const text = JSON.stringify(value);
    const reference = { invocationId: `evaluation-${suffix}`, reportCaptureId: `evaluation-report-${suffix}`, sha256: sha(text) };
    captures.set(reference.reportCaptureId, { channel: 'report', text });
    evaluations.set(reference.invocationId, reference.reportCaptureId);
    return reference;
  };
  const sourceHistory = {
    async read(id) {
      const captureId = id === candidate.invocationId ? candidate.captureId : evaluations.get(id);
      return { invocation: { id, stage: 'finalized', outcome: 'succeeded' },
        captures: captureId ? [{ id: captureId, channel: captures.get(captureId).channel, state: 'complete' }] : [],
        capturesNextCursor: 1, hasMoreCaptures: false };
    },
    async capture(_invocationId, id) { const capture = captures.get(id); assert.ok(capture); return {
      id, channel: capture.channel, state: 'complete', chunks: [{ sequence: 1, text: capture.text }], nextSequence: 1, hasMore: false,
    }; },
  };
  const approval = { reference: 'human-approval-1', extraction, evaluation, candidate,
    target: { repository: repo.path, scope: 'repository', path, expectedRevision: revision, expectedSha256: sha(originalText) } };
  return { repo, sourceHistory, approval, report, addEvaluation, captures };
}

test('explicit approved action records actual committed candidate and actual revert', async () => {
  const f = fixture();
  try {
    const prepared = await prepareAdoption(f.sourceHistory, f.approval);
    assert.equal(prepared.approval.reference, 'human-approval-1');
    const unacted = await confirmAdoption(prepared, { reference: 'action-1', status: 'succeeded' });
    assert.equal(unacted.status, 'not_applied');
    assert.equal('applied' in unacted, false);

    writeFileSync(join(f.repo.path, path), candidateText);
    f.repo.git(['add', path]);
    f.repo.git(['commit', '-m', 'Adopt candidate']);
    const adopted = await confirmAdoption(prepared, { reference: 'action-2', status: 'succeeded' });
    assert.equal(adopted.status, 'applied');
    assert.equal(adopted.applied.revision, f.repo.git(['rev-parse', 'HEAD']).trim());
    assert.equal(adopted.applied.sha256, f.approval.candidate.sha256);
    assert.deepEqual(adopted.approval.evaluation, f.approval.evaluation);

    const reverting = await prepareRevert(adopted, { reference: 'human-revert-1' });
    writeFileSync(join(f.repo.path, path), originalText);
    f.repo.git(['add', path]);
    f.repo.git(['commit', '-m', 'Revert candidate']);
    const reverted = await confirmRevert(reverting, { reference: 'revert-action-1', status: 'succeeded' });
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
    f.captures.set(approved.candidate.captureId, { channel: 'event', text: 'changed captured candidate\n' });
    await assert.rejects(prepareAdoption(f.sourceHistory, approved), /approved candidate bytes changed/);
    f.captures.set(approved.candidate.captureId, { channel: 'event', text: candidateText });
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
    assert.equal((await confirmAdoption(prepared, { reference: 'failure-1', status: 'failed' })).status, 'not_applied');
    assert.equal((await confirmAdoption(prepared, { reference: 'unknown-1', status: 'uncertain' })).status, 'not_applied');
    writeFileSync(join(f.repo.path, path), candidateText);
    f.repo.git(['add', path]);
    f.repo.git(['commit', '-m', 'Candidate after failed action']);
    for (const status of ['failed', 'uncertain']) {
      const result = await confirmAdoption(prepared, { reference: `action-${status}`, status });
      assert.equal(result.status, 'uncertain');
      assert.equal('applied' in result, false);
    }
  } finally { f.repo.dispose(); }
});

test('revert needs an applied record and fresh approval; failed or changed revert cannot claim restored revision', async () => {
  const f = fixture();
  try {
    const prepared = await prepareAdoption(f.sourceHistory, f.approval);
    const unacted = await confirmAdoption(prepared, { reference: 'unacted', status: 'succeeded' });
    await assert.rejects(prepareRevert(unacted, { reference: 'revert' }), /applied adoption/);
    writeFileSync(join(f.repo.path, path), candidateText);
    f.repo.git(['add', path]); f.repo.git(['commit', '-m', 'Apply candidate']);
    const adopted = await confirmAdoption(prepared, { reference: 'adopted', status: 'succeeded' });
    assert.equal(adopted.status, 'applied');
    await assert.rejects(prepareRevert(adopted, { reference: '' }), /explicit approval/);
    const reverting = await prepareRevert(adopted, { reference: 'revert-approval' });
    assert.equal((await confirmRevert(reverting, { reference: 'failed-revert', status: 'failed' })).status, 'not_reverted');
    writeFileSync(join(f.repo.path, path), 'another target\n');
    f.repo.git(['add', path]); f.repo.git(['commit', '-m', 'Change post-adoption target']);
    await assert.rejects(prepareRevert(adopted, { reference: 'stale-revert' }), /renewed review/);
    writeFileSync(join(f.repo.path, path), originalText);
    f.repo.git(['add', path]); f.repo.git(['commit', '-m', 'Restore after intervening change']);
    const result = await confirmRevert(reverting, { reference: 'late-revert', status: 'succeeded' });
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
    const wrong = await confirmAdoption(prepared, { reference: 'wrong-1', status: 'succeeded' });
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
    const result = await confirmAdoption(prepared, { reference: 'scope-1', status: 'succeeded' });
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
    const result = await confirmAdoption(prepared, { reference: 'intervening-1', status: 'succeeded' });
    assert.equal(result.status, 'uncertain');
    assert.equal('applied' in result, false);
  } finally { intervening.repo.dispose(); }
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
    const saveOperation = async (name, value) => {
      const recorder = openRepositoryStore(common);
      try {
        const run = await recorder.createRun();
        const invocation = await recorder.startInvocation({ runId: run.id, worktreeId: sourceWorktreeId,
          owner: { host: 'fixture', pid: process.pid, start: null } });
        await recorder.saveInvocationMetadata(invocation.id, { workflow: `explicit-learning/${name}` });
        const capture = await recorder.createCapture({ invocationId: invocation.id, channel: 'report' });
        await recorder.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text: JSON.stringify(value) }], state: 'complete' });
        await recorder.finalizeInvocation({ id: invocation.id, outcome: 'succeeded', cleanup: 'complete',
          claimId: invocation.claim.id, token: invocation.claim.token });
        return { invocationId: invocation.id, captureId: capture.id };
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
      const prepared = await prepareAdoption(history, approval);
      assert.deepEqual(prepared.evidence.extractionReport, revised.value.extractionReport);
      assert.deepEqual(prepared.evidence.extractionResult, revised.value.extractionResult);
      const approvalRecord = await saveOperation('adoption-approval', prepared);
      assert.equal(retained(approvalRecord.invocationId).value.kind, 'adoption-preparation');
      writeFileSync(join(repo.path, path), candidateText);
      repo.git(['add', path]); repo.git(['commit', '-m', 'Apply approved candidate']);
      const adopted = await confirmAdoption(prepared, { reference: 'fixture-action', status: 'succeeded' });
      assert.equal(adopted.status, 'applied');
      const adoptedRecord = await saveOperation('adoption-result', adopted);
      const savedAdoption = retained(adoptedRecord.invocationId).value;
      assert.equal(savedAdoption.applied.revision, adopted.applied.revision);
      const preparedRevert = await prepareRevert(savedAdoption, { reference: 'fixture-revert-approval' });
      const revertApprovalRecord = await saveOperation('revert-approval', preparedRevert);
      assert.equal(retained(revertApprovalRecord.invocationId).value.kind, 'revert-preparation');
      writeFileSync(join(repo.path, path), originalText);
      repo.git(['add', path]); repo.git(['commit', '-m', 'Revert approved candidate']);
      const reverted = await confirmRevert(preparedRevert, { reference: 'fixture-revert-action', status: 'succeeded' });
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

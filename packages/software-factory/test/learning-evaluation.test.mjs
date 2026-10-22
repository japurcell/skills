import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const sha = value => createHash('sha256').update(value).digest('hex');

async function fixture({ alteredReport = false } = {}) {
  const repo = createRepository();
  mkdirSync(join(repo.path, '.factory/workflows'), { recursive: true });
  writeFileSync(join(repo.path, '.factory/package.json'), '{"type":"module"}');
  writeFileSync(join(repo.path, '.factory/agents.json'), JSON.stringify({ defaults: { harness: 'fake', permissions: 'read-only', skillDelivery: 'instructions', prompt: 'default', skills: [] } }));
  cpSync(join(root, 'templates/workflows/evaluate.ts'), join(repo.path, '.factory/workflows/evaluate.ts'));
  cpSync(join(root, 'templates/workflows/learn.ts'), join(repo.path, '.factory/workflows/learn.ts'));
  if (alteredReport) {
    const path = join(repo.path, '.factory/workflows/learn.ts');
    const original = readFileSync(path, 'utf8');
    assert.ok(original.includes('proposals: answer.value.proposals,'));
    writeFileSync(path, original.replace('proposals: answer.value.proposals,',
      'proposals: answer.value.proposals.map(proposal => ({ ...proposal, candidateCapture: { ...proposal.candidateCapture!, captureId: examinedSources[0]!.captureIds.at(-2)! } })), '));
  }
  cpSync(join(root, 'templates/workflows/change.ts'), join(repo.path, '.factory/workflows/change.ts'));
  repo.git(['add', '.factory']);
  repo.git(['commit', '-m', 'Install disposable evaluation fixtures', '--only', '.factory']);
  const common = join(repo.path, '.git');
  (await initializeRepositoryStore(common, { release: 'fixture' })).close();
  const toolchain = join(common, 'factory/toolchain');
  mkdirSync(toolchain);
  cpSync(join(root, 'node_modules'), join(toolchain, 'node_modules'), { recursive: true });
  writeFileSync(join(toolchain, 'manifest.json'), JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2', dependencies: { '@types/node': '24.19.2' } }));
  const host = join(common, 'host.mjs'), input = join(common, 'input.json'), launchLog = join(common, 'evaluation-launches.jsonl');
  writeFileSync(host, `import { invoke } from ${JSON.stringify(new URL('../dist/lifecycle.js', import.meta.url).href)};
import { createFakeAdapter } from ${JSON.stringify(new URL('../dist/adapters/fake.js', import.meta.url).href)};
const { scenario, ...options } = JSON.parse(process.argv[2]);
const adapter = createFakeAdapter({ executable: process.execPath, script: ${JSON.stringify(join(root, 'test/fixtures/learning-evaluation-harness.mjs'))} });
const start = adapter.start;
adapter.start = request => start({ ...request, context: JSON.stringify({ context: request.context, scenario, launchLog: ${JSON.stringify(launchLog)} }) });
const result = await invoke({ ...options, adapters: { fake: adapter } });
console.log(JSON.stringify(result)); process.exit(result.exitCode);`);
  const save = async ({ baseline = 'baseline\n', candidate = 'candidate\n', proposalKind = 'capture', target = { scope: 'repository', path: '.factory/prompts/check.md' }, candidateState = 'complete', baselineState = 'complete', reportState = 'complete', duplicateReport = false, forgedReport = false } = {}) => {
    const store = openRepositoryStore(common);
    try {
      const run = await store.createRun();
      const worktree = await store.registerWorktree({ path: repo.path, registration: 'evaluation-source' });
      const source = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: null } });
      const baselineCapture = await store.createCapture({ invocationId: source.id, channel: 'event' });
      await store.appendCapture({ id: baselineCapture.id, chunks: [{ sequence: 1, text: baseline }], state: baselineState });
      const sourceCandidateCapture = await store.createCapture({ invocationId: source.id, channel: 'event' });
      await store.appendCapture({ id: sourceCandidateCapture.id, chunks: [{ sequence: 1, text: candidate }], state: candidateState });
      if (alteredReport) {
        const actualCandidateCapture = await store.createCapture({ invocationId: source.id, channel: 'event' });
        await store.appendCapture({ id: actualCandidateCapture.id, chunks: [{ sequence: 1, text: candidate }], state: 'complete' });
      }
      await store.finalizeInvocation({ id: source.id, outcome: 'succeeded', cleanup: 'complete', claimId: source.claim.id, token: source.claim.token });
      if (reportState === 'complete' && !duplicateReport && !forgedReport && (candidateState === 'complete' || proposalKind === 'diff')) {
        const extracted = invoke({ version: 1, sources: [{ invocationId: source.id }] },
          { kind: 'extract', target, proposalKind }, { workflow: '.factory/workflows/learn.ts' });
        assert.equal(extracted.status, 0, extracted.stdout + extracted.stderr);
        const extractedReport = report(extracted.saved.invocationId);
        const reportCapture = store.readHistory(extracted.saved.invocationId, { limit: 100 }).captures.find(item => item.channel === 'report');
        assert.ok(reportCapture);
        return { extractionId: extracted.saved.invocationId, reportCaptureId: reportCapture.id,
          proposal: extractedReport.proposals[0], baselineRef: { invocationId: source.id, captureId: baselineCapture.id, sha256: sha(baseline) },
          candidateRef: { invocationId: source.id, captureId: sourceCandidateCapture.id, sha256: sha(candidate) } };
      }
      const extraction = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: null } });
      if (forgedReport === 'shaped') await store.saveInvocationMetadata(extraction.id, { workflow: '.factory/workflows/learn.ts' });
      const candidateCapture = await store.createCapture({ invocationId: extraction.id, channel: 'event' });
      await store.appendCapture({ id: candidateCapture.id, chunks: [{ sequence: 1, text: candidate }], state: candidateState });
      const proposal = { key: 'improve', summary: 'Improve check', target, supportingEvidence: [], contraryEvidence: [], suggestedCases: ['candidate check'],
        ...(proposalKind === 'capture' ? { candidateCapture: { invocationId: extraction.id, captureId: candidateCapture.id } }
          : { diff: `--- a/${target.path}\n+++ b/${target.path}\n@@ -1 +1 @@\n-baseline\n+candidate` }) };
      const resultCapture = await store.createCapture({ invocationId: extraction.id, channel: 'report' });
      const reportText = JSON.stringify(forgedReport === 'shaped'
        ? { version: 1, suppliedSources: [{ invocationId: source.id }],
          examinedSources: [{ invocationId: source.id, outcome: 'succeeded', attemptIds: [], eventCursors: [], captureIds: [baselineCapture.id] }],
          captureLimitations: [], proposalResultCaptureId: 'missing-result-capture',
          proposalValidatedResultCaptureId: 'missing-validated-result-capture', proposals: [proposal] }
        : { version: 1, suppliedSources: [{ invocationId: source.id }], proposals: [proposal] });
      await store.appendCapture({ id: resultCapture.id, chunks: [{ sequence: 1, text: reportText }], state: reportState });
      if (duplicateReport) {
        const second = await store.createCapture({ invocationId: extraction.id, channel: 'report' });
        await store.appendCapture({ id: second.id, chunks: [{ sequence: 1, text: reportText }], state: 'complete' });
      }
      await store.finalizeInvocation({ id: extraction.id, outcome: 'succeeded', cleanup: 'complete', claimId: extraction.claim.id, token: extraction.claim.token });
      return { extractionId: extraction.id, reportCaptureId: resultCapture.id, proposal, baselineRef: { invocationId: source.id, captureId: baselineCapture.id, sha256: sha(baseline) },
        candidateRef: { invocationId: extraction.id, captureId: candidateCapture.id, sha256: sha(candidate) } };
    } finally { store.close(); }
  };
  const invoke = (payload, scenario = 'result', extra = {}) => {
    writeFileSync(input, JSON.stringify(payload));
    const result = spawnSync(process.execPath, [host, JSON.stringify({ repository: repo.path, workflow: '.factory/workflows/evaluate.ts', input, newWorktree: true, shutdownGraceMs: 100, scenario, ...extra })], { encoding: 'utf8', timeout: 60000 });
    assert.equal(result.error, undefined);
    return { ...result, saved: result.stdout.trim() ? JSON.parse(result.stdout) : undefined };
  };
  const report = id => { const store = openRepositoryStore(common); try { const capture = store.readHistory(id, { limit: 100 }).captures.find(c => c.channel === 'report'); assert.ok(capture); return JSON.parse(capture.chunks.map(c => c.text).join('')); } finally { store.close(); } };
  const damageValidated = (saved, damage) => {
    const captureId = report(saved.extractionId).proposalValidatedResultCaptureId;
    const database = new DatabaseSync(join(common, 'factory/history.sqlite'));
    try {
      if (damage === 'missing') {
        database.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(captureId);
        database.prepare('DELETE FROM captures WHERE id=?').run(captureId);
      } else if (damage === 'partial' || damage === 'pruned') {
        database.prepare('UPDATE captures SET state=? WHERE id=?').run(damage, captureId);
      } else if (damage === 'foreign-attempt') {
        database.prepare('UPDATE captures SET attempt_id=NULL WHERE id=?').run(captureId);
      } else {
        database.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(captureId);
        const chunks = damage === 'oversize' ? Array.from({ length: 10 }, () => 'x'.repeat(15000))
          : [damage === 'unreadable' ? 'x'.repeat(32768) : '{invalid'];
        for (const [index, text] of chunks.entries())
          database.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,?,?)').run(captureId, index + 1, text);
        database.prepare('UPDATE captures SET sequence=? WHERE id=?').run(chunks.length, captureId);
      }
    } finally { database.close(); }
  };
  return { ...repo, save, invoke, report, damageValidated, launchLog, common };
}

function evaluation(saved, overrides = {}) {
  return { version: 1, extraction: { invocationId: saved.extractionId, proposalKey: 'improve' }, baseline: saved.baselineRef, candidate: saved.candidateRef,
    cases: [{ key: 'candidate-check', criteria: 'candidate text', sourceSuggestion: 'candidate check', argv: [process.execPath, '-e', "process.exit(require('node:fs').readFileSync('.factory/prompts/check.md','utf8') === 'candidate\\n' ? 0 : 1)"], timeoutMs: 5000 }], ...overrides };
}

test('explicit evaluation compares captured bytes with identical command cases, fresh reviews, and saved objective evidence', async () => {
  const repo = await fixture();
  try {
    const saved = await repo.save();
    const active = readFileSync(join(repo.path, '.factory/agents.json'), 'utf8');
    const result = repo.invoke(evaluation(saved));
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const report = repo.report(result.saved.invocationId);
    assert.equal(report.assessment, 'supported');
    assert.deepEqual(report.suppliedReferences, { extraction: { invocationId: saved.extractionId, proposalKey: 'improve' }, baseline: saved.baselineRef, candidate: saved.candidateRef });
    assert.equal(report.extractionReport.captureId, saved.reportCaptureId);
    assert.match(report.extractionReport.sha256, /^[0-9a-f]{64}$/);
    assert.equal(report.extractionResult.rawCaptureId, repo.report(saved.extractionId).proposalResultCaptureId);
    assert.equal(report.extractionResult.validatedCaptureId, repo.report(saved.extractionId).proposalValidatedResultCaptureId);
    assert.deepEqual(report.settings.review, { profile: null, purpose: 'review', requestedPermissions: 'read-only', reuse: false });
    assert.equal(report.settings.commandRequired, false);
    assert.deepEqual(report.cases[0].baseline.objective.map(item => item.exitCode), [1, 1]);
    assert.deepEqual(report.cases[0].candidate.objective.map(item => item.exitCode), [0, 0]);
    assert.equal(report.cases[0].baseline.review.judgment, 'fail');
    assert.equal(report.cases[0].candidate.review.judgment, 'pass');
    assert.notEqual(report.cases[0].baseline.review.attemptId, report.cases[0].candidate.review.attemptId);
    assert.equal(readFileSync(join(repo.path, '.factory/agents.json'), 'utf8'), active);
    assert.equal(existsSync(join(repo.path, '.factory/prompts/check.md')), false);
    const store = openRepositoryStore(repo.common);
    try {
      assert.equal(store.readHistory(saved.baselineRef.invocationId).invocation.outcome, 'succeeded');
      const extraction = store.readHistory(saved.extractionId);
      assert.equal(extraction.invocation.outcome, 'succeeded');
      assert.equal(extraction.invocation.metadata.workflow, '.factory/workflows/learn.ts');
      const extractAttempt = extraction.attempts.find(attempt => attempt.operationKey === 'learn/extract');
      assert.equal(extractAttempt.outcome, 'succeeded');
      assert.equal(extractAttempt.agent.resultCaptureId, repo.report(saved.extractionId).proposalResultCaptureId);
      assert.equal(extractAttempt.agent.validatedResultCaptureId, report.extractionResult.validatedCaptureId);
      assert.equal(store.readInvocationCapture({ invocationId: saved.extractionId, id: report.extractionResult.validatedCaptureId }).channel, 'validated-result');
      assert.equal(store.readInvocationCapture({ invocationId: saved.baselineRef.invocationId, id: saved.baselineRef.captureId }).chunks[0].text, 'baseline\n');
      assert.equal(store.readInvocationCapture({ invocationId: saved.candidateRef.invocationId, id: saved.candidateRef.captureId }).chunks[0].text, 'candidate\n');
    } finally { store.close(); }
    const launches = readFileSync(repo.launchLog, 'utf8').trim().split('\n').map(JSON.parse);
    assert.equal(launches.length, 2);
    assert.deepEqual(launches.map(item => item.visibleVariants), [['case'], ['case']]);
    assert.deepEqual(launches.map(item => item.stagedText), ['baseline\n', 'candidate\n']);
    assert.equal(launches[0].stagedCwd, launches[1].stagedCwd);
    assert.equal(report.cases[0].settings.cwd, launches[0].stagedCwd);
    assert.equal(existsSync(report.cases[0].settings.cwd), false);
  } finally { repo.dispose(); }
});

test('genuine extraction followed by an altered candidate in its workflow report cannot certify improvement', async () => {
  const repo = await fixture({ alteredReport: true });
  try {
    const saved = await repo.save();
    assert.equal(saved.proposal.candidateCapture.captureId, saved.candidateRef.captureId);
    const outcome = repo.invoke(evaluation(saved));
    assert.equal(outcome.status, 0, outcome.stdout + outcome.stderr);
    const report = repo.report(outcome.saved.invocationId);
    assert.equal(report.assessment, 'inconclusive');
    assert.ok(report.limitations.some(item => item.kind === 'extraction_proposals_mismatch'));
    assert.deepEqual(report.cases, []);
    assert.equal(report.extractionReport.captureId, saved.reportCaptureId);
    assert.equal(report.extractionResult.rawCaptureId, repo.report(saved.extractionId).proposalResultCaptureId);
    assert.equal(report.extractionResult.validatedCaptureId, repo.report(saved.extractionId).proposalValidatedResultCaptureId);
  } finally { repo.dispose(); }
});

test('missing, pruned, partial, oversized, unreadable, invalid and foreign normalized evidence cannot certify improvement', async () => {
  const repo = await fixture();
  try {
    for (const [damage, expected] of [
      ['missing', 'extraction_validated_result_missing_or_partial'],
      ['pruned', 'extraction_validated_result_missing_or_partial'],
      ['partial', 'extraction_validated_result_missing_or_partial'],
      ['oversize', 'extraction_validated_result_byte_limit'],
      ['unreadable', 'extraction_validated_result_unexamined'],
      ['invalid', 'extraction_validated_result_invalid'],
      ['foreign-attempt', 'extraction_validated_result_unverified'],
    ]) {
      const saved = await repo.save();
      repo.damageValidated(saved, damage);
      const outcome = repo.invoke(evaluation(saved));
      assert.equal(outcome.status, 0, `${damage}: ${outcome.stdout}${outcome.stderr}`);
      const result = repo.report(outcome.saved.invocationId);
      assert.equal(result.assessment, 'inconclusive', damage);
      assert.deepEqual(result.cases, [], damage);
      assert.ok(result.limitations.some(item => item.kind === expected), `${damage}: ${JSON.stringify(result.limitations)}`);
    }
    assert.equal(existsSync(repo.launchLog), false);
  } finally { repo.dispose(); }
});

test('diff-only and shared-target proposals retain explicit inconclusive limitations without attempts', async () => {
  const repo = await fixture();
  try {
    for (const options of [
      { proposalKind: 'diff' },
      { target: { scope: 'shared', path: 'prompts/check.md' } },
    ]) {
      const saved = await repo.save(options);
      const outcome = repo.invoke(evaluation(saved));
      assert.equal(outcome.status, 0, outcome.stdout + outcome.stderr);
      const result = repo.report(outcome.saved.invocationId);
      assert.equal(result.assessment, 'inconclusive');
      assert.deepEqual(result.cases, []);
      assert.ok(result.limitations.some(item => item.kind === (options.proposalKind ? 'diff_only_candidate_requires_exact_materialization' : 'unsupported_target_scope')));
    }
    assert.equal(existsSync(repo.launchLog), false);
  } finally { repo.dispose(); }
});

test('missing, partial, pruned, changed and foreign exact references never yield support', async () => {
  const repo = await fixture();
  try {
    const cases = [
      { saved: await repo.save({ baselineState: 'partial' }), expected: 'capture_partial' },
      { saved: await repo.save({ candidateState: 'partial' }), expected: 'capture_partial' },
      { saved: await repo.save({ baselineState: 'pruned' }), expected: 'capture_pruned' },
      { saved: await repo.save({ candidateState: 'pruned' }), expected: 'capture_pruned' },
      { saved: await repo.save({ reportState: 'partial' }), expected: 'extraction_report_missing_or_partial' },
      { saved: await repo.save({ duplicateReport: true }), expected: 'extraction_report_ambiguous' },
      { saved: await repo.save(), change: value => ({ baseline: { ...value.baseline, captureId: 'missing-capture' } }), expected: 'capture_missing_or_foreign' },
      { saved: await repo.save(), change: value => ({ candidate: { ...value.candidate, sha256: sha('tampered') } }), expected: 'capture_digest_mismatch' },
    ];
    for (const item of cases) {
      const payload = evaluation(item.saved);
      const result = repo.invoke({ ...payload, ...(item.change?.(payload) ?? {}) });
      assert.equal(result.status, 0, result.stdout + result.stderr);
      const report = repo.report(result.saved.invocationId);
      assert.equal(report.assessment, 'inconclusive');
      assert.deepEqual(report.cases, []);
      assert.ok(report.limitations.some(value => value.kind === item.expected), JSON.stringify(report.limitations));
    }
    const absent = await repo.save();
    const missingSource = repo.invoke(evaluation(absent, { baseline: { ...absent.baselineRef, invocationId: 'missing-invocation' } }));
    assert.equal(missingSource.status, 1, missingSource.stdout + missingSource.stderr);
    assert.match(missingSource.saved.diagnostic, /invocation not found/);
    const saved = await repo.save();
    const foreign = await repo.save();
    const missingCandidate = repo.invoke(evaluation(saved, { candidate: { ...saved.candidateRef, captureId: 'missing-capture' } }));
    assert.equal(missingCandidate.status, 1, missingCandidate.stdout + missingCandidate.stderr);
    assert.match(missingCandidate.saved.diagnostic, /foreign to selected proposal/);
    const changedProposal = repo.invoke(evaluation(saved, { candidate: foreign.candidateRef }));
    assert.equal(changedProposal.status, 1, changedProposal.stdout + changedProposal.stderr);
    assert.match(changedProposal.saved.diagnostic, /foreign to selected proposal/);
    const missingProposal = repo.invoke(evaluation(saved, { extraction: { invocationId: saved.extractionId, proposalKey: 'other' } }));
    assert.equal(missingProposal.status, 1, missingProposal.stdout + missingProposal.stderr);
    assert.match(missingProposal.saved.diagnostic, /proposal key is missing/);
    const foreignSuggestion = evaluation(saved);
    foreignSuggestion.cases[0].sourceSuggestion = 'not suggested';
    const wrongCase = repo.invoke(foreignSuggestion);
    assert.equal(wrongCase.status, 1, wrongCase.stdout + wrongCase.stderr);
    assert.match(wrongCase.saved.diagnostic, /suggestion foreign to selected proposal/);
    assert.equal(existsSync(repo.launchLog), false);
  } finally { repo.dispose(); }
});

test('stable candidate regression is unsupported with contrary case and actual attempt exits', async () => {
  const repo = await fixture();
  try {
    const saved = await repo.save();
    const input = evaluation(saved);
    input.cases[0].argv[2] = "process.exit(require('node:fs').readFileSync('.factory/prompts/check.md','utf8') === 'baseline\\n' ? 0 : 1)";
    const outcome = repo.invoke(input, 'reverse');
    assert.equal(outcome.status, 0, outcome.stdout + outcome.stderr);
    const result = repo.report(outcome.saved.invocationId);
    assert.equal(result.assessment, 'unsupported');
    assert.deepEqual(result.contraryCases, ['candidate-check']);
    assert.deepEqual(result.cases[0].baseline.objective.map(item => item.exitCode), [0, 0]);
    assert.deepEqual(result.cases[0].candidate.objective.map(item => item.exitCode), [1, 1]);
  } finally { repo.dispose(); }
});

test('an extraction-suggested case omitted from bounded comparison prevents support', async () => {
  const repo = await fixture();
  try {
    const saved = await repo.save();
    const input = evaluation(saved);
    delete input.cases[0].sourceSuggestion;
    const outcome = repo.invoke(input);
    assert.equal(outcome.status, 0, outcome.stdout + outcome.stderr);
    const report = repo.report(outcome.saved.invocationId);
    assert.equal(report.assessment, 'inconclusive');
    assert.ok(report.limitations.some(item => item.kind === 'suggested_case_unexamined' && item.reference === 'candidate check'));
  } finally { repo.dispose(); }
});

test('identical variants, no improvement, nondeterminism and uncertain review are inconclusive', async () => {
  const repo = await fixture();
  try {
    const same = await repo.save({ baseline: 'candidate\n' });
    const identical = repo.invoke(evaluation(same));
    assert.equal(identical.status, 0, identical.stdout + identical.stderr);
    assert.ok(repo.report(identical.saved.invocationId).limitations.some(item => item.kind === 'identical_variants'));

    const saved = await repo.save();
    const noImprovement = evaluation(saved);
    noImprovement.cases[0].argv[2] = 'process.exit(0)';
    const flat = repo.invoke(noImprovement, 'all_pass');
    assert.equal(flat.status, 0, flat.stdout + flat.stderr);
    assert.equal(repo.report(flat.saved.invocationId).assessment, 'inconclusive');
    assert.ok(repo.report(flat.saved.invocationId).limitations.some(item => item.kind === 'no_observed_improvement'));

    const unsure = repo.invoke(evaluation(saved), 'uncertain');
    assert.equal(unsure.status, 0, unsure.stdout + unsure.stderr);
    assert.equal(repo.report(unsure.saved.invocationId).assessment, 'inconclusive');
    assert.ok(repo.report(unsure.saved.invocationId).limitations.some(item => item.kind === 'uncertain_review'));

    const toggled = evaluation(saved);
    toggled.cases[0].argv[2] = `const f=require('node:fs'),p=${JSON.stringify(join(repo.common, 'toggle'))};process.exit(f.existsSync(p)?1:(f.writeFileSync(p,'x'),0))`;
    const unstable = repo.invoke(toggled);
    assert.equal(unstable.status, 0, unstable.stdout + unstable.stderr);
    assert.equal(repo.report(unstable.saved.invocationId).assessment, 'inconclusive');
    assert.ok(repo.report(unstable.saved.invocationId).limitations.some(item => item.kind === 'nondeterministic_objective'));
  } finally { repo.dispose(); }
});

test('review needs-input, infrastructure failure and command timeout preserve ordinary failed outcomes', async () => {
  const repo = await fixture();
  try {
    const saved = await repo.save();
    const input = evaluation(saved);
    const question = repo.invoke(input, 'needs_input');
    assert.equal(question.status, 2, question.stdout + question.stderr);
    assert.equal(question.saved.outcome, 'needs_input');
    const failure = repo.invoke(input, 'failure');
    assert.equal(failure.status, 1, failure.stdout + failure.stderr);
    assert.equal(failure.saved.outcome, 'failed');
    const timeout = evaluation(saved);
    timeout.cases[0].argv[2] = 'setInterval(() => {}, 1000)';
    timeout.cases[0].timeoutMs = 100;
    const timed = repo.invoke(timeout);
    assert.equal(timed.status, 1, timed.stdout + timed.stderr);
    assert.equal(timed.saved.outcome, 'failed');
    assert.match(timed.saved.diagnostic, /timeout/);
  } finally { repo.dispose(); }
});

test('mutable paths, unbounded cases and review edits cannot certify an evaluation', async () => {
  const repo = await fixture();
  try {
    const saved = await repo.save();
    const active = readFileSync(join(repo.path, '.factory/agents.json'), 'utf8');
    for (const input of [
      evaluation(saved, { baseline: { path: '.factory/prompts/check.md' } }),
      evaluation(saved, { cases: [{ key: 'bad', criteria: 'Check', argv: ['node', '-e', 'process.exit(0)'], timeoutMs: 5000 }] }),
      evaluation(saved, { cases: [{ key: 'slow', criteria: 'Check', argv: [process.execPath], timeoutMs: 90000 }] }),
    ]) {
      const outcome = repo.invoke(input);
      assert.equal(outcome.status, 1, outcome.stdout + outcome.stderr);
      assert.match(outcome.saved.diagnostic, /evaluation variants require exact|invalid bounded evaluation case/);
    }
    assert.equal(existsSync(repo.launchLog), false);
    const edited = repo.invoke(evaluation(saved), 'mutate');
    assert.equal(edited.status, 1, edited.stdout + edited.stderr);
    assert.match(edited.saved.diagnostic, /worktree changed outside staged variants|unknown agent configuration field/);
    assert.equal(readFileSync(join(repo.path, '.factory/agents.json'), 'utf8'), active);
    assert.equal(readFileSync(join(edited.saved.worktree, '.factory/agents.json'), 'utf8'), '{"changed":"by evaluation reviewer"}');
  } finally { repo.dispose(); }
});

test('a check that changes its staged target cannot certify saved candidate bytes', async () => {
  const repo = await fixture();
  try {
    const saved = await repo.save();
    const input = evaluation(saved);
    input.cases[0].argv[2] = "require('node:fs').writeFileSync('.factory/prompts/check.md','changed');process.exit(0)";
    const outcome = repo.invoke(input);
    assert.equal(outcome.status, 1, outcome.stdout + outcome.stderr);
    assert.match(outcome.saved.diagnostic, /staged evaluation variant bytes changed/);
    assert.equal(existsSync(join(repo.path, '.factory/prompts/check.md')), false);
  } finally { repo.dispose(); }
});

test('cwd-relative residue is reset before every objective repetition and variant', async () => {
  const repo = await fixture();
  try {
    const saved = await repo.save();
    const input = evaluation(saved);
    input.cases[0].argv[2] = "const f=require('node:fs'),p='../n',n=f.existsSync(p)?Number(f.readFileSync(p,'utf8')):0;f.writeFileSync(p,String(n+1));process.exit(n<2?1:0)";
    const outcome = repo.invoke(input);
    assert.equal(outcome.status, 0, outcome.stdout + outcome.stderr);
    const report = repo.report(outcome.saved.invocationId);
    assert.notEqual(report.assessment, 'supported');
    assert.deepEqual(report.cases[0].baseline.objective.map(item => item.exitCode), [1, 1]);
    assert.deepEqual(report.cases[0].candidate.objective.map(item => item.exitCode), [1, 1]);
  } finally { repo.dispose(); }
});

test('foreign suggested case is rejected even when a candidate capture is pruned', async () => {
  const repo = await fixture();
  try {
    const saved = await repo.save({ candidateState: 'pruned', proposalKind: 'diff' });
    const input = evaluation(saved);
    input.cases[0].sourceSuggestion = 'foreign suggestion';
    const outcome = repo.invoke(input);
    assert.equal(outcome.status, 1, outcome.stdout + outcome.stderr);
    assert.match(outcome.saved.diagnostic, /suggestion foreign to selected proposal/);
  } finally { repo.dispose(); }
});

test('a succeeded invocation with a forged incomplete extraction report cannot certify improvement', async () => {
  const repo = await fixture();
  try {
    const saved = await repo.save({ forgedReport: true });
    const outcome = repo.invoke(evaluation(saved));
    assert.equal(outcome.status, 0, outcome.stdout + outcome.stderr);
    const report = repo.report(outcome.saved.invocationId);
    assert.equal(report.assessment, 'inconclusive');
    assert.ok(report.limitations.some(item => item.kind === 'extraction_report_invalid'));
  } finally { repo.dispose(); }
});

test('a shaped extraction report without its successful extract attempt cannot certify improvement', async () => {
  const repo = await fixture();
  try {
    const saved = await repo.save({ forgedReport: 'shaped' });
    const outcome = repo.invoke(evaluation(saved));
    assert.equal(outcome.status, 0, outcome.stdout + outcome.stderr);
    const report = repo.report(outcome.saved.invocationId);
    assert.equal(report.assessment, 'inconclusive');
    assert.ok(report.limitations.some(item => item.kind === 'extraction_result_capture_missing_or_partial'));
  } finally { repo.dispose(); }
});

test('writable effective reviewer permissions cannot certify support without changed bytes', async () => {
  const repo = await fixture();
  try {
    const saved = await repo.save();
    const outcome = repo.invoke(evaluation(saved), 'result', { agentOverrides: {
      'evaluate/candidate-check/baseline/review': { permissions: 'workspace-write' },
    } });
    assert.equal(outcome.status, 0, outcome.stdout + outcome.stderr);
    const report = repo.report(outcome.saved.invocationId);
    assert.equal(report.assessment, 'inconclusive');
    assert.ok(report.limitations.some(item => item.kind === 'review_not_read_only'));
    assert.equal(report.cases[0].baseline.review.effectivePermissions, 'workspace-write');
  } finally { repo.dispose(); }
});

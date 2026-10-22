import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const sha = value => createHash('sha256').update(value).digest('hex');

async function fixture() {
  const repo = createRepository();
  mkdirSync(join(repo.path, '.factory/workflows'), { recursive: true });
  writeFileSync(join(repo.path, '.factory/package.json'), '{"type":"module"}');
  writeFileSync(join(repo.path, '.factory/agents.json'), JSON.stringify({ defaults: { harness: 'fake', permissions: 'read-only', skillDelivery: 'instructions', prompt: 'default', skills: [] } }));
  cpSync(join(root, 'templates/workflows/evaluate.ts'), join(repo.path, '.factory/workflows/evaluate.ts'));
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
  const save = async ({ baseline = 'baseline\n', candidate = 'candidate\n', proposalKind = 'capture', target = { scope: 'repository', path: '.factory/prompts/check.md' }, candidateState = 'complete', baselineState = 'complete', reportState = 'complete', duplicateReport = false } = {}) => {
    const store = openRepositoryStore(common);
    try {
      const run = await store.createRun();
      const worktree = await store.registerWorktree({ path: repo.path, registration: 'evaluation-source' });
      const source = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: null } });
      const baselineCapture = await store.createCapture({ invocationId: source.id, channel: 'event' });
      await store.appendCapture({ id: baselineCapture.id, chunks: [{ sequence: 1, text: baseline }], state: baselineState });
      await store.finalizeInvocation({ id: source.id, outcome: 'succeeded', cleanup: 'complete', claimId: source.claim.id, token: source.claim.token });
      const extraction = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: null } });
      const candidateCapture = await store.createCapture({ invocationId: extraction.id, channel: 'event' });
      await store.appendCapture({ id: candidateCapture.id, chunks: [{ sequence: 1, text: candidate }], state: candidateState });
      const proposal = { key: 'improve', summary: 'Improve check', target, supportingEvidence: [], contraryEvidence: [], suggestedCases: ['candidate check'],
        ...(proposalKind === 'capture' ? { candidateCapture: { invocationId: extraction.id, captureId: candidateCapture.id } }
          : { diff: `--- a/${target.path}\n+++ b/${target.path}\n@@ -1 +1 @@\n-baseline\n+candidate` }) };
      const resultCapture = await store.createCapture({ invocationId: extraction.id, channel: 'report' });
      const reportText = JSON.stringify({ version: 1, suppliedSources: [{ invocationId: source.id }], proposals: [proposal] });
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
  const invoke = (payload, scenario = 'result') => {
    writeFileSync(input, JSON.stringify(payload));
    const result = spawnSync(process.execPath, [host, JSON.stringify({ repository: repo.path, workflow: '.factory/workflows/evaluate.ts', input, newWorktree: true, shutdownGraceMs: 100, scenario })], { encoding: 'utf8', timeout: 60000 });
    assert.equal(result.error, undefined);
    return { ...result, saved: result.stdout.trim() ? JSON.parse(result.stdout) : undefined };
  };
  const report = id => { const store = openRepositoryStore(common); try { const capture = store.readHistory(id, { limit: 100 }).captures.find(c => c.channel === 'report'); assert.ok(capture); return JSON.parse(capture.chunks.map(c => c.text).join('')); } finally { store.close(); } };
  return { ...repo, save, invoke, report, launchLog, common };
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
      assert.equal(store.readHistory(saved.extractionId).invocation.outcome, 'succeeded');
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
    toggled.cases[0].argv[2] = "const f=require('node:fs');process.exit(f.existsSync('.toggle')?1:(f.writeFileSync('.toggle','x'),0))";
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

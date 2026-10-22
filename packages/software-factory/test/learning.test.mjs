import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));

async function fixture() {
  const repo = createRepository();
  mkdirSync(join(repo.path, '.factory/workflows'), { recursive: true });
  writeFileSync(join(repo.path, '.factory/package.json'), '{"type":"module"}');
  writeFileSync(join(repo.path, '.factory/agents.json'), JSON.stringify({ defaults: { harness: 'fake', permissions: 'read-only', skillDelivery: 'instructions', prompt: 'default', skills: [] } }));
  writeFileSync(join(repo.path, '.factory/workflows/source.ts'), `import type { WorkflowContext } from '@local/software-factory';
export async function run(context: WorkflowContext, input: Record<string, unknown>) {
  await context.progress('source event');
  if (input.mode === 'failed') throw new Error('selected source failed');
  if (input.mode === 'needs_input') await context.needsInput('Which target?', 'Target missing');
  if (input.mode === 'command') await context.command('observed', { argv: [process.execPath, '-e', 'process.stdout.write(String(42))'] });
  if (input.mode === 'wait') await context.command('wait', { argv: [process.execPath, '-e', 'setInterval(() => {}, 1000)'] });
  return { status: 'seed' };
}`);
  cpSync(join(root, 'templates/workflows/learn.ts'), join(repo.path, '.factory/workflows/learn.ts'));
  cpSync(join(root, 'templates/workflows/change.ts'), join(repo.path, '.factory/workflows/change.ts'));
  repo.git(['add', '.factory']);
  repo.git(['commit', '-m', 'Install disposable extraction fixtures', '--only', '.factory']);
  const common = join(repo.path, '.git');
  (await initializeRepositoryStore(common, { release: 'fixture' })).close();
  const toolchain = join(common, 'factory/toolchain');
  mkdirSync(toolchain);
  cpSync(join(root, 'node_modules'), join(toolchain, 'node_modules'), { recursive: true });
  writeFileSync(join(toolchain, 'manifest.json'), JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2', dependencies: { '@types/node': '24.19.2' } }));
  const host = join(common, 'host.mjs'), input = join(common, 'input.json'), launchLog = join(common, 'learn-launches.jsonl');
  writeFileSync(host, `import { invoke } from ${JSON.stringify(new URL('../dist/lifecycle.js', import.meta.url).href)};
import { createFakeAdapter } from ${JSON.stringify(new URL('../dist/adapters/fake.js', import.meta.url).href)};
const { scenario, ...options } = JSON.parse(process.argv[2]);
const adapter = createFakeAdapter({ executable: process.execPath, script: ${JSON.stringify(join(root, 'test/fixtures/learning-harness.mjs'))} });
const start = adapter.start;
adapter.start = request => start({ ...request, context: JSON.stringify({ context: request.context, scenario, launchLog: ${JSON.stringify(launchLog)} }) });
const result = await invoke({ ...options, adapters: { fake: adapter } });
console.log(JSON.stringify(result)); process.exit(result.exitCode);`);
  const invoke = (workflow, payload, scenario = { kind: 'result', payload: { proposals: [], noProposalReason: 'No justified change.' } }, extra = {}) => {
    writeFileSync(input, JSON.stringify(payload));
    const result = spawnSync(process.execPath, [host, JSON.stringify({ repository: repo.path, workflow: `.factory/workflows/${workflow}.ts`, input, newWorktree: true, shutdownGraceMs: 100, scenario, ...extra })], { encoding: 'utf8', timeout: 60000 });
    assert.equal(result.error, undefined);
    return { ...result, saved: result.stdout.trim() ? JSON.parse(result.stdout) : undefined };
  };
  const history = id => { const store = openRepositoryStore(common); try { return store.readHistory(id, { limit: 100 }); } finally { store.close(); } };
  const report = id => { const page = history(id), capture = page.captures.find(c => c.channel === 'report'); assert.ok(capture); return JSON.parse(capture.chunks.map(c => c.text).join('')); };
  const events = () => { const store = openRepositoryStore(common); try { return store.readEvents({ after: '0', limit: 200 }).events; } finally { store.close(); } };
  const interruptSource = async () => {
    writeFileSync(input, JSON.stringify({ mode: 'wait' }));
    const child = spawn(process.execPath, [host, JSON.stringify({ repository: repo.path, workflow: '.factory/workflows/source.ts', input, newWorktree: true, shutdownGraceMs: 100, scenario: { kind: 'result', payload: {} } })], { stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '', stderr = '';
    child.stdout.on('data', chunk => { stdout += chunk; });
    child.stderr.on('data', chunk => { stderr += chunk; });
    const deadline = Date.now() + 10000;
    let running;
    while (Date.now() < deadline) {
      const store = openRepositoryStore(common);
      try {
        const invocations = store.readInvocations({ limit: 100 }).invocations;
        running = invocations.find(item => item.stage === 'running' && store.readHistory(item.id).attempts.some(attempt => attempt.operationKey === 'wait'));
      } finally { store.close(); }
      if (running) break;
      await delay(20);
    }
    assert.ok(running, stderr);
    child.kill('SIGTERM');
    const code = await new Promise(resolve => child.once('close', resolve));
    assert.equal(code, 143, stdout + stderr);
    return JSON.parse(stdout.trim());
  };
  const seedHistory = async ({ state = 'complete', count = 1, text = 'seeded evidence', outcome = 'succeeded', finalize = true } = {}) => {
    const store = openRepositoryStore(common);
    try {
      const run = await store.createRun();
      const worktree = await store.registerWorktree({ path: repo.path, registration: 'fixture-source' });
      const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: { host: 'fixture', pid: process.pid, start: null } });
      for (let index = 0; index < count; index++) {
        const capture = await store.createCapture({ invocationId: invocation.id, channel: 'event' });
        await store.appendCapture({ id: capture.id, chunks: state === 'pruned' ? [] : [{ sequence: 1, text }], state });
      }
      if (finalize) await store.finalizeInvocation({ id: invocation.id, outcome, cleanup: 'complete', claimId: invocation.claim.id, token: invocation.claim.token });
      return invocation.id;
    } finally { store.close(); }
  };
  return { ...repo, common, invoke, history, report, events, interruptSource, seedHistory, launchLog };
}

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

test('extraction rejects diff paths that disagree with the single declared target', async () => {
  const repo = await fixture();
  try {
    const source = repo.invoke('source', { mode: 'command' }).saved;
    const attemptId = repo.history(source.invocationId).attempts.find(item => item.operationKey === 'observed').id;
    const target = { scope: 'repository', path: '.factory/prompts/check.md' };
    const base = { key: 'path-check', summary: 'Clarify the selected check.', target,
      supportingEvidence: [{ invocationId: source.invocationId, attemptId }], contraryEvidence: [], suggestedCases: ['Selected check'] };
    const cases = [
      '--- a/other.md\n+++ b/other.md\n@@ -1 +1 @@\n-old\n+new',
      '--- a/.factory/prompts/check.md\n+++ b/.factory/prompts/check.md\n@@ -1 +1 @@\n-old\n+new\n--- a/other.md\n+++ b/other.md\n@@ -1 +1 @@\n-old\n+new',
      '--- a/.factory/prompts/../agents.json\n+++ b/.factory/prompts/../agents.json\n@@ -1 +1 @@\n-old\n+new',
      'diff --git a/.factory/prompts/check.md b/.factory/prompts/check.md\nrename from other.md\nrename to .factory/prompts/check.md\n--- a/.factory/prompts/check.md\n+++ b/.factory/prompts/check.md\n@@ -1 +1 @@\n-old\n+new',
    ];
    for (const diff of cases) {
      const result = repo.invoke('learn', { version: 1, sources: [{ invocationId: source.invocationId }] },
        { kind: 'result', payload: { proposals: [{ ...base, diff }] } });
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.saved.diagnostic, /result invalid|unresolved invalid/i);
    }
  } finally { repo.dispose(); }
});

test('extraction accepts a new-file diff without applying it', async () => {
  const repo = await fixture();
  try {
    const source = repo.invoke('source', { mode: 'command' }).saved;
    const attemptId = repo.history(source.invocationId).attempts.find(item => item.operationKey === 'observed').id;
    const diff = 'diff --git a/.factory/prompts/new.md b/.factory/prompts/new.md\nnew file mode 100644\nindex 0000000..1234567\n--- /dev/null\n+++ b/.factory/prompts/new.md\n@@ -0,0 +1 @@\n+New prompt';
    const proposal = { key: 'new-prompt', summary: 'Add a prompt.', target: { scope: 'repository', path: '.factory/prompts/new.md' }, diff,
      supportingEvidence: [{ invocationId: source.invocationId, attemptId }], contraryEvidence: [], suggestedCases: ['New prompt check'] };
    const result = repo.invoke('learn', { version: 1, sources: [{ invocationId: source.invocationId }] },
      { kind: 'result', payload: { proposals: [proposal] } });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.deepEqual(repo.report(result.saved.invocationId).proposals, [proposal]);
    assert.equal(existsSync(join(result.saved.worktree, '.factory/prompts/new.md')), false);
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

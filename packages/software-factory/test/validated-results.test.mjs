import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { cpSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';

const owner = { host: 'fixture-host', pid: process.pid, start: 'fixture-start' };
const root = fileURLToPath(new URL('../', import.meta.url));

async function agentFixture() {
  const repo = createRepository();
  mkdirSync(join(repo.path, '.factory/workflows'), { recursive: true });
  writeFileSync(join(repo.path, '.factory/package.json'), '{"type":"module"}');
  writeFileSync(join(repo.path, '.factory/agents.json'), JSON.stringify({ defaults: {
    harness: 'fake', permissions: 'read-only', skillDelivery: 'instructions', prompt: 'fixture', skills: [],
  } }));
  writeFileSync(join(repo.path, '.factory/workflows/agent.ts'), `import type { WorkflowContext } from '@local/software-factory';
export async function run(context: WorkflowContext, input: Record<string, unknown>) {
  return context.agent('extract', { context: String(input.mode), output: { name: 'answer',
    validate: (value): value is { answer: string } => typeof value === 'object' && value !== null && 'answer' in value && value.answer === 'ok' } });
}`);
  writeFileSync(join(repo.path, '.factory/fake-result.mjs'), `const request = JSON.parse(process.argv[2]);
const mode = request.context;
if (mode === 'failure') process.exit(70);
const envelope = mode === 'needs_input' ? { kind: 'needs_input', question: 'Which?', context: 'Target required' }
  : { kind: 'result', payload: { answer: mode === 'invalid' ? 'bad' : 'ok', token: 'hidden-token', context: mode } };
if (mode === 'jsonl') process.stdout.write(JSON.stringify({ type: 'event', detail: 'provider framing' }) + '\\n');
process.stdout.write(JSON.stringify(envelope) + (mode === 'jsonl' ? '\\n' : ''));
if (mode === 'needs_input') process.exitCode = 2;
`);
  repo.git(['add', '.factory']);
  repo.git(['commit', '-m', 'Install fake result fixture', '--only', '.factory']);
  const common = join(repo.path, '.git');
  (await initializeRepositoryStore(common, { release: 'fixture' })).close();
  const toolchain = join(common, 'factory/toolchain');
  mkdirSync(toolchain);
  cpSync(join(root, 'node_modules'), join(toolchain, 'node_modules'), { recursive: true });
  writeFileSync(join(toolchain, 'manifest.json'), JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2', dependencies: { '@types/node': '24.19.2' } }));
  const input = join(common, 'input.json');
  const host = join(common, 'host.mjs');
  writeFileSync(host, `import { invoke } from ${JSON.stringify(new URL('../dist/lifecycle.js', import.meta.url).href)};
import { createFakeAdapter } from ${JSON.stringify(new URL('../dist/adapters/fake.js', import.meta.url).href)};
import { RepositoryStore } from ${JSON.stringify(new URL('../dist/store.js', import.meta.url).href)};
const options = JSON.parse(process.argv[2]);
if (options.failValidatedCapture) {
  const create = RepositoryStore.prototype.createCapture;
  RepositoryStore.prototype.createCapture = function(input) {
    if (input.channel === 'validated-result') throw new Error('injected validated capture failure');
    return create.call(this, input);
  };
}
if (options.failValidatedLink) {
  const settle = RepositoryStore.prototype.settleAttempt;
  RepositoryStore.prototype.settleAttempt = function(input) {
    if (input.validatedResultCaptureId) throw new Error('injected validated link failure');
    return settle.call(this, input);
  };
}
const adapter = createFakeAdapter({ executable: process.execPath, script: ${JSON.stringify(join(repo.path, '.factory/fake-result.mjs'))} });
adapter.decodeFinal = text => JSON.parse(text.trim().split('\\n').at(-1));
if (options.inflateNormalized) adapter.decodeFinal = () => ({ kind: 'result', payload: { answer: 'ok', filler: 'x'.repeat(1048576) } });
if (options.inflateFiltered) adapter.decodeFinal = () => ({ kind: 'result', payload: { answer: 'ok', filler: 'ABCD'.repeat(200000) } });
const result = await invoke({ ...options, adapters: { fake: adapter } });
console.log(JSON.stringify(result)); process.exit(result.exitCode);`);
  const invoke = (mode, extra = {}, environment = {}) => {
    writeFileSync(input, JSON.stringify({ mode }));
    const result = spawnSync(process.execPath, [host, JSON.stringify({ repository: repo.path,
      workflow: '.factory/workflows/agent.ts', input, newWorktree: true, shutdownGraceMs: 100, ...extra })],
    { encoding: 'utf8', timeout: 60000, env: { ...process.env, ...environment } });
    assert.equal(result.error, undefined);
    return { ...result, saved: JSON.parse(result.stdout.trim()) };
  };
  return { ...repo, common, invoke };
}

test('JSON and JSONL agents link a filtered normalized result before success while preserving raw output', async () => {
  const repo = await agentFixture();
  try {
    for (const mode of ['json', 'jsonl']) {
      const result = repo.invoke(mode);
      assert.equal(result.status, 0, result.stdout + result.stderr);
      const store = openRepositoryStore(repo.common);
      try {
        const history = store.readHistory(result.saved.invocationId, { limit: 100 });
        const attempt = history.attempts.find(item => item.kind === 'agent');
        assert.equal(attempt.outcome, 'succeeded');
        const report = history.captures.find(item => item.channel === 'report');
        assert.equal(JSON.parse(report.chunks.map(chunk => chunk.text).join('')).validatedResultCaptureId,
          attempt.agent.validatedResultCaptureId);
        assert.notEqual(attempt.agent.resultCaptureId, attempt.agent.validatedResultCaptureId);
        const raw = store.readCapture({ id: attempt.agent.resultCaptureId });
        const validated = store.readCapture({ id: attempt.agent.validatedResultCaptureId });
        assert.equal(raw.state, 'complete');
        assert.equal(validated.state, 'complete');
        assert.equal(validated.channel, 'validated-result');
        assert.deepEqual(JSON.parse(validated.chunks.map(chunk => chunk.text).join('')),
          { kind: 'result', payload: { answer: 'ok', token: '[REDACTED]', context: mode } });
        assert.equal(raw.chunks.map(chunk => chunk.text).join('').includes('provider framing'), mode === 'jsonl');
        const events = [];
        let cursor = '0';
        for (;;) {
          const page = store.readEvents({ after: cursor, limit: 200 });
          events.push(...page.events);
          if (page.events.length < 200) break;
          cursor = page.nextCursor;
        }
        const complete = events.find(event => event.kind === 'capture.appended' && event.data.captureId === attempt.agent.validatedResultCaptureId && event.data.state === 'complete');
        const settled = events.find(event => event.kind === 'attempt.settled' && event.data.attemptId === attempt.id);
        assert.ok(complete && settled && BigInt(complete.cursor) < BigInt(settled.cursor));
      } finally { store.close(); }
    }
  } finally { repo.dispose(); }
});

test('invalid payload, question, and process failure never link validated results', async () => {
  const repo = await agentFixture();
  try {
    for (const mode of ['invalid', 'needs_input', 'failure']) {
      const result = repo.invoke(mode);
      assert.equal(result.status, mode === 'needs_input' ? 2 : 1, result.stdout + result.stderr);
      const store = openRepositoryStore(repo.common);
      try {
        const history = store.readHistory(result.saved.invocationId, { limit: 100 });
        const attempt = history.attempts.find(item => item.kind === 'agent');
        assert.ok(attempt);
        assert.equal(attempt.agent.validatedResultCaptureId, undefined);
        assert.equal(history.captures.some(capture => capture.attemptId === attempt.id && capture.channel === 'validated-result'), false);
      } finally { store.close(); }
    }
  } finally { repo.dispose(); }
});

test('validated capture and link failures cannot produce a successful agent attempt', async () => {
  for (const injected of ['failValidatedCapture', 'failValidatedLink']) {
    const repo = await agentFixture();
    try {
      const result = repo.invoke('json', { [injected]: true });
      assert.equal(result.status, 1, result.stdout + result.stderr);
      const store = openRepositoryStore(repo.common);
      try {
        const history = store.readHistory(result.saved.invocationId, { limit: 100 });
        const attempt = history.attempts.find(item => item.kind === 'agent');
        assert.ok(attempt);
        assert.notEqual(attempt.outcome, 'succeeded');
        assert.equal(attempt.agent.validatedResultCaptureId, undefined);
        if (injected === 'failValidatedCapture') {
          assert.equal(history.accounting.occupiedAgents, 1);
          assert.equal(attempt.outcome, null);
        } else {
          assert.equal(attempt.outcome, 'failed');
        }
      } finally { store.close(); }
    } finally { repo.dispose(); }
  }
});

test('a decoded result beyond the normalized size bound fails before settlement', async () => {
  const repo = await agentFixture();
  try {
    const result = repo.invoke('json', { inflateNormalized: true });
    assert.equal(result.status, 1, result.stdout + result.stderr);
    const store = openRepositoryStore(repo.common);
    try {
      const history = store.readHistory(result.saved.invocationId, { limit: 100 });
      const attempt = history.attempts.find(item => item.kind === 'agent');
      assert.equal(attempt.outcome, 'failed');
      assert.equal(attempt.agent.validatedResultCaptureId, undefined);
      assert.equal(history.captures.some(capture => capture.channel === 'validated-result'), false);
    } finally { store.close(); }
  } finally { repo.dispose(); }
});

test('a filtered normalized result that expands beyond the read bound cannot settle successfully', async () => {
  const repo = await agentFixture();
  try {
    const result = repo.invoke('json', { inflateFiltered: true }, { TEST_SECRET: 'ABCD' });
    assert.equal(result.status, 1, result.stdout + result.stderr);
    const store = openRepositoryStore(repo.common);
    try {
      const history = store.readHistory(result.saved.invocationId, { limit: 100 });
      const attempt = history.attempts.find(item => item.kind === 'agent');
      assert.equal(attempt.outcome, 'failed');
      assert.equal(attempt.agent.validatedResultCaptureId, undefined);
    } finally { store.close(); }
  } finally { repo.dispose(); }
});

test('successful settlement links only its own complete validated result and preserves the link on retry', async () => {
  const repository = createRepository();
  const store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
  try {
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    const attempt = await store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'extract', kind: 'agent', intent: 'initial' });
    const second = await store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'other', kind: 'agent', intent: 'initial' });
    const capture = async (attemptId, channel = 'validated-result', state = 'complete') => {
      const saved = await store.createCapture({ invocationId: invocation.id, attemptId, channel });
      await store.appendCapture({ id: saved.id, chunks: [{ sequence: 1, text: '{"kind":"result","payload":{"ok":true}}' }], state });
      return saved.id;
    };
    const foreign = await capture(second.id);
    const wrongChannel = await capture(attempt.id, 'result');
    const partial = await capture(attempt.id, 'validated-result', 'partial');
    const open = await store.createCapture({ invocationId: invocation.id, attemptId: attempt.id, channel: 'validated-result' });
    const valid = await capture(attempt.id);
    const alternate = await capture(attempt.id);
    const raw = await store.createCapture({ invocationId: invocation.id, attemptId: attempt.id, channel: 'result' });
    await store.saveAgentMetadata(attempt.id, { inputsCaptureId: raw.id, resultCaptureId: raw.id, outputCaptureId: raw.id,
      adapter: 'fake', sessionMode: 'fresh', context: 'fixture', validator: null });
    await store.markStarted({ id: attempt.id, owner });
    const settlement = { id: attempt.id, launch: 'started', outcome: 'succeeded', quiescent: true, evidence: 'validated authoritative result' };
    await assert.rejects(store.settleAttempt(settlement), /validated result capture/);
    for (const id of [foreign, wrongChannel, partial, open.id]) {
      await assert.rejects(store.settleAttempt({ ...settlement, validatedResultCaptureId: id }), /validated result capture/);
      assert.equal(store.readAttempt(attempt.id).outcome, null);
    }
    await store.settleAttempt({ ...settlement, validatedResultCaptureId: valid });
    assert.equal(store.readAttempt(attempt.id).agent.validatedResultCaptureId, valid);
    await store.settleAttempt({ ...settlement, validatedResultCaptureId: valid });
    await assert.rejects(store.settleAttempt({ ...settlement, validatedResultCaptureId: alternate }), /settled/);
    await store.settleAttempt(settlement);
    assert.equal(store.readAttempt(attempt.id).agent.validatedResultCaptureId, valid);
    await assert.rejects(store.settleAttempt({ id: second.id, launch: 'not_started', outcome: 'failed', quiescent: true,
      evidence: 'never launched', validatedResultCaptureId: foreign }), /validated result capture/);
    await store.markStarted({ id: second.id, owner });
    await assert.rejects(store.settleAttempt({ id: second.id, launch: 'started', outcome: 'failed', quiescent: true,
      evidence: 'failed', validatedResultCaptureId: foreign }), /validated result capture/);
    assert.equal(store.readAttempt(second.id).outcome, null);
  } finally { store.close(); repository.dispose(); }
});

test('prelaunch agent metadata cannot forge a validated result link', async () => {
  const repository = createRepository();
  const store = await initializeRepositoryStore(join(repository.path, '.git'), { release: 'fixture' });
  try {
    const run = await store.createRun();
    const worktree = await store.registerWorktree({ path: repository.path, registration: 'fixture' });
    const invocation = await store.startInvocation({ runId: run.id, worktreeId: worktree.id, owner });
    await store.activateInvocation(invocation.id);
    const attempt = await store.admitAttempt({ id: randomUUID(), invocationId: invocation.id, operationKey: 'extract', kind: 'agent', intent: 'initial' });
    const capture = await store.createCapture({ invocationId: invocation.id, attemptId: attempt.id, channel: 'result' });
    const metadata = { inputsCaptureId: capture.id, resultCaptureId: capture.id, outputCaptureId: capture.id,
      adapter: 'fake', sessionMode: 'fresh', context: 'fixture', validator: null, validatedResultCaptureId: capture.id };
    await assert.rejects(store.saveAgentMetadata(attempt.id, metadata), /validated result|metadata/);
    assert.equal(store.readAttempt(attempt.id).agent, undefined);
  } finally { store.close(); repository.dispose(); }
});

import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { fileURLToPath } from 'node:url';
import { initializeRepositoryStore, openRepositoryStore } from '../../dist/store.js';
import { copyLearningToolchain } from './learning-toolchain-copy.mjs';
import { createRepository } from './repository.mjs';
import { telemetry, timingSync } from '../../qualification/selector-timing.mjs';
import { fixtureHostTiming } from '../../qualification/selector-timing-host.mjs';
import { fixtureAttemptTiming } from '../../qualification/selector-timing-attempts.mjs';

const root = fileURLToPath(new URL('../../', import.meta.url));
const diagnostic = stage => {
  if (process.env.GITHUB_ACTIONS === 'true') process.stderr.write(`[learning-fixture] ${stage}\n`);
};

export async function fixture() {
  const setupEnd = telemetry()?.begin('setup');
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
  timingSync('commit', () => {
    repo.git(['add', '.factory']);
    repo.git(['commit', '-m', 'Install disposable extraction fixtures', '--only', '.factory']);
  });
  const common = join(repo.path, '.git');
  (await initializeRepositoryStore(common, { release: 'fixture' })).close();
  const toolchain = join(common, 'factory/toolchain');
  mkdirSync(toolchain);
  timingSync('copy', () => copyLearningToolchain(join(root, 'node_modules'), join(toolchain, 'node_modules')));
  writeFileSync(join(toolchain, 'manifest.json'), JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2', dependencies: { '@types/node': '24.19.2' } }));
  const host = join(common, 'host.mjs'), input = join(common, 'input.json'), launchLog = join(common, 'learn-launches.jsonl');
  writeFileSync(host, `import { invoke } from ${JSON.stringify(new URL('../../dist/lifecycle.js', import.meta.url).href)};
import { createFakeAdapter } from ${JSON.stringify(new URL('../../dist/adapters/fake.js', import.meta.url).href)};
const { scenario, qualificationTiming, ...options } = JSON.parse(process.argv[2]);
const adapter = createFakeAdapter({ executable: process.execPath, script: ${JSON.stringify(join(root, 'test/fixtures/learning-harness.mjs'))} });
const start = adapter.start;
adapter.start = request => start({ ...request, context: JSON.stringify({ context: request.context, scenario, launchLog: ${JSON.stringify(launchLog)} }) });
const result = await invoke({ ...options, adapters: { fake: adapter } });
console.log(JSON.stringify(result)); process.exit(result.exitCode);`);
  const exportAttempts = fixtureAttemptTiming(repo.path);
  const invoke = (workflow, payload, scenario = { kind: 'result', payload: { proposals: [], noProposalReason: 'No justified change.' } }, extra = {}) => {
    writeFileSync(input, JSON.stringify(payload));
    const started = performance.now();
    diagnostic(`invoke ${workflow} begin`);
    const end = telemetry()?.begin(workflow === 'learn' ? 'learn' : 'source');
    const hostTiming = fixtureHostTiming(repo.path, 'sync');
    const result = spawnSync(process.execPath, [...(hostTiming?.nodeArgs ?? []), host, JSON.stringify({ repository: repo.path, workflow: `.factory/workflows/${workflow}.ts`, input, newWorktree: true, shutdownGraceMs: 100, scenario, ...extra, ...(hostTiming ? { qualificationTiming: hostTiming.context } : {}) })], { encoding: 'utf8', timeout: 60000 });
    hostTiming?.returned({ pid: result.pid, status: result.status, signal: result.signal, apiError: result.error !== undefined });
    diagnostic(`invoke ${workflow} end status=${result.status ?? 'none'} signal=${result.signal ?? 'none'} elapsedMs=${Math.round(performance.now() - started)}`);
    assert.equal(result.error, undefined);
    const parsed = timingSync('result', () => ({ ...result, saved: result.stdout.trim() ? JSON.parse(result.stdout) : undefined }));
    end?.(result.status === 0 ? 'ok' : 'failed', { exitCode: result.status, invocationId: exportAttempts.invocationId(parsed.saved?.invocationId), disposition: result.signal === 'SIGTERM' || result.signal === 'SIGINT' ? result.signal : result.signal ? 'other-signal' : result.status === 0 ? 'ok' : 'failed' });
    exportAttempts();
    return parsed;
  };
  const history = id => { const store = openRepositoryStore(common); try { return store.readHistory(id, { limit: 100 }); } finally { store.close(); } };
  const report = id => { const page = history(id), capture = page.captures.find(c => c.channel === 'report'); assert.ok(capture); return JSON.parse(capture.chunks.map(c => c.text).join('')); };
  const events = () => { const store = openRepositoryStore(common); try { return store.readEvents({ after: '0', limit: 200 }).events; } finally { store.close(); } };
  const interruptSource = async () => {
    const end = telemetry()?.begin('interrupt');
    diagnostic('interrupt source begin');
    writeFileSync(input, JSON.stringify({ mode: 'wait' }));
    const hostTiming = fixtureHostTiming(repo.path, 'async');
    const child = spawn(process.execPath, [...(hostTiming?.nodeArgs ?? []), host, JSON.stringify({ repository: repo.path, workflow: '.factory/workflows/source.ts', input, newWorktree: true, shutdownGraceMs: 100, scenario: { kind: 'result', payload: {} }, ...(hostTiming ? { qualificationTiming: hostTiming.context } : {}) })], { stdio: ['ignore', 'pipe', 'pipe'] });
    hostTiming?.observe(child);
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
    diagnostic('interrupt source ready');
    child.kill('SIGTERM');
    telemetry()?.mark('interrupt', { disposition: 'SIGTERM' });
    diagnostic('interrupt source signal sent');
    const code = await new Promise(resolve => child.once('close', resolve));
    diagnostic(`interrupt source closed status=${code ?? 'none'}`);
    assert.equal(code, 143, stdout + stderr);
    const saved = timingSync('result', () => JSON.parse(stdout.trim()));
    end?.(code === 143 ? 'ok' : 'failed', { exitCode: code, invocationId: exportAttempts.invocationId(saved.invocationId) });
    exportAttempts();
    return saved;
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
  const dispose = () => { exportAttempts(); return repo.dispose(); };
  setupEnd?.();
  return { ...repo, dispose, common, invoke, history, report, events, interruptSource, seedHistory, launchLog };
}

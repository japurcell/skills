import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';
const cli = fileURLToPath(new URL('../dist/cli.js', import.meta.url));
const packageRoot = fileURLToPath(new URL('../', import.meta.url));
async function fixture(source = `import { message } from './helper.js';
export async function run(context, inputs) {
  await context.scope('check', async scope => {
    await scope.command('print', { argv: [process.execPath, '-e', 'console.log(process.cwd(), process.argv[1])', message + inputs.request], env: {} });
  });
}`) {
  const repo = createRepository();
  mkdirSync(join(repo.path, '.factory/workflows'), { recursive: true });
  writeFileSync(join(repo.path, '.factory/package.json'), '{"type":"module"}');
  writeFileSync(join(repo.path, '.factory/workflows/audit.ts'), source);
  writeFileSync(join(repo.path, '.factory/workflows/helper.ts'), `export const message = 'selected:';`);
  repo.git(['add', '.factory']); repo.git(['commit', '-m', 'Commit workflow', '--only', '.factory']);
  writeFileSync(join(repo.path, '.factory/workflows/helper.ts'), `export const message = 'dirty:';`);
  const common = join(repo.path, '.git');
  const store = await initializeRepositoryStore(common, { release: 'fixture' }); store.close();
  const toolchain = join(common, 'factory/toolchain'); mkdirSync(toolchain);
  cpSync(join(packageRoot, 'node_modules'), join(toolchain, 'node_modules'), { recursive: true });
  writeFileSync(join(toolchain, 'manifest.json'), JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2', dependencies: { '@types/node': '24.19.2' } }));
  const input = join(repo.path, '.git/input.json'); writeFileSync(input, '{"request":"hello"}');
  const call = args => spawnSync(process.execPath, [cli, ...args, '--repository', repo.path, '--json'], { encoding: 'utf8', timeout: 30000 });
  const invoke = extra => call(['invoke', '--workflow', '.factory/workflows/audit.ts', '--input', input, ...extra]);
  return { ...repo, common, input, call, invoke };
}
test('public invoke builds once and runs committed workflow helpers without touching source or index', async () => {
  const repo = await fixture();
  try {
    const status = repo.git(['status', '--porcelain=v1']);
    const index = repo.git(['diff', '--cached']);
    const result = repo.invoke(['--new-worktree', '--ref', 'HEAD']);
    assert.equal(result.status, 0, result.stderr + result.stdout);
    const saved = JSON.parse(result.stdout);
    assert.equal(saved.outcome, 'succeeded'); assert.equal(saved.cleanup, 'complete');
    const history = repo.call(['history', '--invocation', saved.invocationId]);
    assert.equal(history.status, 0, history.stderr);
    const record = JSON.parse(history.stdout);
    assert.equal(record.attempts.filter(a => a.operationKey.includes('startup/build')).length, 1);
    assert.equal(record.attempts.filter(a => a.kind === 'agent').length, 0);
    assert.match(JSON.stringify(record.captures), /selected:hello/);
    assert.doesNotMatch(JSON.stringify(record.captures), /dirty:hello/);
    assert.equal(repo.git(['status', '--porcelain=v1']), status);
    assert.equal(repo.git(['diff', '--cached']), index);
    assert.equal(readFileSync(join(saved.worktree, 'tracked.txt'), 'utf8'), 'committed\n');
  } finally { repo.dispose(); }
});

test('build failure launches no workflow command or agent and retains compiler diagnostics', async () => {
  const repo = await fixture(`export async function run(context) { const invalid: number = 'wrong'; await context.command('should-not-launch', { argv: [process.execPath, '-e', 'process.exit(0)'] }); }`);
  try {
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 3, result.stderr);
    const saved = JSON.parse(result.stdout); assert.equal(saved.outcome, 'failed');
    const record = JSON.parse(repo.call(['history', '--invocation', saved.invocationId]).stdout);
    assert.equal(record.attempts.length, 1); assert.equal(record.attempts[0].kind, 'command');
    assert.match(JSON.stringify(record.captures), /not assignable/);
    assert.equal(record.invocation.cleanup, 'complete');
  } finally { repo.dispose(); }
});
test('missing shared dependencies refuse without installation or source changes', async () => {
  const repo = await fixture();
  try {
    rmSync(join(repo.common, 'factory/toolchain/node_modules/typescript'), { recursive: true });
    const before = repo.git(['status', '--porcelain=v1']);
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 3);
    const saved = JSON.parse(result.stdout); assert.match(saved.diagnostic, /explicitly install/);
    const record = JSON.parse(repo.call(['history', '--invocation', saved.invocationId]).stdout);
    assert.equal(record.attempts.length, 0); assert.equal(repo.git(['status', '--porcelain=v1']), before);
  } finally { repo.dispose(); }
});
test('invalid refs, malformed input and missing same-run context refuse before workflow work', async () => {
  const repo = await fixture();
  try {
    for (const extra of [['--new-worktree', '--ref', 'does-not-exist'], ['--new-worktree', '--context', 'missing'], ['--new-worktree', '--question', 'missing']]) {
      const result = repo.invoke(extra); assert.equal(result.status, 3); assert.equal(result.stdout, '');
    }
    writeFileSync(repo.input, '[]'); const malformed = repo.invoke(['--new-worktree']);
    assert.equal(malformed.status, 3); assert.match(malformed.stderr, /JSON object/);
  } finally { repo.dispose(); }
});
test('explicit worktree reuse starts current entry and preserves unfinished edits and run accounting', async () => {
  const repo = await fixture(`export async function run(context, inputs) { await context.progress('entry:' + inputs.request); }`);
  try {
    const initial = repo.invoke(['--new-worktree']); assert.equal(initial.status, 0, initial.stdout + initial.stderr);
    const first = JSON.parse(initial.stdout);
    writeFileSync(join(first.worktree, 'unfinished.txt'), 'keep me');
    writeFileSync(join(first.worktree, '.factory/workflows/audit.ts'), `export async function run(context, inputs) { await context.progress('current-entry:' + inputs.request); }`);
    writeFileSync(repo.input, '{"request":"second"}');
    const repeated = repo.invoke(['--worktree', first.worktreeId, '--run', first.runId]);
    assert.equal(repeated.status, 0, repeated.stdout + repeated.stderr);
    const second = JSON.parse(repeated.stdout); assert.notEqual(second.invocationId, first.invocationId); assert.equal(second.runId, first.runId);
    assert.equal(readFileSync(join(first.worktree, 'unfinished.txt'), 'utf8'), 'keep me');
    const history = JSON.parse(repo.call(['history', '--invocation', second.invocationId]).stdout);
    assert.match(JSON.stringify(history.captures), /current-entry:second/); assert.equal(history.accounting.additionalUsed, 0);
  } finally { repo.dispose(); }
});
test('conflicting resolution scaffold refuses replacement', async () => {
  const repo = await fixture(`export async function run(context) { await context.progress('initial'); }`);
  try {
    const first = JSON.parse(repo.invoke(['--new-worktree']).stdout);
    rmSync(join(first.worktree, '.factory/node_modules')); mkdirSync(join(first.worktree, '.factory/node_modules'));
    writeFileSync(join(first.worktree, '.factory/node_modules/owned.txt'), 'preserve');
    const result = repo.invoke(['--worktree', first.worktreeId]); assert.equal(result.status, 3);
    assert.match(JSON.parse(result.stdout).diagnostic, /conflicting user-owned/);
    assert.equal(readFileSync(join(first.worktree, '.factory/node_modules/owned.txt'), 'utf8'), 'preserve');
  } finally { repo.dispose(); }
});

test('compiled workflow resolves declared dependencies from the one shared environment', async () => {
  const repo = await fixture(`import { value } from 'factory-fixture-dependency'; export async function run(context) { await context.progress(value); }`);
  try {
    const modules = join(repo.common, 'factory/toolchain/node_modules/factory-fixture-dependency'); mkdirSync(modules);
    writeFileSync(join(modules, 'package.json'), '{"type":"module","version":"1.0.0","exports":"./index.js","types":"./index.d.ts"}');
    writeFileSync(join(modules, 'index.js'), 'export const value = "shared-dependency";');
    writeFileSync(join(modules, 'index.d.ts'), 'export declare const value: string;');
    const manifest = join(repo.common, 'factory/toolchain/manifest.json');
    const installation = JSON.parse(readFileSync(manifest, 'utf8')); installation.dependencies['factory-fixture-dependency'] = '1.0.0'; writeFileSync(manifest, JSON.stringify(installation));
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 0, result.stdout + result.stderr);
    const record = JSON.parse(repo.call(['history', '--invocation', JSON.parse(result.stdout).invocationId]).stdout);
    assert.match(JSON.stringify(record.captures), /shared-dependency/);
  } finally { repo.dispose(); }
});
test('workflow completion drains commands already requested by current entry', async () => {
  const repo = await fixture(`export async function run(context) { void context.command('pending', { argv: [process.execPath, '-e', 'setTimeout(() => console.log("drained"), 100)'], env: {} }); }`);
  try {
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 0, result.stdout + result.stderr);
    const record = JSON.parse(repo.call(['history', '--invocation', JSON.parse(result.stdout).invocationId]).stdout);
    assert.equal(record.attempts.length, 2); assert.match(JSON.stringify(record.captures), /drained/);
    assert.equal(record.accounting.occupiedCommands, 0);
  } finally { repo.dispose(); }
});
test('parent exit with a live descendant keeps ownership and cleanup unknown', async () => {
  const repo = await fixture(`export async function run(context) { await context.command('descendant', { argv: [process.execPath, '-e', 'const {spawn}=require("node:child_process");spawn(process.execPath,["-e","setInterval(()=>{},1000)"],{stdio:"ignore"});process.exit(0)'], env: {} }); }`);
  let group;
  try {
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 1, result.stdout + result.stderr);
    const saved = JSON.parse(result.stdout); assert.equal(saved.cleanup, 'unknown');
    const store = openRepositoryStore(repo.common);
    try { const history = store.readHistory(saved.invocationId); group = history.attempts.at(-1).owner.pid; assert.equal(store.inspectOwners().length, 1); assert.equal(history.accounting.occupiedCommands, 1); } finally { store.close(); }
  } finally { if (group) { try { process.kill(-group, 'SIGKILL'); } catch {} } repo.dispose(); }
});

test('ordinary typed workflows import the published context contract', async () => {
  const repo = await fixture(`import type { WorkflowContext } from '@local/software-factory'; export async function run(context: WorkflowContext, inputs: Record<string, unknown>) { await context.progress(String(inputs.request)); }`);
  try { const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 0, result.stdout + result.stderr); }
  finally { repo.dispose(); }
});
test('existing Git worktree path is validated and unfinished edits are preserved on first use', async () => {
  const repo = await fixture(`export async function run(context) { await context.progress('existing'); }`);
  try {
    const before = repo.git(['status', '--porcelain=v1']);
    const index = repo.git(['diff', '--cached', '--', 'tracked.txt']);
    const result = repo.invoke(['--worktree', repo.path]); assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.equal(readFileSync(join(repo.path, 'tracked.txt'), 'utf8'), 'unstaged\n');
    assert.equal(repo.git(['diff', '--cached', '--', 'tracked.txt']), index);
    assert.equal(repo.git(['status', '--porcelain=v1']).split('\n').filter(line => line !== '?? .factory/node_modules').join('\n'), before);
  } finally { repo.dispose(); }
});
test('same-run explicit followup uses retained operation lineage and current inputs', async () => {
  const repo = await fixture(`export async function run(context) { await context.command('check', { argv: [process.execPath, '-e', 'console.log("first")'], env: {} }); }`);
  try {
    const first = JSON.parse(repo.invoke(['--new-worktree']).stdout);
    const history = JSON.parse(repo.call(['history', '--invocation', first.invocationId]).stdout);
    const prior = history.attempts.at(-1).id;
    writeFileSync(join(first.worktree, '.factory/workflows/audit.ts'), `export async function run(context, inputs) { await context.command('check', { argv: [process.execPath, '-e', 'console.log("followup")'], env: {}, intent: 'followup', priorAttemptId: inputs.prior }); }`);
    writeFileSync(repo.input, JSON.stringify({ prior }));
    const result = repo.invoke(['--worktree', first.worktreeId, '--run', first.runId]);
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const next = JSON.parse(repo.call(['history', '--invocation', JSON.parse(result.stdout).invocationId]).stdout);
    assert.equal(next.attempts.at(-1).operationId, history.attempts.at(-1).operationId); assert.equal(next.accounting.additionalUsed, 0);
    const foreign = repo.invoke(['--worktree', first.worktreeId]); assert.equal(foreign.status, 1);
    assert.match(JSON.parse(foreign.stdout).diagnostic, /another run/);
  } finally { repo.dispose(); }
});
test('saved questions and context references are explicit, complete and restricted to the joined run', async () => {
  const repo = await fixture(`export async function run(context) { await context.needsInput('Choose a target', 'No target supplied'); }`);
  try {
    const asking = repo.invoke(['--new-worktree']); assert.equal(asking.status, 2, asking.stdout + asking.stderr);
    const first = JSON.parse(asking.stdout);
    const history = JSON.parse(repo.call(['history', '--invocation', first.invocationId]).stdout);
    const question = history.captures.find(c => c.channel === 'request').id;
    const context = history.captures.find(c => c.channel === 'context').id;
    writeFileSync(join(first.worktree, '.factory/workflows/audit.ts'), `export async function run(context, inputs) { await context.progress('answer:' + inputs.answer); }`);
    writeFileSync(repo.input, '{"answer":"current"}');
    const answer = repo.invoke(['--worktree', first.worktreeId, '--run', first.runId, '--question', question, '--context', context]);
    assert.equal(answer.status, 0, answer.stdout + answer.stderr);
    const foreign = repo.invoke(['--worktree', first.worktreeId, '--question', question]);
    assert.equal(foreign.status, 3); assert.match(foreign.stderr, /foreign-run/);
  } finally { repo.dispose(); }
});

test('mismatched declared shared dependency versions refuse before compiler execution', async () => {
  const repo = await fixture(`export async function run(context) { await context.progress('not entered'); }`);
  try {
    writeFileSync(join(repo.path, '.factory/package.json'), '{"type":"module","dependencies":{"fixture-package":"2.0.0"}}');
    const result = repo.invoke(['--worktree', repo.path]); assert.equal(result.status, 3, result.stdout + result.stderr);
    const saved = JSON.parse(result.stdout); assert.match(saved.diagnostic, /explicitly install declared dependencies/);
    const history = JSON.parse(repo.call(['history', '--invocation', saved.invocationId]).stdout); assert.equal(history.attempts.length, 0);
    assert.equal(readFileSync(join(repo.path, '.factory/package.json'), 'utf8'), '{"type":"module","dependencies":{"fixture-package":"2.0.0"}}');
  } finally { repo.dispose(); }
});

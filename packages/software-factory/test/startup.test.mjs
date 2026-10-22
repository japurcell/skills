import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { setTimeout as delay } from 'node:timers/promises';
import { spawn, spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, readFileSync, writeFileSync, rmSync, renameSync, realpathSync, existsSync, symlinkSync, chmodSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { DatabaseSync } from 'node:sqlite';
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
    assert.equal(record.attempts.filter(attempt=>attempt.operationKey.startsWith('startup/build/')).length,1); assert.ok(record.attempts.every(attempt=>attempt.kind==='command'&&attempt.operationKey.startsWith('startup/')));
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
    assert.ok(record.attempts.every(attempt=>attempt.kind==='command'&&attempt.operationKey.startsWith('startup/git/'))); assert.equal(repo.git(['status', '--porcelain=v1']), before);
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
    assert.equal(record.attempts.filter(attempt=>!attempt.operationKey.startsWith('startup/')).length,1); assert.equal(record.attempts.at(-1).operationKey,'pending'); assert.match(JSON.stringify(record.captures), /drained/);
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

test('unawaited needsInput saves a complete question before needs-input finalization', async () => {
  const repo = await fixture(`export async function run(context) { void context.needsInput('Choose', 'Need a choice'); }`);
  try {
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 2, result.stdout + result.stderr);
    const saved = JSON.parse(result.stdout); assert.equal(saved.outcome, 'needs_input'); assert.equal(saved.cleanup, 'complete');
    assert.doesNotMatch(result.stderr, /recording failed|unhandled/i);
    const history = JSON.parse(repo.call(['history', '--invocation', saved.invocationId]).stdout);
    const question = history.captures.find(capture => capture.channel === 'request');
    assert.equal(question.state, 'complete'); assert.match(JSON.stringify(question.chunks), /Need a choice/);
    assert.ok(history.captures.every(capture => capture.state === 'complete'));
  } finally { repo.dispose(); }
});

test('unawaited progress completes its capture before successful finalization', async () => {
  const repo = await fixture(`export async function run(context) { void context.progress('complete progress'); }`);
  try {
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.equal(result.stderr, '');
    const saved = JSON.parse(result.stdout);
    const history = JSON.parse(repo.call(['history', '--invocation', saved.invocationId]).stdout);
    assert.match(JSON.stringify(history.captures), /complete progress/);
    assert.ok(history.captures.every(capture => capture.state === 'complete'));
  } finally { repo.dispose(); }
});
test('unawaited unavailable agent fails the invocation without an agent attempt', async () => {
  const repo = await fixture(`export async function run(context) { void context.agent('implement', {}); }`);
  try {
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.equal(result.stderr, '');
    const saved = JSON.parse(result.stdout); assert.equal(saved.outcome, 'failed'); assert.match(saved.diagnostic, /agent adapters unavailable/);
    const history = JSON.parse(repo.call(['history', '--invocation', saved.invocationId]).stdout);
    assert.equal(history.attempts.filter(attempt => attempt.kind === 'agent').length, 0);
    assert.ok(history.captures.every(capture => capture.state === 'complete'));
  } finally { repo.dispose(); }
});
test('unawaited scope owns its delayed callback and commands until they finish', async () => {
  const repo = await fixture(`export async function run(context) { void context.scope('delayed', async scope => { await new Promise(resolve => setTimeout(resolve, 100)); await scope.progress('scope entered'); await scope.command('late', {argv: [process.execPath, '-e', 'console.log("late complete")'], env: {}}); }); }`);
  try {
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.equal(result.stderr, '');
    const history = JSON.parse(repo.call(['history', '--invocation', JSON.parse(result.stdout).invocationId]).stdout);
    assert.equal(history.attempts.at(-1).operationKey, 'delayed/late');
    assert.equal(history.attempts.at(-1).outcome, 'succeeded'); assert.equal(history.accounting.occupiedCommands, 0);
    assert.match(JSON.stringify(history.captures), /late complete/);
    assert.ok(history.captures.every(capture => capture.state === 'complete'));
  } finally { repo.dispose(); }
});
for (const mode of ['awaited question', 'unawaited question']) {
  test(`independent delayed scope failure outranks ${mode} while retaining its complete saved request`, async () => {
    const question = mode === 'awaited question' ? 'await' : 'void';
    const repo = await fixture(`export async function run(context) { void context.scope('failure', async () => { await new Promise(resolve => setTimeout(resolve, 100)); throw new Error('independent scope failure'); }); ${question} context.needsInput('Choose', 'Question must survive'); }`);
    try {
      const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.equal(result.stderr, '');
      const saved = JSON.parse(result.stdout); assert.equal(saved.outcome, 'failed'); assert.equal(saved.cleanup, 'complete'); assert.match(saved.diagnostic, /independent scope failure/);
      const history = JSON.parse(repo.call(['history', '--invocation', saved.invocationId]).stdout);
      const request = history.captures.find(capture => capture.channel === 'request');
      assert.equal(request.state, 'complete'); assert.match(JSON.stringify(request.chunks), /Question must survive/);
      assert.ok(history.captures.every(capture => capture.state === 'complete'));
    } finally { repo.dispose(); }
  });
}

test('trailing-space repository paths keep their distinct Git identity', async () => {
  const selected = await fixture(`export async function run(context) { await context.progress('selected trailing-space repository'); }`);
  const sibling = await fixture(`export async function run(context) { await context.progress('wrong sibling repository'); }`);
  const spaced = selected.path + ' ';
  try {
    renameSync(selected.path, spaced); renameSync(sibling.path, selected.path);
    const result = spawnSync(process.execPath, [cli, 'invoke', '--repository', spaced, '--workflow', '.factory/workflows/audit.ts', '--input', join(spaced, '.git/input.json'), '--new-worktree', '--json'], {encoding: 'utf8', timeout: 30000});
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const saved = JSON.parse(result.stdout); assert.ok(saved.worktree.startsWith(realpathSync(spaced) + '/.git/factory/worktrees/'));
    const history = spawnSync(process.execPath, [cli, 'history', '--repository', spaced, '--invocation', saved.invocationId, '--json'], {encoding: 'utf8'});
    assert.equal(history.status, 0, history.stderr); assert.match(history.stdout, /selected trailing-space repository/); assert.doesNotMatch(history.stdout, /wrong sibling repository/);
  } finally { rmSync(spaced, {recursive: true, force: true}); selected.dispose(); sibling.dispose(); }
});

test('large saved output remains paged in history under a bounded CLI heap', async () => {
  const repo = await fixture(`export async function run(context) { await context.command('large', {argv: [process.execPath, '-e', 'process.stdout.write("x".repeat(40 * 1024 * 1024))'], env: {}}); }`);
  try {
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 0, result.stdout + result.stderr);
    const invocation = JSON.parse(result.stdout).invocationId;
    const call = extra => spawnSync(process.execPath, ['--max-old-space-size=32', cli, 'history', '--repository', repo.path, '--invocation', invocation, '--json', ...extra], {encoding: 'utf8', timeout: 30000, maxBuffer: 2 * 1024 * 1024});
    const detail = call([]); assert.equal(detail.status, 0, detail.stderr); assert.ok(Buffer.byteLength(detail.stdout) < 1024 * 1024);
    const history = JSON.parse(detail.stdout); const output = history.captures.find(capture => capture.channel === 'stdout' && capture.hasMore);
    assert.ok(output); assert.ok(output.nextSequence > 0); assert.equal(output.state, 'complete');
    const next = call(['--capture', output.id, '--after-sequence', String(output.nextSequence), '--limit', '1']);
    assert.equal(next.status, 0, next.stderr); const page = JSON.parse(next.stdout);
    assert.equal(page.chunks[0].sequence, output.nextSequence + 1); assert.equal(page.hasMore, true); assert.equal(page.state, 'complete');
  } finally { repo.dispose(); }
});

test('failed command peer outranks an awaited question and retains both saved facts', async () => {
  const repo = await fixture(`export async function run(context) { try { await context.command('failed-peer', {argv: [process.execPath, '-e', 'process.exit(1)'], env: {}}); } catch {} await context.needsInput('Choose target', 'Need a choice'); }`);
  try {
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 1, result.stdout + result.stderr);
    const saved = JSON.parse(result.stdout); assert.equal(saved.outcome, 'failed'); assert.equal(saved.cleanup, 'complete');
    const history = JSON.parse(repo.call(['history', '--invocation', saved.invocationId]).stdout);
    assert.equal(history.attempts.at(-1).outcome, 'failed'); assert.equal(history.attempts.at(-1).quiescent, true);
    const question = history.captures.find(capture => capture.channel === 'request'); assert.equal(question.state, 'complete'); assert.match(JSON.stringify(question.chunks), /Need a choice/);
  } finally { repo.dispose(); }
});
test('large failed command finalizes through narrow cleanup checks under a bounded CLI heap', async () => {
  const repo = await fixture(`export async function run(context) { await context.command('large-failure', {argv: [process.execPath, '-e', 'process.stdout.write("x".repeat(40 * 1024 * 1024), () => process.exit(1))'], env: {}}); }`);
  try {
    const result = spawnSync(process.execPath, ['--max-old-space-size=32', cli, 'invoke', '--repository', repo.path, '--workflow', '.factory/workflows/audit.ts', '--input', repo.input, '--new-worktree', '--json'], {encoding: 'utf8', timeout: 30000});
    assert.equal(result.status, 1, result.stdout + result.stderr); assert.equal(result.stderr, '');
    const saved = JSON.parse(result.stdout); assert.equal(saved.outcome, 'failed'); assert.equal(saved.cleanup, 'complete');
  } finally { repo.dispose(); }
});

test('explicit advisory check can fail before correction and a required fresh check succeeds', async () => {
  const repo = await fixture(`export async function run(context) {
    const check = await context.command('expected-check', {argv: [process.execPath, '-e', 'process.exit(7)'], env: {}, required: false});
    if (check.exitCode !== 7) throw new Error('expected check result missing');
    await context.command('correction', {argv: [process.execPath, '-e', 'require("node:fs").writeFileSync("candidate.txt", "corrected")'], env: {}});
    await context.command('fresh-check', {argv: [process.execPath, '-e', 'if(require("node:fs").readFileSync("candidate.txt", "utf8") !== "corrected") process.exit(1)'], env: {}});
    return {initialCheck: check};
  }`);
  try {
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 0, result.stdout + result.stderr);
    const saved = JSON.parse(result.stdout); assert.equal(saved.outcome, 'succeeded'); assert.equal(saved.cleanup, 'complete');
    const history = JSON.parse(repo.call(['history', '--invocation', saved.invocationId]).stdout);
    const commands = history.attempts.filter(attempt => !attempt.operationKey.startsWith('startup/'));
    assert.deepEqual(commands.map(attempt => [attempt.operationKey, attempt.outcome]), [['expected-check', 'failed'], ['correction', 'succeeded'], ['fresh-check', 'succeeded']]);
    assert.ok(commands.every(attempt => attempt.quiescent));
    assert.match(JSON.stringify(history.captures), /required.*false/);
    const report = history.captures.find(capture => capture.channel === 'report');
    const final = JSON.parse(report.chunks.map(chunk => chunk.text).join(''));
    assert.equal(final.initialCheck.exitCode, 7); assert.equal(final.initialCheck.attemptId, commands[0].id);
  } finally { repo.dispose(); }
});

test('advisory missing executable remains a terminal non-launch without automatic retry', async () => {
  const repo = await fixture(`export async function run(context) { try { await context.command('missing', {argv: [context.worktree + '/factory-fixture-missing-executable'], env: {}, required: false}); } catch {} await context.progress('workflow caught infrastructure error'); }`);
  try {
    const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 1, result.stdout + result.stderr);
    const saved = JSON.parse(result.stdout); assert.equal(saved.outcome, 'failed'); assert.equal(saved.cleanup, 'complete'); assert.match(saved.diagnostic, /ENOENT/);
    const history = JSON.parse(repo.call(['history', '--invocation', saved.invocationId]).stdout);
    const attempts = history.attempts.filter(attempt => attempt.operationKey === 'missing');
    assert.equal(attempts.length, 1); assert.equal(attempts[0].launch, 'not_started'); assert.equal(attempts[0].outcome, 'failed');
    assert.equal(history.accounting.occupiedCommands, 0);
  } finally { repo.dispose(); }
});
for (const mode of ['caught', 'unawaited']) {
  test(`default required command failure remains terminal when ${mode}`, async () => {
    const command = `context.command('required-check', {argv: [process.execPath, '-e', 'process.exit(9)'], env: {}})`;
    const source = mode === 'caught' ? `try { await ${command}; } catch {} await context.progress('continued');` : `void ${command};`;
    const repo = await fixture(`export async function run(context) { ${source} }`);
    try {
      const result = repo.invoke(['--new-worktree']); assert.equal(result.status, 1, result.stdout + result.stderr);
      const saved = JSON.parse(result.stdout); assert.equal(saved.outcome, 'failed'); assert.match(saved.diagnostic, /required-check/);
      const history = JSON.parse(repo.call(['history', '--invocation', saved.invocationId]).stdout);
      assert.equal(history.attempts.at(-1).outcome, 'failed'); assert.equal(history.attempts.at(-1).launch, 'started');
      assert.match(JSON.stringify(history.captures), /required.*true/);
    } finally { repo.dispose(); }
  });
}


async function reservedCheckout({paid=false,failAnchor=false}={}) {
  const repo=await fixture(`export async function run(c,inputs){await c.progress('original:'+inputs.request);}`);
  let retainedRun;
  if(paid){
    writeFileSync(join(repo.path,'.factory/workflows/charge.ts'),`import type {WorkflowContext} from '@local/software-factory';export async function run(c:WorkflowContext){const settings={harness:'fake',model:'fixture',permissions:'read-only' as const,skillDelivery:'instructions' as const,prompt:'default'};const first=await c.agent('paid',settings);await c.agent('paid',{...settings,intent:'code_correction',priorAttemptId:first.attemptId,context:'saved fixture findings'});}`);
    const host=join(repo.common,'paid-preparation-host.mjs');
    writeFileSync(host,`import{invoke}from ${JSON.stringify(new URL('../dist/lifecycle.js',import.meta.url).href)};import{createFakeAdapter}from ${JSON.stringify(new URL('../dist/adapters/fake.js',import.meta.url).href)};const r=await invoke({repository:${JSON.stringify(repo.path)},workflow:'.factory/workflows/charge.ts',input:${JSON.stringify(repo.input)},newWorktree:false,worktreeId:${JSON.stringify(repo.path)},adapters:{fake:createFakeAdapter({executable:process.execPath,script:${JSON.stringify(join(packageRoot,'test/fixtures/agent-harness.mjs'))}})}});console.log(JSON.stringify(r));process.exit(r.exitCode);`);
    const paidResult=spawnSync(process.execPath,[host],{encoding:'utf8',timeout:30000});assert.equal(paidResult.status,0,paidResult.stdout+paidResult.stderr);retainedRun=JSON.parse(paidResult.stdout).runId;
    const savedStore=openRepositoryStore(repo.common);try{assert.equal(savedStore.readAccounting(retainedRun).additionalUsed,1);}finally{savedStore.close();}
  }
  const nonce=randomUUID(),script=join(repo.common,'escaped-preparation.mjs'),marker=join(repo.common,'escaped-preparation.json'),filter=join(repo.common,'preparation-filter.mjs');
  writeFileSync(script,`import{writeFileSync}from'node:fs';writeFileSync(process.argv[2],JSON.stringify({pid:process.pid,nonce:process.argv[3]}));setInterval(()=>{},1000);`);
  writeFileSync(filter,`import{spawn}from'node:child_process';const child=spawn(${JSON.stringify(process.execPath)},[${JSON.stringify(script)},${JSON.stringify(marker)},${JSON.stringify(nonce)}],{detached:true,stdio:['ignore','ignore','inherit']});child.unref();process.stdin.pipe(process.stdout);`);
  writeFileSync(join(repo.path,'.gitattributes'),'payload.txt filter=preparation\n');writeFileSync(join(repo.path,'payload.txt'),'preserved checkout payload\n');
  repo.git(['add','.gitattributes','payload.txt']);repo.git(['commit','-m','Commit preparation fixture','--only','.gitattributes','payload.txt']);
  const quote=value=>"'"+value.replaceAll("'","'\\''")+"'";
  repo.git(['config','filter.preparation.smudge',quote(process.execPath)+' '+quote(filter)]);repo.git(['config','filter.preparation.required','true']);
  if(failAnchor){const db=new DatabaseSync(join(repo.common,'factory/history.sqlite'));db.exec("CREATE TRIGGER fail_preparation_anchor BEFORE UPDATE ON worktrees WHEN json_extract(NEW.data,'$.preparation') IS NOT NULL BEGIN SELECT RAISE(FAIL,'fixture anchor write failure'); END;");db.close();}
  let stopped=false;
  const identity=pid=>{const r=spawnSync('/bin/ps',['-p',String(pid),'-o','lstart=','-o','command='],{encoding:'utf8'});return r.status===0?r.stdout.trim():null;};
  const stop=async()=>{
    if(stopped)return;
    const child=JSON.parse(readFileSync(marker,'utf8'));assert.equal(child.nonce,nonce);
    const current=identity(child.pid);assert.ok(current?.includes(script)&&current.includes(nonce),'fresh fixture child identity must match');
    assert.equal(identity(child.pid),current,'fixture start/command identity changed before signal');process.kill(child.pid,'SIGTERM');
    const end=performance.now()+3000;while(identity(child.pid)&&performance.now()<end)await delay(20);
    assert.equal(identity(child.pid),null,'fixture child must be absent before clearance');stopped=true;
  };
  const dispose=async()=>{if(existsSync(marker))await stop();repo.dispose();};
  try {
    const first=repo.invoke(['--new-worktree','--command-timeout-ms','1000','--shutdown-grace-ms','100',...(retainedRun?['--run',retainedRun]:[])]);
    assert.equal(first.status,1,first.stdout+first.stderr);
    const saved=JSON.parse(first.stdout);assert.equal(saved.cleanup,'unknown');assert.ok(existsSync(marker));
    const history=()=>JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout);
    assert.equal(history().worktree.registration,'reserved');assert.equal(history().accounting.occupiedCommands,1);
    assert.equal(readFileSync(join(saved.worktree,'payload.txt'),'utf8'),'preserved checkout payload\n');
    const inspect=()=>JSON.parse(repo.call(['inspect-owner']).stdout);
    const clear=()=>{const claim=inspect().find(row=>row.claim.invocationId===saved.invocationId).claim;const r=repo.call(['clear-owner','--claim',claim.id,'--token',claim.token,'--operator-confirmed','--note','Stopped exact disposable preparation child after fresh start/command verification']);assert.equal(r.status,0,r.stderr);return claim;};
    return {...repo,saved,history,inspect,clear,stop,dispose,marker};
  } catch(error){await dispose();throw error;}
}

for(const selection of ['id','path']) test(`cleared reserved checkout recovers by ${selection} using current entry and inputs`,async()=>{
  const repo=await reservedCheckout({paid:selection==='id'});
  try{
    const uncleared=repo.invoke(['--worktree',selection==='id'?repo.saved.worktreeId:repo.saved.worktree,'--run',repo.saved.runId]);
    assert.notEqual(uncleared.status,0);assert.match(uncleared.stderr,/already claimed/);
    await repo.stop();
    const inactive=repo.invoke(['--worktree',repo.saved.worktreeId,'--run',repo.saved.runId]);assert.notEqual(inactive.status,0);assert.match(inactive.stderr,/already claimed/);
    repo.clear();const before=repo.history(),marker=readFileSync(repo.marker,'utf8');
    writeFileSync(join(repo.saved.worktree,'unfinished.txt'),'preserve unfinished candidate\n');
    writeFileSync(join(repo.saved.worktree,'.factory/workflows/audit.ts'),`export async function run(c,inputs){await c.progress('CURRENT-ENTRY:'+inputs.request);return {current:true};}`);
    writeFileSync(repo.input,'{"request":"fresh input"}');
    const next=repo.invoke(['--worktree',selection==='id'?repo.saved.worktreeId:repo.saved.worktree,'--run',repo.saved.runId]);
    assert.equal(next.status,0,next.stdout+next.stderr);
    const saved=JSON.parse(next.stdout),record=JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout),after=repo.history();
    assert.match(JSON.stringify(record.captures),/CURRENT-ENTRY:fresh input/);
    assert.notEqual(after.worktree.registration,'reserved');assert.equal(saved.worktreeId,repo.saved.worktreeId);
    assert.deepEqual(after.invocation,before.invocation);assert.deepEqual(after.attempts,before.attempts);assert.deepEqual(after.captures,before.captures);
    assert.equal(after.accounting.additionalUsed,before.accounting.additionalUsed);assert.equal(after.accounting.additionalUsed,selection==='id'?1:0);assert.equal(record.accounting.occupiedCommands,0);
    assert.equal(readFileSync(join(saved.worktree,'unfinished.txt'),'utf8'),'preserve unfinished candidate\n');
    assert.equal(readFileSync(join(saved.worktree,'payload.txt'),'utf8'),'preserved checkout payload\n');
    assert.equal(readFileSync(repo.marker,'utf8'),marker,'recovery must not replay checkout/filter');assert.deepEqual(repo.inspect(),[]);
  }finally{await repo.dispose();}
});


for(const change of ['directory','marker','symlink','alias']) test(`reserved recovery refuses replaced ${change} identity`,async()=>{
  const repo=await reservedCheckout();
  try{
    await repo.stop();repo.clear();const before=repo.history();let selected=repo.saved.worktreeId;
    if(change==='directory'){const old=repo.saved.worktree+'-original';renameSync(repo.saved.worktree,old);mkdirSync(repo.saved.worktree);cpSync(old,repo.saved.worktree,{recursive:true});}
    else if(change==='marker'){const marker=join(repo.saved.worktree,'.git'),bytes=readFileSync(marker);renameSync(marker,marker+'-original');writeFileSync(marker,bytes);}
    else if(change==='symlink'){const marker=join(repo.saved.worktree,'.git');renameSync(marker,marker+'-original');symlinkSync(marker+'-original',marker);}
    else {selected=join(repo.common,'reserved-alias');symlinkSync(repo.saved.worktree,selected);}
    const r=repo.invoke(['--worktree',selected,'--run',repo.saved.runId]);assert.notEqual(r.status,0,r.stdout+r.stderr);
    assert.match(r.stdout+r.stderr,/identity|marker|symlink/);
    const after=repo.history();assert.equal(after.worktree.registration,'reserved');assert.deepEqual(after.invocation,before.invocation);assert.deepEqual(after.attempts,before.attempts);assert.deepEqual(repo.inspect(),[]);
  }finally{await repo.dispose();}
});

test('reserved recovery verifies the current Git common directory rather than trusting its marker hash',async()=>{
  const repo=await reservedCheckout(),foreign=await fixture();
  try{
    await repo.stop();repo.clear();const registration=repo.git(['-C',repo.saved.worktree,'rev-parse','--path-format=absolute','--git-dir']).trim();
    writeFileSync(join(registration,'commondir'),foreign.common+'\n');
    const r=repo.invoke(['--worktree',repo.saved.worktreeId,'--run',repo.saved.runId]);assert.notEqual(r.status,0,r.stdout+r.stderr);
    assert.match(r.stdout+r.stderr,/another repository|Git probe failed|command failed/);
    assert.equal(repo.history().worktree.registration,'reserved');assert.deepEqual(repo.inspect(),[]);
  }finally{await repo.dispose();foreign.dispose();}
});

test('legacy reserved rows without original identity evidence remain refused',async()=>{
  const repo=await fixture();let store;
  try{
    const directory=join(repo.common,'factory/worktrees');mkdirSync(directory);store=openRepositoryStore(repo.common);
    const run=await store.createRun(),worktree=await store.reserveWorktree(join(directory,randomUUID()));
    const invocation=await store.startInvocation({runId:run.id,worktreeId:worktree.id,owner:{host:'fixture',pid:process.pid,start:'fixture'}});
    repo.git(['worktree','add','--detach',worktree.path,'HEAD']);
    await store.finalizeInvocation({id:invocation.id,outcome:'failed',cleanup:'complete',claimId:invocation.claim.id,token:invocation.claim.token});store.close();store=undefined;
    for(const selected of [worktree.id,worktree.path]){const r=repo.invoke(['--worktree',selected,'--run',run.id]);assert.notEqual(r.status,0);assert.match(r.stdout+r.stderr,/lacks original preparation identity evidence/);}
    store=openRepositoryStore(repo.common);assert.equal(store.readWorktree(worktree.id).registration,'reserved');assert.deepEqual(store.inspectOwners(),[]);
    assert.equal(readFileSync(join(worktree.path,'tracked.txt'),'utf8'),'committed\n');
  }finally{store?.close();repo.dispose();}
});

test('prepared registration reconciliation is exact-claim guarded and commits at most once',async()=>{
  const repo=await reservedCheckout();let a,b;
  try{
    await repo.stop();repo.clear();const registration=repo.git(['-C',repo.saved.worktree,'rev-parse','--path-format=absolute','--git-dir']).trim();
    a=openRepositoryStore(repo.common);b=openRepositoryStore(repo.common);
    const current=await a.startInvocation({runId:repo.saved.runId,worktreeId:repo.saved.worktreeId,owner:{host:'fixture',pid:process.pid,start:'fixture'}});
    await assert.rejects(b.startInvocation({runId:repo.saved.runId,worktreeId:repo.saved.worktreeId,owner:{host:'fixture',pid:process.pid,start:'fixture'}}),/already claimed/);
    await assert.rejects(a.reconcileWorktreePreparation({id:repo.saved.worktreeId,claimId:current.claim.id,token:'stale-token',registration}),/claim\/token/);
    assert.equal(a.readWorktree(repo.saved.worktreeId).registration,'reserved');
    const request={id:repo.saved.worktreeId,claimId:current.claim.id,token:current.claim.token,registration};
    const results=await Promise.allSettled([a.reconcileWorktreePreparation(request),b.reconcileWorktreePreparation(request)]);
    assert.equal(results.filter(r=>r.status==='fulfilled').length,1);assert.equal(results.filter(r=>r.status==='rejected').length,1);
    assert.equal(a.readWorktree(repo.saved.worktreeId).registration,registration);
    await a.finalizeInvocation({id:current.id,outcome:'failed',cleanup:'complete',claimId:current.claim.id,token:current.claim.token});
  }finally{a?.close();b?.close();await repo.dispose();}
});

test('failed reconciliation transaction remains reserved and an explicit fresh invocation can recover',async()=>{
  const repo=await reservedCheckout();let database;
  try{
    await repo.stop();repo.clear();const before=repo.history();
    writeFileSync(join(repo.saved.worktree,'.factory/workflows/audit.ts'),`export async function run(c){await c.progress('AFTER-RECOVERY');}`);
    database=new DatabaseSync(join(repo.common,'factory/history.sqlite'));database.exec("CREATE TRIGGER fail_preparation_reconciliation BEFORE UPDATE ON worktrees WHEN json_extract(OLD.data,'$.registration')='reserved' AND json_extract(NEW.data,'$.registration')!='reserved' BEGIN SELECT RAISE(FAIL,'fixture reconciliation interruption'); END;");database.close();database=undefined;
    const first=repo.invoke(['--worktree',repo.saved.worktreeId,'--run',repo.saved.runId]);assert.equal(first.status,3,first.stdout+first.stderr);
    assert.match(first.stdout,/fixture reconciliation interruption/);const failed=JSON.parse(first.stdout);
    const h=JSON.parse(repo.call(['history','--invocation',failed.invocationId]).stdout);assert.doesNotMatch(JSON.stringify(h.captures),/AFTER-RECOVERY/);assert.equal(repo.history().worktree.registration,'reserved');assert.deepEqual(repo.history().attempts,before.attempts);assert.deepEqual(repo.inspect(),[]);
    database=new DatabaseSync(join(repo.common,'factory/history.sqlite'));database.exec('DROP TRIGGER fail_preparation_reconciliation');database.close();database=undefined;
    const second=repo.invoke(['--worktree',repo.saved.worktreeId,'--run',repo.saved.runId]);assert.equal(second.status,0,second.stdout+second.stderr);
    assert.equal(repo.history().accounting.additionalUsed,before.accounting.additionalUsed);
  }finally{database?.close();await repo.dispose();}
});


test('SIGTERM during claimed recovery metadata leaves registration reserved for explicit fresh recovery',async()=>{
  const repo=await reservedCheckout();let child,closed;
  try{
    await repo.stop();repo.clear();const before=repo.history();
    const bin=join(repo.common,'recovery-bin'),ready=join(repo.common,'recovery-metadata-ready');mkdirSync(bin);
    const realGit=realpathSync(spawnSync('/usr/bin/which',['git'],{encoding:'utf8'}).stdout.trim()),shim=join(bin,'git');
    writeFileSync(shim,'#!'+process.execPath+'\n'+`const{spawnSync}=require('node:child_process');const{writeFileSync}=require('node:fs');const args=process.argv.slice(2);const run=()=>{const r=spawnSync(${JSON.stringify(realGit)},args,{stdio:'inherit',env:process.env});process.exit(r.status??1);};if(args.includes('worktree')&&args.includes('list')){writeFileSync(${JSON.stringify(ready)},'claimed metadata');setTimeout(run,5000);}else run();`);chmodSync(shim,0o755);
    child=spawn(process.execPath,[cli,'invoke','--repository',repo.path,'--workflow','.factory/workflows/audit.ts','--input',repo.input,'--worktree',repo.saved.worktreeId,'--run',repo.saved.runId,'--shutdown-grace-ms','100','--json'],{env:{...process.env,PATH:bin+':'+process.env.PATH},stdio:['ignore','pipe','pipe']});let stdout='',stderr='';child.stdout.on('data',c=>stdout+=c);child.stderr.on('data',c=>stderr+=c);closed=new Promise(resolve=>child.once('close',status=>resolve(status)));
    const end=performance.now()+8000;while(!existsSync(ready)&&performance.now()<end)await delay(20);assert.ok(existsSync(ready),'claimed Git metadata was not reached');child.kill('SIGTERM');assert.equal(await closed,143,stdout+stderr);
    const saved=JSON.parse(stdout),interrupted=JSON.parse(repo.call(['history','--invocation',saved.invocationId]).stdout);assert.equal(saved.cleanup,'complete');assert.equal(repo.history().worktree.registration,'reserved');assert.equal(interrupted.attempts.some(a=>a.operationKey.startsWith('startup/build/')),false);assert.deepEqual(repo.inspect(),[]);assert.deepEqual(repo.history().attempts,before.attempts);
    const next=repo.invoke(['--worktree',repo.saved.worktreeId,'--run',repo.saved.runId]);assert.equal(next.status,0,next.stdout+next.stderr);
  }finally{if(child&&child.exitCode===null&&child.signalCode===null){child.kill('SIGTERM');await closed;}await repo.dispose();}
});


test('failed preparation anchor persistence leaves evidence missing and refuses guessed recovery',async()=>{
  const repo=await reservedCheckout({failAnchor:true});
  try{
    assert.equal(repo.history().worktree.preparation,undefined);await repo.stop();repo.clear();
    const before=repo.history(),r=repo.invoke(['--worktree',repo.saved.worktreeId,'--run',repo.saved.runId]);assert.equal(r.status,3,r.stdout+r.stderr);assert.match(r.stdout,/lacks original preparation identity evidence/);
    assert.equal(repo.history().worktree.registration,'reserved');assert.deepEqual(repo.history().attempts,before.attempts);assert.equal(readFileSync(join(repo.saved.worktree,'payload.txt'),'utf8'),'preserved checkout payload\n');
  }finally{await repo.dispose();}
});

test('reserved recovery cannot silently start a new run to discard paid allowance',async()=>{
  const repo=await reservedCheckout({paid:true});
  try{
    await repo.stop();repo.clear();const before=repo.history();assert.equal(before.accounting.additionalUsed,1);
    const changed=repo.invoke(['--worktree',repo.saved.worktreeId]);assert.equal(changed.status,3,changed.stdout+changed.stderr);assert.match(changed.stdout,/original retained run/);
    assert.equal(repo.history().worktree.registration,'reserved');assert.equal(repo.history().accounting.additionalUsed,1);assert.deepEqual(repo.inspect(),[]);
    const retained=repo.invoke(['--worktree',repo.saved.worktreeId,'--run',repo.saved.runId]);assert.equal(retained.status,0,retained.stdout+retained.stderr);assert.equal(repo.history().accounting.additionalUsed,1);
  }finally{await repo.dispose();}
});

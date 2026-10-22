import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, mkdirSync, readFileSync, symlinkSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { createRepository } from './fixtures/repository.mjs';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { createCopilotAdapter } from '../dist/adapters/copilot.js';

const root = fileURLToPath(new URL('../', import.meta.url));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const inputs = { harness: 'copilot', model: 'gpt-6-luna', reasoning: 'low', permissions: 'read-only', skillDelivery: 'instructions', requiredCapabilities: [], prompt: 'success', skills: [] };
const events = values => values.map(value => JSON.stringify(value)).join('\n') + '\n';
const turn = { type: 'assistant.turn_start', data: { turnId: '0' } };
const finalStart = { type: 'assistant.message_start', data: { messageId: 'final', phase: 'final_answer' } };
const finalDelta = content => ({ type: 'assistant.message_delta', data: { messageId: 'final', deltaContent: content } });
const turnEnd = { type: 'assistant.turn_end', data: { turnId: '0' } };
const result = { type: 'result', sessionId: 'session-a', exitCode: 0 };
const envelope = '{"kind":"result","payload":{"summary":"qualified"}}';

async function fixture(source = `return context.agent('report',{});`, mode = 'success', withSkill = false) {
  const repo = createRepository(), common = join(repo.path, '.git');
  mkdirSync(join(repo.path, '.factory/workflows'), { recursive: true });
  writeFileSync(join(repo.path, '.factory/package.json'), '{"type":"module"}');
  writeFileSync(join(repo.path, '.factory/workflows/main.ts'), `import type {WorkflowContext} from '@local/software-factory';export async function run(context:WorkflowContext){${source}}`);
  const skills = withSkill ? [{ name: 'literal', file: '.factory/skills/SKILL.md', resources: ['.factory/skills/guide.md'] }] : [];
  if (withSkill) {
    mkdirSync(join(repo.path, '.factory/skills'));
    writeFileSync(join(repo.path, '.factory/skills/SKILL.md'), 'Keep literal instructions\nRESOURCE_C7B2');
    writeFileSync(join(repo.path, '.factory/skills/guide.md'), 'Resource data\nPRIVATE_LITERAL_C7B2');
  }
  writeFileSync(join(repo.path, '.factory/agents.json'), JSON.stringify({ defaults: { harness: 'copilot', model: 'gpt-6-luna', reasoning: 'low', permissions: 'read-only', skillDelivery: 'instructions', prompt: mode, skills } }));
  repo.git(['add', '.factory']); repo.git(['commit', '-m', 'Copilot fixture', '--only', '.factory']);
  (await initializeRepositoryStore(common, { release: 'fixture' })).close();
  const tc = join(common, 'factory/toolchain'); mkdirSync(tc); cpSync(join(root, 'node_modules'), join(tc, 'node_modules'), { recursive: true });
  writeFileSync(join(tc, 'manifest.json'), JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2', dependencies: { '@types/node': '24.19.2' } }));
  const packageRoot = join(common, 'copilot-package'); mkdirSync(packageRoot);
  const packageJson = '{"name":"@github/copilot","version":"1.0.101","type":"module"}';
  const loader = readFileSync(join(root, 'test/fixtures/copilot-harness.mjs'));
  writeFileSync(join(packageRoot, 'package.json'), packageJson);
  writeFileSync(join(packageRoot, 'index.js'), loader);
  const manifest = [
    { bytes: loader.length, mode: 420, path: 'index.js', sha256: hash(loader) },
    { bytes: Buffer.byteLength(packageJson), mode: 420, path: 'package.json', sha256: hash(packageJson) },
  ];
  const manifestFile = join(common, 'copilot-manifest.json');
  writeFileSync(manifestFile, JSON.stringify(manifest) + '\n');
  const manifestSha256 = hash(JSON.stringify(manifest));
  const host = join(common, 'host.mjs'), input = join(common, 'input.json'); writeFileSync(input, '{}');
  writeFileSync(host, `import {invoke} from ${JSON.stringify(new URL('../dist/lifecycle.js', import.meta.url).href)};import {createCopilotAdapter} from ${JSON.stringify(new URL('../dist/adapters/copilot.js', import.meta.url).href)};const options=JSON.parse(process.argv[2]);const adapter=createCopilotAdapter({packageRoot:${JSON.stringify(packageRoot)},manifestFile:${JSON.stringify(manifestFile)},manifestSha256:${JSON.stringify(manifestSha256)},environment:{PATH:process.env.PATH,HOME:process.env.HOME}});const result=await invoke({...options,adapters:{copilot:adapter}});console.log(JSON.stringify(result));process.exit(result.exitCode);`);
  const invoke = (extra = {}) => spawnSync(process.execPath, [host, JSON.stringify({ repository: repo.path, workflow: '.factory/workflows/main.ts', input, newWorktree: true, shutdownGraceMs: 100, ...extra })], { encoding: 'utf8', timeout: 20000 });
  const history = id => { const store = openRepositoryStore(common); try { return { history: store.readHistory(id, { limit: 100 }), sessions: store.readSessions({ invocationId: id }) }; } finally { store.close(); } };
  return { ...repo, packageRoot, manifestFile, manifestSha256, invoke, history };
}
const agents = history => history.attempts.filter(attempt => attempt.kind === 'agent');
const adapter = fixture => createCopilotAdapter({ packageRoot: fixture.packageRoot, manifestFile: fixture.manifestFile, manifestSha256: fixture.manifestSha256, environment: { PATH: '/usr/bin:/bin', HOME: '/tmp/native-auth-not-read' } });

test('Copilot public invocation accepts only a final answer followed by terminal result', async () => {
  const repo = await fixture();
  try {
    const run = repo.invoke(); assert.equal(run.status, 0, run.stdout + run.stderr);
    const saved = JSON.parse(run.stdout), { history, sessions } = repo.history(saved.invocationId);
    assert.equal(agents(history).length, 1); assert.equal(agents(history)[0].outcome, 'succeeded');
    assert.equal(sessions.sessions.length, 1); assert.ok(sessions.sessions[0].nativeId);
    assert.deepEqual(sessions.sessions[0].usage, { state: 'unknown' }); assert.deepEqual(sessions.sessions[0].loadedSkills, { state: 'unknown' });
    const launch = JSON.parse(readFileSync(join(saved.worktree, 'copilot-launches.jsonl'), 'utf8'));
    assert.ok(launch.stdin.startsWith('Active task:\nsuccess\n'));
    assert.ok(!launch.args.some(arg => arg.includes('Active task:') || arg.includes('success')));
    assert.match(JSON.stringify(history.captures), /decoy/);
  } finally { repo.dispose(); }
});

test('Copilot public invocation preserves task, correction and resource bytes on managed stdin', async () => {
  const repo = await fixture(`const first=await context.agent('write',{prompt:'malformed'});return context.agent('write',{prompt:'success',intent:'format_correction',priorAttemptId:first.attemptId,context:'Prior result PRIVATE_CONTEXT failed'});`, 'success', true);
  try {
    const run = repo.invoke(); assert.equal(run.status, 0, run.stdout + run.stderr);
    const saved = JSON.parse(run.stdout), launches = readFileSync(join(saved.worktree, 'copilot-launches.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
    assert.equal(launches.length, 2);
    assert.ok(launches[0].stdin.startsWith('Active task:\nmalformed\n'));
    assert.ok(launches[1].stdin.startsWith('Active task:\nsuccess\n'));
    assert.match(launches[1].stdin, /Saved context:[\s\S]*PRIVATE_CONTEXT/);
    for (const launch of launches) {
      assert.match(launch.stdin, /Keep literal instructions\nRESOURCE_C7B2/);
      assert.match(launch.stdin, /Resource data:[\s\S]*Resource data\nPRIVATE_LITERAL_C7B2/);
      assert.ok(!launch.args.some(arg => /PRIVATE_CONTEXT|PRIVATE_LITERAL_C7B2|RESOURCE_C7B2|Active task:/.test(arg)));
    }
  } finally { repo.dispose(); }
});

test('Copilot final decoder rejects missing terminal, malformed private bytes and native failures', async () => {
  const repo = await fixture();
  try {
    const native = adapter(repo);
    assert.deepEqual(native.decodeFinal(events([turn, finalStart, finalDelta(envelope), turnEnd, result])), { kind: 'result', payload: { summary: 'qualified' } });
    for (const invalid of [
      [turn, finalStart, finalDelta(envelope), turnEnd],
      [turn, { type: 'assistant.message', data: { content: envelope } }, turnEnd, result],
      [turn, finalStart, finalDelta('PRIVATE_INVALID_ASSISTANT'), turnEnd, result],
      [turn, finalStart, finalDelta(envelope), turnEnd, { ...result, exitCode: 1 }],
      [turn, finalStart, finalDelta(envelope), turnEnd, { ...result, error: { message: 'PRIVATE_NATIVE_FAILURE' } }],
      [turn, { type: 'tool.execution_complete', data: { success: false, error: { code: 'denied' } } }, finalStart, finalDelta(envelope), turnEnd, result],
      [turn, finalStart, finalDelta(envelope), turnEnd, result, finalDelta(envelope)],
    ]) assert.throws(() => native.decodeFinal(events(invalid)), error => !error.message.includes('PRIVATE_INVALID_ASSISTANT'));
    assert.throws(() => native.decodeFinal('PRIVATE_JSONL_BYTES'), error => error.message === 'invalid Copilot JSONL record');
  } finally { repo.dispose(); }
});

test('Copilot launch pins package closure, delivers literal correction resources through stdin and refuses unsupported modes', async () => {
  const repo = await fixture();
  try {
    const native = adapter(repo), request = { attemptId: 'a', invocationId: 'i', worktree: '/tmp/fixture', inputs: { ...inputs, prompt: 'literal `$(false)`', skills: [{ name: 'fixture', file: 'SKILL.md', instructions: 'bytes\nunchanged', resources: [{ file: 'guide.md', content: 'RESOURCE_C7B2' }] }] }, context: 'Prior result failed validation' };
    const launch = native.start(request);
    assert.equal(launch.argv[0], process.execPath); assert.equal(launch.argv[1], join(repo.packageRoot, 'index.js'));
    for (const flag of ['--no-auto-update', '--no-ask-user', '--no-remote', '--no-remote-export', '--disable-builtin-mcps', '--output-format=json', '--stream=on', '--model=gpt-6-luna', '--reasoning-effort=low']) assert.ok(launch.argv.includes(flag), flag);
    assert.ok(!launch.argv.some(arg => arg.includes(request.inputs.prompt) || arg.includes('RESOURCE_C7B2') || arg.includes(request.context)));
    assert.ok(launch.stdin.startsWith(`Active task:\n${request.inputs.prompt}\n`));
    assert.match(launch.stdin, /Saved context:[\s\S]*Prior result failed validation/);
    assert.match(launch.stdin, /Supplied skill: fixture[\s\S]*bytes\nunchanged/);
    assert.match(launch.stdin, /Resource data: guide\.md[\s\S]*RESOURCE_C7B2/);
    assert.equal(launch.env.COPILOT_AUTO_UPDATE, 'false'); assert.equal(native.canReuse(inputs, inputs), false);
    assert.throws(() => native.start({ ...request, reuseNativeId: 'old' }), /reuse/);
    assert.throws(() => native.validateProfile({ ...inputs, skillDelivery: 'native' }), /native skill/);
    assert.throws(() => native.validateProfile({ ...inputs, permissions: 'workspace-write' }), /workspace-write/);
    assert.throws(() => native.validateProfile({ ...inputs, requiredCapabilities: ['workspace-write'] }), /unsupported/);
    assert.throws(() => native.validateProfile({ ...inputs, model: 'auto' }), /unqualified/);
    const unsafe = createCopilotAdapter({ packageRoot: repo.packageRoot, manifestFile: repo.manifestFile, manifestSha256: repo.manifestSha256, environment: { COPILOT_ALLOW_ALL: 'true' } });
    assert.throws(() => unsafe.validateProfile(inputs), /allow-all/);
  } finally { repo.dispose(); }
});

test('Copilot package closure rejects drift, links, traversal and wrong version before launch', async () => {
  const repo = await fixture();
  try {
    const native = adapter(repo); native.validateProfile(inputs);
    writeFileSync(join(repo.packageRoot, 'extra.js'), 'drift');
    assert.throws(() => native.validateProfile(inputs), /package/);
    const bad = createCopilotAdapter({ packageRoot: repo.packageRoot, manifestFile: repo.manifestFile, manifestSha256: '0'.repeat(64), environment: {} });
    assert.throws(() => bad.validateProfile(inputs), /manifest/);
    const traversedRoot = createCopilotAdapter({ packageRoot: `${repo.packageRoot}/../copilot-package`, manifestFile: repo.manifestFile, manifestSha256: repo.manifestSha256, environment: {} });
    assert.throws(() => traversedRoot.validateProfile(inputs), /absolute package/);
    const malicious = [{ bytes: 1, mode: 420, path: '../escape', sha256: '0'.repeat(64) }];
    writeFileSync(repo.manifestFile, JSON.stringify(malicious));
    const traversal = createCopilotAdapter({ packageRoot: repo.packageRoot, manifestFile: repo.manifestFile, manifestSha256: hash(JSON.stringify(malicious)), environment: {} });
    assert.throws(() => traversal.validateProfile(inputs), /path|manifest/);
  } finally { repo.dispose(); }
  const linked = await fixture();
  try { symlinkSync('index.js', join(linked.packageRoot, 'alias')); assert.throws(() => adapter(linked).validateProfile(inputs), /link|package/); } finally { linked.dispose(); }
  const versioned = await fixture();
  try {
    const changed = '{"name":"@github/copilot","version":"1.0.102","type":"module"}';
    writeFileSync(join(versioned.packageRoot, 'package.json'), changed);
    const manifest = JSON.parse(readFileSync(versioned.manifestFile, 'utf8'));
    manifest[1] = { ...manifest[1], bytes: Buffer.byteLength(changed), sha256: hash(changed) };
    writeFileSync(versioned.manifestFile, JSON.stringify(manifest) + '\n');
    const otherVersion = createCopilotAdapter({ packageRoot: versioned.packageRoot, manifestFile: versioned.manifestFile, manifestSha256: hash(JSON.stringify(manifest)), environment: {} });
    assert.throws(() => otherVersion.validateProfile(inputs), /version/);
  } finally { versioned.dispose(); }
});

for (const mode of ['malformed', 'native-error', 'denied', 'no-terminal']) test(`Copilot ${mode} cannot become a successful or interactive result`, async () => {
  const repo = await fixture(undefined, mode);
  try {
    const run = repo.invoke(); assert.equal(run.status, 1, run.stdout + run.stderr);
    const saved = JSON.parse(run.stdout), { history } = repo.history(saved.invocationId);
    assert.equal(agents(history).length, 1); assert.equal(agents(history)[0].outcome, 'failed');
    assert.equal(history.captures.filter(c => c.channel === 'request').length, 0);
    assert.doesNotMatch(saved.diagnostic ?? '', /PRIVATE_INVALID_ASSISTANT|private native detail/);
    assert.equal(readFileSync(join(saved.worktree, 'copilot-launches.jsonl'), 'utf8').trim().split('\n').length, 1);
  } finally { repo.dispose(); }
});

test('Copilot fresh correction and concurrent launches keep distinct native identities', async () => {
  const repo = await fixture(`const first=await context.agent('write',{prompt:'malformed'});const second=await context.agent('write',{prompt:'malformed',intent:'format_correction',priorAttemptId:first.attemptId,reuse:true,context:'correct invalid output'});await Promise.all([context.agent('review',{purpose:'review',prompt:'success'}),context.agent('audit',{purpose:'review',prompt:'success'})]);return second;`);
  try {
    const run = repo.invoke(); assert.equal(run.status, 0, run.stdout + run.stderr);
    const saved = JSON.parse(run.stdout), { history, sessions } = repo.history(saved.invocationId);
    assert.deepEqual(agents(history).map(attempt => attempt.outcome), ['failed', 'succeeded', 'succeeded', 'succeeded']);
    assert.equal(history.accounting.additionalUsed, 1); assert.equal(new Set(sessions.sessions.map(session => session.nativeId)).size, 4);
    assert.ok(agents(history).every(attempt => attempt.agent.sessionMode === 'fresh'));
  } finally { repo.dispose(); }
});

test('Copilot genuine final assistant question remains a single needs-input request', async () => {
  const repo = await fixture(undefined, 'question');
  try {
    const run = repo.invoke(); assert.equal(run.status, 2, run.stdout + run.stderr);
    const saved = JSON.parse(run.stdout), { history } = repo.history(saved.invocationId);
    assert.equal(agents(history)[0].outcome, 'needs_input');
    assert.equal(history.captures.filter(capture => capture.channel === 'request').length, 1);
    assert.equal(history.accounting.additionalUsed, 0);
  } finally { repo.dispose(); }
});

test('Copilot owned stop terminates a held child with measured group absence', async () => {
  const repo = await fixture(`return context.agent('hold',{prompt:'hold',timeoutMs:300});`);
  try {
    const run = repo.invoke(); assert.equal(run.status, 1, run.stdout + run.stderr);
    const saved = JSON.parse(run.stdout), { history } = repo.history(saved.invocationId), attempt = agents(history)[0];
    assert.match(saved.diagnostic, /timeout/); assert.equal(attempt.outcome, 'failed'); assert.equal(attempt.quiescent, true);
    assert.equal(history.accounting.occupiedAgents, 0); assert.throws(() => process.kill(-attempt.owner.pid, 0), error => error.code === 'ESRCH');
  } finally { repo.dispose(); }
});

test('Copilot launch parsers isolate terminal identities and keep unknown telemetry unknown', async () => {
  const repo = await fixture();
  try {
    const native = adapter(repo), request = { attemptId: 'a', invocationId: 'i', worktree: '/tmp/fixture', inputs, context: '' };
    const left = native.start(request), right = native.start({ ...request, attemptId: 'b' });
    assert.equal(left.mapEvent(JSON.stringify(turn), 'stdout'), undefined);
    assert.equal(right.mapEvent(JSON.stringify(turn), 'stdout'), undefined);
    for (const launch of [left, right]) { launch.mapEvent(JSON.stringify(finalStart), 'stdout'); launch.mapEvent(JSON.stringify(finalDelta(envelope)), 'stdout'); launch.mapEvent(JSON.stringify(turnEnd), 'stdout'); }
    assert.deepEqual(left.mapEvent(JSON.stringify(result), 'stdout'), { nativeId: 'session-a', parentNativeId: null, lifecycle: 'succeeded' });
    assert.deepEqual(right.mapEvent(JSON.stringify({ ...result, sessionId: 'session-b' }), 'stdout'), { nativeId: 'session-b', parentNativeId: null, lifecycle: 'succeeded' });
    assert.throws(() => left.mapEvent(JSON.stringify(result), 'stdout'), /terminal/);
  } finally { repo.dispose(); }
});


test('Copilot artifact validation is separate from native platform qualification', async () => {
  const repo = await fixture();
  const descriptor = Object.getOwnPropertyDescriptor(process, 'platform');
  const architecture = Object.getOwnPropertyDescriptor(process, 'arch');
  try {
    const native = adapter(repo);
    for (const [platform, arch] of [['darwin', 'arm64'], ['darwin', 'x64'], ['linux', 'x64'], ['win32', 'x64']]) {
      Object.defineProperty(process, 'platform', { ...descriptor, value: platform });
      Object.defineProperty(process, 'arch', { ...architecture, value: arch });
      assert.doesNotThrow(() => native.validateProfile(inputs));
    }
  } finally {
    Object.defineProperty(process, 'platform', descriptor);
    Object.defineProperty(process, 'arch', architecture);
    repo.dispose();
  }
});

import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { createEvidenceRoot, createCollector, collectEvidence, hasSelectorCoverage, limits } from './selector-timing.mjs';

test('qualification exports fixed timing records and rejects additional private fields', () => {
  const root = createEvidenceRoot();
  try {
    const collector = createCollector(root);
    collector.mark('worker-open');
    const finish = collector.begin('copy'); finish();
    collector.close();
    const result = collectEvidence(root);
    assert.equal(result.status, 'complete');
    assert.equal(result.records.length, 4);
    assert.ok(result.records.every(record => !('pid' in record) && !('path' in record)));
    assert.throws(() => collector.mark('copy', { private: 'secret' }), /invalid/);
    assert.equal(readFileSync(join(root.path, 'owner.json'), 'utf8').includes(root.token), true);
    assert.equal(hasSelectorCoverage(result.records), false);
  } finally { rmSync(root.path, { recursive: true, force: true }); }
});

test('real failing case timing excludes exception contents and preserves its failed exit', () => {
  const root = createEvidenceRoot(), directory = mkdtempSync(join(tmpdir(), 'selector-failure-'));
  try {
    const file = join(directory, 'learning.test.mjs');
    writeFileSync(file, `import test from 'node:test'; test('failed, needs-input and interrupted invocations are valid explicit learning sources', () => { throw new Error('private-failure-text'); });`);
    const env = { ...process.env, FACTORY_SELECTOR_TIMING_ROOT: root.path, FACTORY_SELECTOR_TIMING_TOKEN: root.token }; delete env.NODE_TEST_CONTEXT;
    const child = spawnSync(process.execPath, ['--import',new URL('./selector-timing-preload.mjs', import.meta.url).href,'--test',file], { env, encoding: 'utf8', timeout: 5000 });
    assert.equal(child.status, 1);
    const evidence = collectEvidence(root);
    assert.equal(evidence.status, 'complete');
    assert.equal(evidence.records.find(record => record.stage === 'case' && record.phase === 'end').disposition, 'failed');
    assert.equal(JSON.stringify(evidence).includes('private-failure-text'), false);
  } finally { rmSync(root.path, { recursive: true, force: true }); rmSync(directory, { recursive: true, force: true }); }
});

test('driver rejects missing arguments or a reused export root before running fixtures', () => {
  const directory = mkdtempSync(join(tmpdir(), 'selector-preflight-'));
  try {
    for (const args of [[], [directory]]) {
      const env = { ...process.env }; delete env.NODE_TEST_CONTEXT;
      const child = spawnSync(process.execPath, [new URL('./selector-timing-driver.mjs', import.meta.url).pathname, ...args], { env, encoding: 'utf8', timeout: 5000 });
      assert.equal(child.status, 1);
      assert.equal(child.stdout, '');
      assert.equal(child.stderr, 'factory qualification timing: incomplete\n');
      assert.deepEqual(readdirSync(directory), []);
    }
  } finally { rmSync(directory, { recursive: true, force: true }); }
});

test('ordered worker emits real immediate dequeue, complete and final summary receipts', () => {
  const root = createEvidenceRoot(), directory = mkdtempSync(join(tmpdir(), 'selector-ordered-'));
  try {
    const file = join(directory, 'learning.test.mjs');
    writeFileSync(file, `import test from 'node:test'; test('failed, needs-input and interrupted invocations are valid explicit learning sources', async () => { await new Promise(resolve => setTimeout(resolve, 10)); });`);
    const script = `import { runOrderedTests } from ${JSON.stringify(new URL('../scripts/ordered-tests.mjs', import.meta.url).href)}; import { timingNodeArgs } from ${JSON.stringify(new URL('./selector-timing.mjs', import.meta.url).href)}; process.exitCode = await runOrderedTests([${JSON.stringify(file)}], { concurrency: 1, cwd: ${JSON.stringify(directory)}, execArgv: timingNodeArgs() });`;
    const env = { ...process.env, FACTORY_SELECTOR_TIMING_ROOT: root.path, FACTORY_SELECTOR_TIMING_TOKEN: root.token }; delete env.NODE_TEST_CONTEXT;
    const child = spawnSync(process.execPath, ['--input-type=module','-e',script], { env, encoding: 'utf8', timeout: 5000 });
    assert.equal(child.status, 0, child.stderr);
    const evidence = collectEvidence(root);
    assert.equal(evidence.status, 'complete');
    assert.ok(evidence.records.some(record => record.stage === 'dequeue' && record.fileId === 'learning.test.mjs'));
    assert.ok(evidence.records.some(record => record.stage === 'complete' && record.fileId === 'learning.test.mjs'));
    assert.ok(evidence.records.some(record => record.stage === 'summary' && record.fileId === ''));
  } finally { rmSync(root.path, { recursive: true, force: true }); rmSync(directory, { recursive: true, force: true }); }
});

test('qualification reports incomplete for an open span or exhausted record bound', () => {
  for (const overflow of [false, true]) {
    const root = createEvidenceRoot();
    try {
      const collector = createCollector(root);
      collector.mark('worker-open');
      if (overflow) for (let i = 0; i < limits.records + 5; i++) collector.mark('copy');
      else collector.begin('copy');
      collector.close();
      const evidence = collectEvidence(root);
      assert.equal(evidence.status, 'incomplete');
      assert.ok(evidence.records.length <= limits.records);
    } finally { rmSync(root.path, { recursive: true, force: true }); }
  }
});

test('qualification rejects corrupt or private records rather than forwarding them', () => {
  const root = createEvidenceRoot();
  try {
    const collector = createCollector(root); collector.mark('worker-open'); collector.close();
    const file = join(root.path, readdirSync(root.path).find(name => name.endsWith('.jsonl')));
    const lines = readFileSync(file, 'utf8').trim().split('\n');
    lines[0] = JSON.stringify({ ...JSON.parse(lines[0]), argv: 'private-input' });
    writeFileSync(file, lines.join('\n') + '\n');
    assert.throws(() => collectEvidence(root), /invalid/);
  } finally { rmSync(root.path, { recursive: true, force: true }); }
});

test('qualification caps worker files atomically and refuses an extra writer', () => {
  const root = createEvidenceRoot();
  try {
    for (let i = 0; i < limits.files; i++) { const collector = createCollector(root); collector.mark('worker-open'); collector.close(); }
    assert.throws(() => createCollector(root), /invalid/);
    assert.equal(readdirSync(root.path).length, limits.files + 2);
    assert.equal(collectEvidence(root).status, 'incomplete');
  } finally { rmSync(root.path, { recursive: true, force: true }); }
});

test('pinned Node emits direct case start and finish receipts through the real preload', () => {
  assert.equal(process.version, 'v24.22.1');
  const root = createEvidenceRoot(), directory = mkdtempSync(join(tmpdir(), 'selector-case-'));
  try {
    // The registered label is fixed; this disposable file runs no product code.
    const file = join(directory, 'learning.test.mjs');
    writeFileSync(file, `import test from 'node:test';\nimport { timingSync } from ${JSON.stringify(new URL('./selector-timing.mjs', import.meta.url).href)};\ntest('failed, needs-input and interrupted invocations are valid explicit learning sources', async () => { timingSync('copy', () => {}); await new Promise(resolve => setTimeout(resolve, 20)); });\n`);
    const env = { ...process.env, FACTORY_SELECTOR_TIMING_ROOT: root.path, FACTORY_SELECTOR_TIMING_TOKEN: root.token };
    delete env.NODE_TEST_CONTEXT;
    const child = spawnSync(process.execPath, ['--import', new URL('./selector-timing-preload.mjs', import.meta.url).href, '--test', file], { env, encoding: 'utf8', timeout: 5000 });
    assert.equal(child.status, 0, child.stderr);
    const evidence = collectEvidence(root);
    assert.equal(evidence.status, 'complete');
    const spans = evidence.records.filter(record => record.stage === 'case');
    assert.deepEqual(spans.map(record => record.phase), ['begin', 'end']);
    assert.equal(spans[0].fileId, 'learning.test.mjs');
    assert.equal(spans[0].caseId, '2');
    assert.equal(spans[0].spanId, spans[1].spanId);
    assert.ok(spans[1].wallMs >= 15);
    assert.ok(spans[1].monoMs > spans[0].monoMs);
    assert.ok(spans[1].cpuUserUs >= 0);
    const fixtureMarkers = evidence.records.filter(record => record.stage === 'copy');
    assert.deepEqual(fixtureMarkers.map(record => [record.phase, record.fileId, record.caseId]), [['begin','learning.test.mjs','2'],['end','learning.test.mjs','2']]);
  } finally { rmSync(root.path, { recursive: true, force: true }); rmSync(directory, { recursive: true, force: true }); }
});

test('attempt timing pages allowlisted metadata read-only and uses opaque stable IDs', () => {
  const root = createEvidenceRoot(), container = mkdtempSync(join(tmpdir(), 'factory-repository-'));
  try {
    const repository = join(container, 'repository'), directory = join(repository, '.git/factory');
    mkdirSync(directory, { recursive: true });
    const file = join(directory, 'history.sqlite'), database = new DatabaseSync(file);
    database.exec('CREATE TABLE observation_events(cursor INTEGER PRIMARY KEY,kind TEXT,data TEXT); CREATE TABLE attempts(id TEXT,invocation_id TEXT,operation_id TEXT,kind TEXT); CREATE TABLE operations(id TEXT,operation_key TEXT); CREATE TABLE captures(secret TEXT);');
    database.prepare('INSERT INTO operations VALUES (?,?)').run('private-operation', 'startup/build/private-invocation');
    database.exec('BEGIN');
    for (let index = 0; index < 130; index++) {
      database.prepare('INSERT INTO attempts VALUES (?,?,?,?)').run(`private-attempt-${index}`, 'private-invocation', 'private-operation', 'command');
      for (const kind of ['attempt.started','attempt.settled']) database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)').run(kind, JSON.stringify({ attemptId: `private-attempt-${index}`, at: '2026-11-04T03:00:00.000Z', argv: 'private-command', capture: 'private-capture' }));
    }
    database.exec('COMMIT'); database.close();
    const hash = () => createHash('sha256').update(readFileSync(file)).digest('hex'), before = hash();
    const script = `import { rememberFixturePath, telemetry } from ${JSON.stringify(new URL('./selector-timing.mjs', import.meta.url).href)}; import { fixtureAttemptTiming } from ${JSON.stringify(new URL('./selector-timing-attempts.mjs', import.meta.url).href)}; rememberFixturePath(${JSON.stringify(repository)}); const read = fixtureAttemptTiming(${JSON.stringify(repository)}); read(); read(); telemetry().mark('result', { invocationId: read.invocationId('private-invocation') });`;
    const env = { ...process.env, FACTORY_SELECTOR_TIMING_ROOT: root.path, FACTORY_SELECTOR_TIMING_TOKEN: root.token }; delete env.NODE_TEST_CONTEXT;
    const child = spawnSync(process.execPath, ['--input-type=module','-e',script], { env, encoding: 'utf8', timeout: 5000 });
    assert.equal(child.status, 0, child.stderr);
    const evidence = collectEvidence(root), attempts = evidence.records.filter(record => record.stage === 'attempt');
    assert.equal(evidence.status, 'complete');
    assert.equal(attempts.length, 260);
    assert.equal(new Set(attempts.map(record => record.attemptId)).size, 130);
    assert.equal(new Set(attempts.map(record => record.invocationId)).size, 1);
    assert.equal(evidence.records.find(record => record.stage === 'result').invocationId, attempts[0].invocationId);
    assert.ok(attempts.every(record => record.operationClass === 'startup/build'));
    assert.equal(JSON.stringify(evidence).includes('private-'), false);
    assert.equal(hash(), before);
  } finally { rmSync(root.path, { recursive: true, force: true }); rmSync(container, { recursive: true, force: true }); }
});

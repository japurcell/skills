import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { cpSync, lstatSync, mkdirSync, readFileSync, readdirSync, realpathSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';
import { createRepository } from './fixtures/repository.mjs';
import { initializeRepositoryStore, openCleanupReadStore } from '../dist/store.js';
import { analyzeCleanupReferences } from '../dist/cleanup-references.js';
const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
async function realExtraction(work, options = {}) {
  const fixture = createRepository(), root = realpathSync(fixture.path), common = join(root, '.git');
  try {
    mkdirSync(join(root, '.factory/workflows'), { recursive: true });
    for (const name of ['learn', 'evaluate', 'change']) cpSync(join(packageRoot, `templates/workflows/${name}.ts`), join(root, `.factory/workflows/${name}.ts`));
    writeFileSync(join(root, '.factory/package.json'), '{"type":"module"}');
    (await initializeRepositoryStore(common, { release: 'learning-graph-fixture' })).close();
    const toolchain = join(common, 'factory/toolchain'); mkdirSync(join(toolchain, 'node_modules/@types'), { recursive: true });
    mkdirSync(join(toolchain, 'node_modules/@typescript'), { recursive: true });
    for (const name of ['typescript', '@types/node', 'undici-types', `@typescript/typescript-${process.platform}-${process.arch}`]) cpSync(join(packageRoot, 'node_modules', name), join(toolchain, 'node_modules', name), { recursive: true });
    const nativeName = `@typescript/typescript-${process.platform}-${process.arch}`, nativeCopy = [];
    function verifyCopy(relative = '') {
      const src = join(packageRoot, 'node_modules', nativeName, relative), dst = join(toolchain, 'node_modules', nativeName, relative);
      const before = lstatSync(src), after = lstatSync(dst); assert.equal(before.isSymbolicLink(), false); assert.equal(after.isSymbolicLink(), false);
      assert.equal(after.mode & 0o777, before.mode & 0o777); assert.notDeepEqual([before.dev, before.ino], [after.dev, after.ino]);
      if (before.isDirectory()) for (const name of readdirSync(src).sort()) verifyCopy(join(relative, name));
      else { assert.equal(after.isFile(), true); const sha256 = hash(readFileSync(src)); assert.equal(hash(readFileSync(dst)), sha256);
        nativeCopy.push({ relative, sha256, mode: after.mode & 0o777, source: [before.dev, before.ino], copy: [after.dev, after.ino] }); }
    }
    verifyCopy(); console.log(JSON.stringify({ nativeFixtureCompiler: nativeName, nativeCopy }));
    writeFileSync(join(toolchain, 'manifest.json'), JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2', dependencies: { '@types/node': '24.19.2' } }));
    const { invoke } = await import('../dist/lifecycle.js');
    const { createFakeAdapter } = await import('../dist/adapters/fake.js');
    const { openCleanupReadStore, openRepositoryStore } = await import('../dist/store.js');
    const { analyzeCleanupReferences } = await import('../dist/cleanup-references.js');
    const input = join(common, 'inputs.json'), launchLog = join(common, 'launches.jsonl');
    const workflow = '.factory/workflows/learning-source.ts';
    const script = "process.stdout.write('baseline\\n'); process.stderr.write('candidate\\n')";
    const priorCommand = options.lineage ? `const prior = await context.command('prior-variants', { argv: [${JSON.stringify(process.execPath)}, '-e', ${JSON.stringify("process.stdout.write('prior retained\\n')")}], loopKey: 'learning-loop' });` : '';
    const lineageOptions = options.lineage ? `, intent: 'repeat', priorAttemptId: prior.attemptId, loopKey: 'learning-loop'` : '';
    writeFileSync(join(root, workflow), `export async function run(context) { ${priorCommand} await context.command('variants', { argv: [${JSON.stringify(process.execPath)}, '-e', ${JSON.stringify(script)}] ${lineageOptions} }); }\n`);
    writeFileSync(join(root, '.factory/agents.json'), JSON.stringify({ defaults: {
      harness: 'fake', permissions: 'read-only', skillDelivery: 'instructions', prompt: 'default', skills: [],
    } }));
    const learnPath = join(root, '.factory/workflows/learn.ts');
    writeFileSync(learnPath, readFileSync(learnPath, 'utf8').replace('export async function run(context: WorkflowContext, raw: Record<string, unknown>) {',
      `export async function run(context: WorkflowContext, raw: Record<string, unknown>) { await context.command('startup/learning-fixture-output', { argv: [${JSON.stringify(process.execPath)}, '-e', ${JSON.stringify("process.stdout.write('unreferenced learning setup 🌍\\n')")} ] });`));
    fixture.git(['add', '.factory']); fixture.git(['commit', '-m', 'Create real learning fixture']);
    async function launch(workflow, payload, scenario, shared = false) {
      writeFileSync(input, JSON.stringify(payload));
      const adapter = createFakeAdapter({ executable: process.execPath,
        script: join(packageRoot, 'test/fixtures/learning-evaluation-harness.mjs') });
      if (shared) adapter.eventChannel = 'stdout';
      const start = adapter.start;
      adapter.start = request => start({ ...request, context: JSON.stringify({ context: request.context, scenario, launchLog }) });
      const result = await invoke({ repository: root, workflow: `.factory/workflows/${workflow}.ts`, input,
        newWorktree: true, shutdownGraceMs: 100, adapters: { fake: adapter } });
      assert.equal(result.outcome, 'succeeded', JSON.stringify(result)); assert.equal(result.cleanup, 'complete');
      return result;
    }
    function facts() {
      const read = openCleanupReadStore(common);
      try {
        const snapshot = read.readCleanupSnapshot();
        const page = (method, domain) => {
          const rows = []; let after = '0';
          do { const value = read[method]({ after, through: snapshot.highWater[domain] });
            assert.equal(value.blocked, null); rows.push(...value.records); after = value.nextCursor;
            if (!value.hasMore) break;
          } while (true);
          assert.ok(rows.every(row => row.status === 'known')); return rows;
        };
        const headers = page('pageCleanupCaptureHeaders', 'captures'), attempts = page('pageCleanupAttemptFacts', 'attempts');
        const text = header => { let after = '0', result = '';
          do { const value = read.readCleanupCapture({ invocationId: header.invocationId, captureId: header.id, after });
            assert.equal(value.status, 'present'); assert.equal(value.blocked, null);
            result += value.chunks.map(chunk => chunk.text).join(''); after = value.nextSequence;
            if (!value.hasMore) return result;
          } while (true);
        };
        return { headers, attempts, payloads: new Map(headers.map(header => [header.id, text(header)])), graph: analyzeCleanupReferences(read) };
      } finally { read.close(); }
    }
    const source = await launch('learning-source', {}, null);
    let saved = facts();
    const variants = saved.attempts.find(row => row.invocationId === source.invocationId && row.operationKey === 'variants');
    const baseline = saved.headers.find(row => row.attemptId === variants.id && row.channel === 'stdout');
    const candidate = saved.headers.find(row => row.attemptId === variants.id && row.channel === 'stderr');
    assert.equal(saved.payloads.get(baseline.id), 'baseline\n'); assert.equal(saved.payloads.get(candidate.id), 'candidate\n');
    const eventReader = openRepositoryStore(common);
    let sourceEvent;
    try { sourceEvent = eventReader.readEvents({ after: '0', limit: 100 }).events.find(row => row.kind === 'attempt.started' && row.data.attemptId === variants.id); assert.ok(sourceEvent); }
    finally { eventReader.close(); }
    const extraction = await launch('learn', { version: 1, sources: [{ invocationId: source.invocationId, ...(options.lineage ? { attemptIds: [variants.id] } : {}), eventCursors: [sourceEvent.cursor] }] },
      { kind: 'extract', proposalKind: 'capture', target: { scope: 'repository', path: '.factory/prompts/check.md' } });
    saved = facts();
    const report = saved.headers.find(row => row.invocationId === extraction.invocationId && row.channel === 'report');
    const extracted = JSON.parse(saved.payloads.get(report.id));
    assert.deepEqual(extracted.examinedSources[0].eventCursors, [sourceEvent.cursor]);
    assert.ok(saved.graph.protected.some(node => node.kind === 'event' && node.cursor === sourceEvent.cursor));
    assert.equal(extracted.proposals[0].candidateCapture.captureId, candidate.id);
    const startup = saved.attempts.find(row => row.invocationId === extraction.invocationId && row.operationKey === 'startup/learning-fixture-output');
    const output = saved.headers.find(row => row.attemptId === startup.id && row.channel === 'stdout');
    assert.equal(saved.payloads.get(output.id), 'unreferenced learning setup 🌍\n');
    const selected = { invocationId: extraction.invocationId, captureId: output.id };
    const analyze = (bounds, adapt = read => read) => { const read = openCleanupReadStore(common); try { return analyzeCleanupReferences(adapt(read), bounds); } finally { read.close(); } };
    await work({ root, common, saved, source, sourceEvent, extraction, report, extracted, baseline, candidate, variants, analyze, facts, launch });
  } finally { fixture.dispose(); }
}
function editCapture(db, id, transform) {
  const rows = db.prepare('SELECT sequence,text FROM capture_chunks WHERE capture_id=? ORDER BY sequence').all(id);
  const original = db.prepare('SELECT sequence FROM captures WHERE id=?').get(id).sequence;
  const beforeHash = hash(rows.map(row => row.text).join(''));
  const source = JSON.stringify(transform(JSON.parse(rows.map(row => row.text).join(''))));
  const chunks = []; let text = '', bytes = 0;
  for (const point of source) { const size = Buffer.byteLength(point); if (bytes + size > 4096) { chunks.push(text); text = ''; bytes = 0; } text += point; bytes += size; }
  if (text) chunks.push(text);
  assert.equal(chunks.join(''), source); assert.equal(hash(chunks.join('')), hash(source));
  db.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(id);
  chunks.forEach((text, index) => db.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,?,?)').run(id, index + 1, text));
  db.prepare('UPDATE captures SET sequence=? WHERE id=?').run(chunks.length, id);
  return () => {
    db.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(id);
    for (const row of rows) db.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,?,?)').run(id, row.sequence, row.text);
    db.prepare('UPDATE captures SET sequence=? WHERE id=?').run(original, id);
    assert.deepEqual(db.prepare('SELECT sequence,text FROM capture_chunks WHERE capture_id=? ORDER BY sequence').all(id), rows);
    assert.equal(hash(rows.map(row => row.text).join('')), beforeHash);
    assert.equal(db.prepare('SELECT sequence FROM captures WHERE id=?').get(id).sequence, original);
  };
}
test('real extraction closure rejects changed format and provenance through the public graph interface', async t => realExtraction(async c => {
  assert.equal(c.saved.graph.status, 'complete', JSON.stringify(c.saved.graph.blockers));
  const db = new DatabaseSync(join(c.common, 'factory/history.sqlite'));
  try {
    for (const [name, transform, code] of [
      ['unknown report field', value => ({ ...value, extension: true }), 'opaque'],
      ['unknown declared version', value => ({ ...value, version: 2 }), 'opaque'],
      ['missing normalized ID', value => { delete value.proposalValidatedResultCaptureId; return value; }, 'ownership'],
      ['missing raw result ID', value => ({ ...value, proposalResultCaptureId: 'absent-result' }), 'missing'],
      ['proposal/report disagreement', value => { value.proposals[0].summary = 'different result'; return value; }, 'digest'],
      ['examined source disagreement', value => { value.examinedSources[0].captureIds.pop(); return value; }, 'digest'],
      ['unknown limitation kind', value => ({ ...value, captureLimitations: [{ invocationId: c.source.invocationId, kind: 'invented' }] }), 'opaque'],
    ]) await t.test(name, () => {
      const restore = editCapture(db, c.report.id, transform);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.equal(graph.snapshotSha256, null);
        assert.ok(graph.blockers.some(row => row.code === code), JSON.stringify(graph.blockers));
        assert.ok(graph.protected.some(row => row.kind === 'capture' && row.captureId === c.report.id));
      } finally { restore(); }
    });
    const producer = c.saved.attempts.find(row => row.operationKey === 'learn/extract');
    const supplied = JSON.parse(c.saved.payloads.get(producer.agent.inputsCaptureId));
    for (const [name, id, transform, code] of [
      ['foreign source input', producer.agent.inputsCaptureId, value => ({ ...value, sourceCaptureId: c.baseline.id }), 'foreign'],
      ['source input duplicated context differs', supplied.sourceCaptureId, value => ({ ...value, context: '{}' }), 'ownership'],
      ['effective inputs unknown field', producer.agent.inputsCaptureId, value => { value.inputs.extra = true; return value; }, 'opaque'],
      ['normalized payload differs', producer.agent.validatedResultCaptureId, value => { value.payload.proposals[0].key = 'different'; return value; }, 'digest'],
      ['empty-prefix input capture still has ownership', producer.agent.inputsCaptureId, value => { const context = JSON.parse(value.context); context.evidence[0].captures[0].id = 'missing-prefix-capture'; value.context = JSON.stringify(context); return value; }, 'ownership'],
    ]) await t.test(name, () => { const restore = editCapture(db, id, transform);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === code), JSON.stringify(graph.blockers)); }
      finally { restore(); }
    });
    for (const state of ['open', 'partial', 'unknown', 'pruned']) await t.test(`normalized ${state}`, () => {
      db.prepare('UPDATE captures SET state=? WHERE id=?').run(state, producer.agent.validatedResultCaptureId);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === (state === 'pruned' ? 'pruned' : 'partial'))); }
      finally { db.prepare("UPDATE captures SET state='complete' WHERE id=?").run(producer.agent.validatedResultCaptureId); }
    });
    await t.test('source bytes changed in-place fail exact retained prefix', () => {
      const before = db.prepare('SELECT text FROM capture_chunks WHERE capture_id=? AND sequence=1').get(c.candidate.id).text;
      db.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=1').run('changed candidate\n', c.candidate.id);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === 'digest')); }
      finally { db.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=1').run(before, c.candidate.id); }
    });
    await t.test('zero examined prefix still protects full newly measured bytes', () => {
      const zero = c.saved.headers.find(row => row.invocationId === c.source.invocationId && row.channel === 'stdout' && row.lastSequence === '0');
      assert.ok(zero); const before = c.analyze();
      db.prepare('INSERT INTO capture_chunks(capture_id,sequence,text) VALUES (?,1,?)').run(zero.id, 'new complete bytes 🌍\n');
      db.prepare('UPDATE captures SET sequence=1 WHERE id=?').run(zero.id);
      try { const after = c.analyze(); assert.equal(after.status, 'complete', JSON.stringify(after.blockers)); assert.notEqual(after.snapshotSha256, before.snapshotSha256);
        assert.ok(after.protected.some(row => row.kind === 'capture' && row.captureId === zero.id)); }
      finally { db.prepare('DELETE FROM capture_chunks WHERE capture_id=?').run(zero.id); db.prepare('UPDATE captures SET sequence=0 WHERE id=?').run(zero.id); }
    });
  } finally { db.close(); }
}));

test('real fake-adapter shared channel keeps exact raw result alias and all owned captures', async () => realExtraction(async c => {
  const ended = await c.launch('learn', { version: 1, sources: [{ invocationId: c.source.invocationId }] },
    { kind: 'extract', proposalKind: 'capture', target: { scope: 'repository', path: '.factory/prompts/check.md' } }, true);
  const retained = c.facts(), producer = retained.attempts.find(row => row.invocationId === ended.invocationId && row.operationKey === 'learn/extract');
  assert.equal(producer.agent.outputCaptureId, producer.agent.resultCaptureId);
  assert.equal(retained.headers.find(row => row.id === producer.agent.resultCaptureId).channel, 'result');
  assert.notEqual(producer.agent.inputsCaptureId, producer.agent.resultCaptureId);
  assert.notEqual(producer.agent.validatedResultCaptureId, producer.agent.resultCaptureId);
  assert.equal(retained.graph.status, 'complete', JSON.stringify(retained.graph.blockers));
  const protectedIds = new Set(retained.graph.protected.filter(row => row.kind === 'capture').map(row => row.captureId));
  for (const header of retained.headers.filter(row => row.attemptId === producer.id)) assert.ok(protectedIds.has(header.id));
}));

test('referenced prior command requires complete full bytes even outside examined captures', async t => realExtraction(async c => {
  assert.equal(c.saved.graph.status, 'complete');
  const prior = c.saved.attempts.find(row => row.operationKey === 'prior-variants');
  const output = c.saved.headers.find(row => row.attemptId === prior.id && row.channel === 'stdout');
  assert.equal(c.extracted.examinedSources[0].attemptIds.includes(prior.id), false);
  assert.equal(c.extracted.examinedSources[0].captureIds.includes(output.id), false);
  assert.ok(c.saved.graph.protected.some(row => row.kind === 'capture' && row.captureId === output.id));
  const db = new DatabaseSync(join(c.common, 'factory/history.sqlite'));
  try {
    await t.test('full prior bytes change the snapshot without a new high water', () => {
      const original = db.prepare('SELECT text FROM capture_chunks WHERE capture_id=? AND sequence=1').get(output.id).text;
      db.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=1').run('other retained\n', output.id);
      try { const changed = c.analyze(); assert.equal(changed.status, 'complete'); assert.deepEqual(changed.snapshot.highWater, c.saved.graph.snapshot.highWater);
        assert.notEqual(changed.snapshotSha256, c.saved.graph.snapshotSha256); }
      finally { db.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=1').run(original, output.id); }
    });
    await t.test('partial unexamined prior output blocks whole payload proof', () => {
      db.prepare("UPDATE captures SET state='partial' WHERE id=?").run(output.id);
      try { const changed = c.analyze(); assert.equal(changed.status, 'blocked'); assert.ok(changed.blockers.some(row => row.code === 'partial'));
        assert.ok(changed.protected.some(row => row.kind === 'capture' && row.captureId === output.id)); }
      finally { db.prepare("UPDATE captures SET state='complete' WHERE id=?").run(output.id); }
    });
  } finally { db.close(); }
}, { lineage: true }));
function evaluationInput(c, extraction = c.extraction) {
  return { version: 1, extraction: { invocationId: extraction.invocationId, proposalKey: 'improve' },
    baseline: { invocationId: c.source.invocationId, captureId: c.baseline.id, sha256: hash('baseline\n') },
    candidate: { invocationId: c.source.invocationId, captureId: c.candidate.id, sha256: hash('candidate\n') },
    cases: [{ key: 'candidate-check', criteria: 'candidate text', sourceSuggestion: 'candidate check',
      argv: [process.execPath, '-e', "process.exit(require('node:fs').readFileSync('.factory/prompts/check.md','utf8') === 'candidate\\n' ? 0 : 1)"], timeoutMs: 5000 }] };
}
test('real early evaluation scope and diff outcomes have complete references without target applicability', async t => realExtraction(async c => {
  const reports = [];
  for (const [scope, proposalKind, expectedKind] of [['shared', 'capture', 'unsupported_target_scope'], ['repository', 'diff', 'diff_only_candidate_requires_exact_materialization']]) {
    const extraction = await c.launch('learn', { version: 1, sources: [{ invocationId: c.source.invocationId }] },
      { kind: 'extract', proposalKind, target: { scope, path: '.factory/prompts/check.md' } });
    const evaluated = await c.launch('evaluate', evaluationInput(c, extraction), 'result');
    const retained = c.facts(), header = retained.headers.find(row => row.invocationId === evaluated.invocationId && row.channel === 'report');
    const value = JSON.parse(retained.payloads.get(header.id));
    assert.equal(value.assessment, 'inconclusive'); assert.deepEqual(value.cases, []); assert.equal(value.resolved, undefined);
    assert.equal(value.limitations[0].kind, expectedKind); assert.equal(retained.graph.status, 'complete', JSON.stringify(retained.graph.blockers));
    assert.equal(retained.attempts.filter(row => row.invocationId === evaluated.invocationId && row.kind === 'agent').length, 0);
    assert.ok(retained.graph.reports.some(row => row.key.captureId === header.id && row.format === 'evaluation-v1'));
    for (const id of [c.baseline.id, c.candidate.id]) assert.ok(retained.graph.protected.some(row => row.kind === 'capture' && row.captureId === id));
    reports.push({ header, value });
  }
  const db = new DatabaseSync(join(c.common, 'factory/history.sqlite'));
  try {
    for (const [name, transform] of [
      ['early unknown limitation reference', value => { value.limitations[0].reference = 'unrelated'; return value; }],
      ['early missing exact extraction digest', value => ({ ...value, extractionReport: null })],
      ['early missing result provenance', value => ({ ...value, extractionResult: null })],
      ['early wrong proposal selector does not guess latest', value => { value.suppliedReferences.extraction.proposalKey = 'absent'; return value; }],
      ['early malformed nested shape', value => { value.settings.review.extra = true; return value; }],
      ['early digest mismatch', value => { value.suppliedReferences.baseline.sha256 = '0'.repeat(64); return value; }],
    ]) await t.test(name, () => {
      const restore = editCapture(db, reports[0].header.id, transform);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.equal(graph.snapshotSha256, null);
        for (const id of [c.baseline.id, c.candidate.id]) assert.ok(graph.protected.some(row => row.kind === 'capture' && row.captureId === id)); }
      finally { restore(); }
    });
    await t.test('all global bounds still refuse complete learning histories', () => {
      for (const [field, value] of [['reports', 1], ['pages', 1], ['nodes', 1], ['edges', 1], ['sourceRows', 1], ['payloadBytes', 1], ['stateBytes', 1024]]) {
        const graph = c.analyze({ [field]: value }); assert.equal(graph.status, 'blocked'); assert.equal(graph.snapshotSha256, null);
        assert.ok(graph.blockers.some(row => row.code === 'limit' && row.limit === field), JSON.stringify(graph.blockers));
      }
    });
  } finally { db.close(); }
}));

test('real completed evaluation refuses changed objective reviewer and exact reference provenance', async t => realExtraction(async c => {
  const ended = await c.launch('evaluate', evaluationInput(c), 'result'), retained = c.facts();
  assert.equal(retained.graph.status, 'complete', JSON.stringify(retained.graph.blockers));
  const header = retained.headers.find(row => row.invocationId === ended.invocationId && row.channel === 'report');
  const report = JSON.parse(retained.payloads.get(header.id)); assert.equal(report.assessment, 'supported');
  const reviewer = retained.attempts.find(row => row.id === report.cases[0].candidate.review.attemptId);
  const objective = retained.attempts.find(row => row.id === report.cases[0].baseline.objective[0].attemptId);
  const objectiveInput = retained.headers.find(row => row.attemptId === objective.id && row.channel === 'context');
  const db = new DatabaseSync(join(c.common, 'factory/history.sqlite'));
  try {
    for (const [name, transform, code] of [
      ['unknown completed nested field', value => { value.cases[0].candidate.review.extra = true; return value; }, 'opaque'],
      ['foreign objective attempt', value => { value.cases[0].baseline.objective[0].attemptId = c.variants.id; return value; }, 'foreign'],
      ['objective success claim contradicts settled outcome', value => { value.cases[0].baseline.objective[0].exitCode = 0; return value; }, 'ownership'],
      ['review raw capture ID differs from actual metadata', value => { value.cases[0].candidate.review.resultCaptureId = c.candidate.id; return value; }, 'ownership'],
      ['review inputs unresolved', value => { value.cases[0].candidate.review.inputsCaptureId = null; return value; }, 'ownership'],
      ['unsupported assessment cannot retire a complete dependency', value => ({ ...value, assessment: 'unsupported' }), 'digest'],
      ['exact extraction report digest differs', value => { value.extractionReport.sha256 = '0'.repeat(64); return value; }, 'digest'],
      ['unknown completed limitation', value => ({ ...value, limitations: [{ kind: 'invented', reference: 'candidate-check' }] }), 'opaque'],
    ]) await t.test(name, () => { const restore = editCapture(db, header.id, transform);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === code), JSON.stringify(graph.blockers));
        assert.ok(graph.protected.some(row => row.kind === 'capture' && row.captureId === header.id)); }
      finally { restore(); }
    });
    for (const [name, id, transform, code] of [
      ['actual objective argv differs from report', objectiveInput.id, value => ({ ...value, argv: [process.execPath, '-e', 'process.exit(0)'] }), 'digest'],
      ['normalized reviewer judgment differs from report', reviewer.agent.validatedResultCaptureId, value => { value.payload.judgment = 'fail'; return value; }, 'digest'],
    ]) await t.test(name, () => { const restore = editCapture(db, id, transform);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === code), JSON.stringify(graph.blockers)); }
      finally { restore(); }
    });
    await t.test('reviewer context text hash must equal the complete selected source', () => {
      const supplied = JSON.parse(retained.payloads.get(reviewer.agent.inputsCaptureId));
      const context = JSON.parse(supplied.context); context.text = 'different candidate\n';
      const change = value => ({ ...value, context: JSON.stringify(context) });
      const first = editCapture(db, reviewer.agent.inputsCaptureId, change), second = editCapture(db, supplied.sourceCaptureId, change);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === 'digest')); }
      finally { second(); first(); }
    });
    await t.test('normalized result requires the actual invocation owner', () => {
      const row = db.prepare('SELECT data FROM attempts WHERE id=?').get(reviewer.id).data;
      const value = JSON.parse(row); value.agent.validatedResultCaptureId = c.baseline.id;
      db.prepare('UPDATE attempts SET data=? WHERE id=?').run(JSON.stringify(value), reviewer.id);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === 'foreign')); }
      finally { db.prepare('UPDATE attempts SET data=? WHERE id=?').run(row, reviewer.id); }
    });
    await t.test('same-length raw result changes bind exact bytes without new high water', () => {
      const rows = db.prepare('SELECT sequence,text FROM capture_chunks WHERE capture_id=? ORDER BY sequence').all(reviewer.agent.resultCaptureId);
      const before = c.analyze(); const changed = rows.map(row => ({ ...row, text: row.text.replace('Examined', 'Observed') }));
      assert.notEqual(changed.map(row => row.text).join(''), rows.map(row => row.text).join(''));
      for (const row of changed) db.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=?').run(row.text, reviewer.agent.resultCaptureId, row.sequence);
      try { const after = c.analyze(); assert.equal(after.status, 'complete', JSON.stringify(after.blockers)); assert.deepEqual(after.snapshot.highWater, before.snapshot.highWater); assert.notEqual(after.snapshotSha256, before.snapshotSha256); }
      finally { for (const row of rows) db.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=?').run(row.text, reviewer.agent.resultCaptureId, row.sequence); }
    });
    await t.test('referenced extraction event has finite typed semantics', () => {
      db.prepare('UPDATE observation_events SET kind=? WHERE cursor=?').run('unknown.reference-format', c.sourceEvent.cursor);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === 'opaque' && row.node?.kind === 'event')); }
      finally { db.prepare('UPDATE observation_events SET kind=? WHERE cursor=?').run(c.sourceEvent.kind, c.sourceEvent.cursor); }
    });
    await t.test('referenced event actual invocation owner wins', () => {
      const original = db.prepare('SELECT data FROM observation_events WHERE cursor=?').get(c.sourceEvent.cursor).data;
      db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(JSON.stringify({ ...JSON.parse(original), invocationId: c.extraction.invocationId }), c.sourceEvent.cursor);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === 'foreign' && row.node?.kind === 'event')); }
      finally { db.prepare('UPDATE observation_events SET data=? WHERE cursor=?').run(original, c.sourceEvent.cursor); }
    });
    await t.test('actual operation row cannot inherit an attempt copied key', () => {
      db.prepare('UPDATE operations SET operation_key=? WHERE id=?').run('unknown-learning-operation', reviewer.operationId);
      try { const graph = c.analyze(); assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === 'ownership' && row.node?.kind === 'operation')); }
      finally { db.prepare('UPDATE operations SET operation_key=? WHERE id=?').run(reviewer.operationKey, reviewer.operationId); }
    });
    await t.test('stalled referenced capture pages never imply complete evidence', () => {
      const graph = c.analyze({}, reader => ({ ...reader, readCleanupCapture(input) { const page = reader.readCleanupCapture(input);
        return input.captureId === c.candidate.id ? { ...page, chunks: [], nextSequence: input.after ?? '0', hasMore: true } : page; } }));
      assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === 'partial'));
    });
  } finally { db.close(); }
}));

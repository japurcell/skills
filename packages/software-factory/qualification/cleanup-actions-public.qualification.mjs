import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, existsSync, lstatSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, readlinkSync, realpathSync, rmSync, unlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { DatabaseSync } from 'node:sqlite';
import { createRepository } from '../test/fixtures/repository.mjs';

const packageRoot = resolve(fileURLToPath(new URL('../', import.meta.url)));
const launcher = resolve(packageRoot, '../../skills/default/software-factory/scripts/install.py');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const platform = `${process.platform}-${process.arch}`;
const node = {
  'darwin-arm64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-darwin-arm64.tar.xz', sha256: '654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628' },
  'linux-x64': { version: 'v24.22.1', url: 'https://nodejs.org/download/release/v24.22.1/node-v24.22.1-linux-x64.tar.xz', sha256: '6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6' },
}[platform];
function retainedRows(common) {
  const database = new DatabaseSync(join(common, 'factory/history.sqlite'), { readOnly: true });
  try {
    const result = {};
    for (const { name } of database.prepare("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").all()) {
      const statement = database.prepare(`SELECT * FROM "${name.replaceAll('"', '""')}" ORDER BY rowid`);
      statement.setReadBigInts(true); result[name] = statement.all();
    }
    return result;
  } finally { database.close(); }
}
function authoringFiles(root) {
  const result = {};
  const walk = (path, relative) => {
    const info = lstatSync(path);
    if (info.isSymbolicLink()) result[relative] = ['link', readlinkSync(path)];
    else if (info.isDirectory()) for (const name of readdirSync(path).sort()) walk(join(path, name), `${relative}/${name}`);
    else result[relative] = ['file', readFileSync(path)];
  };
  walk(join(root, '.factory'), '.factory'); return result;
}

export async function actionClosureFixture(t, { installed = true, probe } = {}) {
  let archive, seed;
  if (installed) {
    assert.ok(node, 'supported pinned Darwin arm64 or Linux x64 profile required');
    assert.equal(process.version, node.version);
    const python = process.env.FACTORY_TEST_PYTHON;
    assert.ok(python && existsSync(python));
    archive = realpathSync(process.env.FACTORY_TEST_NODE_ARCHIVE);
    seed = realpathSync(process.env.FACTORY_TEST_NPM_CACHE_SEED);
    assert.equal(hash(readFileSync(archive)), node.sha256);
  }
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-cleanup-advisory-')));
  const fixture = createRepository(), root = realpathSync(fixture.path), common = join(root, '.git');
  try {
    let upgraded;
    if (installed) {
    const python = process.env.FACTORY_TEST_PYTHON;
    const home = join(container, 'home'), cache = join(container, 'npm-cache');
    mkdirSync(home, { mode: 0o700 }); cpSync(seed, cache, { recursive: true });
    const userConfig = join(container, 'user.npmrc'), globalConfig = join(container, 'global.npmrc');
    writeFileSync(userConfig, '', { mode: 0o600 }); writeFileSync(globalConfig, '', { mode: 0o600 });
    const env = { PATH: process.env.PATH, HOME: home, TMPDIR: container, TMP: container, TEMP: container,
      NPM_CONFIG_USERCONFIG: userConfig, NPM_CONFIG_GLOBALCONFIG: globalConfig };
    const descriptor = join(container, 'selection.json');
    for (const [command, version] of [['install', '1.2.3'], ['upgrade', '1.2.4']]) {
      const bundle = join(container, `bundle-${version}`);
      writeFileSync(descriptor, JSON.stringify({ version, platform, node }));
      const packaged = spawnSync(process.execPath, [join(packageRoot, 'scripts/package-release.mjs'), '--descriptor', descriptor,
        '--source-root', packageRoot, '--destination', bundle], { encoding: 'utf8' });
      assert.equal(packaged.status, 0, packaged.stderr);
      const manifestSha256 = JSON.parse(packaged.stdout).manifestSha256;
      const result = spawnSync(python, [launcher, command, '--repository', root, '--bundle-root', bundle,
        '--manifest-sha256', manifestSha256, '--node-archive', archive, '--offline', '--offline-cache-seed', realpathSync(cache)],
      { env, encoding: 'utf8', timeout: 300_000, maxBuffer: 2 * 1024 * 1024 });
      assert.equal(result.status, 0, result.stderr);
      assert.equal(JSON.parse(result.stdout).state, 'ready');
      if (command === 'upgrade') upgraded = JSON.parse(result.stdout);
    }
    } else {
      const { initializeRepositoryStore } = await import('../dist/store.js');
      (await initializeRepositoryStore(common, { release: 'action-closure-fixture' })).close();
      const toolchain = join(common, 'factory/toolchain'); mkdirSync(join(toolchain, 'node_modules/@types'), { recursive: true });
      mkdirSync(join(toolchain, 'node_modules/@typescript'), { recursive: true });
      for (const name of ['typescript', '@types/node', 'undici-types', `@typescript/typescript-${process.platform}-${process.arch}`])
        cpSync(join(packageRoot, 'node_modules', name), join(toolchain, 'node_modules', name), { recursive: true });
      const native = `@typescript/typescript-${process.platform}-${process.arch}`;
      function verify(relative = '') {
        const source = join(packageRoot, 'node_modules', native, relative), copy = join(toolchain, 'node_modules', native, relative);
        const before = lstatSync(source), after = lstatSync(copy);
        assert.equal(before.isSymbolicLink(), false); assert.equal(after.isSymbolicLink(), false);
        assert.equal(after.mode & 0o777, before.mode & 0o777); assert.notDeepEqual([before.dev, before.ino], [after.dev, after.ino]);
        if (before.isDirectory()) for (const name of readdirSync(source).sort()) verify(join(relative, name));
        else assert.equal(hash(readFileSync(copy)), hash(readFileSync(source)));
      }
      verify();
      writeFileSync(join(toolchain, 'manifest.json'), JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2', dependencies: { '@types/node': '24.19.2' } }));
      mkdirSync(join(root, '.factory/workflows'), { recursive: true }); mkdirSync(join(root, '.factory/prompts'), { recursive: true });
      for (const name of ['learn', 'evaluate', 'change']) cpSync(join(packageRoot, `templates/workflows/${name}.ts`), join(root, `.factory/workflows/${name}.ts`));
      writeFileSync(join(root, '.factory/package.json'), '{"type":"module"}');
    }
    const { invoke } = await import('../dist/lifecycle.js');
    const { currentOwner } = await import('../dist/native/process.js');
    const { sourceHistoryGateway, prepareAdoption, confirmAdoption, prepareRevert, confirmRevert } = await import('../dist/learning.js');
    const { createFakeAdapter } = await import('../dist/adapters/fake.js');
    const { openCleanupReadStore, openRepositoryStore } = await import('../dist/store.js');
    const advisoryModule = await import('../dist/cleanup.js');
    let immutablePaths = [join(root, '.git/index'), join(root, 'tracked.txt'), join(root, 'untracked.txt'), join(root, 'ignored.txt')];
    if (installed) {
    const authorityReader = openCleanupReadStore(common);
    let backupId;
    try { const bound = authorityReader.readCleanupOperationEvidence({ operationId: upgraded.operationId }).backupBound;
      assert.equal(bound.status, 'known'); backupId = bound.data.backupId;
    } finally { authorityReader.close(); }
    const upgradePath = join(common, 'factory', `upgrade-${upgraded.operationId}`);
    const backupPath = join(common, 'factory/maintenance-backups', upgraded.operationId, backupId);
    immutablePaths = [join(root, '.git/index'), join(root, 'tracked.txt'), join(root, 'untracked.txt'), join(root, 'ignored.txt'),
      ...['new-receipt.json', 'intent.json', 'original.json'].map(name => join(upgradePath, name)),
      ...['backup-receipt.json', 'backup-request.json', 'history.sqlite'].map(name => join(backupPath, name))];
    }
    const advisory = { async inspectCleanupSelection(...args) {
      const rows = retainedRows(common), authoring = authoringFiles(root), bytes = immutablePaths.map(path => [path, readFileSync(path)]);
      const result = await advisoryModule.inspectCleanupSelection(...args);
      assert.deepEqual(retainedRows(common), rows); assert.deepEqual(authoringFiles(root), authoring);
      for (const [path, value] of bytes) assert.deepEqual(readFileSync(path), value);
      return result;
    } };
    const { analyzeCleanupReferences } = await import('../dist/cleanup-references.js');
    const input = join(container, 'inputs.json'), launchLog = join(container, 'launches.jsonl');
    const workflow = '.factory/workflows/learning-source.ts';
    const script = "process.stdout.write('baseline\\n'); process.stderr.write('candidate\\n')";
    writeFileSync(join(root, workflow), `export async function run(context) {
      const prior = await context.command('prior-variants', { argv: [${JSON.stringify(process.execPath)}, '-e', ${JSON.stringify("process.stdout.write('prior retained')")}], loopKey: 'action-source-loop' });
      await context.command('variants', { argv: [${JSON.stringify(process.execPath)}, '-e', ${JSON.stringify(script)}], intent: 'repeat', priorAttemptId: prior.attemptId, loopKey: 'action-source-loop' });
    }\n`);
    writeFileSync(join(root, '.factory/agents.json'), JSON.stringify({ defaults: {
      harness: 'fake', permissions: 'read-only', skillDelivery: 'instructions', prompt: 'default', skills: [],
    } }));
    const learnPath = join(root, '.factory/workflows/learn.ts');
    writeFileSync(learnPath, readFileSync(learnPath, 'utf8').replace('export async function run(context: WorkflowContext, raw: Record<string, unknown>) {',
      `export async function run(context: WorkflowContext, raw: Record<string, unknown>) { await context.command('startup/learning-fixture-output', { argv: [${JSON.stringify(process.execPath)}, '-e', ${JSON.stringify("process.stdout.write('unreferenced learning setup 🌍\\n')")} ] });`));
    writeFileSync(join(root, '.factory/prompts/check.md'), 'baseline\n');
    fixture.git(['add', '.factory']); fixture.git(['commit', '-m', 'Create real learning fixture']);
    async function launch(workflow, payload, scenario) {
      writeFileSync(input, JSON.stringify(payload));
      const adapter = createFakeAdapter({ executable: process.execPath,
        script: join(packageRoot, 'test/fixtures/learning-evaluation-harness.mjs') });
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
    async function record(name, value, eventTexts = []) {
      const recorder = openRepositoryStore(common);
      try {
        const run = await recorder.createRun();
        const worktree = await recorder.registerWorktree({ path: root, registration: 'action-fixture' });
        const invocation = await recorder.startInvocation({ runId: run.id, worktreeId: worktree.id, owner: currentOwner() });
        const input = await recorder.createCapture({ invocationId: invocation.id, channel: 'context' });
        await recorder.appendCapture({ id: input.id, chunks: [{ sequence: 1, text: '{"inputs":{},"question":null,"contexts":[]}' }], state: 'complete' });
        await recorder.saveInvocationMetadata(invocation.id, { settings: {}, workflow: `.factory/workflows/${name}.ts`, selectedCommit: null,
          inputCaptureId: input.id, question: null, contexts: [] });
        await recorder.activateInvocation(invocation.id);
        const captures = [];
        for (const text of eventTexts) {
          const capture = await recorder.createCapture({ invocationId: invocation.id, channel: 'event' });
          await recorder.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text }], state: 'complete' }); captures.push(capture);
        }
        let reference;
        if (value !== undefined) {
          const capture = await recorder.createCapture({ invocationId: invocation.id, channel: 'report' });
          const text = JSON.stringify(value);
          await recorder.appendCapture({ id: capture.id, chunks: [{ sequence: 1, text }], state: 'complete' });
          reference = { invocationId: invocation.id, captureId: capture.id, sha256: hash(text) };
        }
        await recorder.stopAdmissions(invocation.id);
        await recorder.finalizeInvocation({ id: invocation.id, outcome: 'succeeded', cleanup: 'complete', claimId: invocation.claim.id, token: invocation.claim.token });
        return { invocationId: invocation.id, captures, reference };
      } finally { recorder.close(); }
    }
    const emitted = await launch('learning-source', {}, null), emittedFacts = facts();
    const emittedVariant = emittedFacts.attempts.find(row => row.invocationId === emitted.invocationId && row.operationKey === 'variants');
    assert.ok(emittedVariant.priorAttemptId);
    const emittedBaseline = emittedFacts.headers.find(row => row.attemptId === emittedVariant.id && row.channel === 'stdout');
    const emittedCandidate = emittedFacts.headers.find(row => row.attemptId === emittedVariant.id && row.channel === 'stderr');
    const baselineBytes = emittedFacts.payloads.get(emittedBaseline.id), candidateBytes = emittedFacts.payloads.get(emittedCandidate.id);
    assert.equal(baselineBytes, 'baseline\n'); assert.equal(candidateBytes, 'candidate\n');
    // Event evidence contains exact bytes read from the actual finalized command producer above.
    const source = await record('action-source', undefined, [baselineBytes, candidateBytes]);
    let saved = facts();
    const [baseline, candidate] = source.captures;
    const eventReader = openRepositoryStore(common);
    let sourceEvent;
    try {
      let after = '0';
      do {
        const page = eventReader.readEvents({ after, limit: 100 });
        sourceEvent = page.events.find(row => row.kind === 'capture.created' && row.data.captureId === baseline.id);
        if (sourceEvent || page.events.length === 0) break;
        assert.ok(BigInt(page.nextCursor) > BigInt(after)); after = page.nextCursor;
      } while (true);
      assert.ok(sourceEvent);
    }
    finally { eventReader.close(); }
    const extraction = await launch('learn', { version: 1, sources: [{ invocationId: source.invocationId, eventCursors: [sourceEvent.cursor] }, { invocationId: emitted.invocationId, attemptIds: [emittedVariant.id] }] },
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
    const beforeRows = retainedRows(common), beforeAuthoring = authoringFiles(root);
    if (installed) {
      const result = await advisory.inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
      assert.equal(result.status, 'inspectable', JSON.stringify(result.blockers)); assert.equal(result.captures[0].disposition, 'eligible');
      assert.equal(result.captures[0].payloadSha256, hash(saved.payloads.get(output.id)));
    }
    assert.deepEqual(retainedRows(common), beforeRows); assert.deepEqual(authoringFiles(root), beforeAuthoring);
    assert.equal(saved.graph.status, 'complete', JSON.stringify(saved.graph.blockers));
    assert.deepEqual(saved.graph.reports, [{ key: { invocationId: extraction.invocationId, captureId: report.id }, format: 'extraction-v1', sha256: hash(saved.payloads.get(report.id)) }]);
    const keys = new Set(saved.graph.protected.filter(row => row.kind === 'capture').map(row => row.captureId));
    for (const header of saved.headers.filter(row => row.invocationId === source.invocationId || row.invocationId === extraction.invocationId &&
      (row.channel === 'report' || row.channel === 'context' || row.attemptId === saved.attempts.find(row => row.operationKey === 'learn/extract').id)))
      assert.ok(keys.has(header.id), `missing exact extraction capture ${header.id}`);
    await t.test('inconclusive and revised supported evaluations both retain every exact dependency', async child => {
      const evaluationInput = { version: 1, extraction: { invocationId: extraction.invocationId, proposalKey: 'improve' },
        baseline: { invocationId: source.invocationId, captureId: baseline.id, sha256: hash('baseline\n') },
        candidate: { invocationId: source.invocationId, captureId: candidate.id, sha256: hash('candidate\n') },
        cases: [{ key: 'candidate-check', criteria: 'candidate text', sourceSuggestion: 'candidate check',
          argv: [process.execPath, '-e', "process.exit(require('node:fs').readFileSync('.factory/prompts/check.md','utf8') === 'candidate\\n' ? 0 : 1)"], timeoutMs: 5000 }] };
      const inconclusive = await launch('evaluate', evaluationInput, 'uncertain');
      const supported = await launch('evaluate', evaluationInput, 'result');
      const opposite = structuredClone(evaluationInput);
      opposite.cases[0].argv = [process.execPath, '-e', "process.exit(require('node:fs').readFileSync('.factory/prompts/check.md','utf8') === 'baseline\\n' ? 0 : 1)"];
      const unsupported = await launch('evaluate', opposite, 'reverse');
      const retained = facts();
      const firstReport = retained.headers.find(row => row.invocationId === inconclusive.invocationId && row.channel === 'report');
      const secondReport = retained.headers.find(row => row.invocationId === supported.invocationId && row.channel === 'report');
      const thirdReport = retained.headers.find(row => row.invocationId === unsupported.invocationId && row.channel === 'report');
      const third = JSON.parse(retained.payloads.get(thirdReport.id)); assert.equal(third.assessment, 'unsupported');
      const first = JSON.parse(retained.payloads.get(firstReport.id)), second = JSON.parse(retained.payloads.get(secondReport.id));
      assert.equal(first.assessment, 'inconclusive'); assert.equal(second.assessment, 'supported');
      const beforeRows = retainedRows(common), beforeAuthoring = authoringFiles(root);
      if (installed) {
        const result = await advisory.inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
        assert.equal(result.status, 'inspectable', JSON.stringify(result.blockers)); assert.equal(result.captures[0].disposition, 'eligible');
      }
      assert.deepEqual(retainedRows(common), beforeRows); assert.deepEqual(authoringFiles(root), beforeAuthoring);
      assert.equal(retained.graph.status, 'complete', JSON.stringify(retained.graph.blockers));
      const reportIds = retained.graph.reports.map(row => row.key.captureId).sort();
      assert.deepEqual(reportIds, [report.id, firstReport.id, secondReport.id, thirdReport.id].sort());
      const protectedIds = new Set(retained.graph.protected.filter(row => row.kind === 'capture').map(row => row.captureId));
      for (const [owner, value] of [[inconclusive, first], [supported, second], [unsupported, third]]) {
        assert.ok(protectedIds.has(retained.headers.find(row => row.invocationId === owner.invocationId && row.channel === 'report').id));
        for (const caseResult of value.cases) for (const variant of ['baseline', 'candidate']) {
          const side = caseResult[variant];
          for (const objective of side.objective) {
            const actual = retained.attempts.find(row => row.id === objective.attemptId);
            assert.equal(actual.operationKey.startsWith(`evaluate/candidate-check/${variant}/objective/`), true);
            for (const header of retained.headers.filter(row => row.attemptId === objective.attemptId)) assert.ok(protectedIds.has(header.id), `objective capture ${header.id}`);
          }
          const reviewer = retained.attempts.find(row => row.id === side.review.attemptId);
          assert.equal(reviewer.operationKey, `evaluate/candidate-check/${variant}/review`);
          for (const header of retained.headers.filter(row => row.attemptId === reviewer.id)) assert.ok(protectedIds.has(header.id), `review capture ${header.id}`);
          const supplied = JSON.parse(retained.payloads.get(reviewer.agent.inputsCaptureId));
          assert.ok(protectedIds.has(supplied.sourceCaptureId), `source input ${supplied.sourceCaptureId}`);
        }
      }
      const historyStore = openRepositoryStore(common);
      try {
        const history = sourceHistoryGateway(historyStore, action => action());
        const target = '.factory/prompts/check.md';
        const expectedRevision = fixture.git(['rev-parse', 'HEAD']).trim();
        const approval = { reference: 'human:approval-label', extraction: evaluationInput.extraction,
          evaluation: { invocationId: supported.invocationId, reportCaptureId: secondReport.id, sha256: hash(retained.payloads.get(secondReport.id)) },
          candidate: evaluationInput.candidate, target: { repository: root, scope: 'repository', path: target,
            expectedRevision, expectedSha256: hash('baseline\n') } };
        const actionReports = [];
        const retain = async (name, value) => { const saved = await record(name, value); actionReports.push({ reference: saved.reference, value }); return saved.reference; };
        const preparation = await prepareAdoption(history, approval);
        const preparedRef = await retain('custom-preparation-name', preparation);
        const notApplied = await confirmAdoption(history, preparedRef, { reference: 'human:failed-action', status: 'failed' });
        assert.equal(notApplied.status, 'not_applied'); await retain('not-applied', notApplied);
        writeFileSync(join(root, target), 'unexpected\n'); fixture.git(['add', target]); fixture.git(['commit', '-m', 'Unexpected fixture target']);
        const uncertain = await confirmAdoption(history, preparedRef, { reference: 'human:uncertain-action', status: 'uncertain' });
        assert.equal(uncertain.status, 'uncertain'); await retain('uncertain-adoption', uncertain);
        fixture.git(['reset', '--hard', expectedRevision]);
        assert.deepEqual(await prepareAdoption(history, approval), preparation);
        writeFileSync(join(root, target), 'candidate\n'); fixture.git(['add', target]); fixture.git(['commit', '-m', 'Apply fixture candidate']);
        const applied = await confirmAdoption(history, preparedRef, { reference: 'human:apply-action', status: 'succeeded' });
        assert.equal(applied.status, 'applied'); const appliedRef = await retain('applied', applied);
        const revertPreparation = await prepareRevert(history, appliedRef, { reference: 'human:revert-approval' });
        const revertRef = await retain('revert-preparation', revertPreparation);
        const notReverted = await confirmRevert(history, revertRef, { reference: 'human:failed-revert', status: 'failed' });
        assert.equal(notReverted.status, 'not_reverted'); await retain('not-reverted', notReverted);
        const adoptedRevision = fixture.git(['rev-parse', 'HEAD']).trim();
        writeFileSync(join(root, target), 'unexpected\n'); fixture.git(['add', target]); fixture.git(['commit', '-m', 'Unexpected fixture revert']);
        const uncertainRevert = await confirmRevert(history, revertRef, { reference: 'human:uncertain-revert', status: 'uncertain' });
        assert.equal(uncertainRevert.status, 'uncertain'); await retain('uncertain-revert', uncertainRevert);
        fixture.git(['reset', '--hard', adoptedRevision]);
        assert.deepEqual(await prepareRevert(history, appliedRef, { reference: 'human:revert-approval' }), revertPreparation);
        writeFileSync(join(root, target), 'baseline\n'); fixture.git(['add', target]); fixture.git(['commit', '-m', 'Revert fixture candidate']);
        const reverted = await confirmRevert(history, revertRef, { reference: 'human:revert-action', status: 'succeeded' });
        assert.equal(reverted.status, 'reverted'); await retain('reverted', reverted);
        const closure = facts();
        if (installed) {
          const impact = await advisory.inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
          assert.equal(impact.status, 'inspectable', JSON.stringify(impact.blockers));
          assert.equal(impact.captures[0].disposition, 'eligible'); assert.equal(impact.captures[0].payloadSha256, hash('unreferenced learning setup 🌍\n'));
        }
        assert.equal(closure.graph.status, 'complete', JSON.stringify(closure.graph.blockers));
        const protectedCaptures = new Set(closure.graph.protected.filter(node => node.kind === 'capture').map(node => node.captureId));
        const actionOwners = new Set(actionReports.map(report => report.reference.invocationId));
        const expectedProtected = new Set(retained.graph.protected.filter(node => node.kind === 'capture').map(node => node.captureId));
        for (const header of closure.headers.filter(header => actionOwners.has(header.invocationId))) expectedProtected.add(header.id);
        for (const id of expectedProtected) assert.ok(protectedCaptures.has(id), `action closure capture ${id}`);
        const expectedReports = [report.id, firstReport.id, secondReport.id, thirdReport.id, ...actionReports.map(row => row.reference.captureId)].sort();
        assert.deepEqual(closure.graph.reports.map(row => row.key.captureId).sort(), expectedReports);
        const hasEdge = (from, to, kind) => closure.graph.edges.some(edge => edge.kind === kind && edge.from.kind === 'capture' && edge.from.captureId === from && edge.to.kind === 'capture' && edge.to.captureId === to);
        assert.ok(hasEdge(preparedRef.captureId, secondReport.id, 'review'));
        assert.ok(hasEdge(preparedRef.captureId, report.id, 'extraction-report'));
        assert.ok(hasEdge(preparedRef.captureId, candidate.id, 'candidate'));
        assert.ok(hasEdge(revertRef.captureId, appliedRef.captureId, 'original-adoption'));
        for (const { reference, value } of actionReports) {
          if (value.preparationReference) assert.ok(hasEdge(reference.captureId, value.preparationReference.captureId, 'preparation'));

          const format = value.kind === 'adoption-preparation' ? 'adoption-preparation-compat1' : value.kind === 'adoption' ? 'adoption-compat1'
            : value.kind === 'revert-preparation' ? 'revert-preparation-compat1' : 'revert-compat1';
          assert.ok(closure.graph.reports.some(report => report.key.captureId === reference.captureId && report.format === format && report.sha256 === reference.sha256));
        }
        if (probe) await probe(child, { root, common, facts, actionReports, selected, closure, immutablePaths,
          inspect: installed ? () => advisory.inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] }) : null });
        for (const header of closure.headers.filter(header => header.attemptId === emittedVariant.priorAttemptId))
          assert.ok(protectedCaptures.has(header.id), `actual prior source capture ${header.id}`);
        // Public library revalidation is deliberately outside cleanup analysis.
        assert.equal((await confirmRevert(history, revertRef, { reference: 'human:retained-revalidation', status: 'succeeded' })).status, 'reverted');
      } finally { historyStore.close(); }
    });
  } finally { fixture.dispose(); rmSync(container, { recursive: true, force: true }); }
}

export async function actionClosureTampering(t, c) {
  const { openCleanupReadStore } = await import('../dist/store.js');
  const { analyzeCleanupReferences } = await import('../dist/cleanup-references.js');
  const db = new DatabaseSync(join(c.common, 'factory/history.sqlite'));
  const report = (kind, status) => c.actionReports.find(row => row.value.kind === kind && (status === undefined || row.value.status === status));
  const prep = report('adoption-preparation'), applied = report('adoption', 'applied'), notApplied = report('adoption', 'not_applied');
  const uncertain = report('adoption', 'uncertain'), revertPrep = report('revert-preparation'), reverted = report('revert', 'reverted');
  function analyze(bounds = {}, adapt = reader => reader) {
    const rows = retainedRows(c.common), files = authoringFiles(c.root), bytes = c.immutablePaths.map(path => [path, readFileSync(path)]);
    const reader = openCleanupReadStore(c.common);
    let graph;
    try { graph = analyzeCleanupReferences(adapt(reader), bounds); } finally { reader.close(); }
    assert.deepEqual(retainedRows(c.common), rows); assert.deepEqual(authoringFiles(c.root), files);
    for (const [path, value] of bytes) assert.deepEqual(readFileSync(path), value);
    return graph;
  }
  function edit(id, transform) {
    const rows = db.prepare('SELECT sequence,text FROM capture_chunks WHERE capture_id=? ORDER BY sequence').all(id);
    const original = db.prepare('SELECT sequence FROM captures WHERE id=?').get(id).sequence;
    const beforeHash = hash(rows.map(row => row.text).join(''));
    const source = JSON.stringify(transform(JSON.parse(rows.map(row => row.text).join(''))));
    const chunks = []; let text = '', bytes = 0;
    for (const point of source) { const size = Buffer.byteLength(point); if (bytes + size > 4096) { chunks.push(text); text = ''; bytes = 0; } text += point; bytes += size; }
    if (text) chunks.push(text);
    assert.equal(chunks.join(''), source);
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
  async function blocked(code) {
    const graph = analyze(); assert.equal(graph.status, 'blocked'); assert.equal(graph.snapshotSha256, null);
    assert.ok(graph.blockers.some(row => row.code === code), JSON.stringify(graph.blockers));
    for (const { reference } of c.actionReports) assert.ok(graph.protected.some(node => node.kind === 'capture' && node.captureId === reference.captureId));
    if (c.inspect) { const impact = await c.inspect(); assert.equal(impact.status, 'blocked'); assert.equal(impact.impactSha256, null);
      assert.equal(impact.captures[0].disposition, 'refused'); }
  }
  try {
    // These are explicitly corrupted fixture records, never claimed as library-produced positive output.
    for (const [name, parent, transform, code] of [
      ['unknown top-level field', prep, value => ({ ...value, version: 1 }), 'opaque'],
      ['unknown approval field', prep, value => { value.approval.extra = true; return value; }, 'opaque'],
      ['unknown nested action field', applied, value => { value.action.captureId = value.action.reference; return value; }, 'opaque'],
      ['unknown embedded original field', reverted, value => { value.originalAdoption.extension = true; return value; }, 'opaque'],
      ['preparation expected observation disagreement', prep, value => { value.expected.sha256 = '0'.repeat(64); return value; }, 'digest'],
      ['evaluation digest mismatch', prep, value => { value.approval.evaluation.sha256 = '0'.repeat(64); return value; }, 'digest'],
      ['foreign evaluation invocation', prep, value => { value.approval.evaluation.invocationId = value.approval.extraction.invocationId; return value; }, 'foreign'],
      ['missing evaluation report', prep, value => { value.approval.evaluation.reportCaptureId = 'absent-evaluation'; return value; }, 'missing'],
      ['extraction evidence disagreement', prep, value => { value.evidence.extractionResult.rawCaptureId = 'absent-raw-result'; return value; }, 'digest'],
      ['candidate reference disagreement', prep, value => { value.approval.candidate.sha256 = '0'.repeat(64); return value; }, 'digest'],
      ['missing preparation', applied, value => { value.preparationReference.captureId = 'absent-preparation'; return value; }, 'missing'],
      ['foreign preparation', applied, value => { value.preparationReference.invocationId = value.approval.extraction.invocationId; return value; }, 'foreign'],
      ['preparation digest mismatch', applied, value => { value.preparationReference.sha256 = '0'.repeat(64); return value; }, 'digest'],
      ['wrong preparation kind', applied, value => { value.preparationReference = revertPrep.reference; return value; }, 'ownership'],
      ['duplicated approval disagreement', applied, value => { value.approval.reference = 'different-human-label'; return value; }, 'digest'],
      ['applied requires successful action', applied, value => { value.action.status = 'failed'; return value; }, 'digest'],
      ['applied hash must equal candidate', applied, value => { value.applied.sha256 = value.approval.target.expectedSha256; return value; }, 'digest'],
      ['applied requires changed revision', applied, value => { value.applied.revision = value.approval.target.expectedRevision; return value; }, 'digest'],
      ['not-applied observed target must remain expected', notApplied, value => { value.observed.sha256 = value.approval.candidate.sha256; return value; }, 'digest'],
      ['uncertain observation reason must agree', uncertain, value => { value.observed = null; return value; }, 'digest'],
      ['original adoption digest mismatch', revertPrep, value => { value.originalAdoptionReference.sha256 = '0'.repeat(64); return value; }, 'digest'],
      ['missing original adoption', revertPrep, value => { value.originalAdoptionReference.captureId = 'absent-adoption'; return value; }, 'missing'],
      ['embedded original adoption disagreement', revertPrep, value => { value.originalAdoption.action.reference = 'different-label'; return value; }, 'digest'],
      ['revert expected observation disagreement', revertPrep, value => { value.expected.sha256 = '0'.repeat(64); return value; }, 'digest'],
      ['revert approval label disagreement', reverted, value => { value.approvalReference = 'different-label'; return value; }, 'digest'],
      ['reverted requires successful action', reverted, value => { value.action.status = 'uncertain'; return value; }, 'digest'],
      ['reverted hash must equal original target', reverted, value => { value.reverted.sha256 = value.originalAdoption.approval.candidate.sha256; return value; }, 'digest'],
      ['action status requires a primitive string', notApplied, value => { value.action.status = ['failed']; return value; }, 'opaque'],
      ['unknown action status', reverted, value => { value.action.status = 'done'; return value; }, 'opaque'],
      ['human labels use UTF-8 byte limit', prep, value => { value.approval.reference = '🌍'.repeat(65); return value; }, 'opaque'],
      ['embedded action object cap', prep, value => ({ ...value, untrusted: Array.from({ length: 65 }, () => ({})) }), 'limit'],
      ['oversized action report', prep, value => ({ ...value, untrusted: '🌍'.repeat(32769) }), 'limit'],
      ['self-reference keeps discovered cycle', applied, value => { value.preparationReference = applied.reference; return value; }, 'cycle'],
    ]) await t.test(name, async () => {
      const restore = edit(parent.reference.captureId, transform);
      try { await blocked(code); } finally { restore(); }
    });
    for (const state of ['open', 'partial', 'unknown', 'pruned']) await t.test(`retained action preparation ${state}`, async () => {
      const id = prep.reference.captureId;
      db.prepare('UPDATE captures SET state=? WHERE id=?').run(state, id);
      try { await blocked(state === 'pruned' ? 'pruned' : 'partial'); }
      finally { db.prepare("UPDATE captures SET state='complete' WHERE id=?").run(id); }
    });
    await t.test('stalled action payload paging blocks without writes', () => {
      const graph = analyze({}, reader => ({ ...reader, readCleanupCapture(input) {
        const page = reader.readCleanupCapture(input);
        return input.captureId === prep.reference.captureId ? { ...page, chunks: [], nextSequence: input.after ?? '0', hasMore: true } : page;
      } }));
      assert.equal(graph.status, 'blocked'); assert.ok(graph.blockers.some(row => row.code === 'partial'));
    });
    await t.test('target files and human labels remain inert during analysis', () => {
      const path = join(c.root, '.factory/prompts/check.md'), bytes = readFileSync(path), before = analyze();
      unlinkSync(path);
      try {
        const after = analyze(); assert.equal(after.status, 'complete', JSON.stringify(after.blockers)); assert.equal(after.snapshotSha256, before.snapshotSha256);
        for (const row of c.actionReports) {
          const label = row.value.action?.reference;
          if (label) assert.ok(!after.protected.some(node => node.kind === 'capture' && node.captureId === label));
        }
      } finally { writeFileSync(path, bytes); }
    });
    assert.equal(analyze().status, 'complete');
  } finally { db.close(); }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) test('genuine retained library actions preserve closure and leave unrelated setup output eligible after install and upgrade', t => actionClosureFixture(t, { probe: actionClosureTampering }));

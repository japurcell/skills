import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash, randomUUID } from 'node:crypto';
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

test('exact extraction closure permits only unrelated ended startup output after genuine install and upgrade', async t => {
  assert.ok(node, 'supported pinned Darwin arm64 or Linux x64 profile required');
  assert.equal(process.version, node.version);
  const python = process.env.FACTORY_TEST_PYTHON;
  assert.ok(python && existsSync(python));
  const archive = realpathSync(process.env.FACTORY_TEST_NODE_ARCHIVE);
  const seed = realpathSync(process.env.FACTORY_TEST_NPM_CACHE_SEED);
  assert.equal(hash(readFileSync(archive)), node.sha256);
  const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-cleanup-advisory-')));
  const fixture = createRepository(), root = realpathSync(fixture.path), common = join(root, '.git');
  try {
    const home = join(container, 'home'), cache = join(container, 'npm-cache');
    mkdirSync(home, { mode: 0o700 }); cpSync(seed, cache, { recursive: true });
    const userConfig = join(container, 'user.npmrc'), globalConfig = join(container, 'global.npmrc');
    writeFileSync(userConfig, '', { mode: 0o600 }); writeFileSync(globalConfig, '', { mode: 0o600 });
    const env = { PATH: process.env.PATH, HOME: home, TMPDIR: container, TMP: container, TEMP: container,
      NPM_CONFIG_USERCONFIG: userConfig, NPM_CONFIG_GLOBALCONFIG: globalConfig };
    const descriptor = join(container, 'selection.json');
    let upgraded;
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
    const { invoke } = await import('../dist/lifecycle.js');
    const { createFakeAdapter } = await import('../dist/adapters/fake.js');
    const { openCleanupReadStore, openRepositoryStore } = await import('../dist/store.js');
    const advisoryModule = await import('../dist/cleanup.js');
    const authorityReader = openCleanupReadStore(common);
    let backupId;
    try { const bound = authorityReader.readCleanupOperationEvidence({ operationId: upgraded.operationId }).backupBound;
      assert.equal(bound.status, 'known'); backupId = bound.data.backupId;
    } finally { authorityReader.close(); }
    const upgradePath = join(common, 'factory', `upgrade-${upgraded.operationId}`);
    const backupPath = join(common, 'factory/maintenance-backups', upgraded.operationId, backupId);
    const immutablePaths = [join(root, '.git/index'), join(root, 'tracked.txt'), join(root, 'untracked.txt'), join(root, 'ignored.txt'),
      ...['new-receipt.json', 'intent.json', 'original.json'].map(name => join(upgradePath, name)),
      ...['backup-receipt.json', 'backup-request.json', 'history.sqlite'].map(name => join(backupPath, name))];
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
    writeFileSync(join(root, workflow), `export async function run(context) { await context.command('variants', { argv: [${JSON.stringify(process.execPath)}, '-e', ${JSON.stringify(script)}] }); }\n`);
    writeFileSync(join(root, '.factory/agents.json'), JSON.stringify({ defaults: {
      harness: 'fake', permissions: 'read-only', skillDelivery: 'instructions', prompt: 'default', skills: [],
    } }));
    const learnPath = join(root, '.factory/workflows/learn.ts');
    writeFileSync(learnPath, readFileSync(learnPath, 'utf8').replace('export async function run(context: WorkflowContext, raw: Record<string, unknown>) {',
      `export async function run(context: WorkflowContext, raw: Record<string, unknown>) { await context.command('startup/learning-fixture-output', { argv: [${JSON.stringify(process.execPath)}, '-e', ${JSON.stringify("process.stdout.write('unreferenced learning setup 🌍\\n')")} ] });`));
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
    const extraction = await launch('learn', { version: 1, sources: [{ invocationId: source.invocationId, eventCursors: [sourceEvent.cursor] }] },
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
    const result = await advisory.inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
    assert.deepEqual(retainedRows(common), beforeRows); assert.deepEqual(authoringFiles(root), beforeAuthoring);
    assert.equal(result.status, 'inspectable', JSON.stringify(result.blockers));
    assert.equal(result.captures[0].disposition, 'eligible');
    assert.equal(result.captures[0].payloadSha256, hash(saved.payloads.get(output.id)));
    assert.equal(saved.graph.status, 'complete', JSON.stringify(saved.graph.blockers));
    assert.deepEqual(saved.graph.reports, [{ key: { invocationId: extraction.invocationId, captureId: report.id }, format: 'extraction-v1', sha256: hash(saved.payloads.get(report.id)) }]);
    const keys = new Set(saved.graph.protected.filter(row => row.kind === 'capture').map(row => row.captureId));
    for (const header of saved.headers.filter(row => row.invocationId === source.invocationId || row.invocationId === extraction.invocationId &&
      (row.channel === 'report' || row.channel === 'context' || row.attemptId === saved.attempts.find(row => row.operationKey === 'learn/extract').id)))
      assert.ok(keys.has(header.id), `missing exact extraction capture ${header.id}`);
    await t.test('inconclusive and revised supported evaluations both retain every exact dependency', async () => {
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
      const result = await advisory.inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
      assert.deepEqual(retainedRows(common), beforeRows); assert.deepEqual(authoringFiles(root), beforeAuthoring);
      assert.equal(result.status, 'inspectable', JSON.stringify(result.blockers)); assert.equal(result.captures[0].disposition, 'eligible');
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
    });
  } finally { fixture.dispose(); rmSync(container, { recursive: true, force: true }); }
});

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

test('cleanup advisory measures real ended command output after public install and upgrade without changing retained history', async t => {
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
    const workflow = '.factory/workflows/cleanup-command.ts', input = join(container, 'inputs.json');
    writeFileSync(input, '{}');
    const script = "process.stdout.write('hello 🌍\\n'); process.stderr.write('saved error\\n')";
    writeFileSync(join(root, workflow), `export async function run(context) { await context.command('plain-output', { argv: [${JSON.stringify(process.execPath)}, '-e', ${JSON.stringify(script)}] }); }\n`);
    const { invoke } = await import('../dist/lifecycle.js');
    const ended = await invoke({ repository: root, workflow, input, newWorktree: false, worktreeId: root });
    assert.equal(ended.outcome, 'succeeded', JSON.stringify(ended)); assert.equal(ended.cleanup, 'complete');
    const { openCleanupReadStore } = await import('../dist/store.js');
    const read = openCleanupReadStore(common);
    let before, selected, backupKey;
    try {
      const snapshot = read.readCleanupSnapshot(), headers = read.pageCleanupCaptureHeaders({ through: snapshot.highWater.captures }).records;
      const attempts = read.pageCleanupAttemptFacts({ through: snapshot.highWater.attempts }).records;
      const command = attempts.find(row => row.status === 'known' && row.operationKey === 'plain-output');
      assert.ok(command);
      const output = headers.find(row => row.status === 'known' && row.attemptId === command.id && row.channel === 'stdout');
      assert.ok(output); assert.equal(headers.some(row => row.channel === 'report'), false);
      selected = { invocationId: ended.invocationId, captureId: output.id };
      before = { snapshot, headers, attempts, payload: read.readCleanupCapture(selected) };
      const bound = read.readCleanupOperationEvidence({ operationId: upgraded.operationId }).backupBound;
      assert.equal(bound.status, 'known'); backupKey = { operationId: upgraded.operationId, backupId: bound.data.backupId };
    } finally { read.close(); }
    const source = ['tracked.txt', 'untracked.txt', 'ignored.txt', workflow, '.git/index'].map(path => [path, readFileSync(join(root, path))]);
    const upgrade = join(common, 'factory', `upgrade-${upgraded.operationId}`);
    const backup = join(common, 'factory/maintenance-backups', backupKey.operationId, backupKey.backupId);
    const receiptFiles = [join(upgrade, 'new-receipt.json'), join(upgrade, 'intent.json'), join(upgrade, 'original.json'),
      join(backup, 'backup-receipt.json'), join(backup, 'backup-request.json'), join(backup, 'history.sqlite')];
    const receipts = receiptFiles.map(path => [path, readFileSync(path)]), rows = retainedRows(common), authored = authoringFiles(root);
    // Deliberately import only after the genuine end-user setup, so absent advisory support is the first RED.
    const advisory = await import('../dist/cleanup.js');
    const inspectCleanupSelection = async (...args) => {
      const beforeRows = retainedRows(common), beforeAuthoring = authoringFiles(root);
      const beforeReceipts = receiptFiles.map(path => [path, readFileSync(path)]);
      const inspected = await advisory.inspectCleanupSelection(...args);
      assert.deepEqual(retainedRows(common), beforeRows); assert.deepEqual(authoringFiles(root), beforeAuthoring);
      for (const [path, bytes] of beforeReceipts) assert.deepEqual(readFileSync(path), bytes);
      return inspected;
    };
    const result = await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
    assert.equal(result.advisory, true); assert.equal(result.status, 'inspectable');
    assert.deepEqual(result.blockers, []); assert.equal(result.captures.length, 1);
    assert.equal(result.captures[0].disposition, 'eligible');
    assert.equal(result.captures[0].logicalBytes, '11');
    assert.equal(result.captures[0].payloadSha256, hash('hello 🌍\n'));
    assert.equal(result.selectedLogicalBytes, '11');
    const after = openCleanupReadStore(common);
    try {
      assert.deepEqual({ snapshot: after.readCleanupSnapshot(), headers: after.pageCleanupCaptureHeaders().records,
        attempts: after.pageCleanupAttemptFacts().records, payload: after.readCleanupCapture(selected) }, before);
    } finally { after.close(); }
    for (const [path, bytes] of source) assert.deepEqual(readFileSync(join(root, path)), bytes);
    assert.deepEqual(retainedRows(common), rows); assert.deepEqual(authoringFiles(root), authored);
    for (const [path, bytes] of receipts) assert.deepEqual(readFileSync(path), bytes);
    assert.deepEqual(await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] }), result);

    await t.test('content updates with unchanged high water alter the selected content snapshot', async () => {
      const database = new DatabaseSync(join(common, 'factory/history.sqlite'));
      const text = database.prepare('SELECT text FROM capture_chunks WHERE capture_id=? AND sequence=1').get(selected.captureId).text;
      try {
        database.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=1').run('other 🌍\n', selected.captureId);
        const changed = await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
        assert.equal(changed.status, 'inspectable'); assert.equal(changed.captures[0].logicalBytes, '11');
        assert.equal(changed.captures[0].payloadSha256, hash('other 🌍\n'));
        assert.notEqual(changed.snapshotSha256, result.snapshotSha256); assert.notEqual(changed.impactSha256, result.impactSha256);
        const reader = openCleanupReadStore(common);
        try { assert.deepEqual(reader.readCleanupSnapshot().highWater, before.snapshot.highWater); } finally { reader.close(); }
      } finally { database.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=1').run(text, selected.captureId); database.close(); }
    });
    await t.test('exact backup facts stay distinct and analysis exhaustion never becomes inspection permission', async () => {
      const selectedBackup = { kind: 'backups', backups: [backupKey] };
      const owned = await inspectCleanupSelection(root, selectedBackup);
      assert.equal(owned.backups[0].status, 'owned'); assert.deepEqual(owned.backups[0].selection, backupKey);
      const unrelated = await inspectCleanupSelection(root, selectedBackup, { nodes: 1 });
      assert.equal(unrelated.backups[0].status, 'owned'); assert.equal(unrelated.status, 'inspectable');
      const limited = await inspectCleanupSelection(root, selectedBackup, { stateBytes: 1024 });
      assert.equal(limited.status, 'blocked'); assert.equal(limited.impactSha256, null);
      assert.ok(limited.blockers.some(row => row.code === 'limit' && row.limit === 'stateBytes'));
    });
    await t.test('callers cannot supply recovery flags or widen selection through mode fields', async () => {
      for (const selection of [
        { kind: 'captures', captures: [selected, selected], exceptional: [], reviewNonOutput: [] },
        { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [], recovery: { status: 'clear', sha256: '0'.repeat(64) } },
      ]) assert.equal((await inspectCleanupSelection(root, selection)).status, 'blocked');
      assert.equal((await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [selected], reviewNonOutput: [] })).status, 'blocked');
      assert.equal((await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] }, { elapsedMs: 30001 })).status, 'blocked');
    });
    await t.test('current admitted activity and a ready-state recovery marker refuse payload eligibility', async () => {
      const { openRepositoryStore } = await import('../dist/store.js');
      const { currentOwner } = await import('../dist/native/process.js');
      const writer = openRepositoryStore(common);
      try {
        const run = await writer.createRun(), active = await writer.startInvocation({ runId: run.id, worktreeId: ended.worktreeId, owner: currentOwner() });
        await writer.activateInvocation(active.id);
        const attempt = await writer.admitAttempt({ id: randomUUID(), invocationId: active.id, operationKey: 'pending-command', kind: 'command', intent: 'initial' });
        const blocked = await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
        assert.equal(blocked.captures[0].disposition, 'refused'); assert.ok(blocked.blockers.some(row => row.code === 'unassessed-recovery'));
        await writer.settleAttempt({ id: attempt.id, launch: 'not_started', outcome: 'interrupted', quiescent: true, evidence: 'fixture did not start a child' });
        await writer.stopAdmissions(active.id);
        await writer.finalizeInvocation({ id: active.id, outcome: 'interrupted', cleanup: 'complete', claimId: active.claim.id, token: active.claim.token });
      } finally { writer.close(); }
      const marker = join(common, 'factory/upgrade-incomplete'); writeFileSync(marker, 'fixture marker', { flag: 'wx', mode: 0o600 });
      try {
        const blocked = await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
        assert.equal(blocked.captures[0].disposition, 'refused'); assert.ok(blocked.blockers.some(row => row.code === 'unassessed-recovery'));
      } finally { unlinkSync(marker); }
    });
    await t.test('ordinary output cannot qualify after its genuine command ownership is removed', async () => {
      const database = new DatabaseSync(join(common, 'factory/history.sqlite'));
      const owner = database.prepare('SELECT attempt_id FROM captures WHERE id=?').get(selected.captureId).attempt_id;
      assert.ok(owner);
      try {
        database.prepare('UPDATE captures SET attempt_id=NULL WHERE id=?').run(selected.captureId);
        const inspected = await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
        assert.equal(inspected.status, 'blocked');
        assert.equal(inspected.captures[0].disposition, 'refused');
        assert.ok(inspected.blockers.some(row => row.code === 'ownership' && row.node.captureId === selected.captureId));
      } finally { database.prepare('UPDATE captures SET attempt_id=? WHERE id=?').run(owner, selected.captureId); database.close(); }
    });
    await t.test('saved question and selected context retain their actual older same-run owner', async () => {
      const questionWorkflow = '.factory/workflows/cleanup-question.ts';
      writeFileSync(join(root, questionWorkflow), `export async function run(context) { await context.command('question-output', { argv: [${JSON.stringify(process.execPath)}, '-e', "process.stdout.write('retained context')"] }); await context.needsInput('Choose a target', 'Retain the old context'); }\n`);
      const question = await invoke({ repository: root, workflow: questionWorkflow, input, newWorktree: false, worktreeId: root });
      assert.equal(question.outcome, 'needs_input', JSON.stringify(question)); assert.equal(question.cleanup, 'complete');
      let request, context;
      const saved = openCleanupReadStore(common);
      try {
        const headers = saved.pageCleanupCaptureHeaders().records;
        const attempt = saved.pageCleanupAttemptFacts().records.find(row => row.operationKey === 'question-output');
        request = headers.find(row => row.invocationId === question.invocationId && row.channel === 'request');
        context = headers.find(row => row.attemptId === attempt.id && row.channel === 'stdout');
        assert.ok(request); assert.ok(context);
      } finally { saved.close(); }
      const followed = await invoke({ repository: root, workflow, input, newWorktree: false, worktreeId: root,
        runId: question.runId, question: request.id, contexts: [context.id] });
      assert.equal(followed.outcome, 'succeeded', JSON.stringify(followed));
      const inspected = await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
      assert.equal(inspected.status, 'inspectable', JSON.stringify(inspected.blockers));
      const { analyzeCleanupReferences } = await import('../dist/cleanup-references.js');
      const reader = openCleanupReadStore(common);
      try {
        const graph = analyzeCleanupReferences(reader);
        assert.equal(graph.status, 'complete', JSON.stringify(graph.blockers));
        for (const id of [request.id, context.id]) assert.ok(graph.protected.some(node => node.kind === 'capture'
          && node.captureId === id && node.invocationId === question.invocationId));
        assert.ok(graph.edges.some(edge => edge.kind === 'question' && edge.from.invocationId === followed.invocationId
          && edge.to.invocationId === question.invocationId && edge.to.captureId === request.id));
      } finally { reader.close(); }
    });
    await t.test('every opaque or incomplete report blocks payloads and report, request and root inputs stay protected', async t => {
      const opaqueWorkflow = '.factory/workflows/cleanup-opaque.ts';
      writeFileSync(join(root, opaqueWorkflow), `export async function run() { return { custom: true, reference: ${JSON.stringify(selected.captureId)} }; }\n`);
      const opaque = await invoke({ repository: root, workflow: opaqueWorkflow, input, newWorktree: false, worktreeId: root });
      assert.equal(opaque.outcome, 'succeeded', JSON.stringify(opaque));
      const reader = openCleanupReadStore(common);
      let report, request, rootInput;
      try {
        const headers = reader.pageCleanupCaptureHeaders().records;
        report = headers.find(row => row.invocationId === opaque.invocationId && row.channel === 'report');
        request = headers.find(row => row.channel === 'request');
        rootInput = before.headers.find(row => row.channel === 'context' && row.attemptId === null);
      } finally { reader.close(); }
      assert.ok(report); assert.ok(request); assert.ok(rootInput);
      const inspected = await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
      assert.equal(inspected.status, 'blocked'); assert.equal(inspected.captures[0].disposition, 'refused');
      assert.ok(inspected.blockers.some(row => row.code === 'opaque' && row.node?.captureId === report.id));
      for (const header of [report, request, rootInput]) {
        const key = { invocationId: header.invocationId, captureId: header.id };
        const protectedResult = await inspectCleanupSelection(root, { kind: 'captures', captures: [key], exceptional: [key], reviewNonOutput: [] });
        assert.equal(protectedResult.status, 'blocked'); assert.equal(protectedResult.captures[0].disposition, 'protected');
      }
      const database = new DatabaseSync(join(common, 'factory/history.sqlite'));
      const text = database.prepare('SELECT text FROM capture_chunks WHERE capture_id=? AND sequence=1').get(report.id).text;
      try {
        await t.test('malformed report', async () => {
          database.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=1').run('{', report.id);
          try {
            const value = await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
            assert.ok(value.blockers.some(row => row.code === 'malformed' && row.node?.captureId === report.id));
          } finally { database.prepare('UPDATE capture_chunks SET text=? WHERE capture_id=? AND sequence=1').run(text, report.id); }
        });
        for (const state of ['partial', 'unknown', 'open', 'pruned']) await t.test(`selected ${state} capture`, async () => {
          database.prepare('UPDATE captures SET state=? WHERE id=?').run(state, selected.captureId);
          try {
            const value = await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
            assert.equal(value.status, 'blocked'); assert.notEqual(value.captures[0].disposition, 'eligible');
            assert.ok(value.blockers.some(row => row.node?.captureId === selected.captureId));
          } finally { database.prepare("UPDATE captures SET state='complete' WHERE id=?").run(selected.captureId); }
        });
        await t.test('partial report', async () => {
          database.prepare("UPDATE captures SET state='partial' WHERE id=?").run(report.id);
          try {
            const value = await inspectCleanupSelection(root, { kind: 'captures', captures: [selected], exceptional: [], reviewNonOutput: [] });
            assert.ok(value.blockers.some(row => row.code === 'partial' && row.node?.captureId === report.id));
          } finally { database.prepare("UPDATE captures SET state='complete' WHERE id=?").run(report.id); }
        });
      } finally { database.close(); }
      const exactBackup = await inspectCleanupSelection(root, { kind: 'backups', backups: [backupKey] });
      assert.equal(exactBackup.backups[0].status, 'owned');
    });
  } finally { fixture.dispose(); rmSync(container, { recursive: true, force: true }); }
});

import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { once } from 'node:events';
import { createHash } from 'node:crypto';
import { copyFileSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createInterface } from 'node:readline';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const fixture = fileURLToPath(new URL('../qualification/windows-storage-loader-fixture.py', import.meta.url));
const childScript = fileURLToPath(new URL('../qualification/windows-storage-loader-child.mjs', import.meta.url));
const qualifier = fileURLToPath(new URL('../qualification/windows-storage-loader.qualification.mjs', import.meta.url));
const python = process.env.FACTORY_WINDOWS_LOADER_TEST_PYTHON;
assert.ok(python, 'FACTORY_WINDOWS_LOADER_TEST_PYTHON must select trusted Python 3.13.14');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const sourceFiles = ['qualification/windows-storage-loader-fixture.py', 'qualification/windows-storage-loader-canary.c',
  'qualification/windows-storage-loader-child.mjs', 'qualification/windows-storage-loader.qualification.mjs',
  'test/windows-storage-loader-contract.test.mjs', 'qualification/windows-storage-loader.md'];
const selection = () => ({ schema: 1, sourceCommit: 'a'.repeat(40),
  sourceSha256: Object.fromEntries(sourceFiles.map(name => [name, 'b'.repeat(64)])),
  inputRoot: 'C:\\trusted-input', stageParent: 'C:\\trusted-fixtures',
  pythonSha256: 'c'.repeat(64), buildReceiptSha256: 'd'.repeat(64),
  artifactSha256: 'e'.repeat(64), windowsBuild: '10.0.26100' });
function invoke(bytes, digest = sha(bytes), caseId = 'positive-user') {
  const root = mkdtempSync(join(tmpdir(), 'factory-loader-contract-'));
  try {
    const selection = join(root, 'selection.json');
    writeFileSync(selection, bytes);
    return spawnSync(python, ['-I', '-S', fixture, '--selection', selection, '--sha256', digest, '--case', caseId], {
      encoding: 'utf8', timeout: 5000, maxBuffer: 16384,
    });
  } finally { rmSync(root, { recursive: true, force: true }); }
}

test('fixed fixture invocation refuses candidate trust fields with closed output', () => {
  const result = invoke('{"trusted":true,"path":"private-canary-secret"}');
  assert.equal(result.status, 1);
  assert.equal(result.stderr, '');
  assert.equal(result.stdout, '{"scope":"windows-storage-loader-fixture","case":"positive-user","state":"refused","phase":"selection","reason":"selection"}\n');
});

test('authenticated closed selection check cannot confer native authority', () => {
  const bytes = JSON.stringify(selection());
  const result = invoke(bytes, sha(bytes), 'selection-only');
  assert.equal(result.status, 1);
  assert.equal(result.stderr, '');
  assert.equal(result.stdout, '{"scope":"windows-storage-loader-fixture","case":"selection-only","state":"refused","phase":"prerequisite","reason":"native-required"}\n');
});

test('fixture refuses overlapping source and disposable namespaces before native work', () => {
  const selected = selection();
  selected.stageParent = `${selected.inputRoot}\\output`;
  const bytes = JSON.stringify(selected);
  const result = invoke(bytes, sha(bytes), 'selection-only');
  assert.equal(result.status, 1);
  assert.equal(JSON.parse(result.stdout).reason, 'selection');
});

test('fixed real child refuses an unknown controller command before require', () => {
  const result = spawnSync(process.execPath, [childScript, 'positive-user'], {
    input: '{"command":"arbitrary-secret"}\n', encoding: 'utf8', timeout: 3000, maxBuffer: 16384,
  });
  assert.equal(result.status, 1);
  assert.equal(result.stderr, '');
  assert.equal(result.stdout, '{"scope":"windows-storage-loader-child","event":"ready"}\n' +
    '{"scope":"windows-storage-loader-child","event":"result","state":"failed","reason":"protocol"}\n');
});

test('real missing fixed canary reports closed failure and waits for release', async () => {
  const root = mkdtempSync(join(tmpdir(), 'factory-loader-real-child-'));
  const script = join(root, 'windows-storage-loader-child.mjs');
  copyFileSync(childScript, script);
  const child = spawn(process.execPath, [script, 'positive-user'], {
    cwd: root, stdio: ['pipe', 'pipe', 'pipe'], timeout: 3000,
  });
  const closed = once(child, 'close');
  const lines = createInterface({ input: child.stdout })[Symbol.asyncIterator]();
  let stderr = '';
  child.stderr.on('data', bytes => { stderr += bytes; });
  try {
    assert.deepEqual(JSON.parse((await lines.next()).value), { scope: 'windows-storage-loader-child', event: 'ready' });
    child.stdin.write('{"command":"load"}\n');
    assert.deepEqual(JSON.parse((await lines.next()).value), {
      scope: 'windows-storage-loader-child', event: 'result', state: 'failed', reason: 'loader',
    });
    assert.equal(child.exitCode, null);
    child.stdin.end('{"command":"release"}\n');
    assert.deepEqual(await closed, [1, null]);
    assert.equal(stderr, '');
    assert.equal((await lines.next()).done, true);
  } finally {
    if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
    await closed;
    rmSync(root, { recursive: true, force: true });
  }
});

test('qualification receipt interface refuses forged authority and never echoes payload', () => {
  const result = spawnSync(process.execPath, [qualifier, '--validate-receipt', 'a'.repeat(64)], {
    input: '{"state":"pass","storageAdmitted":true,"path":"private-receipt-secret"}\n',
    encoding: 'utf8', timeout: 3000, maxBuffer: 16384,
  });
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '{"scope":"windows-storage-loader-receipt-parser","state":"refused","reason":"receipt"}\n');
  assert.equal(result.stderr, '');
});

const closedReceipt = () => ({ scope: 'windows-storage-loader-fixture', case: 'positive-user',
  state: 'pass', phase: 'complete', reason: 'none', selectionSha256: 'a'.repeat(64),
  sourceCommit: 'b'.repeat(40), nodeSha256: 'd702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5',
  artifactSha256: 'c'.repeat(64), buildReceiptSha256: 'd'.repeat(64),
  processStarted: true, processExit: true, stdoutEOF: true, stderrEOF: true,
  ownedClose: true, capture: [256, 0], discard: [0, 0], stage: 'removed' });
function validateReceipt(bytes, selected = 'a'.repeat(64)) {
  return spawnSync(process.execPath, [qualifier, '--validate-receipt', selected], {
    input: bytes, encoding: 'utf8', timeout: 3000, maxBuffer: 16384,
  });
}
test('receipt parser validates a closed context without conferring native authority', () => {
  const result = validateReceipt(`${JSON.stringify(closedReceipt())}\n`);
  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
  assert.equal(result.stdout, '{"scope":"windows-storage-loader-receipt-parser","state":"validated","reason":"none"}\n');
});

test('closed receipt CLI rejects counter, closure, context and disclosure forgeries', () => {
  const controls = [
    ['capture limit', receipt => { receipt.capture[0] = 8193; }],
    ['discard limit', receipt => { receipt.discard[0] = 8193; }],
    ['negative counter', receipt => { receipt.capture[1] = -1; }],
    ['successful discard', receipt => { receipt.discard[0] = 1; }],
    ['missing process exit', receipt => { receipt.processExit = false; }],
    ['missing stdout EOF', receipt => { receipt.stdoutEOF = false; }],
    ['missing stderr EOF', receipt => { receipt.stderrEOF = false; }],
    ['failed owned close', receipt => { receipt.ownedClose = false; }],
    ['retained successful stage', receipt => { receipt.stage = 'retained'; }],
    ['unknown reason', receipt => { receipt.reason = 'private-receipt-canary'; }],
    ['candidate trust', receipt => { receipt.trusted = true; }],
    ['raw path disclosure', receipt => { receipt.path = 'private-receipt-canary'; }],
    ['wrong runtime digest', receipt => { receipt.nodeSha256 = 'e'.repeat(64); }],
    ['wrong selection', receipt => { receipt.selectionSha256 = 'e'.repeat(64); }],
    ['negative control forged pass', receipt => { receipt.case = 'extra-dll'; }],
  ];
  for (const [name, mutate] of controls) {
    const receipt = closedReceipt();
    mutate(receipt);
    const result = validateReceipt(`${JSON.stringify(receipt)}\n`);
    assert.equal(result.status, 1, name);
    assert.equal(result.stderr, '', name);
    assert.equal(result.stdout, '{"scope":"windows-storage-loader-receipt-parser","state":"refused","reason":"receipt"}\n', name);
  }
  const wire = `${JSON.stringify(closedReceipt())}\n`;
  for (const malformed of [wire.replace('"state":"pass"', '"state":"pass","state":"pass"'),
    `${wire}${wire}`, 'x'.repeat(1025), wire.trimEnd(), `${wire} `]) {
    const result = validateReceipt(malformed);
    assert.equal(result.status, 1);
    assert.equal(result.stderr, '');
    assert.doesNotMatch(result.stdout, /private-receipt-canary/);
  }
});

test('failure receipt may retain its primary bounds evidence with unknown cleanup facts', () => {
  const receipt = closedReceipt();
  Object.assign(receipt, { case: 'stdout-overflow', state: 'refused', phase: 'protocol', reason: 'bounds',
    stdoutEOF: false, ownedClose: false, capture: [8192, 0], discard: [8192, 0], stage: 'retained' });
  const result = validateReceipt(`${JSON.stringify(receipt)}\n`);
  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
  assert.equal(result.stdout, '{"scope":"windows-storage-loader-receipt-parser","state":"validated","reason":"none"}\n');
});

test('isolated public selection parser refuses malformed authority and namespace controls', () => {
  const controls = [
    selected => { selected.schema = true; },
    selected => { selected.sourceCommit = 'A'.repeat(40); },
    selected => { delete selected.sourceSha256[sourceFiles[0]]; },
    selected => { selected.sourceSha256['qualification/extra.py'] = 'f'.repeat(64); },
    selected => { selected.pythonSha256 = 'private-selection-canary'; },
    selected => { selected.trusted = true; },
    selected => { selected.executable = 'private-selection-canary'; },
    ...['C:\\unsafe:stream', '\\\\host\\share', '\\\\?\\C:\\unsafe', 'C:\\one\\..\\two', 'C:\\one.',
      'C:\\one ', 'C:\\CON.txt', 'C:\\one;other', `C:\\${'x'.repeat(256)}`, `C:\\${'é'.repeat(128)}`,
      `C:\\${Array(65).fill('segment').join('\\')}`].map(path => selected => { selected.inputRoot = path; }),
  ];
  for (const mutate of controls) {
    const selected = selection();
    mutate(selected);
    const bytes = JSON.stringify(selected);
    const result = invoke(bytes, sha(bytes), 'selection-only');
    assert.equal(result.status, 1);
    assert.equal(result.stderr, '');
    assert.deepEqual(JSON.parse(result.stdout), { scope: 'windows-storage-loader-fixture', case: 'selection-only',
      state: 'refused', phase: 'selection', reason: 'selection' });
  }
  const valid = JSON.stringify(selection());
  for (const bytes of [valid.replace('"schema":1', '"schema":1,"schema":1'),
    `${valid}${valid}`, `${valid}${' '.repeat(1024 * 1024)}`]) {
    const result = invoke(bytes, sha(bytes), 'selection-only');
    assert.equal(result.status, 1);
    assert.equal(JSON.parse(result.stdout).reason, 'selection');
    assert.equal(result.stderr, '');
  }
  assert.equal(JSON.parse(invoke(valid, 'f'.repeat(64), 'selection-only').stdout).reason, 'selection');
  assert.equal(JSON.parse(invoke(`${valid} `, sha(valid), 'selection-only').stdout).reason, 'selection');
});

test('actual fixed child bounds a hostile control record before loading', () => {
  const result = spawnSync(process.execPath, [childScript, 'positive-user'], {
    input: 'private-child-canary'.repeat(100), encoding: 'utf8', timeout: 3000, maxBuffer: 16384,
  });
  assert.equal(result.status, 1);
  assert.equal(result.stderr, '');
  assert.equal(result.stdout, '{"scope":"windows-storage-loader-child","event":"ready"}\n' +
    '{"scope":"windows-storage-loader-child","event":"result","state":"failed","reason":"protocol"}\n');
});

test('fixed fixture rejects executable and flag overrides without echoing arguments', () => {
  const result = spawnSync(python, ['-I', '-S', fixture, '--selection', 'private-argument-canary',
    '--sha256', 'a'.repeat(64), '--case', 'positive-user', '--executable', 'private-argument-canary'], {
    encoding: 'utf8', timeout: 3000, maxBuffer: 16384,
  });
  assert.equal(result.status, 1);
  assert.equal(result.stderr, '');
  assert.deepEqual(JSON.parse(result.stdout), { scope: 'windows-storage-loader-fixture', case: 'invalid',
    state: 'refused', phase: 'selection', reason: 'selection' });
});

test('real child EOF before the load command remains a closed refusal', () => {
  const result = spawnSync(process.execPath, [childScript, 'positive-user'], {
    input: '', encoding: 'utf8', timeout: 3000, maxBuffer: 16384,
  });
  assert.equal(result.status, 1);
  assert.equal(result.stderr, '');
  assert.equal(result.stdout, '{"scope":"windows-storage-loader-child","event":"ready"}\n' +
    '{"scope":"windows-storage-loader-child","event":"result","state":"failed","reason":"protocol"}\n');
});

test('real fixed child produces actual stdout and stderr overflow controls without a canary', async () => {
  for (const mode of ['stdout-overflow', 'stderr-overflow']) {
    const root = mkdtempSync(join(tmpdir(), 'factory-loader-overflow-'));
    const script = join(root, 'windows-storage-loader-child.mjs');
    copyFileSync(childScript, script);
    const child = spawn(process.execPath, [script, mode], { cwd: root, stdio: ['pipe', 'pipe', 'pipe'], timeout: 3000 });
    const closed = once(child, 'close');
    const lines = createInterface({ input: child.stdout })[Symbol.asyncIterator]();
    let stderr = '';
    child.stderr.on('data', bytes => { stderr += bytes; });
    try {
      assert.equal((await lines.next()).value, '{"scope":"windows-storage-loader-child","event":"ready"}');
      child.stdin.write('{"command":"load"}\n');
      const line = (await lines.next()).value;
      const result = mode === 'stdout-overflow' ? line.slice(8193) : line;
      if (mode === 'stdout-overflow') assert.equal(line.slice(0, 8193), 'x'.repeat(8193));
      assert.deepEqual(JSON.parse(result), { scope: 'windows-storage-loader-child', event: 'result', state: 'failed', reason: 'bounds' });
      assert.equal(child.exitCode, null);
      child.stdin.end('{"command":"release"}\n');
      assert.deepEqual(await closed, [1, null]);
      assert.equal(stderr, mode === 'stderr-overflow' ? 'x'.repeat(8193) : '');
      assert.equal((await lines.next()).done, true);
    } finally {
      if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
      await closed;
      rmSync(root, { recursive: true, force: true });
    }
  }
});

test('explicit native entry hard-fails missing prerequisites without default discovery', () => {
  const root = mkdtempSync(join(tmpdir(), 'factory-loader-discovery-'));
  try {
    copyFileSync(qualifier, join(root, 'windows-storage-loader.qualification.mjs'));
    const environment = { ...process.env };
    delete environment.FACTORY_WINDOWS_LOADER_PYTHON;
    delete environment.FACTORY_WINDOWS_LOADER_SELECTION;
    delete environment.FACTORY_WINDOWS_LOADER_SELECTION_SHA256;
    delete environment.NODE_TEST_CONTEXT;
    const discovered = spawnSync(process.execPath, ['--test'], { cwd: root, env: environment, encoding: 'utf8', timeout: 3000 });
    assert.equal(discovered.status, 0);
    assert.match(discovered.stdout, /tests 0/);
    const explicit = spawnSync(process.execPath, [qualifier, '--native'], { env: environment, encoding: 'utf8', timeout: 3000 });
    assert.equal(explicit.status, 1);
    assert.equal(explicit.stderr, '');
    assert.equal(explicit.stdout, '{"scope":"windows-storage-loader-qualification","state":"refused","case":"prerequisite","reason":"prerequisite"}\n');
  } finally { rmSync(root, { recursive: true, force: true }); }
});

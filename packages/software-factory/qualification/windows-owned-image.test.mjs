import test from 'node:test';
import assert from 'node:assert/strict';
import { validateNative, cases, prepareUpload } from './windows-owned-image.mjs';
import { mkdtempSync, writeFileSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { buildCategories, parseBuildDiagnostic, formatFailure } from './windows-owned-image-diagnostics.mjs';

// Public seam: bounded native evidence -> fixed sanitized qualification result.
const positive = () => [
  'OWNED\t1\tpositive', 'FIRST\t40\t41\t40\t41\t3\t40\t41', 'BARRIER\tcreated\t0',
  'SUSPEND\t0', 'BARRIER\tsuspended\t0',
  `IDENTITY\t1\t${'a'.repeat(32)}\t${'b'.repeat(64)}\t1\t${'a'.repeat(32)}\t${'b'.repeat(64)}`, 'BARRIER\tvalidated\t0', 'CONTINUE\t1',
  'BARRIER\tcontinued\t0', 'DETACH\t1', 'DEBUGGER\t0',
  'BARRIER\tdetached\t0', 'RESUME\t1', 'MARKERS\t1\t1\t1\t0',
  'EXIT\t0', 'OUTPUT\t3\t0\t1\t1', 'CONTROL\t1\t1',
  'CLEANUP\t1\t0', 'HANDLES\t0', 'ELAPSED\t250', 'RESULT\tnone', 'COMPLETE',
].join('\n') + '\n';

test('first-event native canary can qualify only its declared narrow profile', () => {
  const result = validateNative(positive(), 'positive');
  assert.equal(result.qualified, true);
  assert.equal(result.productAdmission, false);
  assert.equal(result.namespaceIdentity, 'unverified');
  assert.equal(result.helperAdmission, 'refused');
});

test('missing detach, suspension or debugger postcondition cannot qualify a resume', () => {
  for (const row of ['SUSPEND\t0\n', 'DETACH\t1\n', 'DEBUGGER\t0\n', 'BARRIER\tdetached\t0\n'])
    assert.equal(validateNative(positive().replace(row, ''), 'positive').qualified, false, row);
});

test('raw process and thread observations must refer to the exact created objects', () => {
  for (const row of ['FIRST\t0\t41\t0\t41\t3\t0\t41', 'FIRST\t40\t41\t42\t41\t3\t40\t41',
    'FIRST\t40\t41\t40\t42\t3\t40\t41', 'FIRST\t40\t41\t40\t41\t8\t40\t41',
    'FIRST\t40\t41\t40\t41\t3\t42\t41'])
    assert.equal(validateNative(positive().replace(/^FIRST.*$/m, row), 'positive').qualified, false);
});

test('early native user code, count surprises, missing markers and output errors refuse', () => {
  for (const [old, replacement] of [['BARRIER\tcreated\t0', 'BARRIER\tcreated\t1'],
    ['BARRIER\tcontinued\t0', 'BARRIER\tcontinued\t8'], ['BARRIER\tdetached\t0', 'BARRIER\tdetached\t7'],
    ['SUSPEND\t0', 'SUSPEND\t1'], ['RESUME\t1', 'RESUME\t2'], ['DEBUGGER\t0', 'DEBUGGER\t1'],
    ['MARKERS\t1\t1\t1\t0', 'MARKERS\t1\t0\t1\t0'], ['MARKERS\t1\t1\t1\t0', 'MARKERS\t1\t1\t1\t1'],
    ['OUTPUT\t3\t0\t1\t1', 'OUTPUT\t3\t0\t1\t0'], ['OUTPUT\t3\t0\t1\t1', 'OUTPUT\t4\t0\t1\t1']])
    assert.equal(validateNative(positive().replace(old, replacement), 'positive').qualified, false, replacement);
});

test('same-byte different object identity cannot be converted into a positive', () => {
  const line = `IDENTITY\t1\t${'a'.repeat(32)}\t${'b'.repeat(64)}\t1\t${'c'.repeat(32)}\t${'b'.repeat(64)}`;
  assert.equal(validateNative(positive().replace(/^IDENTITY.*$/m, line), 'positive').qualified, false);
});

const refusal = (name, last, failure, identity) => {
  let rows = positive().trimEnd().split('\n');
  const end = rows.findIndex(row => row === last);
  assert.ok(end >= 0);
  rows = rows.slice(0, end + 1);
  rows[0] = `OWNED\t1\t${name}`;
  if (identity) rows = rows.map(row => row.startsWith('IDENTITY\t') ? identity : row);
  return rows.concat(['EXIT\t125', 'OUTPUT\t0\t0\t1\t1', 'CONTROL\t1\t1', 'CLEANUP\t1\t0',
    'HANDLES\t0', 'ELAPSED\t250', `RESULT\t${failure}`, 'COMPLETE']).join('\n') + '\n';
};
const refusalSpec = {
  'wrong-hash': ['IDENTITY', 'identity'], 'different-file-id': ['IDENTITY', 'identity'], 'different-image': ['IDENTITY', 'identity'],
  'stop-created': ['BARRIER\tcreated\t0', 'stop'], 'stop-suspended': ['BARRIER\tsuspended\t0', 'stop'],
  'stop-validated': ['BARRIER\tvalidated\t0', 'stop'], 'stop-continued': ['BARRIER\tcontinued\t0', 'stop'],
  'stop-detached': ['BARRIER\tdetached\t0', 'stop'], 'stop-resume': ['RESUME\t1', 'stop'],
  'fail-event': ['OWNED', 'event'], 'fail-image-handle': ['BARRIER\tsuspended\t0', 'image-handle'],
  'fail-duplicate': ['BARRIER\tsuspended\t0', 'duplicate'], 'fail-query': ['BARRIER\tsuspended\t0', 'query'],
  'fail-suspend': ['BARRIER\tcreated\t0', 'suspend'], 'fail-continue': ['BARRIER\tvalidated\t0', 'continue'],
  'fail-detach': ['BARRIER\tcontinued\t0', 'detach'], 'fail-postcondition': ['DETACH\t1', 'postcondition'],
  'fail-resume': ['BARRIER\tdetached\t0', 'resume'], 'owner-interruption': ['BARRIER\tcreated\t0', 'owner-loss'],
};
function fixture(name) {
  if (name.startsWith('positive')) return positive().replace('OWNED\t1\tpositive\n', `OWNED\t1\t${name}\n`);
  if (name.endsWith('-replacement')) {
    const kind = name === 'path-replacement' ? 'file' : name === 'alias-replacement' ? 'alias' : 'ancestor';
    return positive().replace('OWNED\t1\tpositive\n', `OWNED\t1\t${name}\nMUTATION\t${kind}\tblocked\n`);
  }
  if (['deadline', 'output-limit', 'crash'].includes(name)) return positive().replace('OWNED\t1\tpositive\n', `OWNED\t1\t${name}\n`)
    .replace('EXIT\t0', name === 'crash' ? 'EXIT\t3762438722' : 'EXIT\t125').replace('RESULT\tnone', `RESULT\t${name}`)
    .replace('ELAPSED\t250', name === 'deadline' ? 'ELAPSED\t700' : 'ELAPSED\t250')
    .replace('OUTPUT\t3\t0', name === 'output-limit' ? 'OUTPUT\t266240\t0' : name === 'crash' || name === 'deadline' ? 'OUTPUT\t0\t0' : 'OUTPUT\t3\t0');
  const [anchor, failure] = refusalSpec[name];
  const last = positive().trimEnd().split('\n').find(row => row === anchor || row.startsWith(anchor + '\t'));
  const identity = name === 'wrong-hash' ? `IDENTITY\t1\t${'a'.repeat(32)}\t${'b'.repeat(64)}\t1\t${'a'.repeat(32)}\t${'c'.repeat(64)}`
    : name === 'different-file-id' ? `IDENTITY\t1\t${'a'.repeat(32)}\t${'b'.repeat(64)}\t1\t${'c'.repeat(32)}\t${'b'.repeat(64)}`
    : name === 'different-image' ? `IDENTITY\t1\t${'a'.repeat(32)}\t${'b'.repeat(64)}\t1\t${'c'.repeat(32)}\t${'c'.repeat(64)}` : undefined;
  return refusal(name, last, failure, identity);
}

test('bounded native refusal and termination profiles qualify their intended control only', () => {
  for (const name of cases) assert.equal(validateNative(fixture(name), name).qualified, true, name);
});

test('refusal labels cannot hide missing execution phases', () => {
  for (const name of Object.keys(refusalSpec).filter(x => x !== 'fail-event')) {
    const rows = fixture(name).split('\n').filter(row => !row.startsWith('FIRST\t') && !row.startsWith('BARRIER\t'));
    assert.equal(validateNative(rows.join('\n'), name).qualified, false, name);
  }
});

test('failure seams cannot silently continue to additional release phases', () => {
  const forged = fixture('fail-detach').replace('EXIT\t125', 'DETACH\t1\nDEBUGGER\t0\nBARRIER\tdetached\t0\nEXIT\t125');
  assert.equal(validateNative(forged, 'fail-detach').qualified, false);
});

test('a replaced namespace qualifies only actual image mismatch refusal', () => {
  const identity = `IDENTITY\t1\t${'a'.repeat(32)}\t${'b'.repeat(64)}\t1\t${'c'.repeat(32)}\t${'c'.repeat(64)}`;
  for (const [name, kind] of [['path-replacement', 'file'], ['ancestor-replacement', 'ancestor'], ['alias-replacement', 'alias']]) {
    const receipt = refusal(name, positive().split('\n').find(x => x.startsWith('IDENTITY\t')), 'identity', identity)
      .replace(`OWNED\t1\t${name}\n`, `OWNED\t1\t${name}\nMUTATION\t${kind}\treplaced\n`);
    assert.equal(validateNative(receipt, name).qualified, true);
    assert.equal(validateNative(fixture(name).replace('\tblocked\n', '\treplaced\n'), name).qualified, false);
  }
});

test('cleanup, independent-control survival, caps, order and unknown fields fail closed', () => {
  for (const receipt of [positive().replace('CLEANUP\t1\t0', 'CLEANUP\t0\t1'), positive().replace('HANDLES\t0', 'HANDLES\t1'),
    positive().replace('CONTROL\t1\t1', 'CONTROL\t0\t1'), positive().replace('ELAPSED\t250', 'ELAPSED\t10001'),
    positive() + 'PRIVATE\tpath\n', positive().replace('RESUME\t1\n', 'RESUME\t1\nRESUME\t1\n'),
    positive().replace('CONTINUE\t1\n', ''), positive().replace('COMPLETE\n', ''), 'x'.repeat(65537),
    positive().replace('ELAPSED\t250', 'ELAPSED\t000250')])
    assert.equal(validateNative(receipt, 'positive').qualified, false);
});

function evidence() {
  const root = mkdtempSync(join(tmpdir(), 'owned-image-protocol-'));
  for (const name of cases) writeFileSync(join(root, `${name}.private.tsv`), fixture(name));
  writeFileSync(join(root, 'driver.private.json'), JSON.stringify({ protocol: 1, complete: true, cleanup: true, node: 'v24.22.1',
    cases: cases.map(name => ({ name, exitCode: 0, signal: null, capped: false, timedOut: false })),
    // This hostile claimed status must never be copied into public artifacts.
    status: 'C:\\private\\secret', productAdmission: true }));
  return root;
}

test('artifact guard reconstructs exactly two bounded artifacts without private identity data', () => {
  const root = evidence();
  try {
    const report = prepareUpload(root);
    assert.equal(report.productAdmission, false);
    assert.deepEqual(readdirSync(join(root, 'upload')).sort(), ['native.tsv', 'qualification.json']);
    const output = readFileSync(join(root, 'upload', 'qualification.json'), 'utf8');
    assert.doesNotMatch(output, /secret|C:|"40"|aaaaaaaa|bbbbbbbb|sha256|compilerVersion/);
    assert.equal(Buffer.byteLength(output) < 65536, true);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('forged completed driver status cannot override native cleanup refusal', () => {
  const root = evidence();
  try {
    writeFileSync(join(root, 'positive.private.tsv'), fixture('positive').replace('CLEANUP\t1\t0', 'CLEANUP\t0\t1'));
    assert.throws(() => prepareUpload(root));
    assert.equal(readdirSync(root).includes('upload'), false);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('artifact guard refuses caps, timeouts, signals, missing cases and oversized private input', () => {
  for (const change of ['cap', 'timeout', 'signal', 'missing', 'order', 'oversize', 'native-size']) {
    const root = evidence();
    try {
      const file = join(root, 'driver.private.json');
      const source = JSON.parse(readFileSync(file, 'utf8'));
      if (change === 'cap') source.cases[0].capped = true;
      if (change === 'timeout') source.cases[0].timedOut = true;
      if (change === 'signal') source.cases[0].signal = 'SIGTERM';
      if (change === 'missing') source.cases.pop();
      if (change === 'order') source.cases.reverse();
      writeFileSync(file, change === 'oversize' ? 'x'.repeat(65537) : JSON.stringify(source));
      if (change === 'native-size') writeFileSync(join(root, 'positive.private.tsv'), 'x'.repeat(65537));
      assert.throws(() => prepareUpload(root), undefined, change);
      assert.equal(readdirSync(root).includes('upload'), false, change);
    } finally { rmSync(root, { recursive: true, force: true }); }
  }
});

test('unknown native row names cannot invoke object prototype members', () => {
  for (const row of ['__proto__', 'constructor', 'toString', 'hasOwnProperty'])
    assert.equal(validateNative(positive().replace('COMPLETE\n', `${row}\nCOMPLETE\n`), 'positive').qualified, false);
});

test('native stop and crash controls require their actual intended exit outcome', () => {
  for (const name of ['wrong-hash', 'different-file-id', 'stop-created', 'stop-resume', 'deadline', 'output-limit', 'crash'])
    assert.equal(validateNative(fixture(name).replace(/^EXIT.*$/m, 'EXIT\t94'), name).qualified, false, name);
  assert.equal(validateNative(fixture('deadline').replace(/^ELAPSED.*$/m, 'ELAPSED\t250'), 'deadline').qualified, false);
});

test('build diagnostics accept only the complete fixed producer grammar', () => {
  for (const category of buildCategories)
    assert.deepEqual(parseBuildDiagnostic(`OWNED_IMAGE_BUILD\t1\t${category}\tnone\tnone\t0\n`),
      { category, code: 'none', source: 'none', line: 0 });
  assert.deepEqual(parseBuildDiagnostic('OWNED_IMAGE_BUILD\t1\tcompile\tC2065\tprobe\t123\r\n'),
    { category: 'compile', code: 'C2065', source: 'probe', line: 123 });
  assert.deepEqual(parseBuildDiagnostic('OWNED_IMAGE_BUILD\t1\tmissing-msvc\tnone\tnone\t0\n'),
    { category: 'missing-msvc', code: 'none', source: 'none', line: 0 });
});

test('path-bearing, forged, multiline and oversized build data is fully redacted', () => {
  for (const value of ['C:\\private\\tool.exe failed', 'OWNED_IMAGE_BUILD\t1\tC:\\private\tnone\tnone\t0\n',
    'OWNED_IMAGE_BUILD\t1\tcompile\tC2065: secret\tprobe\t123\n',
    'OWNED_IMAGE_BUILD\t1\tcompile\tC2065\tC:\\private.cpp\t123\n',
    'OWNED_IMAGE_BUILD\t1\tcompile\tC2065\tprobe\t999999\n',
    'OWNED_IMAGE_BUILD\t1\thost\tnone\tnone\t0\nsecret\n', 'x'.repeat(513),
    'OWNED_IMAGE_BUILD\t1\thost\tnone\tnone\t0\n\n',
    'OWNED_IMAGE_BUILD\t1\thost\tC2065\tprobe\t1\n',
    'OWNED_IMAGE_BUILD\t1\tcompile\tLNK2019\tprobe\t1\n',
    'OWNED_IMAGE_BUILD\t1\tcompile\tC2065\tprobe\t01\n'])
    assert.deepEqual(parseBuildDiagnostic(value), { category: 'unexpected', code: 'none', source: 'none', line: 0 });
});

test('driver failure output validates phase, finite case and fixed compiler fields again', () => {
  for (const category of ['launch', 'timeout', 'cap', 'interrupted'])
    assert.equal(formatFailure({ phase: 'build', category }),
      `Owned image native qualification failed phase=build case=none category=${category} code=none source=none line=0\n`);
  assert.equal(formatFailure({ phase: 'case', name: 'fail-detach', category: 'native' }),
    'Owned image native qualification failed phase=case case=fail-detach category=native code=none source=none line=0\n');
  assert.equal(formatFailure({ phase: 'build', ...parseBuildDiagnostic('OWNED_IMAGE_BUILD\t1\tcompile\tC2065\tprobe\t123\n') }),
    'Owned image native qualification failed phase=build case=none category=compile code=C2065 source=probe line=123\n');
  for (const value of [{ phase: 'C:\\secret', name: 'positive', category: 'native' },
    { phase: 'case', name: 'positive\nsecret', category: 'native' },
    { phase: 'host', category: 'C:\\secret' }, { phase: 'pin', category: 'native' },
    { phase: ['host'], category: 'host' },
    { phase: 'build', category: 'compile', code: 'C2065\nsecret', source: 'probe', line: 4 },
    { phase: 'build', category: 'compile', code: 'C2065\n', source: 'probe', line: 4 },
    { phase: 'host', category: 'host', secret: 'C:\\private' }]) {
    const output = formatFailure(value);
    assert.equal(output, 'Owned image native qualification failed phase=unexpected case=none category=unexpected code=none source=none line=0\n');
  }
});

test('public driver reports a fixed host phase without invoking a native build', () => {
  const root = mkdtempSync(join(tmpdir(), 'owned-image-host-diagnostic-'));
  try {
    const driver = fileURLToPath(new URL('./windows-owned-image-native.qualification.mjs', import.meta.url));
    const result = spawnSync(process.execPath, [driver], { encoding: 'utf8', timeout: 5000, maxBuffer: 1024,
      env: { ...process.env, WINDOWS_OWNED_IMAGE_EVIDENCE: root } });
    assert.equal(result.status, 1);
    assert.equal(result.stdout, '');
    assert.equal(result.stderr, 'Owned image native qualification failed phase=host case=none category=host code=none source=none line=0\n');
    assert.deepEqual(readdirSync(root), []);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

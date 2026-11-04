import test from 'node:test';
import assert from 'node:assert/strict';
import { validateNative, cases, prepareUpload, limit } from './windows-owned-image.mjs';
import { mkdtempSync, writeFileSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { buildCategories, parseBuildDiagnostic, formatFailure } from './windows-owned-image-diagnostics.mjs';
import * as diagnosticApi from './windows-owned-image-diagnostics.mjs';
import * as hostProfile from './windows-owned-image-host-profile.mjs';

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
  for (const category of buildCategories) {
    const tool = category === 'tool-signature' ? 'vswhere' : 'none';
    const condition = category === 'tool-signature' ? 'status-not-valid' : 'none';
    assert.deepEqual(parseBuildDiagnostic(`OWNED_IMAGE_BUILD\t3\t${category}\tnone\tnone\t0\t${tool}\t${condition}\n`),
      { category, code: 'none', source: 'none', line: 0, tool, condition });
  }
  assert.deepEqual(parseBuildDiagnostic('OWNED_IMAGE_BUILD\t3\tcompile\tC2065\tprobe\t123\tnone\tnone\r\n'),
    { category: 'compile', code: 'C2065', source: 'probe', line: 123, tool: 'none', condition: 'none' });
  assert.deepEqual(parseBuildDiagnostic('OWNED_IMAGE_BUILD\t3\tmissing-msvc\tnone\tnone\t0\tnone\tnone\n'),
    { category: 'missing-msvc', code: 'none', source: 'none', line: 0, tool: 'none', condition: 'none' });
});

test('path-bearing, forged, multiline and oversized build data is fully redacted', () => {
  for (const value of ['C:\\private\\tool.exe failed', 'OWNED_IMAGE_BUILD\t3\tC:\\private\tnone\tnone\t0\tnone\tnone\n',
    'OWNED_IMAGE_BUILD\t3\tcompile\tC2065: secret\tprobe\t123\tnone\tnone\n',
    'OWNED_IMAGE_BUILD\t3\tcompile\tC2065\tC:\\private.cpp\t123\tnone\tnone\n',
    'OWNED_IMAGE_BUILD\t3\tcompile\tC2065\tprobe\t999999\tnone\tnone\n',
    'OWNED_IMAGE_BUILD\t3\thost\tnone\tnone\t0\tnone\tnone\nsecret\n', 'x'.repeat(513),
    'OWNED_IMAGE_BUILD\t3\thost\tnone\tnone\t0\tnone\tnone\n\n',
    'OWNED_IMAGE_BUILD\t3\thost\tC2065\tprobe\t1\tnone\tnone\n',
    'OWNED_IMAGE_BUILD\t3\tcompile\tLNK2019\tprobe\t1\tnone\tnone\n',
    'OWNED_IMAGE_BUILD\t3\tcompile\tC2065\tprobe\t01\tnone\tnone\n'])
    assert.deepEqual(parseBuildDiagnostic(value), { category: 'unexpected', code: 'none', source: 'none', line: 0, tool: 'none', condition: 'none' });
});

test('driver failure output validates phase, finite case and fixed compiler fields again', () => {
  for (const category of ['launch', 'timeout', 'cap', 'interrupted'])
    assert.equal(formatFailure({ phase: 'build', category }),
      `Owned image native qualification failed phase=build case=none category=${category} code=none source=none line=0 tool=none condition=none\n`);
  assert.equal(formatFailure({ phase: 'case', name: 'fail-detach', category: 'native' }),
    'Owned image native qualification failed phase=case case=fail-detach category=native code=none source=none line=0 tool=none condition=none\n');
  assert.equal(formatFailure({ phase: 'build', ...parseBuildDiagnostic('OWNED_IMAGE_BUILD\t3\tcompile\tC2065\tprobe\t123\tnone\tnone\n') }),
    'Owned image native qualification failed phase=build case=none category=compile code=C2065 source=probe line=123 tool=none condition=none\n');
  for (const value of [{ phase: 'C:\\secret', name: 'positive', category: 'native' },
    { phase: 'case', name: 'positive\nsecret', category: 'native' },
    { phase: 'host', category: 'C:\\secret' }, { phase: 'pin', category: 'native' },
    { phase: ['host'], category: 'host' },
    { phase: 'build', category: 'compile', code: 'C2065\nsecret', source: 'probe', line: 4 },
    { phase: 'build', category: 'compile', code: 'C2065\n', source: 'probe', line: 4 },
    { phase: 'host', category: 'host', secret: 'C:\\private' }]) {
    const output = formatFailure(value);
    assert.equal(output, 'Owned image native qualification failed phase=unexpected case=none category=unexpected code=none source=none line=0 tool=none condition=none\n');
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
    assert.equal(result.stderr, 'Owned image native qualification failed phase=host case=none category=host code=none source=none line=0 tool=none condition=none\n');
    assert.deepEqual(readdirSync(root), []);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('signature-stage diagnostics identify only a closed tool role', () => {
  for (const tool of ['vswhere', 'compiler', 'linker']) {
    const parsed = parseBuildDiagnostic(`OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\t${tool}\tstatus-not-valid\n`);
    assert.deepEqual(parsed, { category: 'tool-signature', code: 'none', source: 'none', line: 0, tool, condition: 'status-not-valid' });
    assert.equal(formatFailure({ phase: 'build', ...parsed }),
      `Owned image native qualification failed phase=build case=none category=tool-signature code=none source=none line=0 tool=${tool} condition=status-not-valid\n`);
  }
});

test('tool roles reject forged phase, category, case and private values', () => {
  const unexpected = 'Owned image native qualification failed phase=unexpected case=none category=unexpected code=none source=none line=0 tool=none condition=none\n';
  for (const value of [{ phase: 'host', category: 'host', tool: 'compiler' },
    { phase: 'pin', category: 'pin', tool: 'linker' }, { phase: 'case', name: 'positive', category: 'native', tool: 'vswhere' },
    { phase: 'build', category: 'compile', tool: 'compiler' }, { phase: 'build', category: 'tool-signature', tool: 'none', condition: 'status-not-valid' },
    { phase: 'build', name: 'positive', category: 'tool-signature', tool: 'compiler', condition: 'status-not-valid' },
    { phase: 'build', category: 'tool-signature', tool: 'C:\\private\\cl.exe', condition: 'status-not-valid' },
    { phase: 'build', category: 'tool-signature', tool: 'compiler\nprivate', condition: 'status-not-valid' },
    { phase: 'build', category: 'tool-signature', tool: 'compiler\n', condition: 'status-not-valid' },
    { phase: 'build', category: 'tool-signature', tool: 'x'.repeat(513), condition: 'status-not-valid' },
    { phase: 'build', category: 'tool-signature', tool: ['compiler'], condition: 'status-not-valid' }])
    assert.equal(formatFailure(value), unexpected);
  for (const text of ['OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tnone\tstatus-not-valid\n',
    'OWNED_IMAGE_BUILD\t3\tcompile\tnone\tnone\t0\tcompiler\tnone\n',
    'OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tC:\\private\\cl.exe\tstatus-not-valid\n',
    'OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tcompiler\nprivate\tstatus-not-valid\n',
    'OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tcompiler\tstatus-not-valid\n\n',
    `OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\t${'x'.repeat(513)}\tstatus-not-valid\n`,
    'OWNED_IMAGE_BUILD\t1\ttool-signature\tnone\tnone\t0\n'])
    assert.deepEqual(parseBuildDiagnostic(text), { category: 'unexpected', code: 'none', source: 'none', line: 0, tool: 'none', condition: 'none' });
});

test('signature diagnostics expose only a closed rejection condition', () => {
  for (const tool of ['vswhere', 'compiler', 'linker']) {
    for (const condition of ['status-not-valid', 'signer-absent', 'subject-mismatch', 'api-failure']) {
      const parsed = parseBuildDiagnostic(`OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\t${tool}\t${condition}\n`);
      assert.deepEqual(parsed, { category: 'tool-signature', code: 'none', source: 'none', line: 0, tool, condition });
      assert.equal(formatFailure({ phase: 'build', ...parsed }),
        `Owned image native qualification failed phase=build case=none category=tool-signature code=none source=none line=0 tool=${tool} condition=${condition}\n`);
    }
  }
});

test('signature conditions reject forged context and private or malformed values', () => {
  const unexpected = 'Owned image native qualification failed phase=unexpected case=none category=unexpected code=none source=none line=0 tool=none condition=none\n';
  for (const value of [{ phase: 'host', category: 'host', condition: 'api-failure' },
    { phase: 'case', name: 'positive', category: 'native', condition: 'status-not-valid' },
    { phase: 'build', category: 'compile', condition: 'subject-mismatch' },
    { phase: 'build', name: 'positive', category: 'tool-signature', tool: 'vswhere', condition: 'status-not-valid' },
    { phase: 'build', category: 'tool-signature', tool: 'none', condition: 'status-not-valid' },
    { phase: 'build', category: 'tool-signature', tool: 'vswhere', condition: 'none' },
    { phase: 'build', category: 'tool-signature', tool: 'vswhere', condition: 'C:\\private\\certificate' },
    { phase: 'build', category: 'tool-signature', tool: 'vswhere', condition: 'status-not-valid\nprivate' },
    { phase: 'build', category: 'tool-signature', tool: 'vswhere', condition: 'status-not-valid\n' },
    { phase: 'build', category: 'tool-signature', tool: 'vswhere', condition: 'x'.repeat(513) },
    { phase: 'build', category: 'tool-signature', tool: 'vswhere', condition: ['api-failure'] }])
    assert.equal(formatFailure(value), unexpected);
  for (const text of ['OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tvswhere\tnone\n',
    'OWNED_IMAGE_BUILD\t3\thost\tnone\tnone\t0\tnone\tapi-failure\n',
    'OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tvswhere\tC:\\private\\certificate\n',
    'OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tvswhere\tapi-failure\nprivate\n',
    'OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tvswhere\tapi-failure\n\n',
    `OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tvswhere\t${'x'.repeat(513)}\n`,
    'OWNED_IMAGE_BUILD\t2\ttool-signature\tnone\tnone\t0\tvswhere\n'])
    assert.deepEqual(parseBuildDiagnostic(text), { category: 'unexpected', code: 'none', source: 'none', line: 0, tool: 'none', condition: 'none' });
});

test('query failure diagnostics distinguish only closed command and classification branches', () => {
  for (const condition of ['command-unavailable', 'parameter-binding', 'invocation-failure', 'classification-failure']) {
    const parsed = parseBuildDiagnostic(`OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tvswhere\t${condition}\n`);
    assert.deepEqual(parsed, { category: 'tool-signature', code: 'none', source: 'none', line: 0, tool: 'vswhere', condition });
    assert.equal(formatFailure({ phase: 'build', ...parsed }),
      `Owned image native qualification failed phase=build case=none category=tool-signature code=none source=none line=0 tool=vswhere condition=${condition}\n`);
  }
});

test('query branch diagnostics cannot disclose error names or escape signature-stage coherence', () => {
  const unexpected = 'Owned image native qualification failed phase=unexpected case=none category=unexpected code=none source=none line=0 tool=none condition=none\n';
  for (const condition of ['command-unavailable', 'parameter-binding', 'invocation-failure', 'classification-failure']) {
    for (const value of [{ phase: 'host', category: 'host', condition }, { phase: 'pin', category: 'pin', condition },
      { phase: 'case', name: 'positive', category: 'native', condition }, { phase: 'build', category: 'compile', condition },
      { phase: 'build', name: 'positive', category: 'tool-signature', tool: 'vswhere', condition }])
      assert.equal(formatFailure(value), unexpected);
  }
  for (const condition of ['System.Management.Automation.ParameterBindingException', 'C:\\private\\error',
    'parameter-binding\nprivate', 'invocation-failure\n', 'x'.repeat(513)]) {
    assert.equal(formatFailure({ phase: 'build', category: 'tool-signature', tool: 'vswhere', condition }), unexpected);
    assert.deepEqual(parseBuildDiagnostic(`OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tvswhere\t${condition}\n`),
      { category: 'unexpected', code: 'none', source: 'none', line: 0, tool: 'none', condition: 'none' });
  }
});

const moduleObservation = (condition = 'unresolved-command-unavailable', direct = 'not-imported') =>
  `OWNED_IMAGE_BUILD\t3\ttool-signature\tnone\tnone\t0\tvswhere\t${condition}\n` +
  `OWNED_IMAGE_MODULE\t1\tpresent\tpresent\tall\t${direct}\n`;

test('bounded module canary records only closed path/autoload/direct-command observations', () => {
  const result = diagnosticApi.parseBuildObservation(moduleObservation());
  assert.deepEqual(result, { category: 'tool-signature', code: 'none', source: 'none', line: 0, tool: 'vswhere',
    condition: 'unresolved-command-unavailable', module: { inbox: 'present', core: 'present', autoload: 'all', direct: 'not-imported' } });
  assert.equal(formatFailure({ phase: 'build', ...result }),
    'Owned image native qualification failed phase=build case=none category=tool-signature code=none source=none line=0 tool=vswhere condition=unresolved-command-unavailable inbox=present core=present autoload=all direct=not-imported\n');
  assert.equal(diagnosticApi.parseBuildObservation(moduleObservation('nested-command-unavailable', 'imported')).condition, 'nested-command-unavailable');
  assert.equal(diagnosticApi.parseBuildObservation(moduleObservation('command-probe-failure', 'unknown')).condition, 'command-probe-failure');
});

test('module canary rejects forged metadata, multiline/oversize data and inconsistent command attribution', () => {
  const unexpected = { category: 'unexpected', code: 'none', source: 'none', line: 0, tool: 'none', condition: 'none' };
  for (const text of [moduleObservation('nested-command-unavailable', 'not-imported'),
    moduleObservation('unresolved-command-unavailable', 'imported'), moduleObservation('command-probe-failure', 'imported'),
    moduleObservation().replace('present\tpresent', 'C:\\private\tpresent'), moduleObservation() + 'private\n',
    moduleObservation() + '\n', moduleObservation().replace('all\t', 'All\t'), 'x'.repeat(513),
    moduleObservation().replace('OWNED_IMAGE_MODULE', 'PRIVATE'), moduleObservation().replace('tool-signature', 'host')])
    assert.deepEqual(diagnosticApi.parseBuildObservation(text), unexpected);
  const value = diagnosticApi.parseBuildObservation(moduleObservation());
  for (const patch of [{ phase: 'host' }, { name: 'positive' }, { category: 'compile' },
    { module: { ...value.module, pid: 42 } }, { module: { ...value.module, inbox: 'C:\\private' } },
    { module: { ...value.module, direct: 'imported' } }])
    assert.equal(formatFailure({ phase: 'build', ...value, ...patch }),
      'Owned image native qualification failed phase=unexpected case=none category=unexpected code=none source=none line=0 tool=none condition=none\n');
});

const selectedWinPs = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe';
test('candidate child environment contains only the selected WinPS inbox module path', () => {
  const original = { SystemRoot: 'C:\\Windows', PATH: 'retained', PSModulePath: 'inherited-core', pSmOdUlEpAtH: 'inherited-user',
    WinPSModulePath: 'inherited-other', FACTORY_OWNED_IMAGE_INBOX: 'forged' };
  const environment = hostProfile.inboxEnvironment(original, selectedWinPs, selectedWinPs);
  assert.equal(environment.PSModulePath, 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\Modules');
  assert.equal(environment.FACTORY_OWNED_IMAGE_INBOX, environment.PSModulePath);
  assert.equal(environment.FACTORY_OWNED_IMAGE_PROFILE, 'winps-inbox-only');
  assert.equal(environment.PATH, 'retained');
  assert.deepEqual(Object.keys(environment).filter(key => key.toLowerCase() === 'psmodulepath'), ['PSModulePath']);
  assert.equal(Object.keys(environment).some(key => key.toLowerCase() === 'winpsmodulepath'), false);
  assert.equal(original.PSModulePath, 'inherited-core');
});

test('candidate environment refuses an alternate, relative or noncanonical host', () => {
  for (const host of ['powershell.exe', 'C:\\foreign\\powershell.exe', '\\\\remote\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
    'C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe'])
    assert.throws(() => hostProfile.inboxEnvironment({}, host, selectedWinPs), { message: 'host-profile' });
  for (const root of ['C:\\Win[1]', 'C:\\Win*', 'C:\\Win?', 'C:\\Win;other', 'C:\\Win\nprivate']) {
    const host = `${root}\\System32\\WindowsPowerShell\\v1.0\\powershell.exe`;
    assert.throws(() => hostProfile.inboxEnvironment({}, host, host), { message: 'host-profile' });
  }
});

test('host-profile facts expose only a coherent closed origin and availability result', () => {
  assert.deepEqual(hostProfile.parseProfile('OWNED_IMAGE_PROFILE\t2\twinps-inbox-only\tinbox\tavailable\tready\tnone\n'),
    { profile: 'winps-inbox-only', origin: 'inbox', availability: 'available', stage: 'ready', field: 'none' });
  for (const text of ['OWNED_IMAGE_PROFILE\t2\twinps-inbox-only\tinbox\tunavailable\tready\tnone\n',
    'OWNED_IMAGE_PROFILE\t2\twinps-inbox-only\tC:\\private\tavailable\tready\tnone\n',
    'OWNED_IMAGE_PROFILE\t2\twinps-inbox-only\tinbox\tavailable\tready\tnone\nprivate\n', 'x'.repeat(513)])
    assert.equal(hostProfile.parseProfile(text), null);
  assert.equal(hostProfile.formatProfile({ profile: 'winps-inbox-only', origin: 'inbox', availability: 'available', stage: 'ready', field: 'none' }),
    'Owned image host profile=winps-inbox-only origin=inbox availability=available stage=ready field=none\n');
  assert.equal(hostProfile.formatProfile({ profile: 'winps-inbox-only', origin: 'C:\\private', availability: 'available' }),
    'Owned image host profile=winps-inbox-only origin=unverified availability=unavailable stage=unknown field=unknown\n');
});

const profileStageRow = (origin, availability, stage, field) =>
  `OWNED_IMAGE_PROFILE\t2\twinps-inbox-only\t${origin}\t${availability}\t${stage}\t${field}\n`;
test('profile initialization diagnostics identify only coherent fixed stages and current checks', () => {
  const checks = { environment: ['path', 'profile', 'inbox', 'assignment', 'reparse'],
    'management-import': ['manifest', 'reparse', 'import'], 'utility-import': ['manifest', 'reparse', 'import'],
    'security-import': ['manifest', 'reparse', 'import'], 'management-origin': ['count', 'name', 'manifest', 'base'],
    'utility-origin': ['count', 'name', 'manifest', 'base'], 'security-origin': ['count', 'name', 'manifest', 'base'],
    'cmdlet-resolution': ['resolution', 'count'], 'cmdlet-origin': ['path', 'cmdlet-name', 'cmdlet-type', 'module-name', 'manifest', 'base'] };
  for (const [stage, fields] of Object.entries(checks)) for (const field of fields) {
    const availability = stage === 'cmdlet-origin' ? 'available' : 'unavailable';
    const origin = stage === 'cmdlet-origin' ? 'refused' : 'unverified';
    const value = { profile: 'winps-inbox-only', origin, availability, stage, field };
    assert.deepEqual(hostProfile.parseProfile(profileStageRow(origin, availability, stage, field)), value);
    assert.equal(hostProfile.formatProfile(value),
      `Owned image host profile=winps-inbox-only origin=${origin} availability=${availability} stage=${stage} field=${field}\n`);
  }
  assert.equal(hostProfile.parseProfile(profileStageRow('refused', 'unavailable', 'security-origin', 'manifest')).field, 'manifest');
});

test('profile stage projection refuses forged context, paths, extra keys, multiline and oversized input', () => {
  const fallback = 'Owned image host profile=winps-inbox-only origin=unverified availability=unavailable stage=unknown field=unknown\n';
  const good = { profile: 'winps-inbox-only', origin: 'refused', availability: 'unavailable', stage: 'security-origin', field: 'manifest' };
  for (const patch of [{ stage: 'ready' }, { field: 'cmdlet-type' }, { availability: 'available' },
    { origin: 'inbox' }, { stage: 'C:\\private' }, { stage: ['security-origin'] }, { field: ['manifest'] },
    { field: 'manifest\nprivate' }, { field: 'x'.repeat(513) }, { private: 'value' }])
    assert.equal(hostProfile.formatProfile({ ...good, ...patch }), fallback);
  for (const text of [profileStageRow('inbox', 'available', 'security-import', 'import'),
    profileStageRow('refused', 'unavailable', 'cmdlet-origin', 'manifest'),
    profileStageRow('refused', 'unavailable', 'security-origin', 'cmdlet-type'),
    profileStageRow('refused', 'unavailable', 'C:\\private', 'manifest'),
    profileStageRow('refused', 'unavailable', 'security-origin', 'manifest\nprivate'),
    profileStageRow('refused', 'unavailable', 'security-origin', 'manifest') + '\n',
    'OWNED_IMAGE_PROFILE\t1\twinps-inbox-only\tinbox\tavailable\n', 'x'.repeat(513)])
    assert.equal(hostProfile.parseProfile(text), null);
});

const relationContext = { profile: 'winps-inbox-only', origin: 'refused', availability: 'unavailable', stage: 'management-origin', field: 'base' };
const relationWire = relation => profileStageRow('refused', 'unavailable', 'management-origin', 'base') +
  `OWNED_IMAGE_RELATION\t1\t${relation.kind}\t${relation.base}\t${relation.path}\t${relation.baseType}\n`;
test('Management base refusal exposes only exact closed module metadata relations', () => {
  for (const kind of ['manifest', 'binary', 'script', 'unknown'])
    for (const base of ['selected-manifest-directory', 'selected-WinPS-host-directory', 'inbox-root', 'other'])
      for (const path of ['exact-selected-manifest', 'known-fixed-Management-binary-under-selected-host', 'other']) {
        const relation = { kind, base, path, baseType: 'string' };
        assert.ok(Buffer.byteLength(relationWire(relation)) <= 512);
        assert.deepEqual(hostProfile.parseProfile(relationWire(relation)), { ...relationContext, relation });
        assert.equal(hostProfile.formatProfile({ ...relationContext, relation }),
          `Owned image host profile=winps-inbox-only origin=refused availability=unavailable stage=management-origin field=base kind=${kind} base=${base} path=${path} baseType=string\n`);
      }
  for (const baseType of ['null', 'single-string-array', 'other']) {
    const relation = { kind: 'unknown', base: 'other', path: 'other', baseType };
    assert.deepEqual(hostProfile.parseProfile(relationWire(relation)), { ...relationContext, relation });
  }
});

test('Management metadata relations reject foreign contexts, raw values and malformed framing', () => {
  const relation = { kind: 'binary', base: 'selected-WinPS-host-directory', path: 'exact-selected-manifest', baseType: 'string' };
  const value = { ...relationContext, relation };
  const fallback = 'Owned image host profile=winps-inbox-only origin=unverified availability=unavailable stage=unknown field=unknown\n';
  for (const patch of [{ stage: 'security-origin' }, { field: 'manifest' }, { origin: 'unverified' }, { availability: 'available' },
    { relation: { ...relation, kind: 'C:\\private' } }, { relation: { ...relation, base: 'other\nprivate' } },
    { relation: { ...relation, path: 'x'.repeat(513) } }, { relation: { ...relation, kind: ['binary'] } },
    { relation: { ...relation, baseType: 'null' } }, { relation: { ...relation, baseType: 'C:\\private' } },
    { relation: { ...relation, baseType: ['string'] } },
    { relation: { ...relation, extra: 'private' } }, { relation: ['binary', 'other', 'other'] }])
    assert.equal(hostProfile.formatProfile({ ...value, ...patch }), fallback);
  assert.equal(hostProfile.formatProfile(Object.assign(Object.create({ relation: { kind: 'private', base: 'private', path: 'private' } }), relationContext)), fallback);
  const wire = relationWire(relation);
  for (const text of [wire.replace('management-origin', 'utility-origin'), wire.replace('\tbase\n', '\tmanifest\n'),
    wire.replace('refused', 'unverified'), wire.replace('RELATION\t1', 'RELATION\t2'),
    wire.replace('\tbinary\t', '\tC:\\private\t'), wire + '\n', wire + 'private\n',
    wire.replace('exact-selected-manifest', 'exact-selected-manifest\nprivate'), 'x'.repeat(513)])
    assert.equal(hostProfile.parseProfile(text), null);
});

test('fixed-origin candidate exposes capture and kind refusals only at fixed module origin stages', () => {
  for (const stage of ['management-origin', 'utility-origin', 'security-origin']) for (const field of ['capture', 'kind']) {
    const value = { profile: 'winps-inbox-only', origin: 'refused', availability: 'unavailable', stage, field };
    assert.deepEqual(hostProfile.parseProfile(profileStageRow('refused', 'unavailable', stage, field)), value);
    assert.equal(hostProfile.formatProfile(value),
      `Owned image host profile=winps-inbox-only origin=refused availability=unavailable stage=${stage} field=${field}\n`);
  }
  for (const stage of ['environment', 'management-import', 'cmdlet-origin', 'ready'])
    assert.equal(hostProfile.parseProfile(profileStageRow('refused', 'unavailable', stage, 'kind')), null);
});

test('Security authority and captured cmdlet failures remain finite and context coherent', () => {
  for (const field of ['capture', 'authority', 'module-kind']) {
    const value = { profile: 'winps-inbox-only', origin: 'refused', availability: 'available', stage: 'cmdlet-origin', field };
    assert.deepEqual(hostProfile.parseProfile(profileStageRow('refused', 'available', 'cmdlet-origin', field)), value);
    assert.equal(hostProfile.formatProfile(value),
      `Owned image host profile=winps-inbox-only origin=refused availability=available stage=cmdlet-origin field=${field}\n`);
  }
  assert.equal(hostProfile.parseProfile(profileStageRow('refused', 'unavailable', 'security-origin', 'authority')).field, 'authority');
  for (const stage of ['environment', 'management-origin', 'utility-origin', 'cmdlet-resolution'])
    assert.equal(hostProfile.parseProfile(profileStageRow('refused', 'unavailable', stage, 'authority')), null);
});

test('owned transport preserves real Node argv, exitCode and separate output contract', async () => {
  const { runOwnedImageTransport } = await import('./windows-owned-image-transport.mjs');
  const active = [];
  const args = ['owned root [literal]', 'positive', 'owned details [literal]'];
  const result = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stdout.write(JSON.stringify(process.argv.slice(1))); process.stderr.write("synthetic-private"); process.exitCode=7', ...args],
    4096, 2000, child => active.push(child === null ? 'closed' : 'started'));
  assert.deepEqual(JSON.parse(result.stdout), args);
  assert.equal(result.exitCode, 7); assert.equal(Object.hasOwn(result, 'statusCode'), false);
  assert.equal(result.signal, null); assert.equal(result.stderr, 'synthetic-private');
  assert.equal(result.capped, false); assert.equal(result.timedOut, false);
  assert.deepEqual(active, ['started', 'closed']);
  const normal = await runOwnedImageTransport(process.execPath, ['-e', 'process.stdout.write("owned")'], 4096, 2000);
  assert.equal(normal.exitCode, 0); assert.equal(normal.stdout, 'owned'); assert.equal(normal.stderr, '');
});

test('owned transport retains its output cap and deadline refusal controls', async () => {
  const { runOwnedImageTransport } = await import('./windows-owned-image-transport.mjs');
  const capped = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stdout.write(Buffer.alloc(8192,65)); setInterval(()=>{},1000)'], 128, 2000);
  assert.equal(capped.capped, true); assert.ok(Buffer.byteLength(capped.stdout) <= 128);
  const timed = await runOwnedImageTransport(process.execPath, ['-e', 'setInterval(()=>{},1000)'], 4096, 700);
  assert.equal(timed.timedOut, true); assert.equal(timed.capped, false);
});

test('native outcome projects only bounded exit presence/status and stderr flags', () => {
  for (const status of [-2147483648, -1, 0, 1, 2, 2147483647, 2147483648, 4294967295]) {
    const result = diagnosticApi.nativeOutcome({ exitCode: status, stderr: 'synthetic-private' });
    assert.deepEqual(result, { exit: 'present', status, stderr: 'nonempty' });
    assert.equal(formatFailure({ phase: 'case', name: 'positive', category: 'native', native: result }),
      `Owned image native qualification failed phase=case case=positive category=native code=none source=none line=0 tool=none condition=none exit=present status=${status} stderr=nonempty\n`);
  }
  assert.deepEqual(diagnosticApi.nativeOutcome({ stderr: '' }), { exit: 'absent', status: 'none', stderr: 'empty' });
  assert.deepEqual(diagnosticApi.nativeOutcome({ exitCode: null, stderr: '' }), { exit: 'null', status: 'none', stderr: 'empty' });
  for (const exit of ['absent', 'null'])
    assert.equal(formatFailure({ phase: 'case', name: 'positive', category: 'native', native: { exit, status: 'none', stderr: 'empty' } }),
      `Owned image native qualification failed phase=case case=positive category=native code=none source=none line=0 tool=none condition=none exit=${exit} status=none stderr=empty\n`);
});

test('native outcome rejects raw values, forged status/context and contradictory success flags', () => {
  const unexpected = 'Owned image native qualification failed phase=unexpected case=none category=unexpected code=none source=none line=0 tool=none condition=none\n';
  for (const result of [{ exitCode: -2147483649, stderr: '' }, { exitCode: 4294967296, stderr: '' },
    { exitCode: '1', stderr: '' }, { exitCode: 1.5, stderr: '' }, { exitCode: NaN, stderr: '' },
    { exitCode: [], stderr: '' }, { exitCode: 1, stderr: ['private'] }, { exitCode: 1, stderr: 'x'.repeat(limit + 1) }])
    assert.equal(diagnosticApi.nativeOutcome(result), null);
  const native = { exit: 'present', status: 1, stderr: 'empty' };
  for (const patch of [{ phase: 'build' }, { category: 'receipt' }, { category: 'timeout' },
    { native: { ...native, status: 'C:\\private' } }, { native: { ...native, exit: 'present\nprivate' } },
    { native: { ...native, status: 4294967296 } }, { native: { ...native, stderr: 'private' } },
    { native: { ...native, exit: 'absent' } }, { native: { ...native, status: 0 } },
    { native: { ...native, extra: 'private' } }])
    assert.equal(formatFailure({ phase: 'case', name: 'positive', category: 'native', native, ...patch }), unexpected);
  let statusReads = 0;
  const changing = { exit: 'present', stderr: 'empty', get status() { return ++statusReads < 5 ? 1 : 'C:\\private'; } };
  assert.equal(formatFailure({ phase: 'case', name: 'positive', category: 'native', native: changing }), unexpected);
  assert.equal(diagnosticApi.nativeOutcome({ get exitCode() { return 1; }, stderr: '' }), null);
});

test('owned exit-one child exposes a fixed caught condition separately from terminal refusal', async () => {
  const { runOwnedImageTransport } = await import('./windows-owned-image-transport.mjs');
  const wire = 'OWNED_IMAGE_REFUSAL\t1\tpositive\tsurvival-ready\thost-check\t1\t0\t1\t1\n';
  const result = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stdout.write("synthetic-private-receipt"); process.stderr.write(process.argv[1]); process.exitCode=1', wire], 4096, 2000);
  assert.equal(result.exitCode, 1);
  const refusal = diagnosticApi.parseNativeRefusal(result, 'positive');
  assert.deepEqual(refusal, { phase: 'survival-ready', reason: 'host-check', cleanup: true, survival: false, flush: true, close: true });
  assert.equal(formatFailure({ phase: 'case', name: 'positive', category: 'native', native: diagnosticApi.nativeOutcome(result), refusal }),
    'Owned image native qualification failed phase=case case=positive category=native code=none source=none line=0 tool=none condition=none exit=present status=1 stderr=nonempty nativePhase=survival-ready nativeReason=host-check cleanup=true survival=false flush=true close=true\n');
});

const refusalWire = (name = 'positive', phase = 'probe', reason = 'query-check', bits = '0\t1\t1\t1') =>
  `OWNED_IMAGE_REFUSAL\t1\t${name}\t${phase}\t${reason}\t${bits}\n`;
const refusalResult = stderr => ({ exitCode: 1, signal: null, capped: false, timedOut: false, stderr });

test('refusal wire rejects contradictory phases and forged accessor or inherited observations', () => {
  const valid = { phase: 'probe', reason: 'query-check', cleanup: false, survival: true, flush: true, close: true };
  const context = { phase: 'case', name: 'positive', category: 'native', native: { exit: 'present', status: 1, stderr: 'nonempty' }, refusal: valid };
  const unexpected = formatFailure({ phase: 'unexpected' });
  let reads = 0;
  const accessor = { ...context };
  Object.defineProperty(accessor, 'refusal', { enumerable: true, get() { reads++; return valid; } });
  assert.equal(formatFailure(accessor), unexpected);
  assert.equal(reads, 0);
  const inherited = Object.assign(Object.create({ refusal: valid }), context);
  delete inherited.refusal;
  assert.equal(formatFailure(inherited), unexpected);
  const symbol = { ...valid, [Symbol('private')]: 'private' };
  for (const refusal of [symbol, { ...valid, phase: 'owner-interruption', reason: 'owner-interrupted' },
    { ...valid, phase: 'survival-ready' }, { ...valid, cleanup: true }, { ...valid, reason: 'C:\\private' },
    { ...valid, extra: 'private' }, { ...valid, get reason() { reads++; return 'query-check'; } }])
    assert.equal(formatFailure({ ...context, refusal }), unexpected);
  assert.equal(reads, 0);
  assert.equal(diagnosticApi.parseNativeRefusal(refusalResult(refusalWire('positive', 'owner-interruption', 'owner-interrupted')), 'positive'), null);
  assert.equal(diagnosticApi.parseNativeRefusal(refusalResult(refusalWire('owner-interruption')), 'owner-interruption'), null);
});

test('refusal wire accepts only one bounded exact case record in an uninterrupted exit-one context', () => {
  const wire = refusalWire();
  const expected = { phase: 'probe', reason: 'query-check', cleanup: false, survival: true, flush: true, close: true };
  assert.deepEqual(diagnosticApi.parseNativeRefusal(refusalResult(wire.replaceAll('\n', '\r\n')), 'positive'), expected);
  for (const text of ['', wire.trimEnd(), wire + wire, wire + '\n', 'private\n' + wire, wire + 'private\n',
    wire.replace('REFUSAL\t1', 'REFUSAL\t2'), wire.replace('positive', 'positive-repeat'),
    wire.replace('query-check', 'C:\\private'), wire.replace('query-check', 'query-check\nprivate'),
    wire.replace('\t0\t1\t1\t1\n', '\t1\t1\t1\t1\n'), wire.replace('\t0\t1\t1\t1\n', '\tfalse\t1\t1\t1\n'),
    wire.replace('\tprobe\t', '\tunknown\t'), wire.replace('\tprobe\t', '\tnone\t'), 'x'.repeat(513)])
    assert.equal(diagnosticApi.parseNativeRefusal(refusalResult(text), 'positive'), null);
  for (const patch of [{ exitCode: 0 }, { exitCode: 2 }, { exitCode: null }, { exitCode: '1' },
    { signal: 'SIGTERM' }, { signal: undefined }, { capped: true }, { timedOut: true }, { capped: 0 }, { stderr: [wire] }])
    assert.equal(diagnosticApi.parseNativeRefusal({ ...refusalResult(wire), ...patch }, 'positive'), null);
  const inherited = Object.create(refusalResult(wire));
  assert.equal(diagnosticApi.parseNativeRefusal(inherited, 'positive'), null);
  let reads = 0;
  for (const key of ['exitCode', 'signal', 'capped', 'timedOut', 'stderr']) {
    const result = refusalResult(wire);
    Object.defineProperty(result, key, { enumerable: true, get() { reads++; return refusalResult(wire)[key]; } });
    assert.equal(diagnosticApi.parseNativeRefusal(result, 'positive'), null);
  }
  assert.equal(reads, 0);
});

test('terminal-only refusal stays distinct from a caught probe condition and cannot imply admission', () => {
  for (const [phase, reason, name] of [['none', 'clear', 'positive'], ['probe', 'identity-check', 'wrong-hash'],
    ['owner-interruption', 'owner-interrupted', 'owner-interruption'], ['output-check', 'pipe-check', 'positive']]) {
    for (let mask = 0; mask < 15; mask++) {
      const bits = [8, 4, 2, 1].map(bit => mask & bit ? '1' : '0').join('\t');
      const refusal = diagnosticApi.parseNativeRefusal(refusalResult(refusalWire(name, phase, reason, bits)), name);
      assert.equal(refusal?.phase, phase); assert.equal(refusal?.reason, reason);
      assert.equal(validateNative(refusalWire(name, phase, reason, bits), name).qualified, false);
      assert.equal(validateNative(refusalWire(name, phase, reason, bits), name).helperAdmission, 'refused');
    }
  }
  const native = { exit: 'present', status: 1, stderr: 'empty' };
  assert.equal(formatFailure({ phase: 'case', name: 'positive', category: 'native', native, refusal: null }),
    'Owned image native qualification failed phase=case case=positive category=native code=none source=none line=0 tool=none condition=none exit=present status=1 stderr=empty nativePhase=unknown nativeReason=unknown cleanup=unknown survival=unknown flush=unknown close=unknown\n');
  const refusal = diagnosticApi.parseNativeRefusal(refusalResult(refusalWire()), 'positive');
  const unexpected = formatFailure({ phase: 'unexpected' });
  for (const patch of [{ phase: 'build' }, { category: 'receipt' }, { name: 'owner-interruption' },
    { native: { ...native, stderr: 'nonempty', status: 2 } }, { native: { ...native, status: 0 } },
    { native: { ...native, exit: 'null', status: 'none' } }, { native: undefined }])
    assert.equal(formatFailure({ phase: 'case', name: 'positive', category: 'native', native, refusal, ...patch }), unexpected);
});

test('owned child transport never promotes a success, mixed record, cap or deadline to native refusal facts', async () => {
  const { runOwnedImageTransport } = await import('./windows-owned-image-transport.mjs');
  const wire = refusalWire();
  for (const [status, output] of [[0, ''], [0, wire], [2, wire], [1, wire + 'synthetic-private\n'], [1, wire + wire]]) {
    const result = await runOwnedImageTransport(process.execPath,
      ['-e', 'process.stderr.write(process.argv[1]); process.exitCode=Number(process.argv[2])', output, String(status)], 4096, 2000);
    assert.equal(result.exitCode, status);
    assert.equal(diagnosticApi.parseNativeRefusal(result, 'positive'), null);
  }
  const capped = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stderr.write(process.argv[1]); process.stdout.write(Buffer.alloc(8192,65)); setInterval(()=>{},1000)', wire], 128, 2000);
  assert.equal(capped.capped, true);
  assert.equal(diagnosticApi.parseNativeRefusal(capped, 'positive'), null);
  const timed = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stderr.write(process.argv[1]); setInterval(()=>{},1000)', wire], 4096, 700);
  assert.equal(timed.timedOut, true);
  assert.equal(diagnosticApi.parseNativeRefusal(timed, 'positive'), null);
});

const stopFacts = (patch = {}) => ({ Process: true, Stop: true, InitialWait: true, Termination: 'not-reached',
  DebugWait: 'not-reached', EventOwner: 'not-reached', EventClose: 'not-reached', Continue: 'not-reached', DebugExit: 'not-reached',
  FinalWait: true, OutputEof: true, ErrorEof: true, OutputValid: true, ErrorValid: true, ...patch });
const cleanupFacts = (patch = {}) => ({
  ...Object.fromEntries(Object.entries(stopFacts()).map(([key, value]) => ['child' + key, value])),
  ...Object.fromEntries(Object.entries(stopFacts()).map(([key, value]) => ['control' + key, value])),
  exitQuery: true, exitInactive: true, earlyClear: true, rejectedClear: 'not-reached', ownedZero: true,
  countQuery: true, countNonincrease: false, leakedZero: false, closeCalls: true, closeIdentity: true, closeQuery: true, closed: true,
  ownedClose: true, mappingClose: true, debugClose: true, hashClose: true, algorithmClose: true, ownerFileClose: 'not-reached',
  ...patch,
});
const cleanupWire = (facts = cleanupFacts(), name = 'positive') =>
  `OWNED_IMAGE_CLEANUP\t1\t${name}\t${Object.values(facts).map(value => value === true ? '1' : value === false ? '0' : 'n').join('\t')}\n`;

test('owned exit-one cleanup record exposes every fixed terminal contributor without raw counts', async () => {
  const { runOwnedImageTransport } = await import('./windows-owned-image-transport.mjs');
  const wire = refusalWire('positive', 'none', 'clear') + cleanupWire();
  const result = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stdout.write("synthetic-private-counts"); process.stderr.write(process.argv[1]); process.exitCode=1', wire], 4096, 2000);
  assert.equal(result.exitCode, 1);
  const refusal = diagnosticApi.parseNativeRefusal(result, 'positive');
  assert.deepEqual(refusal, { phase: 'none', reason: 'clear', cleanup: false, survival: true, flush: true, close: true });
  const cleanupEvidence = diagnosticApi.parseNativeCleanup(result, 'positive');
  assert.deepEqual(cleanupEvidence, cleanupFacts());
  const formatted = formatFailure({ phase: 'case', name: 'positive', category: 'native', native: diagnosticApi.nativeOutcome(result), refusal, cleanupEvidence });
  assert.ok(formatted.includes('nativePhase=none nativeReason=clear cleanup=false'));
  assert.ok(formatted.includes('childStop=true'));
  assert.ok(formatted.includes('countQuery=true countNonincrease=false leakedZero=false'));
  assert.equal(formatted.includes('synthetic-private'), false);
  assert.equal(validateNative(wire, 'positive').qualified, false);
});

test('cleanup evidence rejects a claimed rejected-marker check after a clear positive probe', () => {
  const facts = cleanupFacts({ rejectedClear: false, countNonincrease: true, leakedZero: 'not-reached' });
  const result = refusalResult(refusalWire('positive', 'none', 'clear') + cleanupWire(facts));
  assert.equal(diagnosticApi.parseNativeRefusal(result, 'positive'), null);
  assert.equal(diagnosticApi.parseNativeCleanup(result, 'positive'), null);
});

test('cleanup phase cannot claim a completed positive probe without an owned child', () => {
  const absent = Object.fromEntries(Object.entries(stopFacts({ Process: false })).map(([key]) => ['child' + key,
    key === 'Process' ? false : key === 'Stop' ? true : 'not-reached']));
  const facts = cleanupFacts({ ...absent, exitQuery: 'not-reached', exitInactive: 'not-reached', earlyClear: 'not-reached' });
  const result = refusalResult(refusalWire('positive', 'none', 'clear') + cleanupWire(facts));
  assert.equal(diagnosticApi.parseNativeRefusal(result, 'positive'), null);
  assert.equal(diagnosticApi.parseNativeCleanup(result, 'positive'), null);
});

test('cleanup protocol reports each Stop refusal category and every terminal conjunction contributor', () => {
  const clear = cleanupFacts({ countNonincrease: true, leakedZero: true });
  for (const prefix of ['child', 'control']) {
    for (const key of ['InitialWait', 'Termination', 'DebugWait', 'EventOwner', 'EventClose', 'Continue', 'DebugExit',
      'FinalWait', 'OutputEof', 'ErrorEof', 'OutputValid', 'ErrorValid']) {
      const debug = ['DebugWait', 'EventOwner', 'EventClose', 'Continue', 'DebugExit'].includes(key);
      const facts = { ...clear, [prefix + 'Stop']: false, [prefix + key]: false, leakedZero: 'not-reached',
        ...(debug ? { [prefix + 'DebugExit']: key === 'DebugExit' || key === 'Continue' || key === 'EventOwner' ? false : true } : {}) };
      const result = refusalResult(refusalWire('positive', 'none', 'clear') + cleanupWire(facts));
      assert.deepEqual(diagnosticApi.parseNativeCleanup(result, 'positive'), facts, prefix + key);
      const text = formatFailure({ phase: 'case', name: 'positive', category: 'native', native: diagnosticApi.nativeOutcome(result),
        refusal: diagnosticApi.parseNativeRefusal(result, 'positive'), cleanupEvidence: facts });
      assert.ok(text.includes(prefix + key + '=false'), key);
    }
  }
  for (const patch of [{ exitQuery: false, exitInactive: 'not-reached' }, { exitInactive: false }, { earlyClear: false },
    { ownedZero: false, leakedZero: false }, { countNonincrease: false, leakedZero: false },
    { countQuery: false, countNonincrease: 'not-reached', closed: false },
    { closeCalls: false, ownedClose: false, closed: false }, { closeIdentity: false, closed: false }, { closeQuery: false, closed: false }]) {
    const facts = { ...clear, leakedZero: 'not-reached', ...patch };
    const result = refusalResult(refusalWire('positive', 'none', 'clear') + cleanupWire(facts));
    assert.deepEqual(diagnosticApi.parseNativeCleanup(result, 'positive'), facts, JSON.stringify(patch));
  }
  const rejected = { ...clear, rejectedClear: false, leakedZero: 'not-reached' };
  const result = refusalResult(refusalWire('positive', 'probe', 'query-check') + cleanupWire(rejected));
  assert.deepEqual(diagnosticApi.parseNativeCleanup(result, 'positive'), rejected);
  const notCreated = { ...cleanupFacts(), ...Object.fromEntries(Object.keys(stopFacts()).map(key => ['child' + key,
    key === 'Process' ? false : key === 'Stop' ? true : 'not-reached'])),
    exitQuery: 'not-reached', exitInactive: 'not-reached', earlyClear: 'not-reached' };
  assert.deepEqual(diagnosticApi.parseNativeCleanup(refusalResult(refusalWire('positive', 'probe', 'identity-check') + cleanupWire(notCreated)), 'positive'), notCreated);
});

test('cleanup records reject contradictory, raw, incomplete or accessor-backed evidence atomically', () => {
  const wire = refusalWire('positive', 'none', 'clear') + cleanupWire();
  const context = { phase: 'case', name: 'positive', category: 'native', native: { exit: 'present', status: 1, stderr: 'nonempty' },
    refusal: { phase: 'none', reason: 'clear', cleanup: false, survival: true, flush: true, close: true }, cleanupEvidence: cleanupFacts() };
  const unexpected = formatFailure({ phase: 'unexpected' });
  for (const patch of [{ childStop: false }, { controlProcess: false }, { childProcess: 'not-reached' },
    { countQuery: false }, { countNonincrease: 'not-reached' }, { ownedZero: false, leakedZero: true }, { closed: false },
    { closeCalls: false }, { closeIdentity: false }, { closeQuery: 'not-reached' }, { exitQuery: false },
    { childInitialWait: false }, { childDebugWait: false }, { childOutputEof: false }, { childEventClose: 'C:\\private' },
    { childTermination: ['not-reached'] }, { extra: 'private' }]) {
    const cleanupEvidence = { ...cleanupFacts(), ...patch };
    assert.equal(formatFailure({ ...context, cleanupEvidence }), unexpected, JSON.stringify(patch));
  }
  let reads = 0;
  const getter = { ...cleanupFacts(), get childStop() { reads++; return true; } };
  assert.equal(formatFailure({ ...context, cleanupEvidence: getter }), unexpected);
  const getterContext = { ...context, get cleanupEvidence() { reads++; return cleanupFacts(); } };
  assert.equal(formatFailure(getterContext), unexpected);
  assert.equal(reads, 0);
  for (const cleanupEvidence of [Object.create(cleanupFacts()), { ...cleanupFacts(), [Symbol('private')]: 'private' }])
    assert.equal(formatFailure({ ...context, cleanupEvidence }), unexpected);
  for (const bad of [wire.trimEnd(), wire + '\n', wire + cleanupWire(), cleanupWire(), cleanupWire() + refusalWire(),
    wire.replace('CLEANUP\t1', 'CLEANUP\t2'), wire.replace('CLEANUP\t1\tpositive', 'CLEANUP\t1\tpositive-repeat'),
    refusalWire('positive', 'none', 'clear') + cleanupWire(cleanupFacts({ countNonincrease: true, leakedZero: true })),
    wire.replace('CLEANUP', 'C:\\private'), wire.replace(/\tn\t/, '\tunknown\t'), wire + 'private\n', 'x'.repeat(513)]) {
    const result = refusalResult(bad);
    assert.equal(diagnosticApi.parseNativeRefusal(result, 'positive'), null, bad);
    assert.equal(diagnosticApi.parseNativeCleanup(result, 'positive'), null, bad);
  }
  for (const patch of [{ phase: 'build' }, { category: 'receipt' }, { name: 'owner-interruption' },
    { native: { ...context.native, status: 0 } }, { native: { ...context.native, stderr: 'empty' } },
    { refusal: { ...context.refusal, cleanup: true, survival: false } }, { refusal: null }, { refusal: undefined }])
    assert.equal(formatFailure({ ...context, ...patch }), unexpected);
  assert.ok(formatFailure({ ...context, cleanupEvidence: null }).endsWith(' cleanupEvidence=unknown\n'));
  assert.equal(diagnosticApi.parseNativeCleanup(refusalResult(refusalWire('positive', 'none', 'clear')), 'positive'), null);
});

test('owned cleanup transport retains exit, cap, deadline and artifact refusal despite a valid record prefix', async () => {
  const { runOwnedImageTransport } = await import('./windows-owned-image-transport.mjs');
  const wire = refusalWire('positive', 'none', 'clear') + cleanupWire();
  for (const [status, output] of [[0, wire], [2, wire], [1, wire + 'synthetic-private\n'], [1, wire.trimEnd()]]) {
    const result = await runOwnedImageTransport(process.execPath,
      ['-e', 'process.stderr.write(process.argv[1]); process.exitCode=Number(process.argv[2])', output, String(status)], 4096, 2000);
    assert.equal(result.exitCode, status);
    assert.equal(diagnosticApi.parseNativeCleanup(result, 'positive'), null);
    assert.equal(diagnosticApi.parseNativeRefusal(result, 'positive'), null);
    assert.equal(validateNative(result.stderr, 'positive').qualified, false);
  }
  const capped = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stderr.write(process.argv[1]); process.stdout.write(Buffer.alloc(8192,65)); setInterval(()=>{},1000)', wire], 512, 2000);
  assert.equal(capped.capped, true);
  assert.equal(diagnosticApi.parseNativeCleanup(capped, 'positive'), null);
  const timed = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stderr.write(process.argv[1]); setInterval(()=>{},1000)', wire], 4096, 700);
  assert.equal(timed.timedOut, true);
  assert.equal(diagnosticApi.parseNativeCleanup(timed, 'positive'), null);
});

test('cleanup evidence separates every original checked-close call category', () => {
  for (const category of ['ownedClose', 'mappingClose', 'debugClose', 'hashClose', 'algorithmClose', 'ownerFileClose']) {
    const owner = category === 'ownerFileClose';
    const name = owner ? 'owner-interruption' : 'positive';
    const facts = cleanupFacts({ [category]: false, closeCalls: false, closed: false, leakedZero: 'not-reached',
      ...(owner ? { rejectedClear: true } : {}) });
    const result = refusalResult(refusalWire(name, owner ? 'owner-interruption' : 'none', owner ? 'owner-interrupted' : 'clear') + cleanupWire(facts, name));
    assert.deepEqual(diagnosticApi.parseNativeCleanup(result, name), facts, category);
  }
});

test('cleanup close categories require the source owner and retired-handle checks to have been reached', () => {
  for (const facts of [cleanupFacts({ ownerFileClose: false, closeCalls: false, closed: false, leakedZero: 'not-reached' }),
    cleanupFacts({ debugClose: false, closeCalls: false, closeIdentity: 'not-reached', closeQuery: 'not-reached', closed: false, leakedZero: 'not-reached' })]) {
    const result = refusalResult(refusalWire('positive', 'none', 'clear') + cleanupWire(facts));
    assert.equal(diagnosticApi.parseNativeDiagnostic(result, 'positive'), null);
  }
});

const handlePhaseFacts = (patch = {}) => ({ entryOutput: 'equal', controlReady: 'above', pinHashEnter: 'above', pinHashLeave: 'above',
  debugCreateEnter: 'above', debugCreateLeave: 'above', firstEvent: 'above', imageHashEnter: 'above', imageHashLeave: 'above',
  continued: 'above', detached: 'above', probeReturn: 'above', childStopped: 'above', controlStopped: 'above', childReleased: 'above',
  final: 'above', pinHash: 'equal', imageHash: 'equal', targetScope: 'above', profileRest: 'above', ...patch });
const handlePhaseWire = (facts = handlePhaseFacts(), name = 'positive') => {
  const tokens = { below: 'b', equal: 'e', above: 'a', 'query-failed': 'f', 'not-reached': 'n', unavailable: 'u' };
  return `OWNED_IMAGE_HANDLE_PHASES\t1\t${name}\t${Object.values(facts).map(value => tokens[value]).join('\t')}\n`;
};

test('owned count-increase child exposes only the accepted finite checkpoint and paired relations', async () => {
  const { runOwnedImageTransport } = await import('./windows-owned-image-transport.mjs');
  const wire = refusalWire('positive', 'none', 'clear') + cleanupWire() + handlePhaseWire();
  assert.ok(Buffer.byteLength(wire) <= 512);
  const result = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stdout.write("synthetic-private-count-values"); process.stderr.write(process.argv[1]); process.exitCode=1', wire], 4096, 2000);
  assert.equal(result.exitCode, 1);
  const observation = diagnosticApi.parseNativeDiagnostic(result, 'positive');
  assert.deepEqual(observation?.handlePhases, handlePhaseFacts());
  assert.deepEqual(observation?.cleanup, cleanupFacts());
  const text = formatFailure({ phase: 'case', name: 'positive', category: 'native', native: diagnosticApi.nativeOutcome(result),
    refusal: observation.refusal, cleanupEvidence: observation.cleanup, handlePhases: observation.handlePhases });
  assert.ok(text.includes('entryOutput=equal controlReady=above'));
  assert.ok(text.includes('final=above pinHash=equal imageHash=equal targetScope=above profileRest=above'));
  assert.equal(text.includes('synthetic-private'), false);
  assert.equal(validateNative(wire, 'positive').qualified, false);
});

test('handle-phase owner-loss evidence cannot omit the reached creation scope', () => {
  const phases = handlePhaseFacts({ pinHashEnter: 'not-reached', pinHashLeave: 'not-reached', debugCreateEnter: 'not-reached',
    debugCreateLeave: 'not-reached', firstEvent: 'not-reached', imageHashEnter: 'not-reached', imageHashLeave: 'not-reached',
    continued: 'not-reached', detached: 'not-reached', probeReturn: 'not-reached', pinHash: 'unavailable', imageHash: 'unavailable' });
  const wire = refusalWire('owner-interruption', 'owner-interruption', 'owner-interrupted') +
    cleanupWire(cleanupFacts({ rejectedClear: true }), 'owner-interruption') + handlePhaseWire(phases, 'owner-interruption');
  assert.equal(diagnosticApi.parseNativeDiagnostic(refusalResult(wire), 'owner-interruption'), null);
});

test('handle-phase pairs accept coherent less, equal, greater and failed-query observations', () => {
  for (const patch of [{ pinHashEnter: 'equal', pinHashLeave: 'below', pinHash: 'below' },
    { pinHashEnter: 'below', pinHashLeave: 'equal', pinHash: 'above' },
    { imageHashEnter: 'equal', imageHashLeave: 'equal', imageHash: 'equal' },
    { imageHashEnter: 'above', imageHashLeave: 'equal', imageHash: 'below' },
    { controlReady: 'above', childReleased: 'equal', targetScope: 'below' },
    { entryOutput: 'above', profileRest: 'below' }, { entryOutput: 'above', profileRest: 'equal' }]) {
    const phases = handlePhaseFacts(patch);
    const result = refusalResult(refusalWire('positive', 'none', 'clear') + cleanupWire() + handlePhaseWire(phases));
    assert.deepEqual(diagnosticApi.parseNativeDiagnostic(result, 'positive')?.handlePhases, phases, JSON.stringify(patch));
  }
  const pairEndpoints = { entryOutput: 'profileRest', controlReady: 'targetScope', pinHashEnter: 'pinHash', pinHashLeave: 'pinHash',
    imageHashEnter: 'imageHash', imageHashLeave: 'imageHash', childReleased: 'targetScope' };
  for (const key of Object.keys(handlePhaseFacts()).slice(0, 15)) {
    const phases = handlePhaseFacts({ [key]: 'query-failed', ...(pairEndpoints[key] ? { [pairEndpoints[key]]: 'unavailable' } : {}) });
    const result = refusalResult(refusalWire('positive', 'none', 'clear') + cleanupWire() + handlePhaseWire(phases));
    assert.deepEqual(diagnosticApi.parseNativeDiagnostic(result, 'positive')?.handlePhases, phases, key);
  }
});

test('handle-phase not-reached slots retain failed-hash and owner-interruption reach semantics', () => {
  const suffix = { pinHashLeave: 'not-reached', debugCreateEnter: 'not-reached', debugCreateLeave: 'not-reached', firstEvent: 'not-reached',
    imageHashEnter: 'not-reached', imageHashLeave: 'not-reached', continued: 'not-reached', detached: 'not-reached', probeReturn: 'not-reached',
    pinHash: 'unavailable', imageHash: 'unavailable' };
  const noChild = Object.fromEntries(Object.keys(stopFacts()).map(key => ['child' + key,
    key === 'Process' ? false : key === 'Stop' ? true : 'not-reached']));
  const failedHash = handlePhaseFacts(suffix);
  const facts = cleanupFacts({ ...noChild, exitQuery: 'not-reached', exitInactive: 'not-reached', earlyClear: 'not-reached',
    closeIdentity: 'not-reached', closeQuery: 'not-reached', debugClose: 'not-reached' });
  const failed = refusalResult(refusalWire('positive', 'probe', 'query-check') + cleanupWire(facts) + handlePhaseWire(failedHash));
  assert.deepEqual(diagnosticApi.parseNativeDiagnostic(failed, 'positive')?.handlePhases, failedHash);
  const owner = handlePhaseFacts({ ...suffix, pinHashLeave: 'above', debugCreateEnter: 'above', debugCreateLeave: 'above', pinHash: 'equal' });
  const ownerResult = refusalResult(refusalWire('owner-interruption', 'owner-interruption', 'owner-interrupted') +
    cleanupWire(cleanupFacts({ rejectedClear: true }), 'owner-interruption') + handlePhaseWire(owner, 'owner-interruption'));
  assert.deepEqual(diagnosticApi.parseNativeDiagnostic(ownerResult, 'owner-interruption')?.handlePhases, owner);
});

test('handle-phase projection rejects impossible inequalities, unknown fields and accessor-backed contexts', () => {
  const native = { exit: 'present', status: 1, stderr: 'nonempty' };
  const context = { phase: 'case', name: 'positive', category: 'native', native,
    refusal: { phase: 'none', reason: 'clear', cleanup: false, survival: true, flush: true, close: true },
    cleanupEvidence: cleanupFacts(), handlePhases: handlePhaseFacts() };
  const unexpected = formatFailure({ phase: 'unexpected' });
  for (const patch of [{ final: 'equal' }, { controlReady: 'not-reached', targetScope: 'unavailable' },
    { pinHashLeave: 'not-reached', pinHash: 'unavailable' }, { pinHashEnter: 'equal', pinHashLeave: 'equal', pinHash: 'above' },
    { pinHashEnter: 'below', pinHashLeave: 'above', pinHash: 'below' },
    { imageHashEnter: 'above', imageHashLeave: 'below', imageHash: 'above' },
    { controlReady: 'below', childReleased: 'above', targetScope: 'below' }, { profileRest: 'below' },
    { imageHash: 'unavailable' }, { pinHashEnter: 'query-failed' }, { entryOutput: ['equal'] },
    { entryOutput: 'C:\\private' }, { entryOutput: 1 }, { extra: 'private' }])
    assert.equal(formatFailure({ ...context, handlePhases: handlePhaseFacts(patch) }), unexpected, JSON.stringify(patch));
  for (const patch of [{ phase: 'build' }, { category: 'receipt' }, { native: { ...native, status: 2 } },
    { cleanupEvidence: null }, { refusal: null }, { native: { ...native, stderr: 'empty' } },
    { cleanupEvidence: cleanupFacts({ countQuery: false, countNonincrease: 'not-reached', closed: false, leakedZero: 'not-reached' }) },
    { cleanupEvidence: cleanupFacts({ countNonincrease: true, ownedZero: false }) }])
    assert.equal(formatFailure({ ...context, ...patch }), unexpected);
  let reads = 0;
  const phases = { ...handlePhaseFacts(), get entryOutput() { reads++; return 'equal'; } };
  assert.equal(formatFailure({ ...context, handlePhases: phases }), unexpected);
  const top = { ...context, get handlePhases() { reads++; return handlePhaseFacts(); } };
  assert.equal(formatFailure(top), unexpected);
  assert.equal(reads, 0);
  for (const handlePhases of [Object.create(handlePhaseFacts()), { ...handlePhaseFacts(), [Symbol('private')]: 'private' }])
    assert.equal(formatFailure({ ...context, handlePhases }), unexpected);
  const inherited = Object.assign(Object.create({ handlePhases: handlePhaseFacts() }), context);
  delete inherited.handlePhases;
  assert.equal(formatFailure(inherited), unexpected);
  assert.ok(formatFailure({ ...context, handlePhases: null }).endsWith(' handlePhases=unknown\n'));
});

test('handle-phase framing is atomic, bounded and cannot reinterpret an older or malformed observation', () => {
  const core = refusalWire('positive', 'none', 'clear') + cleanupWire();
  const row = handlePhaseWire();
  assert.equal(diagnosticApi.parseNativeDiagnostic(refusalResult(core), 'positive').handlePhases, null);
  const changedRows = [row.replace('HANDLE_PHASES\t1', 'HANDLE_PHASES\t2'), row.replace('\tpositive\t', '\tpositive-repeat\t'),
    row.replace('\te\t', '\t17\t'), row.replace('\te\t', '\tC:\\private\t'), row.replace('\te\t', '\tu\t'),
    row.replace('\te\t', '\t\t'), row.trimEnd(), row + '\n', row + row, row + 'private\n', row + 'x'.repeat(513)];
  for (const bad of changedRows) {
    assert.notEqual(bad, row);
    const result = refusalResult(core + bad);
    assert.equal(diagnosticApi.parseNativeDiagnostic(result, 'positive'), null);
    assert.equal(diagnosticApi.parseNativeRefusal(result, 'positive'), null);
    assert.equal(diagnosticApi.parseNativeCleanup(result, 'positive'), null);
  }
  for (const text of [row + core, core + cleanupWire() + row, core + row + cleanupWire(), 'x'.repeat(513)])
    assert.equal(diagnosticApi.parseNativeDiagnostic(refusalResult(text), 'positive'), null);
  assert.deepEqual(diagnosticApi.parseNativeDiagnostic(refusalResult((core + row).replaceAll('\n', '\r\n')), 'positive')?.handlePhases, handlePhaseFacts());
});

test('owned phase-wire transport and artifact guard preserve the actual failed exit, cap and deadline', async () => {
  const { runOwnedImageTransport } = await import('./windows-owned-image-transport.mjs');
  const wire = refusalWire('positive', 'none', 'clear') + cleanupWire() + handlePhaseWire();
  const result = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stderr.write(process.argv[1]); process.stdout.write(process.argv[2]); process.exitCode=1', wire, positive()], 4096, 2000);
  assert.ok(diagnosticApi.parseNativeDiagnostic(result, 'positive')?.handlePhases);
  assert.equal(validateNative(result.stdout, 'positive').qualified, true);
  const root = evidence();
  try {
    const file = join(root, 'driver.private.json');
    const driver = JSON.parse(readFileSync(file, 'utf8'));
    driver.cases[0] = { ...driver.cases[0], exitCode: result.exitCode, handlePhases: handlePhaseFacts() };
    writeFileSync(file, JSON.stringify(driver));
    writeFileSync(join(root, 'positive.private.tsv'), result.stdout);
    writeFileSync(join(root, 'positive.stderr.private.txt'), result.stderr);
    assert.throws(() => prepareUpload(root), { message: 'receipt' });
    assert.equal(readdirSync(root).includes('upload'), false);
  } finally { rmSync(root, { recursive: true, force: true }); }
  for (const status of [0, 2]) {
    const other = await runOwnedImageTransport(process.execPath,
      ['-e', 'process.stderr.write(process.argv[1]); process.exitCode=Number(process.argv[2])', wire, String(status)], 4096, 2000);
    assert.equal(other.exitCode, status);
    assert.equal(diagnosticApi.parseNativeDiagnostic(other, 'positive'), null);
  }
  const capped = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stderr.write(process.argv[1]); process.stdout.write(Buffer.alloc(8192,65)); setInterval(()=>{},1000)', wire], 512, 2000);
  assert.equal(capped.capped, true);
  assert.equal(diagnosticApi.parseNativeDiagnostic(capped, 'positive'), null);
  const timed = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stderr.write(process.argv[1]); setInterval(()=>{},1000)', wire], 4096, 700);
  assert.equal(timed.timedOut, true);
  assert.equal(diagnosticApi.parseNativeDiagnostic(timed, 'positive'), null);
});

test('a complete receipt from a still-running owned controller cannot override its actual deadline', { timeout: 5000 }, async () => {
  const { runOwnedImageTransport } = await import('./windows-owned-image-transport.mjs');
  const result = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stdout.write(process.argv[1]); setInterval(()=>{},1000)', positive()], 4096, 700);
  assert.equal(result.timedOut, true);
  assert.equal(result.capped, false);
  assert.equal(result.stdout, positive());
  assert.equal(validateNative(result.stdout, 'positive').qualified, true);
  const root = evidence();
  try {
    const file = join(root, 'driver.private.json');
    const driver = JSON.parse(readFileSync(file, 'utf8'));
    driver.cases[0] = { name: 'positive', exitCode: result.exitCode, signal: result.signal, capped: result.capped, timedOut: result.timedOut };
    writeFileSync(file, JSON.stringify(driver));
    writeFileSync(join(root, 'positive.private.tsv'), result.stdout);
    assert.throws(() => prepareUpload(root), { message: 'receipt' });
    assert.equal(readdirSync(root).includes('upload'), false);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('an owned controller exiting zero with incomplete cleanup cannot inherit a forged complete driver result', { timeout: 5000 }, async () => {
  const { runOwnedImageTransport } = await import('./windows-owned-image-transport.mjs');
  const partial = positive().slice(0, positive().indexOf('CLEANUP\t'));
  const result = await runOwnedImageTransport(process.execPath,
    ['-e', 'process.stdout.write(process.argv[1])', partial], 4096, 2000);
  assert.equal(result.exitCode, 0);
  assert.equal(result.signal, null);
  assert.equal(result.timedOut, false);
  assert.equal(result.capped, false);
  assert.equal(result.stdout, partial);
  assert.equal(validateNative(result.stdout, 'positive').cleanup, false);
  const root = evidence();
  try {
    writeFileSync(join(root, 'positive.private.tsv'), result.stdout);
    assert.throws(() => prepareUpload(root), { message: 'receipt' });
    assert.equal(readdirSync(root).includes('upload'), false);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('a real owned late producer cannot clear the controller timeout at the artifact guard input', { timeout: 5000 }, async () => {
  const { runOwnedImageTransport } = await import('./windows-owned-image-transport.mjs');
  const { spawn } = await import('node:child_process');
  // A Windows Node parent may kill its ordinary descendants on exit. This
  // producer belongs directly to the test and never shares the controller pipe.
  // READY precedes controller launch; only its actual timeout/close permits the
  // producer to supply COMPLETE. The composite is an explicit guard input.
  const source = 'const timer=setTimeout(()=>{process.exitCode=2;process.disconnect()},1000);' +
    'process.once("message",message=>{if(message!=="complete"){process.exitCode=2;clearTimeout(timer);process.disconnect();return;}' +
    'process.stdout.write("COMPLETE\\n",()=>{clearTimeout(timer);process.disconnect()})});process.send("ready")';
  let readyResolve, readyReject;
  const ready = new Promise((resolve, reject) => { readyResolve = resolve; readyReject = reject; });
  const producer = spawn(process.execPath, ['-e', source], { windowsHide: true, shell: false, stdio: ['ignore', 'pipe', 'pipe', 'ipc'] });
  const output = [], errors = [];
  let producerError = null;
  producer.stdout.on('data', chunk => output.push(chunk));
  producer.stderr.on('data', chunk => errors.push(chunk));
  producer.once('message', message => message === 'ready' ? readyResolve() : readyReject(new Error('unexpected producer readiness')));
  producer.on('error', error => { producerError = error; readyReject(error); });
  const closed = new Promise(resolve => producer.once('close', (exitCode, signal) => {
    readyReject(new Error('producer closed before readiness'));
    resolve({ exitCode, signal });
  }));
  try {
    await ready;
    const partial = positive().replace('COMPLETE\n', '');
    const result = await runOwnedImageTransport(process.execPath,
      ['-e', 'process.stdout.write(process.argv[1]); setInterval(()=>{},1000)', partial], 4096, 700);
    assert.equal(result.timedOut, true);
    assert.equal(result.capped, false);
    assert.equal(result.stdout, partial);
    producer.send('complete');
    assert.deepEqual(await closed, { exitCode: 0, signal: null });
    assert.equal(producerError, null);
    assert.equal(Buffer.concat(errors).toString('utf8'), '');
    const completion = Buffer.concat(output).toString('utf8');
    assert.equal(completion, 'COMPLETE\n');
    const lateWire = result.stdout + completion;
    assert.equal(lateWire, positive());
    assert.equal(validateNative(lateWire, 'positive').qualified, true);
    const root = evidence();
    try {
      const file = join(root, 'driver.private.json');
      const driver = JSON.parse(readFileSync(file, 'utf8'));
      driver.cases[0] = { name: 'positive', exitCode: result.exitCode, signal: result.signal, capped: result.capped, timedOut: result.timedOut };
      writeFileSync(file, JSON.stringify(driver));
      writeFileSync(join(root, 'positive.private.tsv'), lateWire);
      assert.throws(() => prepareUpload(root), { message: 'receipt' });
      assert.equal(readdirSync(root).includes('upload'), false);
    } finally { rmSync(root, { recursive: true, force: true }); }
  } finally {
    if (producer.exitCode === null && producer.signalCode === null) producer.kill();
    await closed;
  }
});

import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { validateProbeReceipt } from './windows-etw-probe.mjs';

const good = [
  'ABI\t120\t280\t112\t448', 'TOKEN\tadministrator', 'OS\tWindows NT 10.0.26100',
  'API\tstart\t0', 'API\treadyQuery\t0', 'QUERY\treadyQuery\t1\t1\t1\t1\t1',
  'MODE\treadyQuery\t1\t1\t0\tstop\t0',
  'API\tbeforeStopQuery\t0', 'QUERY\tbeforeStopQuery\t1\t1\t1\t1\t1',
  'MODE\tbeforeStopQuery\t1\t1\t0\tstop\t0',
  'API\tstop\t0', 'API\topen\t0', 'API\tprocess\t0', 'API\tclose\t0',
  'OWNERSHIP\t11111111-2222-4333-8444-555555555555\tCodex factory ETW feasibility 11111111222243338444555555555555',
  'SESSION\t37748737\t5\t64', 'ROOT\t100\t134000000000000000\tpinned-node',
  'CHILD\t101', 'HELD\troot\t1\t1\t1', 'HELD\tchild\t1\t1\t1',
  'EVENT\tprocess-start\t100\t50\troot\tpinned-node\t134000000000000000',
  'EVENT\tprocess-start\t101\t100\tchild\tpinned-node\t134000000000100000',
  'EVENT\timage-load\t100\tpinned-node\t134000000000200000',
  'EVENT\timage-load\t101\tpinned-node\t134000000000300000',
  'EVENT\tprocess-end\t101\t100\tchild\t0\t134000000000500000',
  'EVENT\tprocess-end\t100\t50\troot\t0\t134000000000600000',
  'SCHEMA\tProcessId:u32\tParentId:u32\tUniqueProcessKey:pointer\tImageFileName:string\tExitStatus:u32\tImage.ProcessId:u32\tImage.FileName:string',
  'RUNDOWN\t0\t0', 'COUNTS\t20\t6',
  'STATS\t0\t0\t0', 'HEADER\t134000000001000000\t0\t0',
  'FILE\t65536', 'COMPLETE', ''
].join('\n');

// Native Windows run 39866555694 before SCHEMA, with its old four-field DIAG omitted
// so each public upload case can insert an exact diagnostic row.
const failedDecode = [
  'ABI\t120\t280\t112\t448', 'TOKEN\tadministrator', 'OS\tMicrosoft Windows NT 10.0.26100.0',
  'API\tstart\t0', 'API\treadyQuery\t0', 'QUERY\treadyQuery\t1\t1\t1\t1\t1',
  'MODE\treadyQuery\t1\t1\t0\tstop\t0',
  'OWNERSHIP\tb1d11c8f-d68b-4ef3-a5ca-cc0a072e568e\tCodex factory ETW feasibility b1d11c8fd68b4ef3a5cacc0a072e568e',
  'SESSION\t37748737\t5\t64', 'ROOT\t7552\t134371824125823679\tpinned-node',
  'CHILD\t2928', 'API\tbeforeStopQuery\t0', 'QUERY\tbeforeStopQuery\t1\t1\t1\t1\t1',
  'MODE\tbeforeStopQuery\t1\t1\t0\tstop\t0', 'API\tstop\t0', 'STATS\t0\t0\t0',
  'FILE\t3276800', 'API\topen\t0', 'API\tprocess\t0', 'API\tclose\t0',
  'FAIL\tdecode\tinvalid-data\t0', ''
].join('\n');

test('fixed fixture reports a live child and exits silently after one release byte', { timeout: 7000 }, async () => {
  const fixture = fileURLToPath(new URL('./windows-etw-child-fixture.cjs', import.meta.url));
  const root = spawn(process.execPath, [fixture], { stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
  let output = '', error = '';
  root.stderr.on('data', (chunk) => { error += chunk; });
  const line = new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('fixture PID line timeout')), 3000);
    root.once('error', (cause) => { clearTimeout(timer); reject(cause); });
    root.once('close', (code) => { clearTimeout(timer); reject(new Error(`fixture exited before release: ${code}`)); });
    root.stdout.on('data', (chunk) => {
      output += chunk;
      if (output.includes('\n')) { clearTimeout(timer); resolve(output); }
    });
  });
  try {
    const pidLine = await line;
    assert.match(pidLine, /^[1-9]\d{0,9}\n$/);
    const childPid = Number(pidLine.trim());
    assert.notEqual(childPid, root.pid);
    assert.doesNotThrow(() => process.kill(childPid, 0));
    const closed = new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('fixture release timeout')), 3000);
      root.once('close', (code, signal) => { clearTimeout(timer); resolve({ code, signal }); });
    });
    root.stdin.end('R');
    assert.deepEqual(await closed, { code: 0, signal: null });
    assert.equal(output, `${childPid}\n`);
    assert.equal(error, '');
  } finally { if (root.exitCode === null) root.kill(); }
});

test('fixed child announces readiness before accepting the release byte', { timeout: 7000 }, async () => {
  const fixture = fileURLToPath(new URL('./windows-etw-child-fixture.cjs', import.meta.url));
  const child = spawn(process.execPath, [fixture, '--child'], { stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
  let output = '', errors = '';
  child.stdout.on('data', chunk => { output += chunk; });
  child.stderr.on('data', chunk => { errors += chunk; });
  try {
    const ready = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('child readiness missing')), 3000);
      child.once('error', error => { clearTimeout(timer); reject(error); });
      child.stdout.once('data', bytes => { clearTimeout(timer); resolve(bytes); });
    });
    assert.deepEqual(ready, Buffer.from('K'));
    assert.doesNotThrow(() => process.kill(child.pid, 0));
    const closed = new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('ready child did not exit')), 3000);
      child.once('close', (code, signal) => { clearTimeout(timer); resolve({ code, signal }); });
    });
    child.stdin.end('R');
    assert.deepEqual(await closed, { code: 0, signal: null });
    assert.equal(output, 'K');
    assert.equal(errors, '');
  } finally { if (child.exitCode === null) child.kill(); }
});

test('public receipt accepts a complete known root and child, pending native proof', () => {
  assert.deepEqual(validateProbeReceipt(good, 'C:\\node\\node.exe'), {
    ok: true, reasons: [], rootPid: 100, childPid: 101,
    processStarts: 2, processEnds: 2, imageLoads: 2
  });
});

test('held root and child proof is required in order and exact closed form', () => {
  const root = 'HELD\troot\t1\t1\t1';
  const child = 'HELD\tchild\t1\t1\t1';
  for (const changed of [
    good.replace(`${root}\n`, ''),
    good.replace(`${child}\n`, ''),
    good.replace(`${root}\n${child}\n`, ''),
    good.replace(root, `${root}\n${root}`),
    good.replace(`${root}\n${child}`, `${child}\n${root}`),
    good.replace(root, 'HELD\troot\t1\t0\t1'),
    good.replace(child, 'HELD\tchild\t1\t1\t0'),
    good.replace(root, `${root}\tC:\\ambient\\node.exe`),
    good.replace(root, 'HELD\tunknown\t1\t1\t1'),
    good.replace(`${root}\n${child}\n`, '').replace('COMPLETE\n', `${root}\n${child}\nCOMPLETE\n`)
  ]) assert.equal(validateProbeReceipt(changed, 'C:\\node\\node.exe').ok, false);
});

test('artifact preparation retains only paired held rows and downgrades forged proof', () => {
  const cli = fileURLToPath(new URL('./windows-etw-probe.mjs', import.meta.url));
  const evidence = mkdtempSync(join(tmpdir(), 'factory-etw-held-proof-'));
  const native = join(evidence, 'native.tsv');
  const root = 'HELD\troot\t1\t1\t1';
  const child = 'HELD\tchild\t1\t1\t1';
  const run = () => spawnSync(process.execPath, [cli, '--prepare-artifacts'], {
    encoding: 'utf8', timeout: 5000,
    env: { ...process.env, WINDOWS_ETW_PROBE_EVIDENCE: evidence }
  });
  try {
    writeFileSync(join(evidence, 'qualification.json'), JSON.stringify({
      status: 'native-feasibility-passed-review-required', receipt: { ok: true },
      rawEtl: 'removed-after-offline-parse'
    }));
    const failedHeld = failedDecode.replace('CHILD\t2928\n',
      `CHILD\t2928\n${root}\n${child}\n`).replace('FAIL\tdecode',
      'DIAG\tcallback\tprocess-image-mismatch\troot\tname-only\tsame\tat-or-after-creation-within-window\nFAIL\tdecode');
    writeFileSync(native, failedHeld);
    assert.equal(run().status, 0);
    assert.equal(readFileSync(join(evidence, 'upload', 'native.tsv'), 'utf8'), failedHeld);
    assert.equal(JSON.parse(readFileSync(join(evidence, 'upload', 'qualification.json'), 'utf8')).status, 'failed');
    for (const malformed of [
      good.replace(`${root}\n`, ''), good.replace(`${child}\n`, ''),
      good.replace(root, `${root}\n${root}`),
      good.replace(`${root}\n${child}`, `${child}\n${root}`),
      good.replace(root, 'HELD\troot\t1\t0\t1'),
      good.replace(child, 'HELD\tchild\t1\t1\t0'),
      good.replace(root, `${root}\tC:\\ambient\\node.exe`),
      good.replace(root, 'HELD\tunknown\t1\t1\t1'),
      good.replace(`${root}\n${child}\n`, '').replace('COMPLETE\n', `${root}\n${child}\nCOMPLETE\n`),
      `${good}${'X'.repeat(65537)}`
    ]) {
      writeFileSync(native, malformed);
      assert.equal(run().status, 0);
      assert.equal(existsSync(native), false);
      assert.equal(existsSync(join(evidence, 'upload', 'native.tsv')), false);
    }
    writeFileSync(native, good.replace(`${root}\n${child}\n`, ''));
    assert.equal(run().status, 0);
    assert.equal(JSON.parse(readFileSync(join(evidence, 'upload', 'qualification.json'), 'utf8')).status, 'failed');
  } finally { rmSync(evidence, { recursive: true, force: true }); }
});

test('artifact preparation retains fixed child-stop failure without promoting it', () => {
  const cli = fileURLToPath(new URL('./windows-etw-probe.mjs', import.meta.url));
  const evidence = mkdtempSync(join(tmpdir(), 'factory-etw-child-stop-'));
  const native = join(evidence, 'native.tsv');
  try {
    writeFileSync(join(evidence, 'qualification.json'), JSON.stringify({
      status: 'native-feasibility-passed-review-required', receipt: { ok: true },
      rawEtl: 'removed-after-offline-parse'
    }));
    const failed = failedDecode.replace('FAIL\tdecode\tinvalid-data\t0',
      'FAIL\tchild-stop\toperation-failed\t0\nFAIL\tdecode\tinvalid-data\t0');
    writeFileSync(native, failed);
    const run = () => spawnSync(process.execPath, [cli, '--prepare-artifacts'], {
      encoding: 'utf8', timeout: 5000,
      env: { ...process.env, WINDOWS_ETW_PROBE_EVIDENCE: evidence }
    });
    assert.equal(run().status, 0);
    assert.equal(readFileSync(join(evidence, 'upload', 'native.tsv'), 'utf8'), failed);
    assert.equal(JSON.parse(readFileSync(join(evidence, 'upload', 'qualification.json'), 'utf8')).status,
      'failed');
    writeFileSync(native, failed.replace('FAIL\tchild-stop\toperation-failed\t0',
      'FAIL\tchild-stop\tC:\\ambient\\node.exe\t0'));
    assert.equal(run().status, 0);
    assert.equal(existsSync(join(evidence, 'upload', 'native.tsv')), false);
  } finally { rmSync(evidence, { recursive: true, force: true }); }
});

test('public receipt requires unique, exact, all-true query evidence', () => {
  const ready = 'QUERY\treadyQuery\t1\t1\t1\t1\t1';
  const beforeStop = 'QUERY\tbeforeStopQuery\t1\t1\t1\t1\t1';
  const changed = [
    good.replace(`${ready}\n`, ''),
    good.replace(`${beforeStop}\n`, ''),
    good.replace(ready, `${ready}\n${ready}`),
    good.replace(beforeStop, `${beforeStop}\n${beforeStop}`),
    good.replace(ready, `${ready}\tC:\\ambient\\node.exe`),
    good.replace(beforeStop, 'QUERY\tunknown\t1\t1\t1\t1\t1')
  ];
  for (const row of [ready, beforeStop]) {
    for (let bit = 0; bit < 5; bit++) {
      const parts = row.split('\t');
      parts[bit + 2] = '0';
      changed.push(good.replace(row, parts.join('\t')));
    }
  }
  for (const receipt of changed)
    assert.ok(validateProbeReceipt(receipt, 'C:\\node\\node.exe').reasons.includes('query evidence invalid'));
});

test('public receipt requires unique expected closed mode categories for both queries', () => {
  const ready = 'MODE\treadyQuery\t1\t1\t0\tstop\t0';
  const beforeStop = 'MODE\tbeforeStopQuery\t1\t1\t0\tstop\t0';
  for (const changed of [
    good.replace(`${ready}\n`, ''),
    good.replace(`${beforeStop}\n`, ''),
    good.replace(ready, `${ready}\n${ready}`),
    good.replace(beforeStop, `${beforeStop}\n${beforeStop}`),
    good.replace(ready, `${ready}\tC:\\ambient\\node.exe`),
    good.replace(beforeStop, 'MODE\tunknown\t1\t1\t0\tstop\t0'),
    good.replace(ready, 'MODE\treadyQuery\t0\t1\t0\tstop\t0'),
    good.replace(ready, 'MODE\treadyQuery\t1\t0\t0\tstop\t0'),
    good.replace(ready, 'MODE\treadyQuery\t1\t1\t1\tstop\t0'),
    good.replace(ready, 'MODE\treadyQuery\t1\t1\t0\tnone\t0'),
    good.replace(ready, 'MODE\treadyQuery\t1\t1\t0\tpersist\t0'),
    good.replace(ready, 'MODE\treadyQuery\t1\t1\t0\tboth\t0'),
    good.replace(ready, 'MODE\treadyQuery\t1\t1\t0\tstop\t1'),
    good.replace(beforeStop, 'MODE\tbeforeStopQuery\t1\t1\t0\tunknown\t0')
  ]) assert.ok(validateProbeReceipt(changed, 'C:\\node\\node.exe').reasons.includes('mode evidence invalid'));
});

test('public receipt requires the single explicit stop-on-hybrid session profile', () => {
  const oldProfile = good.replace('SESSION\t37748737\t5\t64', 'SESSION\t33554433\t5\t64');
  assert.ok(validateProbeReceipt(oldProfile, 'C:\\node\\node.exe').reasons.includes('session mode, flags or cap mismatch'));
});

test('forged qualification cannot pass artifact preparation with missing or old mode policy', () => {
  const cli = fileURLToPath(new URL('./windows-etw-probe.mjs', import.meta.url));
  const evidence = mkdtempSync(join(tmpdir(), 'factory-etw-mode-forgery-'));
  try {
    writeFileSync(join(evidence, 'qualification.json'), JSON.stringify({
      status: 'native-feasibility-passed-review-required', receipt: { ok: true },
      rawEtl: 'removed-after-offline-parse'
    }));
    for (const receipt of [
      good.split('\n').filter((row) => !row.startsWith('MODE\t')).join('\n'),
      good.replace('SESSION\t37748737\t5\t64', 'SESSION\t33554433\t5\t64'),
      good.replace('MODE\treadyQuery\t1\t1\t0\tstop\t0', 'MODE\treadyQuery\t1\t1\t0\tnone\t0')
    ]) {
      writeFileSync(join(evidence, 'native.tsv'), receipt);
      const result = spawnSync(process.execPath, [cli, '--prepare-artifacts'], {
        encoding: 'utf8', timeout: 5000,
        env: { ...process.env, WINDOWS_ETW_PROBE_EVIDENCE: evidence }
      });
      assert.equal(result.status, 0);
      const staged = JSON.parse(readFileSync(join(evidence, 'upload', 'qualification.json'), 'utf8'));
      assert.equal(staged.status, 'failed');
      assert.deepEqual(staged.failure, { stage: 'receipt', code: 'receipt-invalid' });
    }
  } finally { rmSync(evidence, { recursive: true, force: true }); }
});

test('failed native decode retains one bounded fixed diagnostic without qualifying', () => {
  const cli = fileURLToPath(new URL('./windows-etw-probe.mjs', import.meta.url));
  const evidence = mkdtempSync(join(tmpdir(), 'factory-etw-decode-diag-'));
  const native = join(evidence, 'native.tsv');
  const diagnostic = 'DIAG\tcallback\tprocess-image-mismatch\troot\tname-only\tsame\tbefore-creation-within-window';
  const failed = failedDecode.replace('FAIL\tdecode', `${diagnostic}\nFAIL\tdecode`);
  const prepare = () => spawnSync(process.execPath, [cli, '--prepare-artifacts'], {
    encoding: 'utf8', timeout: 5000,
    env: { ...process.env, WINDOWS_ETW_PROBE_EVIDENCE: evidence }
  });
  try {
    const summary = { status: 'native-feasibility-passed-review-required', receipt: { ok: true },
      rawEtl: 'removed-after-offline-parse' };
    writeFileSync(join(evidence, 'qualification.json'), JSON.stringify(summary));
    writeFileSync(native, failed);
    assert.equal(prepare().status, 0);
    assert.equal(readFileSync(join(evidence, 'upload', 'native.tsv'), 'utf8'), failed);
    const staged = JSON.parse(readFileSync(join(evidence, 'upload', 'qualification.json'), 'utf8'));
    assert.equal(staged.status, 'failed');
    assert.equal(staged.receipt.ok, false);
    assert.deepEqual(staged.failure, { stage: 'receipt', code: 'receipt-invalid' });
    assert.equal(validateProbeReceipt(failed, 'C:\\node\\node.exe').ok, false);
    for (const allowed of [
      diagnostic.replace('name-only', 'dos-absolute').replace('before-creation-within-window', 'before-creation-window'),
      diagnostic.replace('name-only', 'device-absolute').replace('before-creation-within-window', 'at-or-after-creation-within-window'),
      diagnostic.replace('name-only', 'other').replace('before-creation-within-window', 'after-creation-window'),
      diagnostic.replace('before-creation-within-window', 'unknown'),
      diagnostic.replace('\tsame\t', '\tdifferent\t'),
      'DIAG\tcallback\tprocess-image-mismatch\tchild\tname-only\tsame\tunknown',
      'DIAG\tcallback\tother\tnone',
      'DIAG\tkeys\tchanged-key\troot',
      'DIAG\tidentity\tcreation-time\troot',
      'DIAG\tidentity\theld-time\tchild\tprocess-end\tafter-exit'
    ]) {
      const evidenceRow = failed.replace(diagnostic, allowed);
      writeFileSync(native, evidenceRow);
      assert.equal(prepare().status, 0);
      assert.equal(readFileSync(join(evidence, 'upload', 'native.tsv'), 'utf8'), evidenceRow);
      assert.equal(JSON.parse(readFileSync(join(evidence, 'upload', 'qualification.json'), 'utf8')).status, 'failed');
    }
    for (const invalid of [
      `${diagnostic}\n${diagnostic}\n`,
      'DIAG\tcallback\tunknown\tchild\n',
      'DIAG\tkeys\tprocess-image-mismatch\tchild\n',
      'DIAG\tkeys\tchanged-key\tnone\n',
      'DIAG\tcallback\tprocess-image-mismatch\troot\n',
      'DIAG\tcallback\tprocess-image-mismatch\troot\tname-only\tsame\n',
      `${diagnostic}\textra\n`,
      diagnostic.replace('name-only', 'unknown') + '\n',
      diagnostic.replace('\tsame\t', '\tunknown\t') + '\n',
      diagnostic.replace('before-creation-within-window', 'unknown-time') + '\n',
      diagnostic.replace('\troot\t', '\tnone\t') + '\n',
      diagnostic.replace('\troot\t', '\tchild\t') + '\n',
      diagnostic.replace('name-only', 'C:\\ambient\\node.exe') + '\n',
      diagnostic.replace('process-image-mismatch', 'other') + '\n',
      `${diagnostic}\npath\n`,
      `${diagnostic}${'X'.repeat(65537)}\n`,
      `${diagnostic}\nFAIL\tdecode\tinvalid-data\t0\n`
    ]) {
      writeFileSync(native, failed.replace(`${diagnostic}\n`, invalid));
      assert.equal(prepare().status, 0);
      assert.equal(existsSync(native), false);
      assert.equal(existsSync(join(evidence, 'upload', 'native.tsv')), false);
    }
    writeFileSync(native, failed.replace(`${diagnostic}\nFAIL\tdecode`, `FAIL\tdecode`)
      .replace('FAIL\tdecode\tinvalid-data\t0\n', `FAIL\tdecode\tinvalid-data\t0\n${diagnostic}\n`));
    assert.equal(prepare().status, 0);
    assert.equal(existsSync(native), false);
    writeFileSync(native, good.replace('COMPLETE\n', `${diagnostic}\nCOMPLETE\n`));
    assert.equal(prepare().status, 0);
    assert.equal(existsSync(native), false);
    assert.equal(existsSync(join(evidence, 'upload', 'native.tsv')), false);
    assert.equal(validateProbeReceipt(good.replace('COMPLETE\n', `${diagnostic}\nCOMPLETE\n`),
      'C:\\node\\node.exe').ok, false);
  } finally { rmSync(evidence, { recursive: true, force: true }); }
});

test('a close failure preserves the first decode diagnostic and one terminal failure', () => {
  const cli = fileURLToPath(new URL('./windows-etw-probe.mjs', import.meta.url));
  const evidence = mkdtempSync(join(tmpdir(), 'factory-etw-close-compound-'));
  const native = join(evidence, 'native.tsv');
  const diagnostic = 'DIAG\tcallback\tprocess-image-mismatch\tchild\tdevice-absolute\tdifferent\tunknown';
  const firstFailure = failedDecode.replace('API\tclose\t0\nFAIL\tdecode\tinvalid-data\t0\n',
    `API\tclose\t5\n${diagnostic}\nFAIL\tdecode\tinvalid-data\t0\n`);
  const prepare = () => spawnSync(process.execPath, [cli, '--prepare-artifacts'], {
    encoding: 'utf8', timeout: 5000,
    env: { ...process.env, WINDOWS_ETW_PROBE_EVIDENCE: evidence }
  });
  try {
    writeFileSync(join(evidence, 'qualification.json'), JSON.stringify({
      status: 'native-feasibility-passed-review-required', receipt: { ok: true },
      rawEtl: 'removed-after-offline-parse'
    }));
    const duplicateFailure = firstFailure.replace(`${diagnostic}\n`,
      `FAIL\tdecode\tnative-api\t5\n${diagnostic}\n`);
    writeFileSync(native, duplicateFailure);
    assert.equal(prepare().status, 0);
    assert.equal(existsSync(native), false);
    assert.equal(existsSync(join(evidence, 'upload', 'native.tsv')), false);

    writeFileSync(native, firstFailure);
    assert.equal(prepare().status, 0);
    assert.equal(readFileSync(join(evidence, 'upload', 'native.tsv'), 'utf8'), firstFailure);
    const summary = JSON.parse(readFileSync(join(evidence, 'upload', 'qualification.json'), 'utf8'));
    assert.equal(summary.status, 'failed');
    assert.equal(summary.receipt.ok, false);
    assert.deepEqual(summary.failure, { stage: 'receipt', code: 'receipt-invalid' });
    assert.equal(validateProbeReceipt(firstFailure, 'C:\\node\\node.exe').ok, false);

    const closeOnly = failedDecode.replace('API\tclose\t0\nFAIL\tdecode\tinvalid-data\t0\n',
      'API\tclose\t5\nFAIL\tdecode\tnative-api\t5\n');
    writeFileSync(native, closeOnly);
    assert.equal(prepare().status, 0);
    assert.equal(readFileSync(join(evidence, 'upload', 'native.tsv'), 'utf8'), closeOnly);
    assert.equal(JSON.parse(readFileSync(join(evidence, 'upload', 'qualification.json'), 'utf8')).status, 'failed');
  } finally { rmSync(evidence, { recursive: true, force: true }); }
});

test('public receipt fails closed on health, schema and missing positive controls', () => {
  for (const changed of [
    good.replace('HEADER\t134000000001000000\t0\t0', 'HEADER\t0\t0\t0'),
    good.replace('STATS\t0\t0\t0', 'STATS\t1\t0\t0'),
    good.replace('API\tstop\t0', 'API\tstop\t5'),
    good.replace('EVENT\tprocess-start\t101\t100\tchild\tpinned-node\t134000000000100000\n', ''),
    good.replace('EVENT\timage-load\t101\tpinned-node\t134000000000300000\n', ''),
    good.replace('COMPLETE\n', ''),
    good.replace('FILE\t65536', 'FILE\t67108864'),
    good.replace('CHILD\t101', 'CHILD\t100'),
    good.replace('EVENT\tprocess-start\t100\t50\troot\tpinned-node\t134000000000000000',
      'EVENT\tprocess-start\t100\t50\troot\tpinned-node\t134000000900000000'),
    good.replace('EVENT\tprocess-end\t101\t100\tchild\t0\t134000000000500000',
      'EVENT\tprocess-end\t101\t100\tchild\t0\t134000000000050000')
  ]) assert.equal(validateProbeReceipt(changed, 'C:\\node\\node.exe').ok, false);
});

test('same-basename foreign image and unverified process image cannot qualify', () => {
  for (const changed of [
    good.replace('EVENT\timage-load\t101\tpinned-node',
      'EVENT\timage-load\t101\tC:\\ambient\\node.exe'),
    good.replace('EVENT\tprocess-start\t101\t100\tchild\tpinned-node',
      'EVENT\tprocess-start\t101\t100\tchild\tC:\\ambient\\node.exe'),
    good.replace('COMPLETE\n', 'EVENT\timage-load\t101\tC:\\ambient\\node.exe\t134000000000350000\nCOMPLETE\n'),
    good.replace('EVENT\timage-load\t101\tpinned-node\t134000000000300000\n', '')
  ]) assert.equal(validateProbeReceipt(changed, 'C:\\node\\node.exe').ok, false);
});

test('public receipt rejects a byte-oversized payload before parsing', () => {
  const oversized = `${good}${'é'.repeat(33000)}`;
  assert.ok(oversized.length < 65536);
  assert.deepEqual(validateProbeReceipt(oversized, 'C:\\node\\node.exe'), {
    ok: false, reasons: ['invalid receipt or expected Node path']
  });
});

test('public CLI reports ETL cleanup failure as failed with a fixed code', () => {
  if (process.platform === 'win32') return;
  const cli = fileURLToPath(new URL('./windows-etw-probe.mjs', import.meta.url));
  const evidence = mkdtempSync(join(tmpdir(), 'factory-etw-cleanup-'));
  try {
    mkdirSync(join(evidence, 'trace.etl'));
    const result = spawnSync(process.execPath, [cli], { encoding: 'utf8', timeout: 5000,
      env: { ...process.env, WINDOWS_ETW_PROBE_EVIDENCE: evidence } });
    const report = JSON.parse(readFileSync(join(evidence, 'qualification.json'), 'utf8'));
    assert.equal(result.status, 1);
    assert.equal(report.status, 'failed');
    assert.deepEqual(report.failure, { stage: 'cleanup', code: 'etl-removal-failed' });
    assert.equal(report.rawEtl, 'cleanup-failed');
    assert.equal(JSON.stringify(report).includes(evidence), false);
  } finally { rmSync(evidence, { recursive: true, force: true }); }
});

test('public CLI rejects unsupported host before native process launch', () => {
  if (process.platform === 'win32') return;
  const cli = fileURLToPath(new URL('./windows-etw-probe.mjs', import.meta.url));
  const evidence = mkdtempSync(join(tmpdir(), 'factory-etw-unsupported-'));
  try {
    const result = spawnSync(process.execPath, [cli], { encoding: 'utf8', timeout: 5000,
      env: { ...process.env, WINDOWS_ETW_PROBE_EVIDENCE: evidence } });
    assert.equal(result.status, 2);
    assert.equal(result.stderr, 'ETW probe failed: host/unsupported-platform\n');
    const reportText = readFileSync(join(evidence, 'qualification.json'), 'utf8');
    assert.equal(reportText.includes(evidence), false);
    assert.deepEqual(JSON.parse(reportText).failure,
      { stage: 'host', code: 'unsupported-platform' });
  } finally { rmSync(evidence, { recursive: true, force: true }); }
});

test('artifact preparation removes oversized and path-bearing native receipts', () => {
  const cli = fileURLToPath(new URL('./windows-etw-probe.mjs', import.meta.url));
  const evidence = mkdtempSync(join(tmpdir(), 'factory-etw-artifacts-'));
  try {
    const native = join(evidence, 'native.tsv');
    for (const payload of ['X'.repeat(65537),
      good.replace('EVENT\timage-load\t101\tpinned-node',
        'EVENT\timage-load\t101\tC:\\ambient\\node.exe')]) {
      writeFileSync(native, payload);
      const result = spawnSync(process.execPath, [cli, '--prepare-artifacts'], {
        encoding: 'utf8', timeout: 5000,
        env: { ...process.env, WINDOWS_ETW_PROBE_EVIDENCE: evidence }
      });
      assert.equal(result.status, 0);
      assert.equal(existsSync(native), false);
      assert.doesNotMatch(result.stderr, /ambient|node\.exe/);
    }
    writeFileSync(native, good);
    const retained = spawnSync(process.execPath, [cli, '--prepare-artifacts'], {
      encoding: 'utf8', timeout: 5000,
      env: { ...process.env, WINDOWS_ETW_PROBE_EVIDENCE: evidence }
    });
    assert.equal(retained.status, 0);
    assert.equal(readFileSync(native, 'utf8'), good);
  } finally { rmSync(evidence, { recursive: true, force: true }); }
});

test('artifact preparation retains fixed failed-query and mode evidence but removes untrusted data', () => {
  const cli = fileURLToPath(new URL('./windows-etw-probe.mjs', import.meta.url));
  const evidence = mkdtempSync(join(tmpdir(), 'factory-etw-query-artifacts-'));
  const native = join(evidence, 'native.tsv');
  const failed = 'API\tstart\t0\nAPI\treadyQuery\t0\nQUERY\treadyQuery\t1\t0\t1\t1\t1\nMODE\treadyQuery\t1\t1\t0\tstop\t0\nFAIL\trun\tinvalid-state\t0\n';
  const prepare = () => spawnSync(process.execPath, [cli, '--prepare-artifacts'], {
    encoding: 'utf8', timeout: 5000,
    env: { ...process.env, WINDOWS_ETW_PROBE_EVIDENCE: evidence }
  });
  try {
    writeFileSync(native, failed);
    assert.equal(prepare().status, 0);
    assert.equal(readFileSync(join(evidence, 'upload', 'native.tsv'), 'utf8'), failed);
    writeFileSync(native, `${failed}QUERY\treadyQuery\tC:\\ambient\\node.exe\t1\t1\t1\t1\n`);
    assert.equal(prepare().status, 0);
    assert.equal(existsSync(join(evidence, 'upload', 'native.tsv')), false);
    assert.equal(existsSync(native), false);
    writeFileSync(native, `${failed}MODE\treadyQuery\t1\t1\t0\tC:\\ambient\\node.exe\t0\n`);
    assert.equal(prepare().status, 0);
    assert.equal(existsSync(join(evidence, 'upload', 'native.tsv')), false);
    assert.equal(existsSync(native), false);
  } finally { rmSync(evidence, { recursive: true, force: true }); }
});

test('artifact preparation excludes raw bootstrap paths and free-text errors', () => {
  const cli = fileURLToPath(new URL('./windows-etw-probe.mjs', import.meta.url));
  const evidence = mkdtempSync(join(tmpdir(), 'factory-etw-bootstrap-artifacts-'));
  const marker = 'ambient-secret-marker';
  try {
    writeFileSync(join(evidence, 'bootstrap.json'), JSON.stringify({
      status: 'failed', directory: `C:\\ambient\\${marker}`,
      error: `arbitrary failure ${marker}`
    }));
    writeFileSync(join(evidence, 'qualification.json'), JSON.stringify({
      status: 'failed', failure: { stage: 'bootstrap', code: 'operation-failed' },
      error: `arbitrary qualification error ${marker}`
    }));
    writeFileSync(join(evidence, 'native.tsv'), good);
    const result = spawnSync(process.execPath, [cli, '--prepare-artifacts'], {
      encoding: 'utf8', timeout: 5000,
      env: { ...process.env, WINDOWS_ETW_PROBE_EVIDENCE: evidence }
    });
    assert.equal(result.status, 0);
    assert.equal(existsSync(join(evidence, 'bootstrap.json')), true);
    const upload = join(evidence, 'upload');
    assert.deepEqual(readdirSync(upload).sort(), ['native.tsv', 'qualification.json']);
    for (const name of ['qualification.json', 'native.tsv']) {
      const contents = readFileSync(join(upload, name), 'utf8');
      assert.equal(contents.includes(marker), false);
    }
    assert.equal(result.stderr.includes(marker), false);
  } finally { rmSync(evidence, { recursive: true, force: true }); }
});

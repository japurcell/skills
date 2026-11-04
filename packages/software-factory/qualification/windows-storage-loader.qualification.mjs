// Explicit qualification-only entry. This file is excluded from recursive native
// discovery. It supplies no installed/product/storage loading authority.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { closeSync, openSync, readSync } from 'node:fs';
import { dirname, isAbsolute, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scope = 'windows-storage-loader-qualification';
const parserScope = 'windows-storage-loader-receipt-parser';
const nodeSha256 = 'd702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5';
const hex = (value, length = 64) => typeof value === 'string' && new RegExp(`^[0-9a-f]{${length}}$`).test(value);
const caseIds = new Set(['positive-user', 'positive-admin', 'acl-change', 'wrong-digest', 'missing-image',
  'changed-image', 'changed-parent', 'reparse-image', 'reparse-parent', 'hardlink', 'nonfile', 'broad-child',
  'broad-root', 'unprotected-root', 'denied-metadata', 'denied-sharing', 'wrong-arch', 'malformed-pe',
  'api-mismatch', 'extra-dll', 'conflicting-import', 'local-redirection', 'manifest-redirection', 'throw-before',
  'require-failure', 'throw-after', 'nonzero', 'stdout-overflow', 'stderr-overflow', 'timeout', 'retained-writer',
  'changed-selection', 'replaced-owned-file', 'oversized-artifact', 'synthetic-close', 'forged-success',
  'unknown-result', 'extra-result', 'synthetic-overflow-close']);
const phases = new Set(['selection', 'prerequisite', 'preflight', 'provision', 'custody', 'process',
  'protocol', 'modules', 'control', 'load', 'close', 'cleanup', 'complete']);
const reasons = new Set(['none', 'selection', 'runtime', 'platform', 'filesystem', 'identity', 'namespace',
  'owner', 'dacl', 'type', 'reparse', 'links', 'changed', 'missing', 'hash', 'source', 'receipt', 'artifact',
  'inventory', 'access', 'sharing', 'native', 'bounds', 'modules', 'control', 'deadline', 'eof', 'protocol',
  'before', 'after', 'loader', 'call', 'exit', 'close']);
const receiptFields = ['scope', 'case', 'state', 'phase', 'reason', 'selectionSha256', 'sourceCommit',
  'nodeSha256', 'artifactSha256', 'buildReceiptSha256', 'processStarted', 'processExit', 'stdoutEOF',
  'stderrEOF', 'ownedClose', 'capture', 'discard', 'stage'];
function parseReceipt(bytes, selectionSha256) {
  if (!hex(selectionSha256) || bytes.length > 1024) throw new Error('receipt');
  const wire = bytes.toString('utf8');
  const receipt = JSON.parse(wire);
  // The fixture emits one canonical closed record. This rejects duplicate keys,
  // trailing records, alternate escapes, invalid UTF-8 and extra whitespace.
  if (wire !== `${JSON.stringify(receipt)}\n` || !receipt || Array.isArray(receipt) ||
      Object.keys(receipt).length !== receiptFields.length || receiptFields.some(key => !Object.hasOwn(receipt, key)) ||
      receipt.scope !== 'windows-storage-loader-fixture' || !caseIds.has(receipt.case) ||
      !['pass', 'refused', 'unknown'].includes(receipt.state) || !phases.has(receipt.phase) || !reasons.has(receipt.reason) ||
      receipt.selectionSha256 !== selectionSha256 || !hex(receipt.sourceCommit, 40) ||
      receipt.nodeSha256 !== nodeSha256 || !hex(receipt.artifactSha256) || !hex(receipt.buildReceiptSha256) ||
      !['removed', 'retained', 'not-created'].includes(receipt.stage)) throw new Error('receipt');
  for (const field of ['processStarted', 'processExit', 'stdoutEOF', 'stderrEOF', 'ownedClose']) {
    if (typeof receipt[field] !== 'boolean') throw new Error('receipt');
  }
  for (const field of ['capture', 'discard']) {
    if (!Array.isArray(receipt[field]) || receipt[field].length !== 2 ||
        receipt[field].some(value => !Number.isInteger(value) || value < 0 || value > 8192)) throw new Error('receipt');
  }
  if (!receipt.processStarted && (receipt.processExit || receipt.stdoutEOF || receipt.stderrEOF ||
      receipt.capture.some(Boolean) || receipt.discard.some(Boolean))) throw new Error('receipt');
  if (receipt.ownedClose && receipt.processStarted && (!receipt.processExit || !receipt.stdoutEOF || !receipt.stderrEOF)) throw new Error('receipt');
  if (receipt.stage === 'removed' && !receipt.ownedClose) throw new Error('receipt');
  if (receipt.state === 'pass') {
    if (!['positive-user', 'positive-admin'].includes(receipt.case) || receipt.phase !== 'complete' || receipt.reason !== 'none' ||
        !receipt.processStarted || !receipt.processExit || !receipt.stdoutEOF || !receipt.stderrEOF || !receipt.ownedClose ||
        receipt.stage !== 'removed' || receipt.capture[0] === 0 || receipt.capture[1] !== 0 || receipt.discard.some(Boolean)) throw new Error('receipt');
  } else if (receipt.phase === 'complete' || receipt.reason === 'none') throw new Error('receipt');
  return receipt;
}
function boundedStdin() {
  const bytes = Buffer.alloc(1025);
  let length = 0;
  while (length < bytes.length) {
    const count = readSync(0, bytes, length, bytes.length - length, null);
    if (count === 0) break;
    length += count;
  }
  if (length > 1024) throw new Error('receipt');
  return bytes.subarray(0, length);
}
function refuseReceipt() {
  process.stdout.write(`${JSON.stringify({ scope: parserScope, state: 'refused', reason: 'receipt' })}\n`);
  process.exitCode = 1;
}

// Finite expected facts are independent of the controller's returned record.
// Every entry must run in order; no skip/filter/retry or relaxed expected result.
const nativeCases = [
  [1, 'positive-user', 'pass', 'complete', 'none', true],
  [1, 'positive-admin', 'pass', 'complete', 'none', true],
  [2, 'acl-change', 'refused', 'custody', 'dacl', true],
  [3, 'wrong-digest', 'refused', 'preflight', 'hash', false],
  [3, 'missing-image', 'refused', 'custody', 'missing', false],
  [3, 'changed-image', 'refused', 'custody', 'changed', false],
  [3, 'changed-parent', 'refused', 'custody', 'changed', false],
  [3, 'reparse-image', 'refused', 'custody', 'reparse', false],
  [3, 'reparse-parent', 'refused', 'custody', 'reparse', false],
  [3, 'hardlink', 'refused', 'custody', 'links', false],
  [3, 'nonfile', 'refused', 'custody', 'type', false],
  [3, 'broad-child', 'refused', 'custody', 'dacl', false],
  [3, 'broad-root', 'refused', 'custody', 'dacl', false],
  [3, 'unprotected-root', 'refused', 'custody', 'dacl', false],
  [3, 'denied-metadata', 'refused', 'custody', 'access', false],
  [3, 'denied-sharing', 'refused', 'custody', 'sharing', false],
  [4, 'wrong-arch', 'refused', 'preflight', 'artifact', false],
  [4, 'malformed-pe', 'refused', 'preflight', 'artifact', false],
  [4, 'api-mismatch', 'refused', 'load', 'loader', true],
  [4, 'extra-dll', 'refused', 'preflight', 'inventory', false],
  [4, 'conflicting-import', 'refused', 'preflight', 'inventory', false],
  [4, 'local-redirection', 'refused', 'preflight', 'inventory', false],
  [4, 'manifest-redirection', 'refused', 'preflight', 'inventory', false],
  [5, 'throw-before', 'refused', 'load', 'before', true],
  [5, 'require-failure', 'refused', 'load', 'loader', true],
  [5, 'throw-after', 'refused', 'load', 'after', true],
  [5, 'nonzero', 'refused', 'process', 'exit', true],
  [5, 'stdout-overflow', 'refused', 'protocol', 'bounds', true],
  [5, 'stderr-overflow', 'refused', 'protocol', 'bounds', true],
  [5, 'timeout', 'unknown', 'process', 'deadline', true],
  [5, 'retained-writer', 'unknown', 'process', 'eof', true],
  [6, 'changed-selection', 'refused', 'custody', 'changed', false],
  [6, 'replaced-owned-file', 'refused', 'cleanup', 'changed', true],
  [6, 'oversized-artifact', 'refused', 'preflight', 'bounds', false],
  [6, 'synthetic-close', 'unknown', 'close', 'close', true],
  [6, 'synthetic-overflow-close', 'refused', 'protocol', 'bounds', true],
  [6, 'forged-success', 'unknown', 'modules', 'modules', true],
  [6, 'unknown-result', 'refused', 'protocol', 'protocol', true],
  [6, 'extra-result', 'refused', 'protocol', 'protocol', true],
];
const sourceFiles = ['qualification/windows-storage-loader-fixture.py', 'qualification/windows-storage-loader-canary.c',
  'qualification/windows-storage-loader-child.mjs', 'qualification/windows-storage-loader.qualification.mjs',
  'test/windows-storage-loader-contract.test.mjs', 'qualification/windows-storage-loader.md'];
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
let progress = { case: 'prerequisite', phase: 'prerequisite' };
function boundedFile(path, cap) {
  const descriptor = openSync(path, 'r');
  try {
    const buffer = Buffer.alloc(cap + 1);
    let size = 0;
    while (size < buffer.length) {
      const count = readSync(descriptor, buffer, size, buffer.length - size, null);
      if (count === 0) break;
      size += count;
    }
    if (size > cap) throw new Error('prerequisite');
    return buffer.subarray(0, size);
  } finally { closeSync(descriptor); }
}
function digestFile(path, cap) {
  const descriptor = openSync(path, 'r');
  try {
    const hash = createHash('sha256');
    const buffer = Buffer.alloc(65536);
    let total = 0;
    while (total <= cap) {
      const count = readSync(descriptor, buffer, 0, Math.min(buffer.length, cap + 1 - total), null);
      if (count === 0) break;
      total += count;
      if (total > cap) throw new Error('prerequisite');
      hash.update(buffer.subarray(0, count));
    }
    return hash.digest('hex');
  } finally { closeSync(descriptor); }
}
function closedObservation(bytes, caseId, selectedSha) {
  try {
    const value = parseReceipt(bytes, selectedSha);
    return { state: value.state, phase: value.phase, reason: value.reason, processStarted: value.processStarted,
      processExit: value.processExit, stdoutEOF: value.stdoutEOF, stderrEOF: value.stderrEOF,
      ownedClose: value.ownedClose, capture: value.capture, discard: value.discard, stage: value.stage };
  } catch {
    try {
      if (bytes.length > 1024) return undefined;
      const value = JSON.parse(bytes.toString('utf8'));
      if (value.scope === 'windows-storage-loader-fixture' && value.case === caseId &&
          ['refused', 'unknown'].includes(value.state) && phases.has(value.phase) && value.phase !== 'complete' &&
          reasons.has(value.reason) && value.reason !== 'none') {
        return { state: value.state, phase: value.phase, reason: value.reason };
      }
    } catch { /* Unvalidated bytes never escape. */ }
    return undefined;
  }
}
function nativeExperiment() {
  assert.equal(process.platform, 'win32');
  assert.equal(process.arch, 'x64');
  assert.equal(process.version, 'v24.22.1');
  const python = process.env.FACTORY_WINDOWS_LOADER_PYTHON;
  const selectionPath = process.env.FACTORY_WINDOWS_LOADER_SELECTION;
  const selectedSha = process.env.FACTORY_WINDOWS_LOADER_SELECTION_SHA256;
  assert.ok(python && selectionPath && isAbsolute(python) && isAbsolute(selectionPath) && hex(selectedSha));
  const raw = boundedFile(selectionPath, 1024 * 1024);
  assert.equal(sha(raw), selectedSha);
  const selected = JSON.parse(raw.toString('utf8'));
  // The controller/interpreter trust basis was accepted before this JS starts.
  // These digest comparisons corroborate frozen inputs, not first-execution
  // authority obtained by hashing or running a candidate interpreter.
  assert.equal(digestFile(python, 128 * 1024 * 1024), selected.pythonSha256);
  const packageRoot = dirname(dirname(fileURLToPath(import.meta.url)));
  const fixture = join(packageRoot, 'qualification/windows-storage-loader-fixture.py');
  const buildPath = join(selected.inputRoot, 'control/build-receipt.json');
  const buildBytes = boundedFile(buildPath, 1024 * 1024);
  assert.equal(sha(buildBytes), selected.buildReceiptSha256);
  const build = JSON.parse(buildBytes.toString('utf8'));
  const freeze = () => {
    assert.equal(sha(boundedFile(selectionPath, 1024 * 1024)), selectedSha);
    assert.equal(sha(boundedFile(buildPath, 1024 * 1024)), selected.buildReceiptSha256);
    assert.equal(digestFile(python, 128 * 1024 * 1024), selected.pythonSha256);
    assert.equal(digestFile(process.execPath, 128 * 1024 * 1024), nodeSha256);
    assert.deepEqual(Object.keys(selected.sourceSha256).sort(), [...sourceFiles].sort());
    for (const path of sourceFiles) assert.equal(sha(boundedFile(join(packageRoot, path), 1024 * 1024)), selected.sourceSha256[path]);
  };
  freeze();
  const transcript = createHash('sha256');
  for (const [group, caseId, state, phase, reason, started] of nativeCases) {
    progress = { case: caseId, group, phase: 'postflight' };
    freeze();
    progress.phase = 'transport';
    const result = spawnSync(python, ['-I', '-S', fixture, '--selection', selectionPath,
      '--sha256', selectedSha, '--case', caseId], {
      encoding: 'buffer', stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true,
      timeout: 35000, maxBuffer: 8192,
      env: { SystemRoot: process.env.SystemRoot, WINDIR: process.env.SystemRoot,
        PATH: `${dirname(python)};${join(process.env.SystemRoot ?? '', 'System32')}` },
    });
    progress.observed = closedObservation(result.stdout ?? Buffer.alloc(0), caseId, selectedSha);
    // The 35s outer cutoff can end an inert UNKNOWN controller. It never turns
    // that OS teardown into owned custody/closure evidence or an expected pass.
    assert.equal(result.error, undefined);
    assert.equal(result.signal, null);
    assert.equal(result.stderr?.length, 0);
    assert.equal(result.status, state === 'pass' ? 0 : 1);
    progress.phase = 'receipt';
    const receipt = parseReceipt(result.stdout, selectedSha);
    progress.phase = 'case';
    assert.equal(receipt.case, caseId);
    assert.equal(receipt.sourceCommit, selected.sourceCommit);
    assert.equal(receipt.buildReceiptSha256, selected.buildReceiptSha256);
    const variant = caseId === 'api-mismatch' ? 'apiMismatch' : caseId === 'wrong-arch' ? 'wrongArch' : 'positive';
    assert.equal(receipt.artifactSha256, build.artifacts[variant].sha256);
    assert.deepEqual([receipt.state, receipt.phase, receipt.reason], [state, phase, reason]);
    assert.equal(receipt.processStarted, started);
    assert.equal(receipt.processExit, started);
    assert.equal(receipt.stdoutEOF, started);
    assert.equal(receipt.stderrEOF, started);
    assert.equal(receipt.ownedClose, !['synthetic-close', 'synthetic-overflow-close'].includes(caseId));
    if (state === 'pass') assert.equal(receipt.stage, 'removed');
    if (state === 'unknown' || ['replaced-owned-file', 'synthetic-overflow-close'].includes(caseId)) assert.equal(receipt.stage, 'retained');
    if (['stdout-overflow', 'stderr-overflow', 'synthetic-overflow-close'].includes(caseId)) {
      assert.equal(receipt.reason, 'bounds'); // Never overwritten by later cleanup.
      assert.ok(receipt.discard.some(value => value > 0));
    }
    if (caseId === 'extra-result') assert.doesNotMatch(result.stdout.toString('utf8'), /loader-private-output-canary/);
    transcript.update(JSON.stringify({ group, ...receipt }));
    progress.phase = 'postflight';
    freeze();
  }
  assert.deepEqual([...new Set(nativeCases.map(value => value[0]))], [1, 2, 3, 4, 5, 6]);
  assert.equal(nativeCases.length, caseIds.size);
  return { scope, state: 'complete', cases: nativeCases.length, selectionSha256: selectedSha,
    sourceCommit: selected.sourceCommit, nodeSha256, artifactSha256: selected.artifactSha256,
    buildReceiptSha256: selected.buildReceiptSha256, transcriptSha256: transcript.digest('hex') };
}
if (process.argv.length === 4 && process.argv[2] === '--validate-receipt') {
  try {
    parseReceipt(boundedStdin(), process.argv[3]);
    process.stdout.write(`${JSON.stringify({ scope: parserScope, state: 'validated', reason: 'none' })}\n`);
  } catch { refuseReceipt(); }
} else if (process.argv.length === 3 && process.argv[2] === '--native') {
  try { process.stdout.write(`${JSON.stringify(nativeExperiment())}\n`); }
  catch {
    process.stdout.write(`${JSON.stringify({ scope, state: 'refused', case: progress.case,
      reason: progress.phase, ...(progress.group ? { group: progress.group } : {}),
      ...(progress.observed ? { observed: progress.observed } : {}) })}\n`);
    process.exitCode = 1;
  }
} else {
  process.stdout.write(`${JSON.stringify({ scope, state: 'refused', reason: 'prerequisite' })}\n`);
  process.exitCode = 1;
}

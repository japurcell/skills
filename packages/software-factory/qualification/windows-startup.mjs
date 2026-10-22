// Qualification protocol only. This file is not imported by the factory runtime.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync } from 'node:fs';
import { join, resolve, sep } from 'node:path';

export const gitModes = Object.freeze([
  ['--no-pager', '--no-lazy-fetch', 'rev-parse', '--show-toplevel'],
  ['--no-pager', '--no-lazy-fetch', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
  ['--no-pager', '--no-lazy-fetch', 'rev-parse', '--path-format=absolute', '--git-dir'],
  ['--no-pager', '--no-lazy-fetch', 'worktree', 'list', '--porcelain', '-z'],
].map((mode) => Object.freeze(mode)));

// A scoped config query does not follow includes unless explicitly requested.
export const includedConfigQuery = Object.freeze(['config', '--global', '--includes', '--get', 'core.fsmonitor']);

export function selectLaunchMode(value = 'no-window') {
  assert.ok(value === 'no-window' || value === 'detached-process',
    `unsupported qualification launch mode: ${String(value)}`);
  return value;
}

const traceKinds = new Set(['ROOT', 'CREATE', 'DLL', 'EXIT', 'STOP_REQUESTED', 'STOP_OBSERVED', 'DONE', 'ERROR']);

export function parseTrace(contents) {
  const records = [];
  for (const line of contents.replace(/^\uFEFF/, '').split(/\r?\n/).filter(Boolean)) {
    const cells = line.split('\t');
    assert.equal(cells.length, 3, 'malformed debug trace row');
    const [kind, pidText, encoded] = cells;
    assert.ok(traceKinds.has(kind), `unknown debug trace event ${kind}`);
    assert.match(pidText, /^(0|[1-9]\d*)$/, 'invalid debug trace PID');
    assert.match(encoded, /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/, 'invalid debug trace data');
    records.push({ kind, pid: Number(pidText), value: Buffer.from(encoded, 'base64').toString('utf8') });
  }
  return records;
}

export function validateTrace(records, rootPid, expectChild, expectedChildImage) {
  const reasons = [];
  const roots = records.filter((record) => record.kind === 'ROOT');
  const created = records.filter((record) => record.kind === 'CREATE');
  const exits = records.filter((record) => record.kind === 'EXIT');
  const done = records.filter((record) => record.kind === 'DONE');
  const children = created.filter((record) => record.pid !== rootPid);
  if (roots.length !== 1 || roots[0].pid !== rootPid) reasons.push('missing or ambiguous root');
  if (created.filter((record) => record.pid === rootPid).length !== 1) reasons.push('missing or ambiguous root creation');
  if (exits.filter((record) => record.pid === rootPid).length !== 1) reasons.push('missing or ambiguous root exit');
  if (done.length !== 1 || done[0].pid !== rootPid || done[0].value !== exits.find((record) => record.pid === rootPid)?.value)
    reasons.push('missing or inconsistent completed debug loop');
  if (records.some((record) => ['STOP_REQUESTED', 'STOP_OBSERVED', 'ERROR'].includes(record.kind)))
    reasons.push('debug trace interrupted or uncertain');
  if (expectChild && children.length === 0) reasons.push('positive child control not observed');
  if (expectedChildImage && !children.some((child) => child.value && normalized(child.value) === normalized(expectedChildImage)))
    reasons.push('intended positive child image not observed');
  if (!expectChild && children.length !== 0) reasons.push('unexpected child process created');
  if (children.some((child) => exits.filter((record) => record.pid === child.pid).length !== 1))
    reasons.push('child exit unobserved');
  return { ok: reasons.length === 0, reasons, children };
}

export function validateStopTrace(records, rootPid, reason, expectedRootImage) {
  const reasons = [];
  const rows = (kind) => records.filter((record) => record.kind === kind);
  const roots = rows('ROOT');
  const created = rows('CREATE');
  const exits = rows('EXIT');
  const requests = rows('STOP_REQUESTED');
  const observed = rows('STOP_OBSERVED');
  const done = rows('DONE');
  const rootExit = exits.find((record) => record.pid === rootPid);
  if (roots.length !== 1 || roots[0].pid !== rootPid) reasons.push('missing or ambiguous root');
  if (created.filter((record) => record.pid === rootPid).length !== 1)
    reasons.push('missing or ambiguous root creation');
  if (created.some((record) => created.filter((other) => other.pid === record.pid).length !== 1))
    reasons.push('ambiguous process creation');
  if (expectedRootImage && [roots[0]?.value, created.find((record) => record.pid === rootPid)?.value]
    .some((image) => !image || normalized(image) !== normalized(expectedRootImage)))
    reasons.push('root image differs from control executable');
  if (exits.filter((record) => record.pid === rootPid).length !== 1)
    reasons.push('stopped root exit unobserved');
  if (rootExit?.value !== '124') reasons.push('root was not terminated with code 124');
  if (created.some((record) => record.pid !== rootPid &&
      exits.filter((exit) => exit.pid === record.pid).length !== 1))
    reasons.push('child exit unobserved');
  if (exits.some((record) => !created.some((createdRecord) => createdRecord.pid === record.pid)))
    reasons.push('exit without creation');
  if (requests.length !== 1 || requests[0].pid !== rootPid) reasons.push('missing stop request');
  else if (requests[0].value !== reason) reasons.push('wrong stop reason');
  if (observed.length !== 1 || observed[0].pid !== rootPid || observed[0].value !== rootExit?.value)
    reasons.push('stop completion unobserved');
  if (done.length !== 1 || done[0].pid !== rootPid || done[0].value !== `stopped:${rootExit?.value}` ||
      records.at(-1) !== done[0])
    reasons.push('missing or inconsistent completed debug loop');
  if (records.some((record) => record.kind === 'ERROR')) reasons.push('stop trace reported error');
  const requestIndex = records.indexOf(requests[0]);
  const rootExitIndex = records.indexOf(rootExit);
  const observedIndex = records.indexOf(observed[0]);
  if (requestIndex < 0 || rootExitIndex < requestIndex || observedIndex < rootExitIndex ||
      exits.some((record) => records.indexOf(record) > observedIndex))
    reasons.push('stop event order inconsistent');
  return { ok: reasons.length === 0, reasons };
}

const absolutePath = (path) => resolve(path.replace(/^\\\\\?\\/, ''));
const normalized = (path) => absolutePath(path).toLowerCase();

export function validateModules(records, executable, archive, windows, expectedGitDlls = []) {
  const root = records.find((record) => record.kind === 'CREATE');
  assert.ok(root?.value && normalized(root.value) === normalized(executable), 'debugged root image differs from exact executable');
  const modules = records.filter((record) => record.kind === 'DLL');
  assert.ok(modules.length > 0, 'no loaded module events for fixed helper');
  const packageRoot = normalized(archive.root) + sep;
  const systemRoot = normalized(windows) + sep;
  const loaded = new Set();
  for (const record of modules) {
    assert.equal(record.pid, root.pid, 'loaded module event belongs to unknown process');
    assert.ok(record.value, 'unresolved loaded module path');
    const actualPath = absolutePath(record.value);
    const path = normalized(record.value);
    assert.ok(existsSync(actualPath), `loaded module path does not exist: ${record.value}`);
    loaded.add(path);
    if (path.startsWith(packageRoot)) {
      const member = path.slice(packageRoot.length).replaceAll('\\', '/');
      assert.ok(archive.files[member], `loaded module absent from pinned archive: ${record.value}`);
      assert.equal(createHash('sha256').update(readFileSync(actualPath)).digest('hex'), archive.files[member],
        `loaded module bytes changed: ${member}`);
    } else {
      assert.ok(path.startsWith(systemRoot), `loaded module outside pinned archive and Windows root: ${record.value}`);
    }
  }
  for (const member of expectedGitDlls)
    assert.ok(loaded.has(normalized(join(archive.root, 'mingw64', 'bin', member))),
      `expected pinned Git dependency was not observed: ${member}`);
}

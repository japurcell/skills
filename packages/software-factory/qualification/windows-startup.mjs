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

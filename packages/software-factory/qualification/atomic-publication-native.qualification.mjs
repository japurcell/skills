import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, realpathSync, statSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { atomicPublicationMove } from '../src/atomic-publication.ts';

const python = process.env.FACTORY_ATOMIC_PYTHON;
if (!python) throw new Error('FACTORY_ATOMIC_PYTHON is required');
const helper = resolve('native/atomic-publication.py');
const identity = path => { const s = statSync(path, { bigint: true }); return `${s.dev}:${s.ino}`; };
const file = path => ({ path: realpathSync(path), identity: identity(path), sha256: createHash('sha256').update(readFileSync(path)).digest('hex') });
test('moves a bound directory into an absent destination', async () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-atomic-')));
  const source = join(root, 'source'), destination = join(root, 'destination');
  mkdirSync(source, { mode: 0o700 });
  const input = { source, destination, sourceIdentity: identity(source), sourceParentIdentity: identity(root),
    destinationParentIdentity: identity(root), binding: { interpreter: file(python), helper: file(helper) } };
  assert.equal(await atomicPublicationMove(input), 'moved');
  assert.equal(identity(destination), input.sourceIdentity);
});

for (const kind of ['empty', 'nonempty', 'file', 'link']) {
  test(`preserves an existing ${kind} target`, async () => {
    const { writeFileSync, symlinkSync, lstatSync } = await import('node:fs');
    const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-atomic-')));
    const source = join(root, 'source'), destination = join(root, 'destination');
    mkdirSync(source, { mode: 0o700 });
    if (kind === 'empty' || kind === 'nonempty') mkdirSync(destination, { mode: 0o700 });
    if (kind === 'nonempty') writeFileSync(join(destination, 'keep'), 'preserve');
    if (kind === 'file') writeFileSync(destination, 'preserve');
    if (kind === 'link') symlinkSync('missing', destination);
    const before = lstatSync(destination, { bigint: true });
    const input = { source, destination, sourceIdentity: identity(source), sourceParentIdentity: identity(root),
      destinationParentIdentity: identity(root), binding: { interpreter: file(python), helper: file(helper) } };
    assert.equal(await atomicPublicationMove(input), 'collision');
    assert.equal(lstatSync(destination, { bigint: true }).ino, before.ino);
    assert.equal(identity(source), input.sourceIdentity);
    if (kind === 'nonempty') assert.equal(readFileSync(join(destination, 'keep'), 'utf8'), 'preserve');
    if (kind === 'file') assert.equal(readFileSync(destination, 'utf8'), 'preserve');
  });
}

test('refuses incorrect source or parent identity and tampered bindings', async () => {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-atomic-'))), source = join(root, 'source');
  mkdirSync(source, { mode: 0o700 });
  const input = { source, destination: join(root, 'destination'), sourceIdentity: identity(source),
    sourceParentIdentity: identity(root), destinationParentIdentity: identity(root),
    binding: { interpreter: file(python), helper: file(helper) } };
  for (const key of ['sourceIdentity', 'sourceParentIdentity', 'destinationParentIdentity'])
    assert.equal(await atomicPublicationMove({ ...input, [key]: '1:1' }), 'refused');
  for (const key of ['interpreter', 'helper'])
    assert.equal(await atomicPublicationMove({ ...input, binding: { ...input.binding,
      [key]: { ...input.binding[key], sha256: '0'.repeat(64) } } }), 'refused');
  assert.equal(identity(source), input.sourceIdentity);
});

test('helper rejects malformed, oversized and extra-field requests without disclosure', async () => {
  const { spawnSync } = await import('node:child_process');
  for (const request of ['{', 'x'.repeat(16385), JSON.stringify({ secret: 'DO_NOT_DISCLOSE' })]) {
    const result = spawnSync(realpathSync(python), ['-I', '-S', '-B', helper], { input: request, encoding: 'utf8', env: {} });
    assert.equal(result.status, 0);
    assert.equal(result.stdout, 'refused\n');
    assert.equal(result.stderr, '');
  }
});

test('returns unknown when the managed helper times out', async () => {
  const { writeFileSync } = await import('node:fs');
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-atomic-'))), source = join(root, 'source');
  mkdirSync(source, { mode: 0o700 });
  const script = join(root, 'slow.py');
  writeFileSync(script, 'import time\ntime.sleep(60)\n');
  const input = { source, destination: join(root, 'destination'), sourceIdentity: identity(source),
    sourceParentIdentity: identity(root), destinationParentIdentity: identity(root),
    binding: { interpreter: file(python), helper: file(script) } };
  const start = Date.now();
  assert.equal(await atomicPublicationMove(input), 'unknown');
  assert.ok(Date.now() - start < 14000);
  assert.equal(identity(source), input.sourceIdentity);
});

test('rejects unexpected helper output as unknown', async () => {
  const { writeFileSync } = await import('node:fs');
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-atomic-'))), source = join(root, 'source');
  mkdirSync(source, { mode: 0o700 });
  const script = join(root, 'invalid.py');
  writeFileSync(script, "print('private unexpected output')\n");
  const input = { source, destination: join(root, 'destination'), sourceIdentity: identity(source),
    sourceParentIdentity: identity(root), destinationParentIdentity: identity(root),
    binding: { interpreter: file(python), helper: file(script) } };
  assert.equal(await atomicPublicationMove(input), 'unknown');
});

test('returns unknown when a success response lacks matching namespace evidence', async () => {
  const { writeFileSync } = await import('node:fs');
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-atomic-'))), source = join(root, 'source');
  mkdirSync(source, { mode: 0o700 });
  const script = join(root, 'false-success.py');
  writeFileSync(script, "print('moved')\n");
  const input = { source, destination: join(root, 'destination'), sourceIdentity: identity(source),
    sourceParentIdentity: identity(root), destinationParentIdentity: identity(root),
    binding: { interpreter: file(python), helper: file(script) } };
  assert.equal(await atomicPublicationMove(input), 'unknown');
});

for (const outcomeMode of ['normal', 'error']) test(`closes owned descendants after ${outcomeMode} helper exit without affecting an unrelated process`, async () => {
  const { writeFileSync, rmSync } = await import('node:fs');
  const { spawn } = await import('node:child_process');
  const { once } = await import('node:events');
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-atomic-'))), source = join(root, 'source');
  mkdirSync(source, { mode: 0o700 });
  const script = join(root, 'descendant.py'), pidFile = join(root, 'child.pid');
  writeFileSync(script, `import subprocess, sys\np = subprocess.Popen([sys.executable, '-I', '-S', '-B', '-c', 'import time; time.sleep(60)'], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\nwith open(${JSON.stringify(pidFile)}, 'w') as f: f.write(str(p.pid))\n${outcomeMode === 'normal' ? "print('moved')" : 'sys.exit(7)'}\n`);
  const unrelated = spawn(realpathSync(python), ['-I', '-S', '-B', '-c', 'import time; time.sleep(60)'],
    { detached: true, stdio: 'ignore' });
  let fixturePid;
  try {
    await once(unrelated, 'spawn');
    const input = { source, destination: join(root, 'destination'), sourceIdentity: identity(source),
      sourceParentIdentity: identity(root), destinationParentIdentity: identity(root),
      binding: { interpreter: file(python), helper: file(script) } };
    const started = Date.now();
    const outcome = await atomicPublicationMove(input);
    fixturePid = Number(readFileSync(pidFile, 'utf8'));
    assert.equal(outcome, 'unknown');
    assert.ok(Number.isSafeInteger(fixturePid) && fixturePid > 1);
    assert.throws(() => process.kill(fixturePid, 0), { code: 'ESRCH' });
    assert.doesNotThrow(() => process.kill(unrelated.pid, 0));
    assert.ok(Date.now() - started < 12000);
    assert.equal(identity(source), input.sourceIdentity);
  } finally {
    if (fixturePid) try { process.kill(fixturePid, 'SIGKILL'); } catch (error) { if (error.code !== 'ESRCH') throw error; }
    if (unrelated.exitCode === null && unrelated.signalCode === null) unrelated.kill('SIGKILL');
    await once(unrelated, 'close');
    rmSync(root, { recursive: true, force: true });
  }
});

test('refuses interpreter changed while the helper is authenticated', async () => {
  const { copyFileSync, writeFileSync, truncateSync, existsSync, rmSync } = await import('node:fs');
  const { spawn } = await import('node:child_process');
  const { once } = await import('node:events');
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'factory-atomic-'))), source = join(root, 'source');
  mkdirSync(source, { mode: 0o700 });
  const script = join(root, 'large.py'), interpreter = join(root, 'python'), ready = join(root, 'ready'), changed = join(root, 'changed');
  copyFileSync(realpathSync(python), interpreter);
  writeFileSync(script, "print('refused')\n");
  truncateSync(script, 120 * 1024 * 1024);
  const binding = { interpreter: file(interpreter), helper: file(script) };
  const watcherCode = `import ctypes, os, sys, time\nscript, interpreter, ready, changed, parent = sys.argv[1:]\nparent = int(parent)\nif sys.platform == 'darwin':\n lib = ctypes.CDLL('/usr/lib/libproc.dylib')\n def opened():\n  for fd in range(3, 128):\n   data = ctypes.create_string_buffer(4096)\n   if lib.proc_pidfdinfo(parent, fd, 2, data, len(data)) > 0 and script.encode() in data.raw: return True\n  return False\nelif sys.platform == 'linux':\n def opened():\n  for fd in os.listdir('/proc/%d/fd' % parent):\n   try:\n    if os.readlink('/proc/%d/fd/%s' % (parent, fd)) == script: return True\n   except OSError: pass\n  return False\nelse: raise RuntimeError('unsupported test host')\nopen(ready, 'w').close()\nend = time.monotonic() + 8\nwhile time.monotonic() < end:\n if opened():\n  with open(interpreter, 'ab') as f: f.write(b'x')\n  open(changed, 'w').close()\n  break\n time.sleep(0.001)\n`;
  const watcher = spawn(realpathSync(python), ['-I', '-S', '-B', '-c', watcherCode, script, interpreter, ready, changed, String(process.pid)], { stdio: 'ignore' });
  const closed = once(watcher, 'close');
  try {
    const waitUntil = Date.now() + 3000;
    while (!existsSync(ready) && Date.now() < waitUntil) await new Promise(resolve => setTimeout(resolve, 5));
    assert.ok(existsSync(ready), 'watcher did not start');
    const input = { source, destination: join(root, 'destination'), sourceIdentity: identity(source),
      sourceParentIdentity: identity(root), destinationParentIdentity: identity(root), binding };
    const result = await atomicPublicationMove(input);
    await closed;
    assert.ok(existsSync(changed), 'helper access was not observed during verification');
    assert.equal(result, 'refused');
    assert.equal(identity(source), input.sourceIdentity);
  } finally {
    if (watcher.exitCode === null && watcher.signalCode === null) watcher.kill('SIGKILL');
    await closed;
    rmSync(root, { recursive: true, force: true });
  }
});

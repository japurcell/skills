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

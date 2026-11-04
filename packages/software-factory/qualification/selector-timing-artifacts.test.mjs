import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { createEvidenceRoot, createCollector, collectEvidence } from './selector-timing.mjs';
import { stageSelectorTimingExports } from './selector-timing-artifacts.mjs';

function fixture() {
  const directory = realpathSync(mkdtempSync(join(tmpdir(), 'selector-export-test-')));
  const root = createEvidenceRoot(), collector = createCollector(root);
  collector.mark('worker-open'); collector.close();
  const records = collectEvidence(root).records;
  const context = { sourceSha: 'a'.repeat(40), runtimeSha256: 'b'.repeat(64) };
  const metadata = { schema: 1, status: 'incomplete', ...context, node: 'v24.22.1', platform: 'darwin', arch: 'arm64',
    availableParallelism: 3, runtimeOsRelease: '24.6.0', runnerImage: 'macos15', runnerImageVersion: '20261028.0489.1',
    fixtureExitCode: 1, clock: 'host-monotonic-ms', attemptClock: 'persisted-utc-wall', cpu: 'emitting-process-only', records: records.length };
  writeFileSync(join(directory, 'selector-timing.json'), JSON.stringify(metadata) + '\n', { mode: 0o600 });
  writeFileSync(join(directory, 'selector-timing.jsonl'), records.map(value => JSON.stringify(value) + '\n').join(''), { mode: 0o600 });
  return { directory, root, context, metadata, records, destination: join(directory, 'unused'),
    dispose() { rmSync(directory, { recursive: true, force: true }); rmSync(root.path, { recursive: true, force: true }); } };
}

test('artifact staging preserves valid incomplete red evidence and publishes exactly two validated files', () => {
  const f = fixture();
  try {
    const destination = join(f.root.path, 'upload');
    stageSelectorTimingExports(f.directory, destination, f.context);
    assert.deepEqual(readdirSync(destination).sort(), ['selector-timing.json', 'selector-timing.jsonl']);
    assert.deepEqual(JSON.parse(readFileSync(join(destination, 'selector-timing.json'), 'utf8')), f.metadata);
    assert.throws(() => stageSelectorTimingExports(f.directory, destination, f.context));
  } finally { f.dispose(); }
});

test('artifact staging refuses private fields, false complete coverage and mismatched source before publication', () => {
  for (const corruption of ['metadata', 'record', 'complete', 'source', 'duplicate']) {
    const f = fixture();
    try {
      if (corruption === 'metadata') f.metadata.pid = 123;
      if (corruption === 'complete') f.metadata.status = 'complete';
      if (corruption === 'source') f.metadata.sourceSha = 'c'.repeat(40);
      if (corruption === 'record') f.records[0].path = '/private-value';
      writeFileSync(join(f.directory, 'selector-timing.json'), JSON.stringify(f.metadata) + '\n');
      if (corruption === 'duplicate') writeFileSync(join(f.directory, 'selector-timing.json'), '{"sourceSha":"/private-value",' + JSON.stringify(f.metadata).slice(1) + '\n');
      writeFileSync(join(f.directory, 'selector-timing.jsonl'), f.records.map(value => JSON.stringify(value) + '\n').join(''));
      const destination = join(f.root.path, 'upload');
      assert.throws(() => stageSelectorTimingExports(f.directory, destination, f.context));
      assert.deepEqual(readdirSync(f.root.path).sort(), ['000.jsonl', 'owner.json']);
    } finally { f.dispose(); }
  }
});

test('artifact staging refuses extra files, linked files and oversized exports', () => {
  for (const corruption of ['extra', 'link', 'oversize']) {
    const f = fixture();
    try {
      const file = join(f.directory, 'selector-timing.jsonl');
      if (corruption === 'extra') writeFileSync(join(f.directory, 'private.json'), '{}');
      if (corruption === 'link') { rmSync(file); symlinkSync(join(f.root.path, '000.jsonl'), file); }
      if (corruption === 'oversize') writeFileSync(file, 'x'.repeat(16 * 1024 * 1024 + 1));
      assert.throws(() => stageSelectorTimingExports(f.directory, join(f.root.path, 'upload'), f.context));
    } finally { f.dispose(); }
  }
});

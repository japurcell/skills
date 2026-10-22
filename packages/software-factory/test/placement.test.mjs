import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { assertLocalPlacement } from '../src/placement.ts';

test('placement accepts a native local directory including literal shell metacharacters', () => {
  const root = mkdtempSync(join(tmpdir(), 'factory-placement-'));
  try {
    const directory = join(root, "literal ' $ ; [safe]");
    mkdirSync(directory);
    const result = assertLocalPlacement(directory);
    assert.equal(result.platform, process.platform);
    assert.ok(['apfs', 'hfs', 'ext', 'btrfs', 'xfs', 'NTFS', 'ReFS'].includes(result.filesystem));
    assert.ok(result.directory.endsWith("literal ' $ ; [safe]"));
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('placement refuses missing, non-directory and network paths without fallback storage', () => {
  const root = mkdtempSync(join(tmpdir(), 'factory-placement-'));
  try {
    const file = join(root, 'file');
    writeFileSync(file, '');
    assert.throws(() => assertLocalPlacement(file), /directory/);
    assert.throws(() => assertLocalPlacement(join(root, 'missing')));
    assert.throws(() => assertLocalPlacement(String.raw`\\server\share\factory`));
  } finally { rmSync(root, { recursive: true, force: true }); }
});

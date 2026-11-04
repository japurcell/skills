import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lstatSync, mkdtempSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';
import { dirname, join, relative } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { copyLearningToolchain } from '../test/fixtures/learning-toolchain-copy.mjs';

const source = fileURLToPath(new URL('../node_modules/', import.meta.url));
const names = ['typescript', '@types/node', 'undici-types', `@typescript/typescript-${process.platform}-${process.arch}`];

function inventory(root) {
  const entries = [];
  const visit = path => {
    for (const item of readdirSync(path, { withFileTypes: true })) {
      const full = join(path, item.name);
      const name = relative(root, full).split('\\').join('/');
      const info = lstatSync(full);
      assert.equal(info.isSymbolicLink(), false, `${name} must be a regular file or directory`);
      if (info.isDirectory()) visit(full);
      else {
        assert.equal(info.isFile(), true, `${name} must be a regular file`);
        const bytes = readFileSync(full);
        entries.push([name, info.mode & 0o777, bytes.length, createHash('sha256').update(bytes).digest('hex')]);
      }
    }
  };
  visit(root);
  return entries.sort((a, b) => a[0].localeCompare(b[0]));
}

test('selected learning compiler closure preserves regular-file bytes and remains independent', t => {
  const scratch = mkdtempSync(join(tmpdir(), 'learning-toolchain-copy-'));
  t.after(() => rmSync(scratch, { recursive: true, force: true }));
  const destination = join(scratch, 'node_modules');
  const sourcePath = source;
  copyLearningToolchain(sourcePath, destination);

  const expected = names.flatMap(name => inventory(join(sourcePath, name)).map(([path, ...rest]) => [`${name}/${path}`, ...rest]))
    .sort((a, b) => a[0].localeCompare(b[0]));
  const actual = inventory(destination);
  const differences = expected.filter((entry, index) => JSON.stringify(entry) !== JSON.stringify(actual[index]));
  assert.equal(actual.length, expected.length, 'copied compiler closure must preserve file count');
  assert.equal(differences.length, 0, `copied compiler closure differs: ${JSON.stringify(differences.slice(0, 3))}`);
  assert.deepEqual(readdirSync(destination).sort(), ['@types', '@typescript', 'typescript', 'undici-types']);

  const sourceFile = join(sourcePath, 'typescript/bin/tsc');
  const copiedFile = join(destination, 'typescript/bin/tsc');
  assert.notEqual(statSync(sourceFile).ino, statSync(copiedFile).ino, 'copied compiler must not share a mutable inode');
  const sourceBytes = readFileSync(sourceFile);
  writeFileSync(copiedFile, Buffer.concat([readFileSync(copiedFile), Buffer.from('\n// isolated copy probe\n')]));
  assert.deepEqual(readFileSync(sourceFile), sourceBytes);

  const compiler = spawnSync(process.execPath, [join(destination, 'typescript/bin/tsc'), '--version'], { encoding: 'utf8' });
  assert.equal(compiler.status, 0, compiler.stderr);
  assert.equal(compiler.stdout.trim(), 'Version 7.0.2');
});

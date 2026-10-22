import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const dispatch = fileURLToPath(new URL('../scripts/test.mjs', import.meta.url));
test('suite selection fails for unfinished suites, unmatched filters and unknown options', () => {
  for (const args of [['notifications'], ['fixtures', '--provider', 'missing'], ['fixtures', '--suite', 'browser'],
    ['fixtures', '--operation', 'upgrade'], ['qualification', '--area', 'missing'], ['fixtures', '--typo']]) {
    const result = spawnSync(process.execPath, [dispatch, ...args], { encoding: 'utf8', timeout: 5000 });
    assert.equal(result.status, 1, result.stderr);
    assert.match(result.stderr, /not implemented|no tests|Unknown option/);
  }
});

// The aggregate command refuses before spawning any unfinished feature suite.
test('aggregate selection reports notifications after workflow and server registration', () => {
  const result = spawnSync(process.execPath, [dispatch, 'all'], { encoding: 'utf8', timeout: 5000 });
  assert.equal(result.status, 1, result.stderr);
  assert.match(result.stderr, /notifications: not implemented; no tests registered/);
  assert.equal(result.stdout, '', 'aggregate refusal must precede launching registered suites');
});

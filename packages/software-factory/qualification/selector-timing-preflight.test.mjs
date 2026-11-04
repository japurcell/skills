import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

test('timing preflight refuses missing explicit native inputs before dependency execution', () => {
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_TEST_PYTHON;
  delete env.FACTORY_ATOMIC_PYTHON;
  delete env.FACTORY_TEST_NPM_CACHE_SEED;
  const result = spawnSync(process.execPath, [new URL('./selector-timing-preflight.mjs', import.meta.url).pathname], { env, encoding: 'utf8', timeout: 5000 });
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.equal(result.stderr, 'factory selector timing preflight: refused\n');
});

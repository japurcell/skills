import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

test('explicit installed qualification refuses a missing selected archive before Python or repository creation', () => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-native-prerequisite-'));
  try {
    const entry = fileURLToPath(new URL('../qualification/installed-cli-native.qualification.mjs', import.meta.url));
    const env = { ...process.env, FACTORY_TEST_NODE_ARCHIVE: join(directory, 'absent-node-archive'),
      FACTORY_TEST_PYTHON: join(directory, 'absent-python') };
    delete env.NODE_TEST_CONTEXT;
    const result = spawnSync(process.execPath, ['--test', entry], {
      encoding: 'utf8', timeout: 180_000,
      env,
    });
    assert.equal(result.status, 1, result.stdout + result.stderr);
    const supported = (process.platform === 'darwin' && process.arch === 'arm64')
      || (process.platform === 'linux' && process.arch === 'x64');
    assert.match(result.stdout + result.stderr, supported ? /exact pinned Node archive missing/
      : /native POSIX qualification requires darwin-arm64 or linux-x64/);
    assert.match(result.stdout + result.stderr, /tests 1/);
    assert.doesNotMatch(result.stdout + result.stderr, /skipping running files|tests 0/);
    assert.doesNotMatch(result.stdout + result.stderr, /public install failed|spawn.*absent-python/);
  } finally { rmSync(directory, { recursive: true, force: true }); }
});

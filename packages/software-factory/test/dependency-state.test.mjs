import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { createRepository } from './fixtures/repository.mjs';
import { inspectInstalledDependencyState } from '../dist/dependency-state.js';

test('read-only dependency inspection refuses an unowned repository without creating installation state', async () => {
  const repository = createRepository();
  try {
    const common = join(repository.path, '.git');
    await assert.rejects(inspectInstalledDependencyState(common, repository.path), /installed binding refused/);
    assert.equal(existsSync(join(common, 'factory')), false);
  } finally { repository.dispose(); }
});

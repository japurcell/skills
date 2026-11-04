import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { createRepository } from './fixtures/repository.mjs';
import { prepareDependencyBackup } from '../dist/dependency-maintenance.js';

test('backup preparation refuses an unowned repository without creating managed or attempt state', async () => {
  const repository = createRepository(), common = join(repository.path, '.git');
  try {
    await assert.rejects(prepareDependencyBackup(repository.path, { commonDir: common,
      operationId: '00000000-0000-4000-8000-000000000001', repositoryId: '00000000-0000-4000-8000-000000000002',
      claimId: '00000000-0000-4000-8000-000000000003', token: 'fixture' }));
    assert.equal(existsSync(join(common, 'factory')), false);
  } finally { repository.dispose(); }
});

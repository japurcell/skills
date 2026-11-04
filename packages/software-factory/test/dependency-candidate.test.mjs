import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { createRepository } from './fixtures/repository.mjs';
import { prepareDependencyCandidate } from '../dist/dependency-candidate.js';

test('candidate preparation refuses missing authenticated inputs without creating managed state', async () => {
  const repository = createRepository(), common = join(repository.path, '.git');
  try {
    await assert.rejects(prepareDependencyCandidate(join(repository.path, 'unowned-request.json'), {
      commonDir: common, operationId: '00000000-0000-4000-8000-000000000001',
      repositoryId: '00000000-0000-4000-8000-000000000002', claimId: '00000000-0000-4000-8000-000000000003', token: 'fixture' }));
    assert.equal(existsSync(join(common, 'factory')), false);
  } finally { repository.dispose(); }
});

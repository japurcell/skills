import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { createRepository } from './fixtures/repository.mjs';
import { beginMaintenance, inspectMaintenance } from '../dist/maintenance.js';
import { inspectDependencyMaintenanceSelection } from '../dist/dependency-maintenance.js';
import { currentOwner } from '../dist/native/process.js';
import { initializeRepositoryStore } from '../dist/store.js';

test('generic dependency admission refuses without an installed exact-selection binding', async () => {
  const repository = createRepository(), common = join(repository.path, '.git');
  let store;
  try {
    store = await initializeRepositoryStore(common, { release: 'fixture' });
    await assert.rejects(beginMaintenance(repository.path, 'dependencies', { release: 'fixture',
      selectionDigest: 'a'.repeat(64), targetReleaseSha256: 'b'.repeat(64), targetSchema: 7,
      artifactDigests: { bundle: 'b'.repeat(64) } }, currentOwner()), /exact installed selection admission/);
    assert.equal((await inspectMaintenance(repository.path)).claims, 0);
    assert.equal((await inspectMaintenance(repository.path)).status, 'ready');
    assert.equal(existsSync(join(common, 'factory/maintenance-backups')), false);
  } finally { store?.close(); repository.dispose(); }
});

test('dependency inspection rejects extra or unsupported selection before creating managed state', async () => {
  const repository = createRepository(), common = join(repository.path, '.git');
  try {
    for (const source of [
      { mode: 'install', bundleRoot: '/not-selected', manifestSha256: 'a'.repeat(64) },
      { mode: 'repair', bundleRoot: '/not-selected', manifestSha256: 'a'.repeat(64), providers: {} },
    ]) await assert.rejects(inspectDependencyMaintenanceSelection(repository.path, source), /exact fixed dependency repair selection/);
    assert.equal(existsSync(join(common, 'factory')), false);
  } finally { repository.dispose(); }
});

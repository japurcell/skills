import assert from 'node:assert/strict';
import { existsSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { createRepository } from './fixtures/repository.mjs';

test('development CLI remains unbound; an installed-shaped path without ownership refuses without creating storage', async () => {
  const { installedCommonForCli, loadInstalledBindings } = await import('../dist/installed-bindings.js');
  const repository = createRepository();
  try {
    const development = fileURLToPath(new URL('../dist/cli.js', import.meta.url));
    assert.equal(installedCommonForCli(development), null);
    assert.equal(await loadInstalledBindings(development, repository.path), null);
    const common = join(repository.path, '.git');
    const spoofed = join(common, 'factory/install/runtime/dist/cli.js');
    assert.equal(installedCommonForCli(spoofed), common);
    await assert.rejects(loadInstalledBindings(spoofed, repository.path), /installed binding refused/);
    assert.equal(existsSync(join(common, 'factory')), false);
  } finally { repository.dispose(); }
});

test('unqualified external provider bytes refuse adapter construction without a provider launch', async () => {
  const { createSelectedAdapters } = await import('../dist/installed-bindings.js');
  const repository = createRepository();
  try {
    const executable = join(realpathSync(repository.path), 'untracked.txt');
    const provider = { codex: { executable, version: '0.163.0', sha256: '0'.repeat(64),
      bytes: readFileSync(executable).length, model: 'gpt-6-luna', reasoning: 'low', modes: ['read-only'] } };
    assert.deepEqual(Object.keys(createSelectedAdapters({}, join(repository.path, '.git/factory'))), []);
    assert.throws(() => createSelectedAdapters(provider, join(repository.path, '.git/factory')),
      /bound Codex source differs/);
    writeFileSync(executable, 'changed external provider bytes');
    assert.throws(() => createSelectedAdapters(provider, join(repository.path, '.git/factory')),
      /bound Codex source differs/);
  } finally { repository.dispose(); }
});

import { constants, cpSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { invoke } from '../dist/lifecycle.js';
import { initializeRepositoryStore } from '../dist/store.js';
import { createRepository } from './fixtures/repository.mjs';

export async function createNotificationFixture(source) {
  const repo = createRepository();
  mkdirSync(join(repo.path, '.factory/workflows'), { recursive: true });
  writeFileSync(join(repo.path, '.factory/package.json'), '{"type":"module"}');
  writeFileSync(join(repo.path, '.factory/workflows/notice.ts'), source);
  repo.git(['add', '.factory']); repo.git(['commit', '-m', 'Commit notification fixture', '--only', '.factory']);
  const common = join(repo.path, '.git');
  const store = await initializeRepositoryStore(common, { release: 'fixture' }); store.close();
  const toolchain = join(common, 'factory/toolchain'); mkdirSync(toolchain);
  const sourceModules = new URL('../node_modules/', import.meta.url);
  const modules = join(toolchain, 'node_modules'); mkdirSync(modules);
  for (const name of ['typescript', '@types/node', 'undici-types', `@typescript/typescript-${process.platform}-${process.arch}`]) {
    const destination = join(modules, name);
    mkdirSync(dirname(destination), { recursive: true });
    cpSync(new URL(name, sourceModules), destination, {
      recursive: true,
      dereference: true,
      mode: constants.COPYFILE_FICLONE,
    });
  }
  writeFileSync(join(toolchain, 'manifest.json'), JSON.stringify({ schema: 1, node: '24.22.1', typescript: '7.0.2', dependencies: { '@types/node': '24.19.2' } }));
  const input = join(common, 'input.json'); writeFileSync(input, '{}');
  const run = (extra = {}) => invoke({ repository: repo.path, workflow: '.factory/workflows/notice.ts', input, newWorktree: true, ...extra });
  return { ...repo, common, input, run };
}

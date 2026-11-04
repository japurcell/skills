import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { rememberFixturePath, timingSync } from '../../qualification/selector-timing.mjs';

/** Each fixture owns its entire mkdtemp container; global Git identity/hooks stay untouched. */
export function createRepository() {
  return timingSync('repository', () => createRepositoryFixture());
}

function createRepositoryFixture() {
  const container = mkdtempSync(join(tmpdir(), 'factory-repository-'));
  const path = join(container, 'repository');
  const configuration = join(container, 'gitconfig');
  const hooks = join(container, 'hooks');
  const git = (args) => execFileSync('git', [
    '-c', 'core.hooksPath=' + hooks.replaceAll('\\', '/'), '-c', 'commit.gpgsign=false',
    '-c', 'user.name=Factory Fixture', '-c', 'user.email=fixture@example.invalid', ...args,
  ], { cwd: path, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], env: {
    PATH: process.env.PATH, SystemRoot: process.env.SystemRoot,
    GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: configuration,
  } });
  const dispose = () => timingSync('dispose', () => rmSync(container, { recursive: true, force: true }));
  try {
    mkdirSync(path, { mode: 0o700 });
    mkdirSync(hooks, { mode: 0o700 });
    writeFileSync(configuration, '', { mode: 0o600, flag: 'wx' });
    git(['init', '--initial-branch=main']);
    writeFileSync(join(path, '.gitignore'), 'ignored.txt\n');
    writeFileSync(join(path, 'tracked.txt'), 'committed\n');
    git(['add', '.gitignore', 'tracked.txt']);
    timingSync('commit', () => git(['commit', '-m', 'Create disposable fixture']));
    writeFileSync(join(path, 'tracked.txt'), 'staged\n');
    git(['add', 'tracked.txt']);
    writeFileSync(join(path, 'tracked.txt'), 'unstaged\n');
    writeFileSync(join(path, 'untracked.txt'), 'untracked\n');
    writeFileSync(join(path, 'ignored.txt'), 'ignored\n');
    rememberFixturePath(path);
    return { path, git, dispose };
  } catch (error) {
    dispose();
    throw error;
  }
}

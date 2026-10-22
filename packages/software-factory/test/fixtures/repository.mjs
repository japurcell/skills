import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { devNull, tmpdir } from 'node:os';
import { join } from 'node:path';

/** Each fixture owns only its mkdtemp directory; global Git identity/hooks stay untouched. */
export function createRepository() {
  const path = mkdtempSync(join(tmpdir(), 'factory-repository-'));
  const git = (args) => execFileSync('git', [
    '-c', 'core.hooksPath=' + devNull, '-c', 'commit.gpgsign=false',
    '-c', 'user.name=Factory Fixture', '-c', 'user.email=fixture@example.invalid', ...args,
  ], { cwd: path, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], env: {
    PATH: process.env.PATH, SystemRoot: process.env.SystemRoot,
    GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: devNull,
  } });
  const dispose = () => rmSync(path, { recursive: true, force: true });
  try {
    git(['init', '--initial-branch=main']);
    writeFileSync(join(path, '.gitignore'), 'ignored.txt\n');
    writeFileSync(join(path, 'tracked.txt'), 'committed\n');
    git(['add', '.gitignore', 'tracked.txt']);
    git(['commit', '-m', 'Create disposable fixture']);
    writeFileSync(join(path, 'tracked.txt'), 'staged\n');
    git(['add', 'tracked.txt']);
    writeFileSync(join(path, 'tracked.txt'), 'unstaged\n');
    writeFileSync(join(path, 'untracked.txt'), 'untracked\n');
    writeFileSync(join(path, 'ignored.txt'), 'ignored\n');
    return { path, git, dispose };
  } catch (error) {
    dispose();
    throw error;
  }
}

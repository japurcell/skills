import { execFileSync } from 'node:child_process';
import { existsSync, realpathSync } from 'node:fs';
import { resolve } from 'node:path';
import { devNull } from 'node:os';

export function git(repository: string, args: string[]) {
  return execFileSync('git', ['-c', `core.hooksPath=${devNull}`, ...args], { cwd: repository,
    encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], env: { PATH: process.env.PATH, SystemRoot: process.env['SystemRoot'], GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: devNull } }).trim();
}
export function repositoryIdentity(repository: string) {
  const root = realpathSync(git(repository, ['rev-parse', '--show-toplevel']));
  const common = realpathSync(git(root, ['rev-parse', '--path-format=absolute', '--git-common-dir']));
  return { root, common };
}
export function selectedCommit(repository: string, ref: string) {
  return git(repository, ['rev-parse', '--verify', '--end-of-options', `${ref}^{commit}`]);
}
export function worktreeIdentity(path: string, common: string) {
  const identity = repositoryIdentity(path);
  if (identity.root !== realpathSync(path) || identity.common !== common) throw new Error('worktree belongs to another repository');
  const registered = git(path, ['worktree', 'list', '--porcelain', '-z']).split('\0').some(field => field === `worktree ${identity.root}`);
  if (!registered) throw new Error('worktree is not registered with Git');
  return realpathSync(git(path, ['rev-parse', '--path-format=absolute', '--git-dir']));
}
export function createWorktree(repository: string, destination: string, commit: string) {
  if (existsSync(destination)) throw new Error('worktree destination collision');
  git(repository, ['worktree', 'add', '--detach', '--', resolve(destination), commit]);
}

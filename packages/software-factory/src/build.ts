import { existsSync, lstatSync, mkdirSync, readFileSync, realpathSync, symlinkSync, writeFileSync } from 'node:fs';
import { isAbsolute, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import type { CommandRunner } from './workflow.js';

function json(path: string): Record<string, unknown> { return JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown>; }
export async function buildWorkflow(options: { common: string; worktree: string; workflow: string; invocationId: string; runner: CommandRunner }) {
  const authoring = join(options.worktree, '.factory');
  if (!existsSync(authoring) || realpathSync(authoring) !== authoring) throw new Error('.factory authoring root must be inside selected worktree, not a symlink');
  const entry = resolve(options.worktree, options.workflow);
  const path = relative(authoring, entry);
  if ((isAbsolute(path) || path === '..' || path.startsWith(`..${sep}`)) || !path.endsWith('.ts') || !existsSync(entry) || realpathSync(entry) !== entry) throw new Error('workflow must be a current .factory TypeScript file in selected worktree');
  const toolchain = join(options.common, 'factory', 'toolchain');
  const modules = join(toolchain, 'node_modules');
  const compiler = join(modules, 'typescript', 'bin', 'tsc');
  try {
    const manifest = json(join(toolchain, 'manifest.json'));
    if (manifest['schema'] !== 1 || manifest['node'] !== process.versions.node || manifest['typescript'] !== '7.0.2'
      || (manifest['dependencies'] as Record<string, unknown>)?.['@types/node'] !== '24.19.2'
      || json(join(modules, 'typescript/package.json'))['version'] !== '7.0.2'
      || json(join(modules, '@types/node/package.json'))['version'] !== '24.19.2' || !existsSync(compiler)) throw new Error('mismatched toolchain');
  } catch { throw new Error('shared workflow dependencies missing or mismatched; explicitly install the pinned factory toolchain before invoking (startup never downloads)'); }
  const authored = json(join(authoring, 'package.json'));
  const installed = json(join(toolchain, 'manifest.json'))['dependencies'] as Record<string, unknown>;
  for (const section of ['dependencies', 'devDependencies']) {
    for (const [name, version] of Object.entries((authored[section] ?? {}) as Record<string, unknown>)) {
      if (name.includes('..') || name.includes('\\') || name.startsWith('/') || typeof version !== 'string' || installed[name] !== version) throw new Error(`workflow dependency ${name} missing or mismatched; explicitly install declared dependencies`);
      try { if (json(join(modules, name, 'package.json'))['version'] !== version) throw new Error('mismatch'); }
      catch { throw new Error(`workflow dependency ${name} missing or mismatched; explicitly install declared dependencies`); }
    }
  }
  if (authored['type'] !== 'module') throw new Error('.factory/package.json must explicitly declare type: module');
  const scaffold = join(authoring, 'node_modules');
  if (existsSync(scaffold) || (() => { try { lstatSync(scaffold); return true; } catch { return false; } })()) {
    if (!lstatSync(scaffold).isSymbolicLink() || realpathSync(scaffold) !== realpathSync(modules)) throw new Error('conflicting user-owned .factory/node_modules resolution scaffolding; refusing replacement');
  } else symlinkSync(modules, scaffold, process.platform === 'win32' ? 'junction' : 'dir');
  const builds = join(options.common, 'factory', 'builds');
  if (!existsSync(builds)) mkdirSync(builds, { mode: 0o700 });
  if (!lstatSync(builds).isDirectory() || lstatSync(builds).isSymbolicLink()) throw new Error('factory builds directory must not be a symlink');
  const output = join(builds, options.invocationId);
  mkdirSync(output, { mode: 0o700 });
  const config = join(output, 'tsconfig.json');
  const declaration = fileURLToPath(new URL('./workflow.d.ts', import.meta.url));
  writeFileSync(config, JSON.stringify({ compilerOptions: { target: 'ES2023', module: 'NodeNext', moduleResolution: 'NodeNext', strict: true, noImplicitAny: false,
    rootDir: authoring, outDir: join(output, 'code'), types: ['node'], typeRoots: [join(modules, '@types')], skipLibCheck: false,
    paths: { '@local/software-factory': [declaration] } }, files: [entry] }));
  await options.runner.execute(`startup/build/${options.invocationId}`, { argv: [process.execPath, compiler, '-p', config], env: {} }, true);
  symlinkSync(modules, join(output, 'code', 'node_modules'), process.platform === 'win32' ? 'junction' : 'dir');
  writeFileSync(join(output, 'code', 'package.json'), '{"type":"module"}');
  // Emitted relative imports resolve within this one immutable invocation build.
  const loaded = await import(pathToFileURL(join(output, 'code', path.replace(/\.ts$/, '.js'))).href) as { run?: unknown };
  if (typeof loaded.run !== 'function') throw new Error('workflow must export run(context, inputs)');
  return loaded.run as (context: import('./workflow.js').WorkflowContext, inputs: Record<string, unknown>) => Promise<unknown>;
}

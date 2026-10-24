import { lstatSync, readFileSync, realpathSync } from 'node:fs';
import { isAbsolute, dirname } from 'node:path';
import { backup, DatabaseSync } from 'node:sqlite';
import { pathToFileURL } from 'node:url';
import { assertForwardRuntime } from './schema-forward.js';

// This fixed entry executes only a private controller request. It emits no source paths or claim secrets.
async function main() {
  assertForwardRuntime();
  if (process.platform === 'win32') throw new Error('forward backup private ownership is unqualified on Windows');
  if (process.argv.length !== 4 || process.argv[2] !== '--request') throw new Error('invalid backup invocation');
  const requestPath = process.argv[3]!;
  const stat = lstatSync(requestPath);
  if (!isAbsolute(requestPath) || !stat.isFile() || stat.isSymbolicLink() || stat.nlink !== 1
    || stat.size < 1 || stat.size > 8192 || (stat.mode & 0o077) !== 0
    || realpathSync(requestPath) !== requestPath) throw new Error('invalid private backup request');
  const request: unknown = JSON.parse(readFileSync(requestPath, 'utf8'));
  if (!request || typeof request !== 'object' || Array.isArray(request)) throw new Error('invalid backup request');
  const { source, target } = request as { source?: unknown; target?: unknown };
  if (Object.keys(request).sort().join(',') !== 'source,target' || typeof source !== 'string' || typeof target !== 'string'
    || !isAbsolute(source) || !isAbsolute(target) || source === target)
    throw new Error('invalid backup paths');
  const origin = lstatSync(source), parent = lstatSync(dirname(target));
  if (!origin.isFile() || origin.isSymbolicLink() || origin.nlink !== 1 || realpathSync(source) !== source
    || !parent.isDirectory() || parent.isSymbolicLink() || realpathSync(dirname(target)) !== dirname(target))
    throw new Error('invalid backup source or target parent');
  for (const suffix of ['-wal', '-shm', '-journal']) {
    let sidecar;
    try { sidecar = lstatSync(`${source}${suffix}`); }
    catch (error) { if ((error as NodeJS.ErrnoException).code === 'ENOENT') continue; throw error; }
    if (!sidecar.isFile() || sidecar.isSymbolicLink() || sidecar.nlink !== 1 || (sidecar.mode & 0o077) !== 0)
      throw new Error('invalid backup source sidecar');
  }
  try { lstatSync(target); throw new Error('backup target already exists'); }
  catch (error) { if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error; }
  process.umask(0o077);
  const url = pathToFileURL(source); url.searchParams.set('mode', 'ro');
  const database = new DatabaseSync(url, { readOnly: true, timeout: 100 });
  try {
    await backup(database, target, { rate: 64 });
  } finally { database.close(); }
  // The parent waits for the entire owned group to exit before trusting this result.
  process.stdout.write('{"completed":true}\n');
}

main().catch(() => { process.stderr.write('forward backup failed\n'); process.exitCode = 1; });

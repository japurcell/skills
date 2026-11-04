import { createHash } from 'node:crypto';
import { closeSync, constants, fstatSync, lstatSync, openSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

/** Authenticate a previously owned manifest without imposing the new release's pins. */
export function readOwnedReleaseManifest(runtime: string, expectedSha256: string) {
  if (!/^[a-f0-9]{64}$/.test(expectedSha256)) throw new Error('owned manifest digest invalid');
  const path = join(runtime, 'release-manifest.json'), observed = lstatSync(path);
  if (!observed.isFile() || observed.isSymbolicLink() || observed.nlink !== 1 || observed.size < 1 || observed.size > 1024 * 1024)
    throw new Error('owned manifest file invalid');
  const fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
  try {
    const before = fstatSync(fd), bytes = readFileSync(fd), after = fstatSync(fd), current = lstatSync(path);
    if (before.dev !== observed.dev || before.ino !== observed.ino || after.dev !== before.dev || after.ino !== before.ino
      || after.size !== before.size || after.mtimeMs !== before.mtimeMs || after.ctimeMs !== before.ctimeMs
      || current.dev !== before.dev || current.ino !== before.ino || current.nlink !== 1
      || createHash('sha256').update(bytes).digest('hex') !== expectedSha256) throw new Error('owned manifest changed');
    const manifest: unknown = JSON.parse(bytes.toString('utf8'));
    if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest)) throw new Error('owned manifest invalid');
    const value = manifest as Record<string, unknown>, node = value['node'];
    if (value['schema'] !== 2 || typeof value['version'] !== 'string' || value['version'].length < 1
      || typeof value['platform'] !== 'string' || !node || typeof node !== 'object' || Array.isArray(node)
      || typeof (node as Record<string, unknown>)['sha256'] !== 'string'
      || !/^[a-f0-9]{64}$/.test((node as Record<string, string>)['sha256']!)) throw new Error('owned manifest shape invalid');
    return { version: value['version'], platform: value['platform'], node: { sha256: (node as Record<string, string>)['sha256']! } };
  } finally { closeSync(fd); }
}

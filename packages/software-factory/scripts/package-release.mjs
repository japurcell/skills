import { lstatSync, readFileSync } from 'node:fs';
import { isAbsolute, resolve } from 'node:path';
import { parseArgs } from 'node:util';
import { fileURLToPath } from 'node:url';
import { packageRelease } from '../src/release.ts';

try {
  const { values, positionals } = parseArgs({ options: {
    descriptor: { type: 'string' },
    'source-root': { type: 'string' },
    destination: { type: 'string' },
  } });
  if (positionals.length || !values.descriptor || !values.destination) throw new Error('usage: node scripts/package-release.mjs --descriptor ABSOLUTE_JSON --destination ABSOLUTE_DIRECTORY [--source-root ABSOLUTE_PACKAGE_ROOT]');
  const sourceRoot = values['source-root'] ?? resolve(fileURLToPath(new URL('../', import.meta.url)));
  if (![values.descriptor, values.destination, sourceRoot].every(isAbsolute)) throw new Error('all paths must be absolute');
  const descriptor = lstatSync(values.descriptor);
  if (!descriptor.isFile() || descriptor.size > 16_384) throw new Error('release descriptor must be a bounded regular file');
  const selection = JSON.parse(readFileSync(values.descriptor, 'utf8'));
  const { manifest, manifestSha256 } = packageRelease(selection, sourceRoot, values.destination);
  process.stdout.write(`${JSON.stringify({ destination: values.destination, version: manifest.version, platform: manifest.platform, manifestSha256, files: manifest.files.length })}\n`);
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
}

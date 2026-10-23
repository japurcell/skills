import { existsSync, lstatSync, realpathSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { scanOwnedTree } from './install-candidate.js';
import { inspectMaintenance } from './maintenance.js';

async function main(): Promise<void> {
  if (process.argv.length !== 3 || process.argv[2] !== '--self-check') throw new Error('publication unavailable');
  const dist = dirname(fileURLToPath(import.meta.url)), payload = dirname(dist);
  const executable = join(payload, process.platform === 'win32' ? 'node.exe' : 'node');
  if (realpathSync(process.execPath) !== executable || !lstatSync(executable).isFile()
    || !existsSync(join(payload, 'package.json')) || resolve(payload) !== payload)
    throw new Error('staged controller executable or package differs');
  scanOwnedTree(dist, 'candidate');
  if (typeof inspectMaintenance !== 'function') throw new Error('staged controller import closure unavailable');
  process.stdout.write('{"selfCheck":"ok"}\n');
}
main().catch(error => {
  process.stderr.write(`staged controller: ${error instanceof Error ? error.message : 'self-check failed'}\n`);
  process.exitCode = 1;
});

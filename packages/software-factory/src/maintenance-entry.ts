import { existsSync, lstatSync, realpathSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { scanOwnedTree } from './install-candidate.js';
import { consumeMaintenanceHandoff, inspectMaintenance } from './maintenance.js';
import { publishFirstInstall } from './install-publication.js';

async function main(): Promise<void> {
  if ((process.argv.length !== 3 || process.argv[2] !== '--self-check')
    && (process.argv.length !== 4 || process.argv[2] !== '--ticket')) throw new Error('private staged controller request required');
  const dist = dirname(fileURLToPath(import.meta.url)), payload = dirname(dist);
  const executable = join(payload, process.platform === 'win32' ? 'node.exe' : 'node');
  if (realpathSync(process.execPath) !== executable || !lstatSync(executable).isFile()
    || !existsSync(join(payload, 'package.json')) || resolve(payload) !== payload)
    throw new Error('staged controller executable or package differs');
  scanOwnedTree(dist, 'candidate');
  if (typeof inspectMaintenance !== 'function') throw new Error('staged controller import closure unavailable');
  if (process.argv[2] === '--self-check') process.stdout.write('{"selfCheck":"ok"}\n');
  else {
    await consumeMaintenanceHandoff(process.argv[3]!);
    process.stdout.write(`${JSON.stringify(await publishFirstInstall(process.argv[3]!))}\n`);
  }
}
main().catch(error => {
  const message = error instanceof Error ? error.message : 'self-check failed';
  process.stderr.write(`staged controller: ${message.replace(/[A-Za-z]:\\(?:[^\\\s]+\\)*[^\\\s]+/g, '[private-path]')
    .replace(/(?:\/[A-Za-z0-9._-]+){2,}/g, '[private-path]').slice(0, 200)}\n`);
  process.exitCode = 1;
});

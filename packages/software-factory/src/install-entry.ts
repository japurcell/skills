import { prepareInstallCandidate } from './install.js';

async function main(): Promise<void> {
  if (process.argv.length !== 4 || process.argv[2] !== '--request') throw new Error('private install request required');
  const prepared = await prepareInstallCandidate(process.argv[3]!);
  process.stdout.write(`${JSON.stringify(prepared)}\n`);
}
main().catch(error => {
  // Request paths and private token never belong in a public diagnostic.
  const message = error instanceof Error ? error.message : 'unknown preparation failure';
  process.stderr.write(`install prepare: ${message.replace(/(?:\/[A-Za-z0-9._-]+){2,}/g, '[private-path]').slice(0, 200)}\n`);
  process.exitCode = 1;
});

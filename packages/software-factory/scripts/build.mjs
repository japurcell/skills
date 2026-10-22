import { spawnSync } from 'node:child_process';
import { cpSync, existsSync, rmSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { buildInputSnapshot, recordBuildReceipt } from '../src/release.ts';

const root = new URL('../', import.meta.url);
const rootPath = resolve(fileURLToPath(root));
const compiler = new URL('../node_modules/typescript/bin/tsc', import.meta.url);
const receipt = new URL('../node_modules/.factory-build-receipt.json', import.meta.url);
rmSync(receipt, { force: true });
if (!existsSync(compiler)) {
  process.stderr.write('factory build: compiler missing; explicitly run npm ci in the development package\n');
  process.exitCode = 1;
} else {
  const inputs = buildInputSnapshot(rootPath);
  const result = spawnSync(process.execPath, [fileURLToPath(compiler), '-p', 'tsconfig.json'], {
    cwd: root, stdio: 'inherit',
  });
  if (result.error) process.stderr.write(`${result.error.message}\n`);
  process.exitCode = result.status ?? 1;
  if (process.exitCode === 0 && existsSync(new URL('../web', import.meta.url))) {
    cpSync(new URL('../web', import.meta.url), new URL('../dist/web', import.meta.url), { recursive: true });
    recordBuildReceipt(rootPath, inputs);
  }
}

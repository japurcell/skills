import { spawnSync } from 'node:child_process';
import { cpSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const compiler = new URL('../node_modules/typescript/bin/tsc', import.meta.url);
if (!existsSync(compiler)) {
  process.stderr.write('factory build: compiler missing; explicitly run npm ci in the development package\n');
  process.exitCode = 1;
} else {
  const result = spawnSync(process.execPath, [fileURLToPath(compiler), '-p', 'tsconfig.json'], {
    cwd: root, stdio: 'inherit',
  });
  if (result.error) process.stderr.write(`${result.error.message}\n`);
  process.exitCode = result.status ?? 1;
  if (process.exitCode === 0 && existsSync(new URL('../web', import.meta.url))) {
    cpSync(new URL('../web', import.meta.url), new URL('../dist/web', import.meta.url), { recursive: true });
  }
}

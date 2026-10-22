import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const cli = fileURLToPath(new URL('../dist/cli.js', import.meta.url));
test('CLI help lists development invocation and history while incomplete input refuses startup', () => {
  const help = spawnSync(process.execPath, [cli, '--help'], { encoding: 'utf8' });
  assert.equal(help.status, 0, help.stderr);
  assert.match(help.stdout, /software-factory/);
  assert.match(help.stdout, /development/);
  assert.match(help.stdout, /invoke/);
  assert.match(help.stdout, /history/);
  const invocation = spawnSync(process.execPath, [cli, 'invoke', '--json'], { encoding: 'utf8' });
  assert.equal(invocation.status, 3);
  assert.equal(invocation.stdout, '');
  assert.equal(invocation.stderr, 'software-factory: --repository is required\n');
});

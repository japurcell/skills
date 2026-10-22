import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const cli = fileURLToPath(new URL('../dist/cli.js', import.meta.url));
test('CLI help states development availability and unfinished commands refuse startup', () => {
  const help = spawnSync(process.execPath, [cli, '--help'], { encoding: 'utf8' });
  assert.equal(help.status, 0, help.stderr);
  assert.match(help.stdout, /software-factory/);
  assert.match(help.stdout, /development/);
  const invocation = spawnSync(process.execPath, [cli, 'invoke', '--json'], { encoding: 'utf8' });
  assert.equal(invocation.status, 3);
  assert.equal(invocation.stdout, '');
  assert.match(invocation.stderr, /not implemented/);
});

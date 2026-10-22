import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { join } from 'node:path';
import { once } from 'node:events';
import { createRepository } from './fixtures/repository.mjs';
import { initializeRepositoryStore, openRepositoryStore } from '../dist/store.js';
import { startObservationHost } from '../dist/dashboard.js';
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

test('dashboard CLI offers an owner handoff and releases its own claim on termination', async () => {
  const repo = createRepository();
  const seed = await initializeRepositoryStore(join(repo.path, '.git'), { release: 'fixture' }); seed.close();
  const child = spawn(process.execPath, [cli, 'dashboard', '--repository', repo.path], { stdio: ['ignore', 'pipe', 'pipe'] });
  let stdout = '', stderr = '';
  child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
  child.stdout.on('data', value => { stdout += value; }); child.stderr.on('data', value => { stderr += value; });
  try {
    const deadline = Date.now() + 3000;
    while (!stdout.includes('\n') && Date.now() < deadline && child.exitCode === null) await new Promise(resolve => setTimeout(resolve, 20));
    assert.match(stdout, /^http:\/\/127\.0\.0\.1:\d+\/#handoff=[0-9a-f-]+\n$/);
    const link = new URL(stdout.trim());
    const ticket = link.hash.slice('#handoff='.length);
    assert.equal((await fetch(link.origin + '/api/runs')).status, 403);
    const redeemed = await fetch(link.origin + '/api/ui-session', { method: 'POST', headers: { Origin: link.origin, 'Content-Type': 'application/json' }, body: JSON.stringify({ ticket }) });
    assert.equal(redeemed.status, 200);
    const { sessionToken } = await redeemed.json();
    assert.equal((await fetch(link.origin + '/api/runs', { headers: { Authorization: 'Bearer ' + sessionToken } })).status, 200);
    child.kill('SIGTERM'); await once(child, 'exit');
    assert.equal(child.exitCode, 0, stderr);
    const store = openRepositoryStore(join(repo.path, '.git'));
    try { assert.equal(store.readDashboardClaim(), undefined); } finally { store.close(); }
  } finally { if (child.exitCode === null) { child.kill('SIGTERM'); await once(child, 'exit'); } repo.dispose(); }
});

test('dashboard CLI refuses a cross-process host without closing its owner', async () => {
  const repo=createRepository();
  const store=await initializeRepositoryStore(join(repo.path,'.git'),{release:'fixture'});
  let host;
  try {
    host=await startObservationHost({store});
    const claimed=store.readDashboardClaim().id;
    const child=spawn(process.execPath,[cli,'dashboard','--repository',repo.path],{stdio:['ignore','pipe','pipe']});
    let stdout='',stderr='';
    child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
    child.stdout.on('data',value=>{stdout+=value;}); child.stderr.on('data',value=>{stderr+=value;});
    const [exitCode]=await once(child,'exit');
    assert.equal(exitCode,3);
    assert.equal(stdout,'');
    assert.match(stderr,/handoff unavailable/);
    assert.equal(store.readDashboardClaim().id,claimed);
    assert.equal((await fetch(host.url+'/api/runs',{headers:{Authorization:'Bearer '+host.sessionToken}})).status,200);
  } finally {await host?.close();store.close();repo.dispose();}
});

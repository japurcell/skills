import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { once } from 'node:events';
import { setTimeout as delay } from 'node:timers/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const harness = fileURLToPath(new URL('./fixtures/fake-harness.mjs', import.meta.url));

test('fixture harness emits streams and a separate final result without a provider', () => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-harness-'));
  try {
    const resultPath = join(directory, 'result.json');
    const result = spawnSync(process.execPath, [harness, '--mode', 'success', '--result', resultPath], {
      encoding: 'utf8', timeout: 5000,
    });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout, 'fixture output\n');
    assert.equal(result.stderr, 'fixture diagnostic\n');
    assert.deepEqual(JSON.parse(readFileSync(resultPath, 'utf8')), {
      kind: 'result', payload: { summary: 'fixture complete' },
    });
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('fixture pauses after launch with a real child and releases without leaked pipes', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-pause-'));
  const release = join(directory, 'release');
  const launch = join(directory, 'launch.json');
  const child = spawn(process.execPath, [harness, '--mode', 'success', '--result', join(directory, 'result.json'),
    '--child', '--launch-log', launch, '--pause-until', release], { stdio: ['ignore', 'pipe', 'pipe'] });
  let stderr = '';
  child.stdout.resume();
  child.stderr.on('data', (chunk) => { stderr += chunk; });
  const closed = once(child, 'close');
  try {
    const deadline = Date.now() + 5000;
    while (!existsSync(launch) && Date.now() < deadline && child.exitCode === null) await delay(10);
    assert.ok(existsSync(launch), stderr);
    const launched = JSON.parse(readFileSync(launch, 'utf8'));
    assert.equal(launched.pid, child.pid);
    assert.equal(typeof launched.childPid, 'number');
    process.kill(launched.childPid, 0);
    assert.equal(child.exitCode, null);
    writeFileSync(release, 'release');
    const [status] = await Promise.race([closed, delay(5000, undefined, { ref: false }).then(() => { throw new Error('fixture pipes did not close'); })]);
    assert.equal(status, 0, stderr);
    assert.throws(() => process.kill(launched.childPid, 0), { code: 'ESRCH' });
  } finally {
    if (child.exitCode === null) child.kill('SIGTERM');
    await closed;
    rmSync(directory, { recursive: true, force: true });
  }
});

test('repository fixture keeps committed, staged, unstaged, untracked and ignored content distinct', async () => {
  const { createRepository } = await import('./fixtures/repository.mjs');
  const repository = createRepository();
  try {
    assert.equal(repository.git(['show', 'HEAD:tracked.txt']), 'committed\n');
    assert.equal(repository.git(['show', ':tracked.txt']), 'staged\n');
    assert.equal(readFileSync(join(repository.path, 'tracked.txt'), 'utf8'), 'unstaged\n');
    assert.equal(repository.git(['status', '--short']), 'MM tracked.txt\n?? untracked.txt\n');
    assert.equal(repository.git(['check-ignore', 'ignored.txt']), 'ignored.txt\n');
  } finally {
    repository.dispose();
  }
});

test('launch report becomes visible only after its complete JSON is available', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-launch-publication-'));
  const launch = join(directory, 'launch.json');
  const writing = join(directory, 'writing');
  const permit = join(directory, 'permit');
  const release = join(directory, 'release');
  const preload = join(directory, 'pause-write.mjs');
  // Pause a real filesystem write after file creation. An existence-based
  // consumer must never discover a partially published launch report.
  writeFileSync(preload, `import fs from 'node:fs';
import {syncBuiltinESMExports} from 'node:module';
const write=fs.writeFileSync;
const open=fs.openSync;
const pause=()=>{
  write(${JSON.stringify(writing)},'ready');
  const until=Date.now()+5000;
  while(!fs.existsSync(${JSON.stringify(permit)})&&Date.now()<until)Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,10);
};
fs.openSync=function(path,...options){
  const descriptor=open(path,...options);
  if(typeof path==='string'&&path.startsWith(${JSON.stringify(launch)}))pause();
  return descriptor;
};
fs.writeFileSync=function(path,data,...options){
  if(typeof path==='string'&&path.startsWith(${JSON.stringify(launch)})){
    const descriptor=open(path,options[0]?.flag??'w',options[0]?.mode??0o666);
    try{
      pause();
      return write(descriptor,data,...options);
    }finally{fs.closeSync(descriptor);}
  }
  return write(path,data,...options);
};
syncBuiltinESMExports();
`);
  const child = spawn(process.execPath, ['--import', preload, harness, '--mode', 'success',
    '--result', join(directory, 'result.json'), '--launch-log', launch, '--pause-until', release],
    { stdio: ['ignore', 'ignore', 'pipe'] });
  let stderr = '';
  child.stderr.on('data', chunk => { stderr += chunk; });
  const closed = once(child, 'close');
  try {
    const deadline = Date.now() + 5000;
    while (!existsSync(writing) && Date.now() < deadline && child.exitCode === null) await delay(10);
    assert.ok(existsSync(writing), stderr);
    assert.equal(existsSync(launch), false, 'a consumer discovered an incomplete launch report');
    writeFileSync(permit, 'continue');
    while (!existsSync(launch) && Date.now() < deadline && child.exitCode === null) await delay(10);
    assert.ok(existsSync(launch), stderr);
    assert.deepEqual(JSON.parse(readFileSync(launch, 'utf8')), { pid: child.pid });
    writeFileSync(release, 'release');
    const [status] = await closed;
    assert.equal(status, 0, stderr);
  } finally {
    writeFileSync(permit, 'continue');
    if (child.exitCode === null) child.kill('SIGTERM');
    await closed;
    rmSync(directory, { recursive: true, force: true });
  }
});

test('fixture harness exposes needs-input, permission denial, malformed and crash outcomes', () => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-outcomes-'));
  try {
    for (const [mode, status] of [['needs-input', 2], ['permission-denied', 1], ['malformed', 0], ['crash', 70]]) {
      const resultPath = join(directory, `${mode}.json`);
      const result = spawnSync(process.execPath, [harness, '--mode', mode, '--result', resultPath], {
        encoding: 'utf8', timeout: 5000,
      });
      assert.equal(result.status, status, `${mode}: ${result.stderr}`);
      if (mode === 'needs-input') {
        assert.deepEqual(JSON.parse(readFileSync(resultPath, 'utf8')), {
          kind: 'needs_input', question: 'Which fixture target?', context: 'Fixture requires an explicit target.',
        });
      } else if (mode === 'permission-denied') {
        assert.match(result.stderr, /permission denied/);
      } else if (mode === 'malformed') {
        assert.throws(() => JSON.parse(readFileSync(resultPath, 'utf8')));
      }
    }
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('launch report collision preserves a pre-existing temporary file', () => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-launch-collision-'));
  const launch = join(directory, 'launch.json');
  const preload = join(directory, 'seed-collision.mjs');
  writeFileSync(preload, `import {writeFileSync} from 'node:fs';writeFileSync(${JSON.stringify(launch)}+'.'+process.pid+'.tmp','existing caller file');`);
  try {
    const child = spawnSync(process.execPath, ['--import', preload, harness, '--mode', 'success',
      '--result', join(directory, 'result.json'), '--launch-log', launch], { encoding: 'utf8', timeout: 5000 });
    assert.equal(child.error, undefined, 'a timeout is not evidence of collision refusal');
    assert.equal(child.signal, null);
    assert.equal(child.status, 1, 'a colliding temporary path must be refused');
    assert.match(child.stderr, /\bEEXIST\b/);
    const temporary = join(directory, 'launch.json.' + child.pid + '.tmp');
    assert.equal(existsSync(temporary), true, 'failed exclusive creation deleted an unowned file');
    assert.equal(readFileSync(temporary, 'utf8'), 'existing caller file');
    assert.equal(existsSync(launch), false);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

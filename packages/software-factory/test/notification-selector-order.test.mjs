import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { setTimeout as delay } from 'node:timers/promises';

const runnerUrl = new URL('../scripts/ordered-tests.mjs', import.meta.url).href;

function fixture(t, { concurrency = 1, cancellable = false } = {}) {
  const directory = mkdtempSync(join(tmpdir(), 'factory-test-order-'));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const script = join(directory, 'run.mjs');
  writeFileSync(script, `import { runOrderedTests } from ${JSON.stringify(runnerUrl)};
    const controller = new AbortController();
    ${cancellable ? "process.on('SIGTERM', () => controller.abort());" : ''}
    const result = await runOrderedTests(process.argv.slice(2), { concurrency: ${concurrency}, cwd: process.cwd(), signal: controller.signal });
    process.exitCode = controller.signal.aborted ? 143 : result;\n`);
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  return { directory, script, env };
}

test('registered file priority controls execution rather than alphabetic reporting', (t) => {
  const { directory, script, env } = fixture(t);
  const receipt = join(directory, 'execution.log');
  const priority = join(directory, 'z-priority.test.mjs');
  const tail = join(directory, 'a-tail.test.mjs');
  writeFileSync(priority, `import test from 'node:test'; import { appendFileSync } from 'node:fs'; test('priority', () => appendFileSync(process.env.ORDER_RECEIPT, 'priority\\n'));\n`);
  writeFileSync(tail, `import test from 'node:test'; import { appendFileSync } from 'node:fs'; test('tail', () => appendFileSync(process.env.ORDER_RECEIPT, 'tail\\n'));\n`);
  env.ORDER_RECEIPT = receipt;
  const result = spawnSync(process.execPath, [script, priority, tail], { cwd: directory, env, encoding: 'utf8', timeout: 5000 });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.equal(readFileSync(receipt, 'utf8'), 'priority\ntail\n');
  assert.match(result.stdout, /# tests 2/);
});

test('four worker slots start the priority files before queued files', { timeout: 8000 }, async (t) => {
  const { directory, script, env } = fixture(t, { concurrency: 4 });
  const release = join(directory, 'release');
  const names = ['z-priority-1', 'z-priority-2', 'z-priority-3', 'a-tail-4', 'b-tail-5', 'c-tail-6'];
  const files = names.map((name, index) => {
    const path = join(directory, `${name}.test.mjs`);
    writeFileSync(path, `import test from 'node:test'; import { writeFileSync, existsSync } from 'node:fs'; import { setTimeout as delay } from 'node:timers/promises';
      test(${JSON.stringify(name)}, async () => { writeFileSync(${JSON.stringify(join(directory, `started-${index}`))}, String(process.pid)); while (!existsSync(${JSON.stringify(release)})) await delay(10); });\n`);
    return path;
  });
  const child = spawn(process.execPath, [script, ...files], { cwd: directory, env, stdio: ['ignore', 'pipe', 'pipe'] });
  const output = [];
  child.stdout.on('data', (chunk) => output.push(chunk));
  child.stderr.on('data', (chunk) => output.push(chunk));
  let timeout;
  try {
    for (let attempt = 0; attempt < 200 && ![0, 1, 2, 3].every((index) => existsSync(join(directory, `started-${index}`))); attempt++) await delay(20);
    const started = names.map((_, index) => existsSync(join(directory, `started-${index}`)));
    assert.deepEqual(started, [true, true, true, true, false, false], Buffer.concat(output).toString());
    writeFileSync(release, 'release');
    const [code] = await Promise.race([
      new Promise((resolve) => child.once('close', (...args) => resolve(args))),
      new Promise((_, reject) => { timeout = setTimeout(() => reject(new Error('ordered runner did not close')), 4000); }),
    ]);
    assert.equal(code, 0, Buffer.concat(output).toString());
    assert.match(Buffer.concat(output).toString(), /# tests 6/);
  } finally {
    clearTimeout(timeout);
    writeFileSync(release, 'release');
    if (child.exitCode === null) child.kill('SIGKILL');
    for (let index = 0; index < names.length; index++) {
      const marker = join(directory, `started-${index}`);
      if (!existsSync(marker)) continue;
      try { process.kill(Number(readFileSync(marker, 'utf8')), 'SIGKILL'); }
      catch (error) { if (error.code !== 'ESRCH') throw error; }
    }
  }
});

test('a failed file still reports every selected case and exits nonzero', (t) => {
  const { directory, script, env } = fixture(t);
  const failure = join(directory, 'z-failure.test.mjs');
  const success = join(directory, 'a-success.test.mjs');
  writeFileSync(failure, `import test from 'node:test'; import assert from 'node:assert/strict'; test('synthetic failure', () => assert.fail('sentinel failure'));\n`);
  writeFileSync(success, `import test from 'node:test'; test('synthetic success', () => {});\n`);
  const result = spawnSync(process.execPath, [script, failure, success], { cwd: directory, env, encoding: 'utf8', timeout: 5000 });
  assert.equal(result.status, 1, result.stdout + result.stderr);
  assert.match(result.stdout, /sentinel failure/);
  assert.match(result.stdout, /# tests 2/);
  assert.match(result.stdout, /# fail 1/);
});

test('empty, skipped and missing selected files cannot produce a passing run', (t) => {
  const { directory, script, env } = fixture(t);
  const empty = join(directory, 'empty.test.mjs');
  writeFileSync(empty, 'export {};\n');
  const emptyResult = spawnSync(process.execPath, [script, empty], { cwd: directory, env, encoding: 'utf8', timeout: 5000 });
  assert.equal(emptyResult.status, 1, emptyResult.stdout + emptyResult.stderr);
  assert.match(emptyResult.stderr, /incomplete test execution/);
  const skipped = join(directory, 'skipped.test.mjs');
  writeFileSync(skipped, `import test from 'node:test'; test.skip('skipped case', () => {});\n`);
  const skippedResult = spawnSync(process.execPath, [script, skipped], { cwd: directory, env, encoding: 'utf8', timeout: 5000 });
  assert.equal(skippedResult.status, 1, skippedResult.stdout + skippedResult.stderr);
  assert.match(skippedResult.stdout, /# skipped 1/);
  const missingResult = spawnSync(process.execPath, [script, join(directory, 'missing.test.mjs')], { cwd: directory, env, encoding: 'utf8', timeout: 5000 });
  assert.equal(missingResult.status, 1, missingResult.stdout + missingResult.stderr);
  assert.match(missingResult.stdout, /not ok/);
});

test('cancellation closes the running child without starting the queued case', { timeout: 5000 }, async (t) => {
  const { directory, script, env } = fixture(t, { cancellable: true });
  const started = join(directory, 'started');
  const tailReceipt = join(directory, 'tail');
  const hanging = join(directory, 'z-hanging.test.mjs');
  const tail = join(directory, 'a-tail.test.mjs');
  writeFileSync(hanging, `import test from 'node:test'; import { writeFileSync } from 'node:fs'; test('hanging', async () => { writeFileSync(process.env.STARTED, String(process.pid)); await new Promise(() => setInterval(() => {}, 1000)); });\n`);
  writeFileSync(tail, `import test from 'node:test'; import { writeFileSync } from 'node:fs'; test('tail', () => writeFileSync(process.env.TAIL_RECEIPT, 'ran'));\n`);
  env.STARTED = started;
  env.TAIL_RECEIPT = tailReceipt;
  const child = spawn(process.execPath, [script, hanging, tail], { cwd: directory, env, stdio: ['ignore', 'pipe', 'pipe'] });
  const output = [];
  child.stdout.on('data', (chunk) => output.push(chunk));
  child.stderr.on('data', (chunk) => output.push(chunk));
  let timeout;
  try {
    for (let attempt = 0; attempt < 100 && !existsSync(started); attempt++) await delay(20);
    assert.ok(existsSync(started), 'the first test child must start before cancellation');
    child.kill('SIGTERM');
    const [code] = await Promise.race([
      new Promise((resolve) => child.once('close', (...args) => resolve(args))),
      new Promise((_, reject) => { timeout = setTimeout(() => reject(new Error('runner or test child retained an open pipe')), 2000); }),
    ]);
    assert.equal(code, 143, Buffer.concat(output).toString());
    assert.equal(existsSync(tailReceipt), false);
    assert.throws(() => process.kill(Number(readFileSync(started, 'utf8')), 0), { code: 'ESRCH' });
  } finally {
    clearTimeout(timeout);
    if (child.exitCode === null) child.kill('SIGKILL');
    if (existsSync(started)) {
      try { process.kill(Number(readFileSync(started, 'utf8')), 'SIGKILL'); }
      catch (error) { if (error.code !== 'ESRCH') throw error; }
    }
  }
});

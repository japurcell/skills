import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { collectEvidence, createEvidenceRoot, validateWorkerClosure } from './selector-timing.mjs';

const runner = new URL('../scripts/ordered-tests.mjs', import.meta.url).href;

test('owned resistant cancellation retains actual closure and telemetry-off result parity', (t) => {
  for (const method of ['abort','SIGTERM','SIGINT']) {
  const directory = mkdtempSync(join(tmpdir(), 'selector-closure-')), root = createEvidenceRoot();
  try {
    const ready = join(directory, 'ready'), file = join(directory, 'hanging.test.mjs');
    const tail = join(directory, 'tail.test.mjs'), tailReceipt = join(directory, 'tail-ran');
    writeFileSync(file, `import test from 'node:test'; import { writeFileSync } from 'node:fs'; process.on('SIGTERM', () => {}); test('controlled hanging child', async () => { writeFileSync(${JSON.stringify(ready)}, 'ready'); await new Promise(() => setInterval(() => {}, 1000)); });`);
    writeFileSync(tail, `import test from 'node:test'; import { writeFileSync } from 'node:fs'; test('must remain queued', () => writeFileSync(${JSON.stringify(tailReceipt)}, 'ran'));`);
    const script = `import { existsSync } from 'node:fs'; import { runOrderedTests } from ${JSON.stringify(runner)}; const controller = new AbortController(); let interruptedBy;
      ${method === 'abort' ? '' : `process.on(${JSON.stringify(method)}, () => { interruptedBy = ${JSON.stringify(method)}; controller.abort(); });`}
      const poll = setInterval(() => { if (existsSync(${JSON.stringify(ready)})) { clearInterval(poll); ${method === 'abort' ? 'controller.abort();' : `process.kill(process.pid, ${JSON.stringify(method)});`} } }, 5);
      const result = await runOrderedTests([${JSON.stringify(file)},${JSON.stringify(tail)}], { concurrency: 1, cwd: ${JSON.stringify(directory)}, signal: controller.signal }); clearInterval(poll); process.exitCode = interruptedBy === 'SIGINT' ? 130 : interruptedBy ? 143 : result;`;
    const outcomes = [];
    for (const enabled of [false, true]) {
      rmSync(ready, { force: true });
      const env = { ...process.env }; delete env.NODE_TEST_CONTEXT; delete env.FACTORY_SELECTOR_TIMING_ROOT; delete env.FACTORY_SELECTOR_TIMING_TOKEN;
      if (enabled) Object.assign(env, { FACTORY_SELECTOR_TIMING_ROOT: root.path, FACTORY_SELECTOR_TIMING_TOKEN: root.token });
      const child = spawnSync(process.execPath, ['--input-type=module','-e',script], { cwd: directory, env, encoding: 'utf8', timeout: 5000 });
      assert.equal(child.error, undefined);
      assert.equal(existsSync(tailReceipt), false);
      outcomes.push({ status: child.status, signal: child.signal });
    }
    const expectedStatus = method === 'abort' ? 1 : method === 'SIGINT' ? 130 : 143;
    assert.deepEqual(outcomes, [{ status: expectedStatus, signal: null }, { status: expectedStatus, signal: null }]);
    const evidence = collectEvidence(root);
    t.diagnostic(method + ' ' + JSON.stringify(evidence.records.map(record => record.stage)));
    assert.equal(evidence.status, 'complete');
    const observed = evidence.records.filter(record => record.stage === 'worker-close-observed');
    assert.equal(observed.length, 1);
    assert.equal(observed[0].disposition, 'SIGKILL');
    assert.equal(observed[0].exitCode, null);
    assert.ok(evidence.records.some(record => record.workerId === observed[0].subjectWorkerId && record.stage === 'worker-open'));
    assert.equal(evidence.records.some(record => record.workerId === observed[0].subjectWorkerId && record.stage === 'worker-close'), false);
    const missingReceipt = evidence.records.filter(record => record !== observed[0]).map(record => record.workerId === observed[0].workerId && record.sequence > observed[0].sequence ? { ...record, sequence:record.sequence - 1 } : record);
    assert.equal(validateWorkerClosure(missingReceipt), false);
  } finally { rmSync(directory, { recursive: true, force: true }); rmSync(root.path, { recursive: true, force: true }); }
  }
});

test('normal, explicit exit and default signal behavior retain off/on status and receipt parity', () => {
  for (const mode of ['normal', 'explicit', 'SIGTERM', 'SIGINT']) {
    const root = createEvidenceRoot();
    try {
      const timing = new URL('./selector-timing.mjs', import.meta.url).href;
      const childSource = `import { telemetry } from ${JSON.stringify(timing)}; telemetry(process.argv[1]); if (process.listenerCount('SIGTERM') || process.listenerCount('SIGINT')) throw new Error('signal handlers changed'); process.stdout.write('R'); ${mode === 'normal' ? 'process.exitCode = 7;' : mode === 'explicit' ? 'process.exit(23);' : 'setInterval(() => {}, 1000);'}`;
      const controller = `import { spawn } from 'node:child_process'; import { ownedWorkerTiming } from ${JSON.stringify(timing)}; const binding = ownedWorkerTiming(); const child = spawn(process.execPath, ['--input-type=module','-e',${JSON.stringify(childSource)},binding?.workerId ?? ''], { stdio: ['ignore','pipe','pipe'] }); binding?.observe(child); ${mode.startsWith('SIG') ? `child.stdout.once('data', () => child.kill(${JSON.stringify(mode)}));` : 'child.stdout.resume();'} child.stderr.resume(); const outcome = await new Promise(resolve => child.once('close', (code, signal) => resolve({ code, signal }))); console.log(JSON.stringify(outcome));`;
      const outcomes = [];
      for (const enabled of [false, true]) {
        const env = { ...process.env }; delete env.NODE_TEST_CONTEXT; delete env.FACTORY_SELECTOR_TIMING_ROOT; delete env.FACTORY_SELECTOR_TIMING_TOKEN;
        if (enabled) Object.assign(env, { FACTORY_SELECTOR_TIMING_ROOT: root.path, FACTORY_SELECTOR_TIMING_TOKEN: root.token });
        const child = spawnSync(process.execPath, ['--input-type=module','-e',controller], { env, encoding: 'utf8', timeout: 3000 });
        assert.equal(child.error, undefined);
        assert.equal(child.status, 0, child.stderr);
        outcomes.push(JSON.parse(child.stdout));
      }
      const expected = mode === 'normal' ? { code: 7, signal: null } : mode === 'explicit' ? { code: 23, signal: null } : { code: null, signal: mode };
      assert.deepEqual(outcomes, [expected, expected]);
      const evidence = collectEvidence(root);
      assert.equal(evidence.status, 'complete');
      const close = evidence.records.find(record => record.stage === 'worker-close-observed');
      assert.equal(close.exitCode, expected.code);
      assert.equal(close.disposition, expected.signal ?? 'failed');
      assert.equal(evidence.records.some(record => record.workerId === close.subjectWorkerId && record.stage === 'worker-close'), !mode.startsWith('SIG'));
    } finally { rmSync(root.path, { recursive: true, force: true }); }
  }
});

test('sending a signal to a resistant owned child never creates an early closure receipt', () => {
  const root = createEvidenceRoot();
  try {
    const timing = new URL('./selector-timing.mjs', import.meta.url).href;
    const childSource = `import { telemetry } from ${JSON.stringify(timing)}; telemetry(process.argv[1]); process.on('SIGTERM', () => {}); process.stdout.write('R'); setInterval(() => {}, 1000);`;
    const controller = `import { spawn } from 'node:child_process'; import { ownedWorkerTiming, collectEvidence } from ${JSON.stringify(timing)};
      const binding = ownedWorkerTiming(); const child = spawn(process.execPath, ['--input-type=module','-e',${JSON.stringify(childSource)},binding.workerId], { stdio: ['ignore','pipe','pipe'] }); binding.observe(child); child.stderr.resume();
      const closed = new Promise(resolve => child.once('close', (code, signal) => resolve({ code, signal })));
      await new Promise(resolve => child.stdout.once('data', resolve)); child.kill('SIGTERM');
      await new Promise(resolve => setTimeout(resolve, 20));
      const partial = collectEvidence({ path:process.env.FACTORY_SELECTOR_TIMING_ROOT, token:process.env.FACTORY_SELECTOR_TIMING_TOKEN });
      console.log(JSON.stringify({ status:partial.status, observed:partial.records.filter(record => record.stage === 'worker-close-observed').length }));
      child.kill('SIGKILL'); console.log(JSON.stringify(await closed));`;
    const env = { ...process.env, FACTORY_SELECTOR_TIMING_ROOT:root.path, FACTORY_SELECTOR_TIMING_TOKEN:root.token }; delete env.NODE_TEST_CONTEXT;
    const child = spawnSync(process.execPath, ['--input-type=module','-e',controller], { env, encoding:'utf8', timeout:3000 });
    assert.equal(child.error, undefined); assert.equal(child.status, 0, child.stderr);
    assert.deepEqual(child.stdout.trim().split('\n').map(line => JSON.parse(line)), [{ status:'incomplete', observed:0 }, { code:null, signal:'SIGKILL' }]);
    assert.equal(collectEvidence(root).status, 'complete');
  } finally { rmSync(root.path, { recursive:true, force:true }); }
});

test('an owned child exit without stdio EOF is insufficient for an observed closure receipt', () => {
  const root = createEvidenceRoot();
  try {
    const timing = new URL('./selector-timing.mjs', import.meta.url).href;
    const childSource = `import { spawn } from 'node:child_process'; import { telemetry } from ${JSON.stringify(timing)}; telemetry(process.argv[1]); spawn(process.execPath, ['-e','setTimeout(() => process.exit(0), 150)'], { stdio:['ignore','inherit','inherit'] }); process.exit(17);`;
    const controller = `import { spawn } from 'node:child_process'; import { ownedWorkerTiming, collectEvidence } from ${JSON.stringify(timing)};
      const binding = ownedWorkerTiming(); const child = spawn(process.execPath, ['--input-type=module','-e',${JSON.stringify(childSource)},binding.workerId], { stdio:['ignore','pipe','pipe'] }); binding.observe(child); child.stdout.resume(); child.stderr.resume();
      const exited = new Promise(resolve => child.once('exit', (code, signal) => resolve({ code, signal })));
      const closed = new Promise(resolve => child.once('close', (code, signal) => resolve({ code, signal })));
      const exit = await exited;
      const partial = collectEvidence({ path:process.env.FACTORY_SELECTOR_TIMING_ROOT, token:process.env.FACTORY_SELECTOR_TIMING_TOKEN });
      console.log(JSON.stringify({ exit, status:partial.status, observed:partial.records.filter(record => record.stage === 'worker-close-observed').length }));
      console.log(JSON.stringify(await closed));`;
    const env = { ...process.env, FACTORY_SELECTOR_TIMING_ROOT:root.path, FACTORY_SELECTOR_TIMING_TOKEN:root.token }; delete env.NODE_TEST_CONTEXT;
    const child = spawnSync(process.execPath, ['--input-type=module','-e',controller], { env, encoding:'utf8', timeout:3000 });
    assert.equal(child.error, undefined); assert.equal(child.status, 0, child.stderr);
    assert.deepEqual(child.stdout.trim().split('\n').map(line => JSON.parse(line)), [{ exit:{ code:17, signal:null }, status:'incomplete', observed:0 }, { code:17, signal:null }]);
    assert.equal(collectEvidence(root).status, 'complete');
  } finally { rmSync(root.path, { recursive:true, force:true }); }
});

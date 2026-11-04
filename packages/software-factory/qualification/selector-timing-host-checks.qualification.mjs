import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { setTimeout as delay } from 'node:timers/promises';
import { collectEvidence, createEvidenceRoot } from './selector-timing.mjs';
import registry from './selector-timing-registry.json' with { type: 'json' };

const timing = new URL('./selector-timing.mjs', import.meta.url).href;
const helper = new URL('./selector-timing-host.mjs', import.meta.url).href;
function runHost(mode = 'seven', alteration = '', options = {}) {
  const directory = realpathSync(mkdtempSync(join(tmpdir(), 'factory-repository-'))), root = createEvidenceRoot();
  const repository = join(directory, 'repository'), common = join(repository, '.git');
  mkdirSync(repository, { mode: 0o700 }); mkdirSync(common, { mode: 0o700 });
  const host = join(common, 'host.mjs'), report = join(directory, 'outcome.json');
  writeFileSync(host, `if (process.listenerCount('SIGTERM') || process.listenerCount('SIGINT')) throw new Error('observer installed a signal handler'); process.stdout.write('original stdout\\n'); process.stderr.write('original stderr\\n'); ${mode === 'zero' ? 'process.exitCode = 0;' : mode === 'explicit' ? 'process.exit(23);' : mode.startsWith('SIG') ? `process.kill(process.pid, ${JSON.stringify(mode)});` : 'process.exitCode = 7;'}`);
  if (options.body) writeFileSync(host, options.body);
  if (options.alias) symlinkSync(directory, join(directory, 'alias'));
  const launchRepository = options.alias ? join(directory, 'alias/repository') : repository;
  const launchHost = options.alias ? join(directory, 'alias/repository/.git/host.mjs') : host;
  const file = join(directory, 'learning.test.mjs');
  writeFileSync(file, `import assert from 'node:assert/strict'; import test from 'node:test'; import { spawn, spawnSync } from 'node:child_process'; import { writeFileSync } from 'node:fs'; import * as fs from 'node:fs'; import fsDefault from 'node:fs'; import { syncBuiltinESMExports } from 'node:module'; import { randomUUID } from 'node:crypto';
    import { rememberFixturePath } from ${JSON.stringify(timing)};
    const { fixtureHostTiming } = await import(${JSON.stringify(helper)}).catch(error => { if (error.code !== 'ERR_MODULE_NOT_FOUND') throw error; return { fixtureHostTiming: () => undefined }; });
    test(${JSON.stringify(registry['learning.test.mjs'][options.asynchronous ? 1 : 0])}, async () => {
      rememberFixturePath(${JSON.stringify(repository)});
      const binding = fixtureHostTiming(${JSON.stringify(launchRepository)}, ${JSON.stringify(options.kind ?? (options.asynchronous ? 'async' : 'sync'))});
      if (binding) { assert.deepEqual(binding.nodeArgs, ['--import', ${JSON.stringify(new URL('./selector-timing-host-preload.mjs', import.meta.url).href)}]); assert.deepEqual(Object.keys(binding.context), ['schema','workerId','fileId','caseId']); }
      const args = [...(binding?.nodeArgs ?? []), ${JSON.stringify(launchHost)}, JSON.stringify({ repository:${JSON.stringify(launchRepository)}, ...(binding ? { qualificationTiming:{ ...binding.context, ...${JSON.stringify(options.context ?? {})} } } : {}) })];
      ${options.asynchronous ? `const child = spawn(process.execPath, args, { stdio:['ignore','pipe','pipe'] }); binding?.observe(child); let stdout = '', stderr = ''; child.stdout.on('data', chunk => { stdout += chunk; }); child.stderr.on('data', chunk => { stderr += chunk; }); const result = await new Promise(resolve => child.once('close', (status, signal) => resolve({ pid:child.pid, status, signal, stdout, stderr })));` : `const result = spawnSync(process.execPath, args, { encoding:'utf8', ...${JSON.stringify(options.launch ?? {})} });`}
      const receipt = binding ? ${JSON.stringify(common)} + '/selector-host-' + binding.context.workerId + '.identity.json' : undefined;
      if (binding) { ${alteration} ${options.swap ? `fs.renameSync(${JSON.stringify(repository)}, ${JSON.stringify(repository + '.old')}); fs.mkdirSync(${JSON.stringify(repository)}); fs.mkdirSync(${JSON.stringify(common)});` : ''} }
      let readBytes, originalRead, originalReadSync;
      ${options.readRace ? `if (binding) { let changed = false; readBytes = 0; originalRead = fsDefault.readFileSync; originalReadSync = fsDefault.readSync;
      const disturb = () => { if (changed) return; changed = true; ${options.readRace === 'grow' ? `fs.appendFileSync(receipt, ' '.repeat(4096));` : `const bytes = originalRead(receipt); fs.renameSync(receipt, receipt + '.saved'); fs.writeFileSync(receipt, bytes, { flag:'wx', mode:0o600 });`} };
      fsDefault.readFileSync = (file, ...args) => { if (typeof file !== 'number') return originalRead(file, ...args); disturb(); const bytes = originalRead(file, ...args); readBytes = Math.max(readBytes, bytes.length); return bytes; };
      fsDefault.readSync = (fd, ...args) => { disturb(); const count = originalReadSync(fd, ...args); readBytes = Math.max(readBytes, count); return count; }; syncBuiltinESMExports(); }` : ''}
      try { ${options.asynchronous ? '' : `binding?.returned({ pid:result.pid, status:result.status, signal:result.signal, apiError:result.error !== undefined });`} }
      finally { ${options.readRace ? `if (binding) { fsDefault.readFileSync = originalRead; fsDefault.readSync = originalReadSync; syncBuiltinESMExports(); }` : ''} }
      writeFileSync(${JSON.stringify(report)}, JSON.stringify({ status:result.status, signal:result.signal, stdout:result.stdout, stderr:result.stderr, apiError:result.error !== undefined, ...(readBytes === undefined ? {} : { readBytes }) }));
    });`);
  const outcomes = [];
  try {
    for (const enabled of [false, true]) {
      const env = { ...process.env }; delete env.NODE_TEST_CONTEXT; delete env.FACTORY_SELECTOR_TIMING_ROOT; delete env.FACTORY_SELECTOR_TIMING_TOKEN;
      if (enabled) Object.assign(env, { FACTORY_SELECTOR_TIMING_ROOT:root.path, FACTORY_SELECTOR_TIMING_TOKEN:root.token });
      const result = spawnSync(process.execPath, ['--test',file], { env, encoding:'utf8', timeout:5000 });
      assert.equal(result.error, undefined); assert.equal(result.status, 0, result.stderr + result.stdout);
      outcomes.push(JSON.parse(readFileSync(report, 'utf8')));
      if (!enabled) assert.deepEqual(readdirSync(common), ['host.mjs']);
    }
    return { outcomes, evidence:collectEvidence(root), receiptCount:readdirSync(common).filter(name => name.endsWith('.identity.json')).length };
  } finally { rmSync(directory, { recursive:true, force:true }); rmSync(root.path, { recursive:true, force:true }); }
}

test('fixed host observation preserves exit 7 and original payload while proving distinct synchronous closure', () => {
  const { outcomes, evidence } = runHost();
  const original = { status:7, signal:null, stdout:'original stdout\n', stderr:'original stderr\n', apiError:false };
  assert.deepEqual(outcomes, [original, original]);
  assert.equal(evidence.status, 'complete');
  const binding = evidence.records.find(record => record.stage === 'worker-bind-sync');
  assert.ok(binding, 'actual synchronous launch needs its distinct binding');
  const host = evidence.records.filter(record => record.workerId === binding.subjectWorkerId);
  assert.deepEqual(host.map(record => record.stage), ['worker-open','fixture-host','worker-close']);
  const returned = evidence.records.filter(record => record.stage === 'worker-close-returned');
  assert.equal(returned.length, 1); assert.equal(returned[0].subjectWorkerId, binding.subjectWorkerId);
  assert.equal(returned[0].exitCode, 7); assert.equal(returned[0].disposition, 'failed');
  assert.equal(evidence.records.some(record => record.stage === 'worker-close-observed'), false);
});


test('normal and explicit host returns preserve outcomes; default signals have closure with unknown CPU', () => {
  for (const mode of ['zero','explicit','SIGKILL','SIGTERM','SIGINT']) {
    const { outcomes, evidence } = runHost(mode);
    assert.deepEqual(outcomes[0], outcomes[1]);
    const expected = mode === 'zero' ? 0 : mode === 'explicit' ? 23 : null;
    assert.equal(outcomes[1].status, expected); assert.equal(outcomes[1].signal, mode.startsWith('SIG') ? mode : null);
    assert.equal(evidence.status, 'complete');
    const close = evidence.records.find(record => record.stage === 'worker-close-returned');
    assert.equal(close.exitCode, expected); assert.equal(close.disposition, mode.startsWith('SIG') ? mode : expected === 0 ? 'ok' : 'failed');
    const selfClose = evidence.records.find(record => record.workerId === close.subjectWorkerId && record.stage === 'worker-close');
    assert.equal(Boolean(selfClose), !mode.startsWith('SIG'));
    assert.equal(close.cpuUserUs, 0); assert.equal(close.cpuSystemUs, 0); assert.equal(close.wallMs, 0);
    assert.equal(evidence.records.some(record => record.stage === 'worker-close-observed'), false);
  }
});

test('private receipt tampering never certifies a synchronous return or leaks rejected values', () => {
  const changes = {
    missing: `fs.rmSync(receipt);`,
    partial: `fs.writeFileSync(receipt, '{');`,
    stale: `const value = JSON.parse(fs.readFileSync(receipt)); value.pid = result.pid + 1; fs.writeFileSync(receipt, JSON.stringify(value) + '\\n');`,
    uuid: `const value = JSON.parse(fs.readFileSync(receipt)); value.workerId = randomUUID(); fs.writeFileSync(receipt, JSON.stringify(value) + '\\n');`,
    private: `fs.chmodSync(receipt, 0o644);`,
    hardlink: `fs.linkSync(receipt, receipt + '.linked');`,
    symlink: `fs.renameSync(receipt, receipt + '.saved'); fs.symlinkSync(receipt + '.saved', receipt);`,
    oversized: `fs.writeFileSync(receipt, 'x'.repeat(257));`,
    noncanonical: `fs.appendFileSync(receipt, ' ');`,
    duplicate: `fs.writeFileSync(receipt, '{"pid":"private-canary",' + fs.readFileSync(receipt, 'utf8').slice(1));`,
    utf8: `fs.writeFileSync(receipt, Buffer.from([0xff]));`,
    extra: `const value = JSON.parse(fs.readFileSync(receipt)); value.path = 'private-canary'; fs.writeFileSync(receipt, JSON.stringify(value) + '\\n');`,
  };
  for (const [name, alteration] of Object.entries(changes)) {
    const { outcomes, evidence } = runHost('seven', alteration);
    assert.deepEqual(outcomes[0], outcomes[1], name);
    assert.equal(evidence.status, 'incomplete', name);
    assert.equal(evidence.records.some(record => record.stage === 'worker-close-returned'), false, name);
    assert.equal(JSON.stringify(evidence).includes('private-canary'), false);
    assert.equal(evidence.records.some(record => 'pid' in record || 'path' in record || 'error' in record), false);
  }
});

test('actual synchronous API failures never become closure even when a host wrote a receipt', () => {
  for (const failure of ['ETIMEDOUT','ENOBUFS']) {
    const options = failure === 'ETIMEDOUT'
      ? { body:`setInterval(() => {}, 1000);`, launch:{ timeout:100, killSignal:'SIGKILL' } }
      : { body:`process.stdout.write('x'.repeat(65536));`, launch:{ maxBuffer:1024 } };
    const { outcomes, evidence, receiptCount } = runHost('seven', '', options);
    assert.equal(receiptCount, 1, failure);
    assert.ok(evidence.records.some(record => record.stage === 'fixture-host'), failure);
    assert.equal(outcomes[0].apiError, true); assert.equal(outcomes[1].apiError, true);
    assert.equal(evidence.status, 'incomplete');
    assert.equal(evidence.records.some(record => record.stage === 'worker-close-returned'), false);
  }
});

test('a sanitized API error flag and repeated use cannot create an additional returned receipt', () => {
  for (const alteration of [`result.error = new Error('private-canary');`, `binding.returned({ pid:result.pid, status:result.status, signal:result.signal, apiError:false });`]) {
    const { evidence } = runHost('seven', alteration);
    assert.equal(evidence.status, 'incomplete');
    assert.ok(evidence.records.filter(record => record.stage === 'worker-close-returned').length <= 1);
    assert.equal(JSON.stringify(evidence).includes('private-canary'), false);
  }
});


test('malformed context, wrong launch mode, replaced fixture and pre-preload failure remain incomplete', () => {
  for (const options of [{ context:{ workerId:'not-a-uuid' } }, { context:{ fileId:'private-canary' } }, { context:{ caseId:'9' } }, { context:{ caseId:1 } }, { context:{ schema:3 } }, { context:{ extra:'private-canary' } }, { kind:'wrong' }, { swap:true }, { launch:{ cwd:'/private/nonexistent-selector-host-directory' } }]) {
    const { evidence } = runHost('seven', '', options);
    assert.equal(evidence.status, 'incomplete');
    assert.equal(evidence.records.some(record => record.stage === 'worker-close-returned'), false);
    assert.equal(JSON.stringify(evidence).includes('private-canary'), false);
  }
});


test('fixed async host retains actual event closure and graceful 143 owns only a measured partial interval', () => {
  const { outcomes, evidence } = runHost('seven', '', { asynchronous:true, body:'process.exit(143);' });
  assert.deepEqual(outcomes[0], outcomes[1]); assert.equal(outcomes[1].status, 143);
  assert.equal(evidence.status, 'complete');
  const binding = evidence.records.find(record => record.stage === 'worker-bind');
  const close = evidence.records.find(record => record.stage === 'worker-close-observed');
  assert.equal(close.subjectWorkerId, binding.subjectWorkerId); assert.equal(close.exitCode, 143); assert.equal(close.disposition, 'failed');
  const host = evidence.records.filter(record => record.workerId === binding.subjectWorkerId);
  assert.deepEqual(host.map(record => record.stage), ['worker-open','fixture-host','worker-close']);
  assert.ok(host.at(-1).wallMs >= 0); assert.ok(host.at(-1).cpuUserUs >= 0); assert.ok(host.at(-1).cpuSystemUs >= 0);
  assert.equal(evidence.records.some(record => ['worker-bind-sync','worker-close-returned'].includes(record.stage)), false);
});


test('an owned fixture under the platform temporary-directory alias retains canonical receipt binding', () => {
  const { outcomes, evidence } = runHost('seven', '', { alias:true });
  assert.deepEqual(outcomes[0], outcomes[1]); assert.equal(evidence.status, 'complete');
  assert.equal(evidence.records.filter(record => record.stage === 'worker-close-returned').length, 1);
});


test('impossible synchronous outcome tuples and unavailable PIDs never certify closure', () => {
  for (const alteration of [`result.pid = undefined;`, `result.status = -1;`, `result.status = 256;`, `result.status = 0.5;`, `result.status = null; result.signal = null;`, `result.status = 0; result.signal = 'SIGTERM';`, `result.status = null; result.signal = 'SIGPRIVATECANARY';`]) {
    const { evidence } = runHost('seven', alteration);
    assert.equal(evidence.status, 'incomplete', alteration);
    assert.equal(evidence.records.some(record => record.stage === 'worker-close-returned'), false, alteration);
    assert.equal(JSON.stringify(evidence).includes('SIGPRIVATECANARY'), false);
  }
});


test('private host receipts retain the fixed nine-per-fixture and 36-total bounds', () => {
  const directory = realpathSync(mkdtempSync(join(tmpdir(), 'selector-host-caps-'))), root = createEvidenceRoot(), containers = [];
  try {
    const fixtures = Array.from({ length:5 }, () => {
      const container = realpathSync(mkdtempSync(join(tmpdir(), 'factory-repository-'))); containers.push(container);
      const repository = join(container, 'repository'), common = join(repository, '.git'), host = join(common, 'host.mjs');
      mkdirSync(repository, { mode:0o700 }); mkdirSync(common); writeFileSync(host, 'process.exit(0);');
      return { repository, host, common };
    });
    const file = join(directory, 'learning.test.mjs');
    writeFileSync(file, `import assert from 'node:assert/strict'; import test from 'node:test'; import { spawnSync } from 'node:child_process'; import { readdirSync } from 'node:fs';
      import { rememberFixturePath } from ${JSON.stringify(timing)}; import { fixtureHostTiming } from ${JSON.stringify(helper)};
      test(${JSON.stringify(registry['learning.test.mjs'][0])}, () => {
        const fixtures = ${JSON.stringify(fixtures)};
        for (let index = 0; index < fixtures.length; index++) {
          const fixture = fixtures[index]; rememberFixturePath(fixture.repository);
          for (let launch = 0; launch < 10; launch++) {
            const binding = fixtureHostTiming(fixture.repository, 'sync');
            assert.equal(Boolean(binding), index < 4 && launch < 9);
            const result = spawnSync(process.execPath, [...(binding?.nodeArgs ?? []), fixture.host, JSON.stringify({ repository:fixture.repository, ...(binding ? { qualificationTiming:binding.context } : {}) })]);
            assert.equal(result.status, 0); binding?.returned({ pid:result.pid, status:result.status, signal:result.signal, apiError:result.error !== undefined });
          }
          assert.equal(readdirSync(fixture.common).filter(name => name.endsWith('.identity.json')).length, index < 4 ? 9 : 0);
        }
      });`);
    const env = { ...process.env, FACTORY_SELECTOR_TIMING_ROOT:root.path, FACTORY_SELECTOR_TIMING_TOKEN:root.token }; delete env.NODE_TEST_CONTEXT;
    const result = spawnSync(process.execPath, ['--test',file], { env, encoding:'utf8', timeout:10000 });
    assert.equal(result.error, undefined); assert.equal(result.status, 0, result.stdout + result.stderr);
    const evidence = collectEvidence(root);
    assert.equal(evidence.status, 'incomplete');
    for (const stage of ['worker-bind-sync','fixture-host','worker-close-returned']) assert.equal(evidence.records.filter(record => record.stage === stage).length, 36);
  } finally { for (const container of containers) rmSync(container, { recursive:true, force:true }); rmSync(directory, { recursive:true, force:true }); rmSync(root.path, { recursive:true, force:true }); }
});

test('timing off accepts an unusable fixture value without any filesystem access', () => {
  const env = { ...process.env }; delete env.NODE_TEST_CONTEXT; delete env.FACTORY_SELECTOR_TIMING_ROOT; delete env.FACTORY_SELECTOR_TIMING_TOKEN;
  const source = `import assert from 'node:assert/strict'; import { fixtureHostTiming, preloadFixtureHostTiming } from ${JSON.stringify(helper)}; assert.equal(fixtureHostTiming({ toString() { throw new Error('filesystem coercion'); } }, 'sync'), undefined); preloadFixtureHostTiming();`;
  const result = spawnSync(process.execPath, ['--input-type=module','-e',source], { env, encoding:'utf8', timeout:3000 });
  assert.equal(result.error, undefined); assert.equal(result.status, 0, result.stderr); assert.equal(result.stdout, ''); assert.equal(result.stderr, '');
});


test('receipt reads stay bounded during growth and reject a path swapped after descriptor acquisition', () => {
  for (const readRace of ['grow','swap']) {
    const { outcomes, evidence } = runHost('seven', '', { readRace });
    assert.equal(outcomes[1].status, 7); assert.equal(outcomes[1].stdout, outcomes[0].stdout); assert.equal(outcomes[1].stderr, outcomes[0].stderr);
    assert.equal(evidence.status, 'incomplete');
    assert.equal(evidence.records.some(record => record.stage === 'worker-close-returned'), false);
    assert.ok(outcomes[1].readBytes > 0 && outcomes[1].readBytes <= 257, readRace + ' must not materialize an unbounded receipt');
  }
});


test('a synchronous signal request cannot certify closure before the actual spawnSync return', { timeout:5000 }, async () => {
  const directory = realpathSync(mkdtempSync(join(tmpdir(), 'factory-repository-'))), root = createEvidenceRoot();
  const repository = join(directory, 'repository'), common = join(repository, '.git'), ready = join(directory, 'ready'), signaled = join(directory, 'signaled');
  mkdirSync(repository, { mode:0o700 }); mkdirSync(common);
  const host = join(common, 'host.mjs'), file = join(directory, 'learning.test.mjs');
  writeFileSync(host, `import { writeFileSync } from 'node:fs'; process.on('SIGTERM', () => writeFileSync(${JSON.stringify(signaled)}, 'seen')); writeFileSync(${JSON.stringify(ready)}, String(process.pid), { mode:0o600 }); setInterval(() => {}, 1000);`);
  writeFileSync(file, `import assert from 'node:assert/strict'; import test from 'node:test'; import { spawnSync } from 'node:child_process';
    import { rememberFixturePath } from ${JSON.stringify(timing)}; import { fixtureHostTiming } from ${JSON.stringify(helper)};
    test(${JSON.stringify(registry['learning.test.mjs'][0])}, () => {
      rememberFixturePath(${JSON.stringify(repository)}); const binding = fixtureHostTiming(${JSON.stringify(repository)}, 'sync');
      const result = spawnSync(process.execPath, [...binding.nodeArgs, ${JSON.stringify(host)}, JSON.stringify({ repository:${JSON.stringify(repository)}, qualificationTiming:binding.context })], { encoding:'utf8', timeout:3000, killSignal:'SIGKILL' });
      binding.returned({ pid:result.pid, status:result.status, signal:result.signal, apiError:result.error !== undefined });
      assert.equal(result.error, undefined); assert.equal(result.signal, 'SIGKILL');
    });`);
  const env = { ...process.env, FACTORY_SELECTOR_TIMING_ROOT:root.path, FACTORY_SELECTOR_TIMING_TOKEN:root.token }; delete env.NODE_TEST_CONTEXT;
  const controller = spawn(process.execPath, ['--test',file], { env, stdio:['ignore','pipe','pipe'] });
  let output = '', pid; controller.stdout.on('data', bytes => { output += bytes; }); controller.stderr.on('data', bytes => { output += bytes; });
  const closed = new Promise(resolve => controller.once('close', (code, signal) => resolve({ code, signal })));
  try {
    for (let index = 0; index < 100; index++) { try { pid = Number(readFileSync(ready, 'utf8')); break; } catch (error) { if (error.code !== 'ENOENT') throw error; } await delay(10); }
    assert.ok(Number.isSafeInteger(pid) && pid > 0, 'the fixed host must announce readiness');
    process.kill(pid, 'SIGTERM');
    let seen = false;
    for (let index = 0; index < 100; index++) { try { seen = readFileSync(signaled, 'utf8') === 'seen'; break; } catch (error) { if (error.code !== 'ENOENT') throw error; } await delay(10); }
    assert.equal(seen, true);
    const partial = collectEvidence(root);
    assert.equal(partial.status, 'incomplete'); assert.equal(partial.records.filter(record => record.stage === 'worker-close-returned').length, 0);
    process.kill(pid, 'SIGKILL');
    assert.deepEqual(await closed, { code:0, signal:null }, output); pid = undefined;
    const evidence = collectEvidence(root), close = evidence.records.find(record => record.stage === 'worker-close-returned');
    assert.equal(evidence.status, 'complete'); assert.equal(close.disposition, 'SIGKILL');
    assert.equal(evidence.records.some(record => record.workerId === close.subjectWorkerId && record.stage === 'worker-close'), false);
    assert.equal(evidence.records.some(record => record.stage === 'worker-close-observed'), false);
  } finally {
    if (pid && controller.exitCode === null) { try { process.kill(pid, 'SIGKILL'); } catch (error) { if (error.code !== 'ESRCH') throw error; } }
    if (controller.exitCode === null && controller.signalCode === null) controller.kill('SIGKILL');
    await closed; rmSync(directory, { recursive:true, force:true }); rmSync(root.path, { recursive:true, force:true });
  }
});

test('host observation retains the original persisted-row and collector record caps without exporting private data', async () => {
  const { DatabaseSync } = await import('node:sqlite'), { createHash } = await import('node:crypto');
  const directory = realpathSync(mkdtempSync(join(tmpdir(), 'factory-repository-'))), root = createEvidenceRoot();
  try {
    const repository = join(directory, 'repository'), common = join(repository, '.git/factory'); mkdirSync(common, { recursive:true });
    const file = join(common, 'history.sqlite'), database = new DatabaseSync(file);
    database.exec('CREATE TABLE observation_events(cursor INTEGER PRIMARY KEY,kind TEXT,data TEXT); CREATE TABLE attempts(id TEXT PRIMARY KEY,invocation_id TEXT,operation_id TEXT,kind TEXT); CREATE TABLE operations(id TEXT PRIMARY KEY,operation_key TEXT); CREATE TABLE captures(secret TEXT);');
    database.prepare('INSERT INTO operations VALUES (?,?)').run('private-operation', 'startup/build/private-invocation');
    const attempt = database.prepare('INSERT INTO attempts VALUES (?,?,?,?)'), event = database.prepare('INSERT INTO observation_events(kind,data) VALUES (?,?)');
    database.exec('BEGIN');
    for (let index = 0; index < 4097; index++) {
      const id = 'private-attempt-' + index; attempt.run(id, 'private-invocation', 'private-operation', 'command');
      event.run('attempt.started', JSON.stringify({ attemptId:id, at:'2026-11-04T03:00:00.000Z', argv:'private-canary', capture:'private-canary' }));
    }
    database.exec('COMMIT'); database.close();
    const hash = () => createHash('sha256').update(readFileSync(file)).digest('hex'), before = hash();
    const source = `import { rememberFixturePath } from ${JSON.stringify(timing)}; import { fixtureAttemptTiming } from ${JSON.stringify(new URL('./selector-timing-attempts.mjs', import.meta.url).href)}; rememberFixturePath(${JSON.stringify(repository)}); fixtureAttemptTiming(${JSON.stringify(repository)})();`;
    const env = { ...process.env, FACTORY_SELECTOR_TIMING_ROOT:root.path, FACTORY_SELECTOR_TIMING_TOKEN:root.token }; delete env.NODE_TEST_CONTEXT;
    const child = spawnSync(process.execPath, ['--input-type=module','-e',source], { env, encoding:'utf8', timeout:3000 });
    assert.equal(child.error, undefined); assert.equal(child.status, 0, child.stderr);
    const evidence = collectEvidence(root);
    assert.equal(evidence.status, 'incomplete'); assert.ok(evidence.records.length <= 4096);
    assert.ok(evidence.records.filter(record => record.stage === 'attempt').length <= 4096);
    assert.equal(JSON.stringify(evidence).includes('private-'), false); assert.equal(hash(), before);
  } finally { rmSync(directory, { recursive:true, force:true }); rmSync(root.path, { recursive:true, force:true }); }
});

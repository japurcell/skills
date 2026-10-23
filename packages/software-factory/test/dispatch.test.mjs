import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const dispatch = fileURLToPath(new URL('../scripts/test.mjs', import.meta.url));
test('suite selection fails for unfinished suites, unmatched filters and unknown options', () => {
  for (const args of [['maintenance'], ['fixtures', '--provider', 'missing'], ['fixtures', '--suite', 'browser'],
    ['fixtures', '--operation', 'upgrade'], ['qualification', '--area', 'missing'], ['fixtures', '--typo']]) {
    const result = spawnSync(process.execPath, [dispatch, ...args], { encoding: 'utf8', timeout: 5000 });
    assert.equal(result.status, 1, result.stderr);
    assert.match(result.stderr, /not implemented|no tests|Unknown option/);
    assert.equal(result.stdout, '', 'invalid selection must precede launching registered suites');
  }
});

// The aggregate command refuses before spawning any unfinished feature suite.
test('aggregate selection reports maintenance after learning registration', () => {
  const result = spawnSync(process.execPath, [dispatch, 'all'], { encoding: 'utf8', timeout: 5000 });
  assert.equal(result.status, 1, result.stderr);
  assert.match(result.stderr, /maintenance: not implemented; missing operations: install, upgrade, dependencies, repair, uninstall, cleanup/);
  assert.equal(result.stdout, '', 'aggregate refusal must precede launching registered suites');
});

test('release bootstrap selection runs deterministic verification without a native archive', () => {
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_TEST_NODE_ARCHIVE;
  const result = spawnSync(process.execPath, [dispatch, 'release', '--area', 'bootstrap'], { encoding: 'utf8', timeout: 15000, env });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /default Node discovery excludes explicit native bootstrap qualification/);
  assert.match(result.stdout, /validator accepts pipe completion between event checks/);
  assert.doesNotMatch(result.stdout, /native public verifier executes authenticated snapshot/);
});

test('release candidate selection runs deterministic preparation checks without native acquisition', () => {
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_TEST_NODE_ARCHIVE;
  const result = spawnSync(process.execPath, [dispatch, 'release', '--area', 'candidate'], { encoding: 'utf8', timeout: 15000, env });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /a bound candidate receipt rejects changed bytes/);
  assert.match(result.stdout, /public Python inventory rejects a changed new import/);
  assert.doesNotMatch(result.stdout, /explicit native offline prepare/);
});

test('release publication selection runs deterministic ownership checks without native acquisition', () => {
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_TEST_NODE_ARCHIVE;
  const result = spawnSync(process.execPath, [dispatch, 'release', '--area', 'publication'], { encoding: 'utf8', timeout: 15000, env });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /publication/);
  assert.match(result.stdout, /ready/);
  assert.doesNotMatch(result.stdout, /explicit native/);
});

test('maintenance controller selection executes admission and handoff checks while incomplete operations refuse', () => {
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  const result = spawnSync(process.execPath, [dispatch, 'maintenance', '--operation', 'controller'], { encoding: 'utf8', timeout: 15000, env });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /bootstrap/);
  assert.match(result.stdout, /handoff/);
  for (const operation of ['install', 'upgrade', 'dependencies', 'repair', 'uninstall', 'cleanup', 'unknown']) {
    const refused = spawnSync(process.execPath, [dispatch, 'maintenance', '--operation', operation], { encoding: 'utf8', timeout: 5000, env });
    assert.equal(refused.status, 1, refused.stderr);
    assert.match(refused.stderr, /no tests match supplied filters/);
    assert.equal(refused.stdout, '');
  }
});


test('notification group runs sender and bounded preflight checks without a desktop', () => {
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT; // Exercise the ordinary CLI, outside this parent test runner.
  const result = spawnSync(process.execPath, [dispatch, 'notifications'], { encoding: 'utf8', timeout: 15000, env });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /unresolved Windows preflight/);
  assert.match(result.stdout, /inherited pipe beyond the deadline/);
  assert.match(result.stdout, /missing notification request fails with a fixed result/);
});


test('learning extraction selection executes public proposal and source checks', () => {
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  const result = spawnSync(process.execPath, [dispatch, 'learning', '--operation', 'extract'], { encoding: 'utf8', timeout: 30000, env });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /explicit extraction saves examined ended sources/);
  assert.match(result.stdout, /extraction rejects diff paths that disagree/);
});


test('Copilot provider selection executes deterministic adapter conformance only', () => {
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  const result = spawnSync(process.execPath, [dispatch, 'adapters', '--provider', 'copilot'], { encoding: 'utf8', timeout: 30000, env });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /Copilot public invocation accepts only a final answer/);
  assert.match(result.stdout, /Copilot package closure rejects drift/);
});

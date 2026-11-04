import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, matchesGlob } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

for (const [name, script, expected, prerequisites = {}] of [
  ['bootstrap refuses local downloads and retains structured failure evidence', 'qualification-bootstrap.mjs', /ephemeral GitHub Actions/],
  ['foundation refuses missing exact npm prerequisite and retains structured failure evidence', 'qualification-foundation.mjs', /explicit bundled npm CLI/],
  ['foundation refuses missing Python before installing dependencies', 'qualification-foundation.mjs', /explicit Python 3\.11 or newer interpreter/, { FACTORY_NPM_CLI: 'unused-npm-cli' }],
  ['foundation refuses missing atomic helper Python before installing dependencies', 'qualification-foundation.mjs', /explicit atomic publication Python interpreter/, {
    FACTORY_NPM_CLI: 'unused-npm-cli', FACTORY_TEST_PYTHON: process.execPath,
  }],
]) test(name, () => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-ci-test-'));
  try {
    const env = { ...process.env, GITHUB_ACTIONS: 'false', FACTORY_EVIDENCE_DIR: directory };
    delete env.FACTORY_NPM_CLI;
    delete env.FACTORY_TEST_PYTHON;
    delete env.FACTORY_ATOMIC_PYTHON;
    Object.assign(env, prerequisites);
    const result = spawnSync(process.execPath, [fileURLToPath(new URL(`../scripts/${script}`, import.meta.url))], { env, encoding: 'utf8', timeout: 5000 });
    assert.equal(result.status, 1, result.stderr);
    assert.match(result.stderr, expected);
    const files = readdirSync(directory);
    assert.equal(files.length, 1);
    const report = JSON.parse(readFileSync(join(directory, files[0]), 'utf8'));
    assert.equal(report.status, 'failed');
    assert.match(report.error, expected);
  } finally { rmSync(directory, { recursive: true, force: true }); }
});

test('foundation validates the selected interpreter before dependency installation', () => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-ci-python-test-'));
  try {
    const result = spawnSync(process.execPath, [fileURLToPath(new URL('../scripts/qualification-foundation.mjs', import.meta.url))], {
      env: { ...process.env, FACTORY_EVIDENCE_DIR: directory, FACTORY_NPM_CLI: 'unused-npm-cli',
        FACTORY_TEST_PYTHON: process.execPath, FACTORY_ATOMIC_PYTHON: process.execPath },
      encoding: 'utf8', timeout: 5000,
    });
    assert.equal(result.status, 1, result.stderr);
    const report = JSON.parse(readFileSync(join(directory, 'foundation.json'), 'utf8'));
    assert.match(report.error, /Python prerequisite failed/);
    assert.deepEqual(report.steps.map(step => [step.name, step.status]), [['python', 'failed']]);
    assert.equal(report.steps[0].command[0], process.execPath);
    assert.deepEqual(readdirSync(directory).sort(), ['foundation.json', 'python.log']);
  } finally { rmSync(directory, { recursive: true, force: true }); }
});

test('foundation explicitly selects native atomic qualification on declared Darwin and Linux targets', () => {
  const foundation = readFileSync(new URL('../scripts/qualification-foundation.mjs', import.meta.url), 'utf8');
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-qualification.yml', import.meta.url), 'utf8');
  assert.match(foundation, /process\.platform === 'darwin' && process\.arch === 'arm64'[\s\S]*atomic-publication-native-darwin-arm64/);
  assert.match(foundation, /process\.platform === 'linux' && process\.arch === 'x64'[\s\S]*atomic-publication-native-linux-x64/);
  assert.match(workflow, /FACTORY_ATOMIC_PYTHON:\s*\$\{\{\s*steps\.python\.outputs\.python-path\s*\}\}/);
});

test('Linux public install and upgrade qualification is registered and invoked only on its declared native target', () => {
  const selector = readFileSync(new URL('../scripts/test.mjs', import.meta.url), 'utf8');
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-qualification.yml', import.meta.url), 'utf8');
  assert.match(selector, /upgrade-publication-linux-native\.qualification\.mjs'[\s\S]*area: 'upgrade-publication-linux'/);
  assert.match(workflow, /- name: Run Linux public install and upgrade qualification[\s\S]*?if: matrix\.target == 'linux-x64'[\s\S]*?timeout-minutes: 15[\s\S]*?FACTORY_TEST_PYTHON:\s*\$\{\{\s*steps\.python\.outputs\.python-path\s*\}\}[\s\S]*?FACTORY_ATOMIC_PYTHON:\s*\$\{\{\s*steps\.python\.outputs\.python-path\s*\}\}[\s\S]*?FACTORY_TEST_NPM_CACHE_SEED:\s*\$\{\{\s*runner\.temp\s*\}\}/);
  assert.match(workflow, /run: node packages\/software-factory\/scripts\/test\.mjs qualification --area upgrade-publication-linux/);
});

test('read-only dependency ownership qualification is explicit and Linux CI supplies its authenticated native inputs', () => {
  const selector = readFileSync(new URL('../scripts/test.mjs', import.meta.url), 'utf8');
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-qualification.yml', import.meta.url), 'utf8');
  assert.match(selector, /dependency-state-native\.qualification\.mjs'[\s\S]*area: 'dependency-ownership'/);
  assert.match(workflow, /- name: Run Linux read-only dependency ownership qualification[\s\S]*?if: matrix\.target == 'linux-x64'[\s\S]*?timeout-minutes: 15[\s\S]*?FACTORY_TEST_PYTHON:\s*\$\{\{\s*steps\.python\.outputs\.python-path\s*\}\}[\s\S]*?FACTORY_ATOMIC_PYTHON:\s*\$\{\{\s*steps\.python\.outputs\.python-path\s*\}\}[\s\S]*?FACTORY_TEST_NPM_CACHE_SEED:\s*\$\{\{\s*runner\.temp\s*\}\}/);
  assert.match(workflow, /run: node packages\/software-factory\/scripts\/test\.mjs qualification --area dependency-ownership/);
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_TEST_NODE_ARCHIVE;
  const result = spawnSync(process.execPath, [fileURLToPath(new URL('../scripts/test.mjs', import.meta.url)), 'qualification', '--area', 'dependency-ownership'], {
    encoding: 'utf8', timeout: 5000, env,
  });
  assert.equal(result.status, 1, result.stdout + result.stderr);
  assert.match(result.stdout + result.stderr, /exact pinned Node archive required|requires Darwin arm64 or Linux x64/);
});

test('dependency claim foundation qualification stays explicit and Linux CI supplies its exact native prerequisites', () => {
  const selector = readFileSync(new URL('../scripts/test.mjs', import.meta.url), 'utf8');
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-qualification.yml', import.meta.url), 'utf8');
  assert.match(selector, /dependency-claim-native\.qualification\.mjs'[\s\S]*area: 'dependency-claim'/);
  assert.match(workflow, /- name: Run Linux dependency claim foundation qualification[\s\S]*?if: matrix\.target == 'linux-x64'[\s\S]*?timeout-minutes: 15[\s\S]*?FACTORY_TEST_PYTHON:\s*\$\{\{\s*steps\.python\.outputs\.python-path\s*\}\}[\s\S]*?FACTORY_ATOMIC_PYTHON:\s*\$\{\{\s*steps\.python\.outputs\.python-path\s*\}\}[\s\S]*?FACTORY_TEST_NPM_CACHE_SEED:\s*\$\{\{\s*runner\.temp\s*\}\}/);
  assert.match(workflow, /run: node packages\/software-factory\/scripts\/test\.mjs qualification --area dependency-claim/);
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_TEST_NODE_ARCHIVE;
  const result = spawnSync(process.execPath, [fileURLToPath(new URL('../scripts/test.mjs', import.meta.url)), 'qualification', '--area', 'dependency-claim'], {
    encoding: 'utf8', timeout: 5000, env,
  });
  assert.equal(result.status, 1, result.stdout + result.stderr);
  assert.match(result.stdout + result.stderr, /exact pinned Node archive required|requires Darwin arm64 or Linux x64/);
});

test('dependency backup qualification is explicit and Linux CI supplies its exact native prerequisites', () => {
  const selector = readFileSync(new URL('../scripts/test.mjs', import.meta.url), 'utf8');
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-qualification.yml', import.meta.url), 'utf8');
  assert.match(selector, /dependency-backup-native\.qualification\.mjs'[\s\S]*area: 'dependency-backup'/);
  assert.match(workflow, /- name: Run Linux verified dependency backup qualification[\s\S]*?if: matrix\.target == 'linux-x64'[\s\S]*?timeout-minutes: 15[\s\S]*?FACTORY_TEST_PYTHON:\s*\$\{\{\s*steps\.python\.outputs\.python-path\s*\}\}[\s\S]*?FACTORY_ATOMIC_PYTHON:\s*\$\{\{\s*steps\.python\.outputs\.python-path\s*\}\}[\s\S]*?FACTORY_TEST_NPM_CACHE_SEED:\s*\$\{\{\s*runner\.temp\s*\}\}/);
  assert.match(workflow, /run: node packages\/software-factory\/scripts\/test\.mjs qualification --area dependency-backup/);
});

test('Darwin timing workflow preserves one full fixtures position and uploads only validated exact exports', () => {
  const foundation = readFileSync(new URL('../scripts/qualification-foundation.mjs', import.meta.url), 'utf8');
  const workflow = readFileSync(new URL('../../../.github/workflows/darwin-selector-timing.yml', import.meta.url), 'utf8');
  assert.match(foundation, /selector-timing-export/);
  assert.match(foundation, /const fixtureArgs = timingExport \? \['qualification\/selector-timing-driver\.mjs', timingExport\] : \['scripts\/test\.mjs', 'fixtures'\]/);
  assert.match(foundation, /const fixturesPassed = run\('fixtures', fixtureArgs\)/);
  assert.match(workflow, /runs-on: macos-15/);
  assert.match(workflow, /qualification-foundation\.mjs --selector-timing-export/);
  assert.match(workflow, /selector-timing-artifacts\.mjs/);
  assert.match(workflow, /if: always\(\) && steps\.artifacts\.outcome == 'success'/);
  assert.match(workflow, /selector-timing-upload\/selector-timing\.json\n\s*\$\{\{ runner\.temp \}\}\/selector-timing-upload\/selector-timing\.jsonl/);
  assert.doesNotMatch(workflow, /continue-on-error|NODE_OPTIONS|path:.*\*/);
});


test('Darwin timing push selection includes executable/schema changes and excludes result notes', () => {
  const workflow = readFileSync(new URL('../../../.github/workflows/darwin-selector-timing.yml', import.meta.url), 'utf8');
  const section = workflow.match(/    paths:\n([\s\S]*?)\npermissions:/)?.[1];
  assert.ok(section, 'explicit push paths required');
  const patterns = section.split('\n').map(line => line.trim()).filter(line => line.startsWith('- ')).map(line => line.slice(2));
  const selected = path => patterns.some(pattern => matchesGlob(path, pattern));
  for (const path of [
    'packages/software-factory/qualification/selector-timing.mjs',
    'packages/software-factory/qualification/selector-timing-preload.mjs',
    'packages/software-factory/qualification/selector-timing-driver.mjs',
    'packages/software-factory/qualification/selector-timing-artifacts.mjs',
    'packages/software-factory/qualification/selector-timing-attempts.mjs',
    'packages/software-factory/qualification/selector-timing-preflight.mjs',
    'packages/software-factory/qualification/selector-timing-registry.json',
    'packages/software-factory/qualification/selector-timing-experiment.json',
    'packages/software-factory/scripts/ordered-tests.mjs',
    'packages/software-factory/scripts/ordered-test-worker.mjs',
  ]) assert.equal(selected(path), true, path);
  for (const path of [
    '.github/workflows/darwin-selector-timing.yml',
    'packages/software-factory/qualification/selector-timing-closure.ExecPlan.md',
    'packages/software-factory/qualification/darwin-selector-timing.ExecPlan.md',
    'brain/plans/software-factory/research/darwin-selector-timing-baseline-2026-11-04.md',
  ]) assert.equal(selected(path), false, path);
  assert.ok(patterns.includes('packages/software-factory/qualification/selector-timing-experiment.json'), 'explicit deliberate experiment control required');
});


test('Gemini source-contract qualification is isolated from canonical provider selection', () => {
  const dispatch = fileURLToPath(new URL('../scripts/test.mjs', import.meta.url));
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  const result = spawnSync(process.execPath, [dispatch, 'qualification', '--area', 'gemini-contract'], { encoding: 'utf8', timeout: 5000, env });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /synthetic Gemini text is a proposed candidate rather than provider success/);
  assert.match(result.stdout, /cannot distinguish unmarked internal stop from ordinary completion/);
  assert.match(result.stdout, /tests 83/);
  for (const args of [['adapters', '--provider', 'gemini'], ['qualification', '--area', 'gemini-contract', '--provider', 'gemini']]) {
    const refused = spawnSync(process.execPath, [dispatch, ...args], { encoding: 'utf8', timeout: 5000, env });
    assert.equal(refused.status, 1, refused.stdout + refused.stderr);
    assert.match(refused.stderr, /no tests match supplied filters/);
    assert.equal(refused.stdout, '');
  }
});


test('learning copy qualification is separately selectable without changing the original fixtures', () => {
  const dispatch = fileURLToPath(new URL('../scripts/test.mjs', import.meta.url));
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  const result = spawnSync(process.execPath, [dispatch, 'qualification', '--area', 'learning-toolchain-copy'], { encoding: 'utf8', timeout: 5000, env });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /selected learning compiler closure preserves regular-file bytes and remains independent/);
  assert.match(result.stdout, /tests 1/);
});


test('OpenCode source-contract qualification stays separate from canonical provider support', () => {
  const dispatch = fileURLToPath(new URL('../scripts/test.mjs', import.meta.url));
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  const result = spawnSync(process.execPath, [dispatch, 'qualification', '--area', 'opencode-contract'], { encoding: 'utf8', timeout: 5000, env });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /synthetic OpenCode text without a terminal is only a candidate with unknown terminal evidence/);
  assert.match(result.stdout, /source success and external user interruption can have indistinguishable JSONL and exit fixtures/);
  assert.match(result.stdout, /tests 68/);
  for (const args of [['adapters', '--provider', 'opencode'], ['qualification', '--area', 'opencode-contract', '--provider', 'opencode']]) {
    const refused = spawnSync(process.execPath, [dispatch, ...args], { encoding: 'utf8', timeout: 5000, env });
    assert.equal(refused.status, 1, refused.stdout + refused.stderr);
    assert.match(refused.stderr, /no tests match supplied filters/);
    assert.equal(refused.stdout, '');
  }
});

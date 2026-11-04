import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
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

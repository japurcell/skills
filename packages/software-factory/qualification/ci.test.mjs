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
]) test(name, () => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-ci-test-'));
  try {
    const env = { ...process.env, GITHUB_ACTIONS: 'false', FACTORY_EVIDENCE_DIR: directory };
    delete env.FACTORY_NPM_CLI;
    delete env.FACTORY_TEST_PYTHON;
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
      env: { ...process.env, FACTORY_EVIDENCE_DIR: directory, FACTORY_NPM_CLI: 'unused-npm-cli', FACTORY_TEST_PYTHON: process.execPath },
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

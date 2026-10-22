import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

for (const [name, script, expected] of [
  ['bootstrap refuses local downloads and retains structured failure evidence', 'qualification-bootstrap.mjs', /ephemeral GitHub Actions/],
  ['foundation refuses missing exact npm prerequisite and retains structured failure evidence', 'qualification-foundation.mjs', /explicit bundled npm CLI/],
]) test(name, () => {
  const directory = mkdtempSync(join(tmpdir(), 'factory-ci-test-'));
  try {
    const env = { ...process.env, GITHUB_ACTIONS: 'false', FACTORY_EVIDENCE_DIR: directory };
    delete env.FACTORY_NPM_CLI;
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

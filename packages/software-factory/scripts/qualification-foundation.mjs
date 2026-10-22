import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { release } from 'node:os';
import { isAbsolute, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const cwd = fileURLToPath(new URL('../', import.meta.url));
const evidence = resolve(process.env.FACTORY_EVIDENCE_DIR ?? join(cwd, 'qualification-results'));
mkdirSync(evidence, { recursive: true });
const report = { scope: 'foundation-only', status: 'failed', node: process.version, sqlite: process.versions.sqlite,
  platform: process.platform, arch: process.arch, os: release(), commit: process.env.GITHUB_SHA ?? null,
  runnerImage: { os: process.env.ImageOS ?? null, version: process.env.ImageVersion ?? null },
  excludedAcceptance: ['unfinished product suites', 'live providers', 'desktop visible notification delivery (T17 last)'], steps: [] };
function run(name, args, timeout = 120_000, executable = process.execPath) {
  const start = Date.now();
  const result = spawnSync(executable, args, { cwd, encoding: 'utf8', timeout, maxBuffer: 8_388_608 });
  const log = `${result.stdout ?? ''}${result.stderr ?? ''}${result.error ? `\n${result.error.message}\n` : ''}`;
  writeFileSync(join(evidence, `${name}.log`), log);
  process.stdout.write(`\n[${name}]\n${log}`);
  const step = { name, command: [executable, ...args], status: result.status === 0 && !result.error ? 'passed' : 'failed',
    exitCode: result.status, signal: result.signal, elapsedMs: Date.now() - start, log: `${name}.log` };
  report.steps.push(step);
  writeFileSync(join(evidence, 'foundation.json'), `${JSON.stringify(report, null, 2)}\n`);
  return step.status === 'passed';
}
try {
  const manifest = JSON.parse(readFileSync(join(cwd, 'qualification/runtime-manifest.json'), 'utf8'));
  assert.equal(process.version, manifest.node, 'manifest-pinned runtime required');
  assert.equal(process.versions.sqlite, manifest.sqlite, 'reviewed bundled SQLite required');
  assert.ok(process.env.FACTORY_NPM_CLI, 'explicit bundled npm CLI required');
  assert.ok(process.env.FACTORY_TEST_PYTHON, 'explicit Python 3.11 or newer interpreter required');
  assert.ok(isAbsolute(process.env.FACTORY_TEST_PYTHON), 'selected Python interpreter must be an absolute path');
  assert.ok(run('python', ['-I', '-c',
    'import json,sys;sys.exit("Python 3.11 or newer required") if sys.version_info < (3,11) else print(json.dumps({"version":sys.version.split()[0]}))',
  ], 10_000, process.env.FACTORY_TEST_PYTHON), 'Python prerequisite failed');
  const installArgs = [process.env.FACTORY_NPM_CLI, 'ci', '--ignore-scripts', '--no-audit', '--no-fund'];
  if (process.env.FACTORY_NPM_OFFLINE === 'true') installArgs.push('--offline', '--cache', process.env.FACTORY_NPM_CACHE ?? '/tmp/software-factory-npm-cache');
  assert.ok(run('install', installArgs), 'locked dependency installation failed');
  run('typecheck', [process.env.FACTORY_NPM_CLI, 'run', 'typecheck']);
  run('build', [process.env.FACTORY_NPM_CLI, 'run', 'build']);
  const fixturesPassed = run('fixtures', ['scripts/test.mjs', 'fixtures']);
  if (!fixturesPassed) {
    // Preserve the original failed fixture step and diagnose one public case
    // separately. Windows failed before source extraction; the hosted macOS
    // trace reached the interrupted-source case before its outer bound ended.
    const diagnosticCase = process.platform === 'win32'
      ? '^explicit extraction saves examined ended sources and a justified empty result without changing active inputs$'
      : '^failed, needs-input and interrupted invocations are valid explicit learning sources$';
    run('learning-fixture-diagnostic', [
      '--test', '--test-reporter=spec',
      `--test-name-pattern=${diagnosticCase}`,
      'test/learning.test.mjs',
    ]);
  }
  run('store', ['scripts/test.mjs', 'store']);
  const placementPassed = run('placement', ['--test', 'test/placement.test.mjs']);
  if (process.platform === 'darwin' && !placementPassed) {
    run('filesystem-diagnostic', ['scripts/qualification-filesystem.mjs']);
  }
  run('ci-contract', ['--test', 'qualification/ci.test.mjs']);
  run('runtime-tests', ['scripts/test.mjs', 'qualification', '--area', 'runtime']);
  // Keep direct structured native storage proof separate from test-runner output.
  run('runtime', ['qualification/runtime.ts'], 30_000);
  const direct = report.steps.find((step) => step.name === 'runtime');
  if (direct.status === 'passed') {
    const json = readFileSync(join(evidence, 'runtime.log'), 'utf8').split('\n').find((line) => line.startsWith('{'));
    assert.ok(json, 'native runtime emitted no structured evidence');
    writeFileSync(join(evidence, 'runtime.json'), `${JSON.stringify(JSON.parse(json), null, 2)}\n`);
  }
  assert.ok(report.steps.every((step) => step.status === 'passed'), 'foundation qualification failed; inspect every native step artifact');
  report.status = 'passed';
} catch (error) {
  report.error = error instanceof Error ? error.message : String(error);
  process.stderr.write(`${report.error}\n`);
  process.exitCode = 1;
} finally {
  writeFileSync(join(evidence, 'foundation.json'), `${JSON.stringify(report, null, 2)}\n`);
}

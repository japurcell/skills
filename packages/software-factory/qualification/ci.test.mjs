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


test('repair inspection is a read-only qualification area and does not advertise maintenance apply', () => {
  const dispatch = fileURLToPath(new URL('../scripts/test.mjs', import.meta.url));
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_TEST_NODE_ARCHIVE;
  const selected = spawnSync(process.execPath, [dispatch, 'qualification', '--area', 'repair-inspection'], { encoding: 'utf8', timeout: 5000, env });
  assert.equal(selected.status, 1, selected.stdout + selected.stderr);
  for (const name of ['public external inspection authenticates retained installation', 'intact recorded upgrade resume', 'live original launcher']) {
    assert.match(selected.stdout + selected.stderr, new RegExp(name));
  }
  assert.doesNotMatch(selected.stderr, /no tests match supplied filters/);
  for (const args of [['maintenance', '--operation', 'repair'], ['maintenance']]) {
    const refused = spawnSync(process.execPath, [dispatch, ...args], { encoding: 'utf8', timeout: 5000, env });
    assert.equal(refused.status, 1, refused.stdout + refused.stderr);
    assert.match(refused.stderr, /no tests match supplied filters|not implemented/);
    assert.equal(refused.stdout, '');
  }
});


test('repair inspection native jobs retain independent Linux and Darwin budgets and exact inputs', () => {
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-repair-inspection.yml', import.meta.url), 'utf8');
  assert.match(workflow, /os: ubuntu-24.04\n\s+target: linux-x64/);
  assert.match(workflow, /os: macos-15\n\s+target: darwin-arm64/);
  assert.doesNotMatch(workflow, /windows-|continue-on-error|--test-name-pattern/);
  assert.match(workflow, /python-version: '3.13.14'/);
  assert.match(workflow, /qualification-bootstrap\.mjs/);
  assert.match(workflow, /ci --ignore-scripts --no-audit --no-fund/);
  assert.match(workflow, /cp toolchain\/package\.json toolchain\/package-lock\.json/);
  assert.match(workflow, /--prefix \"\$RUNNER_TEMP\/repair-inspection-toolchain\"/);
  assert.doesNotMatch(workflow, /--prefix toolchain/);
  assert.match(workflow, /FACTORY_ATOMIC_PYTHON:.*steps\.python\.outputs\.python-path/);
  assert.match(workflow, /FACTORY_TEST_NPM_CACHE_SEED:.*runner\.temp/);
  assert.match(workflow, /timeout-minutes: 20[\s\S]*run: node packages\/software-factory\/scripts\/test\.mjs qualification --area repair-inspection/);
  const foundation = readFileSync(new URL('../scripts/qualification-foundation.mjs', import.meta.url), 'utf8');
  assert.doesNotMatch(foundation, /repair-inspection/);
});


test('cleanup reads launch the exact registered suite without advertising cleanup mutation', () => {
  const dispatch = fileURLToPath(new URL('../scripts/test.mjs', import.meta.url));
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_SELECTOR_TIMING_ROOT;
  delete env.FACTORY_TEST_NODE_ARCHIVE;
  // Observe the actual dispatcher in a disposable child. The foundation phase below
  // still executes all twelve native cases; this contract proves only their launch.
  for (const exitCode of [0, 7]) {
    const program = `
      import assert from 'node:assert/strict';
      import childProcess from 'node:child_process';
      import { EventEmitter } from 'node:events';
      import { syncBuiltinESMExports } from 'node:module';
      let launches = 0;
      childProcess.spawn = (command, args, options) => {
        assert.equal(++launches, 1);
        assert.equal(command, process.execPath);
        assert.deepEqual(args, ['--test', 'test/cleanup-readers.test.mjs']);
        assert.deepEqual(options, { cwd: new URL('../', ${JSON.stringify(new URL('../scripts/test.mjs', import.meta.url).href)}), stdio: 'inherit' });
        assert.equal(options.shell, undefined);
        const child = new EventEmitter();
        setImmediate(() => child.emit('exit', ${exitCode}, null));
        return child;
      };
      syncBuiltinESMExports();
      await import(${JSON.stringify(new URL('../scripts/test.mjs', import.meta.url).href)});
      assert.equal(launches, 1);
      assert.equal(process.exitCode, ${exitCode});
    `;
    const result = spawnSync(process.execPath, ['--input-type=module', '-e', program, 'qualification', '--area', 'cleanup-reads'], { encoding: 'utf8', timeout: 5000, env });
    assert.ifError(result.error);
    assert.equal(result.status, exitCode, result.stdout + result.stderr);
    assert.equal(result.signal, null);
    assert.equal(result.stdout, '');
    assert.equal(result.stderr, '');
  }
  for (const args of [['maintenance', '--operation', 'cleanup'], ['maintenance']]) {
    const refused = spawnSync(process.execPath, [dispatch, ...args], { encoding: 'utf8', timeout: 5000, env });
    assert.equal(refused.status, 1, refused.stdout + refused.stderr);
    assert.match(refused.stderr, /no tests match supplied filters|not implemented/);
    assert.equal(refused.stdout, '');
  }
  const foundation = readFileSync(new URL('../scripts/qualification-foundation.mjs', import.meta.url), 'utf8');
  assert.match(foundation, /run\('cleanup-reads', \['scripts\/test\.mjs', 'qualification', '--area', 'cleanup-reads'\]\)/);
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-qualification.yml', import.meta.url), 'utf8');
  assert.match(workflow, /name: Verify and extract exact official native runtime\n\s+id: bootstrap/);
  assert.match(workflow, /- name: Run Windows cleanup storage diagnostic\n\s+if: always\(\) && matrix\.target == 'win32-x64' && steps\.bootstrap\.outcome == 'success'[\s\S]*?run: node --test packages\/software-factory\/test\/cleanup-storage-diagnostics\.test\.mjs/);
  assert.ok(workflow.indexOf('- name: Run locked foundational checks') < workflow.indexOf('- name: Run Windows cleanup storage diagnostic'));
  assert.doesNotMatch(workflow, /continue-on-error/);
});


test('cleanup backup qualification launches only exact POSIX areas and retains independent public proof budgets', () => {
  const controlPath = 'packages/software-factory/qualification/cleanup-native-execution.json';
  const control = JSON.parse(readFileSync(new URL('./cleanup-native-execution.json', import.meta.url), 'utf8'));
  assert.deepEqual(control, {
    version: 1,
    purpose: 'initial-c2-native-and-storage-qualification',
    sourceHead: '927f78bf62fa5e3ce3f7f35f39046c6bf3d65504',
    ordinaryProof: { head: 'aba7af4e05ded06eace8e38a139965ba2077d496', files: 59, tests: 735 },
    receipt: { inputs: 729, outputs: 171, sha256: '98925fd67888f369fcfc5206f12d66620adc4bfa246b9b2148c2b25cf6469e92' },
    publicBackup: { targets: ['linux-x64', 'darwin-arm64'], area: 'cleanup-backups-public', tests: 43 },
    foundation: { targets: ['linux-x64', 'darwin-arm64', 'win32-x64'], windowsDiagnosticTests: 4 },
  });
  const nativeWorkflow = readFileSync(new URL('../../../.github/workflows/software-factory-cleanup-backups.yml', import.meta.url), 'utf8');
  assert.ok(nativeWorkflow.includes(`      - ${controlPath}\n`));
  const foundationWorkflow = readFileSync(new URL('../../../.github/workflows/software-factory-qualification.yml', import.meta.url), 'utf8');
  const pushPaths = foundationWorkflow.split('  push:\n')[1].split('  workflow_dispatch:')[0];
  assert.match(pushPaths, /'packages\/software-factory\/\*\*'/);
  assert.ok(matchesGlob(controlPath, 'packages/software-factory/**'));
  for (const name of ['windows-factory-owned-image.yml', 'darwin-selector-timing.yml', 'software-factory-repair-inspection.yml']) {
    const text = readFileSync(new URL(`../../../.github/workflows/${name}`, import.meta.url), 'utf8');
    const paths = [...text.split('    paths:\n')[1].split('\npermissions:')[0].matchAll(/^      - ([^\n]+)/gm)].map(match => match[1]);
    assert.equal(paths.some(pattern => matchesGlob(controlPath, pattern)), false, name);
  }
  const dispatch = new URL('../scripts/test.mjs', import.meta.url).href;
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_SELECTOR_TIMING_ROOT;
  for (const [platform, arch, supported] of [['darwin', 'arm64', true], ['linux', 'x64', true], ['win32', 'x64', false]]) {
    for (const [area, file] of [['cleanup-backups', 'test/cleanup-backups.test.mjs'], ['cleanup-backups-public', 'qualification/cleanup-backups-public.qualification.mjs']]) {
      const program = `
        import assert from 'node:assert/strict';
        import childProcess from 'node:child_process';
        import { EventEmitter } from 'node:events';
        import { syncBuiltinESMExports } from 'node:module';
        Object.defineProperty(process, 'platform', { value: ${JSON.stringify(platform)} });
        Object.defineProperty(process, 'arch', { value: ${JSON.stringify(arch)} });
        let launches = 0;
        childProcess.spawn = (command, args, options) => {
          assert.equal(++launches, 1);
          assert.equal(command, process.execPath);
          assert.deepEqual(args, ['--test-concurrency=1', '--test', ${JSON.stringify(file)}]);
          assert.deepEqual(options, { cwd: new URL('../', ${JSON.stringify(dispatch)}), stdio: 'inherit' });
          const child = new EventEmitter();
          setImmediate(() => child.emit('exit', 7, null));
          return child;
        };
        syncBuiltinESMExports();
        await import(${JSON.stringify(dispatch)});
        assert.equal(launches, ${supported ? 1 : 0});
        assert.equal(process.exitCode, ${supported ? 7 : 1});
      `;
      const result = spawnSync(process.execPath, ['--input-type=module', '-e', program, 'qualification', '--area', area], { encoding: 'utf8', timeout: 5000, env });
      assert.ifError(result.error);
      assert.equal(result.status, supported ? 7 : 1, result.stdout + result.stderr);
      assert.equal(result.signal, null);
      if (!supported) assert.match(result.stderr, /unsupported qualification target: win32-x64/);
    }
  }
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-cleanup-backups.yml', import.meta.url), 'utf8');
  assert.match(workflow, /os: ubuntu-24.04\n\s+target: linux-x64/);
  assert.match(workflow, /os: macos-15\n\s+target: darwin-arm64/);
  assert.doesNotMatch(workflow, /windows-|continue-on-error|--test-name-pattern|--prefix toolchain/);
  assert.match(workflow, /python-version: '3.13.14'/);
  assert.match(workflow, /qualification-bootstrap\.mjs/);
  assert.match(workflow, /cp toolchain\/package\.json toolchain\/package-lock\.json/);
  assert.match(workflow, /--prefix "\$RUNNER_TEMP\/cleanup-backups-toolchain"/);
  assert.match(workflow, /FACTORY_ATOMIC_PYTHON:.*steps\.python\.outputs\.python-path/);
  assert.match(workflow, /FACTORY_TEST_NPM_CACHE_SEED:.*runner\.temp/);
  assert.match(workflow, /timeout-minutes: 10[\s\S]*run: node packages\/software-factory\/scripts\/test\.mjs qualification --area cleanup-backups-public/);
  const foundation = readFileSync(new URL('../scripts/qualification-foundation.mjs', import.meta.url), 'utf8');
  assert.doesNotMatch(foundation, /cleanup-backups/);
  const refused = spawnSync(process.execPath, [fileURLToPath(new URL(dispatch)), 'maintenance', '--operation', 'cleanup'], { encoding: 'utf8', timeout: 5000, env });
  assert.equal(refused.status, 1, refused.stdout + refused.stderr);
  assert.match(refused.stderr, /no tests match supplied filters/);
  assert.equal(refused.stdout, '');
});


test('cleanup advisory qualification is explicit POSIX-only and keeps genuine public proof separate', () => {
  const dispatch = new URL('../scripts/test.mjs', import.meta.url).href;
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_SELECTOR_TIMING_ROOT;
  for (const [platform, arch, supported] of [['darwin', 'arm64', true], ['linux', 'x64', true], ['win32', 'x64', false]]) {
    for (const [area, file] of [['cleanup-advisory', 'test/cleanup-reference-graph.test.mjs'], ['cleanup-advisory-public', 'qualification/cleanup-advisory-public.qualification.mjs']]) {
      const program = `
        import assert from 'node:assert/strict';
        import childProcess from 'node:child_process';
        import { EventEmitter } from 'node:events';
        import { syncBuiltinESMExports } from 'node:module';
        Object.defineProperty(process, 'platform', { value: ${JSON.stringify(platform)} });
        Object.defineProperty(process, 'arch', { value: ${JSON.stringify(arch)} });
        let launches = 0;
        childProcess.spawn = (command, args, options) => {
          assert.equal(++launches, 1);
          assert.equal(command, process.execPath);
          assert.deepEqual(args, ['--test-concurrency=1', '--test', ${JSON.stringify(file)}]);
          assert.deepEqual(options, { cwd: new URL('../', ${JSON.stringify(dispatch)}), stdio: 'inherit' });
          const child = new EventEmitter();
          setImmediate(() => child.emit('exit', 7, null));
          return child;
        };
        syncBuiltinESMExports();
        await import(${JSON.stringify(dispatch)});
        assert.equal(launches, ${supported ? 1 : 0});
        assert.equal(process.exitCode, ${supported ? 7 : 1});
      `;
      const result = spawnSync(process.execPath, ['--input-type=module', '-e', program, 'qualification', '--area', area], { encoding: 'utf8', timeout: 5000, env });
      assert.ifError(result.error);
      assert.equal(result.status, supported ? 7 : 1, result.stdout + result.stderr);
      assert.equal(result.signal, null);
      if (!supported) assert.match(result.stderr, /unsupported qualification target: win32-x64/);
    }
  }
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-cleanup-advisory.yml', import.meta.url), 'utf8');
  assert.match(workflow, /os: ubuntu-24.04\n\s+target: linux-x64/);
  assert.match(workflow, /os: macos-15\n\s+target: darwin-arm64/);
  assert.doesNotMatch(workflow, /windows-|continue-on-error|--test-name-pattern|--prefix toolchain/);
  assert.match(workflow, /python-version: '3.13.14'/);
  assert.match(workflow, /qualification-bootstrap\.mjs/);
  assert.match(workflow, /cp toolchain\/package\.json toolchain\/package-lock\.json/);
  assert.match(workflow, /--prefix "\$RUNNER_TEMP\/cleanup-advisory-toolchain"/);
  assert.match(workflow, /FACTORY_ATOMIC_PYTHON:.*steps\.python\.outputs\.python-path/);
  assert.match(workflow, /FACTORY_TEST_NPM_CACHE_SEED:.*runner\.temp/);
  assert.match(workflow, /timeout-minutes: 10[\s\S]*run: node packages\/software-factory\/scripts\/test\.mjs qualification --area cleanup-advisory-public/);
  const foundation = readFileSync(new URL('../scripts/qualification-foundation.mjs', import.meta.url), 'utf8');
  assert.doesNotMatch(foundation, /cleanup-advisory/);
  const refused = spawnSync(process.execPath, [fileURLToPath(new URL(dispatch)), 'maintenance', '--operation', 'cleanup'], { encoding: 'utf8', timeout: 5000, env });
  assert.equal(refused.status, 1, refused.stdout + refused.stderr);
  assert.match(refused.stderr, /no tests match supplied filters/);
  assert.equal(refused.stdout, '');
});


test('loader source-contract selection never registers native loading and binds explicit Python profiles', () => {
  const dispatch = new URL('../scripts/test.mjs', import.meta.url).href;
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_SELECTOR_TIMING_ROOT;
  assert.ok(env.FACTORY_TEST_PYTHON, 'CI requires independently selected Python');
  assert.equal(env.FACTORY_WINDOWS_LOADER_TEST_PYTHON, env.FACTORY_TEST_PYTHON, 'loader contract profile must explicitly select the same Python');
  for (const exitCode of [0, 7]) {
    const program = `
      import assert from 'node:assert/strict';
      import childProcess from 'node:child_process';
      import { EventEmitter } from 'node:events';
      import { syncBuiltinESMExports } from 'node:module';
      let launches = 0;
      childProcess.spawn = (command, args, options) => {
        assert.equal(++launches, 1);
        assert.equal(command, process.execPath);
        assert.deepEqual(args, ['--test', 'test/windows-storage-loader-contract.test.mjs']);
        assert.deepEqual(options, { cwd: new URL('../', ${JSON.stringify(dispatch)}), stdio: 'inherit' });
        const child = new EventEmitter();
        setImmediate(() => child.emit('exit', ${exitCode}, null));
        return child;
      };
      syncBuiltinESMExports();
      await import(${JSON.stringify(dispatch)});
      assert.equal(launches, 1);
      assert.equal(process.exitCode, ${exitCode});
    `;
    const result = spawnSync(process.execPath, ['--input-type=module', '-e', program, 'qualification', '--area', 'windows-storage-loader-contract'], { encoding: 'utf8', timeout: 5000, env });
    assert.ifError(result.error);
    assert.equal(result.status, exitCode, result.stdout + result.stderr);
    assert.equal(result.signal, null);
    assert.equal(result.stdout, '');
    assert.equal(result.stderr, '');
  }
  const refused = spawnSync(process.execPath, [fileURLToPath(new URL(dispatch)), 'qualification', '--area', 'windows-storage-loader-native'], { encoding: 'utf8', timeout: 5000, env });
  assert.equal(refused.status, 1, refused.stdout + refused.stderr);
  assert.match(refused.stderr, /no tests match supplied filters/);
  assert.equal(refused.stdout, '');
  for (const name of ['software-factory-qualification.yml', 'darwin-selector-timing.yml']) {
    const workflow = readFileSync(new URL(`../../../.github/workflows/${name}`, import.meta.url), 'utf8');
    assert.match(workflow, /FACTORY_WINDOWS_LOADER_TEST_PYTHON:.*steps\.python\.outputs\.python-path/);
  }
});


test('cleanup learning closure has isolated POSIX qualification and preserves the existing base advisory proof', () => {
  const dispatch = new URL('../scripts/test.mjs', import.meta.url).href;
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_SELECTOR_TIMING_ROOT;
  for (const [platform, arch, supported] of [['darwin', 'arm64', true], ['linux', 'x64', true], ['win32', 'x64', false]]) {
    for (const [area, file] of [['cleanup-learning', 'test/cleanup-learning-closure.test.mjs'], ['cleanup-learning-public', 'qualification/cleanup-learning-public.qualification.mjs']]) {
      const program = `
        import assert from 'node:assert/strict';
        import childProcess from 'node:child_process';
        import { EventEmitter } from 'node:events';
        import { syncBuiltinESMExports } from 'node:module';
        Object.defineProperty(process, 'platform', { value: ${JSON.stringify(platform)} });
        Object.defineProperty(process, 'arch', { value: ${JSON.stringify(arch)} });
        let launches = 0;
        childProcess.spawn = (command, args, options) => {
          assert.equal(++launches, 1);
          assert.equal(command, process.execPath);
          assert.deepEqual(args, ['--test-concurrency=1', '--test', ${JSON.stringify(file)}]);
          assert.deepEqual(options, { cwd: new URL('../', ${JSON.stringify(dispatch)}), stdio: 'inherit' });
          const child = new EventEmitter();
          setImmediate(() => child.emit('exit', 7, null));
          return child;
        };
        syncBuiltinESMExports();
        await import(${JSON.stringify(dispatch)});
        assert.equal(launches, ${supported ? 1 : 0});
        assert.equal(process.exitCode, ${supported ? 7 : 1});
      `;
      const result = spawnSync(process.execPath, ['--input-type=module', '-e', program, 'qualification', '--area', area], { encoding: 'utf8', timeout: 5000, env });
      assert.ifError(result.error);
      assert.equal(result.status, supported ? 7 : 1, result.stdout + result.stderr);
      assert.equal(result.signal, null);
      if (!supported) assert.match(result.stderr, /unsupported qualification target: win32-x64/);
    }
  }
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-cleanup-learning.yml', import.meta.url), 'utf8');
  assert.match(workflow, /os: ubuntu-24.04\n\s+target: linux-x64/);
  assert.match(workflow, /os: macos-15\n\s+target: darwin-arm64/);
  assert.doesNotMatch(workflow, /windows-|continue-on-error|--test-name-pattern|--prefix toolchain/);
  assert.match(workflow, /python-version: '3.13.14'/);
  assert.match(workflow, /qualification-bootstrap\.mjs/);
  assert.match(workflow, /cp toolchain\/package\.json toolchain\/package-lock\.json/);
  assert.match(workflow, /--prefix "\$RUNNER_TEMP\/cleanup-learning-toolchain"/);
  assert.match(workflow, /FACTORY_ATOMIC_PYTHON:.*steps\.python\.outputs\.python-path/);
  assert.match(workflow, /FACTORY_TEST_NPM_CACHE_SEED:.*runner\.temp/);
  assert.match(workflow, /timeout-minutes: 10[\s\S]*run: node packages\/software-factory\/scripts\/test\.mjs qualification --area cleanup-learning-public/);
  const baseWorkflow = readFileSync(new URL('../../../.github/workflows/software-factory-cleanup-advisory.yml', import.meta.url), 'utf8');
  assert.match(baseWorkflow, /qualification --area cleanup-advisory-public/);
  const foundation = readFileSync(new URL('../scripts/qualification-foundation.mjs', import.meta.url), 'utf8');
  assert.doesNotMatch(foundation, /cleanup-learning/);
  const refused = spawnSync(process.execPath, [fileURLToPath(new URL(dispatch)), 'maintenance', '--operation', 'cleanup'], { encoding: 'utf8', timeout: 5000, env });
  assert.equal(refused.status, 1, refused.stdout + refused.stderr);
  assert.match(refused.stderr, /no tests match supplied filters/);
  assert.equal(refused.stdout, '');
});

test('cleanup action closure has isolated POSIX qualification and preserves existing learning closure proof', () => {
  const dispatch = new URL('../scripts/test.mjs', import.meta.url).href;
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_SELECTOR_TIMING_ROOT;
  for (const [platform, arch, supported] of [['darwin', 'arm64', true], ['linux', 'x64', true], ['win32', 'x64', false]]) {
    for (const [area, file] of [['cleanup-actions', 'test/cleanup-action-closure.test.mjs'], ['cleanup-actions-public', 'qualification/cleanup-actions-public.qualification.mjs']]) {
      const program = `
        import assert from 'node:assert/strict';
        import childProcess from 'node:child_process';
        import { EventEmitter } from 'node:events';
        import { syncBuiltinESMExports } from 'node:module';
        Object.defineProperty(process, 'platform', { value: ${JSON.stringify(platform)} });
        Object.defineProperty(process, 'arch', { value: ${JSON.stringify(arch)} });
        let launches = 0;
        childProcess.spawn = (command, args, options) => {
          assert.equal(++launches, 1);
          assert.equal(command, process.execPath);
          assert.deepEqual(args, ['--test-concurrency=1', '--test', ${JSON.stringify(file)}]);
          assert.deepEqual(options, { cwd: new URL('../', ${JSON.stringify(dispatch)}), stdio: 'inherit' });
          const child = new EventEmitter();
          setImmediate(() => child.emit('exit', 7, null));
          return child;
        };
        syncBuiltinESMExports();
        await import(${JSON.stringify(dispatch)});
        assert.equal(launches, ${supported ? 1 : 0});
        assert.equal(process.exitCode, ${supported ? 7 : 1});
      `;
      const result = spawnSync(process.execPath, ['--input-type=module', '-e', program, 'qualification', '--area', area], { encoding: 'utf8', timeout: 5000, env });
      assert.ifError(result.error);
      assert.equal(result.status, supported ? 7 : 1, result.stdout + result.stderr);
      assert.equal(result.signal, null);
      if (!supported) assert.match(result.stderr, /unsupported qualification target: win32-x64/);
    }
  }
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-cleanup-actions.yml', import.meta.url), 'utf8');
  assert.match(workflow, /os: ubuntu-24.04\n\s+target: linux-x64/);
  assert.match(workflow, /os: macos-15\n\s+target: darwin-arm64/);
  assert.doesNotMatch(workflow, /windows-|continue-on-error|--test-name-pattern|--prefix toolchain/);
  assert.match(workflow, /python-version: '3.13.14'/);
  assert.match(workflow, /qualification-bootstrap\.mjs/);
  assert.match(workflow, /cp toolchain\/package\.json toolchain\/package-lock\.json/);
  assert.match(workflow, /--prefix "\$RUNNER_TEMP\/cleanup-actions-toolchain"/);
  assert.match(workflow, /FACTORY_ATOMIC_PYTHON:.*steps\.python\.outputs\.python-path/);
  assert.match(workflow, /FACTORY_TEST_NPM_CACHE_SEED:.*runner\.temp/);
  assert.match(workflow, /timeout-minutes: 10[\s\S]*run: node packages\/software-factory\/scripts\/test\.mjs qualification --area cleanup-actions-public/);
  const baseWorkflow = readFileSync(new URL('../../../.github/workflows/software-factory-cleanup-learning.yml', import.meta.url), 'utf8');
  assert.match(baseWorkflow, /qualification --area cleanup-learning-public/);
  const foundation = readFileSync(new URL('../scripts/qualification-foundation.mjs', import.meta.url), 'utf8');
  assert.doesNotMatch(foundation, /cleanup-actions/);
  const refused = spawnSync(process.execPath, [fileURLToPath(new URL(dispatch)), 'maintenance', '--operation', 'cleanup'], { encoding: 'utf8', timeout: 5000, env });
  assert.equal(refused.status, 1, refused.stdout + refused.stderr);
  assert.match(refused.stderr, /no tests match supplied filters/);
  assert.equal(refused.stdout, '');
});

test('cleanup ordinary reports have isolated POSIX qualification and preserve action closure proof', () => {
  const dispatch = new URL('../scripts/test.mjs', import.meta.url).href;
  const env = { ...process.env };
  delete env.NODE_TEST_CONTEXT;
  delete env.FACTORY_SELECTOR_TIMING_ROOT;
  for (const [platform, arch, supported] of [['darwin', 'arm64', true], ['linux', 'x64', true], ['win32', 'x64', false]]) {
    for (const [area, file] of [['cleanup-ordinary', 'test/cleanup-ordinary-closure.test.mjs'], ['cleanup-ordinary-public', 'qualification/cleanup-ordinary-public.qualification.mjs']]) {
      const program = `
        import assert from 'node:assert/strict';
        import childProcess from 'node:child_process';
        import { EventEmitter } from 'node:events';
        import { syncBuiltinESMExports } from 'node:module';
        Object.defineProperty(process, 'platform', { value: ${JSON.stringify(platform)} });
        Object.defineProperty(process, 'arch', { value: ${JSON.stringify(arch)} });
        let launches = 0;
        childProcess.spawn = (command, args, options) => {
          assert.equal(++launches, 1);
          assert.equal(command, process.execPath);
          assert.deepEqual(args, ['--test-concurrency=1', '--test', ${JSON.stringify(file)}]);
          assert.deepEqual(options, { cwd: new URL('../', ${JSON.stringify(dispatch)}), stdio: 'inherit' });
          const child = new EventEmitter();
          setImmediate(() => child.emit('exit', 7, null));
          return child;
        };
        syncBuiltinESMExports();
        await import(${JSON.stringify(dispatch)});
        assert.equal(launches, ${supported ? 1 : 0});
        assert.equal(process.exitCode, ${supported ? 7 : 1});
      `;
      const result = spawnSync(process.execPath, ['--input-type=module', '-e', program, 'qualification', '--area', area], { encoding: 'utf8', timeout: 5000, env });
      assert.ifError(result.error);
      assert.equal(result.status, supported ? 7 : 1, result.stdout + result.stderr);
      assert.equal(result.signal, null);
      if (!supported) assert.match(result.stderr, /unsupported qualification target: win32-x64/);
    }
  }
  const workflow = readFileSync(new URL('../../../.github/workflows/software-factory-cleanup-ordinary.yml', import.meta.url), 'utf8');
  assert.match(workflow, /os: ubuntu-24.04\n\s+target: linux-x64/);
  assert.match(workflow, /os: macos-15\n\s+target: darwin-arm64/);
  assert.doesNotMatch(workflow, /windows-|continue-on-error|--test-name-pattern|--prefix toolchain/);
  assert.match(workflow, /python-version: '3.13.14'/);
  assert.match(workflow, /qualification-bootstrap\.mjs/);
  assert.match(workflow, /packages\/software-factory\/templates\/workflows\/change\.ts/);
  assert.match(workflow, /packages\/software-factory\/templates\/workflows\/audit\.ts/);
  assert.match(workflow, /cp toolchain\/package\.json toolchain\/package-lock\.json/);
  assert.match(workflow, /--prefix "\$RUNNER_TEMP\/cleanup-ordinary-toolchain"/);
  assert.match(workflow, /FACTORY_ATOMIC_PYTHON:.*steps\.python\.outputs\.python-path/);
  assert.match(workflow, /FACTORY_TEST_NPM_CACHE_SEED:.*runner\.temp/);
  assert.match(workflow, /timeout-minutes: 10[\s\S]*run: node packages\/software-factory\/scripts\/test\.mjs qualification --area cleanup-ordinary-public/);
  const baseWorkflow = readFileSync(new URL('../../../.github/workflows/software-factory-cleanup-actions.yml', import.meta.url), 'utf8');
  assert.match(baseWorkflow, /qualification --area cleanup-actions-public/);
  const foundation = readFileSync(new URL('../scripts/qualification-foundation.mjs', import.meta.url), 'utf8');
  assert.doesNotMatch(foundation, /cleanup-ordinary/);
  const refused = spawnSync(process.execPath, [fileURLToPath(new URL(dispatch)), 'maintenance', '--operation', 'cleanup'], { encoding: 'utf8', timeout: 5000, env });
  assert.equal(refused.status, 1, refused.stdout + refused.stderr);
  assert.match(refused.stderr, /no tests match supplied filters/);
  assert.equal(refused.stdout, '');
});


test('metadata workflow prints only the closed refusal markers and never advertises diagnostic artifacts', () => {
  const workflow = readFileSync(new URL('../../../.github/workflows/windows-storage-loader-metadata-collect.yml', import.meta.url), 'utf8');
  const expected = [
    'metadata-refused-outer-deadline', 'metadata-refused-outer-exit', 'metadata-refused-outer-eof',
    'metadata-refused-outer-stderr', 'metadata-refused-outer-bounds', 'metadata-refused-outer-process',
    'metadata-refused-inner-deadline', 'metadata-refused-inner-exit', 'metadata-refused-inner-eof',
    'metadata-refused-inner-stderr', 'metadata-refused-inner-bounds', 'metadata-refused-inner-process',
    'metadata-refused-inner-protocol', 'metadata-refused-inner-changed', 'metadata-refused-wire', 'metadata-refused-prerequisite',
  ];
  const table = workflow.match(/\$diagnosticMarkers = @\(([\s\S]*?)\n\s*\)/);
  assert.ok(table, 'fixed workflow refusal marker allowlist is absent');
  const declared = [...table[1].matchAll(/'([^']*)'/g)].map(match => match[1]);
  assert.equal(table[1].replace(/'[^']*'/g, '').replace(/[,\s]/g, ''), '');
  assert.deepEqual(declared, expected);
  const branch = workflow.match(/if \(\$collectionExit -eq 1 -and \$ready\.Count -eq 1 -and \(Test-MetadataDiagnosticMarker \$ready\[0\]\)\) \{([\s\S]*?)\n\s*\}/);
  assert.ok(branch, 'diagnostics must require exit1, one line and exact ordinal membership');
  assert.match(workflow, /function Test-MetadataDiagnosticMarker\(\[object\]\$Value\)/);
  assert.match(workflow, /if \(\$Value -isnot \[string\]\) \{ return \$false \}/);
  assert.match(workflow, /\[string\]::Equals\(\$literal, \$Value, \[StringComparison\]::Ordinal\)/);
  assert.match(branch[1], /^\s*\[Console\]::Out\.WriteLine\(\[string\]\$ready\[0\]\)\s*$/);
  assert.doesNotMatch(branch[1], /GITHUB_OUTPUT|artifacts_ready|exit|prepare/i);
  assert.match(workflow, /\$ready\[0\] -is \[string\]/);
  assert.match(workflow, /\[string\]::Equals\(\$ready\[0\], 'metadata-artifacts-ready', \[StringComparison\]::Ordinal\)[\s\S]*AppendAllText\(\$env:GITHUB_OUTPUT[\s\S]*exit \$collectionExit/);
  assert.match(workflow, /throw 'Metadata collection refused without export'/);
  assert.match(workflow, /steps\.collect\.outputs\.artifacts_ready == 'true'/);
  assert.doesNotMatch(workflow, /continue-on-error/);
});

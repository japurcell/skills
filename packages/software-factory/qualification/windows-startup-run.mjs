// Manual native qualification driver. No factory runtime or product entry point imports this.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { closeSync, existsSync, ftruncateSync, mkdirSync, mkdtempSync, openSync, readFileSync, readdirSync, statSync, truncateSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { gitModes, includedConfigQuery, parseTrace, selectLaunchMode, validateModules, validateTrace } from './windows-startup.mjs';

const root = resolve(fileURLToPath(new URL('.', import.meta.url)));
const evidence = resolve(process.env.WINDOWS_STARTUP_EVIDENCE ?? join(process.cwd(), 'windows-startup-evidence'));
const report = { scope: 'exact-windows-startup-helper-qualification-spike', status: 'failed',
  platform: process.platform, arch: process.arch, node: process.version, cases: [], diagnostics: {},
  disclaimer: 'Native trace evidence is a qualification candidate, not production admission or source-binary equivalence.' };
mkdirSync(evidence, { recursive: true });
const sha256 = (path) => createHash('sha256').update(readFileSync(path)).digest('hex');
const save = () => writeFileSync(join(evidence, 'qualification.json'), `${JSON.stringify(report, null, 2)}\n`);
const gitImportedDlls = Object.freeze([
  'libiconv-2.dll', 'libintl-8.dll', 'libpcre2-8-0.dll', 'libwinpthread-1.dll', 'zlib1.dll',
]);

function privateEnvironment(home, wrappers, config) {
  const windows = process.env.SystemRoot ?? process.env.WINDIR;
  assert.ok(windows && /^[A-Za-z]:\\/.test(windows), 'Windows system root unavailable');
  const system32 = join(windows, 'System32');
  const temporary = join(home, 'temp');
  mkdirSync(temporary, { recursive: true });
  mkdirSync(join(home, 'AppData', 'Roaming'), { recursive: true });
  mkdirSync(join(home, 'AppData', 'Local'), { recursive: true });
  return {
    SystemRoot: windows, WINDIR: windows, ComSpec: join(system32, 'cmd.exe'),
    PATH: `${wrappers};${system32};${windows}`, PATHEXT: '.COM;.EXE;.BAT;.CMD',
    TEMP: temporary, TMP: temporary, HOME: home, USERPROFILE: home,
    HOMEDRIVE: home.slice(0, 2), HOMEPATH: home.slice(2),
    APPDATA: join(home, 'AppData', 'Roaming'), LOCALAPPDATA: join(home, 'AppData', 'Local'),
    GIT_CONFIG_GLOBAL: config, GIT_TRACE2: '0', GIT_TRACE2_EVENT: '0', GIT_TRACE2_PERF: '0',
    GIT_TERMINAL_PROMPT: '0',
  };
}

function assertPackage(archive) {
  for (const [member, expected] of Object.entries(archive.files)) {
    const actual = join(archive.root, ...member.split('/'));
    assert.ok(existsSync(actual), `missing pinned package member: ${member}`);
    assert.equal(sha256(actual), expected, `pinned package member changed: ${member}`);
  }
}

function powerShellBaseline(env) {
  const directory = join(evidence, 'cases', 'positive-child-control');
  mkdirSync(directory, { recursive: true });
  const powershell = join(env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe');
  const startedAt = new Date();
  report.diagnostics.powerShellBaseline = { executable: powershell, startedAt: startedAt.toISOString(), state: 'running' };
  save();
  const invocation = spawnSync(powershell, ['-NoProfile', '-NonInteractive', '-Command',
    "[Console]::Out.Write('baseline-ready')"],
  { env, cwd: directory, encoding: 'utf8', timeout: 75000, maxBuffer: 1_048_576 });
  writeFileSync(join(directory, 'baseline-stdout.txt'), invocation.stdout ?? '');
  writeFileSync(join(directory, 'baseline-stderr.txt'), invocation.stderr ?? '');
  report.diagnostics.powerShellBaseline = {
    executable: powershell, startedAt: startedAt.toISOString(), endedAt: new Date().toISOString(),
    elapsedMs: Date.now() - startedAt.getTime(), status: invocation.status,
    error: invocation.error?.message ?? null,
    outputMatched: invocation.status === 0 && invocation.stdout === 'baseline-ready',
  };
  save();
}

function launchCase(name, executable, cwd, args, env, archive, options = {}) {
  const launchMode = selectLaunchMode(options.launchMode);
  const diagnosticOnly = launchMode === 'detached-process';
  const directory = join(evidence, 'cases', name);
  mkdirSync(directory, { recursive: true });
  const stagePath = join(directory, 'launcher-stages.tsv');
  const spec = { executable, cwd, args, launchMode, diagnosticOnly,
    stdout: join(directory, 'stdout.bin'),
    stderr: join(directory, 'stderr.bin'), trace: join(directory, 'debug.tsv'),
    timeoutMs: options.timeoutMs ?? 15000 };
  writeFileSync(join(directory, 'spec.json'), `${JSON.stringify(spec, null, 2)}\n`);
  const powershell = join(env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe');
  const invocation = spawnSync(powershell, ['-NoProfile', '-NonInteractive', '-File',
    join(root, 'windows-startup-trace.ps1'), '-SpecPath', join(directory, 'spec.json'), '-StagePath', stagePath],
  { env, cwd: directory, encoding: 'utf8', timeout: 75000, maxBuffer: 1_048_576 });
  const result = { name, executable, cwd, args, launchMode, diagnosticOnly, spec: spec.trace, stagePath,
    tracerStatus: invocation.status, tracerError: invocation.error?.message ?? null,
    stages: existsSync(stagePath) ? readFileSync(stagePath, 'utf8').slice(0, 8192) : null,
    trace: [], reasons: [] };
  writeFileSync(join(directory, 'launcher-stdout.txt'), invocation.stdout ?? '');
  writeFileSync(join(directory, 'launcher-stderr.txt'), invocation.stderr ?? '');
  try {
    assert.equal(invocation.status, options.expectedStop ? 3 : 0,
      `trace launcher failed: ${invocation.error?.message ?? invocation.stderr}`);
    const records = parseTrace(readFileSync(spec.trace, 'utf8'));
    result.trace = records;
    const roots = records.filter((record) => record.kind === 'ROOT');
    assert.equal(roots.length, 1, 'missing unique root process ID');
    const exits = records.filter((record) => record.kind === 'EXIT' && record.pid === roots[0].pid);
    if (options.expectedStop) {
      assert.equal(records.filter((record) => record.kind === 'CREATE' && record.pid === roots[0].pid).length, 1);
      assert.equal(exits.length, 1, 'stopped root exit was not observed');
      assert.equal(records.filter((record) => record.kind === 'STOP_REQUESTED').length, 1);
      if (options.expectedStopReason)
        assert.equal(records.find((record) => record.kind === 'STOP_REQUESTED')?.value, options.expectedStopReason);
      assert.equal(records.filter((record) => record.kind === 'STOP_OBSERVED').length, 1);
      assert.equal(records.find((record) => record.kind === 'DONE')?.value, `stopped:${exits[0].value}`);
      assert.ok(!records.some((record) => record.kind === 'ERROR'), 'stop trace reported error');
    } else {
      const checked = validateTrace(records, roots[0].pid, options.expectChild ?? false, options.expectedChildImage);
      assert.ok(checked.ok, checked.reasons.join('; '));
      if (archive) validateModules(records, executable, archive, env.SystemRoot, options.expectedGitDlls);
    }
    result.exitCode = Number(exits[0].value);
    const stdout = readFileSync(spec.stdout);
    const stderr = readFileSync(spec.stderr);
    if (options.expectedStopReason === 'output-limit')
      assert.ok(stdout.length > 262144 || stderr.length > 262144, 'output limit control did not exceed threshold');
    else assert.ok(stdout.length <= 262144 && stderr.length <= 262144, 'diagnostic output exceeds 256 KiB bound');
    if (options.expectedNoOutput) assert.equal(stdout.length + stderr.length, 0, `${name} wrote unexpected output`);
    result.stdoutBytes = stdout.length; result.stderrBytes = stderr.length;
    result.stdoutText = stdout.toString('utf8').slice(0, 4096);
    result.stderrText = stderr.toString('utf8').slice(0, 4096);
    if (options.expectedExit !== undefined) assert.equal(result.exitCode, options.expectedExit, `${name} exit status`);
    if (options.stdoutIncludes) assert.ok(result.stdoutText.includes(options.stdoutIncludes), `${name} output missing expected text`);
    if (options.stdoutPath) assert.ok(result.stdoutText.replaceAll('\\', '/').toLowerCase()
      .includes(options.stdoutPath.replaceAll('\\', '/').toLowerCase()), `${name} output missing expected path`);
    if (options.stderrIncludes) assert.ok(result.stderrText.includes(options.stderrIncludes), `${name} diagnostic missing expected text`);
    if (options.expectedNonzero) assert.notEqual(result.exitCode, 0, `${name} unexpectedly succeeded`);
    result.status = 'passed';
  } catch (error) {
    result.status = 'failed';
    result.reasons.push(error instanceof Error ? error.message : String(error));
  }
  for (const [kind, path] of [['stdout', spec.stdout], ['stderr', spec.stderr]]) {
    if (existsSync(path)) {
      const originalBytes = statSync(path).size;
      result[`${kind}OriginalBytes`] = originalBytes;
      if (originalBytes > 262144) truncateSync(path, 262144);
    }
  }
  report.cases.push(result);
  save();
  return result;
}

function prepareFixture(git, env, work) {
  const repo = join(work, 'main');
  const linked = join(work, 'linked with spaces');
  const unborn = join(work, 'unborn');
  const reftable = join(work, 'reftable');
  function gitCall(cwd, args) {
    const execution = spawnSync(git, args, { cwd, env, encoding: 'utf8', timeout: 15000, maxBuffer: 262144 });
    assert.equal(execution.status, 0, `fixture Git ${args.join(' ')} failed: ${execution.stderr}`);
    return execution.stdout;
  }
  mkdirSync(repo); mkdirSync(unborn); mkdirSync(reftable);
  gitCall(repo, ['init', '--initial-branch=main']);
  gitCall(repo, ['config', 'user.name', 'Qualification Fixture']);
  gitCall(repo, ['config', 'user.email', 'fixture@example.invalid']);
  writeFileSync(join(repo, 'tracked.txt'), 'owned fixture\n');
  gitCall(repo, ['add', 'tracked.txt']);
  gitCall(repo, ['commit', '-m', 'fixture']);
  gitCall(repo, ['worktree', 'add', '--detach', linked, 'HEAD']);
  gitCall(unborn, ['init', '--initial-branch=main']);
  gitCall(reftable, ['init', '--initial-branch=main', '--ref-format=reftable']);
  return { repo, linked, unborn, reftable, gitCall };
}

function writeHostileConfig(home, marker) {
  const include = join(home, 'included.gitconfig');
  const markerSlash = marker.replaceAll('\\', '/');
  const command = `cmd.exe /c echo executed>${markerSlash}`;
  writeFileSync(include, `[core]\n\tfsmonitor = ${command}\n\thooksPath = ${home.replaceAll('\\', '/')}/hooks\n` +
    `[filter "canary"]\n\tsmudge = ${command}\n[credential]\n\thelper = !${command}\n`);
  const config = join(home, 'global.gitconfig');
  writeFileSync(config, `[include]\n\tpath = ${include.replaceAll('\\', '/')}\n` +
    `[core]\n\tpager = ${command}\n[remote "origin"]\n\turl = https://example.invalid/repo\n\tpromisor = true\n`);
  mkdirSync(join(home, 'hooks'));
  writeFileSync(join(home, 'hooks', 'post-checkout'), `${command}\n`);
  return config;
}

function tamperRefusal(archive, member) {
  const path = join(archive.root, ...member.split('/'));
  const original = readFileSync(path);
  try {
    const changed = Buffer.from(original);
    changed[Math.floor(changed.length / 2)] ^= 1;
    writeFileSync(path, changed);
    assert.throws(() => assertPackage(archive), /pinned package member changed/);
  } finally {
    writeFileSync(path, original);
    assertPackage(archive);
  }
  report.cases.push({ name: `tamper-${member.replaceAll('/', '-')}`, status: 'passed',
    evidence: 'Pinned package member mutation refused before launch and exact bytes restored.' });
  save();
}

function generatedConfig(directory, sourceText, compilerOptions) {
  mkdirSync(directory, { recursive: true });
  const source = join(directory, 'input.ts');
  const config = join(directory, 'tsconfig.generated.json');
  writeFileSync(source, sourceText);
  writeFileSync(config, `${JSON.stringify({ files: [source], compilerOptions: {
    target: 'ES2020', module: 'ESNext', strict: true, types: [], lib: ['ES2020'],
    outDir: join(directory, 'out'), noEmitOnError: true, ...compilerOptions,
  } }, null, 2)}\n`);
  return { source, config, output: join(directory, 'out', 'input.js') };
}

async function main() {
  assert.equal(process.platform, 'win32', 'native qualification requires Windows');
  assert.equal(process.arch, 'x64', 'native qualification requires Windows x64');
  assert.equal(process.version, 'v24.22.1', 'pinned Node 24.22.1 required');
  assert.equal(process.env.GITHUB_ACTIONS, 'true', 'run only on a disposable Actions runner');
  const artifacts = JSON.parse(readFileSync(join(evidence, 'artifacts.json'), 'utf8'));
  assert.equal(artifacts.status, 'prepared-not-natively-qualified');
  const gitArchive = artifacts.archives.git;
  const tsArchive = artifacts.archives.typescript;
  assertPackage(gitArchive); assertPackage(tsArchive);
  const git = join(gitArchive.root, 'mingw64', 'bin', 'git.exe');
  const compiler = join(tsArchive.root, 'package', 'lib', 'tsc.exe');
  const work = mkdtempSync(join(evidence, 'owned-'));
  const home = join(work, 'home');
  const wrappers = join(work, 'wrappers');
  mkdirSync(home); mkdirSync(wrappers);
  const marker = join(work, 'canary-executed.txt');
  writeFileSync(join(wrappers, 'git.cmd'), `@echo off\r\necho wrapper>${marker}\r\nexit /b 91\r\n`);
  writeFileSync(join(wrappers, 'tsc.cmd'), `@echo off\r\necho wrapper>${marker}\r\nexit /b 91\r\n`);
  const config = join(home, 'global.gitconfig');
  writeFileSync(config, '');
  for (const key of ['GIT_REDIRECT_STDOUT', 'GIT_ASK_YESNO', 'GIT_STRACE_COMMANDS',
    'TS_GO_DEBUG_STACK_LIMIT', 'NODE_OPTIONS', 'LD_PRELOAD']) process.env[key] = marker;
  const env = privateEnvironment(home, wrappers, config);
  for (const key of ['GIT_REDIRECT_STDOUT', 'GIT_ASK_YESNO', 'GIT_STRACE_COMMANDS',
    'TS_GO_DEBUG_STACK_LIMIT', 'NODE_OPTIONS', 'LD_PRELOAD'])
    assert.ok(!Object.hasOwn(env, key), `hostile inherited ${key} reached helper environment`);
  for (const name of ['git', 'tsc']) {
    const located = spawnSync(join(env.SystemRoot, 'System32', 'where.exe'), [name],
      { cwd: work, env, encoding: 'utf8', timeout: 5000, maxBuffer: 65536 });
    assert.equal(located.status, 0, `PATH ${name} wrapper resolution control failed`);
    assert.ok(located.stdout.replaceAll('\\', '/').toLowerCase()
      .includes(join(wrappers, `${name}.cmd`).replaceAll('\\', '/').toLowerCase()),
      `PATH did not resolve the controlled ${name} wrapper`);
  }
  report.cases.push({ name: 'path-wrapper-resolution', status: 'passed',
    evidence: 'PATH resolves a controlled git.cmd while helper launch uses the absolute native executable.' });
  save();
  const fixture = prepareFixture(git, env, work);
  writeHostileConfig(home, marker);
  assert.ok(fixture.gitCall(fixture.repo, includedConfigQuery)
    .includes(marker.replaceAll('\\', '/')), 'hostile include configuration was not active');
  report.cases.push({ name: 'hostile-include-read', status: 'passed',
    evidence: 'Pinned Git queried core.fsmonitor through the private global include without executing its value; other config canaries are unexercised decoys.' });
  save();

  powerShellBaseline(env);
  const positive = launchCase('positive-child-control', env.ComSpec, work,
    ['/d', '/c', env.ComSpec, '/d', '/c', 'exit', '0'],
    env, null, { expectChild: true, expectedChildImage: env.ComSpec, expectedExit: 0, expectedNoOutput: true });
  assert.equal(positive.status, 'passed', 'debugger positive child control failed');

  const stopControl = launchCase('direct-stop-control', join(env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
    work, ['-NoProfile', '-NonInteractive', '-Command', 'Start-Sleep -Seconds 30'],
    env, null, { expectedStop: true, expectedStopReason: 'deadline', timeoutMs: 500 });
  assert.equal(stopControl.status, 'passed', 'debugger direct stop was not observed');

  const outputControl = launchCase('bounded-output-control', join(env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
    work, ['-NoProfile', '-NonInteractive', '-Command',
      "for ($i=0; $i -lt 10000; $i++) { [Console]::WriteLine('x' * 1000) }; Start-Sleep -Seconds 30"],
    env, null, { expectedStop: true, expectedStopReason: 'output-limit', timeoutMs: 10000 });
  assert.equal(outputControl.status, 'passed', 'debugger bounded output stop was not observed');

  for (const [fixtureName, cwd] of Object.entries({ normal: fixture.repo, linked: fixture.linked,
    unborn: fixture.unborn, reftable: fixture.reftable })) {
    for (let index = 0; index < gitModes.length; index++) {
      assertPackage(gitArchive);
      const name = `git-${fixtureName}-${index}`;
      const options = { expectedExit: 0, expectedGitDlls: gitImportedDlls };
      if (index === 0) options.stdoutPath = cwd;
      if (index === 1) options.stdoutPath = fixtureName === 'linked' ? join(fixture.repo, '.git') : join(cwd, '.git');
      if (index === 2) {
        options.stdoutPath = fixtureName === 'linked'
          ? readFileSync(join(cwd, '.git'), 'utf8').replace(/^gitdir:\s*/i, '').trim()
          : join(cwd, '.git');
      }
      if (index === 3) options.stdoutPath = `worktree ${cwd}`;
      launchCase(name, git, cwd, gitModes[index], env, gitArchive, options);
    }
  }

  // These four cases compare one exact Git mode and the original controls under a detached launch.
  // They are diagnostic evidence only; the complete no-window matrix still determines the report status.
  const detached = 'detached-process';
  assertPackage(gitArchive);
  launchCase('git-normal-0-detached', git, fixture.repo, gitModes[0], env, gitArchive,
    { launchMode: detached, expectedExit: 0, expectedGitDlls: gitImportedDlls, stdoutPath: fixture.repo });
  launchCase('positive-child-control-detached', env.ComSpec, work,
    ['/d', '/c', env.ComSpec, '/d', '/c', 'exit', '0'], env, null,
    { launchMode: detached, expectChild: true, expectedChildImage: env.ComSpec,
      expectedExit: 0, expectedNoOutput: true });
  launchCase('direct-stop-control-detached', join(env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
    work, ['-NoProfile', '-NonInteractive', '-Command', 'Start-Sleep -Seconds 30'], env, null,
    { launchMode: detached, expectedStop: true, expectedStopReason: 'deadline', timeoutMs: 500 });
  launchCase('bounded-output-control-detached', join(env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
    work, ['-NoProfile', '-NonInteractive', '-Command',
      "for ($i=0; $i -lt 10000; $i++) { [Console]::WriteLine('x' * 1000) }; Start-Sleep -Seconds 30"],
    env, null, { launchMode: detached, expectedStop: true, expectedStopReason: 'output-limit', timeoutMs: 10000 });
  assert.ok(!existsSync(marker), 'Git helper or PATH wrapper created canary');

  // An altered linked registration is a negative identity case, not a replacement for a valid worktree.
  const registration = join(fixture.linked, '.git');
  const originalRegistration = readFileSync(registration);
  // Git marks this existing Windows file hidden. Open without CREATE_ALWAYS,
  // which Windows refuses for hidden files, and preserve its native attributes.
  function replaceRegistration(contents) {
    const handle = openSync(registration, 'r+');
    try { ftruncateSync(handle, 0); writeFileSync(handle, contents); }
    finally { closeSync(handle); }
  }
  try {
    const missing = join(work, 'missing-registration');
    assert.ok(!existsSync(missing));
    replaceRegistration(`gitdir: ${missing.replaceAll('\\', '/')}\n`);
    launchCase('git-wrong-registration', git, fixture.linked, gitModes[2], env, gitArchive,
      { expectedNonzero: true, expectedGitDlls: gitImportedDlls });
  } finally {
    replaceRegistration(originalRegistration);
  }

  // This authored config is an unselected decoy: every compiler case uses its generated -p path.
  const authored = join(work, 'authored-tsconfig.json');
  writeFileSync(authored, JSON.stringify({ extends: 'cmd.exe', compilerOptions: { plugins: [{ name: 'child' }], watch: true } }));
  const success = generatedConfig(join(work, 'typescript-success'),
    `eval("require('child_process').execSync('cmd.exe /c echo executed>${marker.replaceAll('\\', '/')}')");\n` +
    'const result: number = 42;\nexport { result };\n', {});
  const error = generatedConfig(join(work, 'typescript-error'), 'const result: number = "wrong";\n', {});
  const noOutput = generatedConfig(join(work, 'typescript-no-output'), 'export const result: number = 7;\n', { noEmit: true });
  const compilerCases = [
    ['typescript-one-build', success, { expectedExit: 0 }],
    ['typescript-error', error, { stdoutIncludes: 'error TS', expectedNonzero: true }],
    ['typescript-no-output', noOutput, { expectedExit: 0, expectedNoOutput: true }],
  ];
  for (const [name, input, options] of compilerCases) {
    assertPackage(tsArchive);
    launchCase(name, compiler, work, ['-p', input.config], env, tsArchive, options);
  }
  assertPackage(tsArchive);
  launchCase('typescript-one-build-detached', compiler, work, ['-p', success.config], env, tsArchive,
    { launchMode: detached, expectedExit: 0 });
  assert.ok(existsSync(success.output), 'one-build case did not emit JavaScript');
  assert.equal(readdirSync(join(work, 'typescript-success', 'out')).length, 1, 'one-build case emitted unexpected files');
  assert.ok(!existsSync(error.output), 'error compiler case emitted JavaScript');
  assert.ok(!existsSync(noOutput.output), 'no-output compiler case emitted JavaScript');
  assert.ok(!existsSync(marker), 'compiler source text or PATH wrapper created canary');
  tamperRefusal(gitArchive, 'mingw64/bin/git.exe');
  tamperRefusal(gitArchive, 'mingw64/bin/zlib1.dll');
  tamperRefusal(tsArchive, 'package/lib/tsc.exe');
  tamperRefusal(tsArchive, 'package/lib/lib.es5.d.ts');
  assertPackage(gitArchive); assertPackage(tsArchive);
  report.status = report.diagnostics.powerShellBaseline.outputMatched &&
    report.cases.every((item) => item.status === 'passed') ? 'native-spike-passed-review-required' : 'failed';
  save();
  if (report.status === 'failed') process.exitCode = 1;
}

main().catch((error) => {
  report.error = error instanceof Error ? error.message : String(error);
  save();
  process.stderr.write(`${report.error}\n`);
  process.exitCode = 1;
});

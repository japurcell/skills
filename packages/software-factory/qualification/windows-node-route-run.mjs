// Seven-case native experiment plus a separate debug-root differential. Never imported by product code.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { basename, join, relative, resolve, win32 } from 'node:path';
import { fileURLToPath } from 'node:url';
import { gitModes, parseTrace, validateModules } from './windows-startup.mjs';
import { validateNodeOutput, validateNodeRoute } from './windows-node-route.mjs';

const sourceRoot = resolve(fileURLToPath(new URL('.', import.meta.url)));
const evidence = resolve(process.env.WINDOWS_NODE_ROUTE_EVIDENCE ?? join(process.cwd(), 'windows-node-route-evidence'));
const manifest = JSON.parse(readFileSync(join(sourceRoot, 'runtime-manifest.json'), 'utf8'));
const report = { scope: 'representative-pinned-node-windows-spawn-route', status: 'failed',
  platform: process.platform, arch: process.arch, node: process.version, cases: [],
  rootLaunchDifferential: { label: 'DEBUG_PROCESS | DETACHED_PROCESS diagnostic',
    status: 'pending', cases: [] },
  limits: { childCaptureBytesPerStream: 262144, deadlineStopMs: 500,
    outputStopAfterBytes: 262144, outputDeadlineMs: 10000, outerTraceMs: 60000 },
  limitation: 'DEBUG_PROCESS observer adds its own launch conditions. This report is a representative experiment, not the full helper matrix or product admission.' };
mkdirSync(evidence, { recursive: true });
const sha256 = (path) => createHash('sha256').update(readFileSync(path)).digest('hex');
const sha256Bytes = (bytes) => createHash('sha256').update(bytes).digest('hex');
const save = () => writeFileSync(join(evidence, 'qualification.json'), `${JSON.stringify(report, null, 2)}\n`);
const normalized = (path) => win32.normalize(path.replace(/^\\\\\?\\/, '')).toLowerCase();
const within = (path, root) => normalized(path).startsWith(normalized(root) + win32.sep);
const gitDlls = ['libiconv-2.dll', 'libintl-8.dll', 'libpcre2-8-0.dll', 'libwinpthread-1.dll', 'zlib1.dll'];
const expectedCompilerBytes = Buffer.from('const result = 42;\nexport { result };\n');

function assertPackage(archive) {
  for (const [member, expected] of Object.entries(archive.files)) {
    const path = join(archive.root, ...member.split('/'));
    assert.ok(existsSync(path), `missing pinned package member ${member}`);
    assert.equal(sha256(path), expected, `changed pinned package member ${member}`);
  }
}

function privateEnvironment(home, config) {
  const windows = process.env.SystemRoot ?? process.env.WINDIR;
  assert.ok(windows && /^[A-Za-z]:\\/.test(windows), 'Windows system root unavailable');
  const temporary = join(home, 'temp');
  for (const path of [temporary, join(home, 'AppData', 'Roaming'), join(home, 'AppData', 'Local')])
    mkdirSync(path, { recursive: true });
  return { SystemRoot: windows, WINDIR: windows, ComSpec: join(windows, 'System32', 'cmd.exe'),
    PATH: `${join(windows, 'System32')};${windows}`, PATHEXT: '.COM;.EXE;.BAT;.CMD',
    TEMP: temporary, TMP: temporary, HOME: home, USERPROFILE: home,
    HOMEDRIVE: home.slice(0, 2), HOMEPATH: home.slice(2),
    APPDATA: join(home, 'AppData', 'Roaming'), LOCALAPPDATA: join(home, 'AppData', 'Local'),
    GIT_CONFIG_GLOBAL: config, GIT_TRACE2: '0', GIT_TRACE2_EVENT: '0', GIT_TRACE2_PERF: '0',
    GIT_TERMINAL_PROMPT: '0', GITHUB_ACTIONS: 'true' };
}

function verifyModules(records, nodePid, helperPid, nodeRoot, helper, archive, windows) {
  const dlls = records.filter((record) => record.kind === 'DLL');
  assert.ok(dlls.some((record) => record.pid === nodePid), 'Node root has no observed DLLs');
  assert.ok(dlls.some((record) => record.pid === helperPid), 'direct helper has no observed DLLs');
  for (const record of dlls) {
    assert.ok(record.value && existsSync(record.value.replace(/^\\\\\?\\/, '')),
      `unresolved or missing DLL path for PID ${record.pid}`);
    assert.ok(within(record.value, windows) ||
      record.pid === nodePid && within(record.value, nodeRoot) ||
      record.pid === helperPid && archive && within(record.value, archive.root),
    `DLL outside Windows and pinned package roots: ${record.value}`);
    if (record.pid === helperPid && archive && within(record.value, archive.root)) {
      const member = relative(archive.root, record.value.replace(/^\\\\\?\\/, '')).replaceAll('\\', '/');
      assert.equal(sha256(record.value.replace(/^\\\\\?\\/, '')), archive.files[member],
        `loaded helper DLL differs from pinned package: ${member}`);
    }
  }
  if (archive) {
    const helperOnly = [{ kind: 'CREATE', pid: helperPid, value: helper },
      ...dlls.filter((record) => record.pid === helperPid)];
    validateModules(helperOnly, helper, archive, windows, archive === report.artifacts?.git ? gitDlls : []);
  }
}

function buildControl(env, work) {
  const executable = join(work, 'windows-startup-control.exe');
  const source = join(sourceRoot, 'windows-startup-control.cs');
  const powershell = join(env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe');
  const invocation = spawnSync(powershell, ['-NoProfile', '-NonInteractive', '-File',
    join(sourceRoot, 'windows-startup-control-build.ps1'), '-SourcePath', source, '-OutputPath', executable],
  { env, cwd: work, encoding: 'utf8', timeout: 75000, maxBuffer: 65536 });
  assert.ifError(invocation.error);
  assert.equal(invocation.status, 0, `control build failed: ${invocation.stderr}`);
  assert.equal(invocation.stdout, 'control-built');
  report.control = { source, sourceSha256: sha256(source), executable, executableSha256: sha256(executable),
    compiler: 'Windows PowerShell 5.1 Add-Type ConsoleApplication' };
  save();
  return executable;
}

function runCase(name, route, executable, args, cwd, env, node, nodeRoot, archive,
  expected = {}, outerLaunchMode = 'no-window') {
  const directory = join(evidence, 'cases', name);
  mkdirSync(directory, { recursive: true });
  const launcher = join(sourceRoot, 'windows-node-route-launch.mjs');
  const nodeSpec = { route, control: expected.stop ?? 'normal', executable, args, cwd, env };
  const nodeSpecPath = join(directory, 'node-spec.json');
  const nodeResultPath = join(directory, 'node-result.json');
  writeFileSync(nodeSpecPath, `${JSON.stringify(nodeSpec, null, 2)}\n`);
  const traceSpec = { executable: node, cwd: directory, args: [launcher, nodeSpecPath, nodeResultPath],
    launchMode: outerLaunchMode, diagnosticOnly: false, timeoutMs: 60000,
    stdout: join(directory, 'node-stdout.bin'), stderr: join(directory, 'node-stderr.bin'),
    trace: join(directory, 'debug.tsv') };
  const traceSpecPath = join(directory, 'trace-spec.json');
  const stagePath = join(directory, 'launcher-stages.tsv');
  writeFileSync(traceSpecPath, `${JSON.stringify(traceSpec, null, 2)}\n`);
  const powershell = join(env.SystemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe');
  const invocation = spawnSync(powershell, ['-NoProfile', '-NonInteractive', '-File',
    join(sourceRoot, 'windows-startup-trace.ps1'), '-SpecPath', traceSpecPath, '-StagePath', stagePath],
  { env, cwd: directory, encoding: 'utf8', timeout: 75000, maxBuffer: 1048576 });
  writeFileSync(join(directory, 'tracer-stdout.txt'), invocation.stdout ?? '');
  writeFileSync(join(directory, 'tracer-stderr.txt'), invocation.stderr ?? '');
  const item = { name, route, outerLaunchMode, executable, args, cwd, archive: archive?.archive ?? null,
    outerLaunch: { executable: node, argv: traceSpec.args, cwd: directory, environment: env,
      flags: ['DEBUG_PROCESS', outerLaunchMode === 'no-window' ? 'CREATE_NO_WINDOW' : 'DETACHED_PROCESS'],
      startup: 'STARTF_USESTDHANDLES',
      stdin: 'inherited NUL handle', stdout: 'inherited file handle', stderr: 'inherited file handle',
      timeoutMs: traceSpec.timeoutMs, outputLimitBytesPerStream: 262144,
      tracerSourceSha256: sha256(join(sourceRoot, 'windows-startup-trace.cs')),
      bridgeSha256: sha256(join(sourceRoot, 'windows-startup-trace.ps1')) },
    tracerStatus: invocation.status, tracerError: invocation.error?.message ?? null,
    reasons: [], status: 'failed' };
  try {
    assert.ifError(invocation.error);
    assert.equal(invocation.status, 0, `outer debug loop failed: ${invocation.stderr}`);
    const records = parseTrace(readFileSync(traceSpec.trace, 'utf8'));
    const result = JSON.parse(readFileSync(nodeResultPath, 'utf8'));
    item.observedProcesses = records.filter((record) => record.kind === 'CREATE');
    item.traceEvents = records.length;
    item.loadedModules = records.filter((record) => record.kind === 'DLL')
      .map((record) => ({ pid: record.pid, path: record.value,
        sha256: record.value && existsSync(record.value.replace(/^\\\\\?\\/, ''))
          ? sha256(record.value.replace(/^\\\\\?\\/, '')) : null }));
    item.nodeResult = result;
    assert.equal(result.error, null, 'Node launcher reported an error');
    assert.equal(result.nodeVersion, 'v24.22.1');
    assert.equal(result.platform, 'win32'); assert.equal(result.arch, 'x64');
    assert.equal(result.nodePid, records.find((record) => record.kind === 'ROOT')?.pid,
      'Node PID differs from independent debug root');
    assert.equal(normalized(result.executable), normalized(executable));
    assert.deepEqual(result.args, args); assert.equal(normalized(result.cwd), normalized(cwd));
    assert.deepEqual(result.childEnvironment, env);
    assert.deepEqual(result.spawnOptions, { detached: route === 'candidate',
      windowsHide: route === 'candidate', shell: false, stdio: ['ignore', 'pipe', 'pipe'] });
    const expectation = { node, helper: executable, nested: expected.nested,
      stop: expected.stop, exitCode: 0, allowAdditional: route === 'baseline' };
    const checked = validateNodeRoute(records, result, expectation);
    assert.ok(checked.ok, checked.reasons.join('; '));
    if (route === 'baseline') {
      const strict = validateNodeRoute(records, result, { ...expectation, allowAdditional: false });
      item.strictNoExtra = { status: strict.ok ? 'passed' : 'failed', reasons: strict.reasons,
        extraProcesses: strict.children.slice(1) };
    }
    verifyModules(records, result.nodePid, result.childPid, nodeRoot, executable, archive, env.SystemRoot);
    assert.equal(statSync(traceSpec.stdout).size, 0, 'Node root wrote unexpected stdout');
    assert.equal(statSync(traceSpec.stderr).size, 0, 'Node root wrote unexpected stderr');
    const stdout = Buffer.from(result.stdoutBase64, 'base64');
    for (const stream of ['stdout', 'stderr']) {
      const bytes = Buffer.from(result[`${stream}Base64`], 'base64');
      assert.equal(bytes.length, result[`${stream}CapturedBytes`], `${stream} capture differs from count`);
    }
    if (expected.git) {
      item.expectedOutput = { gitPath: cwd, lineEnding: 'LF',
        stdoutSha256: sha256Bytes(Buffer.from(`${cwd.replaceAll('\\', '/')}\n`)) };
      const checkedOutput = validateNodeOutput(result, { kind: 'git', path: cwd, lineEnding: '\n' });
      assert.ok(checkedOutput.ok, checkedOutput.reasons.join('; '));
    }
    if (expected.compilerOutput) {
      assert.ok(existsSync(expected.compilerOutput), 'fresh compiler output absent');
      assert.equal(readdirSync(join(expected.compilerOutput, '..')).length, 1,
        'compiler emitted unexpected files');
      assert.ok(statSync(expected.compilerOutput).size <= 262144, 'compiler output exceeds 256 KiB evidence bound');
      const emitted = readFileSync(expected.compilerOutput);
      item.expectedOutput = { compilerOutput: expected.compilerOutput,
        expectedBytes: expectedCompilerBytes.length, expectedSha256: sha256Bytes(expectedCompilerBytes),
        actualBytes: emitted.length, actualSha256: sha256Bytes(emitted) };
      const checkedOutput = validateNodeOutput(result, { kind: 'typescript', emitted: expectedCompilerBytes }, emitted);
      assert.ok(checkedOutput.ok, checkedOutput.reasons.join('; '));
    }
    if (expected.nested) {
      const checkedOutput = validateNodeOutput(result, { kind: 'silent' });
      assert.ok(checkedOutput.ok, checkedOutput.reasons.join('; '));
    }
    if (expected.stop === 'deadline') {
      assert.ok(stdout.includes(Buffer.from('deadline-ready\n')), 'deadline marker absent before kill');
      assert.equal(result.stdoutBytes, 15, 'deadline marker byte count differs');
      assert.ok(result.stop.requestedAtMs >= 500 && result.stop.requestedAtMs < 10000,
        'deadline stop was not requested at 500 ms');
    }
    if (expected.stop === 'output-limit') {
      assert.ok(result.stdoutBytes > 262144, 'output threshold did not precede kill');
      assert.equal(result.stdoutCapturedBytes, 262144, 'output was not retained at 256 KiB cap');
      assert.ok(result.stop.requestedAtMs < 10000, 'output stop missed 10 second deadline');
    }
    item.status = route === 'baseline' ? 'diagnostic-complete' : 'passed';
  } catch (error) {
    item.reasons.push(error instanceof Error ? error.message : String(error));
  }
  if (outerLaunchMode === 'no-window') report.cases.push(item);
  else report.rootLaunchDifferential.cases.push(item);
  save();
  return item;
}

async function main() {
  assert.equal(process.platform, 'win32'); assert.equal(process.arch, 'x64');
  assert.equal(process.version, 'v24.22.1'); assert.equal(process.env.GITHUB_ACTIONS, 'true');
  const bootstrap = JSON.parse(readFileSync(join(evidence, 'bootstrap.json'), 'utf8'));
  assert.equal(bootstrap.status, 'passed');
  assert.equal(bootstrap.native?.node, manifest.node);
  assert.equal(bootstrap.sha256, manifest.artifacts['win32-x64'].sha256);
  const nodeArchive = join(bootstrap.directory, basename(new URL(bootstrap.url).pathname));
  assert.equal(sha256(nodeArchive), manifest.artifacts['win32-x64'].sha256);
  const nodeRoot = join(bootstrap.directory, 'node-v24.22.1-win-x64');
  const node = join(nodeRoot, 'node.exe');
  assert.ok(existsSync(node));
  const member = 'node-v24.22.1-win-x64/node.exe';
  const independent = spawnSync('tar', ['-xOf', nodeArchive, member],
    { encoding: null, timeout: 120000, maxBuffer: 150000000 });
  assert.ifError(independent.error);
  assert.equal(independent.status, 0, `pinned Node archive member extraction failed: ${independent.stderr}`);
  assert.ok(independent.stdout.length > 0, 'pinned Node archive member was empty');
  const archiveMemberSha256 = sha256Bytes(independent.stdout);
  const extractedNodeSha256 = sha256(node);
  const extractedNodeBytes = statSync(node).size;
  report.nodeArtifact = { archive: nodeArchive, archiveSha256: sha256(nodeArchive),
    member, archiveMemberSha256, archiveMemberBytes: independent.stdout.length,
    executable: node, executableSha256: extractedNodeSha256, bytes: extractedNodeBytes,
    memberMatchesExecutable: archiveMemberSha256 === extractedNodeSha256 &&
      independent.stdout.length === extractedNodeBytes };
  save();
  assert.equal(extractedNodeSha256, archiveMemberSha256, 'extracted node.exe differs from pinned archive member');
  assert.equal(extractedNodeBytes, independent.stdout.length, 'extracted node.exe size differs from archive member');
  const artifacts = JSON.parse(readFileSync(join(evidence, 'artifacts.json'), 'utf8'));
  assert.equal(artifacts.status, 'prepared-not-natively-qualified');
  const gitArchive = artifacts.archives.git;
  const tsArchive = artifacts.archives.typescript;
  assertPackage(gitArchive); assertPackage(tsArchive);
  report.artifacts = { git: gitArchive, typescript: tsArchive };
  const git = join(gitArchive.root, 'mingw64', 'bin', 'git.exe');
  const compiler = join(tsArchive.root, 'package', 'lib', 'tsc.exe');
  const work = mkdtempSync(join(evidence, 'owned-'));
  const home = join(work, 'home'); mkdirSync(home);
  const config = join(home, 'global.gitconfig'); writeFileSync(config, '');
  const env = privateEnvironment(home, config);
  const repo = join(work, 'repo'); mkdirSync(repo);
  const init = spawnSync(git, ['init', '--initial-branch=main'],
    { cwd: repo, env, encoding: 'utf8', timeout: 15000, maxBuffer: 262144 });
  assert.equal(init.status, 0, `pinned Git fixture init failed: ${init.stderr}`);
  const compilerSource = 'const result: number = 42;\nexport { result };\n';
  const compilerInput = (label) => {
    const directory = join(work, label); mkdirSync(directory);
    const source = join(directory, 'input.ts'); writeFileSync(source, compilerSource);
    const output = join(directory, 'out', 'input.js');
    const configPath = join(directory, 'tsconfig.generated.json');
    writeFileSync(configPath, `${JSON.stringify({ files: [source], compilerOptions: {
      target: 'ES2020', module: 'ESNext', strict: true, types: [], lib: ['ES2020'],
      outDir: join(directory, 'out'), noEmitOnError: true } }, null, 2)}\n`);
    assert.ok(!existsSync(output), 'compiler output preexisted launch');
    return { configPath, output };
  };
  const baselineTs = compilerInput('typescript-baseline');
  const candidateTs = compilerInput('typescript-candidate');
  const detachedRootTs = compilerInput('typescript-detached-root-candidate');
  const control = buildControl(env, work);
  const cases = [
    ['baseline-git', 'baseline', git, gitModes[0], repo, gitArchive, { git: true }],
    ['baseline-typescript', 'baseline', compiler, ['-p', baselineTs.configPath], work, tsArchive,
      { compilerOutput: baselineTs.output }],
    ['candidate-git', 'candidate', git, gitModes[0], repo, gitArchive, { git: true }],
    ['candidate-typescript', 'candidate', compiler, ['-p', candidateTs.configPath], work, tsArchive,
      { compilerOutput: candidateTs.output }],
    ['candidate-nested-cmd', 'candidate', env.ComSpec,
      ['/d', '/c', env.ComSpec, '/d', '/c', 'exit', '0'], work, null, { nested: env.ComSpec }],
    ['candidate-deadline-control', 'candidate', control, ['deadline'], work, null, { stop: 'deadline' }],
    ['candidate-output-control', 'candidate', control, ['output-limit'], work, null, { stop: 'output-limit' }],
  ];
  for (const [name, route, executable, args, cwd, archive, expected] of cases) {
    assert.equal(sha256(node), archiveMemberSha256, `pinned node.exe changed before ${name}`);
    if (archive) assertPackage(archive);
    runCase(name, route, executable, args, cwd, env, node, nodeRoot, archive, expected);
  }
  const detachedRootCases = [
    ['detached-root-candidate-git', git, gitModes[0], repo, gitArchive, { git: true }],
    ['detached-root-candidate-typescript', compiler, ['-p', detachedRootTs.configPath],
      work, tsArchive, { compilerOutput: detachedRootTs.output }],
    ['detached-root-candidate-nested-cmd', env.ComSpec,
      ['/d', '/c', env.ComSpec, '/d', '/c', 'exit', '0'], work, null, { nested: env.ComSpec }],
    ['detached-root-candidate-deadline-control', control, ['deadline'], work, null,
      { stop: 'deadline' }],
    ['detached-root-candidate-output-control', control, ['output-limit'], work, null,
      { stop: 'output-limit' }],
  ];
  for (const [name, executable, args, cwd, archive, expected] of detachedRootCases) {
    assert.equal(sha256(node), archiveMemberSha256, `pinned node.exe changed before ${name}`);
    if (archive) assertPackage(archive);
    runCase(name, 'candidate', executable, args, cwd, env, node, nodeRoot, archive,
      expected, 'detached-process');
  }
  report.rootLaunchDifferential.status = report.rootLaunchDifferential.cases.length === 5 &&
    report.rootLaunchDifferential.cases.every((item) => item.status === 'passed')
    ? 'strict-diagnostic-passed' : 'failed';
  const candidates = report.cases.filter((item) => item.route === 'candidate');
  const baselines = report.cases.filter((item) => item.route === 'baseline');
  report.status = candidates.length === 5 && candidates.every((item) => item.status === 'passed') &&
    baselines.length === 2 && baselines.every((item) => item.status === 'diagnostic-complete') &&
    report.rootLaunchDifferential.status === 'strict-diagnostic-passed'
    ? 'representative-native-candidate-passed-review-required' : 'failed';
  save();
  if (report.status === 'failed') process.exitCode = 1;
}

main().catch((error) => {
  report.error = error instanceof Error ? error.message : String(error);
  save(); process.stderr.write(`${report.error}\n`); process.exitCode = 1;
});

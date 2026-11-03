// Root-only qualification handshake. Real helpers use the unmodified production spawn tuple.
import { spawn } from 'node:child_process';
import { readFileSync, lstatSync, writeFileSync } from 'node:fs';
import { isAbsolute } from 'node:path';
import { routeCases } from './windows-etw-route.mjs';

let child, report, phase = 'ready', saved = false, timer, stopTimer;
const resultPath = process.argv[3];
const captureLimit = 262144;
const captured = { stdout: [], stderr: [] };
const timers = () => { clearTimeout(timer); clearTimeout(stopTimer); };
const stop = reason => {
  if (!child || report.stop || report.exitObserved) return;
  report.stop = { reason, requestedAtMs: Math.round(performance.now() - report.startedAt),
    killReturned: child.kill('SIGTERM') };
};
const persist = () => {
  if (saved) return;
  saved = true;
  const { startedAt, ...value } = report;
  for (const stream of ['stdout', 'stderr']) value[`${stream}Base64`] = Buffer.concat(captured[stream]).toString('base64');
  writeFileSync(resultPath, JSON.stringify(value) + '\n', { flag: 'wx' });
};
const abort = () => {
  if (report) { report.error ??= 'protocol'; stop('guard'); }
  timers(); process.stdin.destroy();
  // An actual spawned ChildProcess is the only signaling authority here.
  if (child && !report.exitObserved) {
    const watchdog = setTimeout(() => process.exit(2), 1000);
    child.once('close', () => { clearTimeout(watchdog); try { persist(); } catch {} process.exitCode = 2; });
  } else { try { if (report) persist(); } catch {} process.exitCode = 2; }
};
try {
  const specPath = process.argv[2];
  if (!specPath || !resultPath || !isAbsolute(specPath) || !isAbsolute(resultPath) ||
    !lstatSync(specPath).isFile() || lstatSync(specPath).isSymbolicLink() || lstatSync(specPath).size > 65536)
    throw new Error('protocol');
  const spec = JSON.parse(readFileSync(specPath, 'utf8'));
  if (!routeCases.includes(spec.case) || !isAbsolute(spec.executable) || !isAbsolute(spec.cwd) ||
    !Array.isArray(spec.args) || spec.args.length > 32 || spec.args.some(arg => typeof arg !== 'string' || arg.includes('\0')) ||
    !spec.env || Array.isArray(spec.env) || Object.entries(spec.env).some(([key, value]) =>
      typeof value !== 'string' || key.includes('\0') || value.includes('\0'))) throw new Error('protocol');
  const detached = spec.case.startsWith('candidate');
  report = { protocol: 1, case: spec.case, rootPid: process.pid, childPid: null, error: null,
    spawnOptions: { detached, windowsHide: detached, shell: false, stdio: ['ignore', 'pipe', 'pipe'] },
    spawnObserved: false, exitObserved: false, closeObserved: false, stdoutClosed: false, stderrClosed: false,
    exitCode: null, closeCode: null, exitSignal: null, closeSignal: null,
    stdoutBytes: 0, stderrBytes: 0, stdoutCapturedBytes: 0, stderrCapturedBytes: 0,
    stop: null, startedAt: 0 };
  const finish = () => {
    if (!report.closeObserved || !report.stdoutClosed || !report.stderrClosed) return;
    clearTimeout(stopTimer); phase = 'completed'; persist();
    process.stdout.write(`DONE\t${report.childPid ?? 0}\n`);
  };
  const launch = () => {
    phase = 'running'; clearTimeout(timer);
    timer = setTimeout(abort, 24000);
    report.startedAt = performance.now();
    child = spawn(spec.executable, spec.args, { ...report.spawnOptions, cwd: spec.cwd, env: spec.env });
    report.childPid = child.pid ?? null;
    child.on('spawn', () => {
      report.spawnObserved = true;
      if (spec.case === 'candidate-deadline-control') stopTimer = setTimeout(() => stop('deadline'), 500);
      if (spec.case === 'candidate-output-control') stopTimer = setTimeout(() => { report.error = 'output-timeout'; stop('guard'); }, 10000);
    });
    child.on('error', () => { report.error = 'spawn'; });
    for (const stream of ['stdout', 'stderr']) {
      child[stream].on('data', chunk => {
        report[`${stream}Bytes`] += chunk.length;
        const keep = Math.min(chunk.length, captureLimit - report[`${stream}CapturedBytes`]);
        if (keep > 0) { captured[stream].push(chunk.subarray(0, keep)); report[`${stream}CapturedBytes`] += keep; }
        if (spec.case === 'candidate-output-control' && report.stdoutBytes + report.stderrBytes > captureLimit) stop('output-limit');
        if (report.stdoutBytes + report.stderrBytes > 67108864) { report.error = 'output-cap'; stop('guard'); }
      });
      child[stream].on('error', () => { report.error = 'pipe'; });
      child[stream].on('close', () => { report[`${stream}Closed`] = true; finish(); });
    }
    child.on('exit', (code, signal) => { report.exitObserved = true; report.exitCode = code; report.exitSignal = signal; });
    child.on('close', (code, signal) => { report.closeObserved = true; report.closeCode = code; report.closeSignal = signal; finish(); });
  };
  timer = setTimeout(abort, 5000);
  process.stdin.on('data', bytes => {
    if (bytes.length !== 1) return abort();
    if (phase === 'ready' && bytes[0] === 0x52) return launch();
    if (phase === 'completed' && bytes[0] === 0x58) {
      phase = 'finished'; timers(); process.stdin.destroy(); process.exitCode = report.error ? 2 : 0; return;
    }
    abort();
  });
  process.stdin.on('end', () => { if (phase !== 'finished') abort(); });
  process.stdin.on('error', abort);
  process.stdout.write('READY\n');
} catch { abort(); }

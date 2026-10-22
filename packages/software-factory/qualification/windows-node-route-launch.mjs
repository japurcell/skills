// Qualification-only pinned Node child_process.spawn caller. The debugger launches this file as its root.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { isAbsolute, resolve } from 'node:path';

const captureLimit = 262144;
const started = performance.now();
const specPath = process.argv[2];
const resultPath = process.argv[3];
let report = { protocol: 1, nodePid: process.pid, nodeVersion: process.version,
  platform: process.platform, arch: process.arch, error: null };
try {
  assert.equal(process.platform, 'win32');
  assert.equal(process.arch, 'x64');
  assert.equal(process.version, 'v24.22.1');
  assert.equal(process.env.GITHUB_ACTIONS, 'true');
  assert.ok(specPath && resultPath && isAbsolute(specPath) && isAbsolute(resultPath));
  const spec = JSON.parse(readFileSync(specPath, 'utf8'));
  assert.ok(['baseline', 'candidate'].includes(spec.route));
  assert.ok(['normal', 'deadline', 'output-limit'].includes(spec.control));
  assert.ok(isAbsolute(spec.executable) && isAbsolute(spec.cwd));
  assert.ok(Array.isArray(spec.args) && spec.args.every((arg) => typeof arg === 'string'));
  assert.ok(spec.env && typeof spec.env === 'object' && !Array.isArray(spec.env));
  assert.ok(Object.keys(spec.env).every((key) => typeof spec.env[key] === 'string'));
  const detached = spec.route === 'candidate';
  const options = { cwd: spec.cwd, env: spec.env, detached, windowsHide: detached,
    shell: false, stdio: ['ignore', 'pipe', 'pipe'] };
  report = { ...report, route: spec.route, control: spec.control,
    executable: spec.executable, args: spec.args, cwd: spec.cwd, childEnvironment: spec.env,
    spawnOptions: { detached, windowsHide: detached, shell: false, stdio: options.stdio },
    childPid: null, spawnObserved: false, exitObserved: false, exitCode: null, exitSignal: null,
    closeObserved: false, closeCode: null, closeSignal: null,
    stdoutClosed: false, stderrClosed: false, stdoutBytes: 0, stderrBytes: 0,
    stdoutCapturedBytes: 0, stderrCapturedBytes: 0, stdoutBase64: '', stderrBase64: '', stop: null };
  const child = spawn(spec.executable, spec.args, options);
  report.childPid = child.pid ?? null;
  const captured = { stdout: [], stderr: [] };
  const stop = (reason) => {
    if (report.stop || report.closeObserved) return;
    report.stop = { reason, requestedAtMs: Math.round(performance.now() - started),
      killReturned: child.kill('SIGTERM'), signal: 'SIGTERM' };
  };
  let controlTimer;
  const guard = setTimeout(() => stop('guard'), 45000);
  child.on('spawn', () => {
    report.spawnObserved = true;
    if (spec.control === 'deadline') controlTimer = setTimeout(() => stop('deadline'), 500);
    if (spec.control === 'output-limit') controlTimer = setTimeout(() => stop('output-timeout'), 10000);
  });
  child.on('error', (error) => { report.error = `${error.name}: ${error.message}`.slice(0, 1024); });
  for (const stream of ['stdout', 'stderr']) {
    const pipe = child[stream];
    pipe.on('data', (chunk) => {
      report[`${stream}Bytes`] += chunk.length;
      const remaining = captureLimit - report[`${stream}CapturedBytes`];
      if (remaining > 0) {
        const part = chunk.subarray(0, remaining);
        captured[stream].push(part);
        report[`${stream}CapturedBytes`] += part.length;
      }
      if (spec.control === 'output-limit' && report.stdoutBytes + report.stderrBytes > captureLimit)
        stop('output-limit');
    });
    pipe.on('close', () => { report[`${stream}Closed`] = true; });
    pipe.on('error', (error) => { report.error = `${stream}: ${error.message}`.slice(0, 1024); });
  }
  child.on('exit', (code, signal) => {
    report.exitObserved = true; report.exitCode = code; report.exitSignal = signal;
  });
  child.on('close', (code, signal) => {
    clearTimeout(guard); clearTimeout(controlTimer);
    report.closeObserved = true; report.closeCode = code; report.closeSignal = signal;
    for (const stream of ['stdout', 'stderr'])
      report[`${stream}Base64`] = Buffer.concat(captured[stream]).toString('base64');
    report.elapsedMs = Math.round(performance.now() - started);
    writeFileSync(resultPath, `${JSON.stringify(report, null, 2)}\n`, { flag: 'wx' });
    if (report.error) process.exitCode = 1;
  });
} catch (error) {
  report.error = error instanceof Error ? `${error.name}: ${error.message}`.slice(0, 1024) : String(error).slice(0, 1024);
  if (resultPath && resolve(resultPath) === resultPath)
    writeFileSync(resultPath, `${JSON.stringify(report, null, 2)}\n`, { flag: 'wx' });
  process.exitCode = 1;
}
